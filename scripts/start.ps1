param([ValidateRange(1024, 65535)][int]$Port = 8000,
      [string]$Config = 'configs/local.toml')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        throw 'Run .\scripts\setup.ps1 first.'
    }
    if (-not $env:M0_DEMO_TOKEN -or $env:M0_DEMO_TOKEN.Length -lt 24) {
        $env:M0_DEMO_TOKEN = [guid]::NewGuid().ToString('N')
        Write-Host ('Local synthetic demo token (this terminal only): ' + $env:M0_DEMO_TOKEN)
    }
    $env:M0_CONFIG = (Resolve-Path -LiteralPath $Config).Path
    $env:LANGSMITH_TRACING = 'false'
    $env:LANGCHAIN_TRACING_V2 = 'false'
    & '.\.venv\Scripts\python.exe' -m uvicorn app.api.main:create_app --factory --app-dir backend --host 127.0.0.1 --port $Port --no-access-log
    if ($LASTEXITCODE -ne 0) { throw 'M0 API exited with an error.' }
} finally { Pop-Location }
