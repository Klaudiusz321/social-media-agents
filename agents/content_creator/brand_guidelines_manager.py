"""
Brand Guidelines Manager - Module for loading and managing brand guidelines.

Handles loading brand guidelines from JSON files and providing access to specific
guideline elements for content generation.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union

class BrandGuidelinesManager:
    """
    Manages brand guidelines for content generation.
    
    This class is responsible for loading brand guidelines from JSON files
    and providing structured access to different guideline components like
    brand voice, content requirements, visual style, and platform-specific
    guidelines.
    """
    
    def __init__(self, guidelines_path: Optional[str] = None):
        """
        Initialize the BrandGuidelinesManager.
        
        Args:
            guidelines_path: Path to the JSON file containing brand guidelines
        """
        self.logger = logging.getLogger(__name__)
        self.guidelines = None
        
        # Load guidelines if path is provided
        if guidelines_path:
            self.load_guidelines(guidelines_path)
        else:
            # If no guidelines provided, use default science/education brand voice
            self.guidelines = self._get_default_guidelines()
            self.logger.info("Using default brand guidelines")
    
    def load_guidelines(self, guidelines_path: str) -> bool:
        """
        Load brand guidelines from a JSON file.
        
        Args:
            guidelines_path: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(guidelines_path):
                self.logger.warning("Guidelines file not found: %s", guidelines_path)
                return False
            
            with open(guidelines_path, 'r') as f:
                self.guidelines = json.load(f)
            
            self.logger.info("Successfully loaded brand guidelines from %s", guidelines_path)
            return True
            
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in guidelines file: %s", guidelines_path)
            return False
            
        except Exception as e:
            self.logger.error("Error loading guidelines: %s", str(e))
            return False
    
    def get_guidelines(self) -> Dict[str, Any]:
        """
        Get the full brand guidelines.
        
        Returns:
            Dictionary containing all brand guidelines
        """
        if not self.guidelines:
            return self._get_default_guidelines()
        
        return self.guidelines
    
    def get_brand_voice(self) -> Dict[str, Any]:
        """
        Get the brand voice guidelines.
        
        Returns:
            Dictionary containing brand voice information
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("voice", {})
        
        return self.guidelines.get("voice", {})
    
    def get_content_requirements(self) -> List[str]:
        """
        Get the content requirements guidelines.
        
        Returns:
            List of content requirements
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("content_requirements", [])
        
        return self.guidelines.get("content_requirements", [])
    
    def get_prohibited_content(self) -> List[str]:
        """
        Get the prohibited content guidelines.
        
        Returns:
            List of prohibited content types
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("prohibited_content", [])
        
        return self.guidelines.get("prohibited_content", [])
    
    def get_visual_style(self) -> Dict[str, Any]:
        """
        Get the visual style guidelines.
        
        Returns:
            Dictionary containing visual style guidelines
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("visual_style", {})
        
        return self.guidelines.get("visual_style", {})
    
    def get_platform_guidelines(self, platform: str) -> Dict[str, Any]:
        """
        Get platform-specific guidelines.
        
        Args:
            platform: Platform name (twitter, instagram, linkedin)
            
        Returns:
            Dictionary containing platform-specific guidelines
        """
        if not self.guidelines or "platforms" not in self.guidelines:
            default = self._get_default_guidelines().get("platforms", {})
            return default.get(platform.lower(), {})
        
        platforms = self.guidelines.get("platforms", {})
        return platforms.get(platform.lower(), {})
    
    def get_product_mentions(self) -> Dict[str, Any]:
        """
        Get requirements for how to mention products.
        
        Returns:
            Dictionary containing product mention guidelines
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("product_mentions", {})
        
        return self.guidelines.get("product_mentions", {})
    
    def get_target_audience(self) -> Dict[str, Any]:
        """
        Get target audience information.
        
        Returns:
            Dictionary containing target audience information
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("target_audience", {})
        
        return self.guidelines.get("target_audience", {})
    
    def get_product_features(self) -> List[Dict[str, Any]]:
        """
        Get product features information.
        
        Returns:
            List of product features
        """
        if not self.guidelines:
            return self._get_default_guidelines().get("product_features", [])
        
        return self.guidelines.get("product_features", [])
    
    def _get_default_guidelines(self) -> Dict[str, Any]:
        """
        Create default brand guidelines for a science/education brand.
        
        Returns:
            Dictionary containing default guidelines
        """
        return {
            "brand_name": "AstroCalc Pro",
            "voice": {
                "description": "Educational, enthusiastic, and authoritative but accessible.",
                "traits": [
                    "Friendly language that makes complex topics approachable",
                    "Conversational but accurate",
                    "Balances technical precision with engaging explanations",
                    "Passionate about astronomy and space science"
                ]
            },
            "content_requirements": [
                "Always include the product name 'AstroCalc Pro' when relevant",
                "Focus on educational value",
                "Use metric units for measurements",
                "Ensure all scientific claims are accurate",
                "When possible, relate content to real-world applications"
            ],
            "prohibited_content": [
                "Political statements",
                "Religious references",
                "Criticism of other brands or products",
                "Exaggerated or unsubstantiated claims",
                "Overly technical jargon without explanation"
            ],
            "visual_style": {
                "description": "Clean, modern aesthetic with deep space theme",
                "colors": ["#1A2980", "#26D0CE", "#FFFFFF", "#121212"],
                "preferred_imagery": "Scientific illustrations over abstract art",
                "diagrams": "Clear and well-labeled educational diagrams"
            },
            "product_mentions": {
                "first_mention": "AstroCalc Pro",
                "subsequent_mentions": ["AstroCalc", "the app"],
                "emphasis": "Highlight one feature per post, phrased as a benefit"
            },
            "platforms": {
                "twitter": {
                    "tone": "More casual, brief but impactful",
                    "hashtags": ["#AstroCalcPro", "#Astronomy", "#SpaceScience"],
                    "cta": "Encourage clicks to profile link"
                },
                "instagram": {
                    "tone": "Visual first, focus on awe and wonder",
                    "hashtags": ["#AstroCalcPro", "#Astronomy", "#SpaceLovers", "#AstronomyFacts"],
                    "cta": "Encourage profile visits and app downloads"
                },
                "linkedin": {
                    "tone": "Professional, educational focus, industry insights",
                    "hashtags": ["#SpaceTech", "#STEM", "#ScienceEducation"],
                    "cta": "Position as thought leaders, encourage professional discussion"
                }
            },
            "product_features": [
                {
                    "name": "Stellar Simulator",
                    "description": "Accurately simulate star patterns from any location on Earth",
                    "benefit": "Never miss an astronomical event again"
                },
                {
                    "name": "Eclipse Tracker",
                    "description": "Predict and visualize eclipses with precision timing",
                    "benefit": "Plan your observation schedule months in advance"
                },
                {
                    "name": "Planet Viewer",
                    "description": "Interactive 3D model of planets and their orbits",
                    "benefit": "Understand complex celestial mechanics visually"
                },
                {
                    "name": "Astronomy Calculator",
                    "description": "Perform complex astronomical calculations instantly",
                    "benefit": "Save hours on manual calculations for research or hobby"
                }
            ],
            "target_audience": {
                "primary": [
                    "Amateur astronomers",
                    "Astrophotographers",
                    "STEM educators"
                ],
                "secondary": [
                    "Science enthusiasts",
                    "Students",
                    "Professional astronomers"
                ]
            }
        } 