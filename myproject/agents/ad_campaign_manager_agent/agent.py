#!/usr/bin/env python3
"""
Ad Campaign Manager Agent - Automates and optimizes social media
advertising campaigns across multiple platforms.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
from dotenv import load_dotenv

# Import tools
from agent_tools import (
    create_campaign,
    update_campaign,
    get_campaign_status,
    get_campaign_performance,
    optimize_campaign_budget,
    generate_ad_creative,
    schedule_campaign,
    pause_campaign,
    resume_campaign,
    create_audience,
    get_audience_insights,
    analyze_campaign_performance,
    export_campaign_report
)

# Import prompts
from agent_prompts import (
    SYSTEM_PROMPT,
    CAMPAIGN_CREATION_PROMPT,
    CAMPAIGN_OPTIMIZATION_PROMPT,
    AD_CREATION_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/ad_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AdCampaignManagerAgent:
    """
    Agent for managing and optimizing ad campaigns across
    multiple social media platforms
    """
    
    def __init__(self, 
                model_name: str = "gpt-4o",
                system_prompt: str = SYSTEM_PROMPT,
                enable_logging: bool = True,
                platforms: Optional[List[str]] = None):
        """
        Initialize the Ad Campaign Manager Agent
        
        Args:
            model_name: LLM model to use
            system_prompt: System prompt for the agent
            enable_logging: Whether to enable detailed logging
            platforms: List of ad platforms to manage
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        self.platforms = platforms or ["facebook", "instagram", "linkedin", "twitter"]
        
        # Platform clients (to be initialized)
        self.platform_clients = {}
        
        # Campaign configuration
        self.campaign_templates = self._load_campaign_templates()
        self.ad_creative_templates = self._load_ad_creative_templates()
        
        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data/campaigns", exist_ok=True)
        os.makedirs("data/audiences", exist_ok=True)
        os.makedirs("data/ad_creatives", exist_ok=True)
        os.makedirs("data/reports", exist_ok=True)
        
        logger.info(f"Ad Campaign Manager Agent initialized for platforms: {', '.join(self.platforms)}")
    
    def _load_campaign_templates(self) -> Dict[str, Any]:
        """Load campaign templates from file"""
        try:
            with open("data/campaign_templates.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Campaign templates file not found, using defaults")
            return {
                "awareness": {
                    "objective": "brand_awareness",
                    "budget_allocation": {
                        "facebook": 0.4,
                        "instagram": 0.4,
                        "linkedin": 0.1,
                        "twitter": 0.1
                    },
                    "duration_days": 14,
                    "audience_targeting": "broad"
                },
                "engagement": {
                    "objective": "engagement",
                    "budget_allocation": {
                        "facebook": 0.3,
                        "instagram": 0.5,
                        "linkedin": 0.1,
                        "twitter": 0.1
                    },
                    "duration_days": 7,
                    "audience_targeting": "medium"
                },
                "conversion": {
                    "objective": "conversions",
                    "budget_allocation": {
                        "facebook": 0.4,
                        "instagram": 0.3,
                        "linkedin": 0.2,
                        "twitter": 0.1
                    },
                    "duration_days": 30,
                    "audience_targeting": "specific"
                }
            }
    
    def _load_ad_creative_templates(self) -> Dict[str, Any]:
        """Load ad creative templates from file"""
        try:
            with open("data/ad_creative_templates.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Ad creative templates file not found, using defaults")
            return {
                "carousel": {
                    "num_images": 3,
                    "headline_length": 40,
                    "description_length": 125,
                    "cta": "Learn More"
                },
                "single_image": {
                    "headline_length": 40,
                    "description_length": 125,
                    "cta": "Shop Now"
                },
                "video": {
                    "duration_seconds": 15,
                    "headline_length": 40,
                    "description_length": 125,
                    "cta": "Watch More"
                }
            }
    
    async def initialize_platform_clients(self):
        """Initialize the ad platform clients"""
        logger.info("Initializing platform clients")
        
        for platform in self.platforms:
            try:
                if platform == "facebook" or platform == "instagram":
                    from platform_clients import FacebookAdsClient
                    app_id = os.getenv("FACEBOOK_APP_ID")
                    app_secret = os.getenv("FACEBOOK_APP_SECRET")
                    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
                    self.platform_clients[platform] = FacebookAdsClient(app_id, app_secret, access_token)
                    
                elif platform == "twitter":
                    from platform_clients import TwitterAdsClient
                    api_key = os.getenv("TWITTER_API_KEY")
                    api_secret = os.getenv("TWITTER_API_SECRET")
                    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
                    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                    self.platform_clients[platform] = TwitterAdsClient(
                        api_key, api_secret, access_token, access_token_secret
                    )
                    
                elif platform == "linkedin":
                    from platform_clients import LinkedInAdsClient
                    client_id = os.getenv("LINKEDIN_CLIENT_ID")
                    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
                    self.platform_clients[platform] = LinkedInAdsClient(client_id, client_secret)
                
                logger.info(f"Initialized {platform} ads client")
                
            except Exception as e:
                logger.error(f"Error initializing {platform} ads client: {str(e)}")
                # Use a mock client for demo/testing purposes
                from platform_clients import MockAdsClient
                self.platform_clients[platform] = MockAdsClient(platform)
                logger.info(f"Using mock ads client for {platform}")
    
    async def create_ad_campaign(self,
                               campaign_name: str,
                               campaign_type: str,
                               target_platforms: List[str],
                               budget: float,
                               start_date: datetime,
                               end_date: datetime,
                               objectives: Dict[str, str],
                               audience: Dict[str, Any],
                               creatives: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an ad campaign across multiple platforms
        
        Args:
            campaign_name: Name of the campaign
            campaign_type: Type of campaign (awareness, engagement, conversion)
            target_platforms: List of platforms to run the campaign on
            budget: Total budget for the campaign
            start_date: Campaign start date
            end_date: Campaign end date
            objectives: Objectives for each platform
            audience: Audience targeting parameters
            creatives: Creative assets and copy
            
        Returns:
            Dictionary with campaign creation results
        """
        logger.info(f"Creating {campaign_type} campaign: {campaign_name}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        # Get campaign template
        template = self.campaign_templates.get(campaign_type, self.campaign_templates.get("awareness"))
        
        # Calculate budget allocation
        budget_allocation = {}
        for platform in target_platforms:
            allocation_percent = template.get("budget_allocation", {}).get(platform, 1.0 / len(target_platforms))
            budget_allocation[platform] = round(budget * allocation_percent, 2)
        
        # Create campaign on each platform
        campaign_results = {
            "campaign_name": campaign_name,
            "campaign_id": f"camp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "campaign_type": campaign_type,
            "total_budget": budget,
            "budget_allocation": budget_allocation,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "platforms": {}
        }
        
        for platform in target_platforms:
            if platform not in self.platform_clients:
                logger.warning(f"No client available for {platform}, skipping")
                continue
                
            client = self.platform_clients[platform]
            objective = objectives.get(platform, template.get("objective"))
            
            try:
                result = await create_campaign(
                    client=client,
                    platform=platform,
                    campaign_name=f"{campaign_name} - {platform.capitalize()}",
                    objective=objective,
                    budget=budget_allocation[platform],
                    start_date=start_date,
                    end_date=end_date,
                    audience=audience,
                    creatives=creatives.get(platform, {})
                )
                
                campaign_results["platforms"][platform] = result
                logger.info(f"Created campaign on {platform}: {result.get('campaign_id')}")
                
            except Exception as e:
                error_msg = f"Error creating campaign on {platform}: {str(e)}"
                logger.error(error_msg)
                campaign_results["platforms"][platform] = {"error": error_msg}
        
        # Save campaign data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/campaigns/{campaign_name.lower().replace(' ', '_')}_{timestamp}.json", "w") as f:
                json.dump(campaign_results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving campaign data: {str(e)}")
        
        return campaign_results
    
    async def update_ad_campaign(self,
                               campaign_id: str,
                               updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing ad campaign
        
        Args:
            campaign_id: ID of the campaign to update
            updates: Dictionary of updates to apply
            
        Returns:
            Dictionary with update results
        """
        logger.info(f"Updating campaign: {campaign_id}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        # Load existing campaign data
        campaign_data = None
        for file in os.listdir("data/campaigns"):
            if file.endswith(".json"):
                try:
                    with open(f"data/campaigns/{file}", "r") as f:
                        data = json.load(f)
                        if data.get("campaign_id") == campaign_id:
                            campaign_data = data
                            break
                except Exception:
                    continue
        
        if not campaign_data:
            error_msg = f"Campaign not found: {campaign_id}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        update_results = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_data.get("campaign_name"),
            "update_time": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform, platform_data in campaign_data.get("platforms", {}).items():
            if platform not in self.platform_clients:
                logger.warning(f"No client available for {platform}, skipping")
                continue
                
            client = self.platform_clients[platform]
            platform_campaign_id = platform_data.get("campaign_id")
            
            if not platform_campaign_id:
                logger.warning(f"No campaign ID for {platform}, skipping")
                continue
            
            try:
                result = await update_campaign(
                    client=client,
                    platform=platform,
                    campaign_id=platform_campaign_id,
                    updates=updates.get(platform, updates)
                )
                
                update_results["platforms"][platform] = result
                logger.info(f"Updated campaign on {platform}: {platform_campaign_id}")
                
            except Exception as e:
                error_msg = f"Error updating campaign on {platform}: {str(e)}"
                logger.error(error_msg)
                update_results["platforms"][platform] = {"error": error_msg}
        
        return update_results
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get the status of an ad campaign
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary with campaign status
        """
        logger.info(f"Getting status for campaign: {campaign_id}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        # Load existing campaign data
        campaign_data = None
        for file in os.listdir("data/campaigns"):
            if file.endswith(".json"):
                try:
                    with open(f"data/campaigns/{file}", "r") as f:
                        data = json.load(f)
                        if data.get("campaign_id") == campaign_id:
                            campaign_data = data
                            break
                except Exception:
                    continue
        
        if not campaign_data:
            error_msg = f"Campaign not found: {campaign_id}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        status_results = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_data.get("campaign_name"),
            "check_time": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform, platform_data in campaign_data.get("platforms", {}).items():
            if platform not in self.platform_clients:
                logger.warning(f"No client available for {platform}, skipping")
                continue
                
            client = self.platform_clients[platform]
            platform_campaign_id = platform_data.get("campaign_id")
            
            if not platform_campaign_id:
                logger.warning(f"No campaign ID for {platform}, skipping")
                continue
            
            try:
                result = await get_campaign_status(
                    client=client,
                    platform=platform,
                    campaign_id=platform_campaign_id
                )
                
                status_results["platforms"][platform] = result
                logger.info(f"Got status for campaign on {platform}: {platform_campaign_id}")
                
            except Exception as e:
                error_msg = f"Error getting campaign status on {platform}: {str(e)}"
                logger.error(error_msg)
                status_results["platforms"][platform] = {"error": error_msg}
        
        return status_results
    
    async def analyze_campaign_performance(self,
                                        campaign_id: str) -> Dict[str, Any]:
        """
        Analyze the performance of an ad campaign
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary with performance analysis
        """
        logger.info(f"Analyzing performance for campaign: {campaign_id}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        # Get campaign status to have the latest data
        status = await self.get_campaign_status(campaign_id)
        
        if not status.get("campaign_name"):
            return status  # Return the error
        
        # Get performance data from each platform
        performance_data = {
            "campaign_id": campaign_id,
            "campaign_name": status.get("campaign_name"),
            "analysis_time": datetime.now().isoformat(),
            "platforms": {},
            "summary": {}
        }
        
        total_spend = 0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        
        for platform, platform_status in status.get("platforms", {}).items():
            if platform not in self.platform_clients:
                continue
                
            client = self.platform_clients[platform]
            platform_campaign_id = platform_status.get("campaign_id")
            
            if not platform_campaign_id:
                continue
            
            try:
                result = await get_campaign_performance(
                    client=client,
                    platform=platform,
                    campaign_id=platform_campaign_id
                )
                
                performance_data["platforms"][platform] = result
                
                # Aggregate metrics
                platform_spend = result.get("spend", 0)
                platform_impressions = result.get("impressions", 0)
                platform_clicks = result.get("clicks", 0)
                platform_conversions = result.get("conversions", 0)
                
                total_spend += platform_spend
                total_impressions += platform_impressions
                total_clicks += platform_clicks
                total_conversions += platform_conversions
                
                logger.info(f"Got performance data for {platform}: {platform_campaign_id}")
                
            except Exception as e:
                error_msg = f"Error getting campaign performance on {platform}: {str(e)}"
                logger.error(error_msg)
                performance_data["platforms"][platform] = {"error": error_msg}
        
        # Calculate summary metrics
        if total_impressions > 0:
            ctr = (total_clicks / total_impressions) * 100
        else:
            ctr = 0
            
        if total_clicks > 0:
            conversion_rate = (total_conversions / total_clicks) * 100
            cost_per_click = total_spend / total_clicks
        else:
            conversion_rate = 0
            cost_per_click = 0
            
        if total_conversions > 0:
            cost_per_conversion = total_spend / total_conversions
        else:
            cost_per_conversion = 0
        
        performance_data["summary"] = {
            "total_spend": round(total_spend, 2),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "ctr": round(ctr, 2),
            "conversion_rate": round(conversion_rate, 2),
            "cost_per_click": round(cost_per_click, 2),
            "cost_per_conversion": round(cost_per_conversion, 2)
        }
        
        # Analyze the performance
        analysis = await analyze_campaign_performance(performance_data)
        performance_data["analysis"] = analysis
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/reports/performance_{campaign_id}_{timestamp}.json", "w") as f:
                json.dump(performance_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving performance analysis: {str(e)}")
        
        return performance_data
    
    async def optimize_campaign(self,
                              campaign_id: str,
                              optimization_type: str = "budget") -> Dict[str, Any]:
        """
        Optimize an ad campaign
        
        Args:
            campaign_id: ID of the campaign
            optimization_type: Type of optimization to perform
            
        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Optimizing {optimization_type} for campaign: {campaign_id}")
        
        # Analyze campaign performance
        performance = await self.analyze_campaign_performance(campaign_id)
        
        if not performance.get("campaign_name"):
            return performance  # Return the error
        
        optimization_results = {
            "campaign_id": campaign_id,
            "campaign_name": performance.get("campaign_name"),
            "optimization_time": datetime.now().isoformat(),
            "optimization_type": optimization_type,
            "platforms": {},
            "recommendations": []
        }
        
        if optimization_type == "budget":
            # Optimize budget allocation
            try:
                budget_optimization = await optimize_campaign_budget(
                    performance_data=performance,
                    total_budget=performance.get("summary", {}).get("total_spend", 0)
                )
                
                optimization_results["budget_allocation"] = budget_optimization.get("budget_allocation", {})
                optimization_results["recommendations"] = budget_optimization.get("recommendations", [])
                
                # Apply budget updates if requested
                for platform, budget in budget_optimization.get("budget_allocation", {}).items():
                    optimization_results["platforms"][platform] = {
                        "new_budget": budget,
                        "previous_budget": performance.get("platforms", {}).get(platform, {}).get("spend", 0)
                    }
                
                logger.info(f"Budget optimization completed for campaign: {campaign_id}")
                
            except Exception as e:
                error_msg = f"Error optimizing budget: {str(e)}"
                logger.error(error_msg)
                optimization_results["error"] = error_msg
        
        # Save optimization results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/reports/optimization_{campaign_id}_{timestamp}.json", "w") as f:
                json.dump(optimization_results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving optimization results: {str(e)}")
        
        return optimization_results
    
    async def generate_ad_creatives(self,
                                  campaign_type: str,
                                  product_info: Dict[str, Any],
                                  target_platforms: List[str],
                                  creative_types: List[str]) -> Dict[str, Any]:
        """
        Generate ad creatives for multiple platforms
        
        Args:
            campaign_type: Type of campaign
            product_info: Information about the product/service
            target_platforms: List of platforms to generate creatives for
            creative_types: Types of creatives to generate
            
        Returns:
            Dictionary with generated creatives
        """
        logger.info(f"Generating ad creatives for {campaign_type} campaign")
        
        creative_results = {
            "campaign_type": campaign_type,
            "generation_time": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform in target_platforms:
            platform_results = {}
            
            for creative_type in creative_types:
                template = self.ad_creative_templates.get(creative_type, {})
                
                try:
                    creative = await generate_ad_creative(
                        platform=platform,
                        creative_type=creative_type,
                        campaign_type=campaign_type,
                        product_info=product_info,
                        template=template
                    )
                    
                    platform_results[creative_type] = creative
                    logger.info(f"Generated {creative_type} creative for {platform}")
                    
                except Exception as e:
                    error_msg = f"Error generating {creative_type} creative for {platform}: {str(e)}"
                    logger.error(error_msg)
                    platform_results[creative_type] = {"error": error_msg}
            
            creative_results["platforms"][platform] = platform_results
        
        # Save creative results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        campaign_name = product_info.get("name", "product").lower().replace(" ", "_")
        try:
            with open(f"data/ad_creatives/{campaign_name}_{timestamp}.json", "w") as f:
                json.dump(creative_results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving ad creatives: {str(e)}")
        
        return creative_results
    
    async def create_custom_audience(self,
                                   audience_name: str,
                                   audience_definition: Dict[str, Any],
                                   target_platforms: List[str]) -> Dict[str, Any]:
        """
        Create a custom audience for ad targeting
        
        Args:
            audience_name: Name of the audience
            audience_definition: Definition of the audience
            target_platforms: Platforms to create the audience on
            
        Returns:
            Dictionary with audience creation results
        """
        logger.info(f"Creating custom audience: {audience_name}")
        
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        audience_results = {
            "audience_name": audience_name,
            "audience_id": f"aud_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "creation_time": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform in target_platforms:
            if platform not in self.platform_clients:
                logger.warning(f"No client available for {platform}, skipping")
                continue
                
            client = self.platform_clients[platform]
            
            try:
                result = await create_audience(
                    client=client,
                    platform=platform,
                    audience_name=f"{audience_name} - {platform.capitalize()}",
                    audience_definition=audience_definition
                )
                
                audience_results["platforms"][platform] = result
                logger.info(f"Created audience on {platform}: {result.get('audience_id')}")
                
            except Exception as e:
                error_msg = f"Error creating audience on {platform}: {str(e)}"
                logger.error(error_msg)
                audience_results["platforms"][platform] = {"error": error_msg}
        
        # Save audience data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/audiences/{audience_name.lower().replace(' ', '_')}_{timestamp}.json", "w") as f:
                json.dump(audience_results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving audience data: {str(e)}")
        
        return audience_results
    
    async def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run the Ad Campaign Manager Agent with a specific command
        
        Args:
            command: Command to run
            **kwargs: Additional arguments for the command
            
        Returns:
            Result of the command
        """
        logger.info(f"Running command: {command}")
        
        # Initialize platform clients if not already done
        if not self.platform_clients and command not in ["generate_creatives", "export_report"]:
            await self.initialize_platform_clients()
        
        if command == "create_campaign":
            campaign_name = kwargs.get("campaign_name")
            campaign_type = kwargs.get("campaign_type", "awareness")
            target_platforms = kwargs.get("target_platforms", self.platforms)
            budget = kwargs.get("budget", 1000)
            start_date_str = kwargs.get("start_date")
            end_date_str = kwargs.get("end_date")
            objectives = kwargs.get("objectives", {})
            audience = kwargs.get("audience", {})
            creatives = kwargs.get("creatives", {})
            
            # Parse dates if provided as strings
            if start_date_str and isinstance(start_date_str, str):
                start_date = datetime.fromisoformat(start_date_str)
            else:
                start_date = datetime.now() + timedelta(days=1)
                
            if end_date_str and isinstance(end_date_str, str):
                end_date = datetime.fromisoformat(end_date_str)
            else:
                template = self.campaign_templates.get(campaign_type, {})
                duration = template.get("duration_days", 14)
                end_date = start_date + timedelta(days=duration)
            
            if not campaign_name:
                error_msg = "Missing required parameter: campaign_name"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.create_ad_campaign(
                campaign_name=campaign_name,
                campaign_type=campaign_type,
                target_platforms=target_platforms,
                budget=budget,
                start_date=start_date,
                end_date=end_date,
                objectives=objectives,
                audience=audience,
                creatives=creatives
            )
            
            return {
                "success": True,
                "campaign": result
            }
            
        elif command == "update_campaign":
            campaign_id = kwargs.get("campaign_id")
            updates = kwargs.get("updates", {})
            
            if not campaign_id:
                error_msg = "Missing required parameter: campaign_id"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            if not updates:
                error_msg = "Missing required parameter: updates"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.update_ad_campaign(
                campaign_id=campaign_id,
                updates=updates
            )
            
            return {
                "success": "error" not in result,
                "update_result": result
            }
            
        elif command == "get_campaign_status":
            campaign_id = kwargs.get("campaign_id")
            
            if not campaign_id:
                error_msg = "Missing required parameter: campaign_id"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.get_campaign_status(
                campaign_id=campaign_id
            )
            
            return {
                "success": "error" not in result,
                "status": result
            }
            
        elif command == "analyze_performance":
            campaign_id = kwargs.get("campaign_id")
            
            if not campaign_id:
                error_msg = "Missing required parameter: campaign_id"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.analyze_campaign_performance(
                campaign_id=campaign_id
            )
            
            return {
                "success": "error" not in result,
                "performance": result
            }
            
        elif command == "optimize_campaign":
            campaign_id = kwargs.get("campaign_id")
            optimization_type = kwargs.get("optimization_type", "budget")
            
            if not campaign_id:
                error_msg = "Missing required parameter: campaign_id"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.optimize_campaign(
                campaign_id=campaign_id,
                optimization_type=optimization_type
            )
            
            return {
                "success": "error" not in result,
                "optimization": result
            }
            
        elif command == "generate_creatives":
            campaign_type = kwargs.get("campaign_type", "awareness")
            product_info = kwargs.get("product_info", {})
            target_platforms = kwargs.get("target_platforms", self.platforms)
            creative_types = kwargs.get("creative_types", ["single_image", "carousel"])
            
            if not product_info:
                error_msg = "Missing required parameter: product_info"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.generate_ad_creatives(
                campaign_type=campaign_type,
                product_info=product_info,
                target_platforms=target_platforms,
                creative_types=creative_types
            )
            
            return {
                "success": True,
                "creatives": result
            }
            
        elif command == "create_audience":
            audience_name = kwargs.get("audience_name")
            audience_definition = kwargs.get("audience_definition", {})
            target_platforms = kwargs.get("target_platforms", self.platforms)
            
            if not audience_name:
                error_msg = "Missing required parameter: audience_name"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            if not audience_definition:
                error_msg = "Missing required parameter: audience_definition"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = await self.create_custom_audience(
                audience_name=audience_name,
                audience_definition=audience_definition,
                target_platforms=target_platforms
            )
            
            return {
                "success": True,
                "audience": result
            }
            
        elif command == "export_report":
            campaign_id = kwargs.get("campaign_id")
            report_type = kwargs.get("report_type", "performance")
            export_format = kwargs.get("export_format", "pdf")
            
            if not campaign_id:
                error_msg = "Missing required parameter: campaign_id"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # First get the performance data
            performance = await self.analyze_campaign_performance(campaign_id)
            
            if "error" in performance:
                return {"success": False, "error": performance.get("error")}
            
            try:
                result = await export_campaign_report(
                    performance_data=performance,
                    report_type=report_type,
                    export_format=export_format
                )
                
                return {
                    "success": True,
                    "report": result
                }
                
            except Exception as e:
                error_msg = f"Error exporting report: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
        else:
            error_msg = f"Unknown command: {command}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


async def main():
    """
    Main function for testing the Ad Campaign Manager Agent
    """
    agent = AdCampaignManagerAgent()
    
    # Initialize platform clients
    await agent.initialize_platform_clients()
    
    # Test creating a campaign
    campaign_result = await agent.run(
        command="create_campaign",
        campaign_name="Test Summer Sale Campaign",
        campaign_type="conversion",
        target_platforms=["facebook", "instagram"],
        budget=1000,
        objectives={"facebook": "conversions", "instagram": "conversions"},
        audience={
            "interests": ["fashion", "shopping"],
            "age_range": [25, 45],
            "gender": ["female"],
            "locations": ["US", "CA"]
        },
        creatives={
            "facebook": {
                "type": "single_image",
                "headline": "Summer Sale - Up to 50% Off",
                "description": "Shop our summer collection with exclusive discounts up to 50% off. Limited time only!",
                "cta": "Shop Now"
            },
            "instagram": {
                "type": "carousel",
                "headlines": ["Summer Sale", "Exclusive Deals", "Limited Time"],
                "description": "Up to 50% off on our summer collection!",
                "cta": "Shop Now"
            }
        }
    )
    
    if campaign_result.get("success", False):
        campaign_id = campaign_result.get("campaign", {}).get("campaign_id")
        print(f"Created campaign with ID: {campaign_id}")
        
        # Test getting campaign status
        status_result = await agent.run(
            command="get_campaign_status",
            campaign_id=campaign_id
        )
        
        if status_result.get("success", False):
            print("Campaign status retrieved successfully")
            
            # Test analyzing campaign performance
            performance_result = await agent.run(
                command="analyze_performance",
                campaign_id=campaign_id
            )
            
            if performance_result.get("success", False):
                print("Campaign performance analyzed successfully")
                
                # Test optimizing campaign
                optimization_result = await agent.run(
                    command="optimize_campaign",
                    campaign_id=campaign_id
                )
                
                if optimization_result.get("success", False):
                    print("Campaign optimized successfully")
                else:
                    print(f"Error optimizing campaign: {optimization_result.get('error')}")
            else:
                print(f"Error analyzing performance: {performance_result.get('error')}")
        else:
            print(f"Error getting status: {status_result.get('error')}")
    else:
        print(f"Error creating campaign: {campaign_result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main()) 