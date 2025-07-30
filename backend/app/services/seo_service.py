"""
SEO analysis service for content optimization
"""
import re
import json
from typing import Dict, List, Any, Optional
from collections import Counter
import math


class SEOAnalysisService:
    """Service for analyzing and optimizing content for SEO"""
    
    # Common stop words to exclude from keyword analysis
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
        'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with',
        'but', 'or', 'not', 'this', 'they', 'have', 'had', 'what', 'said', 'each', 'which',
        'their', 'time', 'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
        'her', 'would', 'make', 'like', 'into', 'him', 'two', 'more', 'go', 'no', 'way',
        'could', 'my', 'than', 'first', 'been', 'call', 'who', 'oil', 'sit', 'now', 'find',
        'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
    }
    
    def analyze_keyword_density(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword density in content"""
        # Clean and tokenize content
        clean_content = self._clean_text(content)
        words = clean_content.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return {"error": "No content to analyze"}
        
        keyword_analysis = {}
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Count exact matches
            exact_matches = clean_content.lower().count(keyword_lower)
            
            # Count word matches (for single words)
            word_matches = words.count(keyword_lower) if ' ' not in keyword_lower else exact_matches
            
            # Calculate density
            density = (exact_matches / total_words) * 100
            
            keyword_analysis[keyword] = {
                "exact_matches": exact_matches,
                "word_matches": word_matches,
                "density_percentage": round(density, 2),
                "optimal_range": "1-3%",
                "status": self._get_density_status(density)
            }
        
        # Analyze overall keyword distribution
        word_freq = Counter(word for word in words if word not in self.STOP_WORDS and len(word) > 2)
        top_words = dict(word_freq.most_common(10))
        
        return {
            "total_words": total_words,
            "keyword_analysis": keyword_analysis,
            "top_words": top_words,
            "recommendations": self._get_keyword_recommendations(keyword_analysis)
        }
    
    def calculate_readability_score(self, content: str) -> Dict[str, Any]:
        """Calculate Flesch-Kincaid readability scores"""
        # Clean text
        clean_content = self._clean_text(content)
        
        # Count sentences
        sentences = re.split(r'[.!?]+', clean_content)
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count == 0:
            return {"error": "No sentences found in content"}
        
        # Count words
        words = clean_content.split()
        word_count = len(words)
        
        if word_count == 0:
            return {"error": "No words found in content"}
        
        # Count syllables
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Calculate Flesch Reading Ease
        if sentence_count > 0 and word_count > 0:
            flesch_ease = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
        else:
            flesch_ease = 0
        
        # Calculate Flesch-Kincaid Grade Level
        if sentence_count > 0 and word_count > 0:
            flesch_grade = (0.39 * (word_count / sentence_count)) + (11.8 * (syllable_count / word_count)) - 15.59
        else:
            flesch_grade = 0
        
        return {
            "flesch_reading_ease": round(flesch_ease, 2),
            "flesch_kincaid_grade": round(flesch_grade, 2),
            "reading_level": self._get_reading_level(flesch_ease),
            "sentences": sentence_count,
            "words": word_count,
            "syllables": syllable_count,
            "avg_words_per_sentence": round(word_count / sentence_count, 2),
            "avg_syllables_per_word": round(syllable_count / word_count, 2),
            "recommendations": self._get_readability_recommendations(flesch_ease, flesch_grade)
        }
    
    def analyze_meta_description(self, meta_description: Optional[str], target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze meta description for SEO optimization"""
        if not meta_description:
            return {
                "status": "missing",
                "length": 0,
                "recommendations": ["Add a meta description to improve SEO"],
                "keyword_presence": {}
            }
        
        length = len(meta_description)
        keyword_presence = {}
        
        for keyword in target_keywords:
            keyword_presence[keyword] = keyword.lower() in meta_description.lower()
        
        recommendations = []
        
        # Length recommendations
        if length < 120:
            recommendations.append("Meta description is too short. Aim for 120-160 characters.")
        elif length > 160:
            recommendations.append("Meta description is too long. Keep it under 160 characters.")
        else:
            recommendations.append("Meta description length is optimal.")
        
        # Keyword recommendations
        missing_keywords = [k for k, present in keyword_presence.items() if not present]
        if missing_keywords:
            recommendations.append(f"Consider including these keywords: {', '.join(missing_keywords)}")
        
        return {
            "status": "present",
            "length": length,
            "optimal_length": "120-160 characters",
            "keyword_presence": keyword_presence,
            "recommendations": recommendations
        }
    
    def analyze_title_optimization(self, title: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze title for SEO optimization"""
        length = len(title)
        keyword_presence = {}
        
        for keyword in target_keywords:
            keyword_presence[keyword] = keyword.lower() in title.lower()
        
        recommendations = []
        
        # Length recommendations
        if length < 30:
            recommendations.append("Title is too short. Aim for 30-60 characters.")
        elif length > 60:
            recommendations.append("Title is too long. Keep it under 60 characters for better display.")
        else:
            recommendations.append("Title length is optimal.")
        
        # Keyword recommendations
        if not any(keyword_presence.values()):
            recommendations.append("Include at least one target keyword in the title.")
        
        # Position of first keyword
        first_keyword_position = None
        for keyword in target_keywords:
            pos = title.lower().find(keyword.lower())
            if pos != -1:
                if first_keyword_position is None or pos < first_keyword_position:
                    first_keyword_position = pos
        
        if first_keyword_position is not None and first_keyword_position > 30:
            recommendations.append("Consider moving keywords closer to the beginning of the title.")
        
        return {
            "length": length,
            "optimal_length": "30-60 characters",
            "keyword_presence": keyword_presence,
            "first_keyword_position": first_keyword_position,
            "recommendations": recommendations
        }
    
    def generate_seo_score(self, content: str, title: str, meta_description: Optional[str], 
                          target_keywords: List[str]) -> Dict[str, Any]:
        """Generate comprehensive SEO score and recommendations"""
        score = 0
        max_score = 100
        recommendations = []
        
        # Title analysis (25 points)
        title_analysis = self.analyze_title_optimization(title, target_keywords)
        title_score = 0
        if 30 <= title_analysis["length"] <= 60:
            title_score += 15
        elif title_analysis["length"] <= 70:
            title_score += 10
        
        if any(title_analysis["keyword_presence"].values()):
            title_score += 10
        
        score += title_score
        recommendations.extend(title_analysis["recommendations"])
        
        # Meta description analysis (20 points)
        meta_analysis = self.analyze_meta_description(meta_description, target_keywords)
        meta_score = 0
        if meta_analysis["status"] == "present":
            if 120 <= meta_analysis["length"] <= 160:
                meta_score += 15
            elif meta_analysis["length"] <= 180:
                meta_score += 10
            
            if any(meta_analysis["keyword_presence"].values()):
                meta_score += 5
        
        score += meta_score
        recommendations.extend(meta_analysis["recommendations"])
        
        # Content analysis (30 points)
        keyword_analysis = self.analyze_keyword_density(content, target_keywords)
        content_score = 0
        
        if "keyword_analysis" in keyword_analysis:
            optimal_keywords = sum(1 for k, data in keyword_analysis["keyword_analysis"].items() 
                                 if data["status"] == "optimal")
            content_score += min(20, optimal_keywords * 5)
        
        # Word count bonus
        word_count = keyword_analysis.get("total_words", 0)
        if word_count >= 300:
            content_score += 10
        elif word_count >= 200:
            content_score += 5
        
        score += content_score
        recommendations.extend(keyword_analysis.get("recommendations", []))
        
        # Readability analysis (25 points)
        readability = self.calculate_readability_score(content)
        readability_score = 0
        
        if "flesch_reading_ease" in readability:
            ease_score = readability["flesch_reading_ease"]
            if 60 <= ease_score <= 70:  # Standard reading level
                readability_score += 15
            elif 50 <= ease_score <= 80:
                readability_score += 10
            elif ease_score >= 30:
                readability_score += 5
            
            # Sentence length bonus
            avg_words = readability.get("avg_words_per_sentence", 0)
            if 15 <= avg_words <= 20:
                readability_score += 10
            elif 10 <= avg_words <= 25:
                readability_score += 5
        
        score += readability_score
        recommendations.extend(readability.get("recommendations", []))
        
        return {
            "seo_score": min(score, max_score),
            "max_score": max_score,
            "breakdown": {
                "title": title_score,
                "meta_description": meta_score,
                "content": content_score,
                "readability": readability_score
            },
            "recommendations": recommendations,
            "keyword_analysis": keyword_analysis,
            "readability": readability,
            "title_analysis": title_analysis,
            "meta_analysis": meta_analysis
        }
    
    def suggest_improvements(self, content: str, title: str, meta_description: Optional[str],
                           target_keywords: List[str]) -> List[str]:
        """Generate actionable SEO improvement suggestions"""
        seo_analysis = self.generate_seo_score(content, title, meta_description, target_keywords)
        
        suggestions = []
        
        # Priority suggestions based on score
        if seo_analysis["seo_score"] < 50:
            suggestions.append("🚨 Critical: Your content needs significant SEO improvements")
        elif seo_analysis["seo_score"] < 70:
            suggestions.append("⚠️ Warning: Your content has room for SEO improvements")
        else:
            suggestions.append("✅ Good: Your content is well-optimized for SEO")
        
        # Specific actionable suggestions
        breakdown = seo_analysis["breakdown"]
        
        if breakdown["title"] < 20:
            suggestions.append("📝 Optimize your title: Include target keywords and keep it 30-60 characters")
        
        if breakdown["meta_description"] < 15:
            suggestions.append("📄 Add/improve meta description: Write 120-160 characters with target keywords")
        
        if breakdown["content"] < 25:
            suggestions.append("📖 Improve content: Increase word count and optimize keyword density (1-3%)")
        
        if breakdown["readability"] < 20:
            suggestions.append("👥 Improve readability: Use shorter sentences and simpler words")
        
        return suggestions
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        return text.strip()
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)"""
        word = word.lower()
        if len(word) <= 3:
            return 1
        
        # Remove common endings
        word = re.sub(r'(es|ed|e)$', '', word)
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        return max(1, syllable_count)
    
    def _get_density_status(self, density: float) -> str:
        """Get keyword density status"""
        if density < 0.5:
            return "too_low"
        elif density > 3.0:
            return "too_high"
        elif 1.0 <= density <= 3.0:
            return "optimal"
        else:
            return "acceptable"
    
    def _get_reading_level(self, flesch_score: float) -> str:
        """Get reading level description from Flesch score"""
        if flesch_score >= 90:
            return "Very Easy (5th grade)"
        elif flesch_score >= 80:
            return "Easy (6th grade)"
        elif flesch_score >= 70:
            return "Fairly Easy (7th grade)"
        elif flesch_score >= 60:
            return "Standard (8th-9th grade)"
        elif flesch_score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif flesch_score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (Graduate level)"
    
    def _get_keyword_recommendations(self, keyword_analysis: Dict[str, Any]) -> List[str]:
        """Generate keyword optimization recommendations"""
        recommendations = []
        
        if "keyword_analysis" not in keyword_analysis:
            return recommendations
        
        for keyword, data in keyword_analysis["keyword_analysis"].items():
            status = data["status"]
            density = data["density_percentage"]
            
            if status == "too_low":
                recommendations.append(f"Increase usage of '{keyword}' (current: {density}%, target: 1-3%)")
            elif status == "too_high":
                recommendations.append(f"Reduce usage of '{keyword}' (current: {density}%, target: 1-3%)")
        
        return recommendations
    
    def _get_readability_recommendations(self, flesch_ease: float, flesch_grade: float) -> List[str]:
        """Generate readability improvement recommendations"""
        recommendations = []
        
        if flesch_ease < 30:
            recommendations.append("Content is very difficult to read. Use shorter sentences and simpler words.")
        elif flesch_ease < 50:
            recommendations.append("Content is fairly difficult. Consider simplifying complex sentences.")
        elif flesch_ease > 90:
            recommendations.append("Content might be too simple. Consider adding more detailed explanations.")
        
        if flesch_grade > 12:
            recommendations.append("Reading level is too high. Aim for 8th-10th grade level for better accessibility.")
        
        return recommendations