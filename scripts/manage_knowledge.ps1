param([Parameter(ValueFromRemainingArguments=$true)][string[]]$CliArgs)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$previousPythonPath = $env:PYTHONPATH
Push-Location $projectRoot
try {
    $env:PYTHONPATH = Join-Path $projectRoot 'backend'
    & '.\.venv\Scripts\python.exe' -m app.knowledge.manage @CliArgs
    if ($LASTEXITCODE -ne 0) { throw 'M1 knowledge management command failed.' }
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
