@echo off
REM ============================================================
REM  Hardfox v4.0 - Firefox Hardening Tool
REM  Launcher Script
REM ============================================================

title Hardfox v4.0 Launcher

echo.
echo ============================================================
echo  Hardfox v4.0 - Firefox Hardening Tool
echo  Clean Architecture Edition
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.9+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo [1/3] Checking Python installation...
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo       %PYTHON_VERSION% - OK
echo.

REM Check Python version (requires 3.9+)
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.9 or higher is required
    echo        Current version: %PYTHON_VERSION%
    echo.
    pause
    exit /b 1
)

REM Check for required packages
echo [2/3] Checking dependencies...

REM Check for customtkinter (will be needed for GUI in Phase 4)
python -c "import customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo       [!] customtkinter not installed (will be needed for GUI)
    echo       [*] Installing customtkinter...
    pip install customtkinter --quiet
    if %errorlevel% neq 0 (
        echo       [ERROR] Failed to install customtkinter
        pause
        exit /b 1
    )
    echo       [OK] customtkinter installed
) else (
    echo       [OK] customtkinter installed
)

echo.
echo [3/3] All dependencies satisfied!
echo.
echo ============================================================
echo  Launching Hardfox v4.0...
echo ============================================================

REM Launch the GUI application
python hardfox_gui.py %*

REM Show exit status
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo  Application exited successfully
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo  Application exited with error code: %errorlevel%
    echo ============================================================
)

echo.
pause
