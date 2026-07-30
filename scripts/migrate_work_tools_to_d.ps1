[CmdletBinding()]
param(
    [switch]$AuditOnly,
    [switch]$WaitForExit,
    [switch]$RegisterIfBusy
)

$ErrorActionPreference = 'Stop'

$dataRoot = 'D:\ToolData'
$toolRoot = 'D:\Tool'
$logPath = 'D:\LOGS\work-tools-d-migration-20260730.log'
$autoRunPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$autoRunName = 'TomesWorkToolsDMigration'
$legacyAutoRunNames = @(
    'TomesCodexCInstallCleanup',
    'TomesSourceTreeDMigration'
)

$profileRoot = [System.IO.Path]::GetFullPath($env:USERPROFILE)
$localAppData = [System.IO.Path]::GetFullPath($env:LOCALAPPDATA)
$roamingAppData = [System.IO.Path]::GetFullPath($env:APPDATA)
$resolvedDataRoot = [System.IO.Path]::GetFullPath($dataRoot)
$resolvedToolRoot = [System.IO.Path]::GetFullPath($toolRoot)

function Write-MigrationLog {
    param([string]$Message)

    $logDirectory = Split-Path -Parent $logPath
    if (-not (Test-Path -LiteralPath $logDirectory)) {
        New-Item -ItemType Directory -Path $logDirectory | Out-Null
    }
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ssK'
    Add-Content -LiteralPath $logPath -Encoding UTF8 -Value "$timestamp $Message"
}

trap {
    $message = $_.Exception.Message
    try {
        Write-MigrationLog "migration failed: $message"
    }
    catch {
    }
    [Console]::Error.WriteLine($message)
    exit 1
}

function Ensure-DataRootPermissions {
    $userSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $grantArguments = @(
        "*$userSid`:(OI)(CI)(F)",
        '*S-1-5-18:(OI)(CI)(F)',
        '*S-1-5-32-544:(OI)(CI)(F)'
    )
    $repositoryRoot = Split-Path -Parent $PSScriptRoot
    $repositoryAcl = Get-Acl -LiteralPath $repositoryRoot
    $sandboxIdentity = $repositoryAcl.Access |
        Where-Object {
            $_.IdentityReference.Value -like '*\CodexSandboxUsers'
        } |
        Select-Object -First 1 -ExpandProperty IdentityReference
    if (-not $sandboxIdentity) {
        throw 'CodexSandboxUsers ACL identity was not found on the repository'
    }
    $sandboxSid = $sandboxIdentity.Translate(
        [System.Security.Principal.SecurityIdentifier]
    ).Value
    $grantArguments += "*$sandboxSid`:(OI)(CI)(M)"

    & icacls.exe $resolvedDataRoot /grant:r $grantArguments | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to grant D: tool data permissions: $LASTEXITCODE"
    }
    & icacls.exe $resolvedDataRoot /inheritance:r | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to protect D: tool data permissions: $LASTEXITCODE"
    }
}

function Assert-SafeSource {
    param([string]$Path)

    $resolved = [System.IO.Path]::GetFullPath($Path)
    $allowedRoots = @($profileRoot, $localAppData, $roamingAppData)
    $isAllowed = $false
    foreach ($root in $allowedRoots) {
        if (
            $resolved.Equals($root, [System.StringComparison]::OrdinalIgnoreCase) -or
            $resolved.StartsWith(
                ($root.TrimEnd('\') + '\'),
                [System.StringComparison]::OrdinalIgnoreCase
            )
        ) {
            $isAllowed = $true
            break
        }
    }
    if (-not $isAllowed) {
        throw "Refusing source outside the user profile: $resolved"
    }
    return $resolved
}

function Assert-SafeDestination {
    param([string]$Path)

    $resolved = [System.IO.Path]::GetFullPath($Path)
    $allowedRoots = @($resolvedDataRoot, $resolvedToolRoot)
    $isAllowed = $false
    foreach ($root in $allowedRoots) {
        if (
            $resolved.Equals($root, [System.StringComparison]::OrdinalIgnoreCase) -or
            $resolved.StartsWith(
                ($root.TrimEnd('\') + '\'),
                [System.StringComparison]::OrdinalIgnoreCase
            )
        ) {
            $isAllowed = $true
            break
        }
    }
    if (-not $isAllowed) {
        throw "Refusing destination outside D: tool roots: $resolved"
    }
    return $resolved
}

function Get-DirectoryState {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        if (Test-Path -LiteralPath $Destination) {
            return 'DestinationOnly'
        }
        return 'Absent'
    }

    $sourceItem = Get-Item -Force -LiteralPath $Source
    if ($sourceItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        $target = @($sourceItem.Target)[0]
        if (
            [string]::Equals(
                [System.IO.Path]::GetFullPath($target),
                [System.IO.Path]::GetFullPath($Destination),
                [System.StringComparison]::OrdinalIgnoreCase
            )
        ) {
            return 'Migrated'
        }
        return 'UnexpectedReparsePoint'
    }

    return 'OnC'
}

function Get-FileManifest {
    param([string]$Root)

    @(
        Get-ChildItem -File -Recurse -Force -LiteralPath $Root |
            ForEach-Object {
                [pscustomobject]@{
                    RelativePath = $_.FullName.Substring($Root.Length).TrimStart('\')
                    Length = $_.Length
                    Sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
                }
            } |
            Sort-Object RelativePath
    )
}

function Test-SourceManifestInDestination {
    param(
        [string]$Source,
        [string]$Destination
    )

    $sourceManifest = Get-FileManifest $Source
    $destinationManifest = Get-FileManifest $Destination
    $destinationByPath = @{}
    foreach ($entry in $destinationManifest) {
        $destinationByPath[$entry.RelativePath] = $entry
    }

    $differences = @(
        $sourceManifest | Where-Object {
            $destinationEntry = $destinationByPath[$_.RelativePath]
            -not $destinationEntry -or
            $destinationEntry.Length -ne $_.Length -or
            $destinationEntry.Sha256 -ne $_.Sha256
        }
    )

    [pscustomobject]@{
        SourceFiles = $sourceManifest.Count
        DestinationFiles = $destinationManifest.Count
        Differences = $differences.Count
    }
}

function Move-DirectoryToD {
    param(
        [string]$Name,
        [string]$Source,
        [string]$Destination
    )

    $resolvedSource = Assert-SafeSource $Source
    $resolvedDestination = Assert-SafeDestination $Destination
    $state = Get-DirectoryState $resolvedSource $resolvedDestination

    if ($state -eq 'Migrated') {
        Write-MigrationLog "$Name already migrated"
        return
    }
    if ($state -eq 'UnexpectedReparsePoint') {
        throw "$Name source is an unexpected reparse point: $resolvedSource"
    }

    $destinationParent = Split-Path -Parent $resolvedDestination
    if (-not (Test-Path -LiteralPath $destinationParent)) {
        New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
    }
    if (-not (Test-Path -LiteralPath $resolvedDestination)) {
        New-Item -ItemType Directory -Path $resolvedDestination | Out-Null
    }

    if (Test-Path -LiteralPath $resolvedSource) {
        $sourceReparsePoints = @(
            Get-ChildItem -Directory -Recurse -Force -LiteralPath $resolvedSource |
                Where-Object {
                    $_.Attributes -band [System.IO.FileAttributes]::ReparsePoint
                }
        )
        if ($sourceReparsePoints.Count -gt 0) {
            throw "$Name contains nested reparse points; refusing automatic move"
        }

        & robocopy.exe $resolvedSource $resolvedDestination /E /COPY:DAT /DCOPY:DAT `
            /R:2 /W:1 /XJ /NP /NJH /NJS /NFL /NDL | Out-Null
        $robocopyExitCode = $LASTEXITCODE
        if ($robocopyExitCode -ge 8) {
            throw "$Name copy failed with robocopy exit code $robocopyExitCode"
        }

        $verification = Test-SourceManifestInDestination `
            $resolvedSource $resolvedDestination
        if ($verification.Differences -gt 0) {
            throw (
                "$Name verification failed for " +
                "$($verification.Differences) files"
            )
        }

        Write-MigrationLog (
            "$Name verified $($verification.SourceFiles) files; removing C: source"
        )
        Remove-Item -LiteralPath $resolvedSource -Recurse -Force
        if (Test-Path -LiteralPath $resolvedSource) {
            throw "$Name source remains after removal: $resolvedSource"
        }
    }

    $sourceParent = Split-Path -Parent $resolvedSource
    if (-not (Test-Path -LiteralPath $sourceParent)) {
        New-Item -ItemType Directory -Force -Path $sourceParent | Out-Null
    }
    New-Item -ItemType Junction -Path $resolvedSource `
        -Target $resolvedDestination | Out-Null

    $junction = Get-Item -Force -LiteralPath $resolvedSource
    $junctionTarget = @($junction.Target)[0]
    if (
        -not [string]::Equals(
            [System.IO.Path]::GetFullPath($junctionTarget),
            $resolvedDestination,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    ) {
        throw "$Name junction target is unexpected: $junctionTarget"
    }
    Write-MigrationLog "$Name migrated to $resolvedDestination"
}

function Move-GitConfigToD {
    $source = Assert-SafeSource (Join-Path $profileRoot '.gitconfig')
    $destination = Assert-SafeDestination (
        Join-Path $resolvedDataRoot 'Git\.gitconfig'
    )
    $destinationParent = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationParent)) {
        New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
    }

    if (Test-Path -LiteralPath $source) {
        Copy-Item -Force -LiteralPath $source -Destination $destination
        if (
            (Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash -ne
            (Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash
        ) {
            throw 'Git global config verification failed'
        }
    }
    if (-not (Test-Path -LiteralPath $destination)) {
        throw 'Git global config destination is missing'
    }

    $includePath = $destination.Replace('\', '/')
    $compatibilityConfig = "[include]`r`n`tpath = $includePath`r`n"
    Set-Content -LiteralPath $source -Encoding UTF8 -Value $compatibilityConfig
    [Environment]::SetEnvironmentVariable(
        'GIT_CONFIG_GLOBAL',
        $destination,
        'User'
    )
    Write-MigrationLog 'Git global config moved to D: with a C: compatibility include'
}

function Reset-CodexTempToD {
    $source = Assert-SafeSource (
        Join-Path $localAppData 'Temp\CodexSandbox'
    )
    $destination = Assert-SafeDestination (
        Join-Path $resolvedDataRoot 'Temp\CodexSandbox'
    )
    $state = Get-DirectoryState $source $destination
    if ($state -eq 'Migrated') {
        Write-MigrationLog 'Codex temp already migrated'
        return
    }
    if ($state -eq 'UnexpectedReparsePoint') {
        throw "Codex temp is an unexpected reparse point: $source"
    }

    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Directory -Force -Path $destination | Out-Null
    }
    if (Test-Path -LiteralPath $source) {
        $userSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        & icacls.exe $source /grant "*$userSid`:(OI)(CI)(F)" /T /C |
            Out-Null
        Remove-Item -LiteralPath $source -Recurse -Force
        if (Test-Path -LiteralPath $source) {
            throw "Codex temp remains after removal: $source"
        }
    }
    New-Item -ItemType Junction -Path $source -Target $destination | Out-Null
    Write-MigrationLog 'Codex temp reset to D:; disposable C: contents removed'
}

function Set-SourceTreeSystemGit {
    $settingsRoot = Join-Path $resolvedDataRoot 'SourceTree\Atlassian'
    if (-not (Test-Path -LiteralPath $settingsRoot)) {
        return
    }

    $configFiles = @(
        Get-ChildItem -File -Recurse -Filter 'user.config' `
            -LiteralPath $settingsRoot
    )
    foreach ($configFile in $configFiles) {
        [xml]$config = Get-Content -Raw -Encoding UTF8 `
            -LiteralPath $configFile.FullName
        $settings = @(
            $config.configuration.userSettings.ChildNodes.setting
        )
        $gitChoice = $settings | Where-Object { $_.name -eq 'GitWhichOne' }
        $gitPath = $settings | Where-Object { $_.name -eq 'GitSystemPath' }
        if ($gitChoice) {
            $gitChoice.value = '1'
        }
        if ($gitPath) {
            $gitPath.value = $resolvedToolRoot + '\Git'
        }
        if ($gitChoice -or $gitPath) {
            $config.Save($configFile.FullName)
        }
    }
    Write-MigrationLog 'SourceTree configured to use D: system Git'
}

function Set-UserEnvironment {
    param([hashtable]$Values)

    foreach ($entry in $Values.GetEnumerator()) {
        $currentValue = [Environment]::GetEnvironmentVariable(
            $entry.Key,
            'User'
        )
        if ([string]::Equals(
            $currentValue,
            $entry.Value,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
            continue
        }
        [Environment]::SetEnvironmentVariable(
            $entry.Key,
            $entry.Value,
            'User'
        )
    }
}

function Send-EnvironmentChanged {
    if (-not ('EnvironmentBroadcast' -as [type])) {
        Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class EnvironmentBroadcast {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern bool SendNotifyMessage(
        IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam);
}
'@
    }
    [void][EnvironmentBroadcast]::SendNotifyMessage(
        [IntPtr]0xffff,
        0x001A,
        [UIntPtr]::Zero,
        'Environment'
    )
}

function Register-MigrationAutoRun {
    $scriptPath = [System.IO.Path]::GetFullPath($PSCommandPath)
    $command = (
        "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass " +
        "-File `"$scriptPath`" -WaitForExit -RegisterIfBusy"
    )
    if (-not (Test-Path -LiteralPath $autoRunPath)) {
        New-Item -Path $autoRunPath | Out-Null
    }
    Set-ItemProperty -Path $autoRunPath -Name $autoRunName -Value $command
    foreach ($legacyName in $legacyAutoRunNames) {
        Remove-ItemProperty -Path $autoRunPath -Name $legacyName `
            -ErrorAction SilentlyContinue
    }
    Write-MigrationLog "registered persistent migration: $scriptPath"
}

function Remove-MigrationAutoRun {
    if (Test-Path -LiteralPath $autoRunPath) {
        Remove-ItemProperty -Path $autoRunPath -Name $autoRunName `
            -ErrorAction SilentlyContinue
        foreach ($legacyName in $legacyAutoRunNames) {
            Remove-ItemProperty -Path $autoRunPath -Name $legacyName `
                -ErrorAction SilentlyContinue
        }
    }
}

function Get-BlockingProcesses {
    $blockingNames = @(
        'Code.exe',
        'codex.exe',
        'codex-code-mode-host.exe',
        'SourceTree.exe',
        'pageant.exe',
        'dbeaver.exe',
        'idea64.exe',
        'git.exe',
        'gh.exe'
    )
    $gradleSource = Join-Path $profileRoot '.gradle'
    $legacyCodexSource = Join-Path $localAppData 'Programs\OpenAI Codex CLI'
    @(
        Get-CimInstance Win32_Process |
            Where-Object {
                $_.Name -in $blockingNames -or
                (
                    $_.Name -eq 'java.exe' -and
                    $_.CommandLine -and
                    $_.CommandLine.Contains($gradleSource)
                ) -or
                (
                    $_.Name -eq 'node.exe' -and
                    $_.CommandLine -and
                    $_.CommandLine.Contains($legacyCodexSource)
                )
            }
    )
}

$directoryMigrations = @(
    [pscustomobject]@{
        Name = 'Playwright browsers'
        Source = Join-Path $localAppData 'ms-playwright'
        Destination = Join-Path $resolvedDataRoot 'Playwright\Browsers'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'npm cache'
        Source = Join-Path $localAppData 'npm-cache'
        Destination = Join-Path $resolvedDataRoot 'npm\cache'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'Next.js tool data'
        Source = Join-Path $roamingAppData 'nextjs-nodejs'
        Destination = Join-Path $resolvedDataRoot 'Nextjs'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'pip cache'
        Source = Join-Path $localAppData 'pip'
        Destination = Join-Path $resolvedDataRoot 'pip'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'Gradle user home'
        Source = Join-Path $profileRoot '.gradle'
        Destination = Join-Path $resolvedDataRoot 'Gradle'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'Python user base'
        Source = Join-Path $roamingAppData 'Python'
        Destination = Join-Path $resolvedDataRoot 'Python\UserBase'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'GitHub CLI config'
        Source = Join-Path $roamingAppData 'GitHub CLI'
        Destination = Join-Path $resolvedDataRoot 'GitHubCLI'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'GitHub CLI local data'
        Source = Join-Path $localAppData 'GitHub CLI'
        Destination = Join-Path $resolvedDataRoot 'GitHubCLI\Local'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'JetBrains roaming data'
        Source = Join-Path $roamingAppData 'JetBrains'
        Destination = Join-Path $resolvedDataRoot 'JetBrains\Roaming'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'JetBrains local data'
        Source = Join-Path $localAppData 'JetBrains'
        Destination = Join-Path $resolvedDataRoot 'JetBrains\Local'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'Unreal Engine local data'
        Source = Join-Path $localAppData 'UnrealEngine'
        Destination = Join-Path $resolvedDataRoot 'UnrealEngine'
        Deferred = $false
    },
    [pscustomobject]@{
        Name = 'VS Code user data'
        Source = Join-Path $roamingAppData 'Code'
        Destination = Join-Path $resolvedDataRoot 'VSCode\UserData'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'VS Code profile data'
        Source = Join-Path $profileRoot '.vscode'
        Destination = Join-Path $resolvedDataRoot 'VSCode\Profile'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'VS Code shared data'
        Source = Join-Path $profileRoot '.vscode-shared'
        Destination = Join-Path $resolvedDataRoot 'VSCode\Shared'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'GitHub Copilot data'
        Source = Join-Path $profileRoot '.copilot'
        Destination = Join-Path $resolvedDataRoot 'Copilot'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'Codex home'
        Source = Join-Path $profileRoot '.codex'
        Destination = Join-Path $resolvedDataRoot 'Codex'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'DBeaver data'
        Source = Join-Path $roamingAppData 'DBeaverData'
        Destination = Join-Path $resolvedDataRoot 'DBeaver\UserData'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'DBeaver Eclipse data'
        Source = Join-Path $profileRoot '.eclipse'
        Destination = Join-Path $resolvedDataRoot 'DBeaver\Eclipse'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'SourceTree data'
        Source = Join-Path $localAppData 'Atlassian'
        Destination = Join-Path $resolvedDataRoot 'SourceTree\Atlassian'
        Deferred = $true
    },
    [pscustomobject]@{
        Name = 'SourceTree roaming data'
        Source = Join-Path $roamingAppData 'Atlassian'
        Destination = Join-Path $resolvedDataRoot 'SourceTree\AtlassianRoaming'
        Deferred = $true
    }
)

if (-not (Test-Path -LiteralPath $resolvedDataRoot)) {
    if ($AuditOnly) {
        throw "D: tool data root is missing: $resolvedDataRoot"
    }
    New-Item -ItemType Directory -Path $resolvedDataRoot | Out-Null
}
if (-not $AuditOnly) {
    Ensure-DataRootPermissions
}

if ($AuditOnly) {
    $directoryMigrations | ForEach-Object {
        [pscustomobject]@{
            Name = $_.Name
            Source = $_.Source
            Destination = $_.Destination
            State = Get-DirectoryState $_.Source $_.Destination
            Deferred = $_.Deferred
        }
    }
    $codexTempSource = Join-Path $localAppData 'Temp\CodexSandbox'
    $codexTempDestination = Join-Path $resolvedDataRoot 'Temp\CodexSandbox'
    [pscustomobject]@{
        Name = 'Codex temp'
        Source = $codexTempSource
        Destination = $codexTempDestination
        State = Get-DirectoryState $codexTempSource $codexTempDestination
        Deferred = $true
    }
    $blocking = @(Get-BlockingProcesses)
    [pscustomobject]@{
        Name = 'Blocking processes'
        Source = ($blocking.Name | Sort-Object -Unique) -join ','
        Destination = ''
        State = if ($blocking.Count -gt 0) { 'Busy' } else { 'Ready' }
        Deferred = $true
    }
    exit 0
}

$immediateMigrations = @($directoryMigrations | Where-Object { -not $_.Deferred })
foreach ($migration in $immediateMigrations) {
    Move-DirectoryToD $migration.Name $migration.Source $migration.Destination
}

Set-UserEnvironment @{
    PLAYWRIGHT_BROWSERS_PATH = Join-Path $resolvedDataRoot 'Playwright\Browsers'
    NPM_CONFIG_CACHE = Join-Path $resolvedDataRoot 'npm\cache'
    PIP_CACHE_DIR = Join-Path $resolvedDataRoot 'pip\cache'
    PYTHONUSERBASE = Join-Path $resolvedDataRoot 'Python\UserBase'
    GH_CONFIG_DIR = Join-Path $resolvedDataRoot 'GitHubCLI'
    CODEX_INSTALL_DIR = Join-Path $resolvedToolRoot 'nodejs'
}
Send-EnvironmentChanged

$blockingProcesses = @(Get-BlockingProcesses)
if ($blockingProcesses.Count -gt 0 -and -not $WaitForExit) {
    Register-MigrationAutoRun
    $names = ($blockingProcesses.Name | Sort-Object -Unique) -join ','
    Write-MigrationLog "deferred active-tool migration; busy processes: $names"
    Write-Output "Immediate migrations completed; deferred for: $names"
    exit 0
}

if ($blockingProcesses.Count -gt 0 -and $RegisterIfBusy) {
    Register-MigrationAutoRun
}
while ($blockingProcesses.Count -gt 0) {
    Start-Sleep -Seconds 10
    $blockingProcesses = @(Get-BlockingProcesses)
}

$deferredMigrations = @($directoryMigrations | Where-Object { $_.Deferred })
foreach ($migration in $deferredMigrations) {
    Move-DirectoryToD $migration.Name $migration.Source $migration.Destination
}
Reset-CodexTempToD

$sourceTreeScript = Join-Path $PSScriptRoot 'migrate_sourcetree_to_d.ps1'
$codexCleanupScript = Join-Path $PSScriptRoot 'cleanup_codex_c_install.ps1'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $sourceTreeScript
if ($LASTEXITCODE -ne 0) {
    throw "SourceTree app migration failed with exit code $LASTEXITCODE"
}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $codexCleanupScript
if ($LASTEXITCODE -ne 0) {
    throw "Codex C: cleanup failed with exit code $LASTEXITCODE"
}

Move-GitConfigToD
Set-SourceTreeSystemGit

Set-UserEnvironment @{
    CODEX_HOME = Join-Path $resolvedDataRoot 'Codex'
    CODEX_INSTALL_DIR = Join-Path $resolvedToolRoot 'nodejs'
    VSCODE_EXTENSIONS = Join-Path $resolvedDataRoot 'VSCode\Profile\extensions'
    GIT_CONFIG_GLOBAL = Join-Path $resolvedDataRoot 'Git\.gitconfig'
    PLAYWRIGHT_BROWSERS_PATH = Join-Path $resolvedDataRoot 'Playwright\Browsers'
    NPM_CONFIG_CACHE = Join-Path $resolvedDataRoot 'npm\cache'
    PIP_CACHE_DIR = Join-Path $resolvedDataRoot 'pip\cache'
    GRADLE_USER_HOME = Join-Path $resolvedDataRoot 'Gradle'
    PYTHONUSERBASE = Join-Path $resolvedDataRoot 'Python\UserBase'
    GH_CONFIG_DIR = Join-Path $resolvedDataRoot 'GitHubCLI'
}
Send-EnvironmentChanged
Remove-MigrationAutoRun
Write-MigrationLog 'all work-tool data migrated to D:'
Write-Output 'All work-tool data migrations completed.'
