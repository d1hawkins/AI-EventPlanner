/**
 * AI Event Planner SaaS - Agent Onboarding
 * 
 * This file contains the JavaScript code for the agent onboarding experience.
 */

class AgentOnboarding {
    /**
     * Initialize the agent onboarding
     */
    constructor() {
        this.currentStep = 0;
        this.selectedAgentType = null; // Track selected agent type
        this.steps = [
            {
                title: "Welcome to AI Agents",
                content: "Our AI agents help you plan your events efficiently. Each agent specializes in different aspects of event planning, from coordination to financial planning.",
                action: "next"
            },
            {
                title: "Choose an Agent",
                content: "Select the agent that best fits your current needs. You can always switch between agents during your planning process.",
                action: "select-agent"
            },
            {
                title: "Start a Conversation",
                content: "Type your message in the chat input and press Enter or click the Send button. Be specific about your event details for the best results.",
                action: "chat-demo"
            },
            {
                title: "Attach to Events",
                content: "You can attach your agent conversations to specific events. This gives the agent context about your event details.",
                action: "attach-event"
            },
            {
                title: "Export Conversations",
                content: "You can export your conversations for future reference or to share with your team.",
                action: "export-demo"
            },
            {
                title: "Ready to Start",
                content: "You're all set! Select an agent from the list to start planning your event.",
                action: "complete"
            }
        ];
        
        // Sample conversations for each agent type
        this.sampleConversations = {
            coordinator: [
                { role: "user", content: "I need to plan a corporate conference for 200 people in September." },
                { role: "assistant", content: "I'd be happy to help you plan your corporate conference. Let's start by gathering some basic information. Do you have a specific date in September in mind, and do you have a location preference?" },
                { role: "user", content: "We're thinking September 15-16, and we'd prefer a downtown venue." },
                { role: "assistant", content: "Great! A two-day conference in mid-September in the downtown area. What's the main purpose or theme of this conference? And do you have a budget range in mind?" }
            ],
            resource_planning: [
                { role: "user", content: "What type of venue would work for a 50-person workshop?" },
                { role: "assistant", content: "For a 50-person workshop, you have several venue options. A hotel conference room, a coworking space with a large meeting room, or a dedicated event space would all work well. Would you like me to help you evaluate the pros and cons of each option?" },
                { role: "user", content: "Yes, please tell me about hotel conference rooms." },
                { role: "assistant", content: "Hotel conference rooms are a popular choice for 50-person workshops. Pros: They often come with AV equipment, catering options, and on-site staff. They're professionally managed and can handle last-minute changes. Cons: They can be more expensive than other options, and may have stricter time constraints. Would you like me to suggest some specific setup configurations for a workshop of this size?" }
            ],
            financial: [
                { role: "user", content: "Create a budget for a 3-day conference with 150 attendees." },
                { role: "assistant", content: "I'll help you create a budget for your 3-day conference. Let's break it down by category:\n\n1. Venue: $15,000-$25,000 (depends on location)\n2. Catering: $22,500 ($50/person/day × 150 people × 3 days)\n3. AV Equipment: $5,000-$8,000\n4. Speaker Fees: $5,000-$15,000\n5. Marketing: $3,000-$5,000\n6. Staff: $3,000-$6,000\n7. Printed Materials: $1,500-$3,000\n8. Miscellaneous: $3,000-$5,000\n\nEstimated Total: $58,000-$89,500\n\nWould you like me to adjust any of these categories or provide more detailed breakdowns?" }
            ]
        };
        
        // Create modal element
        this.createModalElement();
        
        // Create help button
        this.createHelpButton();
    }
    
    /**
     * Create the modal element
     */
    createModalElement() {
        // Create modal container
        const modalHtml = `
            <div class="onboarding-modal" id="onboardingModal">
                <div class="onboarding-content">
                    <div class="onboarding-header">
                        <h2>AI Agent Onboarding</h2>
                        <div class="onboarding-close" id="onboardingClose">×</div>
                    </div>
                    <div class="onboarding-body" id="onboardingBody">
                        <!-- Steps will be inserted here -->
                    </div>
                    <div class="onboarding-progress" id="onboardingProgress">
                        <!-- Progress dots will be inserted here -->
                    </div>
                    <div class="onboarding-footer">
                        <button class="btn btn-secondary" id="onboardingPrev">Previous</button>
                        <button class="btn btn-primary" id="onboardingNext">Next</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to the page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Get modal elements
        this.modal = document.getElementById('onboardingModal');
        this.modalBody = document.getElementById('onboardingBody');
        this.progressContainer = document.getElementById('onboardingProgress');
        this.prevButton = document.getElementById('onboardingPrev');
        this.nextButton = document.getElementById('onboardingNext');
        this.closeButton = document.getElementById('onboardingClose');
        
        // Add event listeners
        this.prevButton.addEventListener('click', () => this.prevStep());
        this.nextButton.addEventListener('click', () => {
            console.log('Next button clicked');
            this.nextStep();
        });
        this.closeButton.addEventListener('click', () => this.close());
        
        // Create progress dots
        this.createProgressDots();
        
        // Create step elements
        this.createStepElements();
    }
    
    /**
     * Create the help button
     */
    createHelpButton() {
        const helpButtonHtml = `
            <div class="agent-help-button" id="agentHelpButton" title="Agent Help">
                <i class="bi bi-question-lg"></i>
            </div>
        `;
        
        // Add help button to the page
        document.body.insertAdjacentHTML('beforeend', helpButtonHtml);
        
        // Get help button element
        this.helpButton = document.getElementById('agentHelpButton');
        
        // Add event listener
        this.helpButton.addEventListener('click', () => this.start());
    }
    
    /**
     * Create progress dots
     */
    createProgressDots() {
        // Clear progress container
        this.progressContainer.innerHTML = '';
        
        // Create dots
        for (let i = 0; i < this.steps.length; i++) {
            const dot = document.createElement('div');
            dot.className = `progress-dot ${i === this.currentStep ? 'active' : ''}`;
            this.progressContainer.appendChild(dot);
        }
    }
    
    /**
     * Create step elements
     */
    createStepElements() {
        // Clear modal body
        this.modalBody.innerHTML = '';
        
        // Create step elements
        this.steps.forEach((step, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = `onboarding-step ${index === this.currentStep ? 'active' : ''}`;
            stepElement.id = `onboardingStep${index}`;
            
            let stepContent = `
                <div class="onboarding-step-title">${step.title}</div>
                <div class="onboarding-step-content">${step.content}</div>
            `;
            
            // Add action-specific content
            if (step.action === 'select-agent') {
                stepContent += this.createAgentSelectionContent();
            } else if (step.action === 'chat-demo') {
                stepContent += this.createChatDemoContent();
            } else if (step.action === 'attach-event') {
                stepContent += this.createAttachEventContent();
            } else if (step.action === 'export-demo') {
                stepContent += this.createExportDemoContent();
            }
            
            stepElement.innerHTML = stepContent;
            this.modalBody.appendChild(stepElement);
        });
        
        // Add event listeners for agent selection
        if (this.steps[this.currentStep].action === 'select-agent') {
            document.querySelectorAll('.onboarding-agent-card').forEach(card => {
                card.addEventListener('click', () => {
                    document.querySelectorAll('.onboarding-agent-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    // Store the selected agent type
                    this.selectedAgentType = card.getAttribute('data-agent-type');
                    console.log('Selected agent type:', this.selectedAgentType);
                });
            });
        }
    }
    
    /**
     * Create agent selection content
     * @returns {string} HTML content
     */
    createAgentSelectionContent() {
        return `
            <div class="onboarding-agent-selection">
                <div class="onboarding-agent-card" data-agent-type="coordinator">
                    <div class="onboarding-agent-icon">
                        <i class="bi bi-diagram-3"></i>
                    </div>
                    <div class="onboarding-agent-name">Event Coordinator</div>
                    <div class="onboarding-agent-description">Orchestrates the event planning process and delegates tasks to specialized agents</div>
                </div>
                <div class="onboarding-agent-card" data-agent-type="resource_planning">
                    <div class="onboarding-agent-icon">
                        <i class="bi bi-calendar-check"></i>
                    </div>
                    <div class="onboarding-agent-name">Resource Planner</div>
                    <div class="onboarding-agent-description">Plans and manages resources needed for your event</div>
                </div>
                <div class="onboarding-agent-card" data-agent-type="financial">
                    <div class="onboarding-agent-icon">
                        <i class="bi bi-cash-coin"></i>
                    </div>
                    <div class="onboarding-agent-name">Financial Advisor</div>
                    <div class="onboarding-agent-description">Handles budgeting, cost estimation, and financial planning</div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create chat demo content
     * @returns {string} HTML content
     */
    createChatDemoContent() {
        // Get sample conversation based on selected agent type or default to coordinator
        const agentType = this.selectedAgentType || 'coordinator';
        const conversation = this.sampleConversations[agentType];
        
        let chatHtml = `
            <div class="sample-conversation">
        `;
        
        // Add messages
        conversation.forEach(message => {
            if (message.role === 'user') {
                chatHtml += `
                    <div class="sample-message user-message">
                        <div class="sample-message-content">${message.content}</div>
                        <div class="sample-message-avatar">
                            <i class="bi bi-person"></i>
                        </div>
                    </div>
                `;
            } else {
                chatHtml += `
                    <div class="sample-message">
                        <div class="sample-message-avatar">
                            <i class="bi bi-robot"></i>
                        </div>
                        <div class="sample-message-content">${message.content}</div>
                    </div>
                `;
            }
        });
        
        chatHtml += `
            </div>
            <div class="mt-3">
                <p><strong>Tips for effective conversations:</strong></p>
                <ul>
                    <li>Be specific about your event details</li>
                    <li>Ask follow-up questions if needed</li>
                    <li>Provide context about your event goals</li>
                </ul>
            </div>
        `;
        
        return chatHtml;
    }
    
    /**
     * Create attach event content
     * @returns {string} HTML content
     */
    createAttachEventContent() {
        return `
            <div class="text-center mb-3">
                <div class="placeholder-image bg-light p-5 rounded text-center">
                    <i class="bi bi-link-45deg" style="font-size: 3rem;"></i>
                    <h3 class="mt-3">Attach to Event Demo</h3>
                </div>
            </div>
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                Attaching a conversation to an event gives the agent access to all the event details, allowing for more contextual and relevant assistance.
            </div>
        `;
    }
    
    /**
     * Create export demo content
     * @returns {string} HTML content
     */
    createExportDemoContent() {
        return `
            <div class="text-center mb-3">
                <div class="placeholder-image bg-light p-5 rounded text-center">
                    <i class="bi bi-download" style="font-size: 3rem;"></i>
                    <h3 class="mt-3">Export Conversation Demo</h3>
                </div>
            </div>
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                Exporting conversations allows you to save important information and share it with your team or stakeholders.
            </div>
        `;
    }
    
    /**
     * Start the onboarding
     */
    start() {
        // Reset to first step
        this.currentStep = 0;
        this.selectedAgentType = null;
        
        // Update progress dots
        this.createProgressDots();
        
        // Update step elements
        this.createStepElements();
        
        // Update button states
        this.updateButtonStates();
        
        // Show modal
        this.modal.classList.add('active');
    }
    
    /**
     * Close the onboarding
     */
    close() {
        // Hide modal
        this.modal.classList.remove('active');
        
        // Mark as completed
        localStorage.setItem('agent_onboarding_completed', 'true');
        
        // If an agent was selected, store it
        if (this.selectedAgentType) {
            localStorage.setItem('selected_agent_type', this.selectedAgentType);
            
            // Optionally, trigger agent selection in the main UI
            const agentSelectionEvent = new CustomEvent('agent-selected', {
                detail: { agentType: this.selectedAgentType }
            });
            document.dispatchEvent(agentSelectionEvent);
        }
    }
    
    /**
     * Go to the next step
     */
    nextStep() {
        try {
            console.log('nextStep called, current step:', this.currentStep);
            
            // Check if last step
            if (this.currentStep === this.steps.length - 1) {
                console.log('Last step reached, closing onboarding');
                this.close();
                return;
            }
            
            // If on agent selection step, check if an agent is selected
            if (this.steps[this.currentStep].action === 'select-agent' && !this.selectedAgentType) {
                console.log('No agent selected, showing alert');
                alert('Please select an agent to continue.');
                return;
            }
            
            // Increment step
            this.currentStep++;
            console.log('Incremented to step:', this.currentStep);
            
            // Update progress dots
            this.updateProgressDots();
            console.log('Updated progress dots');
            
            // Clear modal body and recreate step elements
            this.modalBody.innerHTML = '';
            console.log('Cleared modal body');
            
            // Create step element for current step only
            const step = this.steps[this.currentStep];
            console.log('Current step action:', step.action);
            
            const stepElement = document.createElement('div');
            stepElement.className = 'onboarding-step active';
            stepElement.id = `onboardingStep${this.currentStep}`;
            console.log('Created step element with ID:', stepElement.id);
            
            let stepContent = `
                <div class="onboarding-step-title">${step.title}</div>
                <div class="onboarding-step-content">${step.content}</div>
            `;
            console.log('Created base step content');
            
            // Add action-specific content
            if (step.action === 'select-agent') {
                console.log('Adding agent selection content');
                stepContent += this.createAgentSelectionContent();
            } else if (step.action === 'chat-demo') {
                console.log('Adding chat demo content');
                stepContent += this.createChatDemoContent();
            } else if (step.action === 'attach-event') {
                console.log('Adding attach event content');
                stepContent += this.createAttachEventContent();
            } else if (step.action === 'export-demo') {
                console.log('Adding export demo content');
                stepContent += this.createExportDemoContent();
            }
            
            console.log('Setting innerHTML for step element');
            stepElement.innerHTML = stepContent;
            console.log('Appending step element to modal body');
            this.modalBody.appendChild(stepElement);
            console.log('Added step element to modal body');
            
            // Add event listeners for agent selection
            if (step.action === 'select-agent') {
                console.log('Adding event listeners for agent selection');
                const agentCards = document.querySelectorAll('.onboarding-agent-card');
                console.log('Found agent cards:', agentCards.length);
                
                agentCards.forEach(card => {
                    card.addEventListener('click', () => {
                        console.log('Agent card clicked:', card.getAttribute('data-agent-type'));
                        document.querySelectorAll('.onboarding-agent-card').forEach(c => c.classList.remove('selected'));
                        card.classList.add('selected');
                        // Store the selected agent type
                        this.selectedAgentType = card.getAttribute('data-agent-type');
                        console.log('Selected agent type:', this.selectedAgentType);
                    });
                });
                console.log('Added event listeners for agent selection');
            }
            
            // Update button states
            this.updateButtonStates();
            console.log('Updated button states');
        } catch (error) {
            console.error('Error in nextStep:', error);
        }
    }
    
    /**
     * Go to the previous step
     */
    prevStep() {
        // Check if first step
        if (this.currentStep === 0) {
            return;
        }
        
        // Decrement step
        this.currentStep--;
        
        // Update progress dots
        this.updateProgressDots();
        
        // Clear modal body and recreate step elements
        this.modalBody.innerHTML = '';
        
        // Create step element for current step only
        const step = this.steps[this.currentStep];
        const stepElement = document.createElement('div');
        stepElement.className = 'onboarding-step active';
        stepElement.id = `onboardingStep${this.currentStep}`;
        
        let stepContent = `
            <div class="onboarding-step-title">${step.title}</div>
            <div class="onboarding-step-content">${step.content}</div>
        `;
        
        // Add action-specific content
        if (step.action === 'select-agent') {
            stepContent += this.createAgentSelectionContent();
        } else if (step.action === 'chat-demo') {
            stepContent += this.createChatDemoContent();
        } else if (step.action === 'attach-event') {
            stepContent += this.createAttachEventContent();
        } else if (step.action === 'export-demo') {
            stepContent += this.createExportDemoContent();
        }
        
        stepElement.innerHTML = stepContent;
        this.modalBody.appendChild(stepElement);
        
        // Add event listeners for agent selection
        if (step.action === 'select-agent') {
            document.querySelectorAll('.onboarding-agent-card').forEach(card => {
                card.addEventListener('click', () => {
                    document.querySelectorAll('.onboarding-agent-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    // Store the selected agent type
                    this.selectedAgentType = card.getAttribute('data-agent-type');
                    console.log('Selected agent type:', this.selectedAgentType);
                });
            });
            
            // If an agent was previously selected, mark it as selected
            if (this.selectedAgentType) {
                const selectedCard = document.querySelector(`.onboarding-agent-card[data-agent-type="${this.selectedAgentType}"]`);
                if (selectedCard) {
                    selectedCard.classList.add('selected');
                }
            }
        }
        
        // Update button states
        this.updateButtonStates();
    }
    
    /**
     * Update progress dots
     */
    updateProgressDots() {
        // Get all dots
        const dots = this.progressContainer.querySelectorAll('.progress-dot');
        
        // Update active dot
        dots.forEach((dot, index) => {
            if (index === this.currentStep) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    /**
     * Update active step
     */
    updateActiveStep() {
        // Clear modal body
        this.modalBody.innerHTML = '';
        
        // Create step elements
        this.steps.forEach((step, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = `onboarding-step ${index === this.currentStep ? 'active' : ''}`;
            stepElement.id = `onboardingStep${index}`;
            
            let stepContent = `
                <div class="onboarding-step-title">${step.title}</div>
                <div class="onboarding-step-content">${step.content}</div>
            `;
            
            // Add action-specific content
            if (step.action === 'select-agent') {
                stepContent += this.createAgentSelectionContent();
            } else if (step.action === 'chat-demo') {
                stepContent += this.createChatDemoContent();
            } else if (step.action === 'attach-event') {
                stepContent += this.createAttachEventContent();
            } else if (step.action === 'export-demo') {
                stepContent += this.createExportDemoContent();
            }
            
            stepElement.innerHTML = stepContent;
            this.modalBody.appendChild(stepElement);
        });
        
        // Add event listeners for agent selection
        if (this.steps[this.currentStep].action === 'select-agent') {
            document.querySelectorAll('.onboarding-agent-card').forEach(card => {
                card.addEventListener('click', () => {
                    document.querySelectorAll('.onboarding-agent-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    // Store the selected agent type
                    this.selectedAgentType = card.getAttribute('data-agent-type');
                    console.log('Selected agent type:', this.selectedAgentType);
                });
            });
            
            // If an agent was previously selected, mark it as selected
            if (this.selectedAgentType) {
                const selectedCard = document.querySelector(`.onboarding-agent-card[data-agent-type="${this.selectedAgentType}"]`);
                if (selectedCard) {
                    selectedCard.classList.add('selected');
                }
            }
        }
    }
    
    /**
     * Update button states
     */
    updateButtonStates() {
        // Update previous button
        if (this.currentStep === 0) {
            this.prevButton.disabled = true;
        } else {
            this.prevButton.disabled = false;
        }
        
        // Update next button
        if (this.currentStep === this.steps.length - 1) {
            this.nextButton.textContent = 'Get Started';
        } else {
            this.nextButton.textContent = 'Next';
        }
    }
    
    /**
     * Show a tooltip
     * @param {HTMLElement} element - The element to attach the tooltip to
     * @param {string} text - The tooltip text
     * @param {string} position - The tooltip position (top, bottom, left, right)
     */
    showTooltip(element, text, position = 'top') {
        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = `onboarding-tooltip ${position}`;
        tooltip.textContent = text;
        
        // Add tooltip to the page
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        
        if (position === 'top') {
            tooltip.style.bottom = `${window.innerHeight - rect.top + 10}px`;
            tooltip.style.left = `${rect.left + rect.width / 2}px`;
            tooltip.style.transform = 'translateX(-50%)';
        } else if (position === 'bottom') {
            tooltip.style.top = `${rect.bottom + 10}px`;
            tooltip.style.left = `${rect.left + rect.width / 2}px`;
            tooltip.style.transform = 'translateX(-50%)';
        } else if (position === 'left') {
            tooltip.style.right = `${window.innerWidth - rect.left + 10}px`;
            tooltip.style.top = `${rect.top + rect.height / 2}px`;
            tooltip.style.transform = 'translateY(-50%)';
        } else if (position === 'right') {
            tooltip.style.left = `${rect.right + 10}px`;
            tooltip.style.top = `${rect.top + rect.height / 2}px`;
            tooltip.style.transform = 'translateY(-50%)';
        }
        
        // Remove tooltip after delay
        setTimeout(() => {
            document.body.removeChild(tooltip);
        }, 3000);
    }
}

// Initialize onboarding when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing onboarding');
    
    // Create onboarding instance
    const onboarding = new AgentOnboarding();
    window.onboarding = onboarding; // Make it accessible globally for debugging
    
    // Check if first-time user
    if (!localStorage.getItem('agent_onboarding_completed')) {
        console.log('First-time user, starting onboarding');
        // Start onboarding
        onboarding.start();
    }
    
    // Add event listener for help button
    const agentHelpButton = document.getElementById('agentHelpButton');
    if (agentHelpButton) {
        agentHelpButton.addEventListener('click', function() {
            console.log('Help button clicked, starting onboarding');
            onboarding.start();
        });
    }
});
