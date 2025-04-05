# Archon Agent System

A modular agent system with multiple specialized subagents for various API integrations and services.

## Features

- **Airtable Subagent:** Database operations and record management
- **Brave Search Subagent:** Web search capabilities and trending topics
- **File System Subagent:** Local file operations and data management
- **GitHub Subagent:** Repository operations and project updates
- **Slack Subagent:** Messaging and notification capabilities
- **Firecrawl Subagent:** Web crawling and data extraction
- **Twitter (X) Subagent:** Social media posting and trend analysis
- **Instagram Subagent:** Media sharing and engagement
- **Instagram Trending Subagent:** Fetches trending topics and generates content accordingly
- **Content Creator Subagent:** Generates engaging content based on trending topics
- **LinkedIn Subagent:** Professional networking and updates
- **Multi-Platform Workflow:** Automated content creation and posting across Instagram, Twitter, and LinkedIn

## Project Structure

```
archon/
├── agent.py                         # Main agent coordinator
├── instagram_trending_workflow.py   # Instagram trending content workflow
├── automatic_instagram_workflow.py  # Fully automated Instagram content workflow
├── multiplatform_workflow.py        # Multi-platform content workflow (Instagram, Twitter, LinkedIn)
├── requirements.txt                 # Project dependencies
├── .env.example                     # Example environment variables
└── subagents/                       # Subagent modules
    ├── __init__.py
    ├── airtable.py
    ├── brave_search.py
    ├── file_system.py
    ├── github.py
    ├── slack.py
    ├── firecrawl.py
    ├── twitter.py                   # Twitter/X API interactions
    ├── instagram.py
    ├── instagram_trending.py        # Instagram trending analysis
    ├── content_creator.py           # Content generation functionality
    └── linkedin.py                  # LinkedIn API interactions
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/archon.git
cd archon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

## Usage

Run the main agent:

```bash
python agent.py
```

### Multi-Platform Social Media Workflow

Run the fully automated workflow that posts to Instagram, Twitter, and LinkedIn based on trending topics:

```bash
python multiplatform_workflow.py
```

This workflow:
1. Fetches trending topics from Instagram
2. Uses the Content Creator subagent to generate engaging posts
3. Prepares media files using the File System subagent
4. Posts content to Instagram, Twitter, and LinkedIn automatically
5. Adapts content for each platform's unique format requirements
6. Saves detailed reports of the entire process

You can configure which platforms to post to:

```python
# Post to specific platforms only
workflow = MultiPlatformWorkflow(
    platforms=["instagram", "twitter"],  # Exclude LinkedIn
    auto_post=True  # Enable actual posting
)
```

### Automatic Instagram Content Workflow

Run the fully automated Instagram content workflow that handles the entire process from trend detection to posting:

```bash
python automatic_instagram_workflow.py
```

This workflow:
1. Fetches trending topics from Instagram
2. Uses the Content Creator subagent to generate engaging posts
3. Prepares media files using the File System subagent
4. Posts the content to Instagram automatically
5. Saves detailed reports of the entire process

### Instagram Trending Content Workflow

For a more focused trending topics workflow:

```bash
python instagram_trending_workflow.py
```

This workflow:
1. Fetches trending topics from Instagram
2. Analyzes the trends to extract insights
3. Generates a content strategy based on trends
4. Creates and posts content based on trending topics
5. Saves trend reports and content strategy to the data/ directory

### Using Individual Subagents

Example of using the Content Creator subagent:

```python
import asyncio
from agent import primary_agent
from subagents.content_creator import content_creator_setup

async def content_creation_example():
    # Initialize the Content Creator
    content_creator = await primary_agent.execute_tool("content_creator_setup")
    
    # Create a sample trend for demonstration
    sample_trend = {
        "title": "AI Image Generation",
        "category": "Technology",
        "hashtags": ["#AI", "#MachineLearning", "#GenerativeAI", "#TechTrends"],
        "engagement_score": 95
    }
    
    # Generate a content package
    content = await content_creator.generate_content_package(sample_trend, "instagram_post")
    
    print(f"Generated content type: {content['content_type']}")
    print(f"Caption: {content['caption']}")
    print(f"Image prompt: {content['image_prompt']}")
    print(f"Hashtags: {' '.join(content['hashtags'])}")

if __name__ == "__main__":
    asyncio.run(content_creation_example())
```

## Configuration

Each subagent requires specific API keys and credentials in your `.env` file:

```
# Instagram
INSTAGRAM_API_KEY=your_instagram_key
INSTAGRAM_API_SECRET=your_instagram_secret

# Twitter/X
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/linkedin/callback
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
```

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/my-new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 