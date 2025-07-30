"""
Content management service for CRUD operations on blog posts
"""
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException

from app.models.content import BlogPost, PostVersion, ContentTemplate
from app.schemas.content import (
    BlogPostCreate, BlogPostUpdate, BlogPostSearchRequest,
    PostVersionCreate, BlogPostStatusEnum, ContentTypeEnum
)


class ContentService:
    """Service for managing blog post content and versions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_blog_post(self, post_data: BlogPostCreate, user_id: str) -> BlogPost:
        """Create a new blog post"""
        # Generate slug if not provided
        slug = post_data.slug
        if not slug:
            slug = self._generate_slug(post_data.title)
        
        # Ensure slug is unique
        slug = self._ensure_unique_slug(slug, user_id)
        
        # Create blog post
        blog_post = BlogPost(
            user_id=user_id,
            title=post_data.title,
            content=post_data.content,
            meta_description=post_data.meta_description,
            keywords=json.dumps(post_data.keywords) if post_data.keywords else None,
            status=post_data.status.value,
            post_type=post_data.post_type.value,
            tone=post_data.tone.value,
            slug=slug,
            featured_image_url=post_data.featured_image_url,
            template_category=post_data.template_category
        )
        
        # Calculate word count and reading time
        blog_post.update_word_count()
        blog_post.calculate_reading_time()
        
        # Calculate initial SEO score
        blog_post.seo_score = self._calculate_seo_score(blog_post)
        
        self.db.add(blog_post)
        self.db.commit()
        self.db.refresh(blog_post)
        
        # Create initial version
        self._create_version(blog_post, "Initial version")
        
        return blog_post
    
    def get_blog_post(self, post_id: str, user_id: str) -> Optional[BlogPost]:
        """Get a blog post by ID"""
        return self.db.query(BlogPost).filter(
            and_(BlogPost.id == post_id, BlogPost.user_id == user_id)
        ).first()
    
    def get_blog_posts(self, user_id: str, search_params: BlogPostSearchRequest) -> Tuple[List[BlogPost], int]:
        """Get blog posts with search and filtering"""
        query = self.db.query(BlogPost).filter(BlogPost.user_id == user_id)
        
        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.meta_description.ilike(search_term)
                )
            )
        
        if search_params.status:
            query = query.filter(BlogPost.status == search_params.status.value)
        
        if search_params.post_type:
            query = query.filter(BlogPost.post_type == search_params.post_type.value)
        
        if search_params.category:
            query = query.filter(BlogPost.template_category == search_params.category)
        
        if search_params.date_from:
            try:
                date_from = datetime.strptime(search_params.date_from, "%Y-%m-%d")
                query = query.filter(BlogPost.created_at >= date_from)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
        
        if search_params.date_to:
            try:
                date_to = datetime.strptime(search_params.date_to, "%Y-%m-%d")
                query = query.filter(BlogPost.created_at <= date_to)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
        
        # Apply sorting
        sort_column = getattr(BlogPost, search_params.sort_by, BlogPost.created_at)
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.per_page
        posts = query.offset(offset).limit(search_params.per_page).all()
        
        return posts, total
    
    def update_blog_post(self, post_id: str, user_id: str, update_data: BlogPostUpdate, 
                        changes_summary: Optional[str] = None) -> Optional[BlogPost]:
        """Update a blog post"""
        blog_post = self.get_blog_post(post_id, user_id)
        if not blog_post:
            return None
        
        # Store original content for version tracking
        original_content = blog_post.content
        original_title = blog_post.title
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field == "keywords" and value is not None:
                setattr(blog_post, field, json.dumps(value))
            elif field in ["status", "post_type", "tone"] and value is not None:
                setattr(blog_post, field, value.value)
            elif value is not None:
                setattr(blog_post, field, value)
        
        # Update slug if title changed
        if update_data.title and update_data.title != original_title:
            new_slug = self._generate_slug(update_data.title)
            blog_post.slug = self._ensure_unique_slug(new_slug, user_id, exclude_post_id=post_id)
        
        # Recalculate metrics if content changed
        if update_data.content and update_data.content != original_content:
            blog_post.update_word_count()
            blog_post.calculate_reading_time()
            blog_post.seo_score = self._calculate_seo_score(blog_post)
        
        self.db.commit()
        self.db.refresh(blog_post)
        
        # Create version if content or title changed
        if (update_data.content and update_data.content != original_content) or \
           (update_data.title and update_data.title != original_title):
            summary = changes_summary or "Content updated"
            self._create_version(blog_post, summary)
        
        return blog_post
    
    def delete_blog_post(self, post_id: str, user_id: str) -> bool:
        """Delete a blog post"""
        blog_post = self.get_blog_post(post_id, user_id)
        if not blog_post:
            return False
        
        self.db.delete(blog_post)
        self.db.commit()
        return True
    
    def get_post_versions(self, post_id: str, user_id: str) -> List[PostVersion]:
        """Get all versions of a blog post"""
        # First verify the post belongs to the user
        blog_post = self.get_blog_post(post_id, user_id)
        if not blog_post:
            return []
        
        return self.db.query(PostVersion).filter(
            PostVersion.post_id == post_id
        ).order_by(desc(PostVersion.version_number)).all()
    
    def get_post_version(self, post_id: str, version_number: int, user_id: str) -> Optional[PostVersion]:
        """Get a specific version of a blog post"""
        # First verify the post belongs to the user
        blog_post = self.get_blog_post(post_id, user_id)
        if not blog_post:
            return None
        
        return self.db.query(PostVersion).filter(
            and_(
                PostVersion.post_id == post_id,
                PostVersion.version_number == version_number
            )
        ).first()
    
    def rollback_to_version(self, post_id: str, version_number: int, user_id: str) -> Optional[BlogPost]:
        """Rollback a blog post to a specific version"""
        blog_post = self.get_blog_post(post_id, user_id)
        if not blog_post:
            return None
        
        version = self.get_post_version(post_id, version_number, user_id)
        if not version:
            return None
        
        # Update blog post with version content
        if version.title:
            blog_post.title = version.title
        if version.content:
            blog_post.content = version.content
            blog_post.update_word_count()
            blog_post.calculate_reading_time()
            blog_post.seo_score = self._calculate_seo_score(blog_post)
        
        self.db.commit()
        self.db.refresh(blog_post)
        
        # Create new version for rollback
        self._create_version(blog_post, f"Rolled back to version {version_number}")
        
        return blog_post
    
    def search_content(self, user_id: str, query: str, limit: int = 10) -> List[BlogPost]:
        """Search blog posts by content"""
        search_term = f"%{query}%"
        return self.db.query(BlogPost).filter(
            and_(
                BlogPost.user_id == user_id,
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.meta_description.ilike(search_term)
                )
            )
        ).limit(limit).all()
    
    def get_posts_by_category(self, user_id: str, category: str) -> List[BlogPost]:
        """Get posts by template category"""
        return self.db.query(BlogPost).filter(
            and_(
                BlogPost.user_id == user_id,
                BlogPost.template_category == category
            )
        ).all()
    
    def get_posts_by_tags(self, user_id: str, tags: List[str]) -> List[BlogPost]:
        """Get posts by tags (simplified - would need proper tag system)"""
        # This is a simplified implementation
        # In a real system, you'd have a separate tags table with many-to-many relationship
        posts = []
        for tag in tags:
            tag_posts = self.db.query(BlogPost).filter(
                and_(
                    BlogPost.user_id == user_id,
                    BlogPost.keywords.ilike(f"%{tag}%")
                )
            ).all()
            posts.extend(tag_posts)
        
        # Remove duplicates
        unique_posts = list({post.id: post for post in posts}.values())
        return unique_posts
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug[:100]  # Limit length
    
    def _ensure_unique_slug(self, slug: str, user_id: str, exclude_post_id: Optional[str] = None) -> str:
        """Ensure slug is unique for the user"""
        original_slug = slug
        counter = 1
        
        while True:
            query = self.db.query(BlogPost).filter(
                and_(
                    BlogPost.user_id == user_id,
                    BlogPost.slug == slug
                )
            )
            
            if exclude_post_id:
                query = query.filter(BlogPost.id != exclude_post_id)
            
            if not query.first():
                return slug
            
            slug = f"{original_slug}-{counter}"
            counter += 1
    
    def _create_version(self, blog_post: BlogPost, changes_summary: str) -> PostVersion:
        """Create a new version of a blog post"""
        # Get next version number
        last_version = self.db.query(PostVersion).filter(
            PostVersion.post_id == blog_post.id
        ).order_by(desc(PostVersion.version_number)).first()
        
        version_number = (last_version.version_number + 1) if last_version else 1
        
        version = PostVersion(
            post_id=blog_post.id,
            version_number=version_number,
            title=blog_post.title,
            content=blog_post.content,
            changes_summary=changes_summary,
            word_count=blog_post.word_count
        )
        
        self.db.add(version)
        self.db.commit()
        return version
    
    def _calculate_seo_score(self, blog_post: BlogPost) -> int:
        """Calculate basic SEO score for a blog post"""
        score = 0
        
        # Title length (5-60 characters is good)
        if 5 <= len(blog_post.title) <= 60:
            score += 20
        elif len(blog_post.title) <= 70:
            score += 15
        
        # Meta description
        if blog_post.meta_description:
            if 120 <= len(blog_post.meta_description) <= 160:
                score += 20
            elif len(blog_post.meta_description) <= 180:
                score += 15
        
        # Content length (300+ words is good)
        if blog_post.word_count >= 300:
            score += 20
        elif blog_post.word_count >= 200:
            score += 15
        
        # Keywords presence
        if blog_post.keywords:
            try:
                keywords = json.loads(blog_post.keywords)
                if keywords and len(keywords) > 0:
                    score += 20
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Slug quality
        if blog_post.slug and len(blog_post.slug) > 0:
            score += 20
        
        return min(score, 100)  # Cap at 100