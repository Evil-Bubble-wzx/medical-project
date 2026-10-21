param([ValidateRange(1024,65535)][int]$Port=8010,[switch]$Reload)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $env:LANGSMITH_TRACING='false'
    $env:LANGCHAIN_TRACING_V2='false'
    $serverArguments=@('-m','uvicorn','app.api.validation:create_validation_app','--factory','--app-dir','backend','--host','127.0.0.1','--port',"$Port",'--no-access-log','--log-level','warning')
    if ($Reload) { $serverArguments+=@('--reload','--reload-dir',(Join-Path $projectRoot 'backend')) }
    & '.\.venv\Scripts\python.exe' @serverArguments
    if ($LASTEXITCODE -ne 0) { throw 'Validation workbench failed to start.' }
} finally { Pop-Location }
