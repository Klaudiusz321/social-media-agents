"""
Agent Factory - Utility for creating and managing agent instances
"""

import importlib
import logging
import asyncio
from typing import Dict, Any, Optional, List

# Import agent configuration
from .config import (
    get_enabled_agents,
    get_agent_info,
    is_agent_enabled
)

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory class for creating and managing agent instances"""
    
    def __init__(self):
        """Initialize the agent factory"""
        self.agents = {}  # Dictionary to store agent instances
    
    async def initialize_agents(self) -> Dict[str, Any]:
        """
        Initialize all enabled agents from the configuration
        
        Returns:
            Dictionary of initialized agent instances
        """
        try:
            # Get all enabled agents from configuration
            enabled_agents = get_enabled_agents()
            
            # Initialize each enabled agent
            for agent_id, config in enabled_agents.items():
                await self.initialize_agent(agent_id, config)
            
            logger.info(f"Initialized {len(self.agents)} agents")
            return self.agents
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            return {}
    
    async def initialize_agent(self, agent_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Initialize a specific agent
        
        Args:
            agent_id: The ID of the agent to initialize
            config: Optional configuration. If None, it will be loaded from the config file.
            
        Returns:
            The initialized agent instance or None if initialization failed
        """
        try:
            # If config is not provided, get it from the configuration
            if config is None:
                config = get_agent_info(agent_id)
                
                # Check if agent is enabled
                if not config or not config.get("enabled", False):
                    logger.warning(f"Agent '{agent_id}' is disabled or not found")
                    return None
            
            # Get the class path from the configuration
            class_path = config.get("class_path")
            if not class_path:
                logger.error(f"No class_path defined for agent '{agent_id}'")
                return None
            
            # Dynamically import the agent class
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            AgentClass = getattr(module, class_name)
            
            # Extract initialization parameters from config
            init_params = {
                "model_name": config.get("model_name", "gpt-4o"),
            }
            
            # Add platforms parameter if present in config
            if "platforms" in config:
                init_params["platforms"] = config.get("platforms", [])
            
            # Initialize the agent instance
            agent = AgentClass(**init_params)
            
            # Initialize platform clients if the method exists
            if hasattr(agent, "initialize_platform_clients"):
                await agent.initialize_platform_clients()
            
            # Store the initialized agent
            self.agents[agent_id] = agent
            logger.info(f"Initialized agent: {agent_id}")
            
            return agent
        except Exception as e:
            logger.error(f"Error initializing agent '{agent_id}': {str(e)}")
            return None
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Get an initialized agent instance
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def is_agent_initialized(self, agent_id: str) -> bool:
        """
        Check if an agent is initialized
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            True if the agent is initialized, False otherwise
        """
        return agent_id in self.agents
    
    async def reload_agent(self, agent_id: str) -> Optional[Any]:
        """
        Reload an agent (reinitialize it)
        
        Args:
            agent_id: The ID of the agent to reload
            
        Returns:
            The reinitialized agent instance or None if reload failed
        """
        # Remove the agent from the dictionary if it exists
        if agent_id in self.agents:
            del self.agents[agent_id]
        
        # Reinitialize the agent
        return await self.initialize_agent(agent_id)

# Create a global instance of the agent factory
agent_factory = AgentFactory()

async def initialize_all_agents() -> Dict[str, Any]:
    """
    Initialize all enabled agents
    
    Returns:
        Dictionary of initialized agent instances
    """
    return await agent_factory.initialize_agents()

def get_agent(agent_id: str) -> Optional[Any]:
    """
    Get an initialized agent instance
    
    Args:
        agent_id: The ID of the agent
        
    Returns:
        The agent instance or None if not found
    """
    return agent_factory.get_agent(agent_id)

def is_agent_initialized(agent_id: str) -> bool:
    """
    Check if an agent is initialized
    
    Args:
        agent_id: The ID of the agent
        
    Returns:
        True if the agent is initialized, False otherwise
    """
    return agent_factory.is_agent_initialized(agent_id)

async def run_agent(agent_id: str, message: str) -> Dict[str, Any]:
    """
    Run an agent with a user message
    
    Args:
        agent_id: The ID of the agent
        message: The user message
        
    Returns:
        The agent response
    """
    try:
        # Check if agent is enabled
        if not is_agent_enabled(agent_id):
            return {
                "message": f"Agent '{agent_id}' is disabled. Please try another agent.",
                "status": "error"
            }
        
        # Get the agent instance
        agent = get_agent(agent_id)
        
        # If agent is not initialized, try to initialize it
        if agent is None:
            agent = await agent_factory.initialize_agent(agent_id)
            
            # If initialization failed, return error
            if agent is None:
                return {
                    "message": f"Agent '{agent_id}' could not be initialized.",
                    "status": "error"
                }
        
        # Check if the agent has a process_message method (for natural language processing)
        if hasattr(agent, "process_message"):
            response = await agent.process_message(message)
            return response
        
        # If no process_message method, use the standard run method
        # Run the agent
        response = await agent.run(message)
        return response
    except Exception as e:
        logger.error(f"Error running agent '{agent_id}': {str(e)}")
        return {
            "message": f"Error processing your request: {str(e)}",
            "status": "error"
        } 