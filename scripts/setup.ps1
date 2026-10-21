$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        & py -3.13 -m venv --without-pip .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create Python 3.13 virtual environment.' }
    }
    # Use the host pip as an installer, but install exclusively into the project venv.
    & py -3.13 -m pip --python '.venv\Scripts\python.exe' install -r requirements.lock
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    Write-Host 'M0 dependencies ready. Run .\scripts\verify.ps1'
} finally { Pop-Location }
