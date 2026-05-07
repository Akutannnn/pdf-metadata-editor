<#
.SYNOPSIS
    Remove the "Edit metadata" right-click context menu for .pdf files.

.DESCRIPTION
    Deletes the per-user HKCU registry keys written by install_context_menu.ps1.
    No administrator privileges are required.

.EXAMPLE
    .\uninstall_context_menu.ps1
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$shellKey   = "HKCU:\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata"
$commandKey = "$shellKey\command"

Write-Host "Removing context menu..." -ForegroundColor Cyan

$removed = $false

if (Test-Path $commandKey) {
    Remove-Item -Path $commandKey -Recurse -Force
    Write-Host "  Removed: $commandKey"
    $removed = $true
}

if (Test-Path $shellKey) {
    Remove-Item -Path $shellKey -Recurse -Force
    Write-Host "  Removed: $shellKey"
    $removed = $true
}

if ($removed) {
    Write-Host ""
    Write-Host "Context menu uninstalled successfully." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Context menu was not installed (registry keys not found)." -ForegroundColor Yellow
}
