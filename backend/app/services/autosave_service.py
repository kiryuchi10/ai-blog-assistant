"""
Auto-save and version control service for content management
"""
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.models.content import BlogPost, PostVersion
from app.core.database import get_db
from app.services.content_service import ContentService


class AutoSaveService:
    """Service for handling auto-save and version control operations"""
    
    # Store auto-save data in memory (in production, use Redis)
    _autosave_cache: Dict[str, Dict[str, Any]] = {}
    _save_intervals: Dict[str, datetime] = {}
    
    def __init__(self):
        self.save_interval = 30  # seconds
        self.max_versions_per_post = 50
        self.conflict_resolution_timeout = 300  # 5 minutes
    
    async def schedule_autosave(self, post_id: str, user_id: str, content: str, 
                               title: str, background_tasks: BackgroundTasks):
        """Schedule an auto-save operation"""
        cache_key = f"{user_id}:{post_id}"
        current_time = datetime.utcnow()
        
        # Update cache with latest content
        self._autosave_cache[cache_key] = {
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
            "title": title,
            "last_modified": current_time,
            "save_pending": True
        }
        
        # Check if we should save immediately or schedule
        last_save = self._save_intervals.get(cache_key)
        if not last_save or (current_time - last_save).seconds >= self.save_interval:
            # Schedule immediate save
            background_tasks.add_task(self._perform_autosave, cache_key)
            self._save_intervals[cache_key] = current_time
        
        return {"status": "scheduled", "next_save_in": self.save_interval}
    
    async def _perform_autosave(self, cache_key: str):
        """Perform the actual auto-save operation"""
        if cache_key not in self._autosave_cache:
            return
        
        cache_data = self._autosave_cache[cache_key]
        
        # Get database session
        db = next(get_db())
        try:
            content_service = ContentService(db)
            
            # Get current post
            blog_post = content_service.get_blog_post(
                cache_data["post_id"], 
                cache_data["user_id"]
            )
            
            if not blog_post:
                return
            
            # Check if content has actually changed
            if (blog_post.content == cache_data["content"] and 
                blog_post.title == cache_data["title"]):
                # No changes, just mark as saved
                cache_data["save_pending"] = False
                return
            
            # Check for conflicts (if post was modified by another session)
            if self._has_conflict(blog_post, cache_data):
                # Handle conflict
                await self._handle_conflict(cache_key, blog_post, cache_data, content_service)
                return
            
            # Perform auto-save
            from app.schemas.content import BlogPostUpdate
            update_data = BlogPostUpdate(
                content=cache_data["content"],
                title=cache_data["title"]
            )
            
            updated_post = content_service.update_blog_post(
                cache_data["post_id"],
                cache_data["user_id"],
                update_data,
                changes_summary="Auto-saved"
            )
            
            if updated_post:
                cache_data["save_pending"] = False
                cache_data["last_saved"] = datetime.utcnow()
                
                # Clean up old versions if needed
                await self._cleanup_old_versions(cache_data["post_id"], content_service)
        
        finally:
            db.close()
    
    def get_autosave_status(self, post_id: str, user_id: str) -> Dict[str, Any]:
        """Get auto-save status for a post"""
        cache_key = f"{user_id}:{post_id}"
        
        if cache_key not in self._autosave_cache:
            return {"status": "no_autosave", "last_saved": None}
        
        cache_data = self._autosave_cache[cache_key]
        
        return {
            "status": "pending" if cache_data.get("save_pending", False) else "saved",
            "last_modified": cache_data.get("last_modified"),
            "last_saved": cache_data.get("last_saved"),
            "next_save_in": self._calculate_next_save_time(cache_key)
        }
    
    def force_save(self, post_id: str, user_id: str) -> Dict[str, Any]:
        """Force an immediate save"""
        cache_key = f"{user_id}:{post_id}"
        
        if cache_key not in self._autosave_cache:
            return {"status": "no_content", "message": "No content to save"}
        
        # Perform immediate save
        asyncio.create_task(self._perform_autosave(cache_key))
        
        return {"status": "saving", "message": "Save initiated"}
    
    def get_version_diff(self, post_id: str, user_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """Get diff between two versions"""
        db = next(get_db())
        try:
            content_service = ContentService(db)
            
            v1 = content_service.get_post_version(post_id, version1, user_id)
            v2 = content_service.get_post_version(post_id, version2, user_id)
            
            if not v1 or not v2:
                return {"error": "Version not found"}
            
            # Simple diff implementation (in production, use a proper diff library)
            diff = self._calculate_diff(v1.content or "", v2.content or "")
            title_diff = self._calculate_diff(v1.title or "", v2.title or "")
            
            return {
                "version1": version1,
                "version2": version2,
                "content_diff": diff,
                "title_diff": title_diff,
                "word_count_change": (v2.word_count or 0) - (v1.word_count or 0)
            }
        
        finally:
            db.close()
    
    def resolve_conflict(self, post_id: str, user_id: str, resolution: str, 
                        content: Optional[str] = None) -> Dict[str, Any]:
        """Resolve editing conflicts"""
        cache_key = f"{user_id}:{post_id}"
        
        if cache_key not in self._autosave_cache:
            return {"error": "No conflict to resolve"}
        
        cache_data = self._autosave_cache[cache_key]
        
        if resolution == "keep_local":
            # Keep the cached version
            asyncio.create_task(self._perform_autosave(cache_key))
            return {"status": "resolved", "action": "kept_local_changes"}
        
        elif resolution == "keep_remote":
            # Discard cached version, reload from database
            db = next(get_db())
            try:
                content_service = ContentService(db)
                blog_post = content_service.get_blog_post(post_id, user_id)
                
                if blog_post:
                    cache_data.update({
                        "content": blog_post.content,
                        "title": blog_post.title,
                        "save_pending": False,
                        "last_saved": datetime.utcnow()
                    })
                
                return {"status": "resolved", "action": "kept_remote_changes"}
            
            finally:
                db.close()
        
        elif resolution == "merge" and content:
            # Use provided merged content
            cache_data.update({
                "content": content,
                "save_pending": True
            })
            asyncio.create_task(self._perform_autosave(cache_key))
            return {"status": "resolved", "action": "merged_changes"}
        
        else:
            return {"error": "Invalid resolution method"}
    
    def _has_conflict(self, blog_post: BlogPost, cache_data: Dict[str, Any]) -> bool:
        """Check if there's a conflict between cached and database versions"""
        # Simple conflict detection based on update time
        last_modified = cache_data.get("last_modified")
        if not last_modified:
            return False
        
        # If the post was updated after our last modification, there might be a conflict
        return blog_post.updated_at > last_modified
    
    async def _handle_conflict(self, cache_key: str, blog_post: BlogPost, 
                              cache_data: Dict[str, Any], content_service: ContentService):
        """Handle editing conflicts"""
        # Mark conflict in cache
        cache_data["conflict"] = {
            "detected_at": datetime.utcnow(),
            "remote_content": blog_post.content,
            "remote_title": blog_post.title,
            "local_content": cache_data["content"],
            "local_title": cache_data["title"]
        }
        
        # Set conflict timeout
        cache_data["conflict_timeout"] = datetime.utcnow() + timedelta(
            seconds=self.conflict_resolution_timeout
        )
    
    async def _cleanup_old_versions(self, post_id: str, content_service: ContentService):
        """Clean up old versions to maintain version limit"""
        versions = content_service.db.query(PostVersion).filter(
            PostVersion.post_id == post_id
        ).order_by(PostVersion.version_number.desc()).all()
        
        if len(versions) > self.max_versions_per_post:
            # Keep the most recent versions, delete the oldest
            versions_to_delete = versions[self.max_versions_per_post:]
            
            for version in versions_to_delete:
                content_service.db.delete(version)
            
            content_service.db.commit()
    
    def _calculate_next_save_time(self, cache_key: str) -> Optional[int]:
        """Calculate seconds until next auto-save"""
        last_save = self._save_intervals.get(cache_key)
        if not last_save:
            return None
        
        elapsed = (datetime.utcnow() - last_save).seconds
        return max(0, self.save_interval - elapsed)
    
    def _calculate_diff(self, text1: str, text2: str) -> Dict[str, Any]:
        """Calculate simple diff between two texts"""
        # This is a very basic diff implementation
        # In production, use a proper diff library like difflib or python-diff-match-patch
        
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        added_lines = []
        removed_lines = []
        
        # Simple line-by-line comparison
        for i, line in enumerate(lines2):
            if i >= len(lines1) or line != lines1[i]:
                added_lines.append({"line": i + 1, "content": line})
        
        for i, line in enumerate(lines1):
            if i >= len(lines2) or line != lines2[i]:
                removed_lines.append({"line": i + 1, "content": line})
        
        return {
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "total_changes": len(added_lines) + len(removed_lines)
        }
    
    def cleanup_cache(self, max_age_hours: int = 24):
        """Clean up old cache entries"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        keys_to_remove = []
        for cache_key, cache_data in self._autosave_cache.items():
            last_modified = cache_data.get("last_modified")
            if last_modified and last_modified < cutoff_time:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self._autosave_cache[key]
            if key in self._save_intervals:
                del self._save_intervals[key]
        
        return {"cleaned_entries": len(keys_to_remove)}