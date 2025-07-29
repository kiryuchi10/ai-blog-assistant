#!/usr/bin/env python3
"""
Test script for AI Blog Assistant Demo
"""

import requests
import json
import time

def test_backend():
    """Test if backend is running and responding"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AI Blog Assistant Backend...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not responding: {e}")
        return False
    
    # Test demo content generation
    try:
        response = requests.post(f"{base_url}/api/v1/content/demo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Demo content generation works")
            print(f"   Content length: {len(data.get('demo_content', ''))}")
            print(f"   Word count: {data.get('metadata', {}).get('word_count', 0)}")
        else:
            print(f"❌ Demo content failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Demo content request failed: {e}")
        return False
    
    # Test content generation with custom input
    try:
        test_data = {
            "title": "Test AI Blog Assistant",
            "content": "This is a test of the AI blog assistant functionality",
            "tone": "professional",
            "format_type": "linkedin",
            "include_hashtags": True,
            "include_seo": True
        }
        
        response = requests.post(
            f"{base_url}/api/v1/content/generate", 
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Custom content generation works")
            print(f"   Generated content preview: {data.get('content', '')[:100]}...")
        else:
            print(f"❌ Custom content failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Custom content request failed: {e}")
        return False
    
    print("\n🎉 All backend tests passed!")
    return True

def show_demo_content():
    """Show the demo LinkedIn post content"""
    print("\n📝 Demo LinkedIn Post Content:")
    print("=" * 50)
    
    demo_content = '''🚀 AI Blog Assistant: Automating the Future of Technical Content

Following up on my goal to build a modular AI-powered innovation lab, I'm excited to introduce the AI Blog Assistant—a tool I built to automate the creation of research summaries, technical blogs, and SEO-ready content.

🧠 Why I Built It
As developers, we spend countless hours digesting technical papers, experimenting, and writing documentation. But sharing our insights publicly often takes a back seat. The AI Blog Assistant solves this by turning structured notes, papers, or ideas into coherent, high-quality blog posts—automatically.

🛠 What It Does
✅ Takes input (bullet points, markdown notes, or PDFs)
✅ Uses GPT to generate summaries, tutorials, or commentary in a chosen tone (explanatory, concise, humorous, etc.)
✅ Automatically embeds key terms, links, and SEO meta-structure
✅ Supports one-click publishing (Notion/Markdown export ready)

📈 Impact on Workflow
✅ Reduced blog creation time by 70%
✅ Enabled daily posting with consistent quality
✅ Increased knowledge retention by forcing structured summarization
✅ Opened the door to multi-language publishing & cross-platform sharing

🌐 Tech Stack
React · GPT API · SEO Schema · Markdown Renderer · Flask Backend (soon to be FastAPI)

Coming soon: integration with arXiv, S2ORC, and image captioning via BLIP

🧩 Part of a Bigger System
This assistant is one module of my broader effort to build plug-and-play tools, including:
📊 AI Stock Sentiment Tracker
🧪 AI-Accelerated DOE for Engineering
🖼 3D MCP Model Generator
🎛 UI Mockup Generator

💬 Let's Share Knowledge Better
I believe tech is best advanced not only by building, but by communicating ideas well. This tool is my attempt to bridge that gap—and I'm happy to open-source it or co-develop it further with researchers, bloggers, and dev teams.

🔗 You can see the project (and others) here: 👉 https://lnkd.in/g2EHhQtd

If this resonates with your work or vision, let's connect.

#AI #BlogAutomation #KnowledgeSharing #MachineLearning #FullStackDevelopment #LLM #SEO #DeveloperTools #OpenSource #InnovationLab #GPT4'''
    
    print(demo_content)
    print("=" * 50)
    print(f"Word count: {len(demo_content.split())}")
    print(f"Character count: {len(demo_content)}")
    print(f"Hashtags: {demo_content.count('#')}")
    print(f"Emojis: {len([c for c in demo_content if ord(c) > 127])}")

if __name__ == "__main__":
    print("🚀 AI Blog Assistant Demo Test")
    print("=" * 40)
    
    # Show the demo content first
    show_demo_content()
    
    # Test backend if it's running
    print("\n🔧 Testing Backend Connection...")
    if test_backend():
        print("\n✅ Demo is ready!")
        print("\n📋 Next Steps:")
        print("1. Frontend: http://localhost:3000")
        print("2. Backend: http://localhost:8000")
        print("3. Login with: demo@example.com / demo123")
        print("4. Go to Content Generation page")
        print("5. Click 'Load Demo Content' button")
    else:
        print("\n⚠️  Backend not running. Start it with:")
        print("   cd backend && python demo_server.py")
        print("\n📋 Demo content is still available above!")