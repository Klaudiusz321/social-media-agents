#!/usr/bin/env python3
"""
Content Creator Agent - Creates engaging content for social media platforms
based on trending topics and brand guidelines.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

# Import tools
from agent_tools import (
    generate_content_from_trends,
    generate_content_from_brief,
    generate_image_prompt,
    create_content_package
)

# Import prompts
from agent_prompts import (
    SYSTEM_PROMPT,
    CONTENT_CREATION_PROMPT,
    CONTENT_REFINEMENT_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/content_creator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ContentCreatorAgent:
    """
    Agent for creating social media content based on trends and briefs
    """
    
    def __init__(self, 
                model_name: str = "gpt-4o",
                system_prompt: str = SYSTEM_PROMPT,
                enable_logging: bool = True):
        """
        Initialize the Content Creator Agent
        
        Args:
            model_name: LLM model to use
            system_prompt: System prompt for the agent
            enable_logging: Whether to enable detailed logging
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        
        # Content templates and brand guidelines
        self.templates = self._load_templates()
        self.brand_guidelines = self._load_brand_guidelines()
        
        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data/content", exist_ok=True)
        os.makedirs("data/images", exist_ok=True)
        
        logger.info("Content Creator Agent initialized")
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load content templates from file"""
        try:
            with open("data/templates.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Templates file not found, using defaults")
            return {
                "instagram": {
                    "caption_templates": [
                        "Check out what's trending in {category}! {hashtags}",
                        "Everyone's talking about {topic}. Here's why it matters: {hashtags}",
                        "The latest {category} trends you need to know about! {hashtags}"
                    ],
                    "hashtag_count": 8
                },
                "twitter": {
                    "caption_templates": [
                        "Trending now: {topic} in {category}. What are your thoughts? {hashtags}",
                        "Breaking updates on {topic}! {hashtags}",
                        "Here's what you need to know about {topic} today. {hashtags}"
                    ],
                    "hashtag_count": 3
                },
                "linkedin": {
                    "caption_templates": [
                        "Industry Insight: How {topic} is transforming {category} for businesses. {hashtags}",
                        "Professional Update: The latest on {topic} and what it means for your career. {hashtags}",
                        "Business Trends: {topic} is changing how companies approach {category}. {hashtags}"
                    ],
                    "hashtag_count": 5
                }
            }
    
    def _load_brand_guidelines(self) -> Dict[str, Any]:
        """Load brand guidelines from file"""
        try:
            with open("data/brand_guidelines.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Brand guidelines file not found, using defaults")
            return {
                "voice": "professional yet approachable",
                "tone": "informative and helpful",
                "taboo_topics": ["politics", "religion", "controversial issues"],
                "preferred_hashtags": ["#Innovation", "#TechTrends", "#FutureOfWork"],
                "color_scheme": ["#3498db", "#2ecc71", "#e74c3c"]
            }
    
    async def create_content_from_trends(self, 
                                        trending_topics: List[Dict[str, Any]], 
                                        platforms: List[str] = ["instagram", "twitter", "linkedin"],
                                        num_pieces: int = 3) -> List[Dict[str, Any]]:
        """
        Create content based on trending topics for specified platforms
        
        Args:
            trending_topics: List of trending topics with metadata
            platforms: List of platforms to create content for
            num_pieces: Number of content pieces to create
            
        Returns:
            List of content packages
        """
        logger.info(f"Creating {num_pieces} content pieces from trending topics for {', '.join(platforms)}")
        
        content_packages = []
        
        # Sort topics by engagement score
        sorted_topics = sorted(trending_topics, 
                              key=lambda x: x.get("engagement_score", 0), 
                              reverse=True)
        
        # Generate content for the top topics
        for i in range(min(num_pieces, len(sorted_topics))):
            topic = sorted_topics[i]
            
            # Create content for each platform
            for platform in platforms:
                try:
                    # Generate content
                    content = await generate_content_from_trends(
                        topic=topic,
                        platform=platform,
                        templates=self.templates.get(platform, {}),
                        brand_guidelines=self.brand_guidelines
                    )
                    
                    # Generate image prompt
                    image_prompt = await generate_image_prompt(
                        topic=topic,
                        platform=platform,
                        content_type="post"
                    )
                    
                    # Create content package
                    package = await create_content_package(
                        topic=topic,
                        platform=platform,
                        content=content,
                        image_prompt=image_prompt
                    )
                    
                    content_packages.append(package)
                    logger.info(f"Created {platform} content for topic: {topic.get('title', 'unknown')}")
                    
                except Exception as e:
                    logger.error(f"Error creating content for {platform}: {str(e)}")
        
        # Save content packages to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/content/content_packages_{timestamp}.json", "w") as f:
                json.dump(content_packages, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving content packages: {str(e)}")
        
        return content_packages
    
    async def create_content_from_brief(self, 
                                       brief: Dict[str, Any], 
                                       platforms: List[str] = ["instagram", "twitter", "linkedin"]) -> Dict[str, Any]:
        """
        Create content based on a creative brief
        
        Args:
            brief: Creative brief with key details
            platforms: List of platforms to create content for
            
        Returns:
            Content package with all generated content
        """
        logger.info(f"Creating content from brief: {brief.get('title', 'untitled')} for {', '.join(platforms)}")
        
        content_package = {
            "brief": brief,
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        # Generate content for each platform
        for platform in platforms:
            try:
                # Generate content
                content = await generate_content_from_brief(
                    brief=brief,
                    platform=platform,
                    templates=self.templates.get(platform, {}),
                    brand_guidelines=self.brand_guidelines
                )
                
                # Generate image prompt
                image_prompt = await generate_image_prompt(
                    topic={"title": brief.get("title"), "category": brief.get("category")},
                    platform=platform,
                    content_type=brief.get("content_type", "post")
                )
                
                content_package["platforms"][platform] = {
                    "content": content,
                    "image_prompt": image_prompt
                }
                
                logger.info(f"Created {platform} content for brief: {brief.get('title', 'untitled')}")
                
            except Exception as e:
                logger.error(f"Error creating content for {platform}: {str(e)}")
        
        # Save content package to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        brief_title = brief.get("title", "untitled").replace(" ", "_").lower()
        try:
            with open(f"data/content/brief_{brief_title}_{timestamp}.json", "w") as f:
                json.dump(content_package, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving content package: {str(e)}")
        
        return content_package
    
    async def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run the Content Creator Agent with a specific command
        
        Args:
            command: Command to run
            **kwargs: Additional arguments for the command
            
        Returns:
            Result of the command
        """
        logger.info(f"Running command: {command}")
        
        if command == "create_from_trends":
            trending_topics = kwargs.get("trending_topics", [])
            platforms = kwargs.get("platforms", ["instagram", "twitter", "linkedin"])
            num_pieces = kwargs.get("num_pieces", 3)
            
            content_packages = await self.create_content_from_trends(
                trending_topics=trending_topics,
                platforms=platforms,
                num_pieces=num_pieces
            )
            
            return {
                "success": True,
                "content_packages": content_packages,
                "count": len(content_packages)
            }
            
        elif command == "create_from_brief":
            brief = kwargs.get("brief", {})
            platforms = kwargs.get("platforms", ["instagram", "twitter", "linkedin"])
            
            content_package = await self.create_content_from_brief(
                brief=brief,
                platforms=platforms
            )
            
            return {
                "success": True,
                "content_package": content_package
            }
            
        else:
            error_msg = f"Unknown command: {command}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


async def main():
    """
    Main function for testing the Content Creator Agent
    """
    agent = ContentCreatorAgent()
    
    # Create sample trending topics
    trending_topics = [
        {
            "title": "AI in Healthcare",
            "category": "Technology",
            "hashtags": ["#AI", "#Healthcare", "#MedTech", "#Innovation"],
            "engagement_score": 95,
            "timestamp": datetime.now().isoformat()
        },
        {
            "title": "Remote Work Trends",
            "category": "Business",
            "hashtags": ["#RemoteWork", "#FutureOfWork", "#WFH", "#BusinessTrends"],
            "engagement_score": 92,
            "timestamp": datetime.now().isoformat()
        },
        {
            "title": "Sustainability Practices",
            "category": "Environment",
            "hashtags": ["#Sustainability", "#GreenTech", "#ClimateAction", "#EcoFriendly"],
            "engagement_score": 88,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Create content from trends
    result = await agent.run(
        command="create_from_trends",
        trending_topics=trending_topics,
        platforms=["instagram", "twitter"],
        num_pieces=2
    )
    
    print(f"Created {result.get('count', 0)} content packages")


if __name__ == "__main__":
    asyncio.run(main()) 