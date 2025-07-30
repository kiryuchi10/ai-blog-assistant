#!/usr/bin/env python3
"""
Script to seed default templates into the database
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.template_service import TemplateService
from app.models.user import User
from app.models.content import ContentTemplate


def seed_default_templates():
    """Seed default templates into the database"""
    db = SessionLocal()
    
    try:
        # Create a system user for seeding templates
        system_user_id = "system-user-123"
        
        # Check if system user exists, create if not
        system_user = db.query(User).filter(User.id == system_user_id).first()
        if not system_user:
            system_user = User(
                id=system_user_id,
                email="system@ai-blog-assistant.com",
                password_hash="system",  # Not used for login
                first_name="System",
                last_name="User"
            )
            db.add(system_user)
            db.commit()
            print("✅ Created system user for template seeding")
        
        # Initialize template service
        template_service = TemplateService(db)
        
        # Seed default templates
        created_count = template_service.seed_default_templates(system_user_id)
        
        print(f"✅ Successfully seeded {created_count} default templates")
        
        # List all templates
        templates = db.query(ContentTemplate).all()
        print(f"\n📋 Total templates in database: {len(templates)}")
        
        for template in templates:
            print(f"  - {template.name} ({template.category}/{template.template_type})")
            print(f"    Usage count: {template.usage_count}")
            print(f"    Public: {template.is_public}")
            print(f"    Placeholders: {len(template.placeholders or [])}")
            print()
        
    except Exception as e:
        print(f"❌ Error seeding templates: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def test_template_operations():
    """Test basic template operations"""
    db = SessionLocal()
    
    try:
        template_service = TemplateService(db)
        
        # Test placeholder extraction
        test_content = "Hello {{name}}, welcome to {{company}}! Your {{role}} is {{department}}."
        placeholders = template_service.extract_placeholders(test_content)
        print(f"🔍 Extracted placeholders: {placeholders}")
        
        # Test placeholder replacement
        variables = {
            "name": "John Doe",
            "company": "Acme Corporation",
            "role": "Software Engineer",
            "department": "Engineering"
        }
        
        result, found, replaced = template_service.replace_placeholders(test_content, variables)
        print(f"📝 Original: {test_content}")
        print(f"📝 Replaced: {result}")
        print(f"🔍 Found placeholders: {found}")
        print(f"✅ Replaced placeholders: {replaced}")
        
        # Test getting popular templates
        popular = template_service.get_popular_templates(limit=3)
        print(f"\n🏆 Popular templates ({len(popular)}):")
        for template in popular:
            print(f"  - {template.name} (usage: {template.usage_count})")
        
        # Test template stats
        stats = template_service.get_template_stats()
        if stats:
            print(f"\n📊 Template Statistics:")
            print(f"  Total templates: {stats.get('total_templates', 0)}")
            print(f"  Public templates: {stats.get('public_templates', 0)}")
            print(f"  Private templates: {stats.get('private_templates', 0)}")
            print(f"  Total usage: {stats.get('total_usage', 0)}")
        
    except Exception as e:
        print(f"❌ Error testing template operations: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding default templates...")
    print("=" * 50)
    
    seed_default_templates()
    
    print("\n🧪 Testing template operations...")
    print("=" * 50)
    
    test_template_operations()
    
    print("\n🎉 Template seeding and testing completed!")