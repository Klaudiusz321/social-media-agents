"""
Cache Manager - Module for caching trend data to avoid excessive API calls.

Provides utilities to store and retrieve trend data with timestamps for determining
when to refresh the data.
"""

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import pickle

logger = logging.getLogger("CacheManager")

class CacheManager:
    """
    Manages caching of trend data to minimize API calls and improve performance.
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.trends_cache_file = os.path.join(cache_dir, "trends_cache.pkl")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            logger.info("Created cache directory: %s", cache_dir)
    
    def cache_trends(self, trends_data: Dict[str, Any]) -> bool:
        """
        Cache trend data to a file.
        
        Args:
            trends_data: Dictionary containing trend data with timestamps
            
        Returns:
            True if caching was successful, False otherwise
        """
        try:
            # Create a cache object with timestamp
            cache_object = {
                "timestamp": datetime.now(),
                "data": trends_data
            }
            
            # Save the cache object
            with open(self.trends_cache_file, 'wb') as cache_file:
                pickle.dump(cache_object, cache_file)
            
            logger.info("Successfully cached trend data at %s", 
                       cache_object["timestamp"].strftime('%Y-%m-%d %H:%M:%S'))
            return True
            
        except Exception as e:
            logger.error("Error caching trend data: %s", str(e))
            return False
    
    def get_cached_trends(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached trend data if available.
        
        Returns:
            Dictionary containing cached data with timestamp or None if no cache exists
        """
        try:
            # Check if cache file exists
            if not os.path.exists(self.trends_cache_file):
                logger.info("No cache file found at %s", self.trends_cache_file)
                return None
            
            # Load the cache object
            with open(self.trends_cache_file, 'rb') as cache_file:
                cache_object = pickle.load(cache_file)
            
            logger.info("Successfully loaded cached data from %s", 
                       cache_object["timestamp"].strftime('%Y-%m-%d %H:%M:%S'))
            return cache_object
            
        except Exception as e:
            logger.error("Error loading cached trend data: %s", str(e))
            return None
    
    def clear_cache(self) -> bool:
        """
        Clear the cached trend data.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        try:
            if os.path.exists(self.trends_cache_file):
                os.remove(self.trends_cache_file)
                logger.info("Successfully cleared trend cache")
                return True
            else:
                logger.info("No cache file exists to clear")
                return True
                
        except Exception as e:
            logger.error("Error clearing trend cache: %s", str(e))
            return False
            
    def get_cache_age(self) -> Optional[int]:
        """
        Get the age of the cached data in seconds.
        
        Returns:
            Age in seconds or None if no cache exists
        """
        cache_data = self.get_cached_trends()
        if not cache_data or "timestamp" not in cache_data:
            return None
        
        cache_time = cache_data["timestamp"]
        current_time = datetime.now()
        age_seconds = (current_time - cache_time).total_seconds()
        
        return int(age_seconds) 