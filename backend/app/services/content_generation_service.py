"""
Content Generation Service
Handles AI-powered content generation using OpenAI GPT
"""

import openai
import os
from typing import Dict, Any, Optional
import json
import re
from datetime import datetime

class ContentGenerationService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
    def generate_content(self, 
                        title: str, 
                        content: str, 
                        tone: str = 'professional',
                        format_type: str = 'linkedin',
                        include_hashtags: bool = True,
                        include_seo: bool = True) -> Dict[str, Any]:
        """
        Generate content using AI based on input parameters
        """
        try:
            prompt = self._build_prompt(title, content, tone, format_type, include_hashtags, include_seo)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(format_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            generated_content = response.choices[0].message.content
            
            # Post-process the content
            processed_content = self._post_process_content(
                generated_content, 
                format_type, 
                include_hashtags, 
                include_seo
            )
            
            return {
                'success': True,
                'content': processed_content,
                'metadata': {
                    'word_count': len(processed_content.split()),
                    'character_count': len(processed_content),
                    'format': format_type,
                    'tone': tone,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None
            }
    
    def _get_system_prompt(self, format_type: str) -> str:
        """Get system prompt based on format type"""
        prompts = {
            'linkedin': """You are an expert LinkedIn content creator who specializes in technical and professional posts. 
            Create engaging, professional content that drives engagement and showcases expertise. 
            Use emojis strategically, include clear value propositions, and structure content for easy reading.""",
            
            'blog': """You are an expert technical blog writer who creates comprehensive, well-structured articles. 
            Focus on clear explanations, practical insights, and valuable takeaways for readers. 
            Use proper markdown formatting and maintain a professional yet accessible tone.""",
            
            'twitter': """You are an expert Twitter content creator who crafts engaging threads. 
            Break down complex topics into digestible tweets, use engaging hooks, and maintain consistency across the thread.""",
            
            'medium': """You are an expert Medium writer who creates in-depth, thoughtful articles. 
            Focus on storytelling, detailed explanations, and providing genuine value to readers."""
        }
        
        return prompts.get(format_type, prompts['linkedin'])
    
    def _build_prompt(self, title: str, content: str, tone: str, format_type: str, 
                     include_hashtags: bool, include_seo: bool) -> str:
        """Build the generation prompt"""
        
        prompt_parts = [
            f"Create a {format_type} post with the following specifications:",
            f"Title: {title}",
            f"Content/Notes: {content}",
            f"Tone: {tone}",
        ]
        
        if format_type == 'linkedin':
            prompt_parts.extend([
                "Requirements for LinkedIn:",
                "- Start with an engaging hook using emojis",
                "- Use bullet points or numbered lists for key points",
                "- Include a call-to-action at the end",
                "- Keep paragraphs short for mobile readability",
                "- Use strategic line breaks for visual appeal"
            ])
        elif format_type == 'blog':
            prompt_parts.extend([
                "Requirements for Blog:",
                "- Use proper markdown formatting with headers",
                "- Include an introduction and conclusion",
                "- Structure with clear sections",
                "- Provide detailed explanations and examples",
                "- Include practical takeaways"
            ])
        
        if include_hashtags:
            prompt_parts.append("- Include relevant hashtags at the end")
        
        if include_seo:
            prompt_parts.append("- Optimize for SEO with relevant keywords naturally integrated")
        
        return "\n".join(prompt_parts)
    
    def _post_process_content(self, content: str, format_type: str, 
                            include_hashtags: bool, include_seo: bool) -> str:
        """Post-process the generated content"""
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        # Add format-specific enhancements
        if format_type == 'linkedin':
            # Ensure proper LinkedIn formatting
            if not content.startswith(('🚀', '💡', '🔥', '✨', '🎯')):
                content = f"🚀 {content}"
        
        return content
    
    def generate_seo_metadata(self, content: str, title: str) -> Dict[str, str]:
        """Generate SEO metadata for the content"""
        try:
            prompt = f"""
            Generate SEO metadata for the following content:
            Title: {title}
            Content: {content[:500]}...
            
            Provide:
            1. Meta description (150-160 characters)
            2. 5-7 relevant keywords
            3. Suggested slug
            4. Open Graph title
            5. Open Graph description
            
            Format as JSON.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Generate accurate, relevant SEO metadata."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse JSON response
            metadata_text = response.choices[0].message.content
            try:
                metadata = json.loads(metadata_text)
                return metadata
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'meta_description': title[:150],
                    'keywords': ['AI', 'blog', 'automation', 'content'],
                    'slug': title.lower().replace(' ', '-')[:50],
                    'og_title': title,
                    'og_description': title[:150]
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'meta_description': title[:150],
                'keywords': ['AI', 'blog', 'automation'],
                'slug': title.lower().replace(' ', '-')[:50]
            }
    
    def suggest_improvements(self, content: str) -> Dict[str, Any]:
        """Suggest improvements for the generated content"""
        try:
            prompt = f"""
            Analyze the following content and suggest improvements:
            
            {content}
            
            Provide suggestions for:
            1. Engagement (hooks, CTAs)
            2. Structure (formatting, flow)
            3. SEO (keywords, readability)
            4. Platform optimization
            5. Overall impact
            
            Be specific and actionable.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content
            
            return {
                'success': True,
                'suggestions': suggestions,
                'analysis': {
                    'word_count': len(content.split()),
                    'readability_score': self._calculate_readability(content),
                    'engagement_elements': self._count_engagement_elements(content)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_readability(self, content: str) -> float:
        """Simple readability score calculation"""
        words = content.split()
        sentences = content.split('.')
        
        if len(sentences) == 0:
            return 0.0
            
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Simple score: lower is better (easier to read)
        score = min(100, max(0, 100 - (avg_words_per_sentence * 2)))
        return round(score, 1)
    
    def _count_engagement_elements(self, content: str) -> Dict[str, int]:
        """Count engagement elements in content"""
        return {
            'emojis': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)),
            'hashtags': len(re.findall(r'#\w+', content)),
            'questions': len(re.findall(r'\?', content)),
            'bullet_points': len(re.findall(r'[•\-\*]\s', content)),
            'call_to_actions': len(re.findall(r'(let\'s|connect|share|comment|like|follow)', content, re.IGNORECASE))
        }

# Example usage and templates
CONTENT_TEMPLATES = {
    'project_showcase': {
        'title': '🚀 {project_name}: {brief_description}',
        'structure': [
            'Hook with project announcement',
            'Problem it solves',
            'Key features/capabilities',
            'Tech stack',
            'Results/impact',
            'Call to action'
        ]
    },
    'technical_tutorial': {
        'title': 'Understanding {topic}: A Developer\'s Guide',
        'structure': [
            'Introduction to the problem',
            'Core concepts explained',
            'Step-by-step implementation',
            'Best practices',
            'Common pitfalls',
            'Conclusion and resources'
        ]
    },
    'weekly_insights': {
        'title': 'This Week in {field}: Key Insights',
        'structure': [
            'Week overview',
            'Top discoveries/learnings',
            'Interesting resources found',
            'Industry trends observed',
            'Personal takeaways',
            'What\'s next'
        ]
    }
}