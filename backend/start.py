#!/usr/bin/env python3
"""
AI Blog Assistant Backend Startup Script
Handles all import issues and provides multiple startup options
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_environment():
    """Setup the Python environment and paths"""
    # Get the backend directory
    backend_dir = Path(__file__).parent
    
    # Add backend directory to Python path
    sys.path.insert(0, str(backend_dir))
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(backend_dir))
    
    print(f"✅ Environment setup complete")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python path: {sys.path[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to install packages automatically")
            print("Please run: pip install fastapi uvicorn pydantic sqlalchemy")
            return False
    else:
        print("✅ All required packages are installed")
    
    return True

def start_simple_server():
    """Start the simple server (recommended)"""
    print("\n🚀 Starting Simple Server...")
    print("This server doesn't require complex imports and should work immediately.")
    
    try:
        import uvicorn
        # Import and run the simple server
        from simple_server import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start simple server: {e}")
        return False
    
    return True

def start_full_server():
    """Start the full FastAPI server with all features"""
    print("\n🚀 Starting Full Server...")
    print("This requires all modules to be properly configured.")
    
    try:
        import uvicorn
        
        # Try to import the main app
        from app.main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Falling back to simple server...")
        return start_simple_server()
    except Exception as e:
        print(f"❌ Failed to start full server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🎯 AI Blog Assistant Backend Startup")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required packages.")
        sys.exit(1)
    
    # Get startup option from command line or default to simple
    startup_mode = sys.argv[1] if len(sys.argv) > 1 else "simple"
    
    if startup_mode == "full":
        print("\n📋 Starting in FULL mode (all features)")
        success = start_full_server()
    else:
        print("\n📋 Starting in SIMPLE mode (basic features)")
        success = start_simple_server()
    
    if not success:
        print("\n❌ Server startup failed")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you're in the backend directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Try: python start.py simple")
        print("4. Check the .env file configuration")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("\n🆘 Please check the error above and try again")
        sys.exit(1)