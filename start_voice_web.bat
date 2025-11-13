@echo off
REM SHADOW Voice Web Interface Launcher
REM Starts the web server with enhanced voice features

echo.
echo ========================================
echo   SHADOW Voice Web Interface
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Starting SHADOW Web Server...
echo.
echo Web Interface will be available at:
echo   - Enhanced Voice: http://localhost:8000/voice
echo   - API Health:     http://localhost:8000/api/health
echo.
echo Features:
echo   [x] Microphone Access
echo   [x] Simple Mode (Click-to-Talk)
echo   [x] Standard Mode (Always-On Wake Words)
echo   [x] Bilingual Support (English + Hindi)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python src\web\api_server.py

pause
