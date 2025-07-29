@echo off
echo 🚀 Starting AI Blog Assistant Backend Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist ".venv" (
    echo 📦 Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found, using system Python
)

REM Install dependencies if needed
if not exist "requirements.txt" (
    echo ⚠️  requirements.txt not found, continuing anyway...
) else (
    echo 📦 Installing/updating dependencies...
    pip install -r requirements.txt
)

REM Start the server
echo.
echo 🎯 Starting server...
echo 📍 Server will be available at: http://localhost:8000
echo 📖 API docs at: http://localhost:8000/docs
echo 🔧 Health check at: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python start.py simple

pause