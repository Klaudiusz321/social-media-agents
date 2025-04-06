#!/usr/bin/env python
"""
Demo script for using the ContentCreatorAgent with TrendScannerAgent.

This script shows how to use the ContentCreatorAgent to generate content
based on trends identified by the TrendScannerAgent.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to allow importing the agents packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.trend_scanner import TrendScannerAgent
from agents.content_creator import ContentCreatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ContentCreatorDemo")

def load_product_info(product_info_path: str = None):
    """
    Load product information from a JSON file or use default.
    
    Args:
        product_info_path: Path to product info JSON file
        
    Returns:
        Dictionary containing product information
    """
    if product_info_path and os.path.exists(product_info_path):
        try:
            with open(product_info_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error loading product info: %s", str(e))
    
    # Default product info
    return {
        "name": "AstroCalc Pro",
        "description": "An advanced calculator app for astronomy and physics calculations",
        "features": [
            {
                "name": "Stellar Simulator",
                "description": "Accurately simulate star patterns from any location"
            },
            {
                "name": "Eclipse Tracker",
                "description": "Predict and visualize eclipses with precision timing"
            }
        ],
        "website": "https://example.com/astrocalc"
    }

def convert_trend_report_to_data(trend_report: str) -> dict:
    """
    Convert a trend report string to structured data.
    
    Args:
        trend_report: Trend report string from TrendScannerAgent
        
    Returns:
        Dictionary containing structured trend data
    """
    # Extract Twitter trends
    twitter_section = None
    instagram_section = None
    linkedin_section = None
    
    lines = trend_report.split('\n')
    
    # Find platform sections
    for i, line in enumerate(lines):
        if "**Twitter:**" in line:
            twitter_section = line.replace("**Twitter:**", "").strip()
        elif "**Instagram:**" in line:
            instagram_section = line.replace("**Instagram:**", "").strip()
        elif "**LinkedIn:**" in line:
            linkedin_section = line.replace("**LinkedIn:**", "").strip()
    
    # Extract hashtags - using a simple approach
    hashtags = []
    
    # Extract hashtags from Twitter section
    if twitter_section:
        for tag in twitter_section.split():
            if tag.startswith('`#') and tag.endswith('`'):
                hashtags.append(tag.strip('`#'))
    
    # Extract hashtags from Instagram section
    if instagram_section:
        for tag in instagram_section.split():
            if tag.startswith('`#') and tag.endswith('`'):
                hashtags.append(tag.strip('`#'))
    
    # Process the main title/trend
    title = "Astronomy and Space Science"  # Default
    if twitter_section:
        # Try to extract a trending topic from the Twitter section
        if "`#" in twitter_section:
            title_match = twitter_section.split("`#")[1].split("`")[0]
            if title_match:
                title = title_match
    
    # Create structured trend data
    trend_data = {
        "title": title,
        "description": "This is a trending topic in astronomy and space science.",
        "hashtags": list(set(hashtags)),  # Remove duplicates
        "source": "TrendScannerAgent",
        "timestamp": datetime.now().isoformat()
    }
    
    # Add platform-specific data if available
    if twitter_section:
        trend_data["twitter_insight"] = twitter_section
    if instagram_section:
        trend_data["instagram_insight"] = instagram_section
    if linkedin_section:
        trend_data["linkedin_insight"] = linkedin_section
    
    return trend_data

def save_content(content: dict, output_dir: str = "generated_content"):
    """
    Save generated content to files.
    
    Args:
        content: Dictionary containing generated content
        output_dir: Directory to save content to
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save content for each platform
    for platform, platform_content in content.items():
        if "error" in platform_content:
            logger.warning("Error in %s content: %s", platform, platform_content["error"])
            continue
        
        # Create a JSON file with the content
        filename = f"{platform}_content_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(platform_content, f, indent=2)
        
        logger.info("Saved %s content to %s", platform, filepath)
        
        # Also save as text file for easy viewing
        text_filename = f"{platform}_content_{timestamp}.txt"
        text_filepath = os.path.join(output_dir, text_filename)
        
        with open(text_filepath, 'w') as f:
            f.write(f"# {platform.capitalize()} Content\n\n")
            
            if platform == "twitter":
                f.write(f"Tweet: {platform_content.get('text', '')}\n\n")
            elif platform == "instagram":
                f.write(f"Caption: {platform_content.get('caption', '')}\n\n")
            elif platform == "linkedin":
                f.write(f"Post: {platform_content.get('text', '')}\n\n")
            
            if "hashtags" in platform_content:
                f.write(f"Hashtags: {', '.join(['#' + tag for tag in platform_content['hashtags']])}\n\n")
            
            if "image" in platform_content:
                f.write(f"Image prompt: {platform_content['image'].get('prompt', '')}\n")
                if "filepath" in platform_content["image"]:
                    f.write(f"Image file: {platform_content['image']['filepath']}\n\n")
        
        logger.info("Saved %s text content to %s", platform, text_filepath)

def main():
    """Run the ContentCreatorAgent demo."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ContentCreatorAgent Demo")
    parser.add_argument(
        "--platforms", 
        nargs="+", 
        default=["twitter", "instagram", "linkedin"],
        help="Platforms to generate content for"
    )
    parser.add_argument(
        "--brand-guidelines", 
        type=str, 
        default="agents/content_creator/example_brand_guidelines.json",
        help="Path to brand guidelines JSON file"
    )
    parser.add_argument(
        "--product-info", 
        type=str, 
        default=None,
        help="Path to product info JSON file"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="generated_content",
        help="Directory to save generated content"
    )
    parser.add_argument(
        "--disable-image-generation", 
        action="store_true",
        help="Disable image generation"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not found in environment. Text generation will fail.")
    
    if not os.environ.get("STABILITY_API_KEY") and not args.disable_image_generation:
        logger.warning("STABILITY_API_KEY not found in environment. Image generation will fail.")
    
    # Load product info
    product_info = load_product_info(args.product_info)
    
    # Step 1: Get trending topics from TrendScannerAgent
    logger.info("Getting trending topics from TrendScannerAgent...")
    trend_scanner = TrendScannerAgent()
    trend_report = trend_scanner.generate_trend_report()
    
    print("\n" + "="*80)
    print("TREND REPORT")
    print("="*80)
    print(trend_report)
    print("="*80 + "\n")
    
    # Step 2: Convert trend report to structured data
    trend_data = convert_trend_report_to_data(trend_report)
    logger.info("Extracted trend data: %s", trend_data.get("title"))
    
    # Step 3: Initialize the ContentCreatorAgent
    logger.info("Initializing ContentCreatorAgent...")
    content_creator = ContentCreatorAgent(
        brand_guidelines_path=args.brand_guidelines,
        image_generation_enabled=not args.disable_image_generation
    )
    
    # Step 4: Generate content for each platform
    logger.info("Generating content for platforms: %s", ", ".join(args.platforms))
    
    content = content_creator.generate_multi_platform_content(
        trend_data=trend_data,
        platforms=args.platforms,
        product_info=product_info
    )
    
    # Step 5: Save the generated content
    save_content(content, args.output_dir)
    
    # Print summary
    print("\n" + "="*80)
    print("CONTENT GENERATION SUMMARY")
    print("="*80)
    
    for platform in args.platforms:
        if platform in content:
            platform_content = content[platform]
            if "error" in platform_content:
                print(f"{platform.capitalize()}: Error - {platform_content['error']}")
            else:
                if platform == "twitter":
                    print(f"Twitter: Generated {len(platform_content.get('text', ''))} character tweet")
                elif platform == "instagram":
                    print(f"Instagram: Generated {len(platform_content.get('caption', ''))} character caption")
                elif platform == "linkedin":
                    print(f"LinkedIn: Generated {len(platform_content.get('text', ''))} character post")
                
                if "image" in platform_content:
                    print(f"  - Image: {platform_content['image'].get('filename', 'Generated')}")
                else:
                    print("  - No image generated")
    
    print(f"\nContent saved to {args.output_dir}/")
    print("="*80)

if __name__ == "__main__":
    main() 