@echo off
title Building Meeting Transcription System - Windows Installer

echo.
echo ========================================
echo Building Meeting Transcription System
echo    Windows Easy Installer
echo ========================================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Running as administrator is recommended
    echo Right-click and select "Run as administrator"
    echo.
    pause
)

:: Check Python
echo Checking Python environment...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: Python not found
    echo.
    echo Python Installation Steps:
    echo 1. Visit https://www.python.org/downloads/release/python-31210/
    echo 2. Download "Windows installer (64-bit)"
    echo 3. During installation, CHECK "Add python.exe to PATH"
    echo 4. After installation, run this script again
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python detected: %PYTHON_VERSION%

:: Create working directory
set INSTALL_DIR=%USERPROFILE%\Desktop\building-meeting-transcriber
echo.
echo Installation directory: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo OK: Directory created
) else (
    echo OK: Using existing directory
)

cd /d "%INSTALL_DIR%"

:: Download from GitHub
set PROJECT_DIR=%INSTALL_DIR%\meetingnote

if not exist "%PROJECT_DIR%" (
    echo.
    echo Downloading project files...
    
    :: Check if Git is available
    git --version >nul 2>&1
    if %errorLevel% equ 0 (
        echo Using Git to clone...
        git clone https://github.com/aiboy2000/meetingnote.git
        if %errorLevel% equ 0 (
            echo OK: Cloned from GitHub
        ) else (
            echo ERROR: Git clone failed
            goto MANUAL_DOWNLOAD
        )
    ) else (
        :MANUAL_DOWNLOAD
        echo.
        echo WARNING: Git not found. Manual download required
        echo.
        echo Manual Download Steps:
        echo 1. Visit https://github.com/aiboy2000/meetingnote
        echo 2. Click "Code" button, then "Download ZIP"
        echo 3. Extract ZIP file to %INSTALL_DIR%
        echo 4. Rename folder to "meetingnote"
        echo 5. Press any key after completion
        echo.
        pause
        
        if not exist "%PROJECT_DIR%" (
            echo ERROR: Project folder not found
            echo Please complete manual download and run again
            pause
            exit /b 1
        )
    )
) else (
    echo OK: Using existing project
)

cd /d "%PROJECT_DIR%"

:: Create virtual environment
echo.
echo Setting up virtual environment...

if not exist "meeting_env" (
    python -m venv meeting_env
    if %errorLevel% equ 0 (
        echo OK: Virtual environment created
    ) else (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo OK: Using existing virtual environment
)

:: Activate virtual environment
call meeting_env\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo OK: Virtual environment activated

:: Install packages
echo.
echo Installing required packages...

:: Upgrade pip
python -m pip install --upgrade pip --quiet

:: Basic packages
echo Installing: Gradio...
python -m pip install gradio==4.44.0 --quiet
if %errorLevel% equ 0 (
    echo OK: Gradio installation completed
) else (
    echo ERROR: Gradio installation failed
)

:: Optional packages
echo.
set /p INSTALL_EXTRA="Install additional packages (PDF processing etc.)? (y/n): "
if /i "%INSTALL_EXTRA%"=="y" (
    echo Installing additional packages...
    python -m pip install pdfplumber pandas requests --quiet
    echo OK: Additional packages completed
)

:: Test installation
echo.
echo Testing installation...
python -c "import gradio; print('OK: Gradio test successful')" 2>nul
if %errorLevel% neq 0 (
    echo ERROR: Gradio test failed
)

:: Create startup script
echo.
echo Creating startup script...

set START_SCRIPT=%INSTALL_DIR%\start_app.bat
echo @echo off > "%START_SCRIPT%"
echo cd /d "%PROJECT_DIR%" >> "%START_SCRIPT%"
echo call meeting_env\Scripts\activate.bat >> "%START_SCRIPT%"
echo echo Starting Building Meeting Transcription System... >> "%START_SCRIPT%"
echo python workflow_app.py >> "%START_SCRIPT%"
echo pause >> "%START_SCRIPT%"

echo OK: Startup script created: %START_SCRIPT%

:: Create desktop shortcut
set /p CREATE_SHORTCUT="Create desktop shortcut? (y/n): "
if /i "%CREATE_SHORTCUT%"=="y" (
    :: Create shortcut using PowerShell
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Building Meeting System.lnk'); $Shortcut.TargetPath = '%START_SCRIPT%'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'Building Meeting Transcription System'; $Shortcut.Save()" 2>nul
    if %errorLevel% equ 0 (
        echo OK: Desktop shortcut created
    ) else (
        echo WARNING: Shortcut creation failed (insufficient permissions)
    )
)

:: Completion message
echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installation location: %PROJECT_DIR%
echo Startup script: %START_SCRIPT%
echo.
echo How to start:
echo   1. Double-click "Building Meeting System" on desktop
echo   2. Or double-click %START_SCRIPT%
echo.
echo Manual: WINDOWS_INSTALL_GUIDE.md
echo Troubleshooting: python check_env.py
echo.

:: Test run option
set /p RUN_TEST="Run test now? (y/n): "
if /i "%RUN_TEST%"=="y" (
    echo.
    echo Starting application...
    python workflow_app.py
)

echo.
echo Installation complete! Press any key to exit...
pause >nul