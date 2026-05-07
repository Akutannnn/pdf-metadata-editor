<#
.SYNOPSIS
    Run PDF Metadata Editor from source (development mode).

.PARAMETER PdfPath
    Optional path to a PDF file to open immediately.

.PARAMETER Debug
    Enable verbose debug logging.

.EXAMPLE
    .\run_dev.ps1
    .\run_dev.ps1 -PdfPath "C:\Documents\sample.pdf"
    .\run_dev.ps1 -Debug
#>
param(
    [string]$PdfPath = "",
    [switch]$Debug
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$VenvDir     = Join-Path $ProjectRoot ".venv"

# Bootstrap venv if it doesn't exist yet
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $VenvDir
    & (Join-Path $VenvDir "Scripts\pip.exe") install -r (Join-Path $ProjectRoot "requirements.txt") --quiet
}

$python = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$args = @((Join-Path $ProjectRoot "main.py"))
if ($PdfPath) { $args += $PdfPath }
if ($Debug)   { $args += "--debug" }

Write-Host "Starting PDF Metadata Editor..." -ForegroundColor Cyan
& $python @args
