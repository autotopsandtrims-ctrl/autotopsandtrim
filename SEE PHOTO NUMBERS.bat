@echo off
REM Double-click to see every page's photos, numbered, so you know what to
REM name a replacement file.
cd /d "%~dp0"
echo.
echo ==========================================================
echo   PHOTO NUMBERS - name your file page-N.jpg to replace one
echo ==========================================================
python "_build\photo_drop.py" --list
echo.
pause
