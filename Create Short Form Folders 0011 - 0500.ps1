# Keep this script next to Short Form Folder Names 0001 - 0500.txt.
# Run with -WhatIf first. Windows PowerShell 5.1 or newer.
# The first ten folder names are reference only; this script processes 0011-0500.
[CmdletBinding(SupportsShouldProcess = $true)]
param()

$ErrorActionPreference = 'Stop'
$basePath = 'E:\_YT\YT Revive\_VER\Ver 3.00\_All Songs\_02 - Short Form'
$listPath = Join-Path $PSScriptRoot 'Short Form Folder Names 0001 - 0500.txt'

if (-not (Test-Path -LiteralPath $basePath -PathType Container)) {
    throw "Short Form base directory not found: $basePath. No folders were created."
}
if (-not (Test-Path -LiteralPath $listPath -PathType Leaf)) {
    throw "Folder names file not found: $listPath. Keep it beside this script."
}

$names = @{}
foreach ($line in (Get-Content -LiteralPath $listPath -Encoding UTF8)) {
    if ($line -notmatch '^(\d{4}) - .+ \(Short Form\)$') {
        throw "Invalid folder-list line: $line"
    }
    $id = [int]$Matches[1]
    if ($id -lt 1 -or $id -gt 500 -or $names.ContainsKey($id)) {
        throw "Unexpected or duplicate number: $id"
    }
    if ($line.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0 -or
        $line.EndsWith('.') -or $line.EndsWith(' ')) {
        throw "Invalid Windows folder name: $line"
    }
    $names[$id] = $line
}
for ($id = 1; $id -le 500; $id++) {
    if (-not $names.ContainsKey($id)) { throw "Missing folder name: $id" }
}

# Preflight all jobs, including existing differently named folders and files
# blocking a required path, before creating any directories.
$jobs = @()
for ($id = 11; $id -le 500; $id++) {
    $hundredStart = [int]([Math]::Floor(($id - 1) / 100) * 100 + 1)
    $tenStart = [int]([Math]::Floor(($id - 1) / 10) * 10 + 1)
    $hundredPath = Join-Path $basePath ('{0:D4} - {1:D4}' -f $hundredStart, ($hundredStart + 99))
    $tenPath = Join-Path $hundredPath ('{0:D4} - {1:D4}' -f $tenStart, ($tenStart + 9))
    $videoPath = Join-Path $tenPath $names[$id]
    if (Test-Path -LiteralPath $tenPath -PathType Container) {
        $prefix = '{0:D4} - ' -f $id
        $conflicts = @(Get-ChildItem -LiteralPath $tenPath -Force | Where-Object {
            $_.Name.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -and
            -not $_.Name.Equals($names[$id], [StringComparison]::OrdinalIgnoreCase)
        })
        if ($conflicts.Count -gt 0) {
            throw "A differently named item already uses ID $id`: $($conflicts[0].FullName). Resolve it before running again. No folders were created by this run."
        }
    }
    $analytics = Join-Path $videoPath '_02 - Analytics'
    $paths = @(
        $hundredPath
        $tenPath
        $videoPath
        (Join-Path $videoPath '_01 - Main Info')
        $analytics
        (Join-Path $analytics '_01 Overview')
        (Join-Path $analytics '_02 Reach')
        (Join-Path $analytics '_03 Engagement')
        (Join-Path $analytics '_04 Audience')
        (Join-Path $analytics '_05 Revenue')
    )
    foreach ($path in $paths) {
        if ((Test-Path -LiteralPath $path) -and -not (Test-Path -LiteralPath $path -PathType Container)) {
            throw "A file blocks a required folder: $path. No folders were created by this run."
        }
    }
    $jobs += ,$paths
}

$created = 0
foreach ($paths in $jobs) {
    foreach ($path in $paths) {
        if (Test-Path -LiteralPath $path -PathType Container) { continue }
        if ($PSCmdlet.ShouldProcess($path, 'Create directory')) {
            [void][IO.Directory]::CreateDirectory($path)
            $created++
        }
    }
}
Write-Host "Finished. 490 video folders processed; $created directories created."
if ($WhatIfPreference) { Write-Host 'Preview only: no directories were created.' }
