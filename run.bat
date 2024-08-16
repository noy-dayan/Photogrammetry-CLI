@echo off

:: Set the Command Prompt window size to 170x20
MODE 157,20

:: Set the screen buffer size to 170x1000
:: This needs to be done after setting the window size to ensure the window size doesn't change
powershell -command "$host.ui.rawui.buffersize = new-object management.automation.host.size(157,1000); $host.ui.rawui.windowsize = new-object management.automation.host.size(157,20)"

:: Change to the scripts directory
cd /d "%~dp0scripts"

:: Run the Python script
python run.py

:: Pause to keep the command window open after the script finishes
pause
