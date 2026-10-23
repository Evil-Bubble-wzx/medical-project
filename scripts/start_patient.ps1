param([ValidateRange(1024,65535)][int]$Port=8012)
$ErrorActionPreference='Stop'
$patientRoot=Split-Path -Parent $PSScriptRoot
try { $ready=Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 ('http://127.0.0.1:'+ $Port +'/patient') } catch { $ready=$null }
if ($ready -and $ready.StatusCode -eq 200) {
    Start-Process ('http://127.0.0.1:'+ $Port +'/patient')
    Write-Host 'Patient service is already running.'
    exit
}
$openCode='$address="http://127.0.0.1:'+ $Port +'/patient";for($attempt=0;$attempt -lt 90;$attempt++){try{$response=Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 $address;if($response.StatusCode -eq 200){Start-Process $address;exit}}catch{};Start-Sleep -Seconds 1}'
$encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($openCode))
Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$encoded)
& (Join-Path $patientRoot 'scripts/start_doctor_trial.ps1') -Port $Port -NoReload
