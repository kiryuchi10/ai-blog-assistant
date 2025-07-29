"""
Content Generation API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.services.content_generation_service import ContentGenerationService
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class ContentGenerationRequest(BaseModel):
    title: str
    content: str
    tone: str = 'professional'
    format_type: str = 'linkedin'
    include_hashtags: bool = True
    include_seo: bool = True

class ContentGenerationResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SEOMetadataRequest(BaseModel):
    content: str
    title: str

class ImprovementRequest(BaseModel):
    content: str

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered content based on user input
    """
    try:
        service = ContentGenerationService()
        
        result = service.generate_content(
            title=request.title,
            content=request.content,
            tone=request.tone,
            format_type=request.format_type,
            include_hashtags=request.include_hashtags,
            include_seo=request.include_seo
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Content generation failed'))
        
        return ContentGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during content generation")

@router.post("/seo-metadata")
async def generate_seo_metadata(
    request: SEOMetadataRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate SEO metadata for content
    """
    try:
        service = ContentGenerationService()
        metadata = service.generate_seo_metadata(request.content, request.title)
        
        return {
            'success': True,
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"SEO metadata generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate SEO metadata")

@router.post("/suggestions")
async def get_content_suggestions(
    request: ImprovementRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get suggestions for improving content
    """
    try:
        service = ContentGenerationService()
        suggestions = service.suggest_improvements(request.content)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Content suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")

@router.get("/templates")
async def get_content_templates():
    """
    Get available content templates
    """
    from app.services.content_generation_service import CONTENT_TEMPLATES
    
    return {
        'success': True,
        'templates': CONTENT_TEMPLATES
    }

@router.post("/demo")
async def generate_demo_content():
    """
    Generate demo content for the AI Blog Assistant showcase
    """
    try:
        service = ContentGenerationService()
        
        demo_request = {
            'title': 'AI Blog Assistant: Automating the Future of Technical Content',
            'content': '''Following up on my goal to build a modular AI-powered innovation lab, I'm excited to introduce the AI Blog Assistant—a tool I built to automate the creation of research summaries, technical blogs, and SEO-ready content.

Key features:
- Takes input (bullet points, markdown notes, or PDFs)
- Uses GPT to generate summaries, tutorials, or commentary in chosen tone
- Automatically embeds key terms, links, and SEO meta-structure
- Supports one-click publishing (Notion/Markdown export ready)

Impact:
- Reduced blog creation time by 70%
- Enabled daily posting with consistent quality
- Increased knowledge retention by forcing structured summarization
- Opened door to multi-language publishing & cross-platform sharing

Tech Stack: React · GPT API · SEO Schema · Markdown Renderer · Flask Backend

Part of bigger system including:
- AI Stock Sentiment Tracker
- AI-Accelerated DOE for Engineering
- 3D MCP Model Generator
- UI Mockup Generator''',
            'tone': 'professional',
            'format_type': 'linkedin',
            'include_hashtags': True,
            'include_seo': True
        }
        
        result = service.generate_content(**demo_request)
        
        return {
            'success': True,
            'demo_content': result['content'],
            'metadata': result.get('metadata', {}),
            'message': 'Demo content generated successfully'
        }
        
    except Exception as e:
        logger.error(f"Demo content generation error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'fallback_content': '''🚀 AI Blog Assistant: Automating the Future of Technical Content

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
        }