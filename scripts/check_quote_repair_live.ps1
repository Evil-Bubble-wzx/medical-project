$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$keyPath=Join-Path $projectRoot 'var\secrets\deepseek-api-key.xml'
$previousKey=$env:DEEPSEEK_API_KEY
try {
    $secureKey=Import-Clixml -LiteralPath $keyPath
    if ($secureKey -isnot [Security.SecureString]) { throw 'Invalid encrypted credential format.' }
    $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try { $env:DEEPSEEK_API_KEY=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'check_quote_repair_live.py')
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic quote repair probe did not pass; inspect the redacted report.' }
} finally { $env:DEEPSEEK_API_KEY=$previousKey }
