[CmdletBinding()]
param(
    [ValidateSet('work', 'personal')]
    [string]$SetProfile,
    [switch]$Json,
    [string]$MarkerPath = 'D:\ToolData\Harness\pc-profile.json',
    [string]$DesktopPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom

function Get-DesktopRoot {
    if (-not [string]::IsNullOrWhiteSpace($DesktopPath)) {
        return [System.IO.Path]::GetFullPath($DesktopPath)
    }

    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
    if ([string]::IsNullOrWhiteSpace($desktop) -and -not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
        $desktop = Join-Path $env:USERPROFILE 'Desktop'
    }
    if ([string]::IsNullOrWhiteSpace($desktop)) {
        throw '바탕화면 경로를 확인할 수 없습니다.'
    }
    return $desktop
}

if ($PSBoundParameters.ContainsKey('SetProfile')) {
    $markerDirectory = [System.IO.Path]::GetDirectoryName($MarkerPath)
    if ([string]::IsNullOrWhiteSpace($markerDirectory)) {
        throw 'MarkerPath에는 상위 폴더가 포함되어야 합니다.'
    }

    [System.IO.Directory]::CreateDirectory($markerDirectory) | Out-Null
    $marker = [ordered]@{
        schema_version = 1
        profile = $SetProfile
    }
    $markerJson = $marker | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($MarkerPath, $markerJson + [Environment]::NewLine, $utf8NoBom)
}

$profile = 'unknown'
$reason = 'marker_missing'

if (Test-Path -LiteralPath $MarkerPath -PathType Leaf) {
    try {
        $rawMarker = [System.IO.File]::ReadAllText($MarkerPath, [System.Text.Encoding]::UTF8)
        $parsedMarker = $rawMarker | ConvertFrom-Json
        $hasSchema = $parsedMarker.PSObject.Properties.Name -contains 'schema_version'
        $hasProfile = $parsedMarker.PSObject.Properties.Name -contains 'profile'
        $validSchema = $hasSchema -and [int]$parsedMarker.schema_version -eq 1
        $validProfile = $hasProfile -and $parsedMarker.profile -in @('work', 'personal')

        if (-not $validSchema -or -not $validProfile) {
            throw '지원하지 않는 PC 프로필 마커입니다.'
        }

        $profile = [string]$parsedMarker.profile
        $reason = 'configured'
    }
    catch {
        $profile = 'unknown'
        $reason = 'marker_invalid'
    }
}

$artifactRoot = $null
if ($profile -ne 'unknown') {
    $desktop = Get-DesktopRoot
    if ($profile -eq 'work') {
        $artifactRoot = Join-Path $desktop 'PR'
    }
    else {
        $artifactRoot = Join-Path $desktop 'Tomes\PR'
    }
}

$result = [ordered]@{
    schema_version = 1
    profile = $profile
    configured = $profile -ne 'unknown'
    reason = $reason
    artifact_root = $artifactRoot
    marker_path = $MarkerPath
}

if ($Json) {
    Write-Output ($result | ConvertTo-Json -Compress)
}
else {
    Write-Output ('PROFILE={0}' -f $result.profile)
    Write-Output ('CONFIGURED={0}' -f $result.configured.ToString().ToLowerInvariant())
    Write-Output ('REASON={0}' -f $result.reason)
    Write-Output ('ARTIFACT_ROOT={0}' -f $result.artifact_root)
    Write-Output ('MARKER_PATH={0}' -f $result.marker_path)
}

if ($profile -eq 'unknown') {
    exit 2
}
