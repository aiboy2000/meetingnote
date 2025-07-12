@echo off
title Quick Fix for Gradio Issues

echo.
echo ========================================
echo Quick Fix for Gradio Issues
echo ========================================
echo.

:: Navigate to project directory
cd /d C:\Users\dmkd3\Desktop\building-meeting-transcriber\meetingnote

:: Activate virtual environment
echo Activating virtual environment...
call meeting_env\Scripts\activate

:: Fix Gradio version issue
echo.
echo Fixing Gradio version issue...
python -m pip uninstall gradio gradio-client -y
python -m pip install gradio==4.44.1 --quiet
echo OK: Gradio updated to 4.44.1

:: Test with stable version
echo.
echo Testing stable version...
python -c "import gradio; print('Gradio version:', gradio.__version__)"

:: Start stable workflow app
echo.
echo Starting stable workflow application...
echo This version avoids file upload issues that cause errors
echo.

python stable_workflow.py

echo.
echo If the stable version doesn't work, try:
echo python simple_workflow.py
echo.
pause