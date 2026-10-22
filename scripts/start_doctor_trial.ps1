param([ValidateRange(1024,65535)][int]$Port=8012,[switch]$NoReload,[switch]$PromptForKey)
$ErrorActionPreference='Stop'
$trialRoot=Split-Path -Parent $PSScriptRoot
$credentialPath=Join-Path $trialRoot 'var\doctor-trial\login.xml'
$previousPassword=$env:ENT_TRIAL_PASSWORD
$previousTrialMode=$env:ENT_DOCTOR_TRIAL
try {
    New-Item -ItemType Directory -Path (Split-Path -Parent $credentialPath) -Force | Out-Null
    if (Test-Path -LiteralPath $credentialPath) {
        $trialCredential=Import-Clixml -LiteralPath $credentialPath
        if ($trialCredential -isnot [Security.SecureString]) { throw 'Invalid encrypted trial login.' }
    } else {
        if (Test-Path -LiteralPath (Join-Path $trialRoot 'var\doctor-trial\business.sqlite3')) { throw 'Trial database exists but encrypted login is missing. Stop to avoid overwriting an account.' }
        $trialCredential=ConvertTo-SecureString ([Guid]::NewGuid().ToString('N')+'-Trial') -AsPlainText -Force
        $trialCredential | Export-Clixml -LiteralPath $credentialPath
    }
    $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($trialCredential)
    try { $env:ENT_TRIAL_PASSWORD=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    & (Join-Path $trialRoot '.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'prepare_doctor_trial.py')
    if ($LASTEXITCODE -ne 0) { throw 'Doctor trial initialization failed; existing records were preserved.' }
    $env:ENT_TRIAL_PASSWORD=$null
    $env:ENT_DOCTOR_TRIAL='1'
    Write-Host ('Doctor trial: http://127.0.0.1:'+ $Port +'/doctor')
    Write-Host 'Username: doctor-trial. Use scripts\show_doctor_trial_login.ps1 locally to view the password.'
    & (Join-Path $PSScriptRoot 'start_with_deepseek.ps1') -Port $Port -NoReload:$NoReload -PromptForKey:$PromptForKey
} finally {
    $env:ENT_TRIAL_PASSWORD=$previousPassword
    $env:ENT_DOCTOR_TRIAL=$previousTrialMode
}
