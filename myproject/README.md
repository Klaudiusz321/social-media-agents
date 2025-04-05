# AI Agents Platform

This project integrates multiple AI agents (Content Creator, Engagement, Analytics, and Ad Campaign Manager) into a unified platform that can coordinate specialized tasks based on natural language requests.

## Project Structure

The project is organized as follows:

```
myproject/
├── agents/
│   ├── ad_campaign_manager_agent/
│   ├── analytics_agent/
│   ├── content_creator_agent/
│   ├── engagement_agent/
│   └── primary_agent/
├── chat/
│   ├── templates/
│   └── models.py
├── static/
│   ├── css/
│   └── js/
├── myproject/
│   ├── settings.py
│   └── urls.py
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
└── .env.example
```

## Docker Deployment

### Prerequisites

- Docker and Docker Compose installed on the deployment server

### Configuration

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd myproject
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your API keys and configuration.

3. Build and start the Docker container:
   ```bash
   docker-compose up --build -d
   ```

4. Monitor the logs:
   ```bash
   docker-compose logs -f
   ```

### Access the Application

The application will be available at:
```
http://localhost:8000/chat/
```

## Usage

The AI Agent Platform provides a chat interface where users can:

1. Interact with the primary AI agent that coordinates all specialized agents
2. Request various tasks related to social media management
3. Receive intelligent responses that leverage the capabilities of specialized agents

## Architecture

- **Primary Agent**: Coordinates all specialized agents
- **Ad Campaign Manager Agent**: Creates and manages ad campaigns
- **Analytics Agent**: Analyzes performance data
- **Content Creator Agent**: Generates creative content
- **Engagement Agent**: Monitors and responds to engagement

## Development

To run the project locally without Docker:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ``` 