param([Parameter(ValueFromRemainingArguments=$true)][string[]]$CliArgs)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$previousPythonPath = $env:PYTHONPATH
Push-Location $projectRoot
try {
    $env:PYTHONPATH = Join-Path $projectRoot 'backend'
    & '.\.venv\Scripts\python.exe' -m app.retrieval.cli @CliArgs
    if ($LASTEXITCODE -ne 0) { throw 'Retrieval experiment failed; check model/index availability.' }
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
