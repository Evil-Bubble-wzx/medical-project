# Run explicitly in your own local terminal. Password is never written to a public file.
$ErrorActionPreference='Stop'
$trialRoot=Split-Path -Parent $PSScriptRoot
$credentialPath=Join-Path $trialRoot 'var\doctor-trial\login.xml'
if (-not (Test-Path -LiteralPath $credentialPath)) { throw 'Run start_doctor_trial.ps1 first.' }
$credential=Import-Clixml -LiteralPath $credentialPath
if ($credential -isnot [Security.SecureString]) { throw 'Invalid encrypted trial login.' }
$pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($credential)
try {
    Write-Host 'Username: doctor-trial'
    Write-Host ('Password: '+[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer))
    Write-Host 'Open: http://127.0.0.1:8012/doctor'
} finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
