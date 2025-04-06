"""
ContentCreatorAgent module for generating platform-specific social media content.

This module contains the ContentCreatorAgent class which handles the generation
of content for various social media platforms based on trending topics.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .text_generator import TextGenerator
from .image_generator import ImageGenerator 
from .platform_formatter import PlatformFormatter
from .brand_guidelines_manager import BrandGuidelinesManager
from .content_moderator import ContentModerator

class ContentCreatorAgent:
    """
    Agent for creating platform-specific social media content.
    
    This agent handles the generation of content for various social media platforms
    based on trending topics, using generative AI for text and images while ensuring
    content adheres to brand guidelines and platform constraints.
    """
    
    def __init__(
        self,
        brand_guidelines_path: str = None,
        openai_api_key: str = None,
        stability_api_key: str = None,
        image_generation_enabled: bool = True,
        custom_filter_words: List[str] = None,
        cache_dir: str = "cache"
    ):
        """
        Initialize the ContentCreatorAgent.
        
        Args:
            brand_guidelines_path: Path to JSON file containing brand guidelines
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            stability_api_key: Stability AI API key (defaults to STABILITY_API_KEY env var)
            image_generation_enabled: Whether to generate images
            custom_filter_words: List of words to filter from content
            cache_dir: Directory to cache generated content
        """
        self.logger = logging.getLogger(__name__)
        
        # Set API keys
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.stability_api_key = stability_api_key or os.environ.get("STABILITY_API_KEY")
        
        # Initialize components
        self.text_generator = TextGenerator(api_key=self.openai_api_key)
        self.image_gen_enabled = image_generation_enabled
        
        if self.image_gen_enabled:
            if not self.stability_api_key:
                self.logger.warning("Image generation enabled but no Stability API key provided.")
                self.image_gen_enabled = False
            else:
                self.image_generator = ImageGenerator(api_key=self.stability_api_key, cache_dir=cache_dir)
        
        # Load brand guidelines
        self.guidelines_manager = BrandGuidelinesManager(guidelines_path=brand_guidelines_path)
        self.brand_guidelines = self.guidelines_manager.get_guidelines()
        
        # Initialize platform formatter
        self.platform_formatter = PlatformFormatter(self.brand_guidelines)
        
        # Initialize content moderator
        self.content_moderator = ContentModerator(custom_filter_words=custom_filter_words)
        
        # Create cache directory if it doesn't exist
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def generate_content_for_platform(
        self, 
        platform: str, 
        trend_data: Dict[str, Any],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a specific platform.
        
        Args:
            platform: Social media platform (twitter, instagram, linkedin)
            trend_data: Dictionary containing trend information
            product_info: Dictionary containing product information
            
        Returns:
            Dictionary containing the generated content
        """
        self.logger.info(f"Generating content for {platform} about '{trend_data.get('title', 'unknown trend')}'")
        
        # Validate platform
        if platform not in ["twitter", "instagram", "linkedin"]:
            self.logger.error(f"Unsupported platform: {platform}")
            return {"error": f"Unsupported platform: {platform}"}
        
        # Get platform-specific guidelines
        platform_guidelines = self.guidelines_manager.get_platform_guidelines(platform)
        
        # Prepare the context for text generation
        context = {
            "platform": platform,
            "trend": trend_data,
            "brand_guidelines": self.brand_guidelines,
            "platform_guidelines": platform_guidelines,
            "product_info": product_info or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate text content
        try:
            text_content = self.text_generator.generate_text(
                context=context,
                platform=platform
            )
        except Exception as e:
            self.logger.error(f"Error generating text for {platform}: {str(e)}")
            return {"error": f"Text generation failed: {str(e)}"}
        
        # Check content moderation
        moderation_result = self.content_moderator.check_content(text_content.get("text", ""))
        if not moderation_result["is_appropriate"]:
            self.logger.warning(f"Content for {platform} flagged by moderation: {moderation_result['reason']}")
            return {"error": f"Content moderation failed: {moderation_result['reason']}"}
        
        # Format content for platform
        formatted_content = self.platform_formatter.format_for_platform(
            content=text_content,
            platform=platform
        )
        
        # Add hashtags from trend data
        hashtags = trend_data.get("hashtags", [])
        if hashtags:
            formatted_content["hashtags"] = hashtags
            
            # Append hashtags to content if appropriate for platform
            if platform == "twitter" or platform == "instagram":
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                
                if platform == "twitter":
                    if "text" in formatted_content:
                        formatted_content["text"] = formatted_content["text"] + "\n\n" + hashtag_text
                elif platform == "instagram":
                    if "caption" in formatted_content:
                        formatted_content["caption"] = formatted_content["caption"] + "\n\n" + hashtag_text
        
        # Generate image if enabled
        if self.image_gen_enabled:
            try:
                # Create image prompt based on trend and platform
                image_prompt = self.text_generator.generate_image_prompt(
                    trend=trend_data,
                    platform=platform,
                    brand_guidelines=self.brand_guidelines
                )
                
                # Generate image
                image_data = self.image_generator.generate_image(
                    prompt=image_prompt,
                    platform=platform,
                    trend_title=trend_data.get("title", "trend")
                )
                
                # Add image data to content
                formatted_content["image"] = image_data
                
            except Exception as e:
                self.logger.error(f"Error generating image for {platform}: {str(e)}")
                formatted_content["image_error"] = str(e)
        
        return formatted_content
    
    def generate_multi_platform_content(
        self,
        trend_data: Dict[str, Any],
        platforms: List[str] = ["twitter", "instagram", "linkedin"],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate content for multiple platforms.
        
        Args:
            trend_data: Dictionary containing trend information
            platforms: List of platforms to generate content for
            product_info: Dictionary containing product information
            
        Returns:
            Dictionary mapping platforms to their generated content
        """
        self.logger.info(f"Generating content for {len(platforms)} platforms: {', '.join(platforms)}")
        
        results = {}
        
        for platform in platforms:
            results[platform] = self.generate_content_for_platform(
                platform=platform,
                trend_data=trend_data,
                product_info=product_info
            )
        
        return results
    
    def validate_trend_data(self, trend_data: Dict[str, Any]) -> bool:
        """
        Validate trend data to ensure it has required fields.
        
        Args:
            trend_data: Dictionary containing trend information
            
        Returns:
            True if trend data is valid, False otherwise
        """
        required_fields = ["title"]
        
        for field in required_fields:
            if field not in trend_data:
                self.logger.error(f"Missing required field in trend data: {field}")
                return False
        
        return True
    
    def save_content_to_file(
        self, 
        content: Dict[str, Any], 
        filename: str = None,
        output_dir: str = "output"
    ) -> str:
        """
        Save generated content to a file.
        
        Args:
            content: Dictionary containing generated content
            filename: Name of file to save content to (default: auto-generated)
            output_dir: Directory to save file in
            
        Returns:
            Path to saved file
        """
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            platform = content.get("platform", "content")
            filename = f"{platform}_{timestamp}.json"
        
        # Save content to file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        
        self.logger.info(f"Content saved to {filepath}")
        
        return filepath 