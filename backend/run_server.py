#!/usr/bin/env python3
"""
Simple server runner for AI Blog Assistant backend
Fixes the relative import issue by running from the correct directory
"""

import sys
import os
import uvicorn

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("🚀 Starting AI Blog Assistant Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔧 Health check at: http://localhost:8000/health")
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )