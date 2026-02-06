param(
  [string]$File = "docs\\index.html",
  [int]$DebounceSeconds = 3
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

$full = Join-Path (Get-Location) $File
if (-not (Test-Path $full)) {
  throw "File not found: $full"
}

$dir = Split-Path -Parent $full
$name = Split-Path -Leaf $full

$script:pending = $false
$script:lastEventUtc = [DateTime]::UtcNow

$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $dir
$fsw.Filter = $name
$fsw.IncludeSubdirectories = $false
$fsw.NotifyFilter = [System.IO.NotifyFilters]'LastWrite, FileName'
$fsw.EnableRaisingEvents = $true

$handler = {
  $script:pending = $true
  $script:lastEventUtc = [DateTime]::UtcNow
}

Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $handler | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Created -Action $handler | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action $handler | Out-Null

Write-Host ("Watching {0}. Auto commit+push after {1}s of inactivity." -f $full, $DebounceSeconds)
Write-Host "Stop with Ctrl+C."

try {
  while ($true) {
    Start-Sleep -Seconds 1

    if (-not $script:pending) { continue }
    $since = ([DateTime]::UtcNow - $script:lastEventUtc).TotalSeconds
    if ($since -lt $DebounceSeconds) { continue }

    $script:pending = $false

    # Only publish if there are actual working tree changes.
    $dirty = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($dirty)) { continue }

    $msg = "auto: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    & .\\scripts\\publish.ps1 -Message $msg
  }
} finally {
  Get-EventSubscriber | Where-Object { $_.SourceObject -eq $fsw } | Unregister-Event
  $fsw.Dispose()
}

