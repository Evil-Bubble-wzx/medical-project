param([ValidateRange(1024,65535)][int]$Port=8011,[switch]$PromptForKey,[switch]$NoReload)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$keyDirectory=Join-Path $projectRoot 'var\secrets'
$keyPath=Join-Path $keyDirectory 'deepseek-api-key.xml'
$previousKey=$env:DEEPSEEK_API_KEY
try {
    if ($PromptForKey -or (Test-Path -LiteralPath $keyPath) -or -not $env:DEEPSEEK_API_KEY) {
        if (-not $PromptForKey -and (Test-Path -LiteralPath $keyPath)) {
            $secureKey=Import-Clixml -LiteralPath $keyPath
            if ($secureKey -isnot [Security.SecureString]) { throw 'Saved credential format is invalid.' }
            Write-Host 'Loaded Windows-encrypted API key.'
        } else {
            $secureKey=Read-Host 'DeepSeek API key (hidden; encrypted locally after validation)' -AsSecureString
        }
        $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
        try { $env:DEEPSEEK_API_KEY=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer).Trim() }
        finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    }
    if (-not $env:DEEPSEEK_API_KEY) { throw 'API key is required.' }
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'check_deepseek_key.py')
    if ($LASTEXITCODE -ne 0) { throw 'API authentication check failed. Service not started; credential cache unchanged.' }
    New-Item -ItemType Directory -Path $keyDirectory -Force | Out-Null
    $cachedKey=ConvertTo-SecureString $env:DEEPSEEK_API_KEY -AsPlainText -Force
    $cachedKey | Export-Clixml -LiteralPath $keyPath
    Write-Host 'Saved with Windows encryption for this Windows user on this computer.'
    Write-Host ('Open http://127.0.0.1:' + $Port + '/ after startup.')
    & (Join-Path $PSScriptRoot 'start_validation.ps1') -Port $Port -Reload:(-not $NoReload)
} finally { $env:DEEPSEEK_API_KEY=$previousKey }
