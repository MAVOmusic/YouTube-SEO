# Run with -WhatIf first. Keep this script and the accompanying folder names
# text file in the same directory. Requires Windows PowerShell 5.1 or newer.
# Creates missing directories only; never removes or overwrites existing files.
[CmdletBinding(SupportsShouldProcess = $true)]
param()

$ErrorActionPreference = 'Stop'
$basePath = 'E:\_YT\YT Revive\_VER\Ver 3.00\_All Songs\_01 - Long Form'
$listPath = Join-Path $PSScriptRoot 'Long Form Folder Names 0001 - 0674.txt'

if (-not (Test-Path -LiteralPath 'E:\' -PathType Container)) {
    throw 'Drive E: is not available. No folders were created.'
}
if (-not (Test-Path -LiteralPath $listPath -PathType Leaf)) {
    throw "Folder names file not found: $listPath. Keep it beside this script."
}

$names = @{}
foreach ($line in (Get-Content -LiteralPath $listPath -Encoding UTF8)) {
    if ($line -notmatch '^(\d{4}) - .+ \(Long Form\)$') {
        throw "Invalid folder-list line: $line"
    }
    $id = [int]$Matches[1]
    if ($names.ContainsKey($id)) { throw "Duplicate number: $id" }
    if ($line.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0 -or
        $line.EndsWith('.') -or $line.EndsWith(' ')) {
        throw "Invalid Windows folder name: $line"
    }
    $names[$id] = $line
}
for ($id = 301; $id -le 674; $id++) {
    if (-not $names.ContainsKey($id)) { throw "Missing folder name: $id" }
}

# Preflight all target IDs before creating anything. If a differently named
# folder already uses an ID in its ten-range, stop instead of duplicating it.
$jobs = @()
for ($id = 301; $id -le 674; $id++) {
    $hundredStart = [int]([Math]::Floor(($id - 1) / 100) * 100 + 1)
    $tenStart = [int]([Math]::Floor(($id - 1) / 10) * 10 + 1)
    $hundred = '{0:D4} - {1:D4}' -f $hundredStart, ($hundredStart + 99)
    $ten = '{0:D4} - {1:D4}' -f $tenStart, ($tenStart + 9)
    $tenPath = Join-Path (Join-Path $basePath $hundred) $ten
    $videoPath = Join-Path $tenPath $names[$id]
    if (Test-Path -LiteralPath $tenPath -PathType Container) {
        $prefix = '{0:D4} - ' -f $id
        $conflicts = @(Get-ChildItem -LiteralPath $tenPath -Directory | Where-Object {
            $_.Name.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -and
            -not $_.Name.Equals($names[$id], [StringComparison]::OrdinalIgnoreCase)
        })
        if ($conflicts.Count -gt 0) {
            throw "A differently named folder already exists for $id`: $($conflicts[0].FullName). Resolve the naming conflict before running again. No folders were created by this run."
        }
    }
    $jobs += $videoPath
}

$created = 0
foreach ($videoPath in $jobs) {
    $analytics = Join-Path $videoPath '_02 - Analytics'
    $paths = @(
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
        if (Test-Path -LiteralPath $path -PathType Container) { continue }
        if (Test-Path -LiteralPath $path) { throw "A file blocks the directory path: $path" }
        if ($PSCmdlet.ShouldProcess($path, 'Create directory')) {
            # CreateDirectory also creates missing hundred- and ten-range parents.
            [void][IO.Directory]::CreateDirectory($path)
            $created++
        }
    }
}
Write-Host "Finished. $($jobs.Count) video folders processed; $created directories created."
if ($WhatIfPreference) { Write-Host 'Preview only: no directories were created.' }
