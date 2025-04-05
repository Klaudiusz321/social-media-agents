#!/usr/bin/env python3
"""
Engagement Agent - Monitors and increases engagement on social media posts
by analyzing performance metrics and generating strategic interactions.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import random
from dotenv import load_dotenv

# Import tools
from agent_tools import (
    analyze_post_performance,
    generate_comment_responses,
    identify_top_performing_content,
    recommend_engagement_actions,
    schedule_engagement_tasks
)

# Import prompts
from agent_prompts import (
    SYSTEM_PROMPT,
    COMMENT_RESPONSE_PROMPT,
    ENGAGEMENT_STRATEGY_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/engagement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EngagementAgent:
    """
    Agent for monitoring and increasing engagement on social media posts
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4o",
                 system_prompt: str = SYSTEM_PROMPT,
                 enable_logging: bool = True,
                 platforms: Optional[List[str]] = None):
        """
        Initialize the Engagement Agent
        
        Args:
            model_name: LLM model to use
            system_prompt: System prompt for the agent
            enable_logging: Whether to enable detailed logging
            platforms: List of social media platforms to monitor
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        self.platforms = platforms or ["instagram", "twitter", "linkedin"]
        
        # Platform clients (to be initialized)
        self.platform_clients = {}
        
        # Engagement metrics tracking
        self.engagement_data = {}
        
        # Brand voice and response guidelines
        self.brand_guidelines = self._load_brand_guidelines()
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data/engagement", exist_ok=True)
        os.makedirs("data/analytics", exist_ok=True)
        
        logger.info(f"Engagement Agent initialized for platforms: {', '.join(self.platforms)}")
    
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
                "response_time_goal_minutes": 60,
                "engagement_types": ["likes", "comments", "shares", "saves"],
                "priority_engagement": "comments"
            }
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates from file"""
        try:
            with open("data/response_templates.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Response templates file not found, using defaults")
            return {
                "appreciation": [
                    "Thank you for your comment! We appreciate your support.",
                    "Thanks for sharing your thoughts with us! We value your input."
                ],
                "question": [
                    "Great question! {answer}",
                    "Thanks for asking! {answer}"
                ],
                "complaint": [
                    "We're sorry to hear about your experience. Please DM us so we can help resolve this.",
                    "We apologize for any inconvenience. Let's connect via DM to address your concerns."
                ],
                "general": [
                    "We're glad you enjoyed this post!",
                    "Thanks for engaging with our content!"
                ]
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
    
    async def analyze_post_engagement(self, post_ids: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analyze engagement metrics for posts across platforms
        
        Args:
            post_ids: Dictionary mapping platforms to lists of post IDs
            
        Returns:
            Engagement analysis results
        """
        logger.info(f"Analyzing engagement for {sum(len(ids) for ids in post_ids.values())} posts")
        
        engagement_results = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform, ids in post_ids.items():
            platform_results = []
            
            if platform not in self.platform_clients:
                logger.warning(f"No client available for {platform}, skipping")
                continue
            
            client = self.platform_clients[platform]
            
            for post_id in ids:
                try:
                    # Get post data and engagement metrics
                    post_data = await client.get_post(post_id)
                    
                    # Analyze the post performance
                    analysis = await analyze_post_performance(
                        platform=platform,
                        post_data=post_data
                    )
                    
                    platform_results.append({
                        "post_id": post_id,
                        "metrics": post_data.get("metrics", {}),
                        "analysis": analysis,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logger.info(f"Analyzed {platform} post {post_id}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {platform} post {post_id}: {str(e)}")
            
            engagement_results["platforms"][platform] = platform_results
        
        # Save engagement results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/engagement/analysis_{timestamp}.json", "w") as f:
                json.dump(engagement_results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving engagement analysis: {str(e)}")
        
        return engagement_results
    
    async def respond_to_comments(self, 
                                 platform: str, 
                                 post_id: str, 
                                 max_responses: int = 10,
                                 response_type: str = "auto") -> Dict[str, Any]:
        """
        Generate and post responses to recent comments
        
        Args:
            platform: Social media platform
            post_id: ID of the post
            max_responses: Maximum number of responses to generate
            response_type: Type of response generation (auto, template, custom)
            
        Returns:
            Response results
        """
        logger.info(f"Responding to comments on {platform} post {post_id}")
        
        if platform not in self.platform_clients:
            error_msg = f"No client available for {platform}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        client = self.platform_clients[platform]
        
        try:
            # Get recent comments
            comments = await client.get_comments(post_id, limit=max_responses)
            
            if not comments:
                logger.info(f"No comments found for {platform} post {post_id}")
                return {"success": True, "responses": 0, "message": "No comments found"}
            
            # Get post content for context
            post_data = await client.get_post(post_id)
            post_content = post_data.get("content", "")
            
            # Generate responses
            responses = await generate_comment_responses(
                platform=platform,
                post_content=post_content,
                comments=comments,
                brand_guidelines=self.brand_guidelines,
                response_templates=self.response_templates,
                response_type=response_type
            )
            
            # Post responses
            response_results = []
            for i, (comment, response) in enumerate(zip(comments, responses)):
                if i >= max_responses:
                    break
                    
                if response_type != "dry_run":
                    # Post the response
                    result = await client.post_comment_reply(
                        post_id=post_id,
                        comment_id=comment.get("id"),
                        reply_text=response.get("text")
                    )
                    
                    response_results.append({
                        "comment_id": comment.get("id"),
                        "comment_text": comment.get("text"),
                        "response_text": response.get("text"),
                        "response_type": response.get("type"),
                        "posted": result.get("success", False),
                        "response_id": result.get("id") if result.get("success", False) else None
                    })
                    
                    logger.info(f"Posted response to comment {comment.get('id')}")
                    
                    # Add a delay between responses to avoid rate limits
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                else:
                    # Just log the response without posting
                    response_results.append({
                        "comment_id": comment.get("id"),
                        "comment_text": comment.get("text"),
                        "response_text": response.get("text"),
                        "response_type": response.get("type"),
                        "posted": False,
                        "dry_run": True
                    })
                    
                    logger.info(f"Generated response for comment {comment.get('id')} (dry run)")
            
            result = {
                "success": True,
                "platform": platform,
                "post_id": post_id,
                "total_comments": len(comments),
                "responses_generated": len(responses),
                "responses_posted": sum(1 for r in response_results if r.get("posted", False)),
                "response_results": response_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save response results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                with open(f"data/engagement/responses_{platform}_{timestamp}.json", "w") as f:
                    json.dump(result, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving response results: {str(e)}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error responding to comments: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def identify_engagement_opportunities(self, 
                                              lookback_days: int = 7,
                                              min_posts: int = 5) -> Dict[str, Any]:
        """
        Identify posts with engagement opportunities
        
        Args:
            lookback_days: Number of days to look back
            min_posts: Minimum number of posts to analyze per platform
            
        Returns:
            Engagement opportunities by platform
        """
        logger.info(f"Identifying engagement opportunities (lookback: {lookback_days} days)")
        
        opportunities = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform, client in self.platform_clients.items():
            try:
                # Get recent posts
                since_date = datetime.now() - timedelta(days=lookback_days)
                posts = await client.get_recent_posts(since=since_date, limit=min_posts)
                
                if not posts:
                    logger.info(f"No recent posts found for {platform}")
                    continue
                
                # Identify top performing and underperforming posts
                performance_analysis = await identify_top_performing_content(
                    platform=platform,
                    posts=posts
                )
                
                # Get recommended actions
                recommendations = await recommend_engagement_actions(
                    platform=platform,
                    performance_analysis=performance_analysis,
                    brand_guidelines=self.brand_guidelines
                )
                
                opportunities["platforms"][platform] = {
                    "posts_analyzed": len(posts),
                    "top_performing": performance_analysis.get("top_performing", []),
                    "underperforming": performance_analysis.get("underperforming", []),
                    "recommendations": recommendations,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Identified engagement opportunities for {platform}")
                
            except Exception as e:
                logger.error(f"Error identifying opportunities for {platform}: {str(e)}")
        
        # Save opportunities
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(f"data/engagement/opportunities_{timestamp}.json", "w") as f:
                json.dump(opportunities, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving engagement opportunities: {str(e)}")
        
        return opportunities
    
    async def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run the Engagement Agent with a specific command
        
        Args:
            command: Command to run
            **kwargs: Additional arguments for the command
            
        Returns:
            Result of the command
        """
        logger.info(f"Running command: {command}")
        
        # Initialize platform clients if not already done
        if not self.platform_clients:
            await self.initialize_platform_clients()
        
        if command == "analyze_posts":
            post_ids = kwargs.get("post_ids", {})
            
            results = await self.analyze_post_engagement(post_ids)
            
            return {
                "success": True,
                "analysis": results
            }
            
        elif command == "respond_to_comments":
            platform = kwargs.get("platform")
            post_id = kwargs.get("post_id")
            max_responses = kwargs.get("max_responses", 10)
            response_type = kwargs.get("response_type", "auto")
            
            if not platform or not post_id:
                error_msg = "Missing required parameters: platform and post_id"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            results = await self.respond_to_comments(
                platform=platform,
                post_id=post_id,
                max_responses=max_responses,
                response_type=response_type
            )
            
            return results
            
        elif command == "identify_opportunities":
            lookback_days = kwargs.get("lookback_days", 7)
            min_posts = kwargs.get("min_posts", 5)
            
            opportunities = await self.identify_engagement_opportunities(
                lookback_days=lookback_days,
                min_posts=min_posts
            )
            
            return {
                "success": True,
                "opportunities": opportunities
            }
            
        elif command == "schedule_engagement":
            engagement_plan = kwargs.get("engagement_plan", {})
            
            if not engagement_plan:
                error_msg = "Missing required parameter: engagement_plan"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            schedule_result = await schedule_engagement_tasks(
                platform_clients=self.platform_clients,
                engagement_plan=engagement_plan
            )
            
            return {
                "success": True,
                "schedule": schedule_result
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
    Main function for testing the Engagement Agent
    """
    agent = EngagementAgent()
    
    # Initialize platform clients
    await agent.initialize_platform_clients()
    
    # Sample post IDs for analysis
    post_ids = {
        "instagram": ["sample_post_1", "sample_post_2"],
        "twitter": ["sample_tweet_1"],
        "linkedin": ["sample_linkedin_post_1"]
    }
    
    # Analyze post engagement
    analysis_result = await agent.run(
        command="analyze_posts",
        post_ids=post_ids
    )
    
    print(f"Analyzed {sum(len(ids) for ids in post_ids.values())} posts")
    
    # Identify engagement opportunities
    opportunities_result = await agent.run(
        command="identify_opportunities",
        lookback_days=7,
        min_posts=3
    )
    
    print(f"Identified opportunities across {len(opportunities_result.get('opportunities', {}).get('platforms', {}))} platforms")


if __name__ == "__main__":
    asyncio.run(main()) 