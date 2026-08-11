@echo off
REM Double-click this after putting images in the photo-drop folder.
REM Processes them, rebuilds the site, checks it, and puts it live.
cd /d "%~dp0"
echo.
echo ==========================================================
echo   AUTO TOPS AND TRIM - PHOTO UPDATE
echo ==========================================================
echo.
python "_build\photo_drop.py" --push
echo.
echo ==========================================================
pause
