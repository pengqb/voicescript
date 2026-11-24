@echo off
setlocal
set "APP_DIR=%~dp0"
set "PYTHON=%APP_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Dependencies are not installed. Run: %APP_DIR%setup.bat 1>&2
    exit /b 1
)

if "%~1"=="" (
    echo Usage: %~nx0 ^<audio.mp3^> [-o output.txt] [--timestamps] [--overwrite] 1>&2
    exit /b 1
)

"%PYTHON%" "%APP_DIR%transcribe.py" %*
exit /b %errorlevel%
