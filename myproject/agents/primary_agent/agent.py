#!/usr/bin/env python3
"""
Primary Agent - Coordinates all subagents in the system
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import AsyncExitStack
from dotenv import load_dotenv

# Import agent factory components
from agents.agent_factory import get_agent
from agents.config import get_enabled_agents, get_agent_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/primary_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Agent system prompt
SYSTEM_PROMPT = """
You are the Primary Agent that coordinates all specialized subagents in the system.
Your role is to analyze user requests and delegate tasks to the appropriate specialized agents:

1. Ad Campaign Manager Agent: For creating and managing ad campaigns across platforms
2. Analytics Agent: For analyzing performance data and generating insights
3. Content Creator Agent: For generating creative content for social media
4. Engagement Agent: For monitoring and responding to user engagement

You should determine which agent(s) to use based on the user's request and coordinate their outputs
to provide a comprehensive response.
"""

class PrimaryAgent:
    """
    Primary Agent that coordinates all subagents in the system
    """
    
    def __init__(self, 
                model_name: str = "gpt-4o",
                system_prompt: str = SYSTEM_PROMPT,
                enable_logging: bool = True):
        """
        Initialize the Primary Agent
        
        Args:
            model_name: LLM model to use
            system_prompt: System prompt for the agent
            enable_logging: Whether to enable detailed logging
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        
        # Get enabled agents
        self.enabled_agents = get_enabled_agents()
        
        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        
        logger.info("Primary Agent initialized")
    
    async def initialize_stack(self):
        """
        Initialize all subagents using AsyncExitStack
        
        Returns:
            AsyncExitStack with all subagents initialized
        """
        stack = AsyncExitStack()
        
        # For each enabled agent, add to the stack
        for agent_id, config in self.enabled_agents.items():
            if agent_id != "primary":  # Don't initialize self
                try:
                    agent = get_agent(agent_id)
                    if agent:
                        # In a real implementation with MCP servers, you would do something like:
                        # await stack.enter_async_context(agent.start_mcp_server())
                        # But for our current setup, we just make sure the agent is initialized
                        logger.info(f"Added agent '{agent_id}' to the stack")
                except Exception as e:
                    logger.error(f"Error adding agent '{agent_id}' to stack: {str(e)}")
        
        logger.info("All subagents initialized in AsyncExitStack")
        return stack
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and coordinate subagents to respond
        
        Args:
            message: User message
            
        Returns:
            Response from appropriate subagent(s)
        """
        logger.info(f"Processing message: {message[:50]}...")
        
        # Determine which agent(s) to use based on the message
        agent_id = self._determine_best_agent(message)
        
        # Get the appropriate agent
        agent = get_agent(agent_id)
        
        if not agent:
            return {
                "message": f"Sorry, the {agent_id} agent is not available right now.",
                "status": "error"
            }
        
        try:
            # Process the message with the selected agent
            if hasattr(agent, "process_message"):
                response = await agent.process_message(message)
            else:
                response = await agent.run(message)
                
            # Add metadata about which agent handled the request
            agent_info = get_agent_info(agent_id)
            if isinstance(response, dict):
                response["agent_used"] = {
                    "id": agent_id,
                    "name": agent_info.get("name", agent_id)
                }
            else:
                response = {
                    "message": response,
                    "agent_used": {
                        "id": agent_id,
                        "name": agent_info.get("name", agent_id)
                    }
                }
                
            return response
            
        except Exception as e:
            logger.error(f"Error processing message with {agent_id} agent: {str(e)}")
            return {
                "message": f"Sorry, there was an error processing your request: {str(e)}",
                "status": "error"
            }
    
    def _determine_best_agent(self, message: str) -> str:
        """
        Determine which agent is best suited for handling the message
        
        Args:
            message: User message
            
        Returns:
            ID of the most appropriate agent
        """
        # Simple keyword-based routing for demonstration
        message = message.lower()
        
        if any(keyword in message for keyword in ["ad", "campaign", "advertise"]):
            return "ad_campaign"
        elif any(keyword in message for keyword in ["analytics", "data", "report", "stats", "performance"]):
            return "analytics"
        elif any(keyword in message for keyword in ["create", "content", "write", "post"]):
            # Note: This would use content_creator if enabled
            return "ad_campaign"  # Fallback if content_creator is disabled
        elif any(keyword in message for keyword in ["engage", "respond", "comment", "message"]):
            # Note: This would use engagement if enabled
            return "ad_campaign"  # Fallback if engagement is disabled
        else:
            # Default to ad_campaign as it's the most general-purpose agent
            return "ad_campaign"
    
    # Tool functions for the primary agent to coordinate subagents
    
    async def run_ad_campaign_agent(self, command: str) -> Dict[str, Any]:
        """
        Run the Ad Campaign Manager Agent
        
        Use this tool when the user wants to create, manage, or optimize advertising campaigns
        across social media platforms like Facebook, Instagram, LinkedIn, and Twitter.
        
        Args:
            command: Command to run on the agent
            
        Returns:
            Response from the agent
        """
        agent = get_agent("ad_campaign")
        
        if not agent:
            return {
                "message": "The Ad Campaign Manager Agent is not available right now.",
                "status": "error"
            }
            
        try:
            if hasattr(agent, "process_message"):
                return await agent.process_message(command)
            else:
                return await agent.run(command)
        except Exception as e:
            logger.error(f"Error running Ad Campaign Manager Agent: {str(e)}")
            return {
                "message": f"Error running Ad Campaign Manager Agent: {str(e)}",
                "status": "error"
            }
    
    async def run_analytics_agent(self, command: str) -> Dict[str, Any]:
        """
        Run the Analytics Agent
        
        Use this tool when the user wants to analyze performance data, generate insights,
        create reports, or visualize metrics from Instagram, Twitter, or LinkedIn.
        
        Args:
            command: Command to run on the agent
            
        Returns:
            Response from the agent
        """
        agent = get_agent("analytics")
        
        if not agent:
            return {
                "message": "The Analytics Agent is not available right now.",
                "status": "error"
            }
            
        try:
            if hasattr(agent, "process_message"):
                return await agent.process_message(command)
            else:
                return await agent.run(command)
        except Exception as e:
            logger.error(f"Error running Analytics Agent: {str(e)}")
            return {
                "message": f"Error running Analytics Agent: {str(e)}",
                "status": "error"
            }
    
    async def run_content_creator_agent(self, command: str) -> Dict[str, Any]:
        """
        Run the Content Creator Agent
        
        Use this tool when the user wants to generate creative content for social media posts,
        captions, hashtags, or other creative writing tasks.
        
        Args:
            command: Command to run on the agent
            
        Returns:
            Response from the agent
        """
        agent = get_agent("content_creator")
        
        if not agent:
            return {
                "message": "The Content Creator Agent is not available right now.",
                "status": "error"
            }
            
        try:
            if hasattr(agent, "process_message"):
                return await agent.process_message(command)
            else:
                return await agent.run(command)
        except Exception as e:
            logger.error(f"Error running Content Creator Agent: {str(e)}")
            return {
                "message": f"Error running Content Creator Agent: {str(e)}",
                "status": "error"
            }
    
    async def run_engagement_agent(self, command: str) -> Dict[str, Any]:
        """
        Run the Engagement Agent
        
        Use this tool when the user wants to monitor or respond to social media engagement,
        handle comments, or manage direct messages across platforms.
        
        Args:
            command: Command to run on the agent
            
        Returns:
            Response from the agent
        """
        agent = get_agent("engagement")
        
        if not agent:
            return {
                "message": "The Engagement Agent is not available right now.",
                "status": "error"
            }
            
        try:
            if hasattr(agent, "process_message"):
                return await agent.process_message(command)
            else:
                return await agent.run(command)
        except Exception as e:
            logger.error(f"Error running Engagement Agent: {str(e)}")
            return {
                "message": f"Error running Engagement Agent: {str(e)}",
                "status": "error"
            }
    
    async def run(self, command: str) -> Dict[str, Any]:
        """
        Main run method for the Primary Agent
        
        Args:
            command: Command/message to process
            
        Returns:
            Response from the appropriate subagent(s)
        """
        return await self.process_message(command)

# Example usage
async def main():
    """Test the Primary Agent"""
    primary_agent = PrimaryAgent()
    
    # Initialize all subagents using AsyncExitStack
    async with await primary_agent.initialize_stack() as stack:
        # Process a message
        response = await primary_agent.process_message("Generate an analytics report for our Instagram account")
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main()) 