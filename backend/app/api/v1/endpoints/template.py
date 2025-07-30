"""
Content template management API endpoints
"""
import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.core.database import get_db
from app.core.auth_middleware import get_current_user
from app.models.user import User
from app.models.content import ContentTemplate
from app.services.template_service import TemplateService
from app.schemas.template import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateUsageRequest,
    TemplateUsageResponse,
    TemplateSearchRequest,
    TemplateAnalyticsResponse,
    TemplateStatsResponse,
    TemplateRatingRequest,
    TemplateRatingResponse,
    TemplateExportRequest,
    TemplateImportRequest,
    TemplateImportResponse
)
from app.services.rate_limiter import rate_limiter


logger = logging.getLogger(__name__)
router = APIRouter()





def _build_search_query(db: Session, search_request: TemplateSearchRequest, user: User):
    """Build search query based on search parameters"""
    query = db.query(ContentTemplate)
    
    # Filter by user's templates or public templates
    query = query.filter(
        or_(
            ContentTemplate.created_by == user.id,
            ContentTemplate.is_public == True
        )
    )
    
    # Apply filters
    if search_request.query:
        search_term = f"%{search_request.query}%"
        query = query.filter(
            or_(
                ContentTemplate.name.ilike(search_term),
                ContentTemplate.description.ilike(search_term),
                ContentTemplate.template_content.ilike(search_term)
            )
        )
    
    if search_request.category:
        query = query.filter(ContentTemplate.category == search_request.category)
    
    if search_request.template_type:
        query = query.filter(ContentTemplate.template_type == search_request.template_type)
    
    if search_request.industry:
        query = query.filter(ContentTemplate.industry.ilike(f"%{search_request.industry}%"))
    
    if search_request.is_public is not None:
        query = query.filter(ContentTemplate.is_public == search_request.is_public)
    
    if search_request.tags:
        # Filter by tags (assuming tags are stored as JSON array)
        for tag in search_request.tags:
            query = query.filter(ContentTemplate.tags.contains([tag]))
    
    # Apply sorting
    sort_field = getattr(ContentTemplate, search_request.sort_by)
    if search_request.sort_order == 'desc':
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    return query


@router.post("/", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new content template"""
    try:
        # Rate limiting
        await rate_limiter.check_rate_limit(f"template_create:{current_user.id}")
        
        # Check if template name already exists for this user
        existing_template = db.query(ContentTemplate).filter(
            and_(
                ContentTemplate.name == request.name,
                ContentTemplate.created_by == current_user.id
            )
        ).first()
        
        if existing_template:
            raise HTTPException(
                status_code=400,
                detail="Template with this name already exists"
            )
        
        # Initialize template service
        template_service = TemplateService(db)
        
        # Extract placeholders from template content
        placeholders = template_service.extract_placeholders(request.template_content)
        
        # Create new template
        template = ContentTemplate(
            name=request.name,
            description=request.description,
            template_content=request.template_content,
            category=request.category,
            template_type=request.template_type,
            industry=request.industry,
            is_public=request.is_public,
            tags=request.tags or [],
            placeholders=placeholders,
            created_by=current_user.id,
            usage_count=0
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Template created: {template.id} by user {current_user.id}")
        
        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description,
            template_content=template.template_content,
            category=template.category,
            template_type=template.template_type,
            industry=template.industry,
            is_public=template.is_public,
            tags=template.tags,
            usage_count=template.usage_count,
            created_by=str(template.created_by),
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except Exception as e:
        logger.error(f"Template creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template creation failed")


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    template_type: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List templates with pagination and filtering"""
    try:
        # Build base query
        query = db.query(ContentTemplate).filter(
            or_(
                ContentTemplate.created_by == current_user.id,
                ContentTemplate.is_public == True
            )
        )
        
        # Apply filters
        if category:
            query = query.filter(ContentTemplate.category == category)
        
        if template_type:
            query = query.filter(ContentTemplate.template_type == template_type)
        
        if is_public is not None:
            query = query.filter(ContentTemplate.is_public == is_public)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        templates = query.offset(offset).limit(per_page).all()
        
        # Convert to response format
        template_responses = [
            TemplateResponse(
                id=str(template.id),
                name=template.name,
                description=template.description,
                template_content=template.template_content,
                category=template.category,
                template_type=template.template_type,
                industry=template.industry,
                is_public=template.is_public,
                tags=template.tags,
                usage_count=template.usage_count,
                created_by=str(template.created_by),
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in templates
        ]
        
        return TemplateListResponse(
            templates=template_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=offset + per_page < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"Template listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template listing failed")


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template by ID"""
    try:
        template = db.query(ContentTemplate).filter(
            and_(
                ContentTemplate.id == template_id,
                or_(
                    ContentTemplate.created_by == current_user.id,
                    ContentTemplate.is_public == True
                )
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description,
            template_content=template.template_content,
            category=template.category,
            template_type=template.template_type,
            industry=template.industry,
            is_public=template.is_public,
            tags=template.tags,
            usage_count=template.usage_count,
            created_by=str(template.created_by),
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template retrieval failed")


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a template"""
    try:
        # Rate limiting
        await rate_limiter.check_rate_limit(f"template_update:{current_user.id}")
        
        template = db.query(ContentTemplate).filter(
            and_(
                ContentTemplate.id == template_id,
                ContentTemplate.created_by == current_user.id
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found or not owned by user")
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        # Update placeholders if template content changed
        if 'template_content' in update_data:
            template_service = TemplateService(db)
            template.placeholders = template_service.extract_placeholders(template.template_content)
        
        template.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(template)
        
        logger.info(f"Template updated: {template.id} by user {current_user.id}")
        
        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description,
            template_content=template.template_content,
            category=template.category,
            template_type=template.template_type,
            industry=template.industry,
            is_public=template.is_public,
            tags=template.tags,
            usage_count=template.usage_count,
            created_by=str(template.created_by),
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template update failed")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a template"""
    try:
        template = db.query(ContentTemplate).filter(
            and_(
                ContentTemplate.id == template_id,
                ContentTemplate.created_by == current_user.id
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found or not owned by user")
        
        db.delete(template)
        db.commit()
        
        logger.info(f"Template deleted: {template_id} by user {current_user.id}")
        
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template deletion failed")


@router.post("/search", response_model=TemplateListResponse)
async def search_templates(
    request: TemplateSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search templates with advanced filtering"""
    try:
        # Build search query
        query = _build_search_query(db, request, current_user)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (request.page - 1) * request.per_page
        templates = query.offset(offset).limit(request.per_page).all()
        
        # Convert to response format
        template_responses = [
            TemplateResponse(
                id=str(template.id),
                name=template.name,
                description=template.description,
                template_content=template.template_content,
                category=template.category,
                template_type=template.template_type,
                industry=template.industry,
                is_public=template.is_public,
                tags=template.tags,
                usage_count=template.usage_count,
                created_by=str(template.created_by),
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in templates
        ]
        
        return TemplateListResponse(
            templates=template_responses,
            total=total,
            page=request.page,
            per_page=request.per_page,
            has_next=offset + request.per_page < total,
            has_prev=request.page > 1
        )
        
    except Exception as e:
        logger.error(f"Template search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template search failed")


@router.post("/{template_id}/use", response_model=TemplateUsageResponse)
async def use_template(
    template_id: str,
    request: TemplateUsageRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use a template to generate content"""
    try:
        # Rate limiting
        await rate_limiter.check_rate_limit(f"template_use:{current_user.id}")
        
        template = db.query(ContentTemplate).filter(
            and_(
                ContentTemplate.id == template_id,
                or_(
                    ContentTemplate.created_by == current_user.id,
                    ContentTemplate.is_public == True
                )
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Initialize template service
        template_service = TemplateService(db)
        
        # Replace placeholders
        generated_content, placeholders_found, placeholders_replaced = template_service.replace_placeholders(
            template.template_content,
            request.variables
        )
        
        # Track usage in background
        background_tasks.add_task(
            template_service.track_template_usage,
            template.id,
            current_user.id,
            request.variables
        )
        
        logger.info(f"Template used: {template_id} by user {current_user.id}")
        
        return TemplateUsageResponse(
            generated_content=generated_content,
            template_name=template.name,
            variables_used=request.variables,
            placeholders_found=placeholders_found,
            placeholders_replaced=placeholders_replaced
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template usage failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template usage failed")


@router.get("/{template_id}/analytics", response_model=TemplateAnalyticsResponse)
async def get_template_analytics(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a template"""
    try:
        template_service = TemplateService(db)
        analytics_data = template_service.get_template_analytics(template_id, current_user.id)
        
        if not analytics_data:
            raise HTTPException(status_code=404, detail="Template not found or not owned by user")
        
        return TemplateAnalyticsResponse(**analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template analytics failed")


@router.post("/seed-defaults")
async def seed_default_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seed default templates (admin only or for development)"""
    try:
        template_service = TemplateService(db)
        created_count = template_service.seed_default_templates(current_user.id)
        
        return {"message": f"Created {created_count} default templates"}
        
    except Exception as e:
        logger.error(f"Default template seeding failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Default template seeding failed")


@router.get("/stats", response_model=TemplateStatsResponse)
async def get_template_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall template statistics"""
    try:
        template_service = TemplateService(db)
        stats_data = template_service.get_template_stats()
        
        return TemplateStatsResponse(**stats_data)
        
    except Exception as e:
        logger.error(f"Template stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template stats failed")


@router.post("/{template_id}/rate", response_model=TemplateRatingResponse)
async def rate_template(
    template_id: str,
    request: TemplateRatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a template"""
    try:
        # Rate limiting
        await rate_limiter.check_rate_limit(f"template_rate:{current_user.id}")
        
        # Check if template exists and is accessible
        template = db.query(ContentTemplate).filter(
            and_(
                ContentTemplate.id == template_id,
                or_(
                    ContentTemplate.created_by == current_user.id,
                    ContentTemplate.is_public == True
                )
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_service = TemplateService(db)
        success = template_service.rate_template(
            template_id, 
            current_user.id, 
            request.rating, 
            request.comment
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to rate template")
        
        # Get updated analytics to return current rating info
        analytics_data = template_service.get_template_analytics(template_id, template.created_by)
        
        return TemplateRatingResponse(
            template_id=template_id,
            user_rating=request.rating,
            comment=request.comment,
            average_rating=analytics_data.get("average_rating", 0.0) if analytics_data else 0.0,
            total_ratings=analytics_data.get("total_ratings", 0) if analytics_data else 0,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template rating failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template rating failed")


@router.get("/popular", response_model=TemplateListResponse)
async def get_popular_templates(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get popular templates based on usage count"""
    try:
        template_service = TemplateService(db)
        popular_templates = template_service.get_popular_templates(limit=limit, category=category)
        
        # Convert to response format
        template_responses = [
            TemplateResponse(
                id=str(template.id),
                name=template.name,
                description=template.description,
                template_content=template.template_content,
                category=template.category,
                template_type=template.template_type,
                industry=template.industry,
                is_public=template.is_public,
                tags=template.tags or [],
                usage_count=template.usage_count,
                created_by=str(template.created_by),
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in popular_templates
        ]
        
        return TemplateListResponse(
            templates=template_responses,
            total=len(template_responses),
            page=1,
            per_page=limit,
            has_next=False,
            has_prev=False
        )
        
    except Exception as e:
        logger.error(f"Popular templates failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Popular templates failed")