#!/usr/bin/env python3
"""
Start the working AI Blog Assistant demo
Runs the simple backend and provides instructions for frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start the simple FastAPI backend"""
    print("🚀 Starting AI Blog Assistant Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Start the simple backend server
        process = subprocess.Popen([
            sys.executable, "simple_main.py"
        ], cwd=backend_dir)
        
        print("✅ Backend starting on http://localhost:8000")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def check_frontend():
    """Check if frontend is ready"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ Frontend package.json not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️ Frontend dependencies not installed")
        print("💡 Run: cd frontend && npm install")
        return False
    
    print("✅ Frontend is ready")
    return True

def main():
    """Main function"""
    print("🎯 AI Blog Assistant - Working Demo Starter")
    print("=" * 50)
    
    # Check current directory
    if not Path("backend").exists():
        print("❌ Please run from the ai-blog-assistant root directory")
        return False
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return False
    
    # Wait for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Check frontend
    frontend_ready = check_frontend()
    
    print("\n🎉 Demo Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Backend is running on: http://localhost:8000")
    print("2. Test backend: http://localhost:8000/health")
    print("3. API docs: http://localhost:8000/docs")
    print("")
    
    if frontend_ready:
        print("4. Start frontend in a new terminal:")
        print("   cd frontend")
        print("   npm start")
        print("")
        print("5. Access the app: http://localhost:3000")
        print("6. Click 'Generate Content' → 'Load Demo Content'")
    else:
        print("4. Install frontend dependencies first:")
        print("   cd frontend")
        print("   npm install")
        print("   npm start")
    
    print("\n🎯 Your LinkedIn post is ready to generate!")
    print("\nPress Ctrl+C to stop the backend server")
    
    try:
        # Keep the backend running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Backend stopped")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)