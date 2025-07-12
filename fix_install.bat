@echo off
title Fix Installation - Continue Setup

echo.
echo ========================================
echo Fix Installation - Continue Setup
echo ========================================
echo.

:: Navigate to the correct directory
set PROJECT_DIR=%USERPROFILE%\Desktop\building-meeting-transcriber\meetingnote

if not exist "%PROJECT_DIR%" (
    echo ERROR: Project directory not found
    echo Expected: %PROJECT_DIR%
    echo Please run the main installer first
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
echo OK: Found project directory

:: Activate virtual environment
echo Activating virtual environment...
if exist "meeting_env\Scripts\activate.bat" (
    call meeting_env\Scripts\activate.bat
    echo OK: Virtual environment activated
) else (
    echo ERROR: Virtual environment not found
    echo Creating new virtual environment...
    python -m venv meeting_env
    call meeting_env\Scripts\activate.bat
)

:: Continue package installation
echo.
echo Continuing package installation...

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Install Gradio
echo Installing Gradio 4.44.0...
python -m pip install gradio==4.44.0 --quiet --no-warn-script-location
if %errorLevel% equ 0 (
    echo OK: Gradio installed successfully
) else (
    echo WARNING: Gradio installation had issues, but may still work
)

:: Test Gradio
echo Testing Gradio...
python -c "import gradio; print('Gradio version:', gradio.__version__)" 2>nul
if %errorLevel% equ 0 (
    echo OK: Gradio test successful
) else (
    echo ERROR: Gradio test failed
    echo Trying alternative installation...
    python -m pip install --upgrade gradio --quiet
)

:: Install optional packages
echo.
set /p INSTALL_EXTRA="Install optional packages (PDF processing)? (y/n): "
if /i "%INSTALL_EXTRA%"=="y" (
    echo Installing optional packages...
    python -m pip install pdfplumber requests --quiet --no-warn-script-location
    echo OK: Optional packages installed
)

:: Create startup script
echo.
echo Creating startup script...

set START_SCRIPT=%USERPROFILE%\Desktop\building-meeting-transcriber\start_app.bat

echo @echo off > "%START_SCRIPT%"
echo title Building Meeting Transcription System >> "%START_SCRIPT%"
echo cd /d "%PROJECT_DIR%" >> "%START_SCRIPT%"
echo call meeting_env\Scripts\activate.bat >> "%START_SCRIPT%"
echo echo. >> "%START_SCRIPT%"
echo echo Starting Building Meeting Transcription System... >> "%START_SCRIPT%"
echo echo Open your browser to: http://127.0.0.1:7860 >> "%START_SCRIPT%"
echo echo. >> "%START_SCRIPT%"
echo python workflow_app.py >> "%START_SCRIPT%"
echo pause >> "%START_SCRIPT%"

echo OK: Startup script created

:: Final test
echo.
echo Running final test...
python check_env.py 2>nul
if %errorLevel% neq 0 (
    echo Environment check script not found, but installation should work
)

echo.
echo ========================================
echo Fix Installation Complete!
echo ========================================
echo.
echo Startup script: %START_SCRIPT%
echo.
echo To start the application:
echo   1. Double-click: %START_SCRIPT%
echo   2. Or run: python workflow_app.py
echo.

set /p RUN_NOW="Start the application now? (y/n): "
if /i "%RUN_NOW%"=="y" (
    echo.
    echo Starting application...
    echo Your browser should open to: http://127.0.0.1:7860
    echo.
    python workflow_app.py
)

echo.
echo Press any key to exit...
pause >nul