@echo off
if not exist index.html.txt (
  echo index.html.txt not found in this folder
  pause & exit /b 1
)
python patch_sushi.py index.html.txt
if errorlevel 1 ( pause & exit /b 1 )
move /Y index.fixed.html index.html >nul
echo.
echo Done - open index.html in your browser.
pause
