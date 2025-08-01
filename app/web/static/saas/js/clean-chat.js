/**
 * AI Event Planner SaaS - Clean Chat Interface JavaScript
 * Handles all interactions for the minimal chat interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const sidebarToggle = document.getElementById('sidebarToggle');
    const conversationSidebar = document.getElementById('conversationSidebar');
    const agentSelector = document.getElementById('agentSelector');
    const currentAgentName = document.getElementById('currentAgentName');
    const newChatBtn = document.getElementById('newChatBtn');
    const messagesContainer = document.getElementById('messagesContainer');
    const welcomeState = document.getElementById('welcomeState');
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const conversationList = document.getElementById('conversationList');
    const conversationSearch = document.getElementById('conversationSearch');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    
    // Modals
    const agentModal = new bootstrap.Modal(document.getElementById('agentModal'));
    const subscriptionModal = new bootstrap.Modal(document.getElementById('subscriptionModal'));
    
    // State
    let selectedAgent = null;
    let currentConversationId = null;
    let conversations = [];
    let agents = [];
    let isTyping = false;
    let messageHistory = [];
    
    // Initialize
    init();
    
    /**
     * Initialize the clean chat interface
     */
    async function init() {
        try {
            // Set up authentication
            setupAuth();
            
            // Load agents and conversations
            await Promise.all([
                loadAgents(),
                loadConversations()
            ]);
            
            // Set up event listeners
            setupEventListeners();
            
            // Auto-resize textarea
            setupTextareaAutoResize();
            
            console.log('Clean chat interface initialized successfully');
        } catch (error) {
            console.error('Error initializing clean chat:', error);
            showError('Failed to initialize chat interface. Please refresh the page.');
        }
    }
    
    /**
     * Set up authentication
     */
    function setupAuth() {
        // Use existing auth setup from agent-ui.js
        if (!localStorage.getItem('authToken')) {
            localStorage.setItem('authToken', 'mock-auth-token');
        }
        if (!localStorage.getItem('organizationId')) {
            localStorage.setItem('organizationId', '1');
        }
    }
    
    /**
     * Load available agents
     */
    async function loadAgents() {
        try {
            const data = await agentService.getAvailableAgents();
            agents = data.agents;
            renderAgentModal();
        } catch (error) {
            console.error('Error loading agents:', error);
            showError('Failed to load AI agents. Please try again.');
        }
    }
    
    /**
     * Load conversation history
     */
    async function loadConversations() {
        try {
            const data = await agentService.listConversations();
            conversations = data.conversations || [];
            renderConversations();
        } catch (error) {
            console.error('Error loading conversations:', error);
            // Don't show error for conversations as it's not critical
        }
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Sidebar toggle
        sidebarToggle.addEventListener('click', toggleSidebar);
        
        // Agent selector
        agentSelector.addEventListener('click', showAgentModal);
        
        // New chat button
        newChatBtn.addEventListener('click', startNewChat);
        
        // Message form
        messageForm.addEventListener('submit', handleMessageSubmit);
        
        // Message input
        messageInput.addEventListener('keydown', handleInputKeydown);
        messageInput.addEventListener('input', handleInputChange);
        
        // Conversation search
        conversationSearch.addEventListener('input', handleConversationSearch);
        
        // Clear all conversations
        clearAllBtn.addEventListener('click', handleClearAllConversations);
        
        // Quick action buttons
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', handleQuickAction);
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', handleOutsideClick);
        
        // Handle window resize
        window.addEventListener('resize', handleWindowResize);
    }
    
    /**
     * Set up textarea auto-resize
     */
    function setupTextareaAutoResize() {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
    
    /**
     * Toggle sidebar visibility
     */
    function toggleSidebar() {
        conversationSidebar.classList.toggle('open');
    }
    
    /**
     * Show agent selection modal
     */
    function showAgentModal() {
        agentModal.show();
    }
    
    /**
     * Render agent modal content
     */
    function renderAgentModal() {
        const agentGrid = document.getElementById('agentGrid');
        
        if (!agents || agents.length === 0) {
            agentGrid.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-exclamation-triangle text-warning mb-3" style="font-size: 3rem;"></i>
                    <h3>No agents available</h3>
                    <p class="text-muted">Please check your subscription or try again later.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        agents.forEach(agent => {
            const isDisabled = !agent.available;
            const isSelected = selectedAgent && selectedAgent.agent_type === agent.agent_type;
            
            html += `
                <div class="agent-card ${isDisabled ? 'disabled' : ''} ${isSelected ? 'selected' : ''}" 
                     data-agent-type="${agent.agent_type}"
                     ${!isDisabled ? 'role="button" tabindex="0"' : ''}>
                    <div class="agent-header">
                        <div class="agent-icon">
                            <i class="bi ${agent.icon}"></i>
                        </div>
                        <div class="agent-info">
                            <h3>${agent.name}</h3>
                            <span class="agent-tier ${agent.subscription_tier}">${agent.subscription_tier}</span>
                        </div>
                    </div>
                    <p class="agent-description">${agent.description}</p>
                    <ul class="agent-capabilities">
                        ${agent.capabilities ? agent.capabilities.slice(0, 3).map(cap => `<li>${cap}</li>`).join('') : ''}
                    </ul>
                    ${isDisabled ? '<div class="text-center mt-3"><small class="text-muted"><i class="bi bi-lock"></i> Upgrade required</small></div>' : ''}
                </div>
            `;
        });
        
        agentGrid.innerHTML = html;
        
        // Add click listeners
        document.querySelectorAll('.agent-card:not(.disabled)').forEach(card => {
            card.addEventListener('click', handleAgentSelection);
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleAgentSelection.call(this);
                }
            });
        });
        
        // Add disabled agent click listeners
        document.querySelectorAll('.agent-card.disabled').forEach(card => {
            card.addEventListener('click', showSubscriptionModal);
        });
    }
    
    /**
     * Handle agent selection
     */
    function handleAgentSelection() {
        const agentType = this.getAttribute('data-agent-type');
        const agent = agents.find(a => a.agent_type === agentType);
        
        if (agent) {
            selectAgent(agent);
            agentModal.hide();
        }
    }
    
    /**
     * Select an agent
     */
    function selectAgent(agent) {
        selectedAgent = agent;
        currentAgentName.textContent = agent.name;
        
        // Update agent selector appearance
        agentSelector.querySelector('i').className = `bi ${agent.icon} me-2`;
        
        // Enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.placeholder = `Message ${agent.name}...`;
        
        // Hide welcome state and show chat
        if (welcomeState) {
            welcomeState.style.display = 'none';
        }
        
        // Clear messages and start fresh
        clearMessages();
        addSystemMessage(`You're now chatting with ${agent.name}. How can I help you plan your event?`);
        
        // Focus input
        messageInput.focus();
        
        console.log('Selected agent:', agent.name);
    }
    
    /**
     * Show subscription modal
     */
    function showSubscriptionModal() {
        subscriptionModal.show();
    }
    
    /**
     * Handle quick action button clicks
     */
    function handleQuickAction() {
        const agentType = this.getAttribute('data-agent');
        const agent = agents.find(a => a.agent_type === agentType);
        
        if (agent && agent.available) {
            selectAgent(agent);
        } else if (agent) {
            showSubscriptionModal();
        }
    }
    
    /**
     * Start a new chat
     */
    function startNewChat() {
        currentConversationId = null;
        clearMessages();
        
        if (selectedAgent) {
            addSystemMessage(`Starting a new conversation with ${selectedAgent.name}. How can I help you?`);
        } else {
            // Show welcome state
            if (welcomeState) {
                welcomeState.style.display = 'flex';
            }
        }
        
        // Clear active conversation
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        messageInput.focus();
    }
    
    /**
     * Handle message form submission
     */
    async function handleMessageSubmit(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message || !selectedAgent) return;
        
        // Add user message
        addUserMessage(message);
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Disable input while processing
        setInputState(false);
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            // Send message to agent
            const response = await agentService.sendMessage(selectedAgent.agent_type, message);
            
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add agent response
            addAgentMessage(response.response);
            
            // Update conversation ID
            currentConversationId = response.conversation_id;
            
            // Refresh conversations
            await loadConversations();
            
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Hide typing indicator
            hideTypingIndicator();
            
            // Show error
            if (error.message && error.message.includes('subscription_required')) {
                showSubscriptionModal();
            } else {
                addSystemMessage('Sorry, I encountered an error. Please try again.', 'error');
            }
        } finally {
            // Re-enable input
            setInputState(true);
            messageInput.focus();
        }
    }
    
    /**
     * Handle input keydown events
     */
    function handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    }
    
    /**
     * Handle input change events
     */
    function handleInputChange() {
        const hasText = messageInput.value.trim().length > 0;
        sendBtn.disabled = !hasText || !selectedAgent;
    }
    
    /**
     * Set input state
     */
    function setInputState(enabled) {
        messageInput.disabled = !enabled;
        sendBtn.disabled = !enabled || !messageInput.value.trim();
    }
    
    /**
     * Add user message to chat
     */
    function addUserMessage(text) {
        const messageEl = createMessageElement('user', text);
        appendMessage(messageEl);
        scrollToBottom();
    }
    
    /**
     * Add agent message to chat
     */
    function addAgentMessage(text) {
        const messageEl = createMessageElement('agent', text);
        appendMessage(messageEl);
        scrollToBottom();
    }
    
    /**
     * Add system message to chat
     */
    function addSystemMessage(text, type = 'info') {
        const messageEl = createSystemMessage(text, type);
        appendMessage(messageEl);
        scrollToBottom();
    }
    
    /**
     * Create message element
     */
    function createMessageElement(sender, text) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${sender === 'user' ? 'user-message' : ''}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="bi bi-person"></i>' : '<i class="bi bi-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const textEl = document.createElement('p');
        textEl.className = 'message-text';
        textEl.innerHTML = formatMessage(text);
        
        const timeEl = document.createElement('div');
        timeEl.className = 'message-time';
        timeEl.textContent = new Date().toLocaleTimeString();
        
        content.appendChild(textEl);
        content.appendChild(timeEl);
        
        if (sender !== 'user') {
            const actions = document.createElement('div');
            actions.className = 'message-actions';
            actions.innerHTML = `
                <button class="message-action-btn" onclick="copyMessage(this)" title="Copy message">
                    <i class="bi bi-clipboard"></i>
                </button>
                <button class="message-action-btn" onclick="regenerateMessage(this)" title="Regenerate">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
            `;
            content.appendChild(actions);
        }
        
        messageEl.appendChild(avatar);
        messageEl.appendChild(content);
        
        return messageEl;
    }
    
    /**
     * Create system message element
     */
    function createSystemMessage(text, type = 'info') {
        const messageEl = document.createElement('div');
        messageEl.className = 'message system-message';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        if (type === 'error') {
            content.style.backgroundColor = '#fef2f2';
            content.style.borderColor = '#fecaca';
            content.style.color = '#dc2626';
        }
        
        const textEl = document.createElement('p');
        textEl.className = 'message-text';
        textEl.innerHTML = formatMessage(text);
        
        content.appendChild(textEl);
        messageEl.appendChild(content);
        
        return messageEl;
    }
    
    /**
     * Append message to container
     */
    function appendMessage(messageEl) {
        // Hide welcome state if visible
        if (welcomeState && welcomeState.style.display !== 'none') {
            welcomeState.style.display = 'none';
        }
        
        messagesContainer.appendChild(messageEl);
    }
    
    /**
     * Clear all messages
     */
    function clearMessages() {
        const messages = messagesContainer.querySelectorAll('.message, .typing-indicator');
        messages.forEach(msg => msg.remove());
    }
    
    /**
     * Show typing indicator
     */
    function showTypingIndicator() {
        if (isTyping) return;
        
        isTyping = true;
        const typingEl = document.createElement('div');
        typingEl.className = 'typing-indicator';
        typingEl.innerHTML = `
            <div class="typing-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="typing-content">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingEl);
        scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    function hideTypingIndicator() {
        isTyping = false;
        const typingEl = messagesContainer.querySelector('.typing-indicator');
        if (typingEl) {
            typingEl.remove();
        }
    }
    
    /**
     * Scroll to bottom of messages
     */
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    /**
     * Format message text
     */
    function formatMessage(text) {
        // Convert newlines to <br>
        let formatted = text.replace(/\n/g, '<br>');
        
        // Make URLs clickable
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return formatted;
    }
    
    /**
     * Render conversations list
     */
    function renderConversations() {
        if (!conversations || conversations.length === 0) {
            conversationList.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-chat-dots empty-icon"></i>
                    <p class="empty-text">No conversations yet</p>
                    <p class="empty-subtext">Start a new chat to begin</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        conversations.forEach(conversation => {
            const date = new Date(conversation.timestamp);
            const isActive = currentConversationId === conversation.conversation_id;
            
            html += `
                <div class="conversation-item ${isActive ? 'active' : ''}" 
                     data-conversation-id="${conversation.conversation_id}"
                     role="button" tabindex="0">
                    <div class="conversation-title">${getAgentName(conversation.agent_type)}</div>
                    <div class="conversation-preview">${conversation.preview || 'No preview available'}</div>
                    <div class="conversation-time">${formatRelativeTime(date)}</div>
                </div>
            `;
        });
        
        conversationList.innerHTML = html;
        
        // Add click listeners
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', handleConversationClick);
            item.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleConversationClick.call(this);
                }
            });
        });
    }
    
    /**
     * Handle conversation click
     */
    async function handleConversationClick() {
        const conversationId = this.getAttribute('data-conversation-id');
        await loadConversation(conversationId);
    }
    
    /**
     * Load a specific conversation
     */
    async function loadConversation(conversationId) {
        try {
            showLoadingOverlay('Loading conversation...');
            
            const data = await agentService.getConversationHistory(conversationId);
            
            // Find and select the agent
            const agent = agents.find(a => a.agent_type === data.agent_type);
            if (agent) {
                selectAgent(agent);
            }
            
            // Clear messages and load history
            clearMessages();
            
            data.messages.forEach(message => {
                if (message.role === 'user') {
                    addUserMessage(message.content);
                } else if (message.role === 'assistant') {
                    addAgentMessage(message.content);
                } else if (message.role === 'system') {
                    addSystemMessage(message.content);
                }
            });
            
            // Update current conversation
            currentConversationId = conversationId;
            
            // Update active conversation in list
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.toggle('active', item.getAttribute('data-conversation-id') === conversationId);
            });
            
            hideLoadingOverlay();
            
        } catch (error) {
            console.error('Error loading conversation:', error);
            hideLoadingOverlay();
            showError('Failed to load conversation. Please try again.');
        }
    }
    
    /**
     * Handle conversation search
     */
    function handleConversationSearch() {
        const query = conversationSearch.value.toLowerCase();
        const items = document.querySelectorAll('.conversation-item');
        
        items.forEach(item => {
            const title = item.querySelector('.conversation-title').textContent.toLowerCase();
            const preview = item.querySelector('.conversation-preview').textContent.toLowerCase();
            const matches = title.includes(query) || preview.includes(query);
            item.style.display = matches ? 'block' : 'none';
        });
    }
    
    /**
     * Handle clear all conversations
     */
    async function handleClearAllConversations() {
        if (!confirm('Are you sure you want to clear all conversations? This action cannot be undone.')) {
            return;
        }
        
        try {
            // Clear conversations (implement API call if available)
            conversations = [];
            renderConversations();
            startNewChat();
        } catch (error) {
            console.error('Error clearing conversations:', error);
            showError('Failed to clear conversations. Please try again.');
        }
    }
    
    /**
     * Handle outside clicks (for mobile sidebar)
     */
    function handleOutsideClick(e) {
        if (window.innerWidth <= 768) {
            if (!conversationSidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                conversationSidebar.classList.remove('open');
            }
        }
    }
    
    /**
     * Handle window resize
     */
    function handleWindowResize() {
        if (window.innerWidth > 768) {
            conversationSidebar.classList.remove('open');
        }
    }
    
    /**
     * Show loading overlay
     */
    function showLoadingOverlay(text = 'Loading...') {
        const loadingText = loadingOverlay.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = text;
        }
        loadingOverlay.style.display = 'flex';
    }
    
    /**
     * Hide loading overlay
     */
    function hideLoadingOverlay() {
        loadingOverlay.style.display = 'none';
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        addSystemMessage(message, 'error');
    }
    
    /**
     * Get agent name from type
     */
    function getAgentName(agentType) {
        const agent = agents.find(a => a.agent_type === agentType);
        return agent ? agent.name : agentType;
    }
    
    /**
     * Format relative time
     */
    function formatRelativeTime(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    }
    
    // Global functions for message actions
    window.copyMessage = function(btn) {
        const messageText = btn.closest('.message-content').querySelector('.message-text').textContent;
        navigator.clipboard.writeText(messageText).then(() => {
            // Show feedback
            const originalIcon = btn.innerHTML;
            btn.innerHTML = '<i class="bi bi-check"></i>';
            setTimeout(() => {
                btn.innerHTML = originalIcon;
            }, 1000);
        });
    };
    
    window.regenerateMessage = function(btn) {
        // Find the user message before this agent message
        const agentMessage = btn.closest('.message');
        const messages = Array.from(messagesContainer.querySelectorAll('.message'));
        const agentIndex = messages.indexOf(agentMessage);
        
        if (agentIndex > 0) {
            const userMessage = messages[agentIndex - 1];
            if (userMessage.classList.contains('user-message')) {
                const userText = userMessage.querySelector('.message-text').textContent;
                
                // Remove the agent message
                agentMessage.remove();
                
                // Resend the user message
                setInputState(false);
                showTypingIndicator();
                
                agentService.sendMessage(selectedAgent.agent_type, userText)
                    .then(response => {
                        hideTypingIndicator();
                        addAgentMessage(response.response);
                        setInputState(true);
                    })
                    .catch(error => {
                        console.error('Error regenerating message:', error);
                        hideTypingIndicator();
                        addSystemMessage('Failed to regenerate message. Please try again.', 'error');
                        setInputState(true);
                    });
            }
        }
    };
    
    // Export for debugging
    window.cleanChat = {
        selectAgent,
        startNewChat,
        loadConversation,
        clearMessages,
        showError
    };
});
