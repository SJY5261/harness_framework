[CmdletBinding()]
param(
    [switch]$AuditOnly,
    [switch]$RegisterIfBusy
)

$ErrorActionPreference = 'Stop'

$sourceRoot = Join-Path $env:LOCALAPPDATA 'Programs\OpenAI Codex CLI'
$destinationRoot = 'D:\Tool\nodejs'
$sourcePackage = Join-Path $sourceRoot 'node_modules\@openai\codex'
$destinationPackage = Join-Path $destinationRoot 'node_modules\@openai\codex'
$logPath = 'D:\LOGS\codex-c-install-cleanup-20260729.log'
$autoRunPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$autoRunName = 'TomesCodexCInstallCleanup'
$expectedSourceRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $env:LOCALAPPDATA 'Programs\OpenAI Codex CLI')
)

function Write-CleanupLog {
    param([string]$Message)

    $logDirectory = Split-Path -Parent $logPath
    New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ssK'
    Add-Content -LiteralPath $logPath -Encoding UTF8 -Value "$timestamp $Message"
}

function Get-PackageManifest {
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

function Register-CleanupAutoRun {
    $scriptPath = [System.IO.Path]::GetFullPath($PSCommandPath)
    $command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -RegisterIfBusy"
    if (-not (Test-Path -LiteralPath $autoRunPath)) {
        New-Item -Path $autoRunPath | Out-Null
    }
    Set-ItemProperty -Path $autoRunPath -Name $autoRunName -Value $command
    Write-CleanupLog "registered persistent login cleanup: $scriptPath"
}

if (-not (Test-Path -LiteralPath $sourceRoot)) {
    Write-CleanupLog 'source already absent; nothing to remove'
    if (Test-Path -LiteralPath $autoRunPath) {
        Remove-ItemProperty -Path $autoRunPath -Name $autoRunName -ErrorAction SilentlyContinue
    }
    exit 0
}

$resolvedSourceRoot = [System.IO.Path]::GetFullPath($sourceRoot)
if (-not $resolvedSourceRoot.Equals(
    $expectedSourceRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Refusing unexpected source path: $resolvedSourceRoot"
}

foreach ($requiredPath in @(
    $sourcePackage,
    $destinationPackage,
    (Join-Path $destinationRoot 'codex.cmd')
)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required path is missing: $requiredPath"
    }
}

$allowedTopLevel = @('codex', 'codex.cmd', 'codex.ps1', 'node_modules', 'shim')
$unexpectedTopLevel = @(
    Get-ChildItem -Force -LiteralPath $sourceRoot |
        Where-Object { $_.Name -notin $allowedTopLevel } |
        Select-Object -ExpandProperty Name
)
if ($unexpectedTopLevel.Count -gt 0) {
    throw "Refusing source with unexpected entries: $($unexpectedTopLevel -join ', ')"
}

$sourceMetadata = Get-Content -Raw -Encoding UTF8 (
    Join-Path $sourcePackage 'package.json'
) | ConvertFrom-Json
$destinationMetadata = Get-Content -Raw -Encoding UTF8 (
    Join-Path $destinationPackage 'package.json'
) | ConvertFrom-Json
if (
    $sourceMetadata.name -ne $destinationMetadata.name -or
    $sourceMetadata.version -ne $destinationMetadata.version
) {
    throw (
        "Package identity differs: source=$($sourceMetadata.name)@$($sourceMetadata.version), " +
        "destination=$($destinationMetadata.name)@$($destinationMetadata.version)"
    )
}

$sourceManifest = Get-PackageManifest $sourcePackage
$destinationManifest = Get-PackageManifest $destinationPackage
$destinationByPath = @{}
foreach ($entry in $destinationManifest) {
    $destinationByPath[$entry.RelativePath] = $entry
}
$manifestDifferences = @(
    $sourceManifest | Where-Object {
        $destinationEntry = $destinationByPath[$_.RelativePath]
        -not $destinationEntry -or
        $destinationEntry.Length -ne $_.Length -or
        $destinationEntry.Sha256 -ne $_.Sha256
    }
)
if ($manifestDifferences.Count -gt 0) {
    throw (
        "The D: package is missing or differs from " +
        "$($manifestDifferences.Count) C: package entries"
    )
}

foreach ($wrapperName in @('codex', 'codex.cmd', 'codex.ps1')) {
    $sourceWrapper = Join-Path $sourceRoot $wrapperName
    $destinationWrapper = Join-Path $destinationRoot $wrapperName
    if (
        -not (Test-Path -LiteralPath $sourceWrapper) -or
        -not (Test-Path -LiteralPath $destinationWrapper)
    ) {
        throw "Wrapper is missing: $wrapperName"
    }
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceWrapper).Hash
    $destinationHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $destinationWrapper).Hash
    if ($sourceHash -ne $destinationHash) {
        throw "Wrapper differs: $wrapperName"
    }
}

$sourceProcesses = @(
    Get-CimInstance Win32_Process |
        Where-Object {
            ($_.ExecutablePath -and $_.ExecutablePath.StartsWith(
                $sourceRoot,
                [System.StringComparison]::OrdinalIgnoreCase
            )) -or
            ($_.CommandLine -and $_.CommandLine.Contains($sourceRoot))
        }
)

if ($AuditOnly) {
    [pscustomobject]@{
        Source = $sourceRoot
        Destination = $destinationRoot
        Package = "$($sourceMetadata.name)@$($sourceMetadata.version)"
        PackageFiles = $sourceManifest.Count
        ManifestDifferences = $manifestDifferences.Count
        DestinationExtraFiles = $destinationManifest.Count - $sourceManifest.Count
        MatchingWrappers = 3
        SourceProcesses = $sourceProcesses.Count
        ReadyToRemove = $sourceProcesses.Count -eq 0
    }
    exit 0
}

if ($sourceProcesses.Count -gt 0) {
    $processIds = ($sourceProcesses | Select-Object -ExpandProperty ProcessId) -join ','
    Write-CleanupLog "deferred; source is used by process IDs: $processIds"
    if ($RegisterIfBusy) {
        Register-CleanupAutoRun
    }
    exit 2
}

Write-CleanupLog (
    "verified duplicate $($sourceMetadata.name)@$($sourceMetadata.version); " +
    "removing $sourceRoot"
)
Remove-Item -LiteralPath $sourceRoot -Recurse -Force
if (Test-Path -LiteralPath $sourceRoot) {
    throw "Source still exists after removal: $sourceRoot"
}

if (Test-Path -LiteralPath $autoRunPath) {
    Remove-ItemProperty -Path $autoRunPath -Name $autoRunName -ErrorAction SilentlyContinue
}
Write-CleanupLog 'removed duplicate C: Codex CLI installation'
