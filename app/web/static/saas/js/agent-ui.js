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
    let currentConversationId = null;
    
    // Debug mode
    window.debugMode = false;
    
    // Initialize
    init();
    
    /**
     * Initialize the agent UI
     */
    async function init() {
        try {
            // Check authentication
            const authToken = localStorage.getItem('authToken');
            if (!authToken) {
                // Redirect to login if not authenticated
                console.log('No auth token found, redirecting to login');
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
                    <i class="bi bi-info-circle me-2" aria-hidden="true"></i>
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
                     ${isDisabled ? '' : 'data-agent-clickable="true"'}
                     role="button"
                     tabindex="${isDisabled ? '-1' : '0'}"
                     aria-pressed="${isActive ? 'true' : 'false'}"
                     aria-disabled="${isDisabled ? 'true' : 'false'}"
                     aria-label="${agent.name} - ${agent.description} (${agent.subscription_tier} tier)${isDisabled ? ' - Requires upgrade' : ''}">
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div class="agent-icon me-3">
                                <i class="bi ${agent.icon}" aria-hidden="true"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h5 class="agent-name">${agent.name}</h5>
                                <p class="agent-description mb-1">${agent.description}</p>
                                <span class="agent-tier ${agent.subscription_tier}">${agent.subscription_tier}</span>
                            </div>
                        </div>
                        ${isDisabled ? `
                            <div class="upgrade-badge">
                                <i class="bi bi-lock" aria-hidden="true"></i> Upgrade
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
            
            // Add keyboard event listeners
            card.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    const agentType = this.getAttribute('data-agent-type');
                    selectAgent(agentType);
                }
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
            const agentName = getAgentNameFromType(conversation.agent_type);
            
            html += `
                <div class="conversation-item" 
                     data-conversation-id="${conversation.conversation_id}"
                     role="button"
                     tabindex="0"
                     aria-label="Conversation with ${agentName} from ${formattedDate}">
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
            
            // Add keyboard event listeners
            item.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    const conversationId = this.getAttribute('data-conversation-id');
                    loadConversation(conversationId);
                }
            });
        });
    }
    
    /**
     * Get agent name from agent type
     * @param {string} agentType - The agent type
     * @returns {string} The agent name
     */
    function getAgentNameFromType(agentType) {
        const agentNames = {
            'coordinator': 'Event Coordinator',
            'resource_planning': 'Resource Planner',
            'financial': 'Financial Advisor',
            'stakeholder_management': 'Stakeholder Manager',
            'marketing_communications': 'Marketing Specialist',
            'project_management': 'Project Manager',
            'analytics': 'Analytics Expert',
            'compliance_security': 'Compliance & Security Specialist'
        };
        
        return agentNames[agentType] || agentType;
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
            
            // Store conversation ID for future messages
            currentConversationId = response.conversation_id;
            
            // Update debug panel if enabled
            if (window.debugMode) {
                updateDebugPanel(response.conversation_id);
            }
            
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
        const messageId = 'msg-' + Date.now();
        
        messageElement.innerHTML = `
            <div class="message-content">
                <p id="${messageId}">${formatMessage(message)}</p>
                <div class="message-time">${timestamp}</div>
            </div>
            <div class="message-avatar">
                <i class="bi bi-person" aria-hidden="true"></i>
            </div>
        `;
        
        // Set ARIA attributes
        messageElement.setAttribute('role', 'listitem');
        messageElement.setAttribute('aria-label', `You said: ${message}`);
        
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
        const messageId = 'msg-' + Date.now();
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="bi bi-robot" aria-hidden="true"></i>
            </div>
            <div class="message-content">
                <p id="${messageId}">${formatMessage(message)}</p>
                <div class="message-footer d-flex justify-content-between align-items-center">
                    <div class="message-time">${timestamp}</div>
                    <div class="message-actions">
                        <button class="btn btn-sm btn-outline-primary feedback-button" aria-label="Rate this response">
                            <i class="bi bi-star me-1" aria-hidden="true"></i>
                            Rate
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Set ARIA attributes
        messageElement.setAttribute('role', 'listitem');
        messageElement.setAttribute('aria-label', `${currentAgentName} said: ${message.substring(0, 100)}${message.length > 100 ? '...' : ''}`);
        
        chatMessages.appendChild(messageElement);
        
        // Add event listener to feedback button
        const feedbackButton = messageElement.querySelector('.feedback-button');
        if (feedbackButton) {
            feedbackButton.addEventListener('click', function() {
                showFeedbackModal(messageId, message);
            });
        }
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Show feedback modal for a message
     * @param {string} messageId - The message ID
     * @param {string} message - The message content
     */
    function showFeedbackModal(messageId, message) {
        // Create modal HTML
        const modalHtml = `
            <div class="modal fade" id="feedbackModal" tabindex="-1" aria-labelledby="feedbackModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="feedbackModalLabel">Rate Response</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="feedbackForm">
                                <div class="mb-4">
                                    <label class="form-label fw-bold">How helpful was this response?</label>
                                    <div class="rating-stars-container text-center my-3">
                                        <div class="star-rating">
                                            <input type="radio" id="star5" name="rating" value="5" />
                                            <label for="star5" title="5 stars - Excellent">
                                                <i class="bi bi-star-fill fs-2 mx-1"></i>
                                            </label>
                                            <input type="radio" id="star4" name="rating" value="4" />
                                            <label for="star4" title="4 stars - Very Good">
                                                <i class="bi bi-star-fill fs-2 mx-1"></i>
                                            </label>
                                            <input type="radio" id="star3" name="rating" value="3" />
                                            <label for="star3" title="3 stars - Good">
                                                <i class="bi bi-star-fill fs-2 mx-1"></i>
                                            </label>
                                            <input type="radio" id="star2" name="rating" value="2" />
                                            <label for="star2" title="2 stars - Fair">
                                                <i class="bi bi-star-fill fs-2 mx-1"></i>
                                            </label>
                                            <input type="radio" id="star1" name="rating" value="1" />
                                            <label for="star1" title="1 star - Poor">
                                                <i class="bi bi-star-fill fs-2 mx-1"></i>
                                            </label>
                                        </div>
                                        <div class="rating-text mt-2" id="ratingText">Select a rating</div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="feedbackComment" class="form-label fw-bold">Additional comments (optional)</label>
                                    <textarea class="form-control" id="feedbackComment" rows="3" placeholder="What did you like or dislike about this response?"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="submitFeedback">Submit Feedback</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove any existing modal
        const existingModal = document.getElementById('feedbackModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to the page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('feedbackModal'));
        modal.show();
        
        // Handle rating selection
        setTimeout(() => {
            const ratingInputs = document.querySelectorAll('input[name="rating"]');
            const ratingText = document.getElementById('ratingText');
            const ratingTexts = {
                '1': 'Poor - Not helpful at all',
                '2': 'Fair - Slightly helpful',
                '3': 'Good - Somewhat helpful',
                '4': 'Very Good - Very helpful',
                '5': 'Excellent - Extremely helpful'
            };
            
            ratingInputs.forEach(input => {
                input.addEventListener('change', function() {
                    ratingText.textContent = ratingTexts[this.value];
                    ratingText.style.fontWeight = 'bold';
                    
                    // Highlight stars up to the selected one
                    const selectedValue = parseInt(this.value);
                    ratingInputs.forEach((input, index) => {
                        const starIndex = 5 - index; // Stars are in reverse order in the DOM
                        const label = input.nextElementSibling;
                        if (starIndex <= selectedValue) {
                            label.querySelector('i').classList.add('text-warning');
                        } else {
                            label.querySelector('i').classList.remove('text-warning');
                        }
                    });
                });
            });
        }, 300);
        
        // Handle submit button click
        setTimeout(() => {
            document.getElementById('submitFeedback').addEventListener('click', function() {
                const rating = document.querySelector('input[name="rating"]:checked')?.value;
                const comment = document.getElementById('feedbackComment').value;
                
                if (!rating) {
                    // Show validation message
                    const ratingText = document.getElementById('ratingText');
                    ratingText.textContent = 'Please select a rating';
                    ratingText.style.color = '#dc3545';
                    ratingText.style.fontWeight = 'bold';
                    return;
                }
                
                // Submit feedback
                submitFeedback(messageId, parseInt(rating), comment);
                
                // Close the modal
                modal.hide();
            });
        }, 300);
    }
    
    /**
     * Submit feedback for a message
     * @param {string} messageId - The message ID
     * @param {number} rating - The rating (1-5)
     * @param {string} comment - The comment
     */
    function submitFeedback(messageId, rating, comment) {
        // Check if conversation exists
        if (!agentService.currentConversationId) {
            showError('No active conversation to provide feedback for.');
            return;
        }
        
        // Find the message index
        const messages = document.querySelectorAll('.chat-message');
        let messageIndex = -1;
        
        for (let i = 0; i < messages.length; i++) {
            if (messages[i].querySelector(`#${messageId}`)) {
                messageIndex = i;
                break;
            }
        }
        
        if (messageIndex === -1) {
            showError('Could not find the message to provide feedback for.');
            return;
        }
        
        // Show loading message
        const loadingMessage = addSystemMessage('Submitting feedback...');
        
        // Send feedback to the server
        agentService.submitFeedback(
            agentService.currentConversationId,
            messageIndex,
            rating,
            comment
        )
        .then(response => {
            // Remove loading message
            if (loadingMessage && loadingMessage.parentNode) {
                loadingMessage.remove();
            }
            
            // Show success message with appropriate styling based on rating
            let ratingClass = 'text-success';
            let ratingIcon = 'bi-emoji-smile-fill';
            
            if (rating <= 2) {
                ratingClass = 'text-danger';
                ratingIcon = 'bi-emoji-frown-fill';
            } else if (rating === 3) {
                ratingClass = 'text-warning';
                ratingIcon = 'bi-emoji-neutral-fill';
            }
            
            const successMessage = addSystemMessage(`
                <div class="d-flex align-items-center">
                    <i class="bi ${ratingIcon} me-2 ${ratingClass}" style="font-size: 1.2rem;"></i>
                    <span>Thank you for your feedback! Your rating: <strong class="${ratingClass}">${rating}/5</strong></span>
                </div>
            `);
            
            // Update the message to show it has been rated
            const messageElement = document.querySelector(`#${messageId}`).closest('.chat-message');
            const feedbackButton = messageElement.querySelector('.feedback-button');
            
            if (feedbackButton) {
                // Create rating stars HTML
                let starsHtml = '';
                for (let i = 1; i <= 5; i++) {
                    if (i <= rating) {
                        starsHtml += '<i class="bi bi-star-fill text-warning" aria-hidden="true"></i>';
                    } else {
                        starsHtml += '<i class="bi bi-star text-warning" aria-hidden="true"></i>';
                    }
                }
                
                feedbackButton.innerHTML = starsHtml;
                feedbackButton.classList.remove('btn-outline-primary');
                feedbackButton.classList.add('btn-outline-success');
                feedbackButton.setAttribute('aria-label', `Rated ${rating}/5`);
                feedbackButton.disabled = true;
                
                // Add tooltip with the comment if provided
                if (comment) {
                    feedbackButton.setAttribute('data-bs-toggle', 'tooltip');
                    feedbackButton.setAttribute('data-bs-placement', 'top');
                    feedbackButton.setAttribute('title', `Comment: ${comment}`);
                    
                    // Initialize tooltip
                    new bootstrap.Tooltip(feedbackButton);
                }
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
            showError('Failed to submit feedback. Please try again.');
        });
        
        return null; // Return null to allow method chaining
    }
    
    /**
     * Add a system message to the chat
     * @param {string} message - The message to add
     */
    function addSystemMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message system-message';
        
        const messageId = 'msg-' + Date.now();
        
        messageElement.innerHTML = `
            <div class="message-content">
                <p id="${messageId}">${formatMessage(message)}</p>
            </div>
        `;
        
        // Set ARIA attributes
        messageElement.setAttribute('role', 'listitem');
        messageElement.setAttribute('aria-label', `System message: ${message}`);
        
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
        
        // Set ARIA attributes
        typingElement.setAttribute('role', 'status');
        typingElement.setAttribute('aria-label', `${currentAgentName} is typing...`);
        
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
        
        const messageId = 'error-' + Date.now();
        
        errorElement.innerHTML = `
            <div class="message-content" style="background-color: #f8d7da; color: #842029;">
                <p id="${messageId}"><i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>${message}</p>
            </div>
        `;
        
        // Set ARIA attributes
        errorElement.setAttribute('role', 'alert');
        errorElement.setAttribute('aria-label', `Error: ${message}`);
        
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
    async function exportChatHistory() {
        try {
            // Check if there's an active conversation
            if (!agentService.currentConversationId) {
                showError('No active conversation to export.');
                return;
            }

            // Get auth token
            const token = localStorage.getItem('authToken');
            const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

            if (!token) {
                throw new Error('Authentication required. Please log in again.');
            }

            // Prepare headers
            const headers = {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            };

            if (orgId) {
                headers['X-Organization-ID'] = orgId;
            }

            // Fetch conversation export from API (default format: JSON)
            const response = await fetch(`/api/agents/conversations/${agentService.currentConversationId}/export?format=json`, {
                method: 'GET',
                headers: headers
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to export conversation: ${response.statusText}`);
            }

            // Get conversation data
            const conversationData = await response.json();

            // Format as readable text for download
            let fileContent = `Conversation Export\n`;
            fileContent += `Date: ${new Date().toLocaleString()}\n`;
            fileContent += `Conversation ID: ${agentService.currentConversationId}\n`;
            fileContent += `Agent: ${conversationData.agent_name || 'AI Assistant'}\n`;
            fileContent += `\n${'='.repeat(80)}\n\n`;

            // Add all messages
            if (conversationData.messages && conversationData.messages.length > 0) {
                conversationData.messages.forEach(message => {
                    const role = message.role === 'user' ? 'User' : message.role === 'assistant' ? 'Agent' : 'System';
                    const timestamp = message.timestamp ? new Date(message.timestamp).toLocaleString() : '';
                    fileContent += `[${timestamp}] ${role}:\n${message.content}\n\n`;
                });
            } else {
                fileContent += 'No messages in conversation.\n';
            }

            // Create download link
            const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8;' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `conversation-${agentService.currentConversationId}-${new Date().toISOString().slice(0, 10)}.txt`;
            a.style.visibility = 'hidden';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // Clean up
            URL.revokeObjectURL(url);

            showSuccess('Conversation exported successfully');

        } catch (error) {
            console.error('Error exporting conversation:', error);
            showError('Failed to export conversation: ' + error.message);
        }
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
                    <div class="modal fade" id="attachEventModal" tabindex="-1" aria-labelledby="attachEventModalLabel" aria-hidden="true" role="dialog">
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
                                            <select class="form-select" id="eventSelect" required aria-describedby="eventSelectHelp">
                                                <option value="">Select an event...</option>
                                                ${eventOptions}
                                            </select>
                                            <div id="eventSelectHelp" class="form-text">Attaching an event will give the agent access to event details.</div>
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
                
                // Set focus to the select element when the modal is shown
                document.getElementById('attachEventModal').addEventListener('shown.bs.modal', function() {
                    document.getElementById('eventSelect').focus();
                });
                
                // Handle attach button click
                document.getElementById('attachEventButton').addEventListener('click', function() {
                    const eventId = document.getElementById('eventSelect').value;
                    if (!eventId) {
                        // Show validation error
                        document.getElementById('eventSelect').classList.add('is-invalid');
                        return;
                    }
                    
                    // Attach event to conversation
                    attachEventToConversation(eventId);
                    
                    // Close the modal
                    modal.hide();
                });
                
                // Handle form submission
                document.getElementById('attachEventForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    document.getElementById('attachEventButton').click();
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
    
    /**
     * Update debug panel with memory information
     * @param {string} conversationId - The conversation ID to debug
     */
    async function updateDebugPanel(conversationId) {
        if (!conversationId) return;
        
        try {
            const response = await fetch(`/api/agents/debug/memory/${conversationId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const debugData = await response.json();
            
            // Create or update debug panel
            let debugPanel = document.getElementById('debugPanel');
            if (!debugPanel) {
                debugPanel = document.createElement('div');
                debugPanel.id = 'debugPanel';
                debugPanel.style.cssText = `
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    width: 400px;
                    max-height: 80vh;
                    overflow-y: auto;
                    background: #f8f9fa;
                    border: 2px solid #007bff;
                    border-radius: 8px;
                    padding: 15px;
                    z-index: 9999;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                `;
                document.body.appendChild(debugPanel);
            }
            
            // Update debug panel content
            debugPanel.innerHTML = `
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <h6 style="margin: 0; color: #007bff;">🐛 Memory Debug Panel</h6>
                    <button onclick="toggleDebugMode()" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 2px 8px; font-size: 10px; cursor: pointer;">Close</button>
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>Conversation ID:</strong><br>
                    <code style="background: #e9ecef; padding: 2px 4px; border-radius: 3px; word-break: break-all;">${debugData.conversation_id}</code>
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>Organization ID:</strong> ${debugData.organization_id || 'N/A'}
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>Memory Available:</strong> 
                    <span style="color: ${debugData.memory_debug?.memory_available ? '#28a745' : '#dc3545'};">
                        ${debugData.memory_debug?.memory_available ? '✅ Yes' : '❌ No'}
                    </span>
                </div>
                ${debugData.memory_debug?.memory_type ? `
                    <div style="margin-bottom: 10px;">
                        <strong>Memory Type:</strong> ${debugData.memory_debug.memory_type}
                    </div>
                ` : ''}
                ${debugData.memory_debug?.memory_contents ? `
                    <div style="margin-bottom: 10px;">
                        <strong>Memory Contents:</strong>
                        <div style="background: #e9ecef; padding: 8px; border-radius: 4px; margin-top: 5px; max-height: 200px; overflow-y: auto;">
                            <pre style="margin: 0; white-space: pre-wrap; font-size: 10px;">${JSON.stringify(debugData.memory_debug.memory_contents, null, 2)}</pre>
                        </div>
                    </div>
                ` : ''}
                ${debugData.memory_debug?.database_records ? `
                    <div style="margin-bottom: 10px;">
                        <strong>Database Records:</strong> ${debugData.memory_debug.database_records.length} records
                        <div style="background: #e9ecef; padding: 8px; border-radius: 4px; margin-top: 5px; max-height: 150px; overflow-y: auto;">
                            ${debugData.memory_debug.database_records.map(record => `
                                <div style="margin-bottom: 5px; padding: 5px; background: white; border-radius: 3px;">
                                    <strong>${record.memory_type}:</strong> ${record.content.substring(0, 50)}${record.content.length > 50 ? '...' : ''}
                                    <br><small style="color: #6c757d;">${record.timestamp}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                ${debugData.state_contents ? `
                    <div style="margin-bottom: 10px;">
                        <strong>State Contents:</strong>
                        <div style="background: #e9ecef; padding: 8px; border-radius: 4px; margin-top: 5px; max-height: 200px; overflow-y: auto;">
                            <pre style="margin: 0; white-space: pre-wrap; font-size: 10px;">${JSON.stringify(debugData.state_contents, null, 2)}</pre>
                        </div>
                    </div>
                ` : ''}
                ${debugData.error ? `
                    <div style="margin-bottom: 10px;">
                        <strong style="color: #dc3545;">Error:</strong>
                        <div style="background: #f8d7da; color: #721c24; padding: 8px; border-radius: 4px; margin-top: 5px;">
                            ${debugData.error}
                        </div>
                    </div>
                ` : ''}
                ${debugData.memory_debug?.memory_error ? `
                    <div style="margin-bottom: 10px;">
                        <strong style="color: #dc3545;">Memory Error:</strong>
                        <div style="background: #f8d7da; color: #721c24; padding: 8px; border-radius: 4px; margin-top: 5px;">
                            ${debugData.memory_debug.memory_error}
                        </div>
                    </div>
                ` : ''}
                ${debugData.memory_debug?.database_error ? `
                    <div style="margin-bottom: 10px;">
                        <strong style="color: #dc3545;">Database Error:</strong>
                        <div style="background: #f8d7da; color: #721c24; padding: 8px; border-radius: 4px; margin-top: 5px;">
                            ${debugData.memory_debug.database_error}
                        </div>
                    </div>
                ` : ''}
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #dee2e6; font-size: 10px; color: #6c757d;">
                    Last updated: ${new Date().toLocaleTimeString()}
                </div>
            `;
            
        } catch (error) {
            console.error('Error updating debug panel:', error);
            
            // Show error in debug panel
            let debugPanel = document.getElementById('debugPanel');
            if (!debugPanel) {
                debugPanel = document.createElement('div');
                debugPanel.id = 'debugPanel';
                debugPanel.style.cssText = `
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    width: 400px;
                    background: #f8f9fa;
                    border: 2px solid #dc3545;
                    border-radius: 8px;
                    padding: 15px;
                    z-index: 9999;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                `;
                document.body.appendChild(debugPanel);
            }
            
            debugPanel.innerHTML = `
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <h6 style="margin: 0; color: #dc3545;">🐛 Memory Debug Panel (Error)</h6>
                    <button onclick="toggleDebugMode()" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 2px 8px; font-size: 10px; cursor: pointer;">Close</button>
                </div>
                <div style="background: #f8d7da; color: #721c24; padding: 8px; border-radius: 4px;">
                    <strong>Debug Error:</strong><br>
                    ${error.message}
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #dee2e6; font-size: 10px; color: #6c757d;">
                    Last updated: ${new Date().toLocaleTimeString()}
                </div>
            `;
        }
    }
    
    /**
     * Toggle debug mode on/off
     */
    window.toggleDebugMode = function() {
        window.debugMode = !window.debugMode;
        
        const debugPanel = document.getElementById('debugPanel');
        if (debugPanel) {
            debugPanel.remove();
        }
        
        if (window.debugMode) {
            // Show debug toggle button
            let debugToggle = document.getElementById('debugToggle');
            if (!debugToggle) {
                debugToggle = document.createElement('button');
                debugToggle.id = 'debugToggle';
                debugToggle.innerHTML = '🐛 Debug ON';
                debugToggle.style.cssText = `
                    position: fixed;
                    top: 10px;
                    left: 10px;
                    background: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                    cursor: pointer;
                    z-index: 9998;
                `;
                debugToggle.onclick = toggleDebugMode;
                document.body.appendChild(debugToggle);
            }
            
            // Update debug panel if we have a conversation
            if (currentConversationId) {
                updateDebugPanel(currentConversationId);
            }
            
            console.log('🐛 Debug mode enabled. Memory information will be shown after each message.');
        } else {
            // Remove debug toggle button
            const debugToggle = document.getElementById('debugToggle');
            if (debugToggle) {
                debugToggle.remove();
            }
            console.log('🐛 Debug mode disabled.');
        }
    };
    
    /**
     * Add debug toggle to console for easy access
     */
    console.log('💡 To enable memory debug mode, type: toggleDebugMode()');
    
    // Expose functions globally for use in HTML and console
    window.selectAgent = selectAgent;
    window.updateDebugPanel = updateDebugPanel;
});
