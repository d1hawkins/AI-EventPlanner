// Simple toast notification function
function showToast(message, type = 'info') {
    console.log(`Toast: ${message} (${type})`);
    
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = message;
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 500);
    }, 3000);
}

// Global variables
let token = localStorage.getItem('token');
let currentConversationId = null;
let currentEventId = null;
let currentTasks = [];
let socket = null;
let thinkingIndicator = null; // Reference to the thinking indicator element

// DOM elements
const authContainer = document.getElementById('auth-container');
const chatInterface = document.getElementById('chat-interface');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const registerFormContainer = document.getElementById('register-form-container');
const showRegisterLink = document.getElementById('show-register');
const showLoginLink = document.getElementById('show-login');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');
const conversationsList = document.getElementById('conversations-list');
const newConversationBtn = document.getElementById('new-conversation-btn');
const conversationTitle = document.getElementById('conversation-title');
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const searchInput = document.getElementById('search-conversations');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

// Event listeners
document.addEventListener('DOMContentLoaded', init);

// Tab switching
if (tabButtons) {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

// Initialize the application
function init() {
    // Set up event listeners
    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (registerForm) registerForm.addEventListener('submit', handleRegister);
    if (showRegisterLink) showRegisterLink.addEventListener('click', showRegisterForm);
    if (showLoginLink) showLoginLink.addEventListener('click', showLoginForm);
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
    if (newConversationBtn) newConversationBtn.addEventListener('click', createNewConversation);
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    if (searchInput) {
        searchInput.addEventListener('input', searchConversations);
    }
    
    // Set up proposal and plan buttons
    setupProposalAndPlanButtons();
    
    // Set up task management
    setupTaskManagement();
    
    // Check if user is logged in
    if (token) {
        // User is logged in
        fetchUserInfo();
        fetchConversations();
        showChatInterface();
        
        // Show welcome message with instructions for new users
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <h2>Welcome to AI Event Planner!</h2>
                    <p>To get started, click the <strong>+ New Conversation</strong> button in the sidebar.</p>
                    <button id="welcome-new-conversation-btn" class="action-btn">
                        <i class="fas fa-plus"></i>
                        Start New Conversation
                    </button>
                </div>
            `;
            
            // Add event listener to the welcome button
            const welcomeNewConversationBtn = document.getElementById('welcome-new-conversation-btn');
            if (welcomeNewConversationBtn) {
                welcomeNewConversationBtn.addEventListener('click', createNewConversation);
            }
        }
    } else {
        // User is not logged in
        showAuthContainer();
    }
}

// Set up proposal and plan buttons
function setupProposalAndPlanButtons() {
    const generateProposalBtn = document.getElementById('generate-proposal-btn');
    const generatePlanBtn = document.getElementById('generate-plan-btn');
    const exportProposalBtn = document.getElementById('export-proposal-btn');
    const printProposalBtn = document.getElementById('print-proposal-btn');
    const exportPlanBtn = document.getElementById('export-plan-btn');
    const printPlanBtn = document.getElementById('print-plan-btn');
    const refreshTasksBtn = document.getElementById('refresh-tasks-btn');
    
    if (generateProposalBtn) {
        generateProposalBtn.addEventListener('click', requestProposal);
    }
    if (generatePlanBtn) {
        generatePlanBtn.addEventListener('click', requestProjectPlan);
    }
    if (exportProposalBtn) {
        exportProposalBtn.addEventListener('click', () => exportDocument('proposal'));
    }
    if (printProposalBtn) {
        printProposalBtn.addEventListener('click', () => printDocument('proposal'));
    }
    if (exportPlanBtn) {
        exportPlanBtn.addEventListener('click', () => exportDocument('project-plan'));
    }
    if (printPlanBtn) {
        printPlanBtn.addEventListener('click', () => printDocument('project-plan'));
    }
    if (refreshTasksBtn) {
        refreshTasksBtn.addEventListener('click', fetchTasks);
    }
}

// Set up task management
function setupTaskManagement() {
    // Add event listeners for task filters
    const statusFilter = document.getElementById('status-filter');
    const agentFilter = document.getElementById('agent-filter');
    const taskSearch = document.getElementById('task-search');
    
    if (statusFilter) statusFilter.addEventListener('change', filterTasks);
    if (agentFilter) agentFilter.addEventListener('change', filterTasks);
    if (taskSearch) taskSearch.addEventListener('input', filterTasks);
}

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username-input').value;
    const password = document.getElementById('password-input').value;
    
    try {
        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'username': username,
                'password': password
            })
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }
        
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        
        fetchUserInfo();
        fetchConversations();
        showChatInterface();
    } catch (error) {
        showToast('Login failed: ' + error.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('reg-email').value;
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                username,
                password
            })
        });
        
        if (!response.ok) {
            throw new Error('Registration failed');
        }
        
        showToast('Registration successful! Please login.', 'success');
        showLoginForm();
    } catch (error) {
        showToast('Registration failed: ' + error.message, 'error');
    }
}

function handleLogout() {
    token = null;
    localStorage.removeItem('token');
    closeWebSocket();
    showAuthContainer();
}

async function fetchUserInfo() {
    try {
        const response = await fetch('/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch user info');
        }
        
        const user = await response.json();
        usernameSpan.textContent = user.username;
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
}

// UI functions
function showAuthContainer() {
    if (authContainer) authContainer.style.display = 'flex';
    if (chatInterface) chatInterface.style.display = 'none';
}

function showChatInterface() {
    if (authContainer) authContainer.style.display = 'none';
    if (chatInterface) chatInterface.style.display = 'flex';
}

function showRegisterForm() {
    if (registerFormContainer) registerFormContainer.style.display = 'block';
    if (loginForm) loginForm.parentElement.style.display = 'none';
}

function showLoginForm() {
    if (registerFormContainer) registerFormContainer.style.display = 'none';
    if (loginForm) loginForm.parentElement.style.display = 'block';
}

// Tab switching function
function switchTab(tabName) {
    // Update active tab button
    tabButtons.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update active tab pane
    tabPanes.forEach(pane => {
        if (pane.id === `${tabName}-content`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// Search conversations
function searchConversations() {
    const searchTerm = searchInput.value.toLowerCase();
    const conversationItems = document.querySelectorAll('.conversation-item');
    
    conversationItems.forEach(item => {
        const title = item.querySelector('.conversation-title').textContent.toLowerCase();
        if (title.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Conversation functions
async function fetchConversations() {
    try {
        const response = await fetch('/api/conversations', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch conversations');
        }
        
        const conversations = await response.json();
        renderConversations(conversations);
        
        // If there are conversations, load the first one
        if (conversations.length > 0) {
            loadConversation(conversations[0].id);
        } else {
            // If there are no conversations (new user), automatically create one
            await createNewConversation();
        }
    } catch (error) {
        console.error('Error fetching conversations:', error);
        showToast('Error fetching conversations', 'error');
    }
}

function renderConversations(conversations) {
    if (!conversationsList) return;
    
    conversationsList.innerHTML = '';
    
    conversations.forEach(conversation => {
        const conversationItem = document.createElement('div');
        conversationItem.className = 'conversation-item';
        conversationItem.dataset.id = conversation.id;
        
        const title = document.createElement('div');
        title.className = 'conversation-title';
        title.textContent = conversation.title;
        
        const date = document.createElement('div');
        date.className = 'conversation-date';
        date.textContent = new Date(conversation.updated_at).toLocaleString();
        
        conversationItem.appendChild(title);
        conversationItem.appendChild(date);
        
        conversationItem.addEventListener('click', () => {
            loadConversation(conversation.id);
        });
        
        conversationsList.appendChild(conversationItem);
    });
}

async function createNewConversation() {
    try {
        const response = await fetch('/api/conversations', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'New Conversation'
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create conversation');
        }
        
        const conversation = await response.json();
        
        // Add the new conversation to the UI
        if (conversationsList) {
            const conversationItem = document.createElement('div');
            conversationItem.className = 'conversation-item';
            conversationItem.dataset.id = conversation.id;
            
            const title = document.createElement('div');
            title.className = 'conversation-title';
            title.textContent = conversation.title;
            
            const date = document.createElement('div');
            date.className = 'conversation-date';
            date.textContent = new Date(conversation.updated_at).toLocaleString();
            
            conversationItem.appendChild(title);
            conversationItem.appendChild(date);
            
            conversationItem.addEventListener('click', () => {
                loadConversation(conversation.id);
            });
            
            // Add to the beginning of the list
            if (conversationsList.firstChild) {
                conversationsList.insertBefore(conversationItem, conversationsList.firstChild);
            } else {
                conversationsList.appendChild(conversationItem);
            }
        }
        
        // Load the new conversation
        loadConversation(conversation.id);
        
        // Show toast notification
        showToast('New conversation created', 'success');
    } catch (error) {
        console.error('Error creating conversation:', error);
        showToast('Error creating conversation', 'error');
    }
}

async function loadConversation(conversationId) {
    // Close existing WebSocket connection
    closeWebSocket();
    
    // Update current conversation ID
    currentConversationId = conversationId;
    
    // Update active conversation in the list
    const conversationItems = document.querySelectorAll('.conversation-item');
    conversationItems.forEach(item => {
        if (item.dataset.id == conversationId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    try {
        // Fetch conversation details
        const response = await fetch(`/api/conversations/${conversationId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch conversation');
        }
        
        const conversation = await response.json();
        
        // Update conversation title
        if (conversationTitle) conversationTitle.textContent = conversation.title;
        
        // Clear messages container
        if (messagesContainer) messagesContainer.innerHTML = '';
        
        // Reset proposal and plan content
        resetProposalAndPlan();
        
        // Connect to WebSocket
        connectWebSocket(conversationId);
    } catch (error) {
        console.error('Error loading conversation:', error);
        showToast('Error loading conversation', 'error');
    }
}

// Reset proposal and plan content
function resetProposalAndPlan() {
    const proposalContent = document.getElementById('proposal-content');
    const projectPlanContent = document.getElementById('project-plan-content');
    const exportProposalBtn = document.getElementById('export-proposal-btn');
    const printProposalBtn = document.getElementById('print-proposal-btn');
    const exportPlanBtn = document.getElementById('export-plan-btn');
    const printPlanBtn = document.getElementById('print-plan-btn');
    
    if (!proposalContent || !projectPlanContent) return;
    
    // Reset proposal content
    proposalContent.querySelector('.plan-body').innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <h4>No Proposal Yet</h4>
            <p>Complete the information gathering process to generate a proposal.</p>
            <button id="generate-proposal-btn" class="action-btn">
                <i class="fas fa-magic"></i>
                Generate Proposal
            </button>
        </div>
    `;
    
    // Reset project plan content - keep the task management structure
    const planBody = projectPlanContent.querySelector('.plan-body');
    planBody.innerHTML = `
        <div id="task-management" class="task-management">
            <div class="task-filters">
                <div class="filter-group">
                    <label for="status-filter">Status:</label>
                    <select id="status-filter">
                        <option value="all">All</option>
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="agent-filter">Assigned To:</label>
                    <select id="agent-filter">
                        <option value="all">All</option>
                        <option value="resource_planning">Resource Planning</option>
                        <option value="financial">Financial</option>
                        <option value="stakeholder_management">Stakeholder</option>
                        <option value="marketing_communications">Marketing</option>
                        <option value="project_management">Project Management</option>
                        <option value="analytics">Analytics</option>
                        <option value="compliance_security">Compliance</option>
                    </select>
                </div>
                <div class="search-task">
                    <input type="text" id="task-search" placeholder="Search tasks...">
                </div>
            </div>
            
            <!-- Task Progress Overview -->
            <div class="task-progress">
                <div class="progress-bar-container">
                    <div class="progress-label">Overall Progress</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="overall-progress" style="width: 0%;">0%</div>
                    </div>
                </div>
                <div class="task-stats">
                    <div class="stat-item">
                        <div class="stat-value" id="total-tasks">0</div>
                        <div class="stat-label">Total</div>
                    </div>
                    <div class="stat-item pending">
                        <div class="stat-value" id="pending-tasks">0</div>
                        <div class="stat-label">Pending</div>
                    </div>
                    <div class="stat-item in-progress">
                        <div class="stat-value" id="in-progress-tasks">0</div>
                        <div class="stat-label">In Progress</div>
                    </div>
                    <div class="stat-item completed">
                        <div class="stat-value" id="completed-tasks">0</div>
                        <div class="stat-label">Completed</div>
                    </div>
                </div>
            </div>
            
            <!-- Task List -->
            <div class="task-list-container">
                <h4>Tasks</h4>
                <div id="task-list" class="task-list">
                    <!-- Tasks will be populated here -->
                    <div class="empty-task-list">
                        <p>No tasks available. Generate a project plan first.</p>
                        <button id="generate-plan-btn" class="action-btn" disabled>
                            <i class="fas fa-magic"></i>
                            Generate Plan
                        </button>
                        <p class="note">Proposal approval required</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Disable export and print buttons
    if (exportProposalBtn) exportProposalBtn.disabled = true;
    if (printProposalBtn) printProposalBtn.disabled = true;
    if (exportPlanBtn) exportPlanBtn.disabled = true;
    if (printPlanBtn) printPlanBtn.disabled = true;
    
    // Add event listeners to the new buttons
    const newGenerateProposalBtn = document.getElementById('generate-proposal-btn');
    const newGeneratePlanBtn = document.getElementById('generate-plan-btn');
    
    if (newGenerateProposalBtn) {
        newGenerateProposalBtn.addEventListener('click', requestProposal);
    }
    
    if (newGeneratePlanBtn) {
        newGeneratePlanBtn.addEventListener('click', requestProjectPlan);
    }
    
    // Set up task management again
    setupTaskManagement();
}

// Show thinking indicator in the chat
function showThinkingIndicator() {
    // Remove any existing thinking indicator
    removeThinkingIndicator();
    
    // Create thinking indicator element
    thinkingIndicator = document.createElement('div');
    thinkingIndicator.className = 'message assistant thinking';
    thinkingIndicator.id = 'thinking-indicator';
    
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    
    // Create the thinking animation with dots
    const thinkingContent = document.createElement('div');
    thinkingContent.className = 'thinking-content';
    
    // Add the spinner
    const spinner = document.createElement('div');
    spinner.className = 'thinking-spinner';
    thinkingContent.appendChild(spinner);
    
    // Add "Thinking" text with animated ellipsis
    const text = document.createElement('span');
    text.textContent = 'Thinking';
    thinkingContent.appendChild(text);
    
    contentElement.appendChild(thinkingContent);
    thinkingIndicator.appendChild(contentElement);
    
    // Add time element
    const timeElement = document.createElement('div');
    timeElement.className = 'message-time';
    timeElement.textContent = formatTime(new Date());
    thinkingIndicator.appendChild(timeElement);
    
    // Add to messages container
    if (messagesContainer) {
        messagesContainer.appendChild(thinkingIndicator);
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    return thinkingIndicator;
}

// Remove thinking indicator from the chat
function removeThinkingIndicator() {
    if (thinkingIndicator && thinkingIndicator.parentNode) {
        thinkingIndicator.parentNode.removeChild(thinkingIndicator);
        thinkingIndicator = null;
    }
}

// WebSocket functions
function connectWebSocket(conversationId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/${conversationId}?token=${token}`;
    
    // Remove any existing connection status indicators
    const existingStatus = document.getElementById('ws-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Add connection status indicator to the UI
    const chatHeader = document.getElementById('chat-header');
    if (chatHeader) {
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'ws-status';
        statusIndicator.className = 'ws-status connecting';
        statusIndicator.textContent = 'Connecting...';
        chatHeader.appendChild(statusIndicator);
    }
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected', 'Connected');
    };
    
    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        // Remove thinking indicator when any message is received
        removeThinkingIndicator();
        
        if (message.error) {
            console.error('WebSocket error:', message.error);
            showErrorMessage(message.error);
            return;
        }
        
        // Handle ephemeral system messages (don't display in chat)
        if (message.ephemeral === true) {
            console.log('Received ephemeral message:', message.content);
            
            // If it's a connection message, update the connection status
            if (message.role === "system" && 
                message.content === "Connected to conversation. You can now send messages.") {
                updateConnectionStatus('connected', 'Connected');
            }
            return;
        }
        
        // Skip rendering system connection messages (for backward compatibility)
        if (message.role === "system" && 
            message.content === "Connected to conversation. You can now send messages.") {
            // Update connection status instead of showing a new message
            updateConnectionStatus('connected', 'Connected');
            return;
        }
        
        renderMessage(message);
        
        // Check if this is a proposal or plan
        if (message.role === 'assistant') {
            if (message.content.includes('Event Planning Proposal') || 
                message.content.toLowerCase().includes('proposal:')) {
                // This looks like a proposal, display it in the proposal tab
                displayProposal(message.content);
                
                // Enable the generate plan button
                const generatePlanBtn = document.getElementById('generate-plan-btn');
                if (generatePlanBtn) {
                    generatePlanBtn.disabled = false;
                }
                const noteElement = document.querySelector('.note');
                if (noteElement) noteElement.remove();
            }
            else if (message.content.includes('Project Plan') || 
                    message.content.toLowerCase().includes('task delegation:')) {
                // This looks like a project plan, display it in the plan tab
                displayProjectPlan(message.content);
            }
        }
    };
    
    socket.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus('disconnected', 'Disconnected');
        
        // Remove thinking indicator if connection is closed
        removeThinkingIndicator();
        
        // Attempt to reconnect after a delay
        setTimeout(() => {
            if (currentConversationId) {
                updateConnectionStatus('connecting', 'Reconnecting...');
                connectWebSocket(currentConversationId);
            }
        }, 3000);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('error', 'Connection Error');
        showErrorMessage('WebSocket connection error. Please try refreshing the page.');
        
        // Remove thinking indicator if there's an error
        removeThinkingIndicator();
    };
}

function updateConnectionStatus(status, text) {
    const statusIndicator = document.getElementById('ws-status');
    if (statusIndicator) {
        statusIndicator.className = `ws-status ${status}`;
        statusIndicator.textContent = text;
    }
}

function showErrorMessage(message) {
    // Create a system message to show errors
    const errorMsg = {
        role: 'system',
        content: `Error: ${message}`,
        timestamp: new Date().toISOString()
    };
    renderMessage(errorMsg);
}

function closeWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
    }
}

async function sendMessage() {
    if (!messageInput) return;
    
    const content = messageInput.value.trim();
    
    if (!content) {
        return;
    }
    
    // If there's no active conversation or socket connection, create a new conversation first
    if (!currentConversationId || !socket || socket.readyState !== WebSocket.OPEN) {
        console.log('No active conversation or socket connection. Creating a new conversation...');
        
        // Show a temporary message to the user
        showToast('Creating a new conversation...', 'info');
        
        // Create a new conversation
        try {
            await createNewConversation();
            
            // After creating a new conversation, check if we have a valid socket connection
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                console.log('Socket still not ready after creating conversation. Waiting...');
                showToast('Connecting to server...', 'info');
                
                // Wait a bit for the socket to connect
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                if (!socket || socket.readyState !== WebSocket.OPEN) {
                    showErrorMessage('Could not establish connection. Please try again or refresh the page.');
                    return;
                }
            }
        } catch (error) {
            console.error('Error creating conversation:', error);
            showErrorMessage('Failed to create a new conversation. Please try again or refresh the page.');
            return;
        }
    }
    
    try {
        const message = {
            content
        };
        
        // Show the user message immediately in the UI
        const userMessage = {
            role: 'user',
            content: content,
            timestamp: new Date().toISOString()
        };
        renderMessage(userMessage);
        
        // Show thinking indicator
        showThinkingIndicator();
        
        // Send the message
        socket.send(JSON.stringify(message));
        
        // Clear input
        messageInput.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
        showErrorMessage('Failed to send message. Please try again.');
        
        // Remove thinking indicator if there's an error
        removeThinkingIndicator();
    }
}

// Request proposal function
function requestProposal() {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        showToast('Cannot generate proposal: No active connection', 'error');
        return;
    }
    
    const proposalContent = document.getElementById('proposal-content');
    if (!proposalContent) return;
    
    // Show loading state
    proposalContent.querySelector('.plan-body').innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p>Generating comprehensive proposal...</p>
        </div>
    `;
    
    // Show thinking indicator in chat as well
    showThinkingIndicator();
    
    // Send proposal request
    const message = {
        content: "Can you create a proposal for this event?"
    };
    socket.send(JSON.stringify(message));
}

// Request project plan function
function requestProjectPlan() {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        showToast('Cannot generate project plan: No active connection', 'error');
        return;
    }
    
    const projectPlanContent = document.getElementById('project-plan-content');
    if (!projectPlanContent) return;
    
    // Show loading state
    projectPlanContent.querySelector('.plan-body').innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p>Generating detailed project plan...</p>
        </div>
    `;
    
    // Show thinking indicator in chat as well
    showThinkingIndicator();
    
    // Send project plan request
    const message = {
        content: "I approve the proposal. Please create a project plan."
    };
    socket.send(JSON.stringify(message));
}

// Helper function to render messages
function renderMessage(message) {
    if (!messagesContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${message.role}`;
    
    // Add error class for system error messages
    if (message.role === 'system' && message.content.toLowerCase().includes('error')) {
        messageElement.classList.add('error');
    }
    
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    
    // Process content based on message role
    if (message.role === 'assistant') {
        try {
            // Parse markdown for assistant messages
            if (typeof marked !== 'undefined') {
                contentElement.innerHTML = marked.parse(message.content);
                
                // Apply syntax highlighting to code blocks
                if (typeof hljs !== 'undefined') {
                    document.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                }
            } else {
                contentElement.textContent = message.content;
            }
        } catch (error) {
            console.error('Error parsing markdown:', error);
            contentElement.textContent = message.content;
        }
    } else {
        // For user and system messages, just escape HTML and add line breaks
        contentElement.innerHTML = escapeHtml(message.content).replace(/\n/g, '<br>');
    }
    
    const timeElement = document.createElement('div');
    timeElement.className = 'message-time';
    
    if (message.timestamp) {
        const date = new Date(message.timestamp);
        timeElement.textContent = formatTime(date);
    } else {
        timeElement.textContent = formatTime(new Date());
    }
    
    messageElement.appendChild(contentElement);
    messageElement.appendChild(timeElement);
    
    messagesContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Helper function to escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Helper function to format timestamps
function formatTime(date) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// Fetch tasks for the current event
async function fetchTasks() {
    if (!currentEventId) {
        console.log('No event ID available');
        return;
    }
    
    // Add debug info to the UI
    const projectPlanContent = document.getElementById('project-plan-content');
    if (projectPlanContent) {
        const debugInfo = document.createElement('div');
        debugInfo.className = 'debug-info';
        debugInfo.innerHTML = `<strong>Debug Info:</strong> Fetching tasks for Event ID: ${currentEventId}`;
        projectPlanContent.appendChild(debugInfo);
    }
    
    try {
        const url = `/api/events/${currentEventId}/tasks`;
        console.log(`Fetching tasks from: ${url}`);
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log(`API response status: ${response.status}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API error response: ${errorText}`);
            throw new Error(`Failed to fetch tasks: ${response.status} ${errorText}`);
        }
        
        const tasks = await response.json();
        console.log(`Received ${tasks.length} tasks from API`);
        
        // Add debug info to the UI
        if (projectPlanContent) {
            const tasksDebugInfo = document.createElement('div');
            tasksDebugInfo.className = 'debug-info';
            tasksDebugInfo.innerHTML = `<strong>Debug Info:</strong> Received ${tasks.length} tasks from API`;
            projectPlanContent.appendChild(tasksDebugInfo);
        }
        
        currentTasks = tasks;
        renderTasks(tasks);
        updateTaskStats(tasks);
        
        // Enable export and print buttons
        const exportPlanBtn = document.getElementById('export-plan-btn');
        const printPlanBtn = document.getElementById('print-plan-btn');
        if (exportPlanBtn) exportPlanBtn.disabled = false;
        if (printPlanBtn) printPlanBtn.disabled = false;
        
        return tasks;
    } catch (error) {
        console.error('Error fetching tasks:', error);
        
        // Add error info to the UI
        if (projectPlanContent) {
            const errorInfo = document.createElement('div');
            errorInfo.className = 'debug-info error';
            errorInfo.innerHTML = `<strong>Error:</strong> ${error.message}`;
            projectPlanContent.appendChild(errorInfo);
        }
        
        showToast('Error fetching tasks: ' + error.message, 'error');
        return [];
    }
}

// Render tasks in the task list
function renderTasks(tasks) {
    const taskList = document.getElementById('task-list');
    if (!taskList) return;
    
    if (tasks.length === 0) {
        taskList.innerHTML = `
            <div class="empty-task-list">
                <p>No tasks available. Generate a project plan first.</p>
                <button id="generate-plan-btn" class="action-btn">
                    <i class="fas fa-magic"></i>
                    Generate Plan
                </button>
            </div>
        `;
        
        // Add event listener to the new button
        const newGeneratePlanBtn = document.getElementById('generate-plan-btn');
        if (newGeneratePlanBtn) {
            newGeneratePlanBtn.addEventListener('click', requestProjectPlan);
        }
        
        return;
    }
    
    taskList.innerHTML = '';
    
    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        taskItem.dataset.id = task.id;
        taskItem.dataset.status = task.status;
        taskItem.dataset.agent = task.assigned_agent || '';
        
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
        
        taskItem.innerHTML = `
            <div class="task-header">
                <div class="task-title">${task.title}</div>
                <div class="task-status ${task.status}">${formatStatus(task.status)}</div>
            </div>
            <div class="task-description">${task.description || 'No description'}</div>
            <div class="task-meta">
                <div class="task-agent">
                    <i class="fas fa-user-circle"></i>
                    ${formatAgentName(task.assigned_agent)}
                </div>
                <div class="task-due-date">Due: ${dueDate}</div>
            </div>
            <div class="task-actions">
                ${getTaskActionButtons(task)}
            </div>
        `;
        
        // Add event listeners for task action buttons
        taskItem.querySelectorAll('.task-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                const taskId = task.id;
                handleTaskAction(taskId, action);
            });
        });
        
        taskList.appendChild(taskItem);
    });
}

// Format status for display
function formatStatus(status) {
    const statusMap = {
        'pending': 'Pending',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    };
    
    return statusMap[status] || status;
}

// Format agent name for display
function formatAgentName(agent) {
    if (!agent) return 'Unassigned';
    
    const agentMap = {
        'resource_planning': 'Resource Planning',
        'financial': 'Financial',
        'stakeholder_management': 'Stakeholder',
        'marketing_communications': 'Marketing',
        'project_management': 'Project Management',
        'analytics': 'Analytics',
        'compliance_security': 'Compliance'
    };
    
    return agentMap[agent] || agent;
}

// Get appropriate action buttons based on task status
function getTaskActionButtons(task) {
    let buttons = '';
    
    switch (task.status) {
        case 'pending':
            buttons = `<button class="task-action-btn start" data-action="start">
                <i class="fas fa-play"></i> Start
            </button>`;
            break;
        case 'in_progress':
            buttons = `<button class="task-action-btn complete" data-action="complete">
                <i class="fas fa-check"></i> Complete
            </button>`;
            break;
        case 'completed':
            // No actions for completed tasks
            break;
        case 'cancelled':
            buttons = `<button class="task-action-btn start" data-action="restart">
                <i class="fas fa-redo"></i> Restart
            </button>`;
            break;
    }
    
    return buttons;
}

// Handle task action button clicks
async function handleTaskAction(taskId, action) {
    let newStatus = '';
    
    switch (action) {
        case 'start':
        case 'restart':
            newStatus = 'in_progress';
            break;
        case 'complete':
            newStatus = 'completed';
            break;
        case 'cancel':
            newStatus = 'cancelled';
            break;
        default:
            console.error('Unknown action:', action);
            return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: newStatus,
                ...(newStatus === 'in_progress' ? { actual_start_date: new Date().toISOString() } : {}),
                ...(newStatus === 'completed' ? { actual_end_date: new Date().toISOString() } : {})
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task');
        }
        
        // Refresh tasks
        fetchTasks();
        
        // Show toast notification
        showToast(`Task ${formatActionMessage(action)}`, 'success');
        
    } catch (error) {
        console.error('Error updating task:', error);
        showToast('Error updating task', 'error');
    }
}

// Format action message for toast notification
function formatActionMessage(action) {
    switch (action) {
        case 'start':
            return 'started';
        case 'restart':
            return 'restarted';
        case 'complete':
            return 'completed';
        case 'cancel':
            return 'cancelled';
        default:
            return 'updated';
    }
}

// Filter tasks based on selected filters
function filterTasks() {
    const statusFilter = document.getElementById('status-filter').value;
    const agentFilter = document.getElementById('agent-filter').value;
    const searchTerm = document.getElementById('task-search').value.toLowerCase();
    
    const taskItems = document.querySelectorAll('.task-item');
    
    taskItems.forEach(item => {
        const status = item.dataset.status;
        const agent = item.dataset.agent;
        const title = item.querySelector('.task-title').textContent.toLowerCase();
        const description = item.querySelector('.task-description').textContent.toLowerCase();
        
        const statusMatch = statusFilter === 'all' || status === statusFilter;
        const agentMatch = agentFilter === 'all' || agent === agentFilter;
        const searchMatch = !searchTerm || 
                           title.includes(searchTerm) || 
                           description.includes(searchTerm);
        
        if (statusMatch && agentMatch && searchMatch) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Update task statistics
function updateTaskStats(tasks) {
    const totalTasks = tasks.length;
    const pendingTasks = tasks.filter(task => task.status === 'pending').length;
    const inProgressTasks = tasks.filter(task => task.status === 'in_progress').length;
    const completedTasks = tasks.filter(task => task.status === 'completed').length;
    
    // Calculate overall progress percentage
    const progressPercentage = totalTasks > 0 
        ? Math.round((completedTasks / totalTasks) * 100) 
        : 0;
    
    // Update DOM elements
    document.getElementById('total-tasks').textContent = totalTasks;
    document.getElementById('pending-tasks').textContent = pendingTasks;
    document.getElementById('in-progress-tasks').textContent = inProgressTasks;
    document.getElementById('completed-tasks').textContent = completedTasks;
    
    const progressFill = document.getElementById('overall-progress');
    progressFill.style.width = `${progressPercentage}%`;
    progressFill.textContent = `${progressPercentage}%`;
}

// Display proposal in the proposal tab
function displayProposal(content) {
    console.log('Displaying proposal:', content.substring(0, 100) + '...');
    
    // Create a formatted proposal document
    const proposalContent = document.getElementById('proposal-content');
    if (!proposalContent) return;
    
    // Update the plan-body with the formatted content
    const planBody = proposalContent.querySelector('.plan-body');
    planBody.innerHTML = `
        <div class="proposal-document">
            <div class="document-content">
                ${marked.parse(content)}
            </div>
            <div class="document-footer">
                <div class="document-status">
                    <i class="fas fa-info-circle"></i>
                    <span>Pending approval</span>
                </div>
                <div class="document-actions">
                    <button id="approve-proposal-btn" class="action-btn">
                        <i class="fas fa-check"></i>
                        Approve
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Enable export and print buttons
    const exportProposalBtn = document.getElementById('export-proposal-btn');
    const printProposalBtn = document.getElementById('print-proposal-btn');
    if (exportProposalBtn) exportProposalBtn.disabled = false;
    if (printProposalBtn) printProposalBtn.disabled = false;
    
    // Add event listener to approve button
    const approveProposalBtn = document.getElementById('approve-proposal-btn');
    if (approveProposalBtn) {
        approveProposalBtn.addEventListener('click', () => {
            // Update the document status
            const documentStatus = planBody.querySelector('.document-status');
            if (documentStatus) {
                documentStatus.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <span class="approved">Approved</span>
                `;
            }
            
            // Enable the generate plan button
            const generatePlanBtn = document.getElementById('generate-plan-btn');
            if (generatePlanBtn) {
                generatePlanBtn.disabled = false;
            }
            
            // Remove the note about proposal approval
            const noteElement = document.querySelector('.note');
            if (noteElement) noteElement.remove();
            
            // Show toast notification
            showToast('Proposal approved. Project plan can now be generated.', 'success');
            
            // Hide the approve button
            approveProposalBtn.style.display = 'none';
        });
    }
    
    showToast('Proposal generated successfully', 'success');
}

// Display project plan in the project plan tab
function displayProjectPlan(content) {
    console.log('Displaying project plan:', content.substring(0, 100) + '...');
    
    // Add the full content to the UI for debugging
    const projectPlanContent = document.getElementById('project-plan-content');
    if (projectPlanContent) {
        const fullContentDebug = document.createElement('div');
        fullContentDebug.className = 'debug-info';
        fullContentDebug.innerHTML = `<strong>Debug Info:</strong> Full content length: ${content.length} characters`;
        projectPlanContent.appendChild(fullContentDebug);
    }
    
    // Try multiple regex patterns to extract event ID
    let eventIdMatch = content.match(/Event ID: ([a-f0-9\-]+|\d+)/i);
    if (!eventIdMatch) {
        eventIdMatch = content.match(/Event ID[:\s]+([a-f0-9\-]+|\d+)/i);
    }
    if (!eventIdMatch) {
        eventIdMatch = content.match(/ID[:\s]+([a-f0-9\-]+|\d+)/i);
    }
    if (!eventIdMatch) {
        // Look for any number that might be an ID
        eventIdMatch = content.match(/\b(\d+)\b/);
    }
    
    if (eventIdMatch && eventIdMatch[1]) {
        currentEventId = eventIdMatch[1];
        console.log('Extracted event ID:', currentEventId);
        
        // Add debug info to the UI
        if (projectPlanContent) {
            const debugInfo = document.createElement('div');
            debugInfo.className = 'debug-info';
            debugInfo.innerHTML = `<strong>Debug Info:</strong> Extracted Event ID: ${currentEventId}`;
            projectPlanContent.appendChild(debugInfo);
            
            // Add the regex match info
            const matchInfo = document.createElement('div');
            matchInfo.className = 'debug-info';
            matchInfo.innerHTML = `<strong>Debug Info:</strong> Regex match: ${eventIdMatch[0]}`;
            projectPlanContent.appendChild(matchInfo);
        }
        
        // Fetch tasks for this event
        fetchTasks();
    } else {
        console.error('Could not extract event ID from project plan content');
        
        // Add error info to the UI
        if (projectPlanContent) {
            const errorInfo = document.createElement('div');
            errorInfo.className = 'debug-info error';
            errorInfo.innerHTML = `<strong>Error:</strong> Could not extract Event ID from content`;
            projectPlanContent.appendChild(errorInfo);
            
            // Show a sample of the content
            const contentSample = document.createElement('div');
            contentSample.className = 'debug-info';
            contentSample.innerHTML = `<strong>Content Sample:</strong> ${content.substring(0, 200)}...`;
            projectPlanContent.appendChild(contentSample);
        }
        
        showToast('Error loading project plan: Could not identify event', 'error');
        
        // Try using a hardcoded event ID for testing
        currentEventId = "1"; // Try with the first event
        console.log('Using hardcoded event ID for testing:', currentEventId);
        
        if (projectPlanContent) {
            const fallbackInfo = document.createElement('div');
            fallbackInfo.className = 'debug-info';
            fallbackInfo.innerHTML = `<strong>Debug Info:</strong> Using fallback Event ID: ${currentEventId}`;
            projectPlanContent.appendChild(fallbackInfo);
        }
        
        // Fetch tasks with the hardcoded ID
        fetchTasks();
    }
    
    showToast('Project plan generated successfully', 'success');
}

// Placeholder functions for document export and print
function exportDocument(documentType) {
    console.log(`Exporting ${documentType} document`);
    showToast(`${documentType === 'proposal' ? 'Proposal' : 'Project plan'} exported successfully`, 'success');
}

function printDocument(documentType) {
    console.log(`Printing ${documentType} document`);
    showToast(`${documentType === 'proposal' ? 'Proposal' : 'Project plan'} sent to printer`, 'success');
}

// Placeholder functions for proposal actions
function approveProposal() {
    console.log('Approving proposal');
    showToast('Proposal approved. Project plan can now be generated.', 'success');
}

function requestProposalChanges() {
    console.log('Requesting proposal changes');
}

function trackProgress() {
    console.log('Tracking progress');
    showToast('Progress tracking view will be implemented in a future update', 'info');
}
