[CmdletBinding()]
param(
    [switch]$AuditOnly,
    [switch]$RegisterIfBusy
)

$ErrorActionPreference = 'Stop'

$sourceRoot = Join-Path $env:LOCALAPPDATA 'SourceTree'
$destinationRoot = 'D:\Tool\SourceTree'
$logPath = 'D:\LOGS\sourcetree-d-migration-20260729.log'
$autoRunPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$autoRunName = 'TomesSourceTreeDMigration'
$expectedSourceRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $env:LOCALAPPDATA 'SourceTree')
)
$expectedDestinationRoot = [System.IO.Path]::GetFullPath(
    'D:\Tool\SourceTree'
)

function Write-MigrationLog {
    param([string]$Message)

    $logDirectory = Split-Path -Parent $logPath
    New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ssK'
    Add-Content -LiteralPath $logPath -Encoding UTF8 -Value "$timestamp $Message"
}

function Register-MigrationAutoRun {
    $scriptPath = [System.IO.Path]::GetFullPath($PSCommandPath)
    $command = (
        "powershell.exe -NoProfile -ExecutionPolicy Bypass " +
        "-File `"$scriptPath`" -RegisterIfBusy"
    )
    if (-not (Test-Path -LiteralPath $autoRunPath)) {
        New-Item -Path $autoRunPath | Out-Null
    }
    Set-ItemProperty -Path $autoRunPath -Name $autoRunName -Value $command
    Write-MigrationLog "registered persistent login migration: $scriptPath"
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

function Remove-MigrationAutoRun {
    if (Test-Path -LiteralPath $autoRunPath) {
        Remove-ItemProperty -Path $autoRunPath -Name $autoRunName `
            -ErrorAction SilentlyContinue
    }
}

$resolvedSourceRoot = [System.IO.Path]::GetFullPath($sourceRoot)
$resolvedDestinationRoot = [System.IO.Path]::GetFullPath($destinationRoot)
if (-not $resolvedSourceRoot.Equals(
    $expectedSourceRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Refusing unexpected source path: $resolvedSourceRoot"
}
if (-not $resolvedDestinationRoot.Equals(
    $expectedDestinationRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Refusing unexpected destination path: $resolvedDestinationRoot"
}

if (Test-Path -LiteralPath $sourceRoot) {
    $sourceItem = Get-Item -Force -LiteralPath $sourceRoot
    if ($sourceItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        $target = @($sourceItem.Target)[0]
        if (-not [string]::Equals(
            $target,
            $destinationRoot,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Source is an unexpected reparse point: $target"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $destinationRoot 'SourceTree.exe'))) {
            throw 'SourceTree destination launcher is missing'
        }
        Remove-MigrationAutoRun
        Write-MigrationLog 'D: SourceTree junction already active'
        if ($AuditOnly) {
            [pscustomobject]@{
                Source = $sourceRoot
                Destination = $destinationRoot
                State = 'Migrated'
                SourceProcesses = 0
                ReadyToMigrate = $false
            }
        }
        exit 0
    }
}

if (-not (Test-Path -LiteralPath $sourceRoot)) {
    if (-not (Test-Path -LiteralPath (Join-Path $destinationRoot 'SourceTree.exe'))) {
        throw 'Neither the SourceTree source nor a complete destination exists'
    }
    New-Item -ItemType Junction -Path $sourceRoot -Target $destinationRoot | Out-Null
    Remove-MigrationAutoRun
    Write-MigrationLog 'recovered missing SourceTree compatibility junction'
    exit 0
}

if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'SourceTree.exe'))) {
    throw 'SourceTree source launcher is missing'
}

$sourceProcesses = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            ($_.ExecutablePath -and $_.ExecutablePath.StartsWith(
                ($sourceRoot + '\'),
                [System.StringComparison]::OrdinalIgnoreCase
            )) -or
            ($_.CommandLine -and $_.CommandLine.Contains($sourceRoot))
        }
)

if ($AuditOnly) {
    $sourceFiles = @(Get-ChildItem -File -Recurse -Force -LiteralPath $sourceRoot)
    [pscustomobject]@{
        Source = $sourceRoot
        Destination = $destinationRoot
        State = 'OnC'
        SourceFiles = $sourceFiles.Count
        SourceBytes = ($sourceFiles | Measure-Object Length -Sum).Sum
        SourceProcesses = $sourceProcesses.Count
        ReadyToMigrate = $sourceProcesses.Count -eq 0
    }
    exit 0
}

if ($sourceProcesses.Count -gt 0) {
    $processIds = ($sourceProcesses | Select-Object -ExpandProperty ProcessId) -join ','
    Write-MigrationLog "deferred; source is used by process IDs: $processIds"
    if ($RegisterIfBusy) {
        Register-MigrationAutoRun
    }
    exit 2
}

New-Item -ItemType Directory -Force -Path $destinationRoot | Out-Null
& robocopy.exe $sourceRoot $destinationRoot /E /COPY:DAT /DCOPY:DAT /R:2 /W:1 `
    /XJ /NP /NJH /NJS /NFL /NDL | Out-Null
$robocopyExitCode = $LASTEXITCODE
if ($robocopyExitCode -ge 8) {
    throw "SourceTree copy failed with robocopy exit code $robocopyExitCode"
}

$sourceManifest = Get-FileManifest $sourceRoot
$destinationManifest = Get-FileManifest $destinationRoot
$manifestDifferences = @(
    Compare-Object $sourceManifest $destinationManifest `
        -Property RelativePath, Length, Sha256
)
if ($manifestDifferences.Count -gt 0) {
    throw "SourceTree manifests differ in $($manifestDifferences.Count) entries"
}

Write-MigrationLog (
    "verified $($sourceManifest.Count) files; moving SourceTree storage to D:"
)
Remove-Item -LiteralPath $sourceRoot -Recurse -Force
if (Test-Path -LiteralPath $sourceRoot) {
    throw "Source still exists after removal: $sourceRoot"
}

New-Item -ItemType Junction -Path $sourceRoot -Target $destinationRoot | Out-Null
$junction = Get-Item -Force -LiteralPath $sourceRoot
$junctionTarget = @($junction.Target)[0]
if (-not [string]::Equals(
    $junctionTarget,
    $destinationRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Unexpected SourceTree junction target: $junctionTarget"
}

Remove-MigrationAutoRun
Write-MigrationLog 'migrated SourceTree files to D: and created compatibility junction'
