@echo off
setlocal
set "APP_DIR=%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python Launcher was not found. Install Python 3 and check "py" is available.
    exit /b 1
)

echo Creating Python virtual environment...
py -3 -m venv "%APP_DIR%.venv"
if errorlevel 1 exit /b 1

echo Installing dependencies...
"%APP_DIR%.venv\Scripts\python.exe" -m pip install -r "%APP_DIR%requirements.txt"
if errorlevel 1 exit /b 1

echo Checking Python syntax...
"%APP_DIR%.venv\Scripts\python.exe" -m py_compile "%APP_DIR%transcribe.py"
if errorlevel 1 exit /b 1

echo Setup complete. Run:
echo   %APP_DIR%run.bat "C:\path\to\audio.mp3"
endlocal
