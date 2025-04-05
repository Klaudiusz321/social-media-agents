"""
Tools for the Content Creator Agent

This module provides tools for generating content,
creating image prompts, and assembling content packages.
"""

import os
import random
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.Client()

async def generate_content_from_trends(
    topic: Dict[str, Any],
    platform: str,
    templates: Dict[str, Any],
    brand_guidelines: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate content for a specific platform based on a trending topic
    
    Args:
        topic: Trending topic data
        platform: Target platform (instagram, twitter, linkedin)
        templates: Platform-specific templates
        brand_guidelines: Brand voice and tone guidelines
        
    Returns:
        Generated content
    """
    logger.info(f"Generating {platform} content for topic: {topic.get('title', 'unknown')}")
    
    # Extract topic details
    title = topic.get("title", "")
    category = topic.get("category", "")
    hashtags = topic.get("hashtags", [])
    
    # Get platform-specific templates
    caption_templates = templates.get("caption_templates", [])
    hashtag_count = templates.get("hashtag_count", 5)
    
    if not caption_templates:
        # Default templates if none provided
        caption_templates = [
            "Check out what's trending in {category}! {hashtags}",
            "Everyone's talking about {topic}. Here's why it matters: {hashtags}",
            "The latest {category} trends you need to know about! {hashtags}"
        ]
    
    # Use LLM to generate the content
    try:
        # Create prompt
        prompt = f"""
        Generate engaging social media content for {platform} about the following trending topic:
        
        Topic: {title}
        Category: {category}
        
        Brand voice: {brand_guidelines.get('voice', 'professional yet approachable')}
        Brand tone: {brand_guidelines.get('tone', 'informative and helpful')}
        
        The content should include:
        1. An attention-grabbing headline
        2. A compelling main text (caption)
        3. A call-to-action
        4. Relevant hashtags (max {hashtag_count})
        
        Avoid these topics: {', '.join(brand_guidelines.get('taboo_topics', []))}
        
        Please format your response as JSON with the following structure:
        {
            "headline": "The headline text",
            "caption": "The main caption text",
            "cta": "The call-to-action",
            "hashtags": ["hashtag1", "hashtag2", ...]
        }
        """
        
        # Call the LLM
        response = await client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a professional social media content creator."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        content_text = response.choices[0].message.content
        content = json.loads(content_text)
        
        # Add predefined hashtags from topic and brand guidelines
        existing_hashtags = content.get("hashtags", [])
        preferred_hashtags = brand_guidelines.get("preferred_hashtags", [])
        topic_hashtags = hashtags
        
        # Combine and limit hashtags
        all_hashtags = list(set(existing_hashtags + preferred_hashtags + topic_hashtags))
        content["hashtags"] = all_hashtags[:hashtag_count]
        
        # Add platform-specific metadata
        content["platform"] = platform
        content["topic"] = title
        content["category"] = category
        content["timestamp"] = datetime.now().isoformat()
        
        return content
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        
        # Fallback to template-based generation
        template = random.choice(caption_templates)
        selected_hashtags = hashtags[:hashtag_count] if hashtags else []
        
        content = {
            "headline": f"Trending in {category}: {title}",
            "caption": template.format(topic=title, category=category, hashtags=""),
            "cta": "What do you think?",
            "hashtags": selected_hashtags,
            "platform": platform,
            "topic": title,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "note": "Generated using fallback template due to error"
        }
        
        return content

async def generate_content_from_brief(
    brief: Dict[str, Any],
    platform: str,
    templates: Dict[str, Any],
    brand_guidelines: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate content for a specific platform based on a creative brief
    
    Args:
        brief: Creative brief with key details
        platform: Target platform (instagram, twitter, linkedin)
        templates: Platform-specific templates
        brand_guidelines: Brand voice and tone guidelines
        
    Returns:
        Generated content
    """
    logger.info(f"Generating {platform} content for brief: {brief.get('title', 'untitled')}")
    
    # Extract brief details
    title = brief.get("title", "")
    description = brief.get("description", "")
    target_audience = brief.get("target_audience", "general audience")
    key_messages = brief.get("key_messages", [])
    hashtags = brief.get("hashtags", [])
    
    # Get platform-specific settings
    hashtag_count = templates.get("hashtag_count", 5)
    
    # Use LLM to generate the content
    try:
        # Create prompt
        prompt = f"""
        Generate engaging social media content for {platform} based on this creative brief:
        
        Title: {title}
        Description: {description}
        Target audience: {target_audience}
        Key messages: {', '.join(key_messages)}
        
        Brand voice: {brand_guidelines.get('voice', 'professional yet approachable')}
        Brand tone: {brand_guidelines.get('tone', 'informative and helpful')}
        
        The content should include:
        1. An attention-grabbing headline
        2. A compelling main text (caption) that incorporates the key messages
        3. A call-to-action tailored to the target audience
        4. Relevant hashtags (max {hashtag_count})
        
        Avoid these topics: {', '.join(brand_guidelines.get('taboo_topics', []))}
        
        Format your response as JSON with this structure:
        {
            "headline": "The headline text",
            "caption": "The main caption text",
            "cta": "The call-to-action",
            "hashtags": ["hashtag1", "hashtag2", ...]
        }
        """
        
        # Call the LLM
        response = await client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a professional social media content creator."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        content_text = response.choices[0].message.content
        content = json.loads(content_text)
        
        # Add predefined hashtags from brief and brand guidelines
        existing_hashtags = content.get("hashtags", [])
        preferred_hashtags = brand_guidelines.get("preferred_hashtags", [])
        brief_hashtags = hashtags
        
        # Combine and limit hashtags
        all_hashtags = list(set(existing_hashtags + preferred_hashtags + brief_hashtags))
        content["hashtags"] = all_hashtags[:hashtag_count]
        
        # Add metadata
        content["platform"] = platform
        content["brief_title"] = title
        content["target_audience"] = target_audience
        content["timestamp"] = datetime.now().isoformat()
        
        return content
        
    except Exception as e:
        logger.error(f"Error generating content from brief: {str(e)}")
        
        # Fallback to simple generation
        content = {
            "headline": title,
            "caption": description,
            "cta": "Learn more!",
            "hashtags": hashtags[:hashtag_count] if hashtags else [],
            "platform": platform,
            "brief_title": title,
            "target_audience": target_audience,
            "timestamp": datetime.now().isoformat(),
            "note": "Generated using fallback method due to error"
        }
        
        return content

async def generate_image_prompt(
    topic: Dict[str, Any],
    platform: str,
    content_type: str = "post"
) -> str:
    """
    Generate a detailed prompt for image generation
    
    Args:
        topic: Topic data (title, category)
        platform: Target platform
        content_type: Type of content (post, story, carousel)
        
    Returns:
        Image generation prompt
    """
    logger.info(f"Generating {content_type} image prompt for {platform}")
    
    title = topic.get("title", "")
    category = topic.get("category", "")
    
    # Platform-specific image styles
    style_map = {
        "instagram": "vibrant, colorful, visually striking, high resolution",
        "twitter": "clear, bold, attention-grabbing, simple",
        "linkedin": "professional, clean, corporate, polished"
    }
    
    style = style_map.get(platform, "modern, digital")
    
    # Content type adjustments
    if content_type == "story":
        aspect = "vertical 9:16 aspect ratio"
    elif content_type == "carousel":
        aspect = "square 1:1 aspect ratio"
    else:  # post
        aspect = "square 1:1 aspect ratio"
    
    try:
        # Create prompt for image generation
        prompt = f"""
        Generate an image prompt for a professional AI image generator.
        
        Topic: {title}
        Category: {category}
        Platform: {platform}
        Content type: {content_type}
        Style: {style}
        Format: {aspect}
        
        Please create a detailed, descriptive prompt that would result in a compelling,
        professional image suitable for {platform} that represents the topic visually.
        Make sure the prompt is detailed and specific enough for an AI image generator.
        """
        
        # Call the LLM
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional prompt engineer for AI image generation."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the image prompt
        image_prompt = response.choices[0].message.content.strip()
        
        return image_prompt
        
    except Exception as e:
        logger.error(f"Error generating image prompt: {str(e)}")
        
        # Fallback image prompt
        fallback_prompt = f"Professional {style} image of {title} related to {category}, {aspect}."
        return fallback_prompt

async def create_content_package(
    topic: Dict[str, Any],
    platform: str,
    content: Dict[str, Any],
    image_prompt: str
) -> Dict[str, Any]:
    """
    Assemble a complete content package
    
    Args:
        topic: Topic data
        platform: Target platform
        content: Generated content
        image_prompt: Generated image prompt
        
    Returns:
        Complete content package
    """
    logger.info(f"Creating content package for {platform}: {topic.get('title', 'unknown')}")
    
    # Create the content package
    package = {
        "metadata": {
            "platform": platform,
            "topic": topic.get("title", ""),
            "category": topic.get("category", ""),
            "timestamp": datetime.now().isoformat(),
            "content_type": "post"
        },
        "content": content,
        "image": {
            "prompt": image_prompt,
            "generation_status": "pending"
        }
    }
    
    # Add the original topic data for reference
    package["topic_data"] = topic
    
    return package 