"""
Twitter Poster - Module for posting content to Twitter.

This module handles authentication, media uploads, and status updates for the Twitter
API, enabling the SchedulerAgent to post content to Twitter automatically.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
import tempfile
import base64

# Optional import to handle cases where tweepy might not be installed
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

class TwitterPoster:
    """
    Posts content to Twitter using the Twitter API via Tweepy.
    
    Handles authentication, media uploads, and posting text content to Twitter.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        cache_dir: str = "cache",
        dry_run: bool = False
    ):
        """
        Initialize the TwitterPoster.
        
        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            cache_dir: Directory to cache API responses
            dry_run: If True, simulates posting without actually sending to API
        """
        self.logger = logging.getLogger(__name__)
        
        # Check if tweepy is available
        if not TWEEPY_AVAILABLE and not dry_run:
            self.logger.error("Tweepy is not installed. Please install it with 'pip install tweepy'")
        
        # Load API credentials
        self.api_key = api_key or os.environ.get("TWITTER_API_KEY")
        self.api_secret = api_secret or os.environ.get("TWITTER_API_SECRET")
        self.access_token = access_token or os.environ.get("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        
        # Configuration
        self.cache_dir = cache_dir
        self.dry_run = dry_run
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize API client if not in dry run mode
        self.api = None
        if not dry_run and TWEEPY_AVAILABLE:
            self._init_api()
        
        self.logger.info("TwitterPoster initialized (dry_run: %s)", dry_run)
    
    def _init_api(self) -> None:
        """Initialize the Tweepy API client."""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            self.logger.error("Twitter API credentials not fully provided")
            return
        
        try:
            # Authenticate with Twitter API
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            
            # Create API client
            self.api = tweepy.API(auth)
            
            # Verify credentials
            self.api.verify_credentials()
            self.logger.info("Twitter API authentication successful")
            
        except tweepy.TweepyException as e:
            self.logger.error("Twitter API authentication failed: %s", str(e))
            self.api = None
    
    def post(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Post content to Twitter.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        if self.dry_run:
            return self._simulate_post(content, post_id)
        
        if not TWEEPY_AVAILABLE:
            return {
                "success": False,
                "error": "Tweepy is not installed",
                "post_id": post_id
            }
        
        if not self.api:
            return {
                "success": False,
                "error": "Twitter API client not initialized",
                "post_id": post_id
            }
        
        try:
            # Extract text content
            text = content.get("text", "")
            if not text:
                return {
                    "success": False,
                    "error": "No text content provided",
                    "post_id": post_id
                }
            
            # Check for length constraints
            if len(text) > 280:
                self.logger.warning(
                    "Tweet text exceeds 280 characters, truncating (original: %d chars)",
                    len(text)
                )
                text = text[:277] + "..."
            
            # Check for media (image or video)
            media_ids = []
            if "image" in content:
                media_id = self._upload_media(content["image"])
                if media_id:
                    media_ids.append(media_id)
            
            # Post the tweet
            tweet = self.api.update_status(
                status=text,
                media_ids=media_ids if media_ids else None
            )
            
            # Get the tweet ID and URL
            tweet_id = tweet.id_str
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            
            self.logger.info("Tweet posted successfully: %s", tweet_url)
            
            # Cache the response
            self._cache_response(post_id, {
                "tweet_id": tweet_id,
                "tweet_url": tweet_url,
                "media_ids": media_ids,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "tweet_url": tweet_url,
                "post_id": post_id
            }
            
        except tweepy.TweepyException as e:
            error_msg = str(e)
            self.logger.error("Error posting to Twitter: %s", error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
    
    def _simulate_post(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Simulate posting to Twitter without actually sending API requests.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the simulated post result
        """
        text = content.get("text", "")
        has_image = "image" in content
        
        self.logger.info(
            "[DRY RUN] Would post to Twitter: %s%s",
            text[:50] + "..." if len(text) > 50 else text,
            " (with image)" if has_image else ""
        )
        
        # Simulate a tweet ID and URL
        tweet_id = f"simulated_{int(time.time())}_{post_id[-8:]}"
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        
        return {
            "success": True,
            "tweet_id": tweet_id,
            "tweet_url": tweet_url,
            "post_id": post_id,
            "simulated": True
        }
    
    def _upload_media(self, image_data: Dict[str, Any]) -> Optional[str]:
        """
        Upload media to Twitter.
        
        Args:
            image_data: Dictionary containing image information
            
        Returns:
            Media ID if successful, None otherwise
        """
        try:
            # Check if we have a file path
            if "filepath" in image_data and os.path.exists(image_data["filepath"]):
                # Upload directly from file
                media = self.api.media_upload(image_data["filepath"])
                return media.media_id_string
            
            # Check if we have base64 data
            elif "base64" in image_data:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_path = temp_file.name
                    # Write base64 data to file
                    temp_file.write(base64.b64decode(image_data["base64"]))
                
                try:
                    # Upload the temporary file
                    media = self.api.media_upload(temp_path)
                    return media.media_id_string
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
            
            self.logger.error("No valid image data found for upload")
            return None
            
        except Exception as e:
            self.logger.error("Error uploading media to Twitter: %s", str(e))
            return None
    
    def _cache_response(self, post_id: str, response_data: Dict[str, Any]) -> None:
        """
        Cache the API response for a post.
        
        Args:
            post_id: Unique ID for the post
            response_data: Data to cache
        """
        cache_file = os.path.join(self.cache_dir, f"twitter_{post_id}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(response_data, f, indent=2)
        except Exception as e:
            self.logger.error("Error caching Twitter response: %s", str(e)) 