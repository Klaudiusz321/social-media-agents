#!/usr/bin/env python3
"""
Analytics Agent - Analyzes social media performance data and generates
comprehensive reports and insights for campaign optimization.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from dotenv import load_dotenv

# Import tools
from agent_tools import (
    fetch_platform_metrics,
    generate_performance_report,
    analyze_audience_demographics,
    identify_content_trends,
    create_visualization,
    export_report_to_format
)

# Import prompts
from agent_prompts import (
    SYSTEM_PROMPT,
    METRICS_ANALYSIS_PROMPT,
    REPORT_GENERATION_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AnalyticsAgent:
    """
    Agent for analyzing social media performance and generating
    data-driven insights and reports
    """
    
    def __init__(self, 
                model_name: str = "gpt-4o",
                system_prompt: str = SYSTEM_PROMPT,
                enable_logging: bool = True,
                platforms: Optional[List[str]] = None):
        """
        Initialize the Analytics Agent
        
        Args:
            model_name: LLM model to use
            system_prompt: System prompt for the agent
            enable_logging: Whether to enable detailed logging
            platforms: List of social media platforms to analyze
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        self.platforms = platforms or ["instagram", "twitter", "linkedin"]
        
        # Platform clients (to be initialized)
        self.platform_clients = {}
        
        # Analytics configuration
        self.report_templates = self._load_report_templates()
        self.visualization_preferences = self._load_visualization_preferences()
        
        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data/analytics", exist_ok=True)
        os.makedirs("data/reports", exist_ok=True)
        os.makedirs("data/visualizations", exist_ok=True)
        
        logger.info(f"Analytics Agent initialized for platforms: {', '.join(self.platforms)}")
    
    def _load_report_templates(self) -> Dict[str, Any]:
        """Load report templates from file"""
        try:
            with open("data/report_templates.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Report templates file not found, using defaults")
            return {
                "executive_summary": {
                    "sections": ["overview", "key_metrics", "trends", "recommendations"],
                    "max_length": 2
                },
                "comprehensive_report": {
                    "sections": ["executive_summary", "platform_analysis", "content_performance", 
                                "audience_insights", "competitor_analysis", "recommendations"],
                    "max_length": 10
                },
                "metrics_snapshot": {
                    "sections": ["key_metrics", "change_from_previous"],
                    "max_length": 1
                }
            }
    
    def _load_visualization_preferences(self) -> Dict[str, Any]:
        """Load visualization preferences from file"""
        try:
            with open("data/visualization_preferences.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Visualization preferences file not found, using defaults")
            return {
                "color_scheme": ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"],
                "default_chart_type": "line",
                "include_branding": True,
                "export_formats": ["png", "pdf"],
                "default_dimensions": [1200, 800]
            }
    
    async def initialize_platform_clients(self):
        """Initialize the social media platform clients"""
        logger.info("Initializing platform clients")
        
        for platform in self.platforms:
            try:
                if platform == "instagram":
                    from platform_clients import InstagramClient
                    api_key = os.getenv("INSTAGRAM_API_KEY")
                    api_secret = os.getenv("INSTAGRAM_API_SECRET")
                    self.platform_clients[platform] = InstagramClient(api_key, api_secret)
                    
                elif platform == "twitter":
                    from platform_clients import TwitterClient
                    api_key = os.getenv("TWITTER_API_KEY")
                    api_secret = os.getenv("TWITTER_API_SECRET")
                    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
                    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                    self.platform_clients[platform] = TwitterClient(
                        api_key, api_secret, access_token, access_token_secret
                    )
                    
                elif platform == "linkedin":
                    from platform_clients import LinkedInClient
                    client_id = os.getenv("LINKEDIN_CLIENT_ID")
                    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
                    self.platform_clients[platform] = LinkedInClient(client_id, client_secret)
                
                logger.info(f"Initialized {platform} client")
                
            except Exception as e:
                logger.error(f"Error initializing {platform} client: {str(e)}")
                # Use a mock client for demo/testing purposes
                from platform_clients import MockClient
                self.platform_clients[platform] = MockClient(platform)
                logger.info(f"Using mock client for {platform}")
    
    async def fetch_platform_data(self, 
                                 start_date: datetime,
                                 end_date: datetime,
                                 metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch analytics data from all platforms
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            metrics: List of metrics to collect (if None, collect all available)
            
        Returns:
            Dictionary of platform data
        """
        logger.info(f"Fetching platform data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        platform_data = {
            "timestamp": datetime.now().isoformat(),
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "platforms": {}
        }
        
        default_metrics = [
            "impressions", "reach", "engagement_rate", "followers", 
            "likes", "comments", "shares", "clicks", "profile_visits"
        ]
        
        metrics_to_fetch = metrics or default_metrics
        
        for platform, client in self.platform_clients.items():
            try:
                platform_metrics = await fetch_platform_metrics(
                    client=client,
                    platform=platform,
                    start_date=start_date,
                    end_date=end_date,
                    metrics=metrics_to_fetch
                )
                
                platform_data["platforms"][platform] = platform_metrics
                logger.info(f"Fetched {len(platform_metrics.get('daily_metrics', []))} days of data for {platform}")
                
            except Exception as e:
                logger.error(f"Error fetching data for {platform}: {str(e)}")
        
        # Save the raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/analytics/raw_data_{timestamp}.json", "w") as f:
                json.dump(platform_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving raw data: {str(e)}")
        
        return platform_data
    
    async def generate_analytics_report(self,
                                       platform_data: Dict[str, Any],
                                       report_type: str = "comprehensive_report",
                                       include_visualizations: bool = True) -> Dict[str, Any]:
        """
        Generate an analytics report from platform data
        
        Args:
            platform_data: Data fetched from platforms
            report_type: Type of report to generate
            include_visualizations: Whether to include visualizations
            
        Returns:
            Generated report
        """
        logger.info(f"Generating {report_type} analytics report")
        
        # Use the appropriate template
        template = self.report_templates.get(report_type, self.report_templates.get("comprehensive_report"))
        
        # Generate the report content
        report_content = await generate_performance_report(
            platform_data=platform_data,
            report_type=report_type,
            report_template=template
        )
        
        # Create report structure
        report = {
            "report_type": report_type,
            "timestamp": datetime.now().isoformat(),
            "date_range": platform_data.get("date_range", {}),
            "content": report_content
        }
        
        # Add visualizations if requested
        if include_visualizations:
            visualizations = []
            
            try:
                for platform, data in platform_data.get("platforms", {}).items():
                    # Create engagement metrics visualization
                    engagement_viz = await create_visualization(
                        data=data,
                        visualization_type="engagement_metrics",
                        title=f"{platform.capitalize()} Engagement Metrics",
                        preferences=self.visualization_preferences
                    )
                    visualizations.append(engagement_viz)
                    
                    # Create audience growth visualization
                    growth_viz = await create_visualization(
                        data=data,
                        visualization_type="audience_growth",
                        title=f"{platform.capitalize()} Audience Growth",
                        preferences=self.visualization_preferences
                    )
                    visualizations.append(growth_viz)
                    
                # Create cross-platform comparison
                if len(platform_data.get("platforms", {})) > 1:
                    comparison_viz = await create_visualization(
                        data=platform_data,
                        visualization_type="platform_comparison",
                        title="Cross-Platform Performance Comparison",
                        preferences=self.visualization_preferences
                    )
                    visualizations.append(comparison_viz)
                
                report["visualizations"] = visualizations
                logger.info(f"Created {len(visualizations)} visualizations for the report")
                
            except Exception as e:
                logger.error(f"Error creating visualizations: {str(e)}")
        
        # Save the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/reports/analytics_report_{timestamp}.json", "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
        
        return report
    
    async def analyze_audience(self, 
                              platform: str, 
                              include_demographics: bool = True) -> Dict[str, Any]:
        """
        Analyze audience demographics and behavior for a platform
        
        Args:
            platform: Platform to analyze
            include_demographics: Whether to include demographic data
            
        Returns:
            Audience analysis
        """
        logger.info(f"Analyzing audience for {platform}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        if platform not in self.platform_clients:
            error_msg = f"No client available for {platform}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        client = self.platform_clients[platform]
        
        try:
            audience_data = await analyze_audience_demographics(
                client=client,
                platform=platform,
                include_demographics=include_demographics
            )
            
            # Save the audience data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                with open(f"data/analytics/audience_analysis_{platform}_{timestamp}.json", "w") as f:
                    json.dump(audience_data, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving audience analysis: {str(e)}")
            
            return {
                "success": True,
                "platform": platform,
                "audience_data": audience_data
            }
            
        except Exception as e:
            error_msg = f"Error analyzing audience: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def identify_trends(self, 
                             platform_data: Dict[str, Any],
                             trend_type: str = "content_performance") -> Dict[str, Any]:
        """
        Identify trends in the platform data
        
        Args:
            platform_data: Data fetched from platforms
            trend_type: Type of trends to identify
            
        Returns:
            Identified trends
        """
        logger.info(f"Identifying {trend_type} trends from platform data")
        
        try:
            trends = await identify_content_trends(
                platform_data=platform_data,
                trend_type=trend_type
            )
            
            # Save the trend analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                with open(f"data/analytics/trend_analysis_{trend_type}_{timestamp}.json", "w") as f:
                    json.dump(trends, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving trend analysis: {str(e)}")
            
            return {
                "success": True,
                "trend_type": trend_type,
                "trends": trends
            }
            
        except Exception as e:
            error_msg = f"Error identifying trends: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def export_report(self, 
                           report: Dict[str, Any], 
                           export_format: str = "pdf") -> Dict[str, Any]:
        """
        Export report to specified format
        
        Args:
            report: Report to export
            export_format: Format to export to (pdf, html, etc.)
            
        Returns:
            Export result
        """
        logger.info(f"Exporting report to {export_format}")
        
        try:
            export_result = await export_report_to_format(
                report=report,
                export_format=export_format
            )
            
            logger.info(f"Report exported to {export_result.get('file_path')}")
            
            return {
                "success": True,
                "export_format": export_format,
                "file_path": export_result.get("file_path"),
                "file_size": export_result.get("file_size")
            }
            
        except Exception as e:
            error_msg = f"Error exporting report: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def parse_natural_language_command(self, message: str) -> Dict[str, Any]:
        """
        Parse a natural language message into a structured command
        
        Args:
            message: The natural language message
            
        Returns:
            A dictionary with command and parameters
        """
        message = message.lower()
        
        # Default parameters
        command_params = {
            "command": "help",
            "kwargs": {}
        }
        
        # Command mapping patterns
        command_patterns = [
            # Fetch data commands
            (r"(fetch|get|retrieve|show).*(data|metrics|stats|analytics)", "fetch_data"),
            (r"(how.*performing|performance).*(last|past|recent|today)", "fetch_data"),
            
            # Report generation commands
            (r"(create|generate|make).*(report|summary|overview)", "generate_report"),
            (r"(analyze|analysis).*(performance|data)", "generate_report"),
            
            # Audience analysis commands
            (r"(analyze|info|details).*(audience|followers|demographics)", "analyze_audience"),
            (r"who.*(following|audience)", "analyze_audience"),
            
            # Trend identification commands
            (r"(identify|find|discover).*(trends|patterns)", "identify_trends"),
            (r"what.*trending", "identify_trends"),
            
            # Export report commands
            (r"(export|save|download).*(report|data|results)", "export_report")
        ]
        
        # Try to match the message to a command
        matched_command = None
        for pattern, command in command_patterns:
            if re.search(pattern, message):
                matched_command = command
                command_params["command"] = command
                break
        
        # Extract parameters based on the command
        if matched_command == "fetch_data":
            # Extract date range
            if "last 7 days" in message or "past week" in message:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                command_params["kwargs"]["start_date"] = start_date.isoformat()
                command_params["kwargs"]["end_date"] = end_date.isoformat()
            elif "last 30 days" in message or "past month" in message or "last month" in message:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                command_params["kwargs"]["start_date"] = start_date.isoformat()
                command_params["kwargs"]["end_date"] = end_date.isoformat()
            elif "last 90 days" in message or "past 3 months" in message or "quarter" in message:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                command_params["kwargs"]["start_date"] = start_date.isoformat()
                command_params["kwargs"]["end_date"] = end_date.isoformat()
            else:
                # Default to last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                command_params["kwargs"]["start_date"] = start_date.isoformat()
                command_params["kwargs"]["end_date"] = end_date.isoformat()
                
            # Extract metrics if specified
            metrics = []
            if "engagement" in message:
                metrics.append("engagement_rate")
            if "reach" in message or "audience" in message:
                metrics.append("reach")
            if "impressions" in message or "views" in message:
                metrics.append("impressions")
            if "followers" in message:
                metrics.append("followers")
            if "likes" in message:
                metrics.append("likes")
            if "comments" in message:
                metrics.append("comments")
            if "shares" in message or "retweets" in message:
                metrics.append("shares")
                
            if metrics:
                command_params["kwargs"]["metrics"] = metrics
                
        elif matched_command == "generate_report":
            # For report generation, we need to first fetch data
            command_params["command"] = "fetch_data"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            command_params["kwargs"]["start_date"] = start_date.isoformat()
            command_params["kwargs"]["end_date"] = end_date.isoformat()
            
            # Save report type for later use
            if "summary" in message or "brief" in message:
                command_params["kwargs"]["report_type"] = "metrics_snapshot"
            elif "comprehensive" in message or "detailed" in message or "full" in message:
                command_params["kwargs"]["report_type"] = "comprehensive_report"
            else:
                command_params["kwargs"]["report_type"] = "executive_summary"
                
            # Check if visualizations are requested
            command_params["kwargs"]["include_visualizations"] = "chart" in message or "graph" in message or "visual" in message
                
        elif matched_command == "analyze_audience":
            # Extract platform if specified
            if "instagram" in message:
                command_params["kwargs"]["platform"] = "instagram"
            elif "twitter" in message:
                command_params["kwargs"]["platform"] = "twitter"
            elif "linkedin" in message:
                command_params["kwargs"]["platform"] = "linkedin"
            else:
                # Default to first platform
                command_params["kwargs"]["platform"] = self.platforms[0] if self.platforms else "instagram"
                
            # Check if demographics are requested
            command_params["kwargs"]["include_demographics"] = "demographic" in message or "age" in message or "gender" in message or "location" in message
                
        elif matched_command == "identify_trends":
            # For trend identification, we need to first fetch data
            command_params["command"] = "fetch_data"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # Use longer period for trends
            command_params["kwargs"]["start_date"] = start_date.isoformat()
            command_params["kwargs"]["end_date"] = end_date.isoformat()
            
            # Save trend type for later use
            if "content" in message:
                command_params["kwargs"]["trend_type"] = "content_performance"
            elif "audience" in message:
                command_params["kwargs"]["trend_type"] = "audience_growth"
            else:
                command_params["kwargs"]["trend_type"] = "engagement_patterns"
                
        elif matched_command == "export_report":
            # For export, we need a report first, so start with fetch_data
            command_params["command"] = "fetch_data"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            command_params["kwargs"]["start_date"] = start_date.isoformat()
            command_params["kwargs"]["end_date"] = end_date.isoformat()
            
            # Extract export format if specified
            if "pdf" in message:
                command_params["kwargs"]["export_format"] = "pdf"
            elif "excel" in message or "xlsx" in message:
                command_params["kwargs"]["export_format"] = "excel"
            elif "csv" in message:
                command_params["kwargs"]["export_format"] = "csv"
            elif "json" in message:
                command_params["kwargs"]["export_format"] = "json"
            else:
                command_params["kwargs"]["export_format"] = "pdf"  # Default to PDF
                
        # If no command was matched, provide help
        if matched_command is None:
            command_params["command"] = "help"
            
        return command_params
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a natural language message and perform the requested action
        
        Args:
            message: The natural language message
            
        Returns:
            Response dictionary with results
        """
        try:
            # Parse the message to determine command and parameters
            command_params = await self.parse_natural_language_command(message)
            command = command_params["command"]
            kwargs = command_params["kwargs"]
            
            # Handle help command
            if command == "help":
                return {
                    "message": (
                        "I'm the Analytics Agent. I can help you with social media analytics tasks such as:\n\n"
                        "- Fetching performance data (e.g., 'Show me our performance for the last 30 days')\n"
                        "- Generating reports (e.g., 'Create a comprehensive report')\n"
                        "- Analyzing audience demographics (e.g., 'Analyze our Instagram audience')\n"
                        "- Identifying trends (e.g., 'What content trends are we seeing?')\n"
                        "- Exporting reports (e.g., 'Export this report as PDF')\n\n"
                        "What would you like to know?"
                    ),
                    "status": "success"
                }
                
            # For fetch_data command
            if command == "fetch_data":
                # Call the run method with the parsed command and parameters
                result = await self.run(command, **kwargs)
                
                if result.get("success", False):
                    platform_data = result.get("platform_data", {})
                    
                    # If there's a report_type, generate a report
                    if "report_type" in kwargs:
                        report_result = await self.run(
                            "generate_report",
                            platform_data=platform_data,
                            report_type=kwargs.get("report_type", "executive_summary"),
                            include_visualizations=kwargs.get("include_visualizations", True)
                        )
                        
                        if report_result.get("success", False):
                            report = report_result.get("report", {})
                            
                            # If there's an export_format, export the report
                            if "export_format" in kwargs:
                                export_result = await self.run(
                                    "export_report",
                                    report=report,
                                    export_format=kwargs.get("export_format", "pdf")
                                )
                                
                                if export_result.get("success", False):
                                    return {
                                        "message": f"Report generated and exported to {export_result.get('file_path')}",
                                        "data": report,
                                        "status": "success"
                                    }
                                else:
                                    return {
                                        "message": f"Generated report but failed to export: {export_result.get('error')}",
                                        "data": report,
                                        "status": "warning"
                                    }
                            
                            # Return the generated report
                            return {
                                "message": self._format_report_for_chat(report),
                                "data": report,
                                "status": "success"
                            }
                        else:
                            return {
                                "message": f"Retrieved data but failed to generate report: {report_result.get('error')}",
                                "data": platform_data,
                                "status": "warning"
                            }
                    
                    # If there's a trend_type, identify trends
                    elif "trend_type" in kwargs:
                        trend_result = await self.run(
                            "identify_trends",
                            platform_data=platform_data,
                            trend_type=kwargs.get("trend_type", "engagement_patterns")
                        )
                        
                        if trend_result.get("success", False):
                            trends = trend_result.get("trends", {})
                            return {
                                "message": self._format_trends_for_chat(trends),
                                "data": trends,
                                "status": "success"
                            }
                        else:
                            return {
                                "message": f"Retrieved data but failed to identify trends: {trend_result.get('error')}",
                                "data": platform_data,
                                "status": "warning"
                            }
                    
                    # Just return the data summary
                    return {
                        "message": self._format_data_for_chat(platform_data),
                        "data": platform_data,
                        "status": "success"
                    }
                else:
                    return {
                        "message": f"Failed to retrieve data: {result.get('error', 'Unknown error')}",
                        "status": "error"
                    }
            
            # For direct commands that don't need data fetching first
            elif command == "analyze_audience":
                result = await self.run(command, **kwargs)
                
                if result.get("success", False):
                    audience_data = result.get("audience_data", {})
                    return {
                        "message": self._format_audience_for_chat(audience_data),
                        "data": audience_data,
                        "status": "success"
                    }
                else:
                    return {
                        "message": f"Failed to analyze audience: {result.get('error', 'Unknown error')}",
                        "status": "error"
                    }
            
            # Default response for unhandled commands
            return {
                "message": "I'm not sure how to handle that request. Try asking for performance data, reports, audience analysis, or trends.",
                "status": "error"
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "message": f"An error occurred while processing your request: {str(e)}",
                "status": "error"
            }
    
    def _format_data_for_chat(self, platform_data: Dict[str, Any]) -> str:
        """Format platform data into a readable chat message"""
        if not platform_data or not platform_data.get("platforms"):
            return "No data available."
            
        message_parts = [
            f"📊 **Performance Data** ({platform_data.get('date_range', {}).get('start_date', 'N/A')} to {platform_data.get('date_range', {}).get('end_date', 'N/A')})\n"
        ]
        
        for platform_name, platform_info in platform_data.get("platforms", {}).items():
            message_parts.append(f"\n**{platform_name.title()}**:")
            
            if "summary_metrics" in platform_info:
                metrics = platform_info["summary_metrics"]
                for metric_name, metric_value in metrics.items():
                    if metric_name == "engagement_rate":
                        message_parts.append(f"- {metric_name.replace('_', ' ').title()}: {metric_value}%")
                    elif metric_name == "follower_growth_rate":
                        message_parts.append(f"- {metric_name.replace('_', ' ').title()}: {metric_value}%")
                    else:
                        message_parts.append(f"- {metric_name.replace('_', ' ').title()}: {metric_value:,}")
        
        return "\n".join(message_parts)
    
    def _format_report_for_chat(self, report: Dict[str, Any]) -> str:
        """Format a report into a readable chat message"""
        if not report:
            return "No report data available."
            
        message_parts = [
            f"📑 **{report.get('title', 'Analytics Report')}**\n"
        ]
        
        # Add executive summary if available
        if "executive_summary" in report:
            message_parts.append("\n**Executive Summary**:")
            message_parts.append(report["executive_summary"])
        
        # Add key metrics if available
        if "key_metrics" in report:
            message_parts.append("\n**Key Metrics**:")
            for platform, metrics in report["key_metrics"].items():
                message_parts.append(f"\n{platform.title()}:")
                for metric_name, metric_value in metrics.items():
                    metric_display = metric_name.replace("_", " ").title()
                    if isinstance(metric_value, float) and metric_name in ["engagement_rate", "follower_growth_rate"]:
                        message_parts.append(f"- {metric_display}: {metric_value:.2f}%")
                    else:
                        message_parts.append(f"- {metric_display}: {metric_value:,}")
        
        # Add recommendations if available
        if "recommendations" in report:
            message_parts.append("\n**Recommendations**:")
            for recommendation in report["recommendations"]:
                message_parts.append(f"- {recommendation}")
        
        # If it's a comprehensive report, let the user know there's more
        if report.get("type") == "comprehensive_report":
            message_parts.append("\n\nThis is a summary of the comprehensive report. The full report includes platform analysis, content performance, audience insights, and more.")
        
        return "\n".join(message_parts)
    
    def _format_audience_for_chat(self, audience_data: Dict[str, Any]) -> str:
        """Format audience data into a readable chat message"""
        if not audience_data:
            return "No audience data available."
            
        platform = audience_data.get("platform", "Unknown")
        message_parts = [
            f"👥 **Audience Analysis for {platform.title()}**\n"
        ]
        
        # Add summary stats
        if "summary" in audience_data:
            message_parts.append("**Summary**:")
            summary = audience_data["summary"]
            for key, value in summary.items():
                message_parts.append(f"- {key.replace('_', ' ').title()}: {value:,}")
        
        # Add demographics if available
        if "demographics" in audience_data:
            message_parts.append("\n**Demographics**:")
            demographics = audience_data["demographics"]
            
            if "age_distribution" in demographics:
                message_parts.append("\nAge Distribution:")
                for age_range, percentage in demographics["age_distribution"].items():
                    message_parts.append(f"- {age_range}: {percentage:.1f}%")
            
            if "gender_distribution" in demographics:
                message_parts.append("\nGender Distribution:")
                for gender, percentage in demographics["gender_distribution"].items():
                    message_parts.append(f"- {gender.title()}: {percentage:.1f}%")
            
            if "top_locations" in demographics:
                message_parts.append("\nTop Locations:")
                for location, percentage in demographics["top_locations"].items():
                    message_parts.append(f"- {location}: {percentage:.1f}%")
        
        return "\n".join(message_parts)
    
    def _format_trends_for_chat(self, trends: Dict[str, Any]) -> str:
        """Format trend data into a readable chat message"""
        if not trends:
            return "No trend data available."
            
        trend_type = trends.get("trend_type", "Unknown")
        message_parts = [
            f"📈 **{trend_type.replace('_', ' ').title()} Trends**\n"
        ]
        
        # Add key findings
        if "key_findings" in trends:
            message_parts.append("**Key Findings**:")
            for finding in trends["key_findings"]:
                message_parts.append(f"- {finding}")
        
        # Add trend details
        if "trends" in trends:
            message_parts.append("\n**Detailed Trends**:")
            for trend in trends["trends"]:
                message_parts.append(f"\n- **{trend.get('name', 'Unnamed Trend')}**:")
                message_parts.append(f"  {trend.get('description', 'No description')}")
                if "metrics" in trend:
                    for metric_name, metric_value in trend["metrics"].items():
                        if isinstance(metric_value, float):
                            message_parts.append(f"  - {metric_name.replace('_', ' ').title()}: {metric_value:.2f}")
                        else:
                            message_parts.append(f"  - {metric_name.replace('_', ' ').title()}: {metric_value}")
        
        return "\n".join(message_parts)
    
    async def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run the Analytics Agent with a specific command
        
        Args:
            command: Command to run
            **kwargs: Additional arguments for the command
            
        Returns:
            Result of the command
        """
        logger.info(f"Running command: {command}")
        
        # Initialize platform clients if not already done
        if not self.platform_clients and command != "export_report":
            await self.initialize_platform_clients()
        
        if command == "fetch_data":
            # Parse date strings if provided
            start_date_str = kwargs.get("start_date")
            end_date_str = kwargs.get("end_date")
            
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str)
                    end_date = datetime.fromisoformat(end_date_str)
                except ValueError:
                    # Default to last 30 days if date parsing fails
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
            else:
                # Default to last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            
            metrics = kwargs.get("metrics")
            
            platform_data = await self.fetch_platform_data(
                start_date=start_date,
                end_date=end_date,
                metrics=metrics
            )
            
            return {
                "success": True,
                "platform_data": platform_data
            }
            
        elif command == "generate_report":
            platform_data = kwargs.get("platform_data")
            report_type = kwargs.get("report_type", "comprehensive_report")
            include_visualizations = kwargs.get("include_visualizations", True)
            
            if not platform_data:
                error_msg = "Missing required parameter: platform_data"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            report = await self.generate_analytics_report(
                platform_data=platform_data,
                report_type=report_type,
                include_visualizations=include_visualizations
            )
            
            return {
                "success": True,
                "report": report
            }
            
        elif command == "analyze_audience":
            platform = kwargs.get("platform")
            include_demographics = kwargs.get("include_demographics", True)
            
            if not platform:
                error_msg = "Missing required parameter: platform"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.analyze_audience(
                platform=platform,
                include_demographics=include_demographics
            )
            
            return result
            
        elif command == "identify_trends":
            platform_data = kwargs.get("platform_data")
            trend_type = kwargs.get("trend_type", "content_performance")
            
            if not platform_data:
                error_msg = "Missing required parameter: platform_data"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.identify_trends(
                platform_data=platform_data,
                trend_type=trend_type
            )
            
            return result
            
        elif command == "export_report":
            report = kwargs.get("report")
            export_format = kwargs.get("export_format", "pdf")
            
            if not report:
                error_msg = "Missing required parameter: report"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.export_report(
                report=report,
                export_format=export_format
            )
            
            return result
            
        else:
            error_msg = f"Unknown command: {command}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


async def main():
    """
    Main function for testing the Analytics Agent
    """
    agent = AnalyticsAgent()
    
    # Initialize platform clients
    await agent.initialize_platform_clients()
    
    # Fetch data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data_result = await agent.run(
        command="fetch_data",
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    if data_result.get("success", False):
        platform_data = data_result.get("platform_data", {})
        
        # Generate a comprehensive report
        report_result = await agent.run(
            command="generate_report",
            platform_data=platform_data,
            report_type="comprehensive_report",
            include_visualizations=True
        )
        
        if report_result.get("success", False):
            report = report_result.get("report", {})
            
            # Export the report to PDF
            export_result = await agent.run(
                command="export_report",
                report=report,
                export_format="pdf"
            )
            
            if export_result.get("success", False):
                print(f"Report exported to: {export_result.get('file_path')}")
            else:
                print(f"Error exporting report: {export_result.get('error')}")
        else:
            print(f"Error generating report: {report_result.get('error')}")
    else:
        print(f"Error fetching data: {data_result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main()) 