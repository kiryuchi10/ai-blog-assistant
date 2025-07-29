#!/usr/bin/env python3
import requests
import sys

def test_frontend():
    try:
        response = requests.get('http://localhost:3000', timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        print("First 500 characters:")
        print(response.text[:500])
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_backend():
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        print(f"Backend Status Code: {response.status_code}")
        print(f"Backend Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Backend Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Backend...")
    backend_ok = test_backend()
    
    print("\nTesting Frontend...")
    frontend_ok = test_frontend()
    
    if backend_ok and frontend_ok:
        print("\n✅ Both frontend and backend are working!")
        sys.exit(0)
    else:
        print("\n❌ Some services are not working properly")
        sys.exit(1)