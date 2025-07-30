"""
Content generation schemas for API requests and responses
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ContentTypeEnum(str, Enum):
    """Content type enumeration for API"""
    ARTICLE = "article"
    HOW_TO = "how_to"
    LISTICLE = "listicle"
    OPINION = "opinion"
    NEWS = "news"
    REVIEW = "review"
    TUTORIAL = "tutorial"


class ContentToneEnum(str, Enum):
    """Content tone enumeration for API"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"
    FRIENDLY = "friendly"


class ContentGenerationRequest(BaseModel):
    """Request schema for content generation"""
    topic: str = Field(..., min_length=5, max_length=200, description="Blog post topic")
    content_type: ContentTypeEnum = Field(default=ContentTypeEnum.ARTICLE, description="Type of content to generate")
    tone: ContentToneEnum = Field(default=ContentToneEnum.PROFESSIONAL, description="Tone of the content")
    keywords: Optional[List[str]] = Field(default=None, description="Target keywords for SEO")
    target_length: int = Field(default=1000, ge=300, le=5000, description="Target word count")
    include_seo: bool = Field(default=True, description="Include SEO optimization")
    industry: Optional[str] = Field(default=None, max_length=100, description="Industry context")
    target_audience: Optional[str] = Field(default=None, max_length=200, description="Target audience description")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError("Maximum 10 keywords allowed")
            for keyword in v:
                if len(keyword.strip()) < 2:
                    raise ValueError("Keywords must be at least 2 characters long")
        return v
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()


class TokenUsageResponse(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float


class ContentGenerationResponse(BaseModel):
    """Response schema for generated content"""
    title: str
    content: str
    meta_description: str
    keywords: List[str]
    seo_suggestions: List[str]
    word_count: int
    reading_time: int  # in minutes
    token_usage: TokenUsageResponse


class ContentRegenerationRequest(BaseModel):
    """Request schema for content section regeneration"""
    original_content: str = Field(..., min_length=100, description="Original blog post content")
    section_to_regenerate: str = Field(..., min_length=10, description="Section to regenerate")
    instructions: str = Field(..., min_length=10, max_length=500, description="Instructions for regeneration")


class ContentRegenerationResponse(BaseModel):
    """Response schema for regenerated content section"""
    regenerated_section: str
    token_usage: TokenUsageResponse


class SEOAnalysisRequest(BaseModel):
    """Request schema for SEO analysis"""
    content: str = Field(..., min_length=100, description="Content to analyze")
    target_keywords: List[str] = Field(..., min_items=1, max_items=10, description="Target keywords")
    
    @validator('target_keywords')
    def validate_keywords(cls, v):
        for keyword in v:
            if len(keyword.strip()) < 2:
                raise ValueError("Keywords must be at least 2 characters long")
        return [keyword.strip() for keyword in v]


class SEOAnalysisResponse(BaseModel):
    """Response schema for SEO analysis"""
    seo_score: int = Field(..., ge=0, le=100, description="SEO score out of 100")
    suggestions: List[str]
    keyword_density: dict = Field(..., description="Keyword density analysis")
    readability_score: float
    token_usage: TokenUsageResponse


class ContentValidationError(BaseModel):
    """Content validation error details"""
    field: str
    message: str
    code: str


class ContentValidationResponse(BaseModel):
    """Content validation response"""
    is_valid: bool
    errors: List[ContentValidationError] = []
    warnings: List[str] = []
    sanitized_content: Optional[str] = None


class StreamingContentChunk(BaseModel):
    """Streaming content chunk"""
    chunk: str
    is_complete: bool = False
    error: Optional[str] = None


# CRUD Schemas for Blog Posts
class BlogPostStatusEnum(str, Enum):
    """Blog post status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class BlogPostCreate(BaseModel):
    """Schema for creating a new blog post"""
    title: str = Field(..., min_length=5, max_length=500, description="Blog post title")
    content: str = Field(..., min_length=100, description="Blog post content")
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    keywords: Optional[List[str]] = Field(default=None, description="SEO keywords")
    status: BlogPostStatusEnum = Field(default=BlogPostStatusEnum.DRAFT, description="Post status")
    post_type: ContentTypeEnum = Field(default=ContentTypeEnum.ARTICLE, description="Type of content")
    tone: ContentToneEnum = Field(default=ContentToneEnum.PROFESSIONAL, description="Content tone")
    slug: Optional[str] = Field(None, max_length=500, description="URL slug")
    featured_image_url: Optional[str] = Field(None, max_length=500, description="Featured image URL")
    template_category: Optional[str] = Field(None, max_length=100, description="Template category")
    tags: Optional[List[str]] = Field(default=None, description="Content tags")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None:
            if len(v) > 20:
                raise ValueError("Maximum 20 keywords allowed")
            return [keyword.strip() for keyword in v if keyword.strip()]
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 15:
                raise ValueError("Maximum 15 tags allowed")
            return [tag.strip() for tag in v if tag.strip()]
        return v


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post"""
    title: Optional[str] = Field(None, min_length=5, max_length=500, description="Blog post title")
    content: Optional[str] = Field(None, min_length=100, description="Blog post content")
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    keywords: Optional[List[str]] = Field(None, description="SEO keywords")
    status: Optional[BlogPostStatusEnum] = Field(None, description="Post status")
    post_type: Optional[ContentTypeEnum] = Field(None, description="Type of content")
    tone: Optional[ContentToneEnum] = Field(None, description="Content tone")
    slug: Optional[str] = Field(None, max_length=500, description="URL slug")
    featured_image_url: Optional[str] = Field(None, max_length=500, description="Featured image URL")
    template_category: Optional[str] = Field(None, max_length=100, description="Template category")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None:
            if len(v) > 20:
                raise ValueError("Maximum 20 keywords allowed")
            return [keyword.strip() for keyword in v if keyword.strip()]
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 15:
                raise ValueError("Maximum 15 tags allowed")
            return [tag.strip() for tag in v if tag.strip()]
        return v


class BlogPostResponse(BaseModel):
    """Schema for blog post response"""
    id: str
    title: str
    content: str
    meta_description: Optional[str]
    keywords: Optional[List[str]]
    status: str
    post_type: str
    tone: str
    seo_score: int
    word_count: int
    reading_time: int
    slug: Optional[str]
    featured_image_url: Optional[str]
    template_category: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class BlogPostListResponse(BaseModel):
    """Schema for blog post list response"""
    posts: List[BlogPostResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class BlogPostSearchRequest(BaseModel):
    """Schema for blog post search request"""
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[BlogPostStatusEnum] = Field(None, description="Filter by status")
    post_type: Optional[ContentTypeEnum] = Field(None, description="Filter by post type")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    category: Optional[str] = Field(None, description="Filter by category")
    date_from: Optional[str] = Field(None, description="Filter from date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter to date (YYYY-MM-DD)")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")


# Version Control Schemas
class PostVersionResponse(BaseModel):
    """Schema for post version response"""
    id: str
    version_number: int
    title: Optional[str]
    content: Optional[str]
    changes_summary: Optional[str]
    word_count: int
    created_at: str
    
    class Config:
        from_attributes = True


class PostVersionCreate(BaseModel):
    """Schema for creating a post version"""
    changes_summary: str = Field(..., min_length=5, max_length=500, description="Summary of changes")


class PostVersionListResponse(BaseModel):
    """Schema for post version list response"""
    versions: List[PostVersionResponse]
    total: int