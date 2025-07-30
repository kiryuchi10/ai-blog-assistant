"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import template, content

# Create main API router
api_router = APIRouter()

# Include template endpoints
api_router.include_router(template.router, prefix="/templates", tags=["templates"])

# Include content endpoints
api_router.include_router(content.router, prefix="/content", tags=["content"])

# Basic health check endpoint
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-blog-assistant-api",
        "version": "1.0.0"
    }