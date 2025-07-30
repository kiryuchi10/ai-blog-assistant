"""
Template management service with analytics and seeding functionality
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from app.models.content import ContentTemplate, TemplateUsage, TemplateRating
from app.models.user import User
from app.schemas.template import TemplateSearchRequest


logger = logging.getLogger(__name__)


class TemplateService:
    """Service for template management and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def extract_placeholders(self, template_content: str) -> List[str]:
        """Extract placeholder variables from template content"""
        # Find placeholders in format {{variable_name}}
        placeholders = re.findall(r'\{\{(\w+)\}\}', template_content)
        return list(set(placeholders))  # Remove duplicates
    
    def replace_placeholders(self, template_content: str, variables: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
        """Replace placeholders in template content with provided variables"""
        placeholders_found = self.extract_placeholders(template_content)
        placeholders_replaced = []
        
        content = template_content
        for placeholder in placeholders_found:
            if placeholder in variables:
                content = content.replace(f'{{{{{placeholder}}}}}', variables[placeholder])
                placeholders_replaced.append(placeholder)
        
        return content, placeholders_found, placeholders_replaced
    
    def track_template_usage(self, template_id: str, user_id: str, variables_used: Dict[str, str], 
                           industry_context: Optional[str] = None, usage_context: Optional[str] = None):
        """Track template usage for analytics"""
        try:
            usage = TemplateUsage(
                template_id=template_id,
                user_id=user_id,
                variables_used=variables_used,
                industry_context=industry_context,
                usage_context=usage_context
            )
            
            self.db.add(usage)
            
            # Increment template usage count
            template = self.db.query(ContentTemplate).filter(ContentTemplate.id == template_id).first()
            if template:
                template.usage_count += 1
            
            self.db.commit()
            logger.info(f"Template usage tracked: {template_id} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track template usage: {str(e)}")
            self.db.rollback()
    
    def get_template_analytics(self, template_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a template"""
        try:
            template = self.db.query(ContentTemplate).filter(
                and_(
                    ContentTemplate.id == template_id,
                    ContentTemplate.created_by == user_id
                )
            ).first()
            
            if not template:
                return None
            
            # Get usage statistics
            now = datetime.utcnow()
            month_ago = now - timedelta(days=30)
            week_ago = now - timedelta(days=7)
            
            total_usage = self.db.query(TemplateUsage).filter(
                TemplateUsage.template_id == template_id
            ).count()
            
            usage_this_month = self.db.query(TemplateUsage).filter(
                and_(
                    TemplateUsage.template_id == template_id,
                    TemplateUsage.created_at >= month_ago
                )
            ).count()
            
            usage_this_week = self.db.query(TemplateUsage).filter(
                and_(
                    TemplateUsage.template_id == template_id,
                    TemplateUsage.created_at >= week_ago
                )
            ).count()
            
            # Get rating statistics
            ratings = self.db.query(TemplateRating).filter(
                TemplateRating.template_id == template_id
            ).all()
            
            average_rating = None
            total_ratings = len(ratings)
            if ratings:
                average_rating = sum(r.rating for r in ratings) / total_ratings
            
            # Get popular variables
            usage_records = self.db.query(TemplateUsage).filter(
                TemplateUsage.template_id == template_id
            ).all()
            
            popular_variables = {}
            usage_by_industry = {}
            
            for usage in usage_records:
                if usage.variables_used:
                    for var in usage.variables_used.keys():
                        popular_variables[var] = popular_variables.get(var, 0) + 1
                
                if usage.industry_context:
                    industry = usage.industry_context
                    usage_by_industry[industry] = usage_by_industry.get(industry, 0) + 1
            
            # Get recent usage
            recent_usage = self.db.query(TemplateUsage).filter(
                TemplateUsage.template_id == template_id
            ).order_by(desc(TemplateUsage.created_at)).limit(10).all()
            
            recent_usage_data = [
                {
                    "date": usage.created_at.isoformat(),
                    "user_id": usage.user_id,
                    "variables_used": list(usage.variables_used.keys()) if usage.variables_used else [],
                    "industry_context": usage.industry_context
                }
                for usage in recent_usage
            ]
            
            return {
                "template_id": template_id,
                "template_name": template.name,
                "total_usage": total_usage,
                "usage_this_month": usage_this_month,
                "usage_this_week": usage_this_week,
                "average_rating": average_rating,
                "total_ratings": total_ratings,
                "popular_variables": popular_variables,
                "usage_by_industry": usage_by_industry,
                "recent_usage": recent_usage_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get template analytics: {str(e)}")
            return None
    
    def get_popular_templates(self, limit: int = 10, category: Optional[str] = None) -> List[ContentTemplate]:
        """Get most popular templates based on usage count"""
        try:
            query = self.db.query(ContentTemplate).filter(ContentTemplate.is_public == True)
            
            if category:
                query = query.filter(ContentTemplate.category == category)
            
            templates = query.order_by(desc(ContentTemplate.usage_count)).limit(limit).all()
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get popular templates: {str(e)}")
            return []
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get overall template statistics"""
        try:
            total_templates = self.db.query(ContentTemplate).count()
            public_templates = self.db.query(ContentTemplate).filter(ContentTemplate.is_public == True).count()
            private_templates = total_templates - public_templates
            
            total_usage = self.db.query(func.sum(ContentTemplate.usage_count)).scalar() or 0
            
            # Category statistics
            category_stats = self.db.query(
                ContentTemplate.category,
                func.count(ContentTemplate.id).label('template_count'),
                func.sum(ContentTemplate.usage_count).label('total_usage')
            ).group_by(ContentTemplate.category).all()
            
            category_stats_data = []
            for stat in category_stats:
                popular_templates = self.db.query(ContentTemplate).filter(
                    ContentTemplate.category == stat.category
                ).order_by(desc(ContentTemplate.usage_count)).limit(3).all()
                
                category_stats_data.append({
                    "category": stat.category,
                    "template_count": stat.template_count,
                    "total_usage": stat.total_usage or 0,
                    "popular_templates": [
                        {
                            "id": str(t.id),
                            "name": t.name,
                            "usage_count": t.usage_count
                        }
                        for t in popular_templates
                    ]
                })
            
            # Most popular templates overall
            most_popular = self.get_popular_templates(limit=5)
            
            # Recent templates
            recent_templates = self.db.query(ContentTemplate).filter(
                ContentTemplate.is_public == True
            ).order_by(desc(ContentTemplate.created_at)).limit(5).all()
            
            return {
                "total_templates": total_templates,
                "public_templates": public_templates,
                "private_templates": private_templates,
                "total_usage": total_usage,
                "category_stats": category_stats_data,
                "most_popular_templates": most_popular,
                "recent_templates": recent_templates
            }
            
        except Exception as e:
            logger.error(f"Failed to get template stats: {str(e)}")
            return {}
    
    def seed_default_templates(self, user_id: str) -> int:
        """Seed default templates for the system"""
        try:
            default_templates = [
                {
                    "name": "Business Blog Post",
                    "description": "Professional business blog post template with company branding",
                    "template_content": """# {{title}}

## Introduction
{{company_name}} is excited to share insights about {{topic}}. In today's competitive market, understanding {{main_focus}} is crucial for business success.

## Main Content
{{main_content}}

### Key Points
- {{key_point_1}}
- {{key_point_2}}
- {{key_point_3}}

## Benefits for Your Business
{{benefits_section}}

### Why This Matters
{{importance_explanation}}

## Implementation Strategy
{{implementation_steps}}

## Conclusion
{{conclusion}}

At {{company_name}}, we believe that {{closing_statement}}. Contact us to learn more about how we can help your business {{call_to_action}}.

---
*About {{company_name}}: {{company_description}}*

*For more information, visit {{website_url}} or contact us at {{contact_email}}.*""",
                    "category": "business",
                    "template_type": "article",
                    "industry": "General",
                    "is_public": True,
                    "tags": ["business", "professional", "corporate", "marketing"]
                },
                {
                    "name": "How-To Guide",
                    "description": "Comprehensive step-by-step tutorial template",
                    "template_content": """# How to {{action}}: A Complete Guide

## Overview
Learn how to {{action}} with this comprehensive guide. Whether you're a beginner or looking to improve your skills, this tutorial will help you {{expected_outcome}}.

## What You'll Need
### Requirements
{{requirements_list}}

### Tools and Materials
{{tools_needed}}

### Estimated Time
{{time_estimate}}

## Step-by-Step Instructions

### Step 1: {{step_1_title}}
{{step_1_description}}

**Pro Tip:** {{step_1_tip}}

### Step 2: {{step_2_title}}
{{step_2_description}}

**Important:** {{step_2_warning}}

### Step 3: {{step_3_title}}
{{step_3_description}}

### Step 4: {{step_4_title}}
{{step_4_description}}

### Step 5: {{step_5_title}}
{{step_5_description}}

## Tips and Best Practices
{{tips_section}}

## Common Mistakes to Avoid
{{common_mistakes}}

## Troubleshooting
{{troubleshooting_guide}}

## Conclusion
Congratulations! You've successfully learned how to {{action}}. {{final_thoughts}}

## Next Steps
{{next_steps}}

---
*Need help? {{support_information}}*""",
                    "category": "education",
                    "template_type": "how_to",
                    "industry": "General",
                    "is_public": True,
                    "tags": ["tutorial", "guide", "how-to", "education", "step-by-step"]
                },
                {
                    "name": "Product Review",
                    "description": "Detailed product review template with pros and cons",
                    "template_content": """# {{product_name}} Review: {{review_headline}}

## Product Overview
{{product_description}}

### Key Specifications
- **Brand:** {{brand_name}}
- **Price:** {{price}}
- **Category:** {{product_category}}
- **Release Date:** {{release_date}}

## First Impressions
{{first_impressions}}

## Detailed Analysis

### Design and Build Quality
{{design_analysis}}

### Performance
{{performance_analysis}}

### Features
{{features_analysis}}

### User Experience
{{user_experience}}

## Pros and Cons

### What We Loved ✅
- {{pro_1}}
- {{pro_2}}
- {{pro_3}}
- {{pro_4}}

### What Could Be Better ❌
- {{con_1}}
- {{con_2}}
- {{con_3}}

## Comparison with Competitors
{{competitor_comparison}}

## Who Should Buy This?
{{target_audience}}

## Final Verdict
{{final_verdict}}

### Rating: {{rating}}/5 stars

## Where to Buy
{{purchase_information}}

---
*Disclaimer: {{disclaimer}}*""",
                    "category": "lifestyle",
                    "template_type": "review",
                    "industry": "Consumer Goods",
                    "is_public": True,
                    "tags": ["review", "product", "analysis", "comparison"]
                },
                {
                    "name": "Technology News Article",
                    "description": "Tech news article template with industry insights",
                    "template_content": """# {{headline}}

## Breaking News
{{news_summary}}

## Background
{{background_information}}

## Key Details
{{key_details}}

### What Happened
{{event_description}}

### Why It Matters
{{significance}}

### Industry Impact
{{industry_impact}}

## Expert Opinions
{{expert_quotes}}

## Technical Analysis
{{technical_details}}

## Market Implications
{{market_analysis}}

## What's Next?
{{future_predictions}}

## Related Stories
- {{related_story_1}}
- {{related_story_2}}
- {{related_story_3}}

---
*Stay updated with the latest tech news at {{publication_name}}*""",
                    "category": "technology",
                    "template_type": "news",
                    "industry": "Technology",
                    "is_public": True,
                    "tags": ["technology", "news", "industry", "analysis"]
                },
                {
                    "name": "Listicle Template",
                    "description": "Engaging listicle template for various topics",
                    "template_content": """# {{number}} {{topic}} That Will {{benefit}}

## Introduction
{{introduction_text}}

## {{item_1_number}}. {{item_1_title}}
{{item_1_description}}

### Why It Works
{{item_1_explanation}}

## {{item_2_number}}. {{item_2_title}}
{{item_2_description}}

### Pro Tip
{{item_2_tip}}

## {{item_3_number}}. {{item_3_title}}
{{item_3_description}}

## {{item_4_number}}. {{item_4_title}}
{{item_4_description}}

## {{item_5_number}}. {{item_5_title}}
{{item_5_description}}

### Expert Insight
{{item_5_insight}}

## {{item_6_number}}. {{item_6_title}}
{{item_6_description}}

## {{item_7_number}}. {{item_7_title}}
{{item_7_description}}

## Bonus: {{bonus_item_title}}
{{bonus_item_description}}

## Conclusion
{{conclusion_text}}

## Your Turn
{{call_to_action}}

---
*What's your favorite from this list? Let us know in the comments!*""",
                    "category": "general",
                    "template_type": "listicle",
                    "industry": "General",
                    "is_public": True,
                    "tags": ["listicle", "list", "tips", "recommendations"]
                }
            ]
            
            created_count = 0
            for template_data in default_templates:
                # Check if template already exists
                existing = self.db.query(ContentTemplate).filter(
                    ContentTemplate.name == template_data["name"]
                ).first()
                
                if not existing:
                    placeholders = self.extract_placeholders(template_data["template_content"])
                    
                    template = ContentTemplate(
                        name=template_data["name"],
                        description=template_data["description"],
                        template_content=template_data["template_content"],
                        category=template_data["category"],
                        template_type=template_data["template_type"],
                        industry=template_data["industry"],
                        is_public=template_data["is_public"],
                        tags=template_data["tags"],
                        placeholders=placeholders,
                        created_by=user_id,
                        usage_count=0
                    )
                    
                    self.db.add(template)
                    created_count += 1
            
            self.db.commit()
            logger.info(f"Seeded {created_count} default templates")
            return created_count
            
        except Exception as e:
            logger.error(f"Failed to seed default templates: {str(e)}")
            self.db.rollback()
            return 0
    
    def rate_template(self, template_id: str, user_id: str, rating: int, comment: Optional[str] = None) -> bool:
        """Rate a template"""
        try:
            # Check if user already rated this template
            existing_rating = self.db.query(TemplateRating).filter(
                and_(
                    TemplateRating.template_id == template_id,
                    TemplateRating.user_id == user_id
                )
            ).first()
            
            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating
                existing_rating.comment = comment
                existing_rating.updated_at = datetime.utcnow()
            else:
                # Create new rating
                new_rating = TemplateRating(
                    template_id=template_id,
                    user_id=user_id,
                    rating=rating,
                    comment=comment
                )
                self.db.add(new_rating)
            
            self.db.commit()
            logger.info(f"Template rated: {template_id} by user {user_id} - {rating} stars")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rate template: {str(e)}")
            self.db.rollback()
            return False