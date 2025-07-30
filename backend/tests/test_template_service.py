"""
Unit tests for template service functionality
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.template_service import TemplateService
from app.models.content import ContentTemplate, TemplateUsage, TemplateRating
from app.models.user import User


class TestTemplateService:
    """Test cases for TemplateService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=Session)
        self.template_service = TemplateService(self.mock_db)
        
        # Mock user
        self.mock_user = Mock(spec=User)
        self.mock_user.id = "user123"
        self.mock_user.email = "test@example.com"
        
        # Mock template
        self.mock_template = Mock(spec=ContentTemplate)
        self.mock_template.id = "template123"
        self.mock_template.name = "Test Template"
        self.mock_template.template_content = "Hello {{name}}, welcome to {{company}}!"
        self.mock_template.category = "business"
        self.mock_template.template_type = "article"
        self.mock_template.industry = "General"
        self.mock_template.is_public = True
        self.mock_template.usage_count = 5
        self.mock_template.created_by = "user123"
        self.mock_template.created_at = datetime.utcnow()
        self.mock_template.updated_at = datetime.utcnow()
    
    def test_extract_placeholders(self):
        """Test placeholder extraction from template content"""
        template_content = "Hello {{name}}, welcome to {{company}}! Your {{role}} is important."
        
        placeholders = self.template_service.extract_placeholders(template_content)
        
        assert set(placeholders) == {"name", "company", "role"}
        assert len(placeholders) == 3
    
    def test_extract_placeholders_with_duplicates(self):
        """Test placeholder extraction removes duplicates"""
        template_content = "{{name}} and {{name}} work at {{company}}. {{name}} likes {{company}}."
        
        placeholders = self.template_service.extract_placeholders(template_content)
        
        assert set(placeholders) == {"name", "company"}
        assert len(placeholders) == 2
    
    def test_extract_placeholders_empty_content(self):
        """Test placeholder extraction with no placeholders"""
        template_content = "This is a simple template with no placeholders."
        
        placeholders = self.template_service.extract_placeholders(template_content)
        
        assert placeholders == []
    
    def test_replace_placeholders_success(self):
        """Test successful placeholder replacement"""
        template_content = "Hello {{name}}, welcome to {{company}}!"
        variables = {"name": "John", "company": "Acme Corp"}
        
        result, found, replaced = self.template_service.replace_placeholders(template_content, variables)
        
        assert result == "Hello John, welcome to Acme Corp!"
        assert set(found) == {"name", "company"}
        assert set(replaced) == {"name", "company"}
    
    def test_replace_placeholders_partial(self):
        """Test placeholder replacement with missing variables"""
        template_content = "Hello {{name}}, welcome to {{company}}! Your {{role}} is important."
        variables = {"name": "John", "company": "Acme Corp"}
        
        result, found, replaced = self.template_service.replace_placeholders(template_content, variables)
        
        assert result == "Hello John, welcome to Acme Corp! Your {{role}} is important."
        assert set(found) == {"name", "company", "role"}
        assert set(replaced) == {"name", "company"}
    
    def test_track_template_usage_success(self):
        """Test successful template usage tracking"""
        template_id = "template123"
        user_id = "user123"
        variables_used = {"name": "John", "company": "Acme"}
        
        # Mock template query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_template
        
        self.template_service.track_template_usage(
            template_id, user_id, variables_used, "technology", "blog post"
        )
        
        # Verify TemplateUsage was added
        self.mock_db.add.assert_called_once()
        added_usage = self.mock_db.add.call_args[0][0]
        assert isinstance(added_usage, TemplateUsage)
        assert added_usage.template_id == template_id
        assert added_usage.user_id == user_id
        assert added_usage.variables_used == variables_used
        assert added_usage.industry_context == "technology"
        assert added_usage.usage_context == "blog post"
        
        # Verify template usage count was incremented
        assert self.mock_template.usage_count == 6
        
        # Verify commit was called
        self.mock_db.commit.assert_called_once()
    
    def test_track_template_usage_template_not_found(self):
        """Test template usage tracking when template doesn't exist"""
        # Mock template query to return None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        self.template_service.track_template_usage(
            "nonexistent", "user123", {"name": "John"}
        )
        
        # Verify TemplateUsage was still added (usage tracking is independent)
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
    
    def test_track_template_usage_database_error(self):
        """Test template usage tracking with database error"""
        # Mock database error
        self.mock_db.add.side_effect = Exception("Database error")
        
        self.template_service.track_template_usage(
            "template123", "user123", {"name": "John"}
        )
        
        # Verify rollback was called
        self.mock_db.rollback.assert_called_once()
    
    def test_get_template_analytics_success(self):
        """Test successful template analytics retrieval"""
        template_id = "template123"
        user_id = "user123"
        
        # Mock template query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_template
        
        # Mock usage queries
        self.mock_db.query.return_value.filter.return_value.count.return_value = 10
        
        # Mock rating queries
        mock_ratings = [Mock(rating=4), Mock(rating=5), Mock(rating=3)]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_ratings
        
        # Mock usage records for variable analysis
        mock_usage_records = [
            Mock(variables_used={"name": "John", "company": "Acme"}, industry_context="tech"),
            Mock(variables_used={"name": "Jane", "role": "Manager"}, industry_context="business"),
        ]
        
        # Configure mock to return different results for different queries
        def mock_query_side_effect(*args):
            mock_query = Mock()
            if args[0] == ContentTemplate:
                mock_query.filter.return_value.first.return_value = self.mock_template
            elif args[0] == TemplateUsage:
                if hasattr(mock_query.filter.return_value, 'count'):
                    mock_query.filter.return_value.count.return_value = 10
                if hasattr(mock_query.filter.return_value, 'all'):
                    mock_query.filter.return_value.all.return_value = mock_usage_records
                if hasattr(mock_query.filter.return_value, 'order_by'):
                    mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_usage_records[:1]
            elif args[0] == TemplateRating:
                mock_query.filter.return_value.all.return_value = mock_ratings
            return mock_query
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        result = self.template_service.get_template_analytics(template_id, user_id)
        
        assert result is not None
        assert result["template_id"] == template_id
        assert result["template_name"] == "Test Template"
        assert result["total_usage"] == 10
        assert result["average_rating"] == 4.0  # (4+5+3)/3
        assert result["total_ratings"] == 3
        assert "popular_variables" in result
        assert "usage_by_industry" in result
        assert "recent_usage" in result
    
    def test_get_template_analytics_not_found(self):
        """Test template analytics when template not found"""
        # Mock template query to return None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.template_service.get_template_analytics("nonexistent", "user123")
        
        assert result is None
    
    def test_get_popular_templates_success(self):
        """Test successful popular templates retrieval"""
        mock_templates = [self.mock_template]
        
        # Mock the complete query chain
        self.mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_templates
        
        result = self.template_service.get_popular_templates(limit=5, category="business")
        
        assert len(result) == 1
        assert result[0] == self.mock_template
        
        # Verify query was built correctly
        self.mock_db.query.assert_called_with(ContentTemplate)
    
    def test_get_popular_templates_no_category(self):
        """Test popular templates retrieval without category filter"""
        mock_templates = [self.mock_template]
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_templates
        self.mock_db.query.return_value = mock_query
        
        result = self.template_service.get_popular_templates(limit=10)
        
        assert len(result) == 1
        # Verify category filter was not applied
        mock_query.filter.assert_called_once()  # Only public filter
    
    def test_rate_template_new_rating(self):
        """Test rating a template for the first time"""
        template_id = "template123"
        user_id = "user123"
        rating = 5
        comment = "Great template!"
        
        # Mock existing rating query to return None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.template_service.rate_template(template_id, user_id, rating, comment)
        
        assert result is True
        
        # Verify new rating was added
        self.mock_db.add.assert_called_once()
        added_rating = self.mock_db.add.call_args[0][0]
        assert isinstance(added_rating, TemplateRating)
        assert added_rating.template_id == template_id
        assert added_rating.user_id == user_id
        assert added_rating.rating == rating
        assert added_rating.comment == comment
        
        self.mock_db.commit.assert_called_once()
    
    def test_rate_template_update_existing(self):
        """Test updating an existing template rating"""
        template_id = "template123"
        user_id = "user123"
        rating = 4
        comment = "Updated comment"
        
        # Mock existing rating
        mock_existing_rating = Mock(spec=TemplateRating)
        mock_existing_rating.rating = 3
        mock_existing_rating.comment = "Old comment"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_existing_rating
        
        result = self.template_service.rate_template(template_id, user_id, rating, comment)
        
        assert result is True
        
        # Verify existing rating was updated
        assert mock_existing_rating.rating == rating
        assert mock_existing_rating.comment == comment
        assert hasattr(mock_existing_rating, 'updated_at')
        
        # Verify no new rating was added
        self.mock_db.add.assert_not_called()
        self.mock_db.commit.assert_called_once()
    
    def test_rate_template_database_error(self):
        """Test template rating with database error"""
        # Mock database error
        self.mock_db.commit.side_effect = Exception("Database error")
        
        result = self.template_service.rate_template("template123", "user123", 5)
        
        assert result is False
        self.mock_db.rollback.assert_called_once()
    
    def test_seed_default_templates_success(self):
        """Test successful default template seeding"""
        user_id = "user123"
        
        # Mock existing template query to return None (no existing templates)
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.template_service.seed_default_templates(user_id)
        
        # Should create 5 default templates (based on the service implementation)
        assert result == 5
        
        # Verify templates were added
        assert self.mock_db.add.call_count == 5
        
        # Verify all added objects are ContentTemplate instances
        for call in self.mock_db.add.call_args_list:
            added_template = call[0][0]
            assert isinstance(added_template, ContentTemplate)
            assert added_template.created_by == user_id
            assert added_template.is_public is True
            assert added_template.usage_count == 0
        
        self.mock_db.commit.assert_called_once()
    
    def test_seed_default_templates_some_exist(self):
        """Test default template seeding when some templates already exist"""
        user_id = "user123"
        
        # Mock existing template query to return a template for first query, None for others
        existing_calls = [self.mock_template, None, None, None, None]
        self.mock_db.query.return_value.filter.return_value.first.side_effect = existing_calls
        
        result = self.template_service.seed_default_templates(user_id)
        
        # Should create 4 templates (5 total - 1 existing)
        assert result == 4
        assert self.mock_db.add.call_count == 4
        self.mock_db.commit.assert_called_once()
    
    def test_seed_default_templates_database_error(self):
        """Test default template seeding with database error"""
        # Mock database error
        self.mock_db.commit.side_effect = Exception("Database error")
        
        result = self.template_service.seed_default_templates("user123")
        
        assert result == 0
        self.mock_db.rollback.assert_called_once()
    
    def test_get_template_stats_success(self):
        """Test successful template statistics retrieval"""
        # Mock various queries for statistics
        self.mock_db.query.return_value.count.return_value = 100  # total templates
        
        # Mock filter chain for public templates
        mock_filter_query = Mock()
        mock_filter_query.count.return_value = 75  # public templates
        self.mock_db.query.return_value.filter.return_value = mock_filter_query
        
        # Mock sum query for total usage
        self.mock_db.query.return_value.scalar.return_value = 500
        
        # Mock category stats
        mock_category_stats = [
            Mock(category="business", template_count=30, total_usage=200),
            Mock(category="technology", template_count=25, total_usage=150),
        ]
        self.mock_db.query.return_value.group_by.return_value.all.return_value = mock_category_stats
        
        # Mock popular and recent templates
        mock_templates = [self.mock_template]
        
        def mock_query_side_effect(*args):
            mock_query = Mock()
            if hasattr(mock_query, 'count'):
                mock_query.count.return_value = 100
            if hasattr(mock_query, 'scalar'):
                mock_query.scalar.return_value = 500
            if hasattr(mock_query, 'filter'):
                mock_filter = Mock()
                mock_filter.count.return_value = 75
                mock_filter.order_by.return_value.limit.return_value.all.return_value = mock_templates
                mock_query.filter.return_value = mock_filter
            if hasattr(mock_query, 'group_by'):
                mock_query.group_by.return_value.all.return_value = mock_category_stats
            return mock_query
        
        self.mock_db.query.side_effect = mock_query_side_effect
        
        result = self.template_service.get_template_stats()
        
        assert "total_templates" in result
        assert "public_templates" in result
        assert "private_templates" in result
        assert "total_usage" in result
        assert "category_stats" in result
        assert "most_popular_templates" in result
        assert "recent_templates" in result
    
    def test_get_template_stats_database_error(self):
        """Test template statistics with database error"""
        # Mock database error
        self.mock_db.query.side_effect = Exception("Database error")
        
        result = self.template_service.get_template_stats()
        
        assert result == {}


@pytest.fixture
def template_service():
    """Fixture for TemplateService with mocked database"""
    mock_db = Mock(spec=Session)
    return TemplateService(mock_db)


def test_template_service_initialization(template_service):
    """Test TemplateService initialization"""
    assert template_service is not None
    assert hasattr(template_service, 'db')
    assert hasattr(template_service, 'extract_placeholders')
    assert hasattr(template_service, 'replace_placeholders')
    assert hasattr(template_service, 'track_template_usage')
    assert hasattr(template_service, 'get_template_analytics')
    assert hasattr(template_service, 'get_popular_templates')
    assert hasattr(template_service, 'rate_template')
    assert hasattr(template_service, 'seed_default_templates')
    assert hasattr(template_service, 'get_template_stats')