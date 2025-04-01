/**
 * AI Event Planner SaaS - Agent UI
 * 
 * This file contains the JavaScript code for the agent UI interactions.
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const agentList = document.getElementById('agentList');
    const conversationHistory = document.getElementById('conversationHistory');
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const currentAgentNameElement = document.getElementById('currentAgentName');
    let currentAgentName = '';
    const agentCapabilities = document.getElementById('agentCapabilities');
    const subscriptionTier = document.getElementById('subscriptionTier');
    const refreshAgents = document.getElementById('refreshAgents');
    const clearChat = document.getElementById('clearChat');
    const exportChat = document.getElementById('exportChat');
    const attachEvent = document.getElementById('attachEvent');
    
    // State
    let selectedAgentType = null;
    let agents = [];
    let conversations = [];
    let isAuthenticated = true; // Bypass authentication check for testing
    
    // Set a mock auth token for testing
    localStorage.setItem('authToken', 'mock-auth-token');
    localStorage.setItem('organizationId', '1');
    
    // Initialize
    init();
    
    /**
     * Initialize the agent UI
     */
    async function init() {
        try {
            // Check authentication
            if (!isAuthenticated) {
                // Redirect to login if not authenticated
                window.location.href = '/saas/login.html';
                return;
            }
            
            // Load available agents
            await loadAgents();
            
            // Load conversation history
            await loadConversations();
            
            // Set up event listeners
            setupEventListeners();
            
            // Check if first-time user and show onboarding
            if (!localStorage.getItem('agent_onboarding_completed')) {
                // Wait for onboarding to be initialized
                setTimeout(() => {
                    // Check if onboarding instance exists
                    if (window.onboarding) {
                        window.onboarding.start();
                    }
                }, 500);
            }
        } catch (error) {
            console.error('Error initializing agent UI:', error);
            showError('Failed to initialize agent UI. Please try refreshing the page.');
        }
    }
    
    /**
     * Load available agents from the API
     */
    async function loadAgents() {
        try {
            // Show loading state
            agentList.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading agents...</p>
                </div>
            `;
            
            // Get available agents
            const data = await agentService.getAvailableAgents();
            agents = data.agents;
            
            // Update subscription tier display
            subscriptionTier.textContent = data.subscription_tier.charAt(0).toUpperCase() + data.subscription_tier.slice(1);
            
            // Render agent list
            renderAgentList();
        } catch (error) {
            console.error('Error loading agents:', error);
            agentList.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load agents. Please try refreshing the page.
                </div>
            `;
        }
    }
    
    /**
     * Load conversation history from the API
     */
    async function loadConversations() {
        try {
            // Show loading state
            conversationHistory.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading conversations...</p>
                </div>
            `;
            
            // Get conversation history
            const data = await agentService.listConversations();
            conversations = data.conversations;
            
            // Render conversation history
            renderConversationHistory();
        } catch (error) {
            console.error('Error loading conversations:', error);
            conversationHistory.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load conversation history.
                </div>
            `;
        }
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Refresh agents button
        refreshAgents.addEventListener('click', function(e) {
            e.preventDefault();
            loadAgents();
        });
        
        // Chat form submission
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
        
        // Clear chat button
        clearChat.addEventListener('click', function(e) {
            e.preventDefault();
            clearChatMessages();
        });
        
        // Export chat button
        exportChat.addEventListener('click', function(e) {
            e.preventDefault();
            exportChatHistory();
        });
        
        // Attach event button
        attachEvent.addEventListener('click', function(e) {
            e.preventDefault();
            showAttachEventModal();
        });
        
        // Agent help button
        const agentHelpButton = document.getElementById('agentHelpButton');
        if (agentHelpButton) {
            agentHelpButton.addEventListener('click', function(e) {
                e.preventDefault();
                // Check if onboarding instance exists
                if (window.onboarding) {
                    window.onboarding.start();
                } else {
                    // Fallback to showing the help modal
                    const helpModal = new bootstrap.Modal(document.getElementById('agentHelpModal'));
                    helpModal.show();
                }
            });
        }
    }
    
    /**
     * Render the agent list
     */
    function renderAgentList() {
        if (!agents || agents.length === 0) {
            agentList.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    No agents available.
                </div>
            `;
            return;
        }
        
        let html = '';
        
        agents.forEach(agent => {
            const isActive = agent.agent_type === selectedAgentType;
            const isDisabled = !agent.available;
            
            html += `
                <div class="card agent-card ${isActive ? 'active' : ''} ${isDisabled ? 'disabled' : ''}" 
                     data-agent-type="${agent.agent_type}" 
                     ${isDisabled ? '' : 'data-agent-clickable="true"'}>
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div class="agent-icon me-3">
                                <i class="bi ${agent.icon}"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h5 class="agent-name">${agent.name}</h5>
                                <p class="agent-description mb-1">${agent.description}</p>
                                <span class="agent-tier ${agent.subscription_tier}">${agent.subscription_tier}</span>
                            </div>
                        </div>
                        ${isDisabled ? `
                            <div class="upgrade-badge">
                                <i class="bi bi-lock"></i> Upgrade
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });
        
        agentList.innerHTML = html;
        
        // Add click event listeners to agent cards
        document.querySelectorAll('.agent-card:not(.disabled)').forEach(card => {
            card.addEventListener('click', function() {
                const agentType = this.getAttribute('data-agent-type');
                console.log('Agent card clicked:', agentType);
                selectAgent(agentType);
            });
        });
    }
    
    /**
     * Render the conversation history
     */
    function renderConversationHistory() {
        if (!conversations || conversations.length === 0) {
            conversationHistory.innerHTML = `
                <p class="text-muted text-center">No recent conversations</p>
            `;
            return;
        }
        
        let html = '';
        
        conversations.forEach(conversation => {
            const date = new Date(conversation.timestamp);
            const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
            
            html += `
                <div class="conversation-item" data-conversation-id="${conversation.conversation_id}">
                    <div class="conversation-title">${conversation.agent_type}</div>
                    <div class="conversation-preview">${conversation.preview || 'No preview available'}</div>
                    <div class="conversation-time">${formattedDate}</div>
                </div>
            `;
        });
        
        conversationHistory.innerHTML = html;
        
        // Add click event listeners to conversation items
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', function() {
                const conversationId = this.getAttribute('data-conversation-id');
                loadConversation(conversationId);
            });
        });
    }
    
    /**
     * Select an agent
     * @param {string} agentType - The agent type to select
     */
function selectAgent(agentType) {
        console.log('selectAgent called with:', agentType);
        
        // Update selected agent
        selectedAgentType = agentType;
        
        // Update UI
        document.querySelectorAll('.agent-card').forEach(card => {
            card.classList.remove('active');
        });
        
        const selectedCard = document.querySelector(`.agent-card[data-agent-type="${agentType}"]`);
        if (selectedCard) {
            selectedCard.classList.add('active');
        }
        
        // Get agent metadata
        const agent = agents.find(a => a.agent_type === agentType);
        
        // Update current agent name
        currentAgentName = agent ? agent.name : 'Unknown Agent';
        if (currentAgentNameElement) {
            currentAgentNameElement.textContent = currentAgentName;
        }
        
        // Enable chat input
        messageInput.disabled = false;
        sendButton.disabled = false;
        
        // Clear chat messages
        clearChatMessages();
        
        // Add welcome message
        addSystemMessage(`You are now chatting with the ${currentAgentName}. How can I help you with your event planning?`);
        
        // Show agent capabilities
        showAgentCapabilities(agentType);
    }
    
    /**
     * Show agent capabilities
     * @param {string} agentType - The agent type
     */
    function showAgentCapabilities(agentType) {
        console.log('showAgentCapabilities called with:', agentType);
        console.log('agents array:', agents);
        
        const capabilities = agentService.getAgentCapabilities(agentType);
        
        let html = `
            <h5>${capabilities.title}</h5>
            <p>${capabilities.description}</p>
            <hr>
            <h6>What This Agent Can Do:</h6>
            <div class="row">
        `;
        
        capabilities.capabilities.forEach(capability => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="capability-item">
                        <div class="capability-title">${capability.title}</div>
                        <div class="capability-description">${capability.description}</div>
                        <div class="capability-example">
                            <strong>Example:</strong> "${capability.example}"
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
            </div>
        `;
        
        agentCapabilities.innerHTML = html;
    }
    
    /**
     * Load a conversation
     * @param {string} conversationId - The conversation ID to load
     */
    async function loadConversation(conversationId) {
        try {
            // Show loading state
            chatMessages.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading conversation...</p>
                </div>
            `;
            
            // Get conversation history
            const data = await agentService.getConversationHistory(conversationId);
            
            // Update selected agent
            selectedAgentType = data.agent_type;
            
            // Update UI
            document.querySelectorAll('.agent-card').forEach(card => {
                card.classList.remove('active');
            });
            
            const selectedCard = document.querySelector(`.agent-card[data-agent-type="${selectedAgentType}"]`);
            if (selectedCard) {
                selectedCard.classList.add('active');
            }
            
            // Get agent metadata
            const agent = agents.find(a => a.agent_type === selectedAgentType);
            
            // Update current agent name
            currentAgentName = agent ? agent.name : 'Unknown Agent';
            if (currentAgentNameElement) {
                currentAgentNameElement.textContent = currentAgentName;
            }
            
            // Enable chat input
            messageInput.disabled = false;
            sendButton.disabled = false;
            
            // Clear chat messages
            clearChatMessages();
            
            // Add messages
            data.messages.forEach(message => {
                if (message.role === 'user') {
                    addUserMessage(message.content);
                } else if (message.role === 'assistant') {
                    addAgentMessage(message.content);
                } else if (message.role === 'system') {
                    addSystemMessage(message.content);
                }
            });
            
            // Show agent capabilities
            showAgentCapabilities(selectedAgentType);
            
            // Update conversation ID
            agentService.currentConversationId = conversationId;
        } catch (error) {
            console.error('Error loading conversation:', error);
            showError('Failed to load conversation. Please try again.');
        }
    }
    
    /**
     * Send a message to the selected agent
     */
    async function sendMessage() {
        const message = messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        if (!selectedAgentType) {
            showError('Please select an agent first.');
            return;
        }
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input
        messageInput.value = '';
        
        // Disable input while waiting for response
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            // Send message to agent
            const response = await agentService.sendMessage(selectedAgentType, message);
            
            // Remove typing indicator
            hideTypingIndicator();
            
            // Add agent response to chat
            addAgentMessage(response.response);
            
            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
            
            // Refresh conversation history
            await loadConversations();
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Remove typing indicator
            hideTypingIndicator();
            
            // Check if error is due to subscription limitations
            if (error.message && error.message.startsWith('subscription_required:')) {
                const errorMessage = error.message.split('subscription_required:')[1];
                showSubscriptionRequiredError(errorMessage);
            } else {
                showError('Failed to send message. Please try again.');
            }
            
            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
        }
    }
    
    /**
     * Add a user message to the chat
     * @param {string} message - The message to add
     */
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message user-message';
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageElement.innerHTML = `
            <div class="message-content">
                <p>${formatMessage(message)}</p>
                <div class="message-time">${timestamp}</div>
            </div>
            <div class="message-avatar">
                <i class="bi bi-person"></i>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Add an agent message to the chat
     * @param {string} message - The message to add
     */
    function addAgentMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="message-content">
                <p>${formatMessage(message)}</p>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Add a system message to the chat
     * @param {string} message - The message to add
     */
    function addSystemMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message system-message';
        
        messageElement.innerHTML = `
            <div class="message-content">
                <p>${formatMessage(message)}</p>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Show a typing indicator
     */
    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'typing-indicator';
        typingElement.id = 'typingIndicator';
        
        typingElement.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        
        chatMessages.appendChild(typingElement);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Hide the typing indicator
     */
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    /**
     * Show an error message in the chat
     * @param {string} message - The error message to show
     */
    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'chat-message system-message';
        
        errorElement.innerHTML = `
            <div class="message-content" style="background-color: #f8d7da; color: #842029;">
                <p><i class="bi bi-exclamation-triangle me-2"></i>${message}</p>
            </div>
        `;
        
        chatMessages.appendChild(errorElement);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Show a subscription required error message
     * @param {string} message - The error message to show
     */
    function showSubscriptionRequiredError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'chat-message system-message';
        
        errorElement.innerHTML = `
            <div class="message-content" style="background-color: #f8d7da; color: #842029;">
                <p><i class="bi bi-exclamation-triangle me-2"></i>${message}</p>
                <div class="mt-2">
                    <a href="/saas/subscription.html" class="btn btn-danger btn-sm">
                        <i class="bi bi-arrow-up-circle me-1"></i>Upgrade Subscription
                    </a>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(errorElement);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Clear all chat messages
     */
    function clearChatMessages() {
        chatMessages.innerHTML = '';
        
        // Add welcome message if agent is selected
        if (selectedAgentType) {
            addSystemMessage(`You are now chatting with the ${currentAgentName}. How can I help you with your event planning?`);
        }
    }
    
    /**
     * Export chat history
     */
    function exportChatHistory() {
        // Get all messages
        const messages = [];
        
        document.querySelectorAll('.chat-message').forEach(messageElement => {
            const isUser = messageElement.classList.contains('user-message');
            const isSystem = messageElement.classList.contains('system-message');
            
            const contentElement = messageElement.querySelector('.message-content p');
            if (!contentElement) return;
            
            const content = contentElement.textContent;
            
            if (isUser) {
                messages.push(`User: ${content}`);
            } else if (isSystem) {
                messages.push(`System: ${content}`);
            } else {
                messages.push(`Agent: ${content}`);
            }
        });
        
        if (messages.length === 0) {
            showError('No messages to export.');
            return;
        }
        
        // Create file content
        const fileContent = messages.join('\n\n');
        
        // Create download link
        const blob = new Blob([fileContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        
        // Clean up
        URL.revokeObjectURL(url);
    }
    
    /**
     * Show the attach event modal
     */
    function showAttachEventModal() {
        // Check if conversation exists
        if (!agentService.currentConversationId) {
            showError('No active conversation to attach to an event.');
            return;
        }
        
        // Fetch events for the current organization
        agentService.getEvents()
            .then(data => {
                // Check if there are any events
                if (!data.events || data.events.length === 0) {
                    showError('No events found. Please create an event first.');
                    return;
                }
                
                // Create event options
                let eventOptions = '';
                data.events.forEach(event => {
                    eventOptions += `<option value="${event.id}">${event.title}</option>`;
                });
                
                // Create modal HTML
                const modalHtml = `
                    <div class="modal fade" id="attachEventModal" tabindex="-1" aria-labelledby="attachEventModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="attachEventModalLabel">Attach to Event</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <form id="attachEventForm">
                                        <div class="mb-3">
                                            <label for="eventSelect" class="form-label">Select Event</label>
                                            <select class="form-select" id="eventSelect" required>
                                                <option value="">Select an event...</option>
                                                ${eventOptions}
                                            </select>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="button" class="btn btn-primary" id="attachEventButton">Attach</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Remove any existing modal
                const existingModal = document.getElementById('attachEventModal');
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Add modal to the page
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Show the modal
                const modal = new bootstrap.Modal(document.getElementById('attachEventModal'));
                modal.show();
                
                // Handle attach button click
                document.getElementById('attachEventButton').addEventListener('click', function() {
                    const eventId = document.getElementById('eventSelect').value;
                    if (!eventId) {
                        return;
                    }
                    
                    // Attach event to conversation
                    attachEventToConversation(eventId);
                    
                    // Close the modal
                    modal.hide();
                });
            })
            .catch(error => {
                console.error('Error fetching events:', error);
                showError('Failed to load events. Please try again.');
            });
    }
    
    /**
     * Attach an event to the current conversation
     * @param {string} eventId - The event ID to attach
     */
    function attachEventToConversation(eventId) {
        // Check if conversation exists
        if (!agentService.currentConversationId) {
            showError('No active conversation to attach to an event.');
            return;
        }
        
        // Show loading message
        addSystemMessage('Attaching event to conversation...');
        
        // Send request to attach event
        agentService.attachEventToConversation(agentService.currentConversationId, eventId)
            .then(data => {
                // Show success message
                addSystemMessage(`Event has been attached to this conversation. The agent now has access to the event details.`);
            })
            .catch(error => {
                console.error('Error attaching event:', error);
                showError('Failed to attach event. Please try again.');
            });
    }
    
    /**
     * Format a message for display
     * @param {string} message - The message to format
     * @returns {string} The formatted message
     */
    function formatMessage(message) {
        // Replace newlines with <br>
        let formatted = message.replace(/\n/g, '<br>');
        
        // Make URLs clickable
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return formatted;
    }
    
    /**
     * Scroll the chat messages to the bottom
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Expose selectAgent function globally for use in HTML
    window.selectAgent = selectAgent;
});
