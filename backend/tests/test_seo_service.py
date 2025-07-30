"""
Unit tests for SEO analysis service
"""
import pytest
from app.services.seo_service import SEOAnalysisService


class TestSEOAnalysisService:
    """Test SEO analysis service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.seo_service = SEOAnalysisService()
        
        # Sample content for testing
        self.sample_content = """
        This is a comprehensive guide about SEO optimization for blog posts. 
        SEO is crucial for improving your website's visibility in search engines.
        When you optimize your content for SEO, you increase the chances of ranking higher.
        
        Key SEO factors include keyword density, readability, and meta descriptions.
        The best SEO practices involve using keywords naturally throughout your content.
        Remember that SEO is not just about keywords, but also about providing value to readers.
        
        In conclusion, effective SEO requires a balance between optimization and readability.
        """
        
        self.sample_title = "Complete Guide to SEO Optimization for Blog Posts"
        self.sample_meta = "Learn essential SEO optimization techniques for blog posts to improve search rankings and visibility."
        self.target_keywords = ["SEO", "optimization", "blog posts"]
    
    def test_keyword_density_analysis(self):
        """Test keyword density analysis"""
        result = self.seo_service.analyze_keyword_density(
            self.sample_content, 
            self.target_keywords
        )
        
        assert "total_words" in result
        assert "keyword_analysis" in result
        assert "top_words" in result
        assert "recommendations" in result
        
        # Check keyword analysis structure
        for keyword in self.target_keywords:
            assert keyword in result["keyword_analysis"]
            keyword_data = result["keyword_analysis"][keyword]
            assert "exact_matches" in keyword_data
            assert "density_percentage" in keyword_data
            assert "status" in keyword_data
            assert keyword_data["density_percentage"] >= 0
    
    def test_readability_score_calculation(self):
        """Test Flesch-Kincaid readability score calculation"""
        result = self.seo_service.calculate_readability_score(self.sample_content)
        
        assert "flesch_reading_ease" in result
        assert "flesch_kincaid_grade" in result
        assert "reading_level" in result
        assert "sentences" in result
        assert "words" in result
        assert "syllables" in result
        assert "avg_words_per_sentence" in result
        assert "avg_syllables_per_word" in result
        assert "recommendations" in result
        
        # Check score ranges
        assert isinstance(result["flesch_reading_ease"], float)
        assert isinstance(result["flesch_kincaid_grade"], float)
        assert result["sentences"] > 0
        assert result["words"] > 0
        assert result["syllables"] > 0
    
    def test_meta_description_analysis(self):
        """Test meta description analysis"""
        # Test with valid meta description
        result = self.seo_service.analyze_meta_description(
            self.sample_meta, 
            self.target_keywords
        )
        
        assert result["status"] == "present"
        assert "length" in result
        assert "keyword_presence" in result
        assert "recommendations" in result
        
        # Check keyword presence
        for keyword in self.target_keywords:
            assert keyword in result["keyword_presence"]
            assert isinstance(result["keyword_presence"][keyword], bool)
        
        # Test with missing meta description
        result_missing = self.seo_service.analyze_meta_description(None, self.target_keywords)
        assert result_missing["status"] == "missing"
        assert result_missing["length"] == 0
    
    def test_title_optimization_analysis(self):
        """Test title optimization analysis"""
        result = self.seo_service.analyze_title_optimization(
            self.sample_title, 
            self.target_keywords
        )
        
        assert "length" in result
        assert "keyword_presence" in result
        assert "recommendations" in result
        assert result["length"] == len(self.sample_title)
        
        # Check keyword presence
        for keyword in self.target_keywords:
            assert keyword in result["keyword_presence"]
    
    def test_comprehensive_seo_score(self):
        """Test comprehensive SEO score generation"""
        result = self.seo_service.generate_seo_score(
            content=self.sample_content,
            title=self.sample_title,
            meta_description=self.sample_meta,
            target_keywords=self.target_keywords
        )
        
        assert "seo_score" in result
        assert "max_score" in result
        assert "breakdown" in result
        assert "recommendations" in result
        assert "keyword_analysis" in result
        assert "readability" in result
        assert "title_analysis" in result
        assert "meta_analysis" in result
        
        # Check score range
        assert 0 <= result["seo_score"] <= result["max_score"]
        assert result["max_score"] == 100
        
        # Check breakdown structure
        breakdown = result["breakdown"]
        assert "title" in breakdown
        assert "meta_description" in breakdown
        assert "content" in breakdown
        assert "readability" in breakdown
        
        # All breakdown scores should be non-negative
        for score in breakdown.values():
            assert score >= 0
    
    def test_improvement_suggestions(self):
        """Test SEO improvement suggestions"""
        suggestions = self.seo_service.suggest_improvements(
            content=self.sample_content,
            title=self.sample_title,
            meta_description=self.sample_meta,
            target_keywords=self.target_keywords
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # Check that suggestions are strings
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0
    
    def test_keyword_density_edge_cases(self):
        """Test keyword density analysis with edge cases"""
        # Empty content
        result_empty = self.seo_service.analyze_keyword_density("", ["test"])
        assert "error" in result_empty
        
        # Single word content
        result_single = self.seo_service.analyze_keyword_density("test", ["test"])
        assert "keyword_analysis" in result_single
        assert result_single["total_words"] == 1
        
        # No keywords
        result_no_keywords = self.seo_service.analyze_keyword_density(
            self.sample_content, 
            []
        )
        assert result_no_keywords["keyword_analysis"] == {}
    
    def test_readability_edge_cases(self):
        """Test readability calculation with edge cases"""
        # Empty content
        result_empty = self.seo_service.calculate_readability_score("")
        assert "error" in result_empty
        
        # Single sentence
        result_single = self.seo_service.calculate_readability_score("This is a test.")
        assert "flesch_reading_ease" in result_single
        assert result_single["sentences"] == 1
        
        # Very short content
        result_short = self.seo_service.calculate_readability_score("Test.")
        assert "words" in result_short
        assert result_short["words"] == 1
    
    def test_syllable_counting(self):
        """Test syllable counting algorithm"""
        # Test various words
        test_cases = [
            ("hello", 2),
            ("world", 1),
            ("beautiful", 3),
            ("optimization", 5),
            ("a", 1),
            ("the", 1),
            ("", 1)  # Minimum syllable count
        ]
        
        for word, expected_min in test_cases:
            syllables = self.seo_service._count_syllables(word)
            assert syllables >= 1  # Minimum syllable count
            if word:  # Non-empty words
                assert syllables >= expected_min or syllables == 1
    
    def test_density_status_classification(self):
        """Test keyword density status classification"""
        test_cases = [
            (0.3, "too_low"),
            (1.5, "optimal"),
            (2.5, "optimal"),
            (4.0, "too_high"),
            (0.8, "acceptable")
        ]
        
        for density, expected_status in test_cases:
            status = self.seo_service._get_density_status(density)
            assert status == expected_status
    
    def test_reading_level_classification(self):
        """Test reading level classification"""
        test_cases = [
            (95, "Very Easy (5th grade)"),
            (85, "Easy (6th grade)"),
            (75, "Fairly Easy (7th grade)"),
            (65, "Standard (8th-9th grade)"),
            (55, "Fairly Difficult (10th-12th grade)"),
            (35, "Difficult (College level)"),
            (20, "Very Difficult (Graduate level)")
        ]
        
        for score, expected_level in test_cases:
            level = self.seo_service._get_reading_level(score)
            assert level == expected_level
    
    def test_text_cleaning(self):
        """Test text cleaning functionality"""
        dirty_text = """
        <p>This is <strong>HTML</strong> content with   extra   spaces.</p>
        <div>It has special characters: @#$%^&*()!</div>
        """
        
        clean_text = self.seo_service._clean_text(dirty_text)
        
        # Should remove HTML tags
        assert "<p>" not in clean_text
        assert "<strong>" not in clean_text
        assert "<div>" not in clean_text
        
        # Should normalize whitespace
        assert "   " not in clean_text
        
        # Should preserve basic punctuation
        assert "." in clean_text
        assert "!" in clean_text
    
    def test_keyword_recommendations(self):
        """Test keyword optimization recommendations"""
        # Test with various keyword densities
        keyword_analysis = {
            "keyword_analysis": {
                "SEO": {"status": "too_low", "density_percentage": 0.3},
                "optimization": {"status": "optimal", "density_percentage": 2.0},
                "content": {"status": "too_high", "density_percentage": 4.5}
            }
        }
        
        recommendations = self.seo_service._get_keyword_recommendations(keyword_analysis)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 2  # Should have recommendations for too_low and too_high
        
        # Check recommendation content
        rec_text = " ".join(recommendations)
        assert "SEO" in rec_text
        assert "content" in rec_text
        assert "Increase" in rec_text or "Reduce" in rec_text
    
    def test_readability_recommendations(self):
        """Test readability improvement recommendations"""
        # Test with difficult content
        difficult_recommendations = self.seo_service._get_readability_recommendations(25, 15)
        assert len(difficult_recommendations) > 0
        assert any("difficult" in rec.lower() for rec in difficult_recommendations)
        
        # Test with very easy content
        easy_recommendations = self.seo_service._get_readability_recommendations(95, 3)
        assert len(easy_recommendations) > 0
        assert any("simple" in rec.lower() for rec in easy_recommendations)
        
        # Test with optimal content
        optimal_recommendations = self.seo_service._get_readability_recommendations(65, 8)
        # Should have fewer or no recommendations for optimal content
        assert len(optimal_recommendations) <= 1
    
    def test_comprehensive_analysis_integration(self):
        """Test integration of all SEO analysis components"""
        # Test with content that should score well
        good_content = """
        SEO optimization is essential for blog success. When you optimize your content for SEO, 
        you improve search rankings. This guide covers SEO best practices for blog posts.
        
        First, focus on keyword optimization. Use your target keywords naturally in the content.
        Second, ensure good readability. Write clear, concise sentences that are easy to read.
        Third, create compelling meta descriptions that include your keywords.
        
        Remember, good SEO balances optimization with user experience. Your content should 
        provide value to readers while being discoverable by search engines.
        """
        
        good_title = "SEO Optimization Guide for Blog Posts"
        good_meta = "Learn SEO optimization techniques to improve your blog post rankings and visibility in search engines."
        
        result = self.seo_service.generate_seo_score(
            content=good_content,
            title=good_title,
            meta_description=good_meta,
            target_keywords=["SEO", "optimization", "blog"]
        )
        
        # Should get a decent SEO score
        assert result["seo_score"] >= 50  # Should be at least moderate
        
        # Should have analysis for all components
        assert result["keyword_analysis"]["total_words"] > 0
        assert result["readability"]["words"] > 0
        assert result["title_analysis"]["length"] > 0
        assert result["meta_analysis"]["status"] == "present"
        
        # Recommendations should be helpful
        assert len(result["recommendations"]) > 0
    
    def test_performance_with_large_content(self):
        """Test performance with large content"""
        # Create large content (simulate a long blog post)
        large_content = self.sample_content * 50  # Repeat content 50 times
        
        result = self.seo_service.generate_seo_score(
            content=large_content,
            title=self.sample_title,
            meta_description=self.sample_meta,
            target_keywords=self.target_keywords
        )
        
        # Should still work with large content
        assert "seo_score" in result
        assert result["keyword_analysis"]["total_words"] > 1000
        assert result["readability"]["words"] > 1000

if __name__ == "__main__":
    pytest.main([__file__])