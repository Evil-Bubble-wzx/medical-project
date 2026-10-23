$ErrorActionPreference='Stop'
$patientRoot=Split-Path -Parent $PSScriptRoot
& (Join-Path $patientRoot '.venv/Scripts/python.exe') (Join-Path $PSScriptRoot 'recover_patient_login.py')
if ($LASTEXITCODE -ne 0) { throw 'Patient credential recovery failed. No password was displayed.' }
$patientCredentialPath=Join-Path $patientRoot 'var/doctor-trial/patient-login.xml'
$patientPreviousPassword=$env:ENT_PATIENT_TRIAL_PASSWORD
try {
 if (Test-Path -LiteralPath $patientCredentialPath) {
  $patientSecure=Import-Clixml -LiteralPath $patientCredentialPath
  if ($patientSecure -isnot [Security.SecureString]) { throw 'Invalid patient credential format.' }
 } else { $patientSecure=ConvertTo-SecureString ([Guid]::NewGuid().ToString('N')+'-Patient') -AsPlainText -Force }
 $patientPointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($patientSecure)
 try { $env:ENT_PATIENT_TRIAL_PASSWORD=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($patientPointer) }
 finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($patientPointer) }
 & (Join-Path $patientRoot '.venv/Scripts/python.exe') (Join-Path $PSScriptRoot 'prepare_patient_trial.py')
 if ($LASTEXITCODE -ne 0) { throw 'Patient initialization failed. Existing account was not overwritten.' }
 $patientSecure | Export-Clixml -LiteralPath $patientCredentialPath
} finally { $env:ENT_PATIENT_TRIAL_PASSWORD=$patientPreviousPassword }
