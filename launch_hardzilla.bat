@echo off
echo ========================================
echo Hardzilla - Firefox Hardening Tool
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if not present
echo Checking dependencies...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo Installing customtkinter...
    pip install customtkinter --quiet
)

pip show pywinstyles >nul 2>&1
if errorlevel 1 (
    echo Installing pywinstyles ^(Windows acrylic effect^)...
    pip install pywinstyles --quiet
)

echo Starting Hardzilla...
echo.
echo FEATURES:
echo - Individual control over each data type
echo - Choose exactly what to keep and what to delete
echo - Session restore settings
echo - Cookie management
echo - Network and security options
echo - Permission controls
echo.

python hardzilla.py

if errorlevel 1 (
    echo.
    echo Hardzilla encountered an error.
    pause
)

exit /b 0
