param(
  [string]$Message = ""
)

$ErrorActionPreference = "Stop"

# Run from repo root even if invoked elsewhere.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

git add -A | Out-Null

$staged = git diff --cached --name-only
if ([string]::IsNullOrWhiteSpace($staged)) {
  Write-Host "No changes to publish."
  exit 0
}

if ([string]::IsNullOrWhiteSpace($Message)) {
  $Message = "publish: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}

git commit -m $Message
git push

