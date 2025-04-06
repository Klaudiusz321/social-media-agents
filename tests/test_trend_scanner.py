"""
Tests for the TrendScannerAgent module.

Run with: pytest -v tests/test_trend_scanner.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path to allow importing the agents package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trend_scanner import (
    TrendScannerAgent, 
    TwitterScanner, 
    InstagramScanner, 
    LinkedInScanner,
    CacheManager
)

class TestTrendScannerAgent(unittest.TestCase):
    """Test cases for the TrendScannerAgent."""
    
    def setUp(self):
        """Set up for tests."""
        # Create mock scanners
        self.mock_twitter = MagicMock()
        self.mock_instagram = MagicMock()
        self.mock_linkedin = MagicMock()
        self.mock_cache = MagicMock()
        
        # Sample trend data
        self.twitter_trends = {
            "trending_hashtags": [
                {"name": "space", "tweet_volume": 10000, "relevance_score": 1.0},
                {"name": "blackhole", "tweet_volume": 5000, "relevance_score": 0.9}
            ],
            "popular_formats": [
                {"name": "Thread", "description": "explaining complex topics"}
            ]
        }
        
        self.instagram_trends = {
            "trending_hashtags": [
                {"name": "astrophotography", "post_count": 500, "relevance_score": 1.0}
            ],
            "popular_formats": [
                {"name": "Carousel", "description": "multi-image posts explaining scientific concepts"}
            ]
        }
        
        self.linkedin_trends = {
            "trending_topics": [
                {"name": "Space Technology", "relevance_score": 1.0},
                {"name": "James Webb Space Telescope", "relevance_score": 0.9}
            ],
            "popular_formats": [
                {"name": "Text post with stats", "description": "highlighting key research findings"}
            ]
        }
        
        # Configure mock returns
        self.mock_twitter.get_trending_topics.return_value = self.twitter_trends
        self.mock_instagram.get_trending_hashtags.return_value = self.instagram_trends
        self.mock_linkedin.get_trending_topics.return_value = self.linkedin_trends
        self.mock_cache.get_cached_trends.return_value = None
    
    @patch('agents.trend_scanner.agent.TwitterScanner')
    @patch('agents.trend_scanner.agent.InstagramScanner')
    @patch('agents.trend_scanner.agent.LinkedInScanner')
    @patch('agents.trend_scanner.agent.CacheManager')
    def test_scan_all_platforms(self, mock_cache_cls, mock_linkedin_cls, 
                               mock_instagram_cls, mock_twitter_cls):
        """Test scanning all platforms."""
        # Configure mocks
        mock_twitter_cls.return_value = self.mock_twitter
        mock_instagram_cls.return_value = self.mock_instagram
        mock_linkedin_cls.return_value = self.mock_linkedin
        mock_cache_cls.return_value = self.mock_cache
        
        # Create agent instance
        agent = TrendScannerAgent()
        
        # Call the method to test
        result = agent.scan_all_platforms()
        
        # Verify the scanners were called
        self.mock_twitter.get_trending_topics.assert_called_once()
        self.mock_instagram.get_trending_hashtags.assert_called_once()
        self.mock_linkedin.get_trending_topics.assert_called_once()
        
        # Verify expected keys in result
        self.assertIn("twitter", result)
        self.assertIn("instagram", result)
        self.assertIn("linkedin", result)
        
        # Verify cache was updated
        self.mock_cache.cache_trends.assert_called_once()
    
    @patch('agents.trend_scanner.agent.TwitterScanner')
    @patch('agents.trend_scanner.agent.InstagramScanner')
    @patch('agents.trend_scanner.agent.LinkedInScanner')
    @patch('agents.trend_scanner.agent.CacheManager')
    def test_generate_trend_report(self, mock_cache_cls, mock_linkedin_cls, 
                                  mock_instagram_cls, mock_twitter_cls):
        """Test generating a trend report."""
        # Configure mocks
        mock_twitter_cls.return_value = self.mock_twitter
        mock_instagram_cls.return_value = self.mock_instagram
        mock_linkedin_cls.return_value = self.mock_linkedin
        mock_cache_cls.return_value = self.mock_cache
        
        # Create agent instance
        agent = TrendScannerAgent()
        
        # Call the method to test
        report = agent.generate_trend_report()
        
        # Verify report structure
        self.assertIn("Trend Report -", report)
        
        # Verify platform markers are present
        self.assertIn("**Twitter:**", report)
        self.assertIn("**Instagram:**", report)
        self.assertIn("**LinkedIn:**", report)
        
        # Verify expected content formats
        self.assertIn("`#space`", report.lower())
        self.assertIn("`#astrophotography`", report.lower())
        self.assertIn("Space Technology", report)
        
        # Verify engagement metrics
        self.assertIn("k+ tweets", report)
        
        # Verify content format details
        self.assertIn("thread", report.lower())
        self.assertIn("carousel", report.lower())
        
        # Verify the disclaimer about relevant content
        self.assertIn("focuses on trends relevant to astronomy", report)

class TestTwitterScanner(unittest.TestCase):
    """Test cases for the TwitterScanner."""
    
    def setUp(self):
        """Set up for tests."""
        self.relevant_topics = ["astronomy", "space", "physics"]
    
    def test_initialization(self):
        """Test proper initialization of the scanner."""
        scanner = TwitterScanner(self.relevant_topics)
        
        # Verify relevant topics are stored and converted to lowercase
        self.assertEqual(len(scanner.relevant_topics), len(self.relevant_topics))
        self.assertTrue(all(topic.lower() == topic for topic in scanner.relevant_topics))
        
        # Verify default WOEID is worldwide (1)
        self.assertEqual(scanner.woeid, 1)
    
    def test_calculate_relevance(self):
        """Test relevance calculation logic."""
        scanner = TwitterScanner(self.relevant_topics)
        
        # Direct match should have highest relevance
        self.assertEqual(scanner._calculate_relevance("Latest Space News"), 1.0)
        
        # Partial match should have medium relevance
        self.assertEqual(scanner._calculate_relevance("spacecraft launch"), 0.5)
        
        # Unrelated should have lowest relevance
        self.assertLess(scanner._calculate_relevance("politics today"), 0.5)

if __name__ == '__main__':
    unittest.main() 