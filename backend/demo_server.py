"""
Demo server for AI Blog Assistant
Simple Flask server to demonstrate the content generation functionality
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import random

app = Flask(__name__)
CORS(app)

# Demo content templates
DEMO_CONTENT = {
    'linkedin': '''🚀 AI Blog Assistant: Automating the Future of Technical Content

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

#AI #BlogAutomation #KnowledgeSharing #MachineLearning #FullStackDevelopment #LLM #SEO #DeveloperTools #OpenSource #InnovationLab #GPT4''',

    'blog': '''# AI Blog Assistant: Automating the Future of Technical Content

## Introduction

Following up on my goal to build a modular AI-powered innovation lab, I'm excited to introduce the AI Blog Assistant—a tool I built to automate the creation of research summaries, technical blogs, and SEO-ready content.

## Why I Built It

As developers, we spend countless hours digesting technical papers, experimenting, and writing documentation. But sharing our insights publicly often takes a back seat. The AI Blog Assistant solves this by turning structured notes, papers, or ideas into coherent, high-quality blog posts—automatically.

## What It Does

The AI Blog Assistant provides several key features:

- **Input Processing**: Takes input (bullet points, markdown notes, or PDFs)
- **AI Generation**: Uses GPT to generate summaries, tutorials, or commentary in a chosen tone
- **SEO Optimization**: Automatically embeds key terms, links, and SEO meta-structure
- **Publishing Ready**: Supports one-click publishing (Notion/Markdown export ready)

## Impact on Workflow

The results have been impressive:

- Reduced blog creation time by 70%
- Enabled daily posting with consistent quality
- Increased knowledge retention by forcing structured summarization
- Opened the door to multi-language publishing & cross-platform sharing

## Tech Stack

- **Frontend**: React with modern UI components
- **AI Integration**: GPT API for content generation
- **SEO**: Schema markup and optimization
- **Content**: Markdown renderer for flexible output
- **Backend**: Flask (migrating to FastAPI)

Coming soon: integration with arXiv, S2ORC, and image captioning via BLIP.

## Part of a Bigger System

This assistant is one module of my broader effort to build plug-and-play tools, including:

- AI Stock Sentiment Tracker
- AI-Accelerated DOE for Engineering
- 3D MCP Model Generator
- UI Mockup Generator

## Conclusion

I believe tech is best advanced not only by building, but by communicating ideas well. This tool is my attempt to bridge that gap—and I'm happy to open-source it or co-develop it further with researchers, bloggers, and dev teams.

---

*Keywords: AI, Blog Automation, Knowledge Sharing, Machine Learning, Full Stack Development, LLM, SEO, Developer Tools, Open Source, Innovation Lab, GPT-4*'''
}

@app.route('/api/v1/content/generate', methods=['POST'])
def generate_content():
    """Generate content based on user input"""
    try:
        data = request.get_json()
        
        # Simulate processing time
        time.sleep(random.uniform(1, 3))
        
        title = data.get('title', '')
        content = data.get('content', '')
        tone = data.get('tone', 'professional')
        format_type = data.get('format_type', 'linkedin')
        include_hashtags = data.get('include_hashtags', True)
        include_seo = data.get('include_seo', True)
        
        # Generate content based on format
        if format_type in DEMO_CONTENT:
            generated_content = DEMO_CONTENT[format_type]
        else:
            generated_content = DEMO_CONTENT['linkedin']
        
        # Customize based on user input
        if title and title != 'AI Blog Assistant: Automating Technical Content':
            generated_content = generated_content.replace(
                'AI Blog Assistant: Automating the Future of Technical Content',
                title
            )
        
        # Add user content if provided
        if content and len(content.strip()) > 10:
            user_section = f"\n\n🎯 Key Points:\n{content}\n"
            # Insert after the first section
            parts = generated_content.split('\n\n', 2)
            if len(parts) >= 2:
                generated_content = parts[0] + '\n\n' + parts[1] + user_section + '\n\n' + '\n\n'.join(parts[2:])
        
        # Adjust tone
        if tone == 'casual':
            generated_content = generated_content.replace('I\'m excited to introduce', 'I\'m super excited to share')
            generated_content = generated_content.replace('Let\'s Share Knowledge Better', 'Let\'s Share Knowledge & Have Fun!')
        elif tone == 'technical':
            generated_content = generated_content.replace('🚀', '⚡')
            generated_content = generated_content.replace('I believe tech is best advanced', 'Technical advancement requires')
        
        return jsonify({
            'success': True,
            'content': generated_content,
            'metadata': {
                'word_count': len(generated_content.split()),
                'character_count': len(generated_content),
                'format': format_type,
                'tone': tone,
                'generated_at': time.time()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/content/demo', methods=['POST'])
def generate_demo_content():
    """Generate demo content"""
    try:
        return jsonify({
            'success': True,
            'demo_content': DEMO_CONTENT['linkedin'],
            'metadata': {
                'word_count': len(DEMO_CONTENT['linkedin'].split()),
                'character_count': len(DEMO_CONTENT['linkedin']),
                'format': 'linkedin',
                'tone': 'professional'
            },
            'message': 'Demo content generated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/content/templates', methods=['GET'])
def get_templates():
    """Get content templates"""
    templates = {
        'project_showcase': {
            'title': '🚀 {project_name}: {brief_description}',
            'structure': [
                'Hook with project announcement',
                'Problem it solves',
                'Key features/capabilities',
                'Tech stack',
                'Results/impact',
                'Call to action'
            ]
        },
        'technical_tutorial': {
            'title': 'Understanding {topic}: A Developer\'s Guide',
            'structure': [
                'Introduction to the problem',
                'Core concepts explained',
                'Step-by-step implementation',
                'Best practices',
                'Common pitfalls',
                'Conclusion and resources'
            ]
        },
        'weekly_insights': {
            'title': 'This Week in {field}: Key Insights',
            'structure': [
                'Week overview',
                'Top discoveries/learnings',
                'Interesting resources found',
                'Industry trends observed',
                'Personal takeaways',
                'What\'s next'
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'templates': templates
    })

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Demo login endpoint"""
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    # Demo authentication
    if email == 'demo@example.com' and password == 'demo123':
        return jsonify({
            'success': True,
            'token': 'demo_token_12345',
            'user': {
                'id': 1,
                'name': 'Demo User',
                'email': 'demo@example.com'
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401

@app.route('/api/v1/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    auth_header = request.headers.get('Authorization', '')
    
    if 'demo_token' in auth_header:
        return jsonify({
            'success': True,
            'user': {
                'id': 1,
                'name': 'Demo User',
                'email': 'demo@example.com'
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Blog Assistant Demo Server',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)