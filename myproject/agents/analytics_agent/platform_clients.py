"""
Platform Clients - Clients for connecting to various social media platforms
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import json

logger = logging.getLogger(__name__)

class BaseClient:
    """Base class for platform clients"""
    
    def __init__(self, platform_name: str):
        """Initialize the base client"""
        self.platform_name = platform_name
        logger.info(f"Initialized {platform_name} client")
    
    async def get_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Get metrics for the platform"""
        raise NotImplementedError("Subclasses must implement get_metrics")
    
    async def get_audience_data(self, include_demographics: bool = True) -> Dict[str, Any]:
        """Get audience data for the platform"""
        raise NotImplementedError("Subclasses must implement get_audience_data")
    
    async def get_content_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get content performance data for the platform"""
        raise NotImplementedError("Subclasses must implement get_content_performance")

class InstagramClient(BaseClient):
    """Client for connecting to Instagram's API"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the Instagram client"""
        super().__init__("instagram")
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def get_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Get metrics from Instagram"""
        # Mock implementation
        return self._generate_mock_metrics(start_date, end_date, metrics)
    
    async def get_audience_data(self, include_demographics: bool = True) -> Dict[str, Any]:
        """Get audience data from Instagram"""
        # Mock implementation
        audience_data = {
            "total_followers": random.randint(5000, 50000),
            "follower_growth_rate": random.uniform(0.5, 5.0),
            "engagement_rate": random.uniform(1.0, 8.0)
        }
        
        if include_demographics:
            audience_data["demographics"] = {
                "age_distribution": {
                    "13-17": random.uniform(5, 15),
                    "18-24": random.uniform(20, 40),
                    "25-34": random.uniform(25, 45),
                    "35-44": random.uniform(10, 25),
                    "45-54": random.uniform(5, 15),
                    "55+": random.uniform(1, 10)
                },
                "gender_distribution": {
                    "male": random.uniform(30, 70),
                    "female": random.uniform(30, 70)
                },
                "top_locations": {
                    "United States": random.uniform(20, 45),
                    "United Kingdom": random.uniform(5, 15),
                    "Canada": random.uniform(3, 10),
                    "Australia": random.uniform(2, 8),
                    "Germany": random.uniform(2, 7)
                }
            }
        
        return audience_data
    
    async def get_content_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get content performance data from Instagram"""
        # Mock implementation
        return {
            "top_posts": [
                {
                    "id": f"post_{i}",
                    "type": random.choice(["image", "video", "carousel"]),
                    "engagement_rate": random.uniform(1.0, 15.0),
                    "likes": random.randint(500, 5000),
                    "comments": random.randint(10, 500),
                    "shares": random.randint(5, 200),
                    "impressions": random.randint(1000, 50000),
                    "posted_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }
                for i in range(1, 6)  # Top 5 posts
            ]
        }
    
    def _generate_mock_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Generate mock metrics for Instagram"""
        summary_metrics = {
            "impressions": random.randint(50000, 500000),
            "reach": random.randint(30000, 300000),
            "followers": random.randint(5000, 50000),
            "likes": random.randint(10000, 100000),
            "comments": random.randint(1000, 10000),
            "shares": random.randint(500, 5000),
            "saves": random.randint(300, 3000),
            "profile_visits": random.randint(2000, 20000),
            "clicks": random.randint(1500, 15000),
            "engagement_rate": random.uniform(1.0, 8.0)
        }
        
        # Filter to only requested metrics
        if metrics:
            summary_metrics = {k: v for k, v in summary_metrics.items() if k in metrics}
        
        # Generate daily metrics
        daily_metrics = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = {
                "date": current_date.isoformat(),
                "metrics": {}
            }
            
            for metric in summary_metrics.keys():
                # Generate a value that's roughly proportional to the summary metric
                # but with some randomness to create realistic patterns
                base_value = summary_metrics[metric]
                if isinstance(base_value, float):
                    daily_value = base_value * random.uniform(0.5, 1.5)
                    daily_data["metrics"][metric] = round(daily_value, 2)
                else:
                    # For integer metrics, scale by days in range
                    days_in_range = (end_date - start_date).days + 1
                    avg_daily = base_value / days_in_range
                    daily_value = int(avg_daily * random.uniform(0.5, 1.5))
                    daily_data["metrics"][metric] = daily_value
            
            daily_metrics.append(daily_data)
            current_date += timedelta(days=1)
        
        return {
            "summary_metrics": summary_metrics,
            "daily_metrics": daily_metrics
        }

class TwitterClient(BaseClient):
    """Client for connecting to Twitter's API"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, 
                 access_token: Optional[str] = None, access_token_secret: Optional[str] = None):
        """Initialize the Twitter client"""
        super().__init__("twitter")
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
    
    async def get_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Get metrics from Twitter"""
        # Mock implementation
        return self._generate_mock_metrics(start_date, end_date, metrics)
    
    async def get_audience_data(self, include_demographics: bool = True) -> Dict[str, Any]:
        """Get audience data from Twitter"""
        # Mock implementation
        audience_data = {
            "total_followers": random.randint(8000, 80000),
            "follower_growth_rate": random.uniform(0.3, 4.0),
            "engagement_rate": random.uniform(0.8, 5.0)
        }
        
        if include_demographics:
            audience_data["demographics"] = {
                "age_distribution": {
                    "13-17": random.uniform(3, 10),
                    "18-24": random.uniform(15, 35),
                    "25-34": random.uniform(30, 45),
                    "35-44": random.uniform(15, 30),
                    "45-54": random.uniform(5, 20),
                    "55+": random.uniform(2, 15)
                },
                "gender_distribution": {
                    "male": random.uniform(40, 65),
                    "female": random.uniform(35, 60)
                },
                "top_locations": {
                    "United States": random.uniform(25, 50),
                    "United Kingdom": random.uniform(6, 18),
                    "Japan": random.uniform(4, 12),
                    "Brazil": random.uniform(3, 10),
                    "India": random.uniform(5, 15)
                }
            }
        
        return audience_data
    
    async def get_content_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get content performance data from Twitter"""
        # Mock implementation
        return {
            "top_tweets": [
                {
                    "id": f"tweet_{i}",
                    "type": random.choice(["text", "image", "video", "link"]),
                    "engagement_rate": random.uniform(0.5, 10.0),
                    "likes": random.randint(300, 3000),
                    "retweets": random.randint(50, 1000),
                    "replies": random.randint(10, 300),
                    "impressions": random.randint(2000, 100000),
                    "posted_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }
                for i in range(1, 6)  # Top 5 tweets
            ]
        }
    
    def _generate_mock_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Generate mock metrics for Twitter"""
        summary_metrics = {
            "impressions": random.randint(80000, 800000),
            "reach": random.randint(50000, 500000),
            "followers": random.randint(8000, 80000),
            "likes": random.randint(15000, 150000),
            "retweets": random.randint(3000, 30000),
            "replies": random.randint(1000, 10000),
            "profile_visits": random.randint(3000, 30000),
            "clicks": random.randint(2000, 20000),
            "engagement_rate": random.uniform(0.8, 5.0)
        }
        
        # Filter to only requested metrics
        if metrics:
            summary_metrics = {k: v for k, v in summary_metrics.items() if k in metrics}
        
        # Generate daily metrics
        daily_metrics = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = {
                "date": current_date.isoformat(),
                "metrics": {}
            }
            
            for metric in summary_metrics.keys():
                # Generate a value with realistic patterns
                base_value = summary_metrics[metric]
                if isinstance(base_value, float):
                    daily_value = base_value * random.uniform(0.5, 1.5)
                    daily_data["metrics"][metric] = round(daily_value, 2)
                else:
                    days_in_range = (end_date - start_date).days + 1
                    avg_daily = base_value / days_in_range
                    daily_value = int(avg_daily * random.uniform(0.5, 1.5))
                    daily_data["metrics"][metric] = daily_value
            
            daily_metrics.append(daily_data)
            current_date += timedelta(days=1)
        
        return {
            "summary_metrics": summary_metrics,
            "daily_metrics": daily_metrics
        }

class LinkedInClient(BaseClient):
    """Client for connecting to LinkedIn's API"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the LinkedIn client"""
        super().__init__("linkedin")
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def get_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Get metrics from LinkedIn"""
        # Mock implementation
        return self._generate_mock_metrics(start_date, end_date, metrics)
    
    async def get_audience_data(self, include_demographics: bool = True) -> Dict[str, Any]:
        """Get audience data from LinkedIn"""
        # Mock implementation
        audience_data = {
            "total_followers": random.randint(3000, 30000),
            "follower_growth_rate": random.uniform(0.2, 3.0),
            "engagement_rate": random.uniform(0.5, 4.0)
        }
        
        if include_demographics:
            audience_data["demographics"] = {
                "industry_distribution": {
                    "Technology": random.uniform(20, 40),
                    "Marketing": random.uniform(10, 25),
                    "Finance": random.uniform(5, 20),
                    "Healthcare": random.uniform(5, 15),
                    "Education": random.uniform(3, 12)
                },
                "job_level_distribution": {
                    "Entry": random.uniform(10, 25),
                    "Senior": random.uniform(30, 50),
                    "Manager": random.uniform(15, 30),
                    "Director": random.uniform(5, 15),
                    "Executive": random.uniform(2, 10)
                },
                "company_size_distribution": {
                    "1-10": random.uniform(5, 15),
                    "11-50": random.uniform(10, 25),
                    "51-200": random.uniform(15, 30),
                    "201-1000": random.uniform(20, 35),
                    "1001+": random.uniform(10, 30)
                }
            }
        
        return audience_data
    
    async def get_content_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get content performance data from LinkedIn"""
        # Mock implementation
        return {
            "top_posts": [
                {
                    "id": f"post_{i}",
                    "type": random.choice(["article", "image", "video", "document"]),
                    "engagement_rate": random.uniform(0.5, 8.0),
                    "likes": random.randint(200, 2000),
                    "comments": random.randint(10, 200),
                    "shares": random.randint(5, 100),
                    "clicks": random.randint(50, 1000),
                    "impressions": random.randint(1000, 20000),
                    "posted_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }
                for i in range(1, 6)  # Top 5 posts
            ]
        }
    
    def _generate_mock_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Generate mock metrics for LinkedIn"""
        summary_metrics = {
            "impressions": random.randint(30000, 300000),
            "reach": random.randint(20000, 200000),
            "followers": random.randint(3000, 30000),
            "likes": random.randint(5000, 50000),
            "comments": random.randint(500, 5000),
            "shares": random.randint(200, 2000),
            "profile_views": random.randint(1000, 10000),
            "clicks": random.randint(2000, 20000),
            "engagement_rate": random.uniform(0.5, 4.0)
        }
        
        # Filter to only requested metrics
        if metrics:
            summary_metrics = {k: v for k, v in summary_metrics.items() if k in metrics}
        
        # Generate daily metrics
        daily_metrics = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = {
                "date": current_date.isoformat(),
                "metrics": {}
            }
            
            for metric in summary_metrics.keys():
                # Generate a value with realistic patterns
                base_value = summary_metrics[metric]
                if isinstance(base_value, float):
                    daily_value = base_value * random.uniform(0.5, 1.5)
                    daily_data["metrics"][metric] = round(daily_value, 2)
                else:
                    days_in_range = (end_date - start_date).days + 1
                    avg_daily = base_value / days_in_range
                    daily_value = int(avg_daily * random.uniform(0.5, 1.5))
                    daily_data["metrics"][metric] = daily_value
            
            daily_metrics.append(daily_data)
            current_date += timedelta(days=1)
        
        return {
            "summary_metrics": summary_metrics,
            "daily_metrics": daily_metrics
        }

class MockClient(BaseClient):
    """Mock client for testing purposes"""
    
    def __init__(self, platform_name: str):
        """Initialize the mock client"""
        super().__init__(platform_name)
    
    async def get_metrics(self, start_date: datetime, end_date: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Get mock metrics"""
        summary_metrics = {
            "impressions": random.randint(10000, 100000),
            "reach": random.randint(7000, 70000),
            "followers": random.randint(1000, 10000),
            "likes": random.randint(2000, 20000),
            "comments": random.randint(200, 2000),
            "shares": random.randint(100, 1000),
            "profile_visits": random.randint(500, 5000),
            "clicks": random.randint(300, 3000),
            "engagement_rate": random.uniform(0.5, 6.0)
        }
        
        # Filter to only requested metrics
        if metrics:
            summary_metrics = {k: v for k, v in summary_metrics.items() if k in metrics}
        
        # Generate daily metrics
        daily_metrics = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = {
                "date": current_date.isoformat(),
                "metrics": {}
            }
            
            for metric in summary_metrics.keys():
                # Generate a value with realistic patterns
                base_value = summary_metrics[metric]
                if isinstance(base_value, float):
                    daily_value = base_value * random.uniform(0.5, 1.5)
                    daily_data["metrics"][metric] = round(daily_value, 2)
                else:
                    days_in_range = (end_date - start_date).days + 1
                    avg_daily = base_value / days_in_range
                    daily_value = int(avg_daily * random.uniform(0.5, 1.5))
                    daily_data["metrics"][metric] = daily_value
            
            daily_metrics.append(daily_data)
            current_date += timedelta(days=1)
        
        return {
            "summary_metrics": summary_metrics,
            "daily_metrics": daily_metrics
        }
    
    async def get_audience_data(self, include_demographics: bool = True) -> Dict[str, Any]:
        """Get mock audience data"""
        audience_data = {
            "total_followers": random.randint(1000, 10000),
            "follower_growth_rate": random.uniform(0.1, 3.0),
            "engagement_rate": random.uniform(0.3, 5.0)
        }
        
        if include_demographics:
            audience_data["demographics"] = {
                "age_distribution": {
                    "13-17": random.uniform(5, 10),
                    "18-24": random.uniform(20, 30),
                    "25-34": random.uniform(30, 40),
                    "35-44": random.uniform(10, 20),
                    "45-54": random.uniform(5, 10),
                    "55+": random.uniform(1, 5)
                },
                "gender_distribution": {
                    "male": random.uniform(40, 60),
                    "female": random.uniform(40, 60)
                },
                "top_locations": {
                    "United States": random.uniform(30, 50),
                    "United Kingdom": random.uniform(5, 15),
                    "Canada": random.uniform(5, 10),
                    "Australia": random.uniform(3, 8),
                    "Germany": random.uniform(2, 7)
                }
            }
        
        return audience_data
    
    async def get_content_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get mock content performance data"""
        return {
            "top_posts": [
                {
                    "id": f"post_{i}",
                    "type": random.choice(["text", "image", "video"]),
                    "engagement_rate": random.uniform(0.5, 8.0),
                    "likes": random.randint(100, 1000),
                    "comments": random.randint(10, 100),
                    "shares": random.randint(5, 50),
                    "impressions": random.randint(500, 5000),
                    "posted_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }
                for i in range(1, 6)  # Top 5 posts
            ]
        } 