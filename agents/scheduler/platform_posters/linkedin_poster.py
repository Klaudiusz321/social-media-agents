"""
LinkedIn Poster - Module for posting content to LinkedIn.

This module handles authentication, media uploads, and status updates for LinkedIn,
enabling the SchedulerAgent to post content to LinkedIn automatically.
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Any, Optional, Union
import tempfile
import base64

class LinkedInPoster:
    """
    Posts content to LinkedIn using the LinkedIn API.
    
    Handles OAuth authentication, media uploads, and posting text/image updates to LinkedIn.
    """
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        organization_id: Optional[str] = None,
        cache_dir: str = "cache",
        dry_run: bool = False
    ):
        """
        Initialize the LinkedInPoster.
        
        Args:
            access_token: LinkedIn API access token
            organization_id: LinkedIn organization ID (for company page posts)
            cache_dir: Directory to cache API responses
            dry_run: If True, simulates posting without actually sending to API
        """
        self.logger = logging.getLogger(__name__)
        
        # Load API credentials
        self.access_token = access_token or os.environ.get("LINKEDIN_ACCESS_TOKEN")
        self.organization_id = organization_id or os.environ.get("LINKEDIN_ORGANIZATION_ID")
        
        # Configuration
        self.cache_dir = cache_dir
        self.dry_run = dry_run
        self.api_version = "v2"
        self.base_url = f"https://api.linkedin.com/{self.api_version}"
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check if we have the required credentials
        if not self.access_token and not dry_run:
            self.logger.warning("LinkedIn access token not provided")
        
        self.logger.info(
            "LinkedInPoster initialized (dry_run: %s, using organization: %s)", 
            dry_run, bool(self.organization_id)
        )
    
    def post(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Post content to LinkedIn.
        
        Args:
            content: Dictionary containing text and optionally image data
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        if self.dry_run:
            return self._simulate_post(content, post_id)
        
        if not self.access_token:
            return {
                "success": False,
                "error": "LinkedIn access token not provided",
                "post_id": post_id
            }
        
        # Extract content
        text = content.get("text", "")
        has_image = "image" in content
        
        try:
            # Determine if posting as user or organization
            author = f"urn:li:organization:{self.organization_id}" if self.organization_id else "urn:li:person"
            
            # Create a share
            if has_image:
                return self._post_with_image(text, content["image"], author, post_id)
            else:
                return self._post_text_only(text, author, post_id)
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error("Error posting to LinkedIn: %s", error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
    
    def _post_text_only(self, text: str, author: str, post_id: str) -> Dict[str, Any]:
        """
        Post text-only content to LinkedIn.
        
        Args:
            text: Text content to post
            author: LinkedIn URN for the author (person or organization)
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        # Prepare the API request
        url = f"{self.base_url}/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Prepare the payload
        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if the request was successful
        if response.status_code != 201:
            error_msg = f"LinkedIn API error: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
        
        # Extract the LinkedIn post ID
        linkedin_post_id = response.headers.get("x-restli-id", "unknown")
        
        self.logger.info("LinkedIn post published successfully: %s", linkedin_post_id)
        
        # Cache the response
        response_data = {
            "linkedin_post_id": linkedin_post_id,
            "timestamp": time.time()
        }
        self._cache_response(post_id, response_data)
        
        return {
            "success": True,
            "linkedin_post_id": linkedin_post_id,
            "post_id": post_id
        }
    
    def _post_with_image(self, text: str, image_data: Dict[str, Any], author: str, post_id: str) -> Dict[str, Any]:
        """
        Post content with an image to LinkedIn.
        
        Args:
            text: Text content to post
            image_data: Dictionary containing image information
            author: LinkedIn URN for the author (person or organization)
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the post result
        """
        # Step 1: Register the image upload
        register_url = f"{self.base_url}/assets?action=registerUpload"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        register_response = requests.post(register_url, headers=headers, json=register_payload)
        
        if register_response.status_code != 200:
            error_msg = f"LinkedIn image registration failed: {register_response.status_code} - {register_response.text}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
        
        # Extract upload URL and asset URN
        register_data = register_response.json()
        upload_url = register_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = register_data["value"]["asset"]
        
        # Step 2: Upload the image
        # Get image data
        image_path = self._get_image_filepath(image_data)
        if not image_path:
            return {
                "success": False,
                "error": "Failed to prepare image for LinkedIn",
                "post_id": post_id
            }
        
        # Read the image file
        with open(image_path, "rb") as f:
            image_binary = f.read()
        
        # Upload the image
        upload_headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        upload_response = requests.put(upload_url, headers=upload_headers, data=image_binary)
        
        if upload_response.status_code != 201:
            error_msg = f"LinkedIn image upload failed: {upload_response.status_code} - {upload_response.text}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
        
        # Clean up temporary file if needed
        if image_path.startswith(tempfile.gettempdir()):
            try:
                os.unlink(image_path)
            except Exception as e:
                self.logger.warning("Could not remove temporary file: %s", str(e))
        
        # Step 3: Create a post with the uploaded image
        post_url = f"{self.base_url}/ugcPosts"
        
        post_payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Image"
                            },
                            "media": asset_urn,
                            "title": {
                                "text": ""
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        post_response = requests.post(post_url, headers=headers, json=post_payload)
        
        if post_response.status_code != 201:
            error_msg = f"LinkedIn post creation failed: {post_response.status_code} - {post_response.text}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id
            }
        
        # Extract the LinkedIn post ID
        linkedin_post_id = post_response.headers.get("x-restli-id", "unknown")
        
        self.logger.info("LinkedIn post with image published successfully: %s", linkedin_post_id)
        
        # Cache the response
        response_data = {
            "linkedin_post_id": linkedin_post_id,
            "asset_urn": asset_urn,
            "timestamp": time.time()
        }
        self._cache_response(post_id, response_data)
        
        return {
            "success": True,
            "linkedin_post_id": linkedin_post_id,
            "asset_urn": asset_urn,
            "post_id": post_id
        }
    
    def _simulate_post(self, content: Dict[str, Any], post_id: str) -> Dict[str, Any]:
        """
        Simulate posting to LinkedIn without actually sending API requests.
        
        Args:
            content: Dictionary containing the content to post
            post_id: Unique ID for this post
            
        Returns:
            Dictionary with the simulated post result
        """
        text = content.get("text", "")
        has_image = "image" in content
        
        self.logger.info(
            "[DRY RUN] Would post to LinkedIn: %s%s",
            text[:50] + "..." if len(text) > 50 else text,
            " (with image)" if has_image else ""
        )
        
        # Simulate a post ID
        timestamp = int(time.time())
        linkedin_post_id = f"simulated_{timestamp}_{post_id[-8:]}"
        
        return {
            "success": True,
            "linkedin_post_id": linkedin_post_id,
            "post_id": post_id,
            "simulated": True
        }
    
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
        cache_file = os.path.join(self.cache_dir, f"linkedin_{post_id}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(response_data, f, indent=2)
        except Exception as e:
            self.logger.error("Error caching LinkedIn response: %s", str(e)) 