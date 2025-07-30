"""
Integration tests for content CRUD operations
"""
import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.content import BlogPost, PostVersion
from app.services.auth_service import AuthService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_content.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    try:
        # Create test user
        auth_service = AuthService(db)
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        user = auth_service.create_user(user_data)
        
        # Generate token
        token = auth_service.create_access_token({"user_id": user.id, "email": user.email})
        
        return {"user": user, "token": token}
    finally:
        db.close()

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers"""
    return {"Authorization": f"Bearer {test_user['token']}"}

class TestBlogPostCRUD:
    """Test blog post CRUD operations"""
    
    def test_create_blog_post(self, setup_database, auth_headers):
        """Test creating a new blog post"""
        post_data = {
            "title": "Test Blog Post",
            "content": "This is a test blog post content with more than 100 characters to meet the minimum requirement for content length.",
            "meta_description": "Test meta description",
            "keywords": ["test", "blog", "post"],
            "status": "draft",
            "post_type": "article",
            "tone": "professional",
            "tags": ["testing", "api"]
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]
        assert data["status"] == post_data["status"]
        assert data["word_count"] > 0
        assert data["reading_time"] > 0
        assert data["seo_score"] >= 0
        
        return data["id"]  # Return post ID for other tests
    
    def test_get_blog_post(self, setup_database, auth_headers):
        """Test retrieving a blog post"""
        # First create a post
        post_id = self.test_create_blog_post(setup_database, auth_headers)
        
        response = client.get(f"/api/v1/content/posts/{post_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post_id
        assert data["title"] == "Test Blog Post"
    
    def test_get_blog_posts_list(self, setup_database, auth_headers):
        """Test retrieving blog posts list"""
        response = client.get("/api/v1/content/posts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        assert isinstance(data["posts"], list)
    
    def test_update_blog_post(self, setup_database, auth_headers):
        """Test updating a blog post"""
        # First create a post
        post_id = self.test_create_blog_post(setup_database, auth_headers)
        
        update_data = {
            "title": "Updated Test Blog Post",
            "content": "This is updated content for the test blog post with sufficient length to meet requirements.",
            "status": "published"
        }
        
        response = client.put(
            f"/api/v1/content/posts/{post_id}",
            json=update_data,
            headers=auth_headers,
            params={"changes_summary": "Updated title and content"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["status"] == update_data["status"]
    
    def test_delete_blog_post(self, setup_database, auth_headers):
        """Test deleting a blog post"""
        # First create a post
        post_id = self.test_create_blog_post(setup_database, auth_headers)
        
        response = client.delete(f"/api/v1/content/posts/{post_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify post is deleted
        response = client.get(f"/api/v1/content/posts/{post_id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_search_blog_posts(self, setup_database, auth_headers):
        """Test searching blog posts"""
        # Create a post first
        self.test_create_blog_post(setup_database, auth_headers)
        
        response = client.get(
            "/api/v1/content/posts",
            params={"query": "test", "status": "draft"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) >= 0
    
    def test_get_nonexistent_post(self, setup_database, auth_headers):
        """Test retrieving a non-existent blog post"""
        response = client.get("/api/v1/content/posts/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

class TestVersionControl:
    """Test version control functionality"""
    
    def test_get_post_versions(self, setup_database, auth_headers):
        """Test retrieving post versions"""
        # Create and update a post to generate versions
        post_data = {
            "title": "Version Test Post",
            "content": "Original content for version testing with sufficient length to meet minimum requirements.",
            "status": "draft"
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        post_id = response.json()["id"]
        
        # Update the post to create a new version
        update_data = {
            "content": "Updated content for version testing with different text to create a new version."
        }
        
        client.put(
            f"/api/v1/content/posts/{post_id}",
            json=update_data,
            headers=auth_headers,
            params={"changes_summary": "Updated content for version test"}
        )
        
        # Get versions
        response = client.get(f"/api/v1/content/posts/{post_id}/versions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "versions" in data
        assert "total" in data
        assert len(data["versions"]) >= 1
    
    def test_get_specific_version(self, setup_database, auth_headers):
        """Test retrieving a specific version"""
        # Create a post
        post_data = {
            "title": "Specific Version Test",
            "content": "Content for specific version testing with adequate length for requirements.",
            "status": "draft"
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        post_id = response.json()["id"]
        
        # Get version 1
        response = client.get(f"/api/v1/content/posts/{post_id}/versions/1", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version_number"] == 1
        assert data["title"] == post_data["title"]
    
    def test_rollback_to_version(self, setup_database, auth_headers):
        """Test rolling back to a previous version"""
        # Create a post
        post_data = {
            "title": "Rollback Test Post",
            "content": "Original content for rollback testing with sufficient length to meet requirements.",
            "status": "draft"
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        post_id = response.json()["id"]
        
        # Update the post
        update_data = {
            "title": "Updated Rollback Test Post",
            "content": "Updated content for rollback testing with different text to create version differences."
        }
        
        client.put(
            f"/api/v1/content/posts/{post_id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Rollback to version 1
        response = client.post(
            f"/api/v1/content/posts/{post_id}/rollback/1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == post_data["title"]  # Should be original title
        assert data["content"] == post_data["content"]  # Should be original content

class TestSEOAnalysis:
    """Test SEO analysis functionality"""
    
    def test_analyze_post_seo(self, setup_database, auth_headers):
        """Test SEO analysis for a blog post"""
        # Create a post
        post_data = {
            "title": "SEO Test Post with Keywords",
            "content": "This is content for SEO testing. It contains keywords like SEO, testing, and optimization. The content is long enough to provide meaningful analysis results for keyword density and readability metrics.",
            "meta_description": "SEO test post for analyzing optimization metrics",
            "keywords": ["SEO", "testing", "optimization"],
            "status": "draft"
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        post_id = response.json()["id"]
        
        # Analyze SEO
        analysis_data = {
            "content": post_data["content"],
            "target_keywords": ["SEO", "testing"]
        }
        
        response = client.post(
            f"/api/v1/content/posts/{post_id}/seo-analysis",
            json=analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "seo_score" in data
        assert "recommendations" in data
        assert "keyword_analysis" in data
        assert "readability" in data
        assert isinstance(data["seo_score"], int)
        assert 0 <= data["seo_score"] <= 100
    
    def test_analyze_content_seo(self, setup_database, auth_headers):
        """Test SEO analysis for any content"""
        analysis_data = {
            "content": "This is test content for SEO analysis. It includes keywords and sufficient text for meaningful analysis of readability and keyword density metrics.",
            "target_keywords": ["test", "SEO", "analysis"]
        }
        
        response = client.post("/api/v1/content/seo/analyze", json=analysis_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "seo_score" in data
        assert "keyword_analysis" in data
        assert "readability" in data

class TestAutoSave:
    """Test auto-save functionality"""
    
    def test_schedule_autosave(self, setup_database, auth_headers):
        """Test scheduling auto-save"""
        # Create a post first
        post_data = {
            "title": "AutoSave Test Post",
            "content": "Content for auto-save testing with adequate length for requirements.",
            "status": "draft"
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        post_id = response.json()["id"]
        
        # Schedule auto-save
        autosave_data = {
            "content": "Updated content for auto-save testing",
            "title": "Updated AutoSave Test Post"
        }
        
        response = client.post(
            f"/api/v1/content/posts/{post_id}/autosave",
            params=autosave_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "scheduled"
    
    def test_get_autosave_status(self, setup_database, auth_headers):
        """Test getting auto-save status"""
        # Create a post first
        post_data = {
            "title": "AutoSave Status Test",
            "content": "Content for auto-save status testing with sufficient length.",
            "status": "draft"
        }
        
        response = client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        post_id = response.json()["id"]
        
        response = client.get(f"/api/v1/content/posts/{post_id}/autosave-status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

class TestSearchAndCategorization:
    """Test search and categorization functionality"""
    
    def test_search_content(self, setup_database, auth_headers):
        """Test content search"""
        # Create a post with searchable content
        post_data = {
            "title": "Searchable Test Post",
            "content": "This content contains unique searchable terms like 'findme' and 'searchterm' for testing search functionality.",
            "status": "published"
        }
        
        client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        
        response = client.get(
            "/api/v1/content/search",
            params={"q": "findme", "limit": 10},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "total" in data
        assert data["query"] == "findme"
    
    def test_get_posts_by_category(self, setup_database, auth_headers):
        """Test getting posts by category"""
        # Create a post with a category
        post_data = {
            "title": "Category Test Post",
            "content": "Content for category testing with adequate length for requirements.",
            "template_category": "technology",
            "status": "published"
        }
        
        client.post("/api/v1/content/posts", json=post_data, headers=auth_headers)
        
        response = client.get(
            "/api/v1/content/categories/technology/posts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "posts" in data
        assert "total" in data
        assert data["category"] == "technology"

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_create_post_invalid_data(self, setup_database, auth_headers):
        """Test creating post with invalid data"""
        invalid_data = {
            "title": "A",  # Too short
            "content": "Short",  # Too short
        }
        
        response = client.post("/api/v1/content/posts", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_unauthorized_access(self, setup_database):
        """Test accessing endpoints without authentication"""
        response = client.get("/api/v1/content/posts")
        assert response.status_code == 401  # Unauthorized
    
    def test_update_nonexistent_post(self, setup_database, auth_headers):
        """Test updating a non-existent post"""
        update_data = {
            "title": "Updated Title",
            "content": "Updated content with sufficient length for requirements."
        }
        
        response = client.put(
            "/api/v1/content/posts/nonexistent-id",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__])