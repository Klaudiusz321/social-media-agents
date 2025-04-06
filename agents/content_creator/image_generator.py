"""
Image Generator - Module for generating images using Stability AI API.

Handles creating image prompts, calling the Stability AI API, and processing responses
for different content types and platforms.
"""

import logging
import os
import json
import requests
import base64
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ImageGenerator")

class ImageGenerator:
    """
    Generates images using Stability AI's API.
    Creates platform-specific images based on trend data.
    """
    
    def __init__(
        self,
        enabled: bool = True,
        api_host: str = "https://api.stability.ai",
        engine_id: str = "stable-diffusion-xl-1024-v1-0",
        output_dir: str = "generated_images",
        max_retries: int = 3
    ):
        """
        Initialize the ImageGenerator.
        
        Args:
            enabled: Whether image generation is enabled
            api_host: Stability AI API host
            engine_id: Model engine ID to use
            output_dir: Directory to save generated images
            max_retries: Maximum number of API call retries
        """
        self.enabled = enabled
        self.api_host = api_host
        self.engine_id = engine_id
        self.output_dir = output_dir
        self.max_retries = max_retries
        
        # Load API key from environment variable
        self.api_key = os.environ.get("STABILITY_API_KEY")
        if not self.api_key and enabled:
            logger.warning("Stability AI API key not found. Image generation will fail.")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info("Created output directory: %s", output_dir)
        
        logger.info("ImageGenerator initialized (enabled: %s)", enabled)
    
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        save_image: bool = True,
        cfg_scale: float = 7.0,
        steps: int = 30
    ) -> Dict[str, Any]:
        """
        Generate an image using the Stability AI API.
        
        Args:
            prompt: Image generation prompt
            aspect_ratio: Image aspect ratio (1:1, 16:9, etc.)
            save_image: Whether to save the image to disk
            cfg_scale: How strictly to follow the prompt (higher = more strictly)
            steps: Number of diffusion steps to run
            
        Returns:
            Dictionary with image information
        """
        if not self.enabled:
            logger.info("Image generation disabled")
            return {"status": "disabled", "prompt": prompt}
        
        if not self.api_key:
            logger.error("Stability AI API key not configured")
            return {"error": "API key not configured", "prompt": prompt}
        
        # Determine dimensions based on aspect ratio
        width, height = self._get_dimensions_from_aspect_ratio(aspect_ratio)
        
        # Track retries
        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info("Generating image with prompt: %s", prompt[:100] + "..." if len(prompt) > 100 else prompt)
                
                # Prepare the API request
                response = requests.post(
                    f"{self.api_host}/v1/generation/{self.engine_id}/text-to-image",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "text_prompts": [
                            {
                                "text": prompt,
                                "weight": 1.0
                            }
                        ],
                        "cfg_scale": cfg_scale,
                        "height": height,
                        "width": width,
                        "steps": steps,
                        "samples": 1
                    }
                )
                
                # Check for errors
                if response.status_code != 200:
                    logger.error("Error generating image: %s", response.text)
                    raise Exception(f"API error: {response.status_code} - {response.text}")
                
                # Process successful response
                data = response.json()
                
                # Save and process the image
                image_info = self._process_image_response(data, prompt, save_image)
                
                logger.info("Successfully generated image: %s", image_info.get("filename", "unknown"))
                return image_info
                
            except requests.exceptions.RequestException as e:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                logger.warning("API request error: %s. Retrying in %d seconds...", str(e), wait_time)
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error("Error generating image: %s", str(e))
                raise
        
        logger.error("Failed to generate image after %d retries", self.max_retries)
        return {"error": f"Failed after {self.max_retries} retries", "prompt": prompt}
    
    def _get_dimensions_from_aspect_ratio(self, aspect_ratio: str) -> tuple:
        """
        Convert aspect ratio string to width and height dimensions.
        
        Args:
            aspect_ratio: String aspect ratio (e.g., "1:1", "16:9")
            
        Returns:
            Tuple of (width, height) values
        """
        # Default square image
        if aspect_ratio == "1:1":
            return (1024, 1024)
        
        # Landscape 16:9 (common for video/LinkedIn)
        elif aspect_ratio == "16:9":
            return (1024, 576)
        
        # Portrait 4:5 (Instagram)
        elif aspect_ratio == "4:5":
            return (768, 960)
        
        # Other common ratios
        elif aspect_ratio == "3:2":
            return (1024, 682)
        elif aspect_ratio == "4:3":
            return (1024, 768)
        
        # Default to square if ratio not recognized
        else:
            logger.warning("Unrecognized aspect ratio: %s. Using 1:1 (square).", aspect_ratio)
            return (1024, 1024)
    
    def _process_image_response(
        self,
        response_data: Dict[str, Any],
        prompt: str,
        save_image: bool
    ) -> Dict[str, Any]:
        """
        Process the API response and save the generated image.
        
        Args:
            response_data: API response data
            prompt: The prompt used to generate the image
            save_image: Whether to save the image to disk
            
        Returns:
            Dictionary with image information
        """
        # Check if we have artifacts
        if "artifacts" not in response_data or not response_data["artifacts"]:
            return {"error": "No image artifacts found in response", "prompt": prompt}
        
        # Get the first artifact (we only requested one)
        artifact = response_data["artifacts"][0]
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"image_{timestamp}_{unique_id}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save the image if requested
        if save_image:
            image_data = base64.b64decode(artifact["base64"])
            with open(filepath, "wb") as f:
                f.write(image_data)
            logger.info("Image saved to: %s", filepath)
        
        # Return image information
        return {
            "filename": filename,
            "filepath": filepath if save_image else None,
            "prompt": prompt,
            "seed": artifact.get("seed"),
            "timestamp": timestamp,
            "saved": save_image,
            "width": artifact.get("width"),
            "height": artifact.get("height")
        } 