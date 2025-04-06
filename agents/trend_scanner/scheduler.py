"""
Scheduler - Module for periodically running the TrendScannerAgent.

Uses APScheduler to run the agent at specified intervals and generate trend reports.
"""

import logging
import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .agent import TrendScannerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TrendScannerScheduler")

class TrendScannerScheduler:
    """
    Scheduler for running the TrendScannerAgent at specified intervals.
    """
    
    def __init__(
        self, 
        interval_hours: int = 1,
        report_dir: str = "reports",
        cache_duration: int = 3600,  # Default cache: 1 hour
        relevant_topics: list = None
    ):
        """
        Initialize the scheduler.
        
        Args:
            interval_hours: Hours between trend scanning runs
            report_dir: Directory to save trend reports
            cache_duration: Time in seconds before refreshing trends data
            relevant_topics: List of topics of interest
        """
        self.interval_hours = interval_hours
        self.report_dir = report_dir
        
        # Create report directory if it doesn't exist
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            logger.info("Created report directory: %s", report_dir)
        
        # Initialize the trend scanner agent
        self.agent = TrendScannerAgent(
            cache_duration=cache_duration,
            relevant_topics=relevant_topics
        )
        
        # Initialize the scheduler
        self.scheduler = BackgroundScheduler()
        
        logger.info("TrendScannerScheduler initialized with %d hour interval", 
                   interval_hours)
    
    def start(self):
        """Start the scheduler."""
        try:
            # Add job to run at the specified interval
            self.scheduler.add_job(
                func=self._run_scan_and_report,
                trigger=IntervalTrigger(hours=self.interval_hours),
                id='trend_scanner_job',
                name='Scan trends and generate report',
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("Scheduler started. Will run every %d hours", self.interval_hours)
            
            # Run immediately for the first time
            self._run_scan_and_report()
            
        except Exception as e:
            logger.error("Error starting scheduler: %s", str(e))
            raise
    
    def stop(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error("Error stopping scheduler: %s", str(e))
    
    def _run_scan_and_report(self):
        """Run the trend scanner and generate a report."""
        try:
            logger.info("Running scheduled trend scan")
            
            # Generate the trend report
            report = self.agent.generate_trend_report()
            
            # Save the report to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"trend_report_{timestamp}.txt"
            report_path = os.path.join(self.report_dir, report_filename)
            
            # Add a header for the saved file
            file_content = [
                "="*80,
                "SOCIAL MEDIA TREND REPORT",
                "="*80,
                "",
                report,
                "",
                "="*80,
                f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "This report follows the TrendScannerAgent MDC format, focusing on 2-3 key trends per platform.",
                "Use this data to guide your content creation strategy for maximum engagement.",
                "="*80
            ]
            
            # Write the report to the file
            with open(report_path, 'w') as report_file:
                report_file.write("\n".join(file_content))
            
            logger.info("Trend report saved to %s", report_path)
            
            # For demonstration, also log a summary of the report to console
            logger.info("Trend Report Summary:\n%s", report[:300] + "..." 
                       if len(report) > 300 else report)
            
        except Exception as e:
            logger.error("Error in scheduled trend scan: %s", str(e))

if __name__ == "__main__":
    # Example usage
    scheduler = TrendScannerScheduler(interval_hours=1)
    scheduler.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop() 