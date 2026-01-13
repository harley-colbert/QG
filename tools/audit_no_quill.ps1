# PowerShell: Fail if Quill remnants exist.
# Usage: powershell -ExecutionPolicy Bypass -File .\tools\audit_no_quill.ps1

$ErrorActionPreference = "Stop"

$patterns = @(
  "quill",
  "ql-",
  "dangerouslyPasteHTML"
)

$excludeDirs = @(
  ".git",
  "__pycache__",
  "node_modules",
  "venv",
  "planQuoteGenV4.7",
  "agentsQuoteGenV4.7",
  "tools"
)

Write-Host "Audit: scanning repo for prohibited Quill remnants..."

$results = @()

Get-ChildItem -Recurse -File | ForEach-Object {
  foreach ($ex in $excludeDirs) {
    if ($_.FullName -like "*\$ex\*") { return }
  }

  $content = Get-Content -LiteralPath $_.FullName -Raw -ErrorAction SilentlyContinue
  if ($null -eq $content) { return }

  foreach ($p in $patterns) {
    if ($content -match [regex]::Escape($p)) {
      $results += "$($_.FullName) :: $p"
    }
  }
}

if ($results.Count -gt 0) {
  Write-Host "FAILED: Found prohibited Quill remnants:"
  $results | Sort-Object | Get-Unique | ForEach-Object { Write-Host $_ }
  exit 1
}

Write-Host "PASSED: No Quill remnants found."
exit 0
