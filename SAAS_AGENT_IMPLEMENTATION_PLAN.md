# AI Event Planner SaaS Implementation Plan

## Overview

This document serves as a comprehensive implementation plan for the missing functionality in the AI Event Planner SaaS application. It is structured as a task-by-task guide that can be used as input for implementation.

## How to Use This Document

1. Present this document as input to start implementing the tasks.
2. Work on tasks that are NOT marked as completed. Completed tasks are marked with `[✓]` 
3. Each task includes detailed implementation instructions and verification steps.
4. After completing a task, verify it works as expected.
5. Update the document to mark the task as complete by changing `[  ]` to `[✓]`.
6. Stop as complete. 

## Implementation Phases

The implementation is divided into three phases, with each phase containing multiple tasks:

### Phase 1: User Experience Enhancements (2-3 weeks)

#### Task 1.1: Agent Onboarding Flow
- **Status**: [✓] Completed
- **Priority**: High
- **Estimated Time**: 3-4 days
- **Dependencies**: None

**Implementation Steps**:
1. Create `app/web/static/saas/agent-onboarding.html` with a step-by-step guide for first-time users
2. Create `app/web/static/saas/css/agent-onboarding.css` for styling the onboarding flow
3. Create `app/web/static/saas/js/agent-onboarding.js` with the following functionality:
   - Track first-time agent users using localStorage
   - Implement a modal-based step-by-step guide
   - Add sample conversations for each agent type
   - Include tooltips and help text
4. Modify `app/web/static/saas/js/agent-ui.js` to trigger the onboarding flow for first-time users
5. Add an "Agent Help" button to the agent interface that can re-trigger the onboarding flow

**Verification Steps**:
1. Run the application using `python run_saas_with_agents.py`
2. Navigate to the agents page as a new user
3. Verify that the onboarding flow appears automatically
4. Complete the onboarding flow and verify that it doesn't appear again on subsequent visits
5. Click the "Agent Help" button and verify that the onboarding flow can be manually triggered

**Code Snippets**:
```javascript
// app/web/static/saas/js/agent-onboarding.js
class AgentOnboarding {
    constructor() {
        this.currentStep = 0;
        this.steps = [
            {
                title: "Welcome to AI Agents",
                content: "Our AI agents help you plan your events efficiently...",
                action: "next"
            },
            {
                title: "Choose an Agent",
                content: "Select the agent that best fits your current needs...",
                action: "select-agent"
            },
            // More steps...
        ];
    }
    
    start() {
        // Show onboarding modal
        this.showStep(0);
    }
    
    showStep(stepIndex) {
        // Display current step
    }
    
    // More methods...
}

// Initialize onboarding
document.addEventListener('DOMContentLoaded', function() {
    const onboarding = new AgentOnboarding();
    
    // Check if first-time user
    if (!localStorage.getItem('agent_onboarding_completed')) {
        onboarding.start();
    }
    
    // Add event listener for help button
    document.getElementById('agentHelpButton').addEventListener('click', function() {
        onboarding.start();
    });
});
```

#### Task 1.2: Mobile Optimization
- **Status**: [✓] Completed
- **Priority**: Medium
- **Estimated Time**: 2-3 days
- **Dependencies**: None

**Implementation Steps**:
1. Enhance `app/web/static/saas/css/agent-chat.css` with responsive design for mobile devices
2. Implement touch-friendly UI elements for mobile users
3. Optimize keyboard handling on mobile devices
4. Add mobile-specific layouts for small screens
5. Implement responsive adjustments for the agent list and chat interface

**Verification Steps**:
1. Run the application using `python run_saas_with_agents.py`
2. Open the application on a mobile device or use browser developer tools to simulate mobile devices
3. Verify that the interface is properly responsive on different screen sizes
4. Test touch interactions on mobile devices
5. Verify that the keyboard appears and functions correctly on mobile

**Code Snippets**:
```css
/* app/web/static/saas/css/agent-chat.css */
/* Mobile-specific styles */
@media (max-width: 768px) {
    .dashboard-content {
        padding: 10px;
    }
    
    .chat-container {
        height: calc(100vh - 200px);
    }
    
    .agent-card {
        margin-bottom: 10px;
    }
    
    .chat-messages {
        max-height: calc(100vh - 250px);
    }
    
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 10px;
        background-color: #fff;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Touch-friendly adjustments */
    .agent-card, .btn, .form-control {
        min-height: 44px; /* Minimum touch target size */
    }
}
```

#### Task 1.3: Accessibility Improvements
- **Status**: [  ] Not Started
- **Priority**: Medium
- **Estimated Time**: 2-3 days
- **Dependencies**: None

**Implementation Steps**:
1. Add ARIA attributes to all interactive elements in the agent interface
2. Implement keyboard navigation and shortcuts
3. Enhance focus management for better screen reader compatibility
4. Add proper alt text to all images and icons
5. Ensure color contrast meets WCAG 2.1 AA standards
6. Implement proper heading structure and semantic HTML

**Verification Steps**:
1. Run the application using `python run_saas_with_agents.py`
2. Test keyboard navigation throughout the interface
3. Use a screen reader to verify accessibility
4. Run an automated accessibility audit using a tool like Lighthouse
5. Verify that all interactive elements are properly labeled

**Code Snippets**:
```html
<!-- Example of accessibility improvements in app/web/static/saas/agents.html -->
<div class="agent-card" data-agent-type="coordinator" tabindex="0" role="button" aria-pressed="false" aria-label="Select Coordinator Agent">
    <div class="card-body">
        <div class="d-flex align-items-center">
            <div class="agent-icon me-3" aria-hidden="true">
                <i class="bi bi-diagram-3"></i>
            </div>
            <div class="flex-grow-1">
                <h5 class="agent-name">Event Coordinator</h5>
                <p class="agent-description mb-1">Orchestrates the event planning process and delegates tasks to specialized agents</p>
                <span class="agent-tier free">free</span>
            </div>
        </div>
    </div>
</div>
```

```javascript
// Keyboard navigation in app/web/static/saas/js/agent-ui.js
document.addEventListener('keydown', function(event) {
    // Add keyboard shortcuts
    if (event.key === '/' && (event.ctrlKey || event.metaKey)) {
        // Focus on message input
        event.preventDefault();
        document.getElementById('messageInput').focus();
    }
    
    // Add more keyboard shortcuts...
});
```

### Phase 2: Advanced Features (3-4 weeks)

#### Task 2.1: Event-Agent Integration
- **Status**: [✓] Completed
- **Priority**: High
- **Estimated Time**: 4-5 days
- **Dependencies**: None

**Implementation Steps**:
1. Create new database models for linking events and conversations
2. Add new endpoints in `app/agents/api_router.py` for attaching events to conversations
3. Update agent state to include event context
4. Modify `app/agents/agent_factory.py` to load event data into agent context
5. Implement UI for attaching conversations to events in `app/web/static/saas/js/agent-ui.js`
6. Add event selection dropdown in the agent interface

**Verification Steps**:
1. Run the application using `python run_saas_with_agents.py`
2. Create a new event in the events interface
3. Navigate to the agents page and start a conversation
4. Use the "Attach to Event" feature to link the conversation to the event
5. Verify that the agent has access to the event context in its responses

**Code Snippets**:
```python
# New endpoint in app/agents/api_router.py
@router.post("/agents/attach-event", response_model=AttachEventResponse)
async def attach_event_to_conversation(
    request: Request,
    attach_request: AttachEventRequest = Body(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Attach an event to a conversation.
    
    Args:
        request: FastAPI request
        attach_request: Attach event request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Success message
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Verify that the conversation exists and belongs to this organization
        conversation_id = attach_request.conversation_id
        event_id = attach_request.event_id
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get conversation state
        state = agent_factory.state_manager.get_conversation_state(conversation_id)
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check if the conversation belongs to the current organization
        if organization_id and state.get("organization_id") != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation"
            )
        
        # Get the event
        event = db.query(Event).filter(
            Event.id == event_id,
            Event.organization_id == organization_id
        ).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        # Update the conversation state with event context
        state["event_context"] = {
            "event_id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "attendee_count": event.attendee_count,
            "event_type": event.event_type,
            "budget": event.budget
        }
        
        # Update the state
        agent_factory.state_manager.update_conversation_state(conversation_id, state)
        
        # Add a system message about the attached event
        if "messages" in state:
            state["messages"].append({
                "role": "system",
                "content": f"Event '{event.title}' has been attached to this conversation. The agent now has access to the event details.",
                "timestamp": datetime.utcnow().isoformat()
            })
            agent_factory.state_manager.update_conversation_state(conversation_id, state)
        
        return {
            "message": f"Event {event_id} attached to conversation {conversation_id}",
            "conversation_id": conversation_id,
            "event_id": event_id,
            "organization_id": organization_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in attach_event_to_conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error attaching event to conversation: {str(e)}"
        )
```

```javascript
// UI for attaching events in app/web/static/saas/js/agent-ui.js
function showAttachEventModal() {
    // Fetch events for the current organization
    fetch('/api/events', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
        }
    })
    .then(response => response.json())
    .then(data => {
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
        
        // Add modal to the page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('attachEventModal'));
        modal.show();
        
        // Handle attach button click
        document.getElementById('attachEventButton').addEventListener('click', function() {
            const eventId = document.getElementById('eventSelect').value;
            if (!eventId) return;
            
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

function attachEventToConversation(eventId) {
    // Check if conversation exists
    if (!agentService.currentConversationId) {
        showError('No active conversation to attach to an event.');
        return;
    }
    
    // Send request to attach event
    fetch('/api/agents/attach-event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
        },
        body: JSON.stringify({
            conversation_id: agentService.currentConversationId,
            event_id: eventId
        })
    })
    .then(response => response.json())
    .then(data => {
        // Show success message
        addSystemMessage(`Event has been attached to this conversation. The agent now has access to the event details.`);
    })
    .catch(error => {
        console.error('Error attaching event:', error);
        showError('Failed to attach event. Please try again.');
    });
}
```

#### Task 2.2: Analytics Dashboard
- **Status**: [  ] Not Started
- **Priority**: Medium
- **Estimated Time**: 3-4 days
- **Dependencies**: None

**Implementation Steps**:
1. Create `app/web/static/saas/agent-analytics.html` for the analytics dashboard
2. Implement analytics tracking in agent interactions
3. Create new endpoints in `app/agents/api_router.py` for retrieving analytics data
4. Implement data aggregation and visualization using Chart.js
5. Add filtering and date range selection for analytics

**Verification Steps**:
1. Run the application using `python run_saas_with_agents.py`
2. Generate some agent conversations for testing
3. Navigate to the analytics dashboard
4. Verify that the dashboard displays accurate metrics
5. Test filtering and date range selection

**Code Snippets**:
```python
# New endpoint in app/agents/api_router.py
@router.get("/agents/analytics", response_model=AgentAnalyticsResponse)
async def get_agent_analytics(
    request: Request,
    start_date: str = None,
    end_date: str = None,
    agent_type: str = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get analytics data for agent usage.
    
    Args:
        request: FastAPI request
        start_date: Start date for analytics (YYYY-MM-DD)
        end_date: End date for analytics (YYYY-MM-DD)
        agent_type: Filter by agent type
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Analytics data
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get all conversations for this organization
        conversations = agent_factory.state_manager.list_conversations()
        
        # Parse date filters
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        # Filter conversations by date and agent type
        filtered_conversations = []
        for conv in conversations:
            # Skip if no created_at timestamp
            if "created_at" not in conv:
                continue
            
            # Parse conversation timestamp
            try:
                conv_datetime = datetime.fromisoformat(conv["created_at"])
            except (ValueError, TypeError):
                continue
            
            # Apply date filters
            if start_datetime and conv_datetime < start_datetime:
                continue
            
            if end_datetime and conv_datetime >= end_datetime:
                continue
            
            # Apply agent type filter
            if agent_type and conv.get("agent_type") != agent_type:
                continue
            
            filtered_conversations.append(conv)
        
        # Calculate analytics metrics
        total_conversations = len(filtered_conversations)
        conversations_by_agent = {}
        messages_by_agent = {}
        conversations_by_date = {}
        
        for conv in filtered_conversations:
            # Count conversations by agent
            agent_type = conv.get("agent_type", "unknown")
            conversations_by_agent[agent_type] = conversations_by_agent.get(agent_type, 0) + 1
            
            # Count messages by agent
            messages = conv.get("messages", [])
            messages_by_agent[agent_type] = messages_by_agent.get(agent_type, 0) + len(messages)
            
            # Count conversations by date
            try:
                conv_date = datetime.fromisoformat(conv["created_at"]).strftime("%Y-%m-%d")
                conversations_by_date[conv_date] = conversations_by_date.get(conv_date, 0) + 1
            except (ValueError, TypeError, KeyError):
                pass
        
        # Prepare response
        return {
            "total_conversations": total_conversations,
            "conversations_by_agent": [
                {"agent_type": agent, "count": count}
                for agent, count in conversations_by_agent.items()
            ],
            "messages_by_agent": [
                {"agent_type": agent, "count": count}
                for agent, count in messages_by_agent.items()
            ],
            "conversations_by_date": [
                {"date": date, "count": count}
                for date, count in sorted(conversations_by_date.items())
            ],
            "organization_id": organization_id
        }
        
    except Exception as e:
        print(f"Error in get_agent_analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics data: {str(e)}"
        )
```

```javascript
// app/web/static/saas/js/agent-analytics.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    const timeChartCtx = document.getElementById('conversationsTimeChart').getContext('2d');
    const agentChartCtx = document.getElementById('conversationsAgentChart').getContext('2d');
    
    let timeChart = new Chart(timeChartCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Conversations',
                data: [],
                borderColor: 'rgba(78, 115, 223, 1)',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: '#fff',
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            }
        }
    });
    
    let agentChart = new Chart(agentChartCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    'rgba(78, 115, 223, 0.8)',
                    'rgba(28, 200, 138, 0.8)',
                    'rgba(246, 194, 62, 0.8)',
                    'rgba(231, 74, 59, 0.8)',
                    'rgba(54, 185, 204, 0.8)',
                    'rgba(133, 135, 150, 0.8)',
                    'rgba(105, 70, 180, 0.8)',
                    'rgba(0, 150, 136, 0.8)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Load analytics data
    loadAnalyticsData();
    
    // Set up event listeners
    document.getElementById('refreshAnalytics').addEventListener('click', loadAnalyticsData);
    document.getElementById('analyticsFilters').addEventListener('submit', function(e) {
        e.preventDefault();
        loadAnalyticsData();
    });
    
    function loadAnalyticsData() {
        // Get filter values
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const agentType = document.getElementById('agentType').value;
        
        // Build query string
        let queryParams = [];
        if (startDate) queryParams.push(`start_date=${startDate}`);
        if (endDate) queryParams.push(`end_date=${endDate}`);
        if (agentType) queryParams.push(`agent_type=${agentType}`);
        
        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        
        // Fetch analytics data
        fetch(`/api/agents/analytics${queryString}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update overview metrics
            document.getElementById('totalConversations').textContent = data.total_conversations;
            
            // Update time chart
            const timeLabels = data.conversations_by_date.map(item => item.date);
            const timeData = data.conversations_by_date.map(item => item.count);
            
            timeChart.data.labels = timeLabels;
            timeChart.data.datasets[0].data = timeData;
            timeChart.update();
            
            // Update agent chart
            const agentLabels = data.conversations_by_agent.map(item => {
                // Convert agent_type to readable name
                const agentNames = {
                    'coordinator': 'Coordinator',
                    'resource_planning': 'Resource Planning',
                    'financial': 'Financial',
                    'stakeholder_management': 'Stakeholder',
                    'marketing_communications': 'Marketing',
                    'project_management': 'Project Management',
                    'analytics': 'Analytics',
                    'compliance_security': 'Compliance & Security'
                };
                return agentNames[item.agent_type] || item.agent_type;
            });
            
            const agentData = data.conversations_by_agent.map(item => item.count);
            
            agentChart.data.labels = agentLabels;
            agentChart.data.datasets[0].data = agentData;
            agentChart.update();
        })
        .catch(error => {
            console.error('Error loading analytics data:', error);
            alert('Failed to load analytics data. Please try again.');
        });
    }
});
```

#### Task 2.3: Feedback Mechanism
- **Status**: [  ] Not Started
- **Priority**: Medium
- **Estimated Time**: 2-3 days
- **Dependencies**: None

**Implementation Steps**:
1. Add rating UI in the chat interface
2. Create new endpoints in `app/agents/api_router.py` for submitting and retrieving feedback
3. Implement feedback storage in the database
4. Create a feedback analysis dashboard for administrators
5. Add sentiment analysis for text feedback

**Verification Steps**:
1. Run the application using `python run_saas_with_agents.py`
2. Start a conversation with an agent
3. After receiving a response, use the rating UI to provide feedback
4. Verify that the feedback is stored correctly
5. Access the feedback dashboard and verify that it displays the collected feedback

**Code Snippets**:
```python
# New endpoint in app/agents/api_router.py
@router.post("/agents/feedback", response_model=AgentFeedbackResponse)
async def submit_agent_feedback(
    request: Request,
    feedback_request: AgentFeedbackRequest = Body(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Submit feedback for an agent response.
    
    Args:
        request: FastAPI request
        feedback_request: Feedback request
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        Success message
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Verify that the conversation exists and belongs to this organization
        conversation_id = feedback_request.conversation_id
        message_index = feedback_request.message_index
        rating = feedback_request.rating
        comment = feedback_request.comment
        
        # Get agent factory with tenant context
        agent_factory = get_agent_factory(db=db, organization_id=organization_id)
        
        # Get conversation state
        state = agent_factory.state_manager.get_conversation_state(conversation_id)
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check if the conversation belongs to the current organization
        if organization_id and state.get("organization_id") != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation"
            )
        
        # Check if the message index is valid
        if "messages" not in state or message_index >= len(state["messages"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid message index: {message_index}"
            )
        
        # Get the message
        message = state["messages"][message_index]
        
        # Check if the message is from the assistant
        if message.get("role") != "assistant":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback can only be provided for assistant messages"
            )
        
        # Add feedback to the message
        message["feedback"] = {
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": current_user_id
        }
        
        # Update the state
        agent_factory.state_manager.update_conversation_state(conversation_id, state)
        
        # Store feedback in the database for analytics
        # This would typically be implemented with a Feedback model
        
        return {
            "message": "Feedback submitted successfully",
            "conversation_id": conversation_id,
            "message_index": message_index,
            "organization_id": organization_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in submit_agent_feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )
```

```javascript
// Add to app/web/static/saas/js/agent-ui.js
function addAgentMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message';
    
    const timestamp = new Date().toLocaleTimeString();
    const messageId = 'msg-' + Date.now();
    
    messageElement.innerHTML = `
        <div class="message-avatar">
            <i class="bi bi-robot"></i>
        </div>
        <div class="message-content">
            <p>${formatMessage(message)}</p>
            <div class="message-footer">
                <div class="message-time">${timestamp}</div>
                <div class="message-actions">
