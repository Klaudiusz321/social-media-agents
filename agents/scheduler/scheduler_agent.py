"""
SchedulerAgent - Module for scheduling and posting content to social media platforms.

This module handles the timing and execution of social media posts across
multiple platforms (Twitter, Instagram, LinkedIn), ensuring optimal posting
times and proper API interactions.
"""

import logging
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import threading
import queue

from .platform_posters.twitter_poster import TwitterPoster
from .platform_posters.instagram_poster import InstagramPoster
from .platform_posters.linkedin_poster import LinkedInPoster
from .post_scheduler import PostScheduler

class SchedulerAgent:
    """
    Agent responsible for scheduling and posting content to social media platforms.
    
    This agent handles the 'when' and 'where' of content distribution, taking content
    from the ContentCreatorAgent and publishing it to social platforms at optimal times.
    It manages authentication, API interactions, logging, and error handling.
    """
    
    def __init__(
        self,
        post_log_path: str = "logs/post_log.json",
        cache_dir: str = "cache",
        time_zone: str = "UTC",
        auto_retry: bool = True,
        max_retries: int = 3,
        dry_run: bool = False
    ):
        """
        Initialize the SchedulerAgent.
        
        Args:
            post_log_path: Path to the post log file
            cache_dir: Directory to cache API responses and tokens
            time_zone: Time zone for scheduling calculations
            auto_retry: Whether to automatically retry failed posts
            max_retries: Maximum number of retry attempts
            dry_run: If True, simulates posting without actually sending to APIs
        """
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.post_log_path = post_log_path
        self.cache_dir = cache_dir
        self.time_zone = time_zone
        self.auto_retry = auto_retry
        self.max_retries = max_retries
        self.dry_run = dry_run
        
        # Initialize post log directory
        os.makedirs(os.path.dirname(post_log_path), exist_ok=True)
        
        # Initialize platform posters
        self._init_platform_posters()
        
        # Initialize scheduler
        self.scheduler = PostScheduler(time_zone=time_zone)
        
        # Queue for scheduled posts
        self.post_queue = queue.PriorityQueue()
        
        # Threading control
        self.running = False
        self.scheduler_thread = None
        
        self.logger.info("SchedulerAgent initialized (dry_run: %s)", dry_run)
    
    def _init_platform_posters(self) -> None:
        """Initialize platform-specific posting handlers."""
        try:
            self.twitter_poster = TwitterPoster(
                cache_dir=self.cache_dir,
                dry_run=self.dry_run
            )
            self.instagram_poster = InstagramPoster(
                cache_dir=self.cache_dir,
                dry_run=self.dry_run
            )
            self.linkedin_poster = LinkedInPoster(
                cache_dir=self.cache_dir,
                dry_run=self.dry_run
            )
            self.logger.info("Platform posters initialized successfully")
        except Exception as e:
            self.logger.error("Error initializing platform posters: %s", str(e))
            raise
    
    def schedule_post(
        self, 
        content: Dict[str, Any],
        platform: str,
        scheduled_time: Optional[datetime] = None,
        post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a post for a specific platform.
        
        Args:
            content: The content to post (text, images, etc.)
            platform: Target platform (twitter, instagram, linkedin)
            scheduled_time: When to post (if None, uses optimal time)
            post_id: Optional unique ID for the post
            
        Returns:
            Dictionary with scheduling details
        """
        # Validate platform
        if platform.lower() not in ["twitter", "instagram", "linkedin"]:
            self.logger.error("Unsupported platform: %s", platform)
            return {"error": f"Unsupported platform: {platform}"}
        
        # Generate post ID if not provided
        if not post_id:
            post_id = f"{platform}_{int(time.time())}_{os.urandom(4).hex()}"
        
        # Determine scheduled time if not specified
        if scheduled_time is None:
            scheduled_time = self.scheduler.get_optimal_time(platform)
            self.logger.info(
                "No specific time provided, using optimal time for %s: %s", 
                platform, scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        # Create the schedule entry
        schedule_entry = {
            "post_id": post_id,
            "platform": platform.lower(),
            "content": content,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "scheduled",
            "retry_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        # Add to queue (using timestamp as priority)
        priority = scheduled_time.timestamp()
        self.post_queue.put((priority, schedule_entry))
        
        # Log the scheduled post
        self._log_scheduled_post(schedule_entry)
        
        self.logger.info(
            "Post %s scheduled for %s at %s", 
            post_id, platform, scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return {
            "status": "scheduled",
            "post_id": post_id,
            "platform": platform,
            "scheduled_time": scheduled_time.isoformat()
        }
    
    def schedule_multi_platform(
        self,
        content_by_platform: Dict[str, Dict[str, Any]],
        scheduled_times: Optional[Dict[str, datetime]] = None,
        stagger_minutes: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Schedule posts across multiple platforms.
        
        Args:
            content_by_platform: Dictionary mapping platforms to content
            scheduled_times: Optional dictionary of custom times per platform
            stagger_minutes: Minutes to stagger posts if using optimal times
            
        Returns:
            List of scheduling results
        """
        results = []
        
        # Determine base time for staggering if no specific times
        base_time = None
        if scheduled_times is None:
            scheduled_times = {}
            base_time = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=5)
        
        # Schedule each platform's content
        for i, (platform, content) in enumerate(content_by_platform.items()):
            # Get scheduled time (custom or staggered)
            if platform in scheduled_times:
                scheduled_time = scheduled_times[platform]
            elif base_time:
                # Stagger posts by platform to avoid simultaneous posting
                scheduled_time = base_time + timedelta(minutes=i * stagger_minutes)
            else:
                scheduled_time = None
            
            # Schedule the post
            result = self.schedule_post(
                content=content,
                platform=platform,
                scheduled_time=scheduled_time
            )
            
            results.append(result)
        
        return results
    
    def start_scheduler(self) -> None:
        """Start the background scheduler thread to process the queue."""
        if self.running:
            self.logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self.scheduler_thread.start()
        self.logger.info("Scheduler thread started")
    
    def stop_scheduler(self) -> None:
        """Stop the background scheduler thread."""
        if not self.running:
            self.logger.warning("Scheduler not running")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
            self.logger.info("Scheduler thread stopped")
    
    def post_now(
        self, 
        content: Dict[str, Any],
        platform: str,
        post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content immediately without scheduling.
        
        Args:
            content: The content to post
            platform: Target platform
            post_id: Optional unique ID for the post
            
        Returns:
            Result of the posting operation
        """
        # Generate post ID if not provided
        if not post_id:
            post_id = f"{platform}_{int(time.time())}_{os.urandom(4).hex()}"
        
        self.logger.info("Posting to %s immediately (post_id: %s)", platform, post_id)
        
        # Create post record
        post_record = {
            "post_id": post_id,
            "platform": platform.lower(),
            "content": content,
            "scheduled_time": datetime.now().isoformat(),
            "status": "posting",
            "retry_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        # Perform the post
        result = self._execute_post(post_record)
        
        # Update the record with result
        post_record.update({
            "status": "posted" if result.get("success") else "failed",
            "result": result,
            "posted_at": datetime.now().isoformat()
        })
        
        # Log the completed post
        self._log_post_result(post_record)
        
        return result
    
    def _scheduler_loop(self) -> None:
        """Background thread that processes the post queue."""
        self.logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Check if we have posts due for execution
                now = datetime.now()
                
                # Peek at the next item without dequeuing
                if not self.post_queue.empty():
                    priority, next_post = self.post_queue.queue[0]
                    scheduled_time = datetime.fromisoformat(next_post["scheduled_time"])
                    
                    # If it's time to post, dequeue and process
                    if scheduled_time <= now:
                        # Remove from queue
                        self.post_queue.get()
                        
                        # Execute the post
                        self.logger.info(
                            "Executing scheduled post %s for %s",
                            next_post["post_id"], next_post["platform"]
                        )
                        
                        # Process in a separate thread to not block the scheduler
                        threading.Thread(
                            target=self._process_scheduled_post,
                            args=(next_post,),
                            daemon=True
                        ).start()
                
                # Sleep briefly to avoid CPU spinning
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error("Error in scheduler loop: %s", str(e))
                # Sleep a bit longer after an error
                time.sleep(5.0)
    
    def _process_scheduled_post(self, post: Dict[str, Any]) -> None:
        """
        Process a post that's due for publishing.
        
        Args:
            post: The scheduled post data
        """
        try:
            # Update status to 'posting'
            post["status"] = "posting"
            self._log_scheduled_post(post)
            
            # Execute the post
            result = self._execute_post(post)
            
            # Update the post record
            post.update({
                "status": "posted" if result.get("success") else "failed",
                "result": result,
                "posted_at": datetime.now().isoformat()
            })
            
            # Handle retry if needed
            if not result.get("success") and self.auto_retry and post["retry_count"] < self.max_retries:
                retry_delay = min(5 * 2 ** post["retry_count"], 60)  # Exponential backoff
                
                self.logger.info(
                    "Post %s failed, scheduling retry in %d minutes",
                    post["post_id"], retry_delay
                )
                
                # Update for retry
                post["retry_count"] += 1
                post["status"] = "scheduled_retry"
                post["scheduled_time"] = (datetime.now() + timedelta(minutes=retry_delay)).isoformat()
                
                # Add back to queue with new priority
                priority = datetime.fromisoformat(post["scheduled_time"]).timestamp()
                self.post_queue.put((priority, post))
            
            # Log the final result
            self._log_post_result(post)
            
        except Exception as e:
            self.logger.error("Error processing scheduled post %s: %s", post["post_id"], str(e))
            post["status"] = "error"
            post["error"] = str(e)
            self._log_post_result(post)
    
    def _execute_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a post to the appropriate platform.
        
        Args:
            post: The post data to publish
            
        Returns:
            Result of the posting operation
        """
        platform = post["platform"].lower()
        content = post["content"]
        post_id = post["post_id"]
        
        try:
            if platform == "twitter":
                return self.twitter_poster.post(content, post_id)
            elif platform == "instagram":
                return self.instagram_poster.post(content, post_id)
            elif platform == "linkedin":
                return self.linkedin_poster.post(content, post_id)
            else:
                return {"success": False, "error": f"Unsupported platform: {platform}"}
        except Exception as e:
            self.logger.error("Error executing post to %s: %s", platform, str(e))
            return {"success": False, "error": str(e), "post_id": post_id}
    
    def _log_scheduled_post(self, post: Dict[str, Any]) -> None:
        """Log a scheduled post to the post log file."""
        try:
            post_log = self._load_post_log()
            
            # Add/update this post
            post_id = post["post_id"]
            post_log[post_id] = post
            
            # Save back to file
            self._save_post_log(post_log)
            
        except Exception as e:
            self.logger.error("Error logging scheduled post: %s", str(e))
    
    def _log_post_result(self, post: Dict[str, Any]) -> None:
        """Log the result of a post attempt."""
        try:
            post_log = self._load_post_log()
            
            # Add/update this post
            post_id = post["post_id"]
            post_log[post_id] = post
            
            # Save back to file
            self._save_post_log(post_log)
            
        except Exception as e:
            self.logger.error("Error logging post result: %s", str(e))
    
    def _load_post_log(self) -> Dict[str, Any]:
        """Load the post log from file."""
        if not os.path.exists(self.post_log_path):
            return {}
        
        try:
            with open(self.post_log_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("Error loading post log: %s", str(e))
            return {}
    
    def _save_post_log(self, post_log: Dict[str, Any]) -> None:
        """Save the post log to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.post_log_path), exist_ok=True)
            
            with open(self.post_log_path, 'w') as f:
                json.dump(post_log, f, indent=2)
        except Exception as e:
            self.logger.error("Error saving post log: %s", str(e))
    
    def get_posting_history(
        self, 
        platform: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get posting history with optional filters.
        
        Args:
            platform: Filter by platform
            status: Filter by status (scheduled, posted, failed, etc.)
            start_date: Filter by posts after this date
            end_date: Filter by posts before this date
            
        Returns:
            List of post records matching the filters
        """
        post_log = self._load_post_log()
        
        # Convert to list and sort by scheduled time
        posts = list(post_log.values())
        posts.sort(key=lambda x: x.get("scheduled_time", ""), reverse=True)
        
        # Apply filters
        filtered_posts = []
        for post in posts:
            # Platform filter
            if platform and post.get("platform") != platform.lower():
                continue
            
            # Status filter
            if status and post.get("status") != status:
                continue
            
            # Date filters
            post_time = None
            if "scheduled_time" in post:
                try:
                    post_time = datetime.fromisoformat(post["scheduled_time"])
                except (ValueError, TypeError):
                    continue
            
            if start_date and (not post_time or post_time < start_date):
                continue
                
            if end_date and (not post_time or post_time > end_date):
                continue
            
            filtered_posts.append(post)
        
        return filtered_posts 