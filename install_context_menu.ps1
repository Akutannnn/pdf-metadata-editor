<#
.SYNOPSIS
    Install "Edit metadata" right-click context menu for .pdf files.

.DESCRIPTION
    Registers a per-user HKCU registry entry so that right-clicking any
    .pdf file in Windows Explorer shows "Edit metadata".  No administrator
    privileges are required.

.PARAMETER ExePath
    Full path to PDFMetadataEditor.exe (built by build.ps1).
    If omitted, the script looks for the executable relative to its own
    location: .\dist\PDFMetadataEditor\PDFMetadataEditor.exe

.EXAMPLE
    .\install_context_menu.ps1
    .\install_context_menu.ps1 -ExePath "C:\Tools\PDFMetadataEditor\PDFMetadataEditor.exe"

.NOTES
    Registry key written:
        HKCU\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata
        HKCU\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata\command

    To uninstall run: .\uninstall_context_menu.ps1
#>
param(
    [string]$ExePath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Resolve executable path ---
if (-not $ExePath) {
    $defaultExe = Join-Path $PSScriptRoot "dist\PDFMetadataEditor\PDFMetadataEditor.exe"
    if (Test-Path $defaultExe) {
        $ExePath = $defaultExe
    } else {
        Write-Host "ERROR: Could not find PDFMetadataEditor.exe." -ForegroundColor Red
        Write-Host ""
        Write-Host "Either:"
        Write-Host "  1. Build the app first:   .\build.ps1"
        Write-Host "  2. Supply the path:       .\install_context_menu.ps1 -ExePath <path>"
        exit 1
    }
}

# Resolve to absolute path with proper quoting
$ExePath = (Resolve-Path $ExePath).Path
if (-not (Test-Path $ExePath)) {
    Write-Host "ERROR: Executable not found: $ExePath" -ForegroundColor Red
    exit 1
}

Write-Host "Installing context menu..." -ForegroundColor Cyan
Write-Host "  Executable : $ExePath"

# --- Registry keys ---
$shellKey   = "HKCU:\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata"
$commandKey = "$shellKey\command"
$label      = "Edit metadata"
$command    = "`"$ExePath`" `"%1`""

# Create the shell entry
if (-not (Test-Path $shellKey)) {
    New-Item -Path $shellKey -Force | Out-Null
}
Set-ItemProperty -Path $shellKey -Name "(Default)" -Value $label
Set-ItemProperty -Path $shellKey -Name "Icon"      -Value "`"$ExePath`""

# Create the command entry
if (-not (Test-Path $commandKey)) {
    New-Item -Path $commandKey -Force | Out-Null
}
Set-ItemProperty -Path $commandKey -Name "(Default)" -Value $command

Write-Host ""
Write-Host "Context menu installed successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Right-click any .pdf file in Windows Explorer to see 'Edit metadata'."
Write-Host ""
Write-Host "Registry key:"
Write-Host "  $shellKey"
Write-Host ""
Write-Host "To uninstall: .\uninstall_context_menu.ps1"
