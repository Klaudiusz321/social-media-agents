"""
Instagram Poster - Module for posting content to Instagram.

This module handles authentication, media uploads, and caption posting for the Instagram
Graph API, enabling the SchedulerAgent to post content to Instagram automatically.
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Any, Optional, Union
import tempfile
import base64

# Optional import to handle cases where instagrapi might not be installed
try:
    from instagrapi import Client
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False

class InstagramPoster:
    """
    Posts content to Instagram using the Instagram Graph API or Instagrapi.
    
    Handles authentication, media uploads, and posting captions to Instagram.
    """
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
        cache_dir: str = "cache",
        dry_run: bool = False
    ):
        """
        Initialize the InstagramPoster.
        
        Args:
            username: Instagram username (for instagrapi)
            password: Instagram password (for instagrapi)
            access_token: Instagram Graph API access token
            instagram_account_id: Instagram account ID for Graph API
            cache_dir: Directory to cache API responses
            dry_run: If True, simulates posting without actually sending to API
        """
        self.logger = logging.getLogger(__name__)
        
        # Check if instagrapi is available
        if not INSTAGRAPI_AVAILABLE and not dry_run:
            self.logger.warning("Instagrapi is not installed. Please install it with 'pip install instagrapi'")
        
        # Load API credentials
        self.username = username or os.environ.get("INSTAGRAM_USERNAME")
        self.password = password or os.environ.get("INSTAGRAM_PASSWORD")
        self.access_token = access_token or os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = instagram_account_id or os.environ.get("INSTAGRAM_ACCOUNT_ID")
        
        # Configuration
        self.cache_dir = cache_dir
        self.dry_run = dry_run
        self.using_graph_api = bool(self.access_token and self.instagram_account_id)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize API client if not in dry run mode
        self.client = None
        if not dry_run and INSTAGRAPI_AVAILABLE:
            self._init_client()
        
        self.logger.info(
            "InstagramPoster initialized (dry_run: %s, using_graph_api: %s)",
            dry_run, self.using_graph_api
        )
    
    def _init_client(self) -> None:
        """Initialize the Instagram API client."""
        # Use Graph API if access token is provided
        if self.using_graph_api:
            self.logger.info("Using Instagram Graph API for posting")
            return
        
        # Otherwise use instagrapi with username/password
        if not all([self.username, self.password]):
            self.logger.error("Instagram credentials not fully provided")
            return
        
        try:
            # Create Instagram client
            self.client = Client()
            
            # Load session if exists
            session_file = os.path.join(self.cache_dir, "instagram_session.json")
            if os.path.exists(session_file):
                try:
                    self.client.load_settings(session_file)
                    self.logger.info("Loaded Instagram session from cache")
                    
                    # Verify session is still valid
                    if self.client.user_id is None:
                        self.logger.info("Instagram session expired, logging in again")
                        self.client.login(self.username, self.password)
                except Exception as e:
                    self.logger.warning("Error loading Instagram session: %s", str(e))
                    self.client.login(self.username, self.password)
            else:
                # Login with username and password
                self.client.login(self.username, self.password)
            
            # Save session for future use
            self.client.dump_settings(session_file)
            self.logger.info("Instagram authentication successful")
            
        except Exception as e:
            self.logger.error("Instagram authentication failed: %s", str(e))
            self.client = None
    
    def post(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Post content to Instagram.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        if self.dry_run:
            return self._simulate_post(content, post_id)
        
        # Instagram posts require an image
        if "image" not in content:
            return {
                "success": False,
                "error": "Instagram posts require an image",
                "post_id": post_id
            }
        
        # Check which posting method to use
        if self.using_graph_api:
            return self._post_using_graph_api(content, post_id)
        elif INSTAGRAPI_AVAILABLE and self.client:
            return self._post_using_instagrapi(content, post_id)
        else:
            return {
                "success": False,
                "error": "No valid Instagram posting method available",
                "post_id": post_id
            }
    
    def _post_using_graph_api(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Post to Instagram using the Graph API.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        try:
            # Extract caption
            caption = content.get("caption", "")
            
            # Get image URL or upload to temporary hosting
            image_url = self._get_image_url(content["image"])
            if not image_url:
                return {
                    "success": False,
                    "error": "Failed to prepare image URL for Instagram Graph API",
                    "post_id": post_id
                }
            
            # Step 1: Create a media container
            container_url = f"https://graph.facebook.com/v13.0/{self.instagram_account_id}/media"
            container_params = {
                "access_token": self.access_token,
                "image_url": image_url,
                "caption": caption
            }
            
            container_response = requests.post(container_url, params=container_params)
            container_data = container_response.json()
            
            if "id" not in container_data:
                error_msg = container_data.get("error", {}).get("message", "Unknown error")
                self.logger.error("Error creating Instagram media container: %s", error_msg)
                return {
                    "success": False,
                    "error": f"Container creation failed: {error_msg}",
                    "post_id": post_id
                }
            
            container_id = container_data["id"]
            
            # Step 2: Publish the container
            publish_url = f"https://graph.facebook.com/v13.0/{self.instagram_account_id}/media_publish"
            publish_params = {
                "access_token": self.access_token,
                "creation_id": container_id
            }
            
            publish_response = requests.post(publish_url, params=publish_params)
            publish_data = publish_response.json()
            
            if "id" not in publish_data:
                error_msg = publish_data.get("error", {}).get("message", "Unknown error")
                self.logger.error("Error publishing Instagram media: %s", error_msg)
                return {
                    "success": False,
                    "error": f"Publishing failed: {error_msg}",
                    "post_id": post_id
                }
            
            # Get the Instagram post ID and URL
            instagram_post_id = publish_data["id"]
            instagram_url = f"https://www.instagram.com/p/{instagram_post_id}"
            
            self.logger.info("Instagram post published successfully: %s", instagram_post_id)
            
            # Cache the response
            self._cache_response(post_id, {
                "instagram_post_id": instagram_post_id,
                "instagram_url": instagram_url,
                "container_id": container_id,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "instagram_post_id": instagram_post_id,
                "instagram_url": instagram_url,
                "post_id": post_id
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error("Error posting to Instagram with Graph API: %s", error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
    
    def _post_using_instagrapi(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Post to Instagram using Instagrapi.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        try:
            # Extract caption
            caption = content.get("caption", "")
            
            # Get image filepath
            image_path = self._get_image_filepath(content["image"])
            if not image_path:
                return {
                    "success": False,
                    "error": "Failed to prepare image for Instagram",
                    "post_id": post_id
                }
            
            # Upload photo
            media = self.client.photo_upload(
                path=image_path,
                caption=caption
            )
            
            # Get media information
            media_id = media.id
            media_code = media.code
            media_url = f"https://www.instagram.com/p/{media_code}"
            
            self.logger.info("Instagram post published successfully: %s", media_url)
            
            # Clean up temporary file if needed
            if image_path.startswith(tempfile.gettempdir()):
                try:
                    os.unlink(image_path)
                except Exception as e:
                    self.logger.warning("Could not remove temporary file: %s", str(e))
            
            # Cache the response
            self._cache_response(post_id, {
                "instagram_post_id": media_id,
                "instagram_code": media_code,
                "instagram_url": media_url,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "instagram_post_id": media_id,
                "instagram_code": media_code,
                "instagram_url": media_url,
                "post_id": post_id
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error("Error posting to Instagram with Instagrapi: %s", error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
    
    def _simulate_post(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Simulate posting to Instagram without actually sending API requests.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the simulated post result
        """
        caption = content.get("caption", "")
        has_image = "image" in content
        
        self.logger.info(
            "[DRY RUN] Would post to Instagram: %s%s",
            caption[:50] + "..." if len(caption) > 50 else caption,
            " (with image)" if has_image else " (ERROR: no image)"
        )
        
        # Simulate a post ID and code
        timestamp = int(time.time())
        media_id = f"simulated_{timestamp}_{post_id[-8:]}"
        media_code = f"ABC{timestamp % 10000}"
        media_url = f"https://www.instagram.com/p/{media_code}"
        
        return {
            "success": True,
            "instagram_post_id": media_id,
            "instagram_code": media_code,
            "instagram_url": media_url,
            "post_id": post_id,
            "simulated": True
        }
    
    def _get_image_url(self, image_data: Dict[str, Any]) -> Optional[str]:
        """
        Get or create a publicly accessible URL for an image.
        
        Args:
            image_data: Dictionary containing image information
            
        Returns:
            Public URL for the image if successful, None otherwise
        """
        # If the image already has a URL, use it
        if "url" in image_data:
            return image_data["url"]
        
        # TODO: Implement temporary image hosting for the Graph API approach
        # For production use, this would need to:
        # 1. Upload the image to a temporary hosting service
        # 2. Return the public URL
        # 3. Set up a mechanism to clean up the image after posting
        
        self.logger.error("No image URL provided, and temp hosting not implemented")
        return None
    
    def _get_image_filepath(self, image_data: Dict[str, Any]) -> Optional[str]:
        """
        Get or create a filepath for an image.
        
        Args:
            image_data: Dictionary containing image information
            
        Returns:
            Filepath for the image if successful, None otherwise
        """
        # Check if we have a file path
        if "filepath" in image_data and os.path.exists(image_data["filepath"]):
            return image_data["filepath"]
        
        # Check if we have base64 data
        elif "base64" in image_data:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_path = temp_file.name
                # Write base64 data to file
                temp_file.write(base64.b64decode(image_data["base64"]))
            
            return temp_path
        
        self.logger.error("No valid image data found")
        return None
    
    def _cache_response(self, post_id: str, response_data: Dict[str, Any]) -> None:
        """
        Cache the API response for a post.
        
        Args:
            post_id: Unique ID for the post
            response_data: Data to cache
        """
        cache_file = os.path.join(self.cache_dir, f"instagram_{post_id}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(response_data, f, indent=2)
        except Exception as e:
            self.logger.error("Error caching Instagram response: %s", str(e)) 