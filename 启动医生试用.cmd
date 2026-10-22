@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_doctor_trial.ps1" -NoReload
pause
