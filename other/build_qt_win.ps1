Param(
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
Write-Host "Building Shop Manager Pro Qt (Windows standalone)..." -ForegroundColor Cyan

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Clean previous build artifacts if requested
if ($Clean) {
    if (Test-Path build) { Remove-Item build -Recurse -Force }
    if (Test-Path dist) { Remove-Item dist -Recurse -Force }
}

# Ensure pip and PyInstaller are available
python -m pip install --upgrade pip
python -m pip install pyinstaller

# Bundle additional data (locales)
$addDataWin = "locales;locales"  # Windows uses ';' for src;dest

# Build one-file, windowed executable
pyinstaller --noconfirm --clean --onefile --windowed `
    --name ShopManagerPro `
    --add-data $addDataWin `
    --hidden-import PyQt6 `
    --hidden-import PyQt6.QtCore `
    --hidden-import PyQt6.QtGui `
    --hidden-import PyQt6.QtWidgets `
    "shop_manager_pro_qt.py"

Write-Host "Build complete. Output: dist\ShopManagerPro.exe" -ForegroundColor Green
