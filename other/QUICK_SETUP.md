Quick Setup

- Double-click `setup_env.bat` to install Python (if needed), create a virtual environment, and install libraries.
- The script uses `winget` when available; otherwise it downloads the official Python installer.
- It installs packages from these files when present:
  - `requirements.txt`
  - `requirements_ai.txt`
  - `buildthon digital fest\requirements.txt`

After Setup

- PowerShell: run `\.venv\Scripts\Activate.ps1` to activate the environment.
- CMD: run `\.venv\Scripts\activate.bat` to activate the environment.
- To install more packages later: `\.venv\Scripts\python.exe -m pip install <package>`.

Troubleshooting

- If PowerShell blocks scripts, open PowerShell as Administrator and run: `Set-ExecutionPolicy Bypass -Scope CurrentUser`.
- If `winget` is missing, the script falls back to downloading the Python installer.
- If behind a proxy, set `HTTPS_PROXY` before running the script.

