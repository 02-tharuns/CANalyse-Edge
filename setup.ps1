$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (-not (Test-Path "Automoble")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3.12 -m venv Automoble
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        if ($PythonVersion -ne "3.12") {
            throw "Python 3.12 is required; found Python $PythonVersion."
        }
        python -m venv Automoble
    }
    else {
        throw "Python 3.12 was not found. Install it from python.org, then rerun setup.ps1."
    }
}
& ".\Automoble\Scripts\python.exe" -m pip install --upgrade pip
& ".\Automoble\Scripts\python.exe" -m pip install -r requirements.txt
& ".\Automoble\Scripts\python.exe" -m pip check
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Write-Host "Ready. Activate with: .\Automoble\Scripts\Activate.ps1"
