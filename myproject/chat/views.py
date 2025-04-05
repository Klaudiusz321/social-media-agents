import json
import asyncio
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import Conversation, Message

# Import agent configuration and factory
from agents.config import get_visible_agents, get_agent_info, is_agent_enabled
from agents.agent_factory import initialize_all_agents, run_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize agents on startup
try:
    asyncio.run(initialize_all_agents())
except Exception as e:
    logger.error(f"Failed to initialize agents: {str(e)}")

@ensure_csrf_cookie
def index(request):
    """Render the main chat interface"""
    # Get or create a conversation
    conversation_id = request.session.get('conversation_id')
    agent_id = 'primary'  # Always use primary agent
    
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        # Ensure the agent type is set to primary
        if conversation.agent_type != agent_id:
            conversation.agent_type = agent_id
            conversation.save()
    else:
        # Create a new conversation
        conversation = Conversation.objects.create(agent_type=agent_id)
        request.session['conversation_id'] = conversation.id
    
    messages = conversation.messages.all()
    
    return render(request, 'chat/index.html', {
        'conversation': conversation,
        'messages': messages
    })

@csrf_exempt
@require_POST
def send_message(request):
    """Process a message from the user"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_id = request.session.get('conversation_id')
        agent_id = 'primary'  # Always use primary agent
        
        if not is_agent_enabled(agent_id):
            return JsonResponse({
                'message': "The AI system is not available right now. Please try again later.",
                'status': 'error'
            }, status=500)
        
        if not conversation_id:
            # Create a new conversation
            conversation = Conversation.objects.create(agent_type=agent_id)
            request.session['conversation_id'] = conversation.id
        else:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            
            # Ensure the agent type is set to primary
            if conversation.agent_type != agent_id:
                conversation.agent_type = agent_id
                conversation.save()
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )
        
        # Process message with agent (using asyncio)
        response = asyncio.run(run_agent(agent_id, user_message))
        
        # Extract response message
        if isinstance(response, dict):
            if 'message' in response:
                ai_response = response['message']
            elif 'error' in response:
                ai_response = f"Error: {response['error']}"
            else:
                # For more complex responses from the agent
                ai_response = f"Response: {json.dumps(response, indent=2)}"
        else:
            # Handle case where response is not a dict
            ai_response = str(response)
        
        # Save AI response
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        
        # Prepare response
        response_data = {
            'message': ai_response,
            'timestamp': ai_message.timestamp.isoformat(),
        }
        
        # Add additional fields if present in the agent response
        if isinstance(response, dict):
            # Include which agent was used (for Primary Agent that delegates to subagents)
            if 'agent_used' in response:
                response_data['agent_used'] = response['agent_used']
            
            # Add other fields
            for key in ['status', 'actions', 'suggestions']:
                if key in response:
                    response_data[key] = response[key]
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return JsonResponse({
            'message': f"Error processing your request: {str(e)}",
            'status': 'error'
        }, status=500)

def new_conversation(request):
    """Start a new conversation"""
    agent_id = 'primary'  # Always use primary agent
    
    conversation = Conversation.objects.create(agent_type=agent_id)
    request.session['conversation_id'] = conversation.id
    
    return redirect('chat:index')

def switch_agent(request, agent_id):
    """Switch to a different agent for the current conversation"""
    # Validate agent ID
    if not is_agent_enabled(agent_id):
        return JsonResponse({
            'message': f"Agent '{agent_id}' is not available.",
            'status': 'error'
        }, status=400)
    
    conversation_id = request.session.get('conversation_id')
    
    if conversation_id:
        # Update existing conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        conversation.agent_type = agent_id
        conversation.save()
        
        # Add system message about switching agents
        agent_info = get_agent_info(agent_id)
        agent_name = agent_info.get('name', agent_id) if agent_info else agent_id
        
        Message.objects.create(
            conversation=conversation,
            content=f"Switched to {agent_name} agent.",
            is_user=False
        )
    else:
        # Create a new conversation
        conversation = Conversation.objects.create(agent_type=agent_id)
        request.session['conversation_id'] = conversation.id
    
    # If this is an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'agent_id': agent_id,
            'agent_name': agent_info.get('name', agent_id) if agent_info else agent_id
        })
    
    # Otherwise, redirect to the chat index
    return redirect('chat:index')

def list_agents(request):
    """Return a list of all available agents"""
    # Get all visible agents
    visible_agents = get_visible_agents()
    
    # Convert to a format suitable for the frontend
    agent_list = []
    for agent_id, config in visible_agents.items():
        agent_list.append({
            'id': agent_id,
            'name': config.get('name', agent_id),
            'description': config.get('description', ''),
            'icon': config.get('icon', '🤖')
        })
    
    return JsonResponse({
        'agents': agent_list
    })
