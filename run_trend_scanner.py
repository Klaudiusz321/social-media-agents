#!/usr/bin/env python
"""
Sample script to run the TrendScannerAgent.

This script demonstrates both manual execution and scheduled operation of the agent.
"""

import os
import sys
import time
import argparse
import logging
from dotenv import load_dotenv

# Add parent directory to path to allow importing the agents package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.trend_scanner import TrendScannerAgent, TrendScannerScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TrendScannerDemo")

def run_once():
    """Run the TrendScannerAgent once and print the report."""
    logger.info("Running TrendScannerAgent once")
    
    # Initialize the agent
    agent = TrendScannerAgent()
    
    # Generate the trend report
    report = agent.generate_trend_report()
    
    # Print with formatting
    print("\n" + "="*80)
    print("SOCIAL MEDIA TREND REPORT")
    print("="*80)
    print(report)
    print("\n" + "="*80)
    print("Report generated at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("This report follows the TrendScannerAgent MDC format, focusing on 2-3 key trends per platform.")
    print("Use this data to guide your content creation strategy for maximum engagement.")
    print("="*80)
    
    logger.info("TrendScannerAgent run completed")

def run_scheduled(interval_hours):
    """Run the TrendScannerAgent on a schedule."""
    logger.info(f"Starting TrendScannerAgent scheduler (interval: {interval_hours} hours)")
    
    # Initialize the scheduler
    scheduler = TrendScannerScheduler(interval_hours=interval_hours)
    
    try:
        # Start the scheduler
        scheduler.start()
        
        logger.info(f"Scheduler running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping scheduler")
        scheduler.stop()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the TrendScannerAgent")
    parser.add_argument(
        "--schedule", 
        action="store_true", 
        help="Run the agent on a schedule"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=1, 
        help="Interval in hours between scheduled runs (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Check if API credentials are set
    if not os.environ.get("TWITTER_API_KEY"):
        logger.warning("Twitter API credentials not found. Using fallback data.")
    
    if not os.environ.get("INSTAGRAM_ACCESS_TOKEN"):
        logger.warning("Instagram API credentials not found. Using fallback data.")
    
    if not os.environ.get("LINKEDIN_ACCESS_TOKEN"):
        logger.warning("LinkedIn API credentials not found. Using fallback data.")
    
    # Run the agent based on command line arguments
    if args.schedule:
        run_scheduled(args.interval)
    else:
        run_once() 