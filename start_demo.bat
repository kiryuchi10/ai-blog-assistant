@echo off
echo Starting AI Blog Assistant Demo...

echo.
echo Starting Backend Server...
start "Backend" cmd /k "cd backend && python demo_server.py"

echo.
echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting Frontend Development Server...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo Demo servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul