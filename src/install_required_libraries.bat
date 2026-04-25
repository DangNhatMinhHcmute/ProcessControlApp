@echo off
echo Checking Python and pip...

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not added to PATH.
    pause
    exit /b
)

where pip >nul 2>nul
if errorlevel 1 (
    echo pip is not installed or not added to PATH.
    pause
    exit /b
)

echo Installing required packages...

pip install -r required_libraries.txt

echo.
echo ✅ All required libraries have been installed.
pause
