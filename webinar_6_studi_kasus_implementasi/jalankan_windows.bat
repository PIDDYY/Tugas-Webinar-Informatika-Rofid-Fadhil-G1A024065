@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 main.py
) else (
    python main.py
)
if errorlevel 1 (
    echo.
    echo Terjadi kesalahan. Pastikan Python 3 sudah dipasang.
) else (
    echo.
    echo Hasil tersimpan. Buka hasil\dashboard_hasil.html di browser.
)
pause
