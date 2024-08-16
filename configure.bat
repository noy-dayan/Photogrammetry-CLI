@echo off

:: Check if the script is running with administrative privileges
openfiles >nul 2>&1
if '%errorlevel%' neq '0' (
    echo This script requires administrative privileges. Attempting to restart with elevated permissions...
    :: Re-run the batch file as an administrator
    powershell -Command "Start-Process cmd -ArgumentList '/c %~f0' -Verb RunAs"
    exit /b
)

:: Change to the scripts directory
cd /d "%~dp0scripts"

:: Run the configuration Python script
python configure.py

:: Pause to allow user to see output
pause
