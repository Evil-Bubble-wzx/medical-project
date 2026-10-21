$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    & '.\.venv\Scripts\ruff.exe' check backend scripts
    if ($LASTEXITCODE -ne 0) { throw 'Lint failed.' }
    & '.\.venv\Scripts\ruff.exe' format --check backend scripts
    if ($LASTEXITCODE -ne 0) { throw 'Format check failed.' }
    & '.\.venv\Scripts\python.exe' -m pytest
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
    & '.\scripts\evaluate.ps1'
    if ($LASTEXITCODE -ne 0) { throw 'Evaluation failed.' }
} finally { Pop-Location }
