"""
Twitter Scanner - Module for scanning Twitter/X for trending topics and content formats.

Uses Twitter API v1.1 endpoint GET trends/place.json to retrieve worldwide trends
and analyze their relevance to our topics of interest.
"""

import logging
import tweepy
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

logger = logging.getLogger("TwitterScanner")

class TwitterScanner:
    """
    Scanner for Twitter/X trending topics and content formats.
    Uses the Twitter API to fetch trending hashtags and topics.
    """
    
    def __init__(self, relevant_topics: List[str], woeid: int = 1):
        """
        Initialize the Twitter scanner.
        
        Args:
            relevant_topics: List of topics relevant to our domain
            woeid: The 'Where On Earth ID' for the location to get trends.
                   Default is 1 (worldwide)
        """
        self.relevant_topics = [topic.lower() for topic in relevant_topics]
        self.woeid = woeid
        
        # Load API credentials from environment variables
        # These should be set in a .env file or environment
        self.api_key = os.environ.get("TWITTER_API_KEY")
        self.api_secret = os.environ.get("TWITTER_API_SECRET")
        self.access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        
        # Initialize the API client (lazy initialization)
        self._api = None
        
        logger.info("TwitterScanner initialized for WOEID: %d", self.woeid)
    
    @property
    def api(self):
        """
        Lazy initialization of the Twitter API client.
        
        Returns:
            Authenticated Tweepy API client
        """
        if self._api is None:
            # Validate API credentials
            if not all([self.api_key, self.api_secret, 
                        self.access_token, self.access_token_secret]):
                raise ValueError("Twitter API credentials are not properly configured")
            
            # Set up authentication
            auth = tweepy.OAuth1UserHandler(
                self.api_key, 
                self.api_secret,
                self.access_token, 
                self.access_token_secret
            )
            
            # Create API object
            self._api = tweepy.API(auth)
            
            # Verify credentials
            try:
                self._api.verify_credentials()
                logger.info("Twitter API authentication successful")
            except Exception as e:
                logger.error("Twitter API authentication failed: %s", str(e))
                raise
        
        return self._api
    
    def get_trending_topics(self) -> Dict[str, Any]:
        """
        Get trending topics from Twitter.
        
        Returns:
            Dictionary containing trending hashtags and popular content formats
        """
        try:
            # Get trending topics for the specified WOEID
            trends = self.api.get_place_trends(self.woeid)
            
            if not trends or not trends[0].get('trends'):
                logger.warning("No trending topics found for WOEID: %d", self.woeid)
                return {
                    "trending_hashtags": [],
                    "popular_formats": [],
                    "timestamp": datetime.now()
                }
            
            # Extract trend data - focus on hashtags and topics
            all_trends = trends[0]['trends']
            
            # Filter trends to get hashtags (starts with #)
            hashtags = [
                {
                    "name": trend['name'].lstrip('#'),
                    "url": trend['url'],
                    "tweet_volume": trend['tweet_volume'] or 0,
                    "relevance_score": self._calculate_relevance(trend['name'])
                }
                for trend in all_trends
                if trend['name'].startswith('#')
            ]
            
            # Get topics (non-hashtag trends)
            topics = [
                {
                    "name": trend['name'],
                    "url": trend['url'],
                    "tweet_volume": trend['tweet_volume'] or 0,
                    "relevance_score": self._calculate_relevance(trend['name'])
                }
                for trend in all_trends
                if not trend['name'].startswith('#')
            ]
            
            # Sort by relevance score and tweet volume
            hashtags.sort(key=lambda x: (x['relevance_score'], x['tweet_volume']), reverse=True)
            topics.sort(key=lambda x: (x['relevance_score'], x['tweet_volume']), reverse=True)
            
            # Detect popular content formats through sampling tweets
            # For now, we'll use a predefined list as a placeholder
            # In a real implementation, we would analyze recent popular tweets
            formats = self._detect_popular_formats()
            
            return {
                "trending_hashtags": hashtags[:10],  # Top 10 hashtags
                "trending_topics": topics[:10],      # Top 10 non-hashtag topics
                "popular_formats": formats,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error("Error fetching Twitter trends: %s", str(e))
            raise
    
    def _calculate_relevance(self, trend_name: str) -> float:
        """
        Calculate relevance score of a trend to our topics of interest.
        
        Args:
            trend_name: The name of the trend
            
        Returns:
            Relevance score (0.0-1.0)
        """
        trend_name = trend_name.lower()
        
        # Check if the trend directly contains any of our relevant topics
        for topic in self.relevant_topics:
            if topic in trend_name:
                return 1.0
        
        # Basic NLP could be implemented here to detect semantic similarity
        # For now, just return a lower score for trends that might be partially relevant
        for topic in self.relevant_topics:
            # Check for partial matches (e.g., "space" in "spacecraft")
            if any(word.startswith(topic) or topic.startswith(word) 
                   for word in trend_name.split()):
                return 0.5
        
        # Default score for unrelated trends
        return 0.0
    
    def _detect_popular_formats(self) -> List[Dict[str, str]]:
        """
        Detect popular content formats currently used on Twitter.
        
        Returns:
            List of dictionaries describing popular content formats
        """
        # This is a placeholder - in a real implementation, 
        # we would analyze actual tweets to identify formats
        formats = [
            {
                "name": "Thread",
                "description": "Multi-tweet threads explaining complex topics"
            },
            {
                "name": "Infographic",
                "description": "Visual data presentations and explanations"
            },
            {
                "name": "Poll",
                "description": "Interactive polls asking followers' opinions"
            },
            {
                "name": "Video",
                "description": "Short educational or explanatory videos"
            }
        ]
        
        return formats
    
    def get_sample_tweets(self, hashtag: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get sample tweets for a specific hashtag.
        
        Args:
            hashtag: The hashtag to search for (without #)
            count: Number of tweets to retrieve
            
        Returns:
            List of tweet data dictionaries
        """
        try:
            # Search for recent tweets with the hashtag
            query = f"#{hashtag}"
            tweets = self.api.search_tweets(q=query, count=count, result_type='popular')
            
            # Extract relevant information from tweets
            tweet_data = []
            for tweet in tweets:
                tweet_info = {
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "user": tweet.user.screen_name,
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count,
                    "has_media": hasattr(tweet, 'entities') and 'media' in tweet.entities
                }
                tweet_data.append(tweet_info)
            
            return tweet_data
            
        except Exception as e:
            logger.error(f"Error fetching sample tweets for #{hashtag}: {str(e)}")
            return [] 