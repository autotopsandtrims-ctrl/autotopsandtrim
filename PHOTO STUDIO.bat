@echo off
REM Double-click. Opens the drag-and-drop photo studio in your browser.
cd /d "%~dp0"
start "" http://localhost:8732
python "_build\photo_studio.py"
pause
