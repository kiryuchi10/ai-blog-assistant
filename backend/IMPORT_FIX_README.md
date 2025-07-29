# AI Blog Assistant Backend - Import Fix Guide

This guide explains how to fix the "attempted relative import with no known parent package" error and get the backend running properly.

## 🚨 The Problem

When you run `python main.py` from the `app` directory, you get:
```
ImportError: attempted relative import with no known parent package
```

This happens because Python can't resolve relative imports when running a script directly.

## ✅ Solutions (Multiple Options)

### Option 1: Use the Simple Server (Recommended)
```bash
# Navigate to backend directory
cd ai-blog-assistant/ai-blog-assistant/backend

# Run the simple server (no complex imports)
python simple_server.py
```

### Option 2: Use the Startup Script
```bash
# Navigate to backend directory
cd ai-blog-assistant/ai-blog-assistant/backend

# Run the startup script (handles everything automatically)
python start.py

# Or for full features (if all modules are configured)
python start.py full
```

### Option 3: Use the Batch File (Windows)
```bash
# Navigate to backend directory
cd ai-blog-assistant/ai-blog-assistant/backend

# Double-click or run
start.bat
```

### Option 4: Run as Module (Advanced)
```bash
# Navigate to backend directory
cd ai-blog-assistant/ai-blog-assistant/backend

# Run the app as a module
python -m app.main
```

### Option 5: Use the Fixed Run Server
```bash
# Navigate to backend directory
cd ai-blog-assistant/ai-blog-assistant/backend

# Use the fixed runner
python run_server.py
```

## 🔧 What Each Solution Provides

### Simple Server (`simple_server.py`)
- ✅ No complex imports - works immediately
- ✅ All basic API endpoints
- ✅ Mock content generation
- ✅ User authentication endpoints
- ✅ Template management
- ✅ CORS configured for frontend
- ✅ Automatic API documentation at `/docs`

**Endpoints Available:**
- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /api/v1/content/generate` - Generate blog content
- `GET /api/v1/content/templates` - Get content templates
- `GET /api/v1/content/history` - Get content history
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/user/profile` - User profile

### Startup Script (`start.py`)
- ✅ Automatic dependency checking and installation
- ✅ Environment setup
- ✅ Fallback to simple server if full server fails
- ✅ Multiple startup modes
- ✅ Comprehensive error handling

### Full Server (`app/main.py`)
- ✅ Complete FastAPI application
- ✅ Database integration
- ✅ Advanced authentication
- ✅ All enterprise features
- ⚠️ Requires all modules to be properly configured

## 📦 Dependencies

Install required packages:
```bash
pip install fastapi uvicorn pydantic sqlalchemy python-dotenv
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## 🌐 Testing the Server

Once the server is running, test these URLs:

1. **Health Check**: http://localhost:8000/health
2. **API Documentation**: http://localhost:8000/docs
3. **Root Endpoint**: http://localhost:8000/

### Test Content Generation
```bash
curl -X POST "http://localhost:8000/api/v1/content/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "The Future of AI",
       "content_type": "blog_post",
       "tone": "professional",
       "length": 500,
       "keywords": ["AI", "technology", "future"]
     }'
```

## 🔍 Troubleshooting

### Issue: "Module not found"
**Solution**: Make sure you're in the backend directory and have installed dependencies
```bash
cd ai-blog-assistant/ai-blog-assistant/backend
pip install fastapi uvicorn pydantic
python simple_server.py
```

### Issue: "Port already in use"
**Solution**: Kill the process using port 8000 or change the port
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: "CORS errors from frontend"
**Solution**: The servers are already configured with CORS for localhost:3000. If you're using a different port, update the CORS origins in the server files.

### Issue: "Import errors persist"
**Solution**: Use the simple server which doesn't have complex imports:
```bash
python simple_server.py
```

## 📁 File Structure

```
backend/
├── app/
│   ├── __init__.py          ✅ Created
│   ├── main.py              ✅ Fixed imports
│   ├── core/
│   │   ├── __init__.py      ✅ Created
│   │   ├── config.py        ✅ Created
│   │   └── database.py      ✅ Created
│   └── api/
│       ├── __init__.py      ✅ Created
│       └── v1/
│           ├── __init__.py  ✅ Created
│           └── api.py       ✅ Created
├── simple_server.py         ✅ New - Works immediately
├── start.py                 ✅ New - Smart startup
├── start.bat                ✅ New - Windows batch file
├── run_server.py            ✅ Fixed - Handles imports
├── requirements.txt         ✅ New - All dependencies
├── .env                     ✅ Configuration
└── .env.example             ✅ Template
```

## 🎯 Recommended Workflow

1. **For Development**: Use `python simple_server.py`
2. **For Testing**: Use `python start.py`
3. **For Production**: Configure the full server with proper database and security

## 🔗 Frontend Integration

The backend is configured to work with the React frontend on `http://localhost:3000`. The CORS settings allow:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:3001`

## 📞 Still Having Issues?

If you're still experiencing problems:

1. **Check Python Version**: Ensure you're using Python 3.8+
   ```bash
   python --version
   ```

2. **Verify Directory**: Make sure you're in the correct directory
   ```bash
   pwd  # Should end with /backend
   ls   # Should show app/, simple_server.py, start.py, etc.
   ```

3. **Clean Install**: Try a fresh dependency install
   ```bash
   pip uninstall fastapi uvicorn pydantic
   pip install fastapi uvicorn pydantic
   ```

4. **Use Virtual Environment**: Create a clean environment
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

The simple server should work in 99% of cases. If it doesn't, there might be a more fundamental Python environment issue.