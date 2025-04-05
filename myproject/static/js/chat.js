/**
 * Chat interface functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatContent = document.getElementById('chat-content');
    const sendingIndicator = document.getElementById('sending-indicator');
    
    // Scroll to bottom of chat on load
    scrollToBottom();
    
    // Handle message submission
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to UI immediately
        addMessage(message, true);
        
        // Clear input
        messageInput.value = '';
        
        // Show sending indicator
        sendingIndicator.style.display = 'flex';
        
        // Send message to server (always using primary agent)
        fetch('/chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide sending indicator
            sendingIndicator.style.display = 'none';
            
            // Add AI response to UI with subagent info if available
            addMessage(data.message, false, data.agent_used);
            
            // Handle any additional actions from the response
            if (data.actions) {
                handleActions(data.actions);
            }
            
            // Handle any suggestions from the response
            if (data.suggestions) {
                showSuggestions(data.suggestions);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            sendingIndicator.style.display = 'none';
            addMessage('Sorry, there was an error processing your message. Please try again.', false);
        });
    });
    
    // Allow pressing Enter to send message (Shift+Enter for new line)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });
    
    /**
     * Add a message to the chat UI
     */
    function addMessage(content, isUser, agentInfo = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        
        // Add subagent class if from a specific subagent
        if (!isUser && agentInfo && agentInfo.id && agentInfo.id !== 'primary') {
            messageDiv.classList.add('subagent-message');
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.innerText = content;
        
        const timeSpan = document.createElement('span');
        timeSpan.classList.add('message-time');
        const now = new Date();
        
        let senderText = isUser ? 'You' : 'AI';
        
        // Add subagent info if provided and this is not a user message
        if (!isUser && agentInfo && agentInfo.name && agentInfo.id !== 'primary') {
            const subagentText = `AI (${agentInfo.name})`;
            senderText = subagentText;
        }
        
        timeSpan.innerText = `${senderText} • ${now.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        })}`;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeSpan);
        
        chatContent.appendChild(messageDiv);
        
        // Apply markdown formatting
        applyMarkdownFormatting(contentDiv);
        
        scrollToBottom();
    }
    
    /**
     * Scroll to the bottom of the chat
     */
    function scrollToBottom() {
        chatContent.scrollTop = chatContent.scrollHeight;
    }
    
    /**
     * Apply markdown-like formatting to message content
     */
    function applyMarkdownFormatting(contentElement) {
        let html = contentElement.innerHTML;
        
        // Bold (**text**)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic (_text_)
        html = html.replace(/\_(.*?)\_/g, '<em>$1</em>');
        
        // Code (`code`)
        html = html.replace(/\`(.*?)\`/g, '<code>$1</code>');
        
        // Lists
        html = html.replace(/^\- (.*?)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
        
        // Replace newlines with <br> tags
        html = html.replace(/\n/g, '<br>');
        
        contentElement.innerHTML = html;
    }
    
    /**
     * Handle any actions returned from the server
     */
    function handleActions(actions) {
        if (!actions || !Array.isArray(actions)) return;
        
        actions.forEach(action => {
            switch (action.type) {
                case 'redirect':
                    if (action.url) {
                        window.location.href = action.url;
                    }
                    break;
                case 'notify':
                    if (action.message) {
                        showNotification(action.message, action.level || 'info');
                    }
                    break;
                // Add more action types as needed
            }
        });
    }
    
    /**
     * Show a notification to the user
     */
    function showNotification(message, level) {
        const alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', `alert-${level}`, 'alert-dismissible', 'fade', 'show', 'mt-3');
        alertDiv.setAttribute('role', 'alert');
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.querySelector('.chat-container').prepend(alertDiv);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }
    
    /**
     * Show message suggestions
     */
    function showSuggestions(suggestions) {
        if (!suggestions || !Array.isArray(suggestions) || suggestions.length === 0) return;
        
        // Create or clear existing suggestions container
        let suggestionsContainer = document.getElementById('suggestion-chips');
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.id = 'suggestion-chips';
            suggestionsContainer.classList.add('suggestion-chips', 'mt-2', 'd-flex', 'flex-wrap', 'gap-2');
            document.querySelector('.message-form').prepend(suggestionsContainer);
        } else {
            suggestionsContainer.innerHTML = '';
        }
        
        // Add suggestion chips
        suggestions.forEach(suggestion => {
            const chip = document.createElement('button');
            chip.type = 'button';
            chip.classList.add('btn', 'btn-sm', 'btn-outline-secondary', 'rounded-pill');
            chip.textContent = suggestion;
            
            chip.addEventListener('click', () => {
                messageInput.value = suggestion;
                messageForm.dispatchEvent(new Event('submit'));
                suggestionsContainer.innerHTML = '';
            });
            
            suggestionsContainer.appendChild(chip);
        });
    }
    
    // Apply markdown formatting to existing messages
    document.querySelectorAll('.message-content').forEach(applyMarkdownFormatting);
}); 