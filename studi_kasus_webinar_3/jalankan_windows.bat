@echo off
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Periksa instalasi Python 3 dan lokasi file input.
    pause
    exit /b 1
)
echo.
echo Hasil tersimpan di folder output.
pause
