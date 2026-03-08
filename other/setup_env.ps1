$ErrorActionPreference = 'Stop'

Set-Location -Path $PSScriptRoot

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Ensure-Python {
    if (Test-Command 'python' -or Test-Command 'py') { return }

    Write-Host 'Python not found. Attempting installation...' -ForegroundColor Yellow

    if (Test-Command 'winget') {
        Write-Host 'Installing Python via winget...' -ForegroundColor Yellow
        winget install -e --id Python.Python.3 --source winget --accept-source-agreements --accept-package-agreements --silent | Out-Null
    } else {
        Write-Host 'winget not available. Downloading Python installer...' -ForegroundColor Yellow
        $version = '3.12.7'
        $url = "https://www.python.org/ftp/python/$version/python-$version-amd64.exe"
        $installer = Join-Path $env:TEMP "python-$version-installer.exe"
        try {
            Invoke-WebRequest $url -OutFile $installer
        } catch {
            throw "Failed to download Python installer from $url. Check your internet connection or proxy settings."
        }
        Write-Host 'Running Python installer...' -ForegroundColor Yellow
        Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 DisablePathLengthLimit=1" -Wait
    }

    if (!(Test-Command 'python') -and !(Test-Command 'py')) {
        throw "Python installation did not complete. Please install Python manually from https://python.org/downloads."
    }
}

Ensure-Python

$venvPath = Join-Path $PSScriptRoot '.venv'
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath" -ForegroundColor Cyan
    if (Test-Command 'python') {
        & python -m venv $venvPath
    } elseif (Test-Command 'py') {
        & py -3 -m venv $venvPath
    } else {
        throw 'Python not available to create a virtual environment.'
    }
}

$venvPython = Join-Path $venvPath 'Scripts\python.exe'

Write-Host 'Upgrading pip in the virtual environment...' -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip

$reqFiles = @(
    Join-Path $PSScriptRoot 'requirements.txt',
    Join-Path $PSScriptRoot 'requirements_ai.txt',
    Join-Path $PSScriptRoot 'buildthon digital fest\requirements.txt'
)

foreach ($req in $reqFiles) {
    if (Test-Path $req) {
        Write-Host "Installing libraries from $req" -ForegroundColor Green
        & $venvPython -m pip install -r $req
    }
}

Write-Host ''
Write-Host 'Setup complete.' -ForegroundColor Green
Write-Host 'To use the environment:'
Write-Host '  - PowerShell: .\\.venv\\Scripts\\Activate.ps1'
Write-Host '  - CMD:       .\\.venv\\Scripts\\activate.bat'

