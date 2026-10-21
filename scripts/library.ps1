param(
    [ValidateSet('collect', 'build', 'status', 'search')][string]$Action = 'status',
    [string]$Query = '', [ValidateRange(1,20)][int]$Limit = 5, [string]$Topic = ''
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$previousPythonPath = $env:PYTHONPATH
Push-Location $projectRoot
try {
    $env:PYTHONPATH = Join-Path $projectRoot 'backend'
    $cliArgs = @('-m', 'app.knowledge.cli', $Action)
    if ($Action -eq 'search') {
        if (-not $Query) { throw 'Provide -Query for search.' }
        $cliArgs += @($Query, '--limit', $Limit)
        if ($Topic) { $cliArgs += @('--topic', $Topic) }
    }
    & '.\.venv\Scripts\python.exe' @cliArgs
    if ($LASTEXITCODE -ne 0) { throw 'Local corpus operation failed; see manifest failures.' }
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
