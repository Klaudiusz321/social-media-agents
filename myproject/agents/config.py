"""
Agent Configuration file - Centralized settings and configuration for all agents
"""

from typing import Dict, Any, List, Optional

# Agent configuration dictionary
AGENT_CONFIG = {
    # Primary Agent (Coordinator)
    "primary": {
        "name": "Primary Agent",
        "description": "Coordinates all specialized subagents to fulfill complex requests",
        "class_path": "agents.primary_agent.agent.PrimaryAgent",
        "model_name": "gpt-4o",
        "enabled": True,
        "visible_in_ui": True,
        "icon": "🧠"
    },
    # Ad Campaign Manager Agent
    "ad_campaign": {
        "name": "Ad Campaign Manager",
        "description": "Creates and manages ad campaigns across various platforms",
        "class_path": "agents.ad_campaign_manager_agent.agent.AdCampaignManagerAgent",
        "model_name": "gpt-4o",
        "enabled": True,
        "platforms": ["facebook", "instagram", "linkedin", "twitter"],
        "visible_in_ui": True,
        "icon": "📊"
    },
    # Analytics Agent
    "analytics": {
        "name": "Analytics Agent",
        "description": "Analyzes performance data and provides insights",
        "class_path": "agents.analytics_agent.agent.AnalyticsAgent",
        "model_name": "gpt-4o",
        "enabled": True,  # Set to True now that it's ready to use
        "platforms": ["instagram", "twitter", "linkedin"],
        "visible_in_ui": True,
        "icon": "📈"
    },
    # Content Creator Agent
    "content_creator": {
        "name": "Content Creator",
        "description": "Generates creative content for social media",
        "class_path": "agents.content_creator_agent.agent.ContentCreatorAgent",
        "model_name": "gpt-4o",
        "enabled": False,
        "visible_in_ui": False,
        "icon": "✏️"
    },
    # Engagement Agent
    "engagement": {
        "name": "Engagement Agent",
        "description": "Monitors and responds to user engagement",
        "class_path": "agents.engagement_agent.agent.EngagementAgent",
        "model_name": "gpt-4o",
        "enabled": False,
        "visible_in_ui": False,
        "icon": "🔔"
    }
}

def get_enabled_agents() -> Dict[str, Dict[str, Any]]:
    """
    Returns a dictionary of enabled agents
    
    Returns:
        Dict containing all enabled agents
    """
    return {agent_id: config for agent_id, config in AGENT_CONFIG.items() 
            if config.get("enabled", False)}

def get_visible_agents() -> Dict[str, Dict[str, Any]]:
    """
    Returns a dictionary of agents that should be visible in the UI
    
    Returns:
        Dict containing all visible agents
    """
    return {agent_id: config for agent_id, config in AGENT_CONFIG.items() 
            if config.get("visible_in_ui", False) and config.get("enabled", False)}

def get_agent_info(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific agent
    
    Args:
        agent_id: The ID of the agent
        
    Returns:
        Dict with agent configuration or None if not found
    """
    return AGENT_CONFIG.get(agent_id)

def is_agent_enabled(agent_id: str) -> bool:
    """
    Check if an agent is enabled
    
    Args:
        agent_id: The ID of the agent
        
    Returns:
        True if the agent is enabled, False otherwise
    """
    agent_config = AGENT_CONFIG.get(agent_id)
    if not agent_config:
        return False
    return agent_config.get("enabled", False) 