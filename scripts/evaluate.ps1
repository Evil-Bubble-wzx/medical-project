param([string]$Config = 'configs/local.toml', [string]$Output = '')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $projectRoot 'backend'
    $evalArgs = @('-m', 'app.evaluation', '--config', $Config)
    if ($Output) { $evalArgs += @('--output', $Output) }
    & '.\.venv\Scripts\python.exe' @evalArgs
    if ($LASTEXITCODE -ne 0) { throw 'M0 engineering evaluation failed.' }
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
