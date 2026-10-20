@echo off
setlocal

cd /d "%~dp0"

set "ROADLENS_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%ROADLENS_PYTHON%" (
    echo [RoadLens] Khong tim thay moi truong Python: %ROADLENS_PYTHON%
    echo Hay cai dat theo huong dan trong README.md.
    pause
    exit /b 1
)

if not defined ROADLENS_DATA set "ROADLENS_DATA=%~dp0du_lieu_tai_nan_2024_san_sang_truc_quan.csv"
if not exist "%ROADLENS_DATA%" (
    echo [RoadLens] Khong tim thay file du lieu: %ROADLENS_DATA%
    pause
    exit /b 1
)

set "ROADLENS_PORT=%~1"
if not defined ROADLENS_PORT set "ROADLENS_PORT=8501"

echo.
echo [RoadLens] Dashboard: http://127.0.0.1:%ROADLENS_PORT%
echo [RoadLens] Nhan Ctrl+C de dung ung dung.
echo.

"%ROADLENS_PYTHON%" -m streamlit run app.py ^
    --server.address 127.0.0.1 ^
    --server.port %ROADLENS_PORT% ^
    --server.headless true ^
    --browser.gatherUsageStats false

set "ROADLENS_EXIT=%ERRORLEVEL%"
if not "%ROADLENS_EXIT%"=="0" (
    echo.
    echo [RoadLens] Streamlit da dung voi ma loi %ROADLENS_EXIT%.
    pause
)

exit /b %ROADLENS_EXIT%
