#!/usr/bin/env python3
"""
Simple FastAPI server for AI Blog Assistant
Minimal implementation that works without complex imports
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="AI Blog Assistant API",
    description="Simple API for AI-powered blog content generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ContentRequest(BaseModel):
    title: str
    content_type: str = "blog_post"
    tone: str = "professional"
    length: int = 800
    keywords: List[str] = []
    ai_model: str = "gpt-4-turbo-preview"

class ContentResponse(BaseModel):
    title: str
    content: str
    word_count: int
    status: str = "generated"
    ai_model: str

class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    content_type: str

class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Blog Assistant API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "content_generation": "/api/v1/content/generate",
            "templates": "/api/v1/content/templates"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-blog-assistant-api",
        "version": "1.0.0",
        "environment": "development"
    }

# Content generation endpoint
@app.post("/api/v1/content/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """Generate blog content using AI"""
    
    try:
        # Mock content generation (replace with actual AI integration)
        mock_content = generate_mock_content(request)
        
        return ContentResponse(
            title=request.title,
            content=mock_content,
            word_count=len(mock_content.split()),
            ai_model=request.ai_model
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

# Templates endpoint
@app.get("/api/v1/content/templates", response_model=List[TemplateResponse])
async def get_templates():
    """Get available content templates"""
    
    templates = [
        TemplateResponse(
            id="blog_post",
            name="Blog Post",
            description="Standard blog post with introduction, main content, and conclusion",
            content_type="blog_post"
        ),
        TemplateResponse(
            id="article",
            name="Long-form Article",
            description="Detailed article with multiple sections and research-based content",
            content_type="article"
        ),
        TemplateResponse(
            id="social_media",
            name="Social Media Post",
            description="Short, engaging content for social media platforms",
            content_type="social_media"
        ),
        TemplateResponse(
            id="newsletter",
            name="Newsletter",
            description="Email newsletter format with sections and call-to-action",
            content_type="newsletter"
        ),
        TemplateResponse(
            id="product_description",
            name="Product Description",
            description="Compelling product descriptions for e-commerce",
            content_type="product_description"
        )
    ]
    
    return templates

# User authentication endpoints (mock)
@app.post("/api/v1/auth/register")
async def register_user(user: UserRegistration):
    """Register a new user"""
    return {
        "message": "User registered successfully",
        "user_id": "mock_user_123",
        "email": user.email
    }

@app.post("/api/v1/auth/login")
async def login_user(credentials: UserLogin):
    """Login user"""
    return {
        "access_token": "mock_jwt_token_123",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "email": credentials.email,
            "user_id": "mock_user_123"
        }
    }

# Content history endpoint
@app.get("/api/v1/content/history")
async def get_content_history():
    """Get user's content generation history"""
    return {
        "content": [
            {
                "id": "content_1",
                "title": "Sample Blog Post",
                "content_type": "blog_post",
                "created_at": "2024-01-15T10:30:00Z",
                "word_count": 850
            },
            {
                "id": "content_2", 
                "title": "Product Launch Article",
                "content_type": "article",
                "created_at": "2024-01-14T15:45:00Z",
                "word_count": 1200
            }
        ],
        "total": 2
    }

# User profile endpoint
@app.get("/api/v1/user/profile")
async def get_user_profile():
    """Get user profile information"""
    return {
        "user_id": "mock_user_123",
        "email": "user@example.com",
        "full_name": "John Doe",
        "subscription_plan": "free",
        "content_generated": 15,
        "monthly_limit": 50,
        "created_at": "2024-01-01T00:00:00Z"
    }

def generate_mock_content(request: ContentRequest) -> str:
    """Generate mock content based on request parameters"""
    
    tone_styles = {
        "professional": "This comprehensive analysis explores",
        "casual": "Let's dive into",
        "academic": "This research examines",
        "creative": "Imagine a world where",
        "technical": "The implementation of"
    }
    
    content_templates = {
        "blog_post": """
{intro} {title} and its implications for modern businesses.

## Introduction

{title} has become increasingly important in today's digital landscape. Understanding its core principles and applications can provide significant advantages for organizations looking to stay competitive.

## Key Benefits

The primary advantages of {title} include:

1. **Enhanced Efficiency**: Streamlined processes that reduce operational overhead
2. **Improved User Experience**: Better engagement and satisfaction metrics
3. **Scalable Solutions**: Adaptable frameworks that grow with your business
4. **Cost Optimization**: Reduced expenses through intelligent automation

## Implementation Strategy

To successfully implement {title}, consider the following approach:

### Phase 1: Assessment and Planning
Begin with a thorough evaluation of your current systems and identify areas for improvement.

### Phase 2: Development and Testing
Create a robust development pipeline with comprehensive testing protocols.

### Phase 3: Deployment and Monitoring
Roll out the solution with continuous monitoring and optimization.

## Best Practices

Key recommendations for success:

- Maintain clear documentation throughout the process
- Engage stakeholders early and often
- Implement feedback loops for continuous improvement
- Monitor performance metrics regularly

## Conclusion

{title} represents a significant opportunity for organizations to enhance their operations and deliver superior value to their customers. By following the strategies outlined above, businesses can successfully navigate the implementation process and achieve their desired outcomes.

Keywords: {keywords}
        """,
        
        "article": """
{intro} {title} in detail, providing comprehensive insights and analysis.

## Executive Summary

This article provides an in-depth examination of {title}, covering its historical context, current applications, and future implications. Through detailed analysis and case studies, we explore how this concept is reshaping industries and creating new opportunities for innovation.

## Historical Context

The evolution of {title} can be traced back to early developments in the field, where initial concepts laid the groundwork for today's advanced implementations.

## Current Applications

### Industry Use Cases

1. **Technology Sector**: Leading companies are leveraging {title} to drive innovation
2. **Healthcare**: Medical institutions are implementing solutions to improve patient outcomes
3. **Finance**: Financial services are adopting new approaches to enhance security and efficiency
4. **Education**: Educational institutions are transforming learning experiences

### Case Studies

**Case Study 1: Enterprise Implementation**
A Fortune 500 company successfully implemented {title}, resulting in 40% efficiency improvements and $2M annual savings.

**Case Study 2: Startup Innovation**
An emerging startup used {title} to disrupt traditional markets and achieve rapid growth.

## Technical Analysis

The technical aspects of {title} involve several key components:

- **Architecture Design**: Scalable and maintainable system structures
- **Data Management**: Efficient storage and retrieval mechanisms
- **Security Protocols**: Robust protection against threats and vulnerabilities
- **Performance Optimization**: Enhanced speed and reliability

## Future Trends

Looking ahead, {title} is expected to evolve in several key areas:

1. **Artificial Intelligence Integration**: Enhanced automation and decision-making capabilities
2. **Cloud-Native Solutions**: Improved scalability and accessibility
3. **Sustainability Focus**: Environmentally conscious implementations
4. **User-Centric Design**: Enhanced user experiences and accessibility

## Challenges and Solutions

### Common Challenges

- Implementation complexity
- Resource constraints
- Change management
- Technical debt

### Recommended Solutions

- Phased implementation approach
- Stakeholder engagement
- Continuous training and development
- Regular system updates and maintenance

## Conclusion

{title} continues to be a driving force for innovation and transformation across industries. Organizations that embrace these concepts and implement them effectively will be well-positioned for future success.

Keywords: {keywords}
        """,
        
        "social_media": """
🚀 {title} is changing the game! 

Here's what you need to know:

✅ Key benefits that matter
✅ Simple implementation tips  
✅ Real results you can achieve

Ready to get started? Here's your action plan:

1️⃣ Assess your current situation
2️⃣ Set clear, measurable goals
3️⃣ Take the first step today

💡 Pro tip: Start small and scale up as you see results!

What's your experience with {title}? Share in the comments! 👇

#{keywords}
        """,
        
        "newsletter": """
# Weekly Insights: {title}

Hello there! 👋

Welcome to this week's newsletter where we dive deep into {title} and explore how it can transform your approach to business and innovation.

## This Week's Highlights

🔥 **Trending Topic**: {title} adoption rates have increased by 300% this quarter

📊 **Industry Insight**: Leading companies are seeing significant ROI from implementation

💡 **Expert Tip**: Start with small pilot projects to minimize risk

## Featured Article

{intro} {title} and its practical applications in today's market. This comprehensive guide covers everything from basic concepts to advanced implementation strategies.

### Key Takeaways:
- Understanding the fundamentals is crucial for success
- Implementation requires careful planning and execution
- Measuring results helps optimize performance

## Resources for You

📚 **Recommended Reading**: "The Complete Guide to {title}"
🎥 **Video Tutorial**: "Getting Started in 10 Minutes"
🛠️ **Free Tool**: Implementation checklist and templates

## Community Spotlight

This week, we're featuring success stories from our community members who have successfully implemented {title} in their organizations.

## What's Next?

Next week, we'll explore advanced strategies and share exclusive insights from industry leaders.

Stay tuned!

Best regards,
The AI Blog Assistant Team

---
Keywords: {keywords}
        """,
        
        "product_description": """
# {title} - Transform Your Business Today

## Why Choose {title}?

{intro} {title} as the ultimate solution for modern businesses looking to stay ahead of the competition.

### Key Features:
🎯 **Advanced Functionality**: Cutting-edge features designed for maximum impact
⚡ **Lightning Fast**: Optimized performance that saves you time
🔒 **Enterprise Security**: Bank-level security to protect your data
📱 **Mobile Ready**: Access anywhere, anytime, on any device

### What You Get:
- Complete implementation package
- 24/7 customer support
- Regular updates and improvements
- Comprehensive training materials

### Perfect For:
- Growing businesses
- Enterprise organizations
- Startups and entrepreneurs
- Teams of any size

## Customer Success Stories

"Since implementing {title}, our productivity has increased by 50% and our costs have decreased by 30%." - Sarah Johnson, CEO

"The best investment we've made for our business. The ROI was evident within the first month." - Michael Chen, Operations Director

## Get Started Today

Ready to transform your business with {title}?

🎁 **Special Offer**: Get 30% off your first year
📞 **Free Consultation**: Speak with our experts
✅ **Money-Back Guarantee**: 60-day risk-free trial

[Get Started Now] [Schedule Demo] [Contact Sales]

Keywords: {keywords}
        """
    }
    
    # Get the appropriate template
    template = content_templates.get(request.content_type, content_templates["blog_post"])
    intro = tone_styles.get(request.tone, tone_styles["professional"])
    keywords_str = ", ".join(request.keywords) if request.keywords else "innovation, technology, business"
    
    # Generate content
    content = template.format(
        intro=intro,
        title=request.title,
        keywords=keywords_str
    ).strip()
    
    # Adjust length if needed
    words = content.split()
    if len(words) > request.length:
        content = " ".join(words[:request.length]) + "..."
    
    return content

if __name__ == "__main__":
    print("🚀 Starting AI Blog Assistant Simple Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔧 Health check at: http://localhost:8000/health")
    print("")
    print("Available endpoints:")
    print("  • POST /api/v1/content/generate - Generate blog content")
    print("  • GET  /api/v1/content/templates - Get content templates")
    print("  • GET  /api/v1/content/history - Get content history")
    print("  • POST /api/v1/auth/register - Register user")
    print("  • POST /api/v1/auth/login - Login user")
    print("  • GET  /api/v1/user/profile - Get user profile")
    print("")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )