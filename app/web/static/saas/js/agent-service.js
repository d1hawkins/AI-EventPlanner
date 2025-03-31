/**
 * AI Event Planner SaaS - Agent Service
 * 
 * This file contains the JavaScript service for interacting with the agent API endpoints.
 */

class AgentService {
    /**
     * Initialize the agent service
     */
    constructor() {
        this.apiBaseUrl = 'http://localhost:8002/api';
        this.authToken = this.getAuthToken();
        this.currentConversationId = null;
        this.currentAgentType = null;
    }

    /**
     * Get the authentication token from localStorage
     * @returns {string} The authentication token
     */
    getAuthToken() {
        return localStorage.getItem('authToken');
    }

    /**
     * Set the authentication headers for API requests
     * @returns {Object} The headers object
     */
    getHeaders() {
        // Get organization ID from localStorage
        const organizationId = localStorage.getItem('organizationId');
        
        // Return headers with tenant context
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.authToken}`,
            'X-Tenant-ID': organizationId || '1' // Default to organization ID 1 if not set
        };
    }

    /**
     * Handle API errors
     * @param {Response} response - The fetch response
     * @returns {Promise} A promise that resolves to the JSON response or rejects with an error
     */
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json();
            
            // Check if the error is due to subscription limitations
            if (response.status === 403 && errorData.detail && errorData.detail.includes('not available on your current')) {
                throw new Error('subscription_required:' + errorData.detail);
            }
            
            throw new Error(errorData.detail || 'An error occurred');
        }
        
        return response.json();
    }

    /**
     * Get available agents based on subscription tier
     * @returns {Promise<Object>} A promise that resolves to the available agents
     */
    async getAvailableAgents() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/agents/available`, {
                method: 'GET',
                headers: this.getHeaders()
            });
            
            return this.handleResponse(response);
        } catch (error) {
            console.error('Error getting available agents:', error);
            throw error;
        }
    }

    /**
     * Send a message to an agent
     * @param {string} agentType - The type of agent to send the message to
     * @param {string} message - The message to send
     * @param {string} conversationId - The conversation ID (optional)
     * @returns {Promise<Object>} A promise that resolves to the agent response
     */
    async sendMessage(agentType, message, conversationId = null) {
        try {
            // Update current agent type and conversation ID
            this.currentAgentType = agentType;
            
            const payload = {
                agent_type: agentType,
                message: message,
                conversation_id: conversationId || this.currentConversationId
            };
            
            const response = await fetch(`${this.apiBaseUrl}/agents/message`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(payload)
            });
            
            const data = await this.handleResponse(response);
            
            // Update the current conversation ID
            this.currentConversationId = data.conversation_id;
            
            return data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    /**
     * Get conversation history
     * @param {string} conversationId - The conversation ID
     * @returns {Promise<Object>} A promise that resolves to the conversation history
     */
    async getConversationHistory(conversationId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/agents/conversations/${conversationId}`, {
                method: 'GET',
                headers: this.getHeaders()
            });
            
            return this.handleResponse(response);
        } catch (error) {
            console.error('Error getting conversation history:', error);
            throw error;
        }
    }

    /**
     * List all conversations
     * @param {number} limit - Maximum number of conversations to return
     * @param {number} offset - Offset for pagination
     * @returns {Promise<Object>} A promise that resolves to the list of conversations
     */
    async listConversations(limit = 100, offset = 0) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/agents/conversations?limit=${limit}&offset=${offset}`, {
                method: 'GET',
                headers: this.getHeaders()
            });
            
            return this.handleResponse(response);
        } catch (error) {
            console.error('Error listing conversations:', error);
            throw error;
        }
    }

    /**
     * Delete a conversation
     * @param {string} conversationId - The conversation ID
     * @returns {Promise<Object>} A promise that resolves to the success message
     */
    async deleteConversation(conversationId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/agents/conversations/${conversationId}`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });
            
            // If this was the current conversation, clear it
            if (conversationId === this.currentConversationId) {
                this.currentConversationId = null;
            }
            
            return this.handleResponse(response);
        } catch (error) {
            console.error('Error deleting conversation:', error);
            throw error;
        }
    }

    /**
     * Get agent capabilities based on agent type
     * @param {string} agentType - The type of agent
     * @returns {Object} The agent capabilities
     */
    getAgentCapabilities(agentType) {
        console.log('getAgentCapabilities called with:', agentType);
        
        // This is a static method that returns hardcoded capabilities for each agent type
        // In a real application, this could be fetched from the server
        const capabilities = {
            // Map backend agent types to frontend capabilities
            coordinator: {
                title: 'Event Coordinator',
                description: 'The Event Coordinator orchestrates the entire event planning process and delegates tasks to specialized agents.',
                capabilities: [
                    {
                        title: 'Event Planning Coordination',
                        description: 'Coordinates all aspects of event planning, from initial concept to execution.',
                        example: 'I need to plan a corporate conference for 200 people in September.'
                    },
                    {
                        title: 'Task Delegation',
                        description: 'Delegates specific tasks to specialized agents based on your needs.',
                        example: 'Can you help me create a budget for this event?'
                    },
                    {
                        title: 'Progress Tracking',
                        description: 'Tracks progress across all aspects of event planning.',
                        example: 'What\'s the current status of my event planning?'
                    }
                ]
            },
            resource_planning: {
                title: 'Resource Planner',
                description: 'The Resource Planner helps you identify, allocate, and manage resources needed for your event.',
                capabilities: [
                    {
                        title: 'Venue Selection',
                        description: 'Helps identify suitable venues based on event requirements.',
                        example: 'What type of venue would work for a 50-person workshop?'
                    },
                    {
                        title: 'Equipment Planning',
                        description: 'Identifies necessary equipment and technology for your event.',
                        example: 'What AV equipment will I need for a presentation?'
                    },
                    {
                        title: 'Staff Allocation',
                        description: 'Recommends staffing levels and roles for your event.',
                        example: 'How many staff members should I have for a 100-person dinner?'
                    }
                ]
            },
            financial: {
                title: 'Financial Advisor',
                description: 'The Financial Advisor helps with budgeting, cost estimation, and financial planning for your event.',
                capabilities: [
                    {
                        title: 'Budget Creation',
                        description: 'Creates detailed event budgets based on your requirements.',
                        example: 'Create a budget for a 3-day conference with 150 attendees.'
                    },
                    {
                        title: 'Cost Estimation',
                        description: 'Provides cost estimates for various event components.',
                        example: 'How much should I budget for catering for 50 people?'
                    },
                    {
                        title: 'Financial Tracking',
                        description: 'Tracks expenses and helps you stay within budget.',
                        example: 'Update my budget with a $2,000 venue deposit payment.'
                    }
                ]
            },
            stakeholder_management: {
                title: 'Stakeholder Manager',
                description: 'The Stakeholder Manager helps you identify, engage, and communicate with event stakeholders.',
                capabilities: [
                    {
                        title: 'Stakeholder Identification',
                        description: 'Identifies key stakeholders for your event.',
                        example: 'Who are the key stakeholders for a corporate product launch?'
                    },
                    {
                        title: 'Communication Planning',
                        description: 'Creates communication plans for different stakeholder groups.',
                        example: 'How should I communicate with sponsors before the event?'
                    },
                    {
                        title: 'Expectation Management',
                        description: 'Helps manage stakeholder expectations.',
                        example: 'How can I ensure VIP attendees have a good experience?'
                    }
                ]
            },
            marketing_communications: {
                title: 'Marketing Specialist',
                description: 'The Marketing Specialist helps you promote your event and create effective communication materials.',
                capabilities: [
                    {
                        title: 'Marketing Strategy',
                        description: 'Develops marketing strategies to promote your event.',
                        example: 'Create a marketing plan for my charity fundraiser.'
                    },
                    {
                        title: 'Content Creation',
                        description: 'Suggests content for event promotion.',
                        example: 'What should I include in my event invitation email?'
                    },
                    {
                        title: 'Social Media Planning',
                        description: 'Creates social media plans for event promotion.',
                        example: 'How should I promote my event on social media?'
                    }
                ]
            },
            project_management: {
                title: 'Project Manager',
                description: 'The Project Manager helps you plan, execute, and track your event as a project.',
                capabilities: [
                    {
                        title: 'Timeline Creation',
                        description: 'Creates detailed event timelines and schedules.',
                        example: 'Create a timeline for my conference from planning to execution.'
                    },
                    {
                        title: 'Task Management',
                        description: 'Breaks down the event into manageable tasks.',
                        example: 'What tasks need to be completed 2 weeks before the event?'
                    },
                    {
                        title: 'Risk Management',
                        description: 'Identifies potential risks and mitigation strategies.',
                        example: 'What risks should I consider for an outdoor event?'
                    }
                ]
            },
            analytics: {
                title: 'Analytics Expert',
                description: 'The Analytics Expert helps you collect, analyze, and interpret data related to your event.',
                capabilities: [
                    {
                        title: 'Data Collection Planning',
                        description: 'Plans what data to collect before, during, and after your event.',
                        example: 'What data should I collect to measure event success?'
                    },
                    {
                        title: 'Performance Analysis',
                        description: 'Analyzes event performance based on collected data.',
                        example: 'How did my event perform compared to industry benchmarks?'
                    },
                    {
                        title: 'Insights & Recommendations',
                        description: 'Provides insights and recommendations based on data analysis.',
                        example: 'What can I improve for my next event based on this data?'
                    }
                ]
            },
            compliance_security: {
                title: 'Compliance & Security Specialist',
                description: 'The Compliance & Security Specialist helps ensure your event meets legal requirements and security standards.',
                capabilities: [
                    {
                        title: 'Compliance Assessment',
                        description: 'Assesses compliance requirements for your event.',
                        example: 'What permits do I need for a public event in Chicago?'
                    },
                    {
                        title: 'Security Planning',
                        description: 'Creates security plans for your event.',
                        example: 'What security measures should I have for a high-profile speaker?'
                    },
                    {
                        title: 'Risk Assessment',
                        description: 'Conducts risk assessments for compliance and security.',
                        example: 'What are the liability risks for my outdoor sports event?'
                    }
                ]
            }
        };
        
        return capabilities[agentType] || {
            title: 'Unknown Agent',
            description: 'Information about this agent is not available.',
            capabilities: []
        };
    }
}

// Create a global instance of the agent service
const agentService = new AgentService();
