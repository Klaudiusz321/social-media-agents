"""
ContentCreatorAgent - Generates platform-specific social media content based on trending topics.

This agent creates engaging content tailored for Twitter, Instagram, and LinkedIn, following
brand guidelines and leveraging trending topics from the TrendScannerAgent.
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from .text_generator import TextGenerator
from .image_generator import ImageGenerator
from .platform_formatter import PlatformFormatter
from .brand_guidelines import BrandGuidelinesManager
from .content_moderator import ContentModerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ContentCreatorAgent")

class ContentCreatorAgent:
    """
    Agent responsible for generating platform-specific social media content based on trends.
    Uses AI to create text and images tailored to each platform's requirements and brand guidelines.
    """
    
    def __init__(
        self,
        brand_guidelines_path: Optional[str] = None,
        image_generation_enabled: bool = True
    ):
        """
        Initialize the ContentCreatorAgent.
        
        Args:
            brand_guidelines_path: Path to brand guidelines JSON file
            image_generation_enabled: Whether to enable AI image generation
        """
        # Load brand guidelines
        self.brand_manager = BrandGuidelinesManager(brand_guidelines_path)
        
        # Initialize components
        self.text_generator = TextGenerator(self.brand_manager)
        self.image_generator = ImageGenerator(enabled=image_generation_enabled)
        self.platform_formatter = PlatformFormatter(self.brand_manager)
        self.content_moderator = ContentModerator()
        
        # Settings
        self.image_generation_enabled = image_generation_enabled
        
        logger.info("ContentCreatorAgent initialized with brand guidelines: %s", 
                    "Loaded" if self.brand_manager.guidelines else "Default")
        logger.info("Image generation is %s", 
                    "enabled" if image_generation_enabled else "disabled")
    
    def generate_content(
        self, 
        trend_data: Dict[str, Any],
        platform: str,
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a specific platform based on trend data.
        
        Args:
            trend_data: Dictionary containing trend information
            platform: Target platform (twitter, instagram, linkedin)
            product_info: Optional product information to include
            
        Returns:
            Dictionary containing the generated content
        """
        logger.info("Generating content for platform: %s", platform)
        
        # Validate platform
        if platform.lower() not in ["twitter", "instagram", "linkedin"]:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Create content based on platform
        if platform.lower() == "twitter":
            return self._generate_twitter_content(trend_data, product_info)
        elif platform.lower() == "instagram":
            return self._generate_instagram_content(trend_data, product_info)
        elif platform.lower() == "linkedin":
            return self._generate_linkedin_content(trend_data, product_info)
    
    def generate_multi_platform_content(
        self,
        trend_data: Dict[str, Any],
        platforms: List[str] = ["twitter", "instagram", "linkedin"],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate content for multiple platforms based on the same trend data.
        
        Args:
            trend_data: Dictionary containing trend information
            platforms: List of target platforms
            product_info: Optional product information to include
            
        Returns:
            Dictionary with platform keys and content values
        """
        logger.info("Generating content for multiple platforms: %s", ", ".join(platforms))
        
        # Generate content for each platform
        results = {}
        for platform in platforms:
            try:
                results[platform] = self.generate_content(
                    trend_data=trend_data,
                    platform=platform,
                    product_info=product_info
                )
                logger.info("Successfully generated content for %s", platform)
            except Exception as e:
                logger.error("Error generating content for %s: %s", platform, str(e))
                results[platform] = {"error": str(e)}
        
        return results
    
    def _generate_twitter_content(
        self,
        trend_data: Dict[str, Any],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate Twitter-specific content.
        
        Args:
            trend_data: Dictionary containing trend information
            product_info: Optional product information to include
            
        Returns:
            Dictionary containing Twitter content
        """
        # 1. Generate the text content using GPT
        text_prompt = self.platform_formatter.format_twitter_prompt(trend_data, product_info)
        text_content = self.text_generator.generate_text(text_prompt, max_length=280)
        
        # 2. Moderate the content to ensure it's appropriate
        is_appropriate = self.content_moderator.check_content(text_content)
        if not is_appropriate:
            logger.warning("Generated Twitter content was flagged as inappropriate")
            # Try to regenerate with a more strict prompt
            text_content = self.text_generator.generate_text(
                text_prompt + " Keep it professional and appropriate.",
                max_length=280
            )
            
            # Check again
            is_appropriate = self.content_moderator.check_content(text_content)
            if not is_appropriate:
                logger.error("Failed to generate appropriate Twitter content")
                return {"error": "Content moderation failed"}
        
        # 3. Generate or select an image if enabled
        image_info = {}
        if self.image_generation_enabled:
            image_prompt = self.platform_formatter.format_image_prompt(
                trend_data, 
                platform="twitter", 
                product_info=product_info
            )
            image_info = self.image_generator.generate_image(image_prompt)
        
        # 4. Extract hashtags from the content or add them if missing
        hashtags = self.platform_formatter.extract_hashtags(text_content)
        if not hashtags and trend_data.get("hashtags"):
            # Use up to 2 trending hashtags for Twitter
            hashtags = trend_data.get("hashtags", [])[:2]
        
        # 5. Assemble the final content package
        result = {
            "platform": "twitter",
            "text": text_content,
            "hashtags": hashtags,
            "character_count": len(text_content),
            "timestamp": datetime.now().isoformat(),
            "trend_source": trend_data.get("source", "unknown"),
            "moderation_passed": is_appropriate
        }
        
        # Add image info if available
        if image_info:
            result["image"] = image_info
        
        return result
    
    def _generate_instagram_content(
        self,
        trend_data: Dict[str, Any],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate Instagram-specific content.
        
        Args:
            trend_data: Dictionary containing trend information
            product_info: Optional product information to include
            
        Returns:
            Dictionary containing Instagram content
        """
        # 1. Generate the text content (caption) using GPT
        caption_prompt = self.platform_formatter.format_instagram_prompt(trend_data, product_info)
        caption = self.text_generator.generate_text(caption_prompt, max_length=2200)
        
        # 2. Moderate the content
        is_appropriate = self.content_moderator.check_content(caption)
        if not is_appropriate:
            logger.warning("Generated Instagram caption was flagged as inappropriate")
            caption = self.text_generator.generate_text(
                caption_prompt + " Keep it professional and appropriate.",
                max_length=2200
            )
            
            is_appropriate = self.content_moderator.check_content(caption)
            if not is_appropriate:
                logger.error("Failed to generate appropriate Instagram caption")
                return {"error": "Content moderation failed"}
        
        # 3. Generate or select an image (essential for Instagram)
        image_info = {}
        if self.image_generation_enabled:
            image_prompt = self.platform_formatter.format_image_prompt(
                trend_data, 
                platform="instagram", 
                product_info=product_info
            )
            image_info = self.image_generator.generate_image(
                image_prompt, 
                aspect_ratio="1:1"  # Square format for Instagram
            )
        else:
            logger.warning("Image generation disabled but Instagram content requires an image")
        
        # 4. Generate or extract hashtags (important for Instagram)
        hashtags = self.platform_formatter.extract_hashtags(caption)
        if len(hashtags) < 5 and trend_data.get("hashtags"):
            # Instagram posts typically have more hashtags (5-10)
            trending_hashtags = trend_data.get("hashtags", [])
            # Add trending hashtags that aren't already included
            for tag in trending_hashtags:
                if tag not in hashtags and len(hashtags) < 10:
                    hashtags.append(tag)
        
        # 5. Assemble the final content package
        result = {
            "platform": "instagram",
            "caption": caption,
            "hashtags": hashtags,
            "hashtag_string": " ".join([f"#{tag}" for tag in hashtags]),
            "character_count": len(caption),
            "timestamp": datetime.now().isoformat(),
            "trend_source": trend_data.get("source", "unknown"),
            "moderation_passed": is_appropriate
        }
        
        # Add image info (required for Instagram)
        if image_info:
            result["image"] = image_info
        else:
            result["warning"] = "No image provided; Instagram posts require images"
        
        return result
    
    def _generate_linkedin_content(
        self,
        trend_data: Dict[str, Any],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate LinkedIn-specific content.
        
        Args:
            trend_data: Dictionary containing trend information
            product_info: Optional product information to include
            
        Returns:
            Dictionary containing LinkedIn content
        """
        # 1. Generate the text content using GPT (can be longer and more professional)
        post_prompt = self.platform_formatter.format_linkedin_prompt(trend_data, product_info)
        post_text = self.text_generator.generate_text(post_prompt, max_length=3000)
        
        # 2. Moderate the content
        is_appropriate = self.content_moderator.check_content(post_text)
        if not is_appropriate:
            logger.warning("Generated LinkedIn post was flagged as inappropriate")
            post_text = self.text_generator.generate_text(
                post_prompt + " Keep it very professional and appropriate.",
                max_length=3000
            )
            
            is_appropriate = self.content_moderator.check_content(post_text)
            if not is_appropriate:
                logger.error("Failed to generate appropriate LinkedIn post")
                return {"error": "Content moderation failed"}
        
        # 3. Generate or select an image
        image_info = {}
        if self.image_generation_enabled:
            image_prompt = self.platform_formatter.format_image_prompt(
                trend_data, 
                platform="linkedin", 
                product_info=product_info
            )
            image_info = self.image_generator.generate_image(
                image_prompt, 
                aspect_ratio="16:9"  # Professional format for LinkedIn
            )
        
        # 4. Extract or generate hashtags (fewer, more professional for LinkedIn)
        hashtags = self.platform_formatter.extract_hashtags(post_text)
        if len(hashtags) < 3 and trend_data.get("hashtags"):
            # Select the most professional/industry-related hashtags
            professional_tags = self._filter_professional_hashtags(
                trend_data.get("hashtags", [])
            )
            # Add up to 3-4 hashtags 
            for tag in professional_tags:
                if tag not in hashtags and len(hashtags) < 4:
                    hashtags.append(tag)
        
        # 5. Assemble the final content package
        result = {
            "platform": "linkedin",
            "text": post_text,
            "hashtags": hashtags,
            "character_count": len(post_text),
            "timestamp": datetime.now().isoformat(),
            "trend_source": trend_data.get("source", "unknown"),
            "moderation_passed": is_appropriate
        }
        
        # Add image info if available
        if image_info:
            result["image"] = image_info
        
        return result
    
    def _filter_professional_hashtags(self, hashtags: List[str]) -> List[str]:
        """
        Filter hashtags to select those most appropriate for professional platforms like LinkedIn.
        
        Args:
            hashtags: List of hashtags to filter
            
        Returns:
            List of professional hashtags
        """
        # List of prefixes/terms that indicate professional or industry hashtags
        professional_indicators = [
            "tech", "industry", "business", "professional", "career", 
            "education", "science", "research", "development", "innovation",
            "leadership", "management", "strategy", "growth", "analysis",
            "data", "engineering", "stem", "academic", "learning"
        ]
        
        # Filter hashtags
        professional_tags = []
        for tag in hashtags:
            tag_lower = tag.lower()
            # Check if the tag contains any professional indicator
            if any(indicator in tag_lower for indicator in professional_indicators):
                professional_tags.append(tag)
        
        # If we didn't find any professional tags, return the original list
        # (limited to 4) to ensure we have something to work with
        if not professional_tags:
            return hashtags[:4]
        
        return professional_tags 