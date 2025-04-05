# Primary Agent

The Primary Agent serves as the coordinator for all specialized subagents in the system. It analyzes user requests and delegates tasks to the appropriate specialized agents, then consolidates their responses.

## Features

- Automated task routing to the most appropriate subagent
- Coordination of multiple subagents for complex tasks
- Centralized error handling and response formatting
- Unified interface for accessing all agent capabilities

## Supported Subagents

The Primary Agent can coordinate with the following specialized agents:

1. **Ad Campaign Manager Agent**: Creates and manages ad campaigns across various platforms
2. **Analytics Agent**: Analyzes performance data and provides insights
3. **Content Creator Agent**: Generates creative content for social media
4. **Engagement Agent**: Monitors and responds to user engagement

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy the `.env.example` file to `.env` and fill in your API keys and other configuration values:
   ```
   cp .env.example .env
   ```

## Usage

The Primary Agent can be used in two ways:

### 1. Direct message processing

```python
from agents.primary_agent import PrimaryAgent

async def example():
    primary_agent = PrimaryAgent()
    
    # Initialize the agent stack
    async with await primary_agent.initialize_stack() as stack:
        # Process a user message
        response = await primary_agent.process_message("Generate an analytics report for our Instagram account")
        print(response)
```

### 2. Using specific subagent tools

```python
from agents.primary_agent import PrimaryAgent

async def example():
    primary_agent = PrimaryAgent()
    
    # Initialize the agent stack
    async with await primary_agent.initialize_stack() as stack:
        # Use a specific subagent
        response = await primary_agent.run_analytics_agent("Generate a report on our Instagram engagement for the past month")
        print(response)
```

## Environment Variables

The Primary Agent uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: The model to use (default: gpt-4o)
- Various API keys for the different platforms (see .env.example for details)

## MCP Server Configuration

In a production environment, the Primary Agent would initialize MCP servers for each subagent using the AsyncExitStack pattern. This ensures that resources are properly managed and cleaned up when the agent is done.

## Error Handling

The Primary Agent includes comprehensive error handling to ensure graceful degradation when subagents fail. If a subagent is unavailable, the Primary Agent will attempt to use an alternative agent or provide a helpful error message. 