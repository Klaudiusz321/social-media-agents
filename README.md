# AI Trend Scanner & Content Creator

A modular system for monitoring trending topics in astronomy, physics, and space technology, generating optimized social media content, and scheduling posts at optimal times.

## Features

### TrendScannerAgent
- Monitors social media and news sources for trending topics in astronomy, physics, and space science
- Generates comprehensive trend reports in Markdown format
- Customizable monitoring parameters and sources
- Modular design for easy extension and updates

### ContentCreatorAgent
- Generates platform-specific content for Twitter, Instagram, and LinkedIn
- Integrates with OpenAI for text generation
- Integrates with Stability AI for image generation
- Ensures content follows brand guidelines
- Content moderation to ensure appropriateness
- Platform-specific formatting optimization

### SchedulerAgent
- Schedules social media posts at optimal times for maximum engagement
- Platform-specific posting strategies (Twitter, Instagram, LinkedIn)
- Handles authentication and API interactions with social platforms
- Supports dry-run mode for testing without actual posting
- Robust error handling and retry mechanisms
- Customizable time zones and scheduling rules

### Orchestrator
- Coordinates all agents into a seamless automated workflow
- Manages the timing and execution of the full pipeline
- Maintains a content pool for efficient content distribution
- Supports human review of content before posting
- Configurable interval settings for trend scanning and content creation
- Can run as a one-time process or a continuous daemon

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-agents.git
cd ai-agents
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file with all required API keys
python api_setup.py --save-report
```

Alternatively, you can create the `.env` file manually using this template:
```
# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Stability AI API
STABILITY_API_KEY=your_stability_api_key

# Twitter/X API
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret

# Instagram Credentials
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
```

5. Verify API connections:
```bash
python api_setup.py
```

## Usage

### API Setup and Validation

```bash
python api_setup.py
```

This utility will:
1. Validate all configured API connections
2. Generate a summary report of which APIs are correctly configured
3. Identify any missing or invalid credentials

Additional options:
```bash
python api_setup.py --test-openai --prompt "Write a tweet about space" --save-report
```

Available options:
- `--env-file`, `-e`: Path to custom .env file
- `--test-openai`, `-t`: Test OpenAI API with a sample prompt
- `--prompt`, `-p`: Custom prompt for OpenAI test
- `--save-report`, `-s`: Save validation report to file
- `--report-file`, `-r`: Custom path for validation report

### Running the Trend Scanner

```bash
python run_trend_scanner.py
```

This will:
1. Monitor sources for trending topics
2. Generate a trend report
3. Save the report to the `reports` directory

### Running the Content Creator

```bash
python run_content_creator.py
```

This will:
1. Get trending topics from the TrendScannerAgent
2. Generate platform-specific content for each trend
3. Save the generated content to the `generated_content` directory

### Running the Complete Pipeline with Scheduler

```bash
python demos/scheduler_demo.py
```

This will:
1. Scan for trends using the TrendScannerAgent
2. Generate content with the ContentCreatorAgent
3. Schedule and post content at optimal times using the SchedulerAgent

### Running the Full Orchestrator

```bash
python orchestrator.py
```

This will:
1. Initialize all agents (TrendScannerAgent, ContentCreatorAgent, SchedulerAgent)
2. Run the complete pipeline once, from trend scanning to content scheduling
3. Exit after completion

To run as a continuous service:

```bash
python orchestrator.py --daemon
```

This will:
1. Start the orchestrator as a background service
2. Run the full pipeline immediately and schedule future runs
3. Continue running until manually stopped (Ctrl+C)

### Command Line Options

#### Content Creator Options:
```bash
python run_content_creator.py --platforms twitter instagram --disable-image-generation
```

Available options:
- `--platforms`: Specify which platforms to generate content for (default: all)
- `--brand-guidelines`: Path to custom brand guidelines JSON file
- `--product-info`: Path to custom product info JSON file
- `--output-dir`: Directory to save generated content
- `--disable-image-generation`: Skip image generation

#### Scheduler Demo Options:
```bash
python demos/scheduler_demo.py --platforms twitter linkedin --dry-run --time-zone "Europe/London"
```

Available options:
- `--keywords`: Keywords to search for trends
- `--platforms`: Platforms to create and schedule content for
- `--brand-file`: Path to brand guidelines file
- `--time-zone`: Time zone for scheduling posts
- `--dry-run`: Simulate posting without actually sending to APIs
- `--skip-trend-scan`: Skip trend scanning and use existing report

#### Orchestrator Options:
```bash
python orchestrator.py --platforms twitter linkedin --dry-run --human-review --time-zone "Europe/London" --daemon
```

Available options:
- `--keywords`, `-k`: Keywords to search for trends (default: astronomy, physics, space)
- `--platforms`, `-p`: Platforms to create content for (default: all)
- `--brand-file`, `-b`: Path to brand guidelines file
- `--time-zone`, `-t`: Time zone for scheduling posts (default: America/New_York)
- `--dry-run`, `-d`: Simulate posting without actually sending to APIs
- `--human-review`, `-r`: Enable human review of content before posting
- `--trend-interval`: Hours between trend scans (default: 4)
- `--content-interval`: Hours between content creation cycles (default: 24)
- `--daemon`: Run as a background service with scheduled tasks
- `--max-twitter`: Maximum Twitter posts per day (default: 5)
- `--max-instagram`: Maximum Instagram posts per day (default: 2)
- `--max-linkedin`: Maximum LinkedIn posts per day (default: 1)

## Project Structure

```
ai-agents/
├── agents/
│   ├── trend_scanner/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── source_analyzer.py
│   │   └── ...
│   ├── content_creator/
│   │   ├── __init__.py
│   │   ├── content_creator_agent.py
│   │   ├── text_generator.py
│   │   ├── image_generator.py
│   │   ├── platform_formatter.py
│   │   ├── content_moderator.py
│   │   ├── brand_guidelines_manager.py
│   │   └── ...
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── scheduler_agent.py
│   │   ├── post_scheduler.py
│   │   ├── scheduler.mdc
│   │   ├── platform_posters/
│   │   │   ├── __init__.py
│   │   │   ├── twitter_poster.py
│   │   │   ├── instagram_poster.py
│   │   │   ├── linkedin_poster.py
│   │   │   └── ...
├── demos/
│   ├── scheduler_demo.py
│   └── ...
├── orchestrator.py
├── api_setup.py
├── run_trend_scanner.py
├── run_content_creator.py
├── requirements.txt
├── .env
└── README.md
```

## Customization

### Brand Guidelines

Create a custom brand guidelines JSON file to specify your brand's voice, content requirements, prohibited content, and platform-specific guidelines:

```json
{
  "brand_name": "Your Brand",
  "voice": {
    "description": "Your brand voice description",
    "traits": ["Trait 1", "Trait 2"]
  },
  "content_requirements": ["Requirement 1", "Requirement 2"],
  "prohibited_content": ["Prohibited 1", "Prohibited 2"],
  "visual_style": {
    "description": "Your visual style description",
    "colors": ["#123456", "#789ABC"]
  },
  "platforms": {
    "twitter": {
      "tone": "Platform-specific tone guidance",
      "hashtags": ["BrandHashtag1", "BrandHashtag2"]
    },
    "instagram": {
      "tone": "Platform-specific tone guidance",
      "hashtags": ["BrandHashtag1", "BrandHashtag2"]
    },
    "linkedin": {
      "tone": "Platform-specific tone guidance",
      "hashtags": ["BrandHashtag1", "BrandHashtag2"]
    }
  }
}
```

Then run with:
```bash
python run_content_creator.py --brand-guidelines path/to/brand_guidelines.json
```

### API Configuration

The system supports multiple API integration options:

1. **Text Generation**: Uses OpenAI GPT-4 or GPT-3.5-turbo with configurable parameters like temperature and max_tokens
2. **Image Generation**: Uses Stability AI's Stable Diffusion API or optionally DALL-E
3. **Social Platforms**:
   - Twitter/X: Supports both v1.1 and v2 endpoints via Tweepy
   - Instagram: Supports both Graph API (for business accounts) and instagrapi (for personal accounts)
   - LinkedIn: Uses LinkedIn Marketing API with UGC posts

For third-party integrations, the system also supports:
- Ayrshare API for unified social posting
- AWS S3 for image storage

Edit the `.env` file to configure these options or use the interactive setup:
```bash
python api_setup.py
```

### Scheduling Rules

The scheduler follows the guidelines defined in `agents/scheduler/scheduler.mdc`. You can modify this file to adjust:

- Optimal posting times for each platform
- Frequency limitations
- Cross-platform coordination rules
- Error handling behavior
- Compliance requirements

### Orchestration Configuration

The orchestrator can be customized in several ways:

1. **Time Intervals**: Adjust how often trend scanning and content creation runs
2. **Post Frequency**: Control the maximum number of posts per day for each platform
3. **Human Review**: Enable a review step to approve content before posting
4. **Dry Run Mode**: Test the pipeline without actually posting to social media

Edit the values in `orchestrator.py` or pass them as command-line arguments:

```bash
python orchestrator.py --trend-interval 6 --content-interval 12 --max-twitter 3
```

## Requirements

- Python 3.8+
- OpenAI API key (for text generation)
- Stability AI API key (for image generation)
- Twitter/X API credentials (for posting to Twitter)
- Instagram credentials (for posting to Instagram)
- LinkedIn API credentials (for posting to LinkedIn)
- schedule package (for orchestrator scheduling)
- python-dotenv (for environment variable management)

## License

MIT License 