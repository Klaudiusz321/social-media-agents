#!/usr/bin/env python3
"""
Scheduler Demo - Demonstrates integration between TrendScannerAgent, ContentCreatorAgent, and SchedulerAgent.

This demo shows the full workflow from trend scanning to content creation to scheduled posting.
"""

import os
import sys
import json
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.trend_scanner.trend_scanner_agent import TrendScannerAgent
from agents.content_creator.content_creator_agent import ContentCreatorAgent
from agents.scheduler.scheduler_agent import SchedulerAgent
from agents.scheduler.post_scheduler import PostScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scheduler_demo.log')
    ]
)

logger = logging.getLogger("scheduler_demo")

def load_brand_guidelines(brand_file: str) -> Dict[str, Any]:
    """
    Load brand guidelines from a JSON file.
    
    Args:
        brand_file: Path to the brand guidelines JSON file
        
    Returns:
        Dictionary containing brand guidelines
    """
    try:
        with open(brand_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load brand guidelines: {e}")
        return {}

def load_trend_report(trend_file: str) -> Dict[str, Any]:
    """
    Load trend report from a JSON file.
    
    Args:
        trend_file: Path to the trend report JSON file
        
    Returns:
        Dictionary containing trend data
    """
    try:
        with open(trend_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load trend report: {e}")
        return {}

def scan_trends(keywords: List[str], output_file: str) -> bool:
    """
    Run the TrendScannerAgent to scan for trends.
    
    Args:
        keywords: List of keywords to search for
        output_file: Path to save the trend report
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Starting trend scanning with keywords: {keywords}")
        
        # Initialize TrendScannerAgent
        trend_scanner = TrendScannerAgent(
            api_keys={},  # Use environment variables for API keys
            cache_dir="cache"
        )
        
        # Scan for trends
        trends = trend_scanner.scan_trends(keywords)
        
        # Save trend report
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(trends, f, indent=2)
        
        logger.info(f"Trend report saved to {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error scanning trends: {e}")
        return False

def create_content(trend_file: str, brand_file: str, platforms: List[str], output_dir: str) -> Dict[str, str]:
    """
    Run the ContentCreatorAgent to create content based on trends.
    
    Args:
        trend_file: Path to the trend report JSON file
        brand_file: Path to the brand guidelines JSON file
        platforms: List of platforms to create content for
        output_dir: Directory to save the generated content
        
    Returns:
        Dictionary mapping platforms to content file paths
    """
    try:
        logger.info(f"Creating content for platforms: {platforms}")
        
        # Load trend data and brand guidelines
        trend_data = load_trend_report(trend_file)
        brand_guidelines = load_brand_guidelines(brand_file)
        
        if not trend_data:
            logger.error("No trend data available")
            return {}
        
        # Initialize ContentCreatorAgent
        content_creator = ContentCreatorAgent(
            brand_guidelines=brand_guidelines,
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            output_dir=output_dir
        )
        
        # Generate content for each platform
        content_files = {}
        for platform in platforms:
            try:
                content_file = os.path.join(output_dir, f"{platform}_content.json")
                logger.info(f"Generating content for {platform}")
                
                content = content_creator.generate_for_platform(
                    platform=platform,
                    trend_data=trend_data,
                    save_to_file=content_file
                )
                
                if content:
                    content_files[platform] = content_file
                    logger.info(f"Content generated for {platform} and saved to {content_file}")
                else:
                    logger.warning(f"Failed to generate content for {platform}")
            
            except Exception as e:
                logger.error(f"Error generating content for {platform}: {e}")
        
        return content_files
    
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        return {}

def schedule_posts(content_files: Dict[str, str], time_zone: str, dry_run: bool = True) -> bool:
    """
    Schedule posts using the SchedulerAgent.
    
    Args:
        content_files: Dictionary mapping platforms to content file paths
        time_zone: Time zone for scheduling
        dry_run: If True, simulate posting without actually sending to APIs
        
    Returns:
        True if scheduling was successful, False otherwise
    """
    try:
        logger.info(f"Scheduling posts for platforms: {list(content_files.keys())}")
        
        # Initialize PostScheduler and SchedulerAgent
        post_scheduler = PostScheduler(time_zone=time_zone)
        
        scheduler = SchedulerAgent(
            time_zone=time_zone,
            cache_dir="cache",
            post_log_path="logs/posts.json",
            dry_run=dry_run
        )
        
        # Start the scheduler
        scheduler.start_scheduler()
        
        # Load content for each platform and schedule posts
        for platform, content_file in content_files.items():
            try:
                with open(content_file, 'r') as f:
                    content = json.load(f)
                
                # Get optimal posting time
                optimal_time = post_scheduler.get_optimal_time(platform)
                post_time = optimal_time.strftime("%Y-%m-%d %H:%M:%S")
                
                logger.info(f"Scheduling {platform} post for {post_time}")
                
                # Schedule the post
                if platform.lower() == "twitter":
                    scheduler.schedule_post(
                        platform="twitter",
                        content=content,
                        scheduled_time=optimal_time,
                        post_id=f"{platform}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )
                
                elif platform.lower() == "instagram":
                    scheduler.schedule_post(
                        platform="instagram",
                        content=content,
                        scheduled_time=optimal_time,
                        post_id=f"{platform}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )
                
                elif platform.lower() == "linkedin":
                    scheduler.schedule_post(
                        platform="linkedin",
                        content=content,
                        scheduled_time=optimal_time,
                        post_id=f"{platform}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )
            
            except Exception as e:
                logger.error(f"Error scheduling post for {platform}: {e}")
        
        logger.info("All posts have been scheduled")
        
        # In a real application, we would keep the scheduler running
        # For the demo, we'll stop it after a short delay
        if dry_run:
            import time
            logger.info("Dry run mode: Waiting 10 seconds to show scheduled posts...")
            time.sleep(10)
        
        # Stop the scheduler
        scheduler.stop_scheduler()
        return True
    
    except Exception as e:
        logger.error(f"Error scheduling posts: {e}")
        return False

def run_full_pipeline(
    keywords: List[str],
    platforms: List[str],
    brand_file: str,
    time_zone: str,
    dry_run: bool = True,
    skip_trend_scan: bool = False
) -> bool:
    """
    Run the full pipeline: trend scanning, content creation, and post scheduling.
    
    Args:
        keywords: List of keywords to search for trends
        platforms: List of platforms to create content for
        brand_file: Path to the brand guidelines JSON file
        time_zone: Time zone for scheduling
        dry_run: If True, simulate posting without actually sending to APIs
        skip_trend_scan: If True, use existing trend report
        
    Returns:
        True if the pipeline was successful, False otherwise
    """
    try:
        # Create necessary directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("cache", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("content", exist_ok=True)
        
        trend_file = "data/trend_report.json"
        
        # Step 1: Scan for trends (or use existing report)
        if not skip_trend_scan:
            logger.info("Step 1: Scanning for trends")
            if not scan_trends(keywords, trend_file):
                logger.error("Trend scanning failed")
                return False
        else:
            logger.info("Step 1: Using existing trend report")
            if not os.path.exists(trend_file):
                logger.error(f"Trend report {trend_file} not found")
                return False
        
        # Step 2: Create content
        logger.info("Step 2: Creating content")
        content_files = create_content(trend_file, brand_file, platforms, "content")
        
        if not content_files:
            logger.error("Content creation failed")
            return False
        
        # Step 3: Schedule posts
        logger.info("Step 3: Scheduling posts")
        if not schedule_posts(content_files, time_zone, dry_run):
            logger.error("Post scheduling failed")
            return False
        
        logger.info("Full pipeline completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error in pipeline: {e}")
        return False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Demo of the TrendScanner, ContentCreator, and Scheduler integration")
    
    parser.add_argument('--keywords', '-k', type=str, nargs='+', default=['astronomy', 'physics', 'space'],
                        help='Keywords to search for trends')
    
    parser.add_argument('--platforms', '-p', type=str, nargs='+', default=['twitter', 'instagram', 'linkedin'],
                        choices=['twitter', 'instagram', 'linkedin'],
                        help='Platforms to create content for')
    
    parser.add_argument('--brand-file', '-b', type=str, 
                        default='agents/content_creator/example_brand_guidelines.json',
                        help='Path to the brand guidelines JSON file')
    
    parser.add_argument('--time-zone', '-t', type=str, default='America/New_York',
                        help='Time zone for scheduling')
    
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Simulate posting without actually sending to APIs')
    
    parser.add_argument('--skip-trend-scan', '-s', action='store_true',
                        help='Skip trend scanning and use existing report')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    logger.info("Starting scheduler demo")
    logger.info(f"Keywords: {args.keywords}")
    logger.info(f"Platforms: {args.platforms}")
    logger.info(f"Brand file: {args.brand_file}")
    logger.info(f"Time zone: {args.time_zone}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Skip trend scan: {args.skip_trend_scan}")
    
    success = run_full_pipeline(
        keywords=args.keywords,
        platforms=args.platforms,
        brand_file=args.brand_file,
        time_zone=args.time_zone,
        dry_run=args.dry_run,
        skip_trend_scan=args.skip_trend_scan
    )
    
    if success:
        logger.info("Demo completed successfully")
        sys.exit(0)
    else:
        logger.error("Demo failed")
        sys.exit(1) 