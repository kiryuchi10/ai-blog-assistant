"""
Content Management API Endpoints - CRUD operations for blog posts
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Optional, Dict, Any, List
import logging
import math

from app.services.content_generation_service import ContentGenerationService
from app.services.content_service import ContentService
from app.services.seo_service import SEOAnalysisService
from app.services.autosave_service import AutoSaveService
from app.core.auth_middleware import get_current_user
from app.core.database import get_db
from app.schemas.content import (
    BlogPostCreate, BlogPostUpdate, BlogPostResponse, BlogPostListResponse,
    BlogPostSearchRequest, PostVersionResponse, PostVersionListResponse,
    PostVersionCreate, SEOAnalysisRequest, SEOAnalysisResponse
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
autosave_service = AutoSaveService()

# Legacy content generation endpoints (keeping for backward compatibility)
from pydantic import BaseModel

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

# CRUD Endpoints for Blog Posts

@router.post("/posts", response_model=BlogPostResponse)
async def create_blog_post(
    post_data: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new blog post"""
    try:
        content_service = ContentService(db)
        blog_post = content_service.create_blog_post(post_data, current_user["user_id"])
        
        return BlogPostResponse.from_orm(blog_post)
        
    except Exception as e:
        logger.error(f"Error creating blog post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create blog post")

@router.get("/posts/{post_id}", response_model=BlogPostResponse)
async def get_blog_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific blog post"""
    content_service = ContentService(db)
    blog_post = content_service.get_blog_post(post_id, current_user["user_id"])
    
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return BlogPostResponse.from_orm(blog_post)

@router.get("/posts", response_model=BlogPostListResponse)
async def get_blog_posts(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get blog posts with search and filtering"""
    try:
        search_params = BlogPostSearchRequest(
            query=query,
            status=status,
            post_type=post_type,
            category=category,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        content_service = ContentService(db)
        posts, total = content_service.get_blog_posts(current_user["user_id"], search_params)
        
        total_pages = math.ceil(total / per_page)
        
        return BlogPostListResponse(
            posts=[BlogPostResponse.from_orm(post) for post in posts],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error fetching blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch blog posts")

@router.put("/posts/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: str,
    update_data: BlogPostUpdate,
    changes_summary: Optional[str] = Query(None, description="Summary of changes"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a blog post"""
    try:
        content_service = ContentService(db)
        blog_post = content_service.update_blog_post(
            post_id, 
            current_user["user_id"], 
            update_data,
            changes_summary
        )
        
        if not blog_post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return BlogPostResponse.from_orm(blog_post)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating blog post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update blog post")

@router.delete("/posts/{post_id}")
async def delete_blog_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a blog post"""
    try:
        content_service = ContentService(db)
        success = content_service.delete_blog_post(post_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return {"message": "Blog post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting blog post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete blog post")

# Version Control Endpoints

@router.get("/posts/{post_id}/versions", response_model=PostVersionListResponse)
async def get_post_versions(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all versions of a blog post"""
    try:
        content_service = ContentService(db)
        versions = content_service.get_post_versions(post_id, current_user["user_id"])
        
        return PostVersionListResponse(
            versions=[PostVersionResponse.from_orm(version) for version in versions],
            total=len(versions)
        )
        
    except Exception as e:
        logger.error(f"Error fetching post versions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch post versions")

@router.get("/posts/{post_id}/versions/{version_number}", response_model=PostVersionResponse)
async def get_post_version(
    post_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific version of a blog post"""
    content_service = ContentService(db)
    version = content_service.get_post_version(post_id, version_number, current_user["user_id"])
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return PostVersionResponse.from_orm(version)

@router.post("/posts/{post_id}/rollback/{version_number}", response_model=BlogPostResponse)
async def rollback_to_version(
    post_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Rollback a blog post to a specific version"""
    try:
        content_service = ContentService(db)
        blog_post = content_service.rollback_to_version(
            post_id, 
            version_number, 
            current_user["user_id"]
        )
        
        if not blog_post:
            raise HTTPException(status_code=404, detail="Post or version not found")
        
        return BlogPostResponse.from_orm(blog_post)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to rollback post")

# SEO Analysis Endpoints

@router.post("/posts/{post_id}/seo-analysis", response_model=Dict[str, Any])
async def analyze_post_seo(
    post_id: str,
    analysis_request: SEOAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze SEO for a blog post"""
    try:
        content_service = ContentService(db)
        blog_post = content_service.get_blog_post(post_id, current_user["user_id"])
        
        if not blog_post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        seo_service = SEOAnalysisService()
        analysis = seo_service.generate_seo_score(
            content=analysis_request.content,
            title=blog_post.title,
            meta_description=blog_post.meta_description,
            target_keywords=analysis_request.target_keywords
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing SEO: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze SEO")

@router.post("/seo/analyze", response_model=Dict[str, Any])
async def analyze_content_seo(
    analysis_request: SEOAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze SEO for any content"""
    try:
        seo_service = SEOAnalysisService()
        
        # Extract title from content if not provided separately
        lines = analysis_request.content.split('\n')
        title = lines[0] if lines else "Untitled"
        
        analysis = seo_service.generate_seo_score(
            content=analysis_request.content,
            title=title,
            meta_description=None,
            target_keywords=analysis_request.target_keywords
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing content SEO: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze content SEO")

# Auto-save Endpoints

@router.post("/posts/{post_id}/autosave")
async def schedule_autosave(
    post_id: str,
    content: str,
    title: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Schedule auto-save for a blog post"""
    try:
        result = await autosave_service.schedule_autosave(
            post_id, 
            current_user["user_id"], 
            content, 
            title, 
            background_tasks
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error scheduling autosave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule autosave")

@router.get("/posts/{post_id}/autosave-status")
async def get_autosave_status(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get auto-save status for a blog post"""
    try:
        status = autosave_service.get_autosave_status(post_id, current_user["user_id"])
        return status
        
    except Exception as e:
        logger.error(f"Error getting autosave status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get autosave status")

@router.post("/posts/{post_id}/force-save")
async def force_save_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Force immediate save of a blog post"""
    try:
        result = autosave_service.force_save(post_id, current_user["user_id"])
        return result
        
    except Exception as e:
        logger.error(f"Error forcing save: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to force save")

# Search and Categorization Endpoints

@router.get("/search")
async def search_content(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search blog posts by content"""
    try:
        content_service = ContentService(db)
        posts = content_service.search_content(current_user["user_id"], q, limit)
        
        return {
            "query": q,
            "results": [BlogPostResponse.from_orm(post) for post in posts],
            "total": len(posts)
        }
        
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search content")

@router.get("/categories/{category}/posts")
async def get_posts_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get posts by category"""
    try:
        content_service = ContentService(db)
        posts = content_service.get_posts_by_category(current_user["user_id"], category)
        
        return {
            "category": category,
            "posts": [BlogPostResponse.from_orm(post) for post in posts],
            "total": len(posts)
        }
        
    except Exception as e:
        logger.error(f"Error fetching posts by category: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch posts by category")

# Legacy endpoints (keeping for backward compatibility)

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered content based on user input"""
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
    """Generate SEO metadata for content"""
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
    """Get suggestions for improving content"""
    try:
        service = ContentGenerationService()
        suggestions = service.suggest_improvements(request.content)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Content suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")

@router.get("/templates")
async def get_content_templates():
    """Get available content templates"""
    from app.services.content_generation_service import CONTENT_TEMPLATES
    
    return {
        'success': True,
        'templates': CONTENT_TEMPLATES
    }