$ErrorActionPreference='Stop'
$patientRoot=Split-Path -Parent $PSScriptRoot
& (Join-Path $patientRoot '.venv/Scripts/python.exe') (Join-Path $PSScriptRoot 'recover_patient_login.py')
if ($LASTEXITCODE -ne 0) { throw 'Patient credential recovery failed. No password was displayed.' }
$patientSecure=Import-Clixml -LiteralPath (Join-Path $patientRoot 'var/doctor-trial/patient-login.xml')
$patientPointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($patientSecure)
try { Write-Host 'Username: patient-trial'; Write-Host ('Password: '+[Runtime.InteropServices.Marshal]::PtrToStringBSTR($patientPointer)); Write-Host 'View locally only. Do not share this window.' }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($patientPointer) }
