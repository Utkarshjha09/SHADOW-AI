@echo off
echo Starting SHADOW Voice Assistant...
echo.

echo Starting React Frontend (Port 3000)...
start "React Frontend" cmd /k "cd /d c:\Document\SHADOW\src\web\react-app && npm run dev"

timeout /t 3 /nobreak >nul

echo Starting Flask Backend (Port 8000)...
start "Flask Backend" cmd /k "cd /d c:\Document\SHADOW && python src\web\api_server.py"

timeout /t 3 /nobreak >nul

echo.
echo ================================
echo SHADOW Voice Assistant Started!
echo ================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo Features:
echo - No OpenAI API key required
echo - Uses Google Web Speech API (free)
echo - Supports Hindi and English
echo - Ollama AI for responses
echo.
echo Wake Words:
echo - "Hey SHADOW" / "Hi SHADOW"
echo - "सुनो SHADOW" / "क्या SHADOW"
echo - "Suno SHADOW" / "Kya SHADOW"
echo.
echo Instructions:
echo 1. Open http://localhost:3000
echo 2. Click microphone button
echo 3. Say a wake word
echo 4. Speak your command
echo 5. Get AI response!
echo.
pause