<#
.SYNOPSIS
    Build PDF Metadata Editor into a Windows executable.

.DESCRIPTION
    Creates/activates a virtual environment, installs dependencies,
    optionally generates an icon, then runs PyInstaller.

.PARAMETER Clean
    Delete the dist/ and build/ directories before building.

.PARAMETER SkipIcon
    Skip generating the application icon (uses a placeholder if missing).

.EXAMPLE
    .\build.ps1
    .\build.ps1 -Clean
#>
param(
    [switch]$Clean,
    [switch]$SkipIcon
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$VenvDir     = Join-Path $ProjectRoot ".venv"
$DistDir     = Join-Path $ProjectRoot "dist"
$BuildDir    = Join-Path $ProjectRoot "build"
$AssetsDir   = Join-Path $ProjectRoot "assets"
$IconPath    = Join-Path $AssetsDir "app_icon.ico"

function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Fail([string]$msg) {
    Write-Host "ERROR: $msg" -ForegroundColor Red
    exit 1
}

# --- Require Python 3.12+ ---
Write-Step "Checking Python version"
$pythonExe = "python"
try {
    $verOutput = & $pythonExe --version 2>&1
    Write-Host $verOutput
    if ($verOutput -notmatch "Python 3\.(1[2-9]|[2-9]\d)") {
        Fail "Python 3.12 or later is required. Found: $verOutput"
    }
} catch {
    Fail "Python not found. Install Python 3.12+ and ensure it is on PATH."
}

# --- Clean ---
if ($Clean) {
    Write-Step "Cleaning previous build artefacts"
    foreach ($dir in @($DistDir, $BuildDir)) {
        if (Test-Path $dir) {
            Remove-Item $dir -Recurse -Force
            Write-Host "  Removed $dir"
        }
    }
}

# --- Virtual environment ---
Write-Step "Setting up virtual environment"
if (-not (Test-Path $VenvDir)) {
    & $pythonExe -m venv $VenvDir
}
$pip    = Join-Path $VenvDir "Scripts\pip.exe"
$python = Join-Path $VenvDir "Scripts\python.exe"

Write-Step "Installing / upgrading dependencies"
& $pip install --upgrade pip --quiet
& $pip install -r (Join-Path $ProjectRoot "requirements.txt") --quiet
& $pip install -r (Join-Path $ProjectRoot "requirements-dev.txt") --quiet

# --- Icon ---
if (-not $SkipIcon) {
    Write-Step "Generating application icon"
    if (-not (Test-Path $IconPath)) {
        $iconScript = Join-Path $AssetsDir "create_icon.py"
        if (Test-Path $iconScript) {
            & $python $iconScript
            if (Test-Path $IconPath) {
                Write-Host "  Icon created at $IconPath"
            } else {
                Write-Host "  Icon script ran but produced no file - continuing without icon." -ForegroundColor Yellow
            }
        } else {
            Write-Host "  No create_icon.py found - continuing without icon." -ForegroundColor Yellow
        }
    } else {
        Write-Host "  Icon already exists."
    }
}

if (-not (Test-Path $IconPath)) {
    Write-Host "  Warning: app_icon.ico not found - build will succeed but with no icon." -ForegroundColor Yellow
}

# --- Run PyInstaller ---
Write-Step "Running PyInstaller"
$specFile = Join-Path $ProjectRoot "pdf_metadata_editor.spec"
& $python -m PyInstaller $specFile --noconfirm

if (-not $?) {
    Fail "PyInstaller failed."
}

# --- Report ---
$exePath = Join-Path $DistDir "PDFMetadataEditor\PDFMetadataEditor.exe"
if (Test-Path $exePath) {
    Write-Host ""
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable: $exePath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Test:    & '$exePath' 'C:\path\to\sample.pdf'"
    Write-Host "  2. Install context menu: .\install_context_menu.ps1 -ExePath '$exePath'"
} else {
    Fail "Build completed but executable not found at expected path: $exePath"
}
