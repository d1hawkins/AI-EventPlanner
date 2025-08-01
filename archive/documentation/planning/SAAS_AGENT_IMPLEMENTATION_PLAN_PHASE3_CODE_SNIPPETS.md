# Code Snippets for AI Event Planner SaaS Implementation Plan - Phase 3

This document contains code snippets referenced in the implementation plan for Phase 3 of the AI Event Planner SaaS application.

## Task 3.1: Calendar Integration

### Calendar.js Implementation

```javascript
// app/web/static/saas/js/calendar.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize FullCalendar
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) return;
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        themeSystem: 'bootstrap5',
        events: fetchEvents,
        eventClick: handleEventClick,
        dateClick: handleDateClick,
        editable: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        select: handleDateSelect,
        eventDrop: handleEventDrop,
        eventResize: handleEventResize,
        loading: handleLoading
    });
    
    calendar.render();
    
    // Event handlers
    function fetchEvents(info, successCallback, failureCallback) {
        fetch(`/api/events?start=${info.startStr}&end=${info.endStr}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            }
        })
        .then(response => response.json())
        .then(data => {
            const events = data.events.map(event => ({
                id: event.id,
                title: event.title,
                start: event.start_date,
                end: event.end_date,
                allDay: !event.start_time,
                location: event.location,
                extendedProps: {
                    description: event.description,
                    attendee_count: event.attendee_count,
                    event_type: event.event_type,
                    status: event.status
                },
                backgroundColor: getEventColor(event.status),
                borderColor: getEventColor(event.status)
            }));
            successCallback(events);
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            failureCallback(error);
        });
    }
    
    function handleEventClick(info) {
        // Show event details modal
        const event = info.event;
        const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
        
        document.getElementById('eventTitle').textContent = event.title;
        document.getElementById('eventDate').textContent = formatDateRange(event.start, event.end);
        document.getElementById('eventLocation').textContent = event.extendedProps.location || 'No location specified';
        document.getElementById('eventDescription').textContent = event.extendedProps.description || 'No description';
        document.getElementById('eventAttendees').textContent = event.extendedProps.attendee_count || '0';
        document.getElementById('eventType').textContent = formatEventType(event.extendedProps.event_type);
        document.getElementById('eventStatus').textContent = formatStatus(event.extendedProps.status);
        
        document.getElementById('editEventBtn').setAttribute('data-event-id', event.id);
        document.getElementById('deleteEventBtn').setAttribute('data-event-id', event.id);
        
        modal.show();
    }
    
    // Helper functions
    function getEventColor(status) {
        switch (status) {
            case 'draft': return '#6c757d'; // gray
            case 'planning': return '#ffc107'; // yellow
            case 'confirmed': return '#0d6efd'; // blue
            case 'completed': return '#198754'; // green
            case 'cancelled': return '#dc3545'; // red
            default: return '#6c757d'; // gray
        }
    }
    
    function formatDateRange(start, end) {
        if (!start) return 'No date specified';
        
        const startDate = new Date(start);
        const endDate = end ? new Date(end) : null;
        
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        
        if (!endDate) {
            return startDate.toLocaleDateString('en-US', options);
        }
        
        if (startDate.toDateString() === endDate.toDateString()) {
            return `${startDate.toLocaleDateString('en-US', options)} ${formatTimeRange(startDate, endDate)}`;
        }
        
        return `${startDate.toLocaleDateString('en-US')} - ${endDate.toLocaleDateString('en-US')}`;
    }
    
    // More helper functions...
});
```

### Calendar API Endpoints

```python
# app/web/router.py
@router.get("/events", response_model=EventListResponse)
async def get_events(
    request: Request,
    start: str = None,
    end: str = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get events for calendar view.
    
    Args:
        request: FastAPI request
        start: Start date (ISO format)
        end: End date (ISO format)
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        List of events
    """
    try:
        # Get tenant ID from request
        organization_id = get_tenant_id(request) if request else None
        
        # Build query
        query = db.query(Event).filter(Event.organization_id == organization_id)
        
        # Apply date filters
        if start:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            query = query.filter(Event.end_date >= start_date)
        
        if end:
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
            query = query.filter(Event.start_date <= end_date)
        
        # Execute query
        events = query.all()
        
        # Convert to response model
        return {
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_date": event.start_date.isoformat() if event.start_date else None,
                    "end_date": event.end_date.isoformat() if event.end_date else None,
                    "location": event.location,
                    "attendee_count": event.attendee_count,
                    "event_type": event.event_type,
                    "status": event.status,
                    "organization_id": event.organization_id
                }
                for event in events
            ]
        }
        
    except Exception as e:
        print(f"Error in get_events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving events: {str(e)}"
        )
```

## Task 3.2: Event Templates

### Template Models

```python
# app/db/models_saas.py
class EventTemplate(Base):
    """Event template model."""
    
    __tablename__ = "event_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_type = Column(String, nullable=True)
    duration_days = Column(Integer, nullable=True)
    template_data = Column(JSON, nullable=False)
    is_public = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tenant relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="event_templates")
    
    # User relationship
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User")
    
    # Template items relationship
    items = relationship("TemplateItem", back_populates="template", cascade="all, delete-orphan")
```

### Template Management UI

```javascript
// app/web/static/saas/js/templates.js
document.addEventListener('DOMContentLoaded', function() {
    // Load templates
    loadTemplates();
    
    // Set up event listeners
    document.getElementById('createTemplateBtn').addEventListener('click', showCreateTemplateModal);
    document.getElementById('saveTemplateBtn').addEventListener('click', saveTemplate);
    document.getElementById('templateCategoryFilter').addEventListener('change', filterTemplates);
    document.getElementById('templateSearchInput').addEventListener('input', searchTemplates);
    
    // Template functions
    function loadTemplates() {
        fetch('/api/templates', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            }
        })
        .then(response => response.json())
        .then(data => {
            const templateList = document.getElementById('templateList');
            templateList.innerHTML = '';
            
            if (data.templates.length === 0) {
                templateList.innerHTML = '<div class="text-center p-4">No templates found. Create your first template!</div>';
                return;
            }
            
            // Group templates by category
            const templatesByCategory = {};
            data.templates.forEach(template => {
                const category = template.category || 'Uncategorized';
                if (!templatesByCategory[category]) {
                    templatesByCategory[category] = [];
                }
                templatesByCategory[category].push(template);
            });
            
            // Populate template list
            Object.keys(templatesByCategory).sort().forEach(category => {
                const categorySection = document.createElement('div');
                categorySection.className = 'template-category mb-4';
                categorySection.innerHTML = `
                    <h3 class="h5 mb-3">${category}</h3>
                    <div class="row template-category-items" data-category="${category}"></div>
                `;
                templateList.appendChild(categorySection);
                
                const categoryItems = categorySection.querySelector('.template-category-items');
                templatesByCategory[category].forEach(template => {
                    const templateCard = createTemplateCard(template);
                    categoryItems.appendChild(templateCard);
                });
            });
            
            // Update category filter options
            updateCategoryFilterOptions(Object.keys(templatesByCategory));
        })
        .catch(error => {
            console.error('Error loading templates:', error);
            showError('Failed to load templates. Please try again.');
        });
    }
    
    function createTemplateCard(template) {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        col.innerHTML = `
            <div class="card h-100 template-card" data-template-id="${template.id}" data-template-name="${template.name}" data-template-category="${template.category || 'Uncategorized'}">
                <div class="card-body">
                    <h5 class="card-title">${template.name}</h5>
                    <p class="card-text small text-muted">${template.description || 'No description'}</p>
                    <div class="template-tags mb-2">
                        ${template.tags ? template.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('') : ''}
                    </div>
                    <div class="template-meta small text-muted">
                        <div>Type: ${template.event_type || 'Not specified'}</div>
                        <div>Duration: ${template.duration_days || 'N/A'} days</div>
                        <div>Version: ${template.version}</div>
                    </div>
                </div>
                <div class="card-footer bg-transparent border-top-0">
                    <div class="btn-group w-100" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary use-template-btn" data-template-id="${template.id}">Use</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary edit-template-btn" data-template-id="${template.id}">Edit</button>
                        <button type="button" class="btn btn-sm btn-outline-danger delete-template-btn" data-template-id="${template.id}">Delete</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        col.querySelector('.use-template-btn').addEventListener('click', () => useTemplate(template.id));
        col.querySelector('.edit-template-btn').addEventListener('click', () => editTemplate(template.id));
        col.querySelector('.delete-template-btn').addEventListener('click', () => deleteTemplate(template.id));
        
        return col;
    }
    
    // More functions...
});
```

## Task 3.3: Advanced Agent Collaboration

### Multi-Agent Conversation Infrastructure

```python
# app/agents/agent_factory.py
class AgentFactory:
    """Factory for creating agents with tenant context."""
    
    def __init__(self, db: Session, organization_id: Optional[int] = None):
        """
        Initialize the agent factory.
        
        Args:
            db: Database session
            organization_id: Organization ID for tenant context
        """
        self.db = db
        self.organization_id = organization_id
        self.state_manager = TenantAwareStateManager(organization_id=organization_id)
        self.feature_control = SubscriptionFeatureControl(db=db, organization_id=organization_id)
    
    def create_multi_agent_conversation(
        self,
        primary_agent_type: str,
        supporting_agent_types: List[str],
        initial_message: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Create a new multi-agent conversation.
        
        Args:
            primary_agent_type: Primary agent type
            supporting_agent_types: List of supporting agent types
            initial_message: Initial message from the user
            user_id: User ID
            
        Returns:
            Conversation state
        """
        # Check subscription for access to all agent types
        all_agent_types = [primary_agent_type] + supporting_agent_types
        for agent_type in all_agent_types:
            if not self.feature_control.has_access_to_agent(agent_type):
                raise ValueError(f"Subscription does not include access to {agent_type} agent")
        
        # Create conversation state
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        state = {
            "conversation_id": conversation_id,
            "primary_agent_type": primary_agent_type,
            "supporting_agent_types": supporting_agent_types,
            "organization_id": self.organization_id,
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": [
                {
                    "role": "system",
                    "content": "This is a multi-agent conversation. The primary agent will coordinate with supporting agents to provide comprehensive assistance.",
                    "timestamp": timestamp
                },
                {
                    "role": "user",
                    "content": initial_message,
                    "timestamp": timestamp,
                    "user_id": user_id
                }
            ],
            "active_agent": primary_agent_type,
            "agent_states": {agent_type: {} for agent_type in all_agent_types},
            "shared_context": {},
            "handoff_history": []
        }
        
        # Save state
        self.state_manager.create_conversation_state(conversation_id, state)
        
        return state
    
    def get_agent_for_conversation(
        self,
        conversation_id: str,
        agent_type: Optional[str] = None
    ) -> BaseAgent:
        """
        Get an agent for a conversation.
        
        Args:
            conversation_id: Conversation ID
            agent_type: Agent type (if None, use the active agent from the conversation)
            
        Returns:
            Agent instance
        """
        # Get conversation state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Determine agent type
        if agent_type is None:
            agent_type = state.get("active_agent") or state.get("primary_agent_type")
        
        # Check if agent type is part of the conversation
        all_agent_types = [state.get("primary_agent_type")] + state.get("supporting_agent_types", [])
        if agent_type not in all_agent_types:
            raise ValueError(f"Agent type {agent_type} is not part of conversation {conversation_id}")
        
        # Create agent
        agent = self.create_agent(agent_type)
        
        # Set agent context
        agent_state = state.get("agent_states", {}).get(agent_type, {})
        agent.set_state(agent_state)
        
        # Set shared context
        shared_context = state.get("shared_context", {})
        agent.set_shared_context(shared_context)
        
        return agent
    
    def perform_agent_handoff(
        self,
        conversation_id: str,
        from_agent_type: str,
        to_agent_type: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Perform a handoff from one agent to another.
        
        Args:
            conversation_id: Conversation ID
            from_agent_type: Current agent type
            to_agent_type: Target agent type
            reason: Reason for handoff
            
        Returns:
            Updated conversation state
        """
        # Get conversation state
        state = self.state_manager.get_conversation_state(conversation_id)
        if not state:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Check if agent types are valid
        all_agent_types = [state.get("primary_agent_type")] + state.get("supporting_agent_types", [])
        if from_agent_type not in all_agent_types:
            raise ValueError(f"Agent type {from_agent_type} is not part of conversation {conversation_id}")
        if to_agent_type not in all_agent_types:
            raise ValueError(f"Agent type {to_agent_type} is not part of conversation {conversation_id}")
        
        # Update active agent
        state["active_agent"] = to_agent_type
        
        # Record handoff
        timestamp = datetime.utcnow().isoformat()
        handoff = {
            "from_agent": from_agent_type,
            "to_agent": to_agent_type,
            "reason": reason,
            "timestamp": timestamp
        }
        state.setdefault("handoff_history", []).append(handoff)
        
        # Add system message about handoff
        state["messages"].append({
            "role": "system",
            "content": f"Handoff from {from_agent_type} to {to_agent_type}: {reason}",
            "timestamp": timestamp
        })
        
        # Update state
        state["updated_at"] = timestamp
        self.state_manager.update_conversation_state(conversation_id, state)
        
        return state
```

## Task 3.4: Vendor Management

### Vendor Models

```python
# app/db/models_saas.py
class Vendor(Base):
    """Vendor model."""
    
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    services = Column(ARRAY(String), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tenant relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="vendors")
    
    # Relationships
    events = relationship("Event", secondary="event_vendors", back_populates="vendors")
    reviews = relationship("VendorReview", back_populates="vendor", cascade="all, delete-orphan")
    quotes = relationship("VendorQuote", back_populates="vendor", cascade="all, delete-orphan")
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        if not self.reviews:
            return None
        return sum(review.rating for review in self.reviews) / len(self.reviews)
```

## Task 3.5: Budget Tracking and Management

### Budget Visualization

```javascript
// app/web/static/saas/js/budget.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    const budgetBreakdownCtx = document.getElementById('budgetBreakdownChart').getContext('2d');
    const budgetTimelineCtx = document.getElementById('budgetTimelineChart').getContext('2d');
    
    let budgetBreakdownChart = new Chart(budgetBreakdownCtx, {
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
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    let budgetTimelineChart = new Chart(budgetTimelineCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Planned',
                    data: [],
                    backgroundColor: 'rgba(78, 115, 223, 0.8)',
                    borderColor: 'rgba(78, 115, 223, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Actual',
                    data: [],
                    backgroundColor: 'rgba(28, 200, 138, 0.8)',
                    borderColor: 'rgba(28, 200, 138, 1)',
                    borderWidth: 1
                }
            ]
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
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw || 0;
                            return `${label}: $${value.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });
    
    // Load budget data
    loadBudgetData();
    
    // Set up event listeners
    document.getElementById('refreshBudget').addEventListener('click', loadBudgetData);
    document.getElementById('addBudgetItemBtn').addEventListener('click', showAddBudgetItemModal);
    document.getElementById('saveBudgetItemBtn').addEventListener('click', saveBudgetItem);
    document.getElementById('exportBudgetBtn').addEventListener('click', exportBudget);
    
    // Budget functions
    function loadBudgetData() {
        const eventId = getEventIdFromUrl();
        if (!eventId) {
            showError('No event selected. Please select an event to view its budget.');
            return;
        }
        
        fetch(`/api/events/${eventId}/budget`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update budget summary
            document.getElementById('totalBudget').textContent = formatCurrency(data.total_budget);
            document.getElementById('totalExpenses').textContent = formatCurrency(data.total_expenses);
            document.getElementById('remainingBudget').textContent = formatCurrency(data.remaining_budget);
            
            // Update progress bar
            const progressPercentage = data.total_budget > 0 ? (data.total_expenses / data.total_budget) * 100 : 0;
            const progressBar = document.getElementById('budgetProgress');
            progressBar.style.width = `${Math.min(progressPercentage, 100)}%`;
            progressBar.setAttribute('aria-valuenow', progressPercentage);
            
            // Set progress bar color based on percentage
            if (progressPercentage > 90) {
                progressBar.className = 'progress-bar bg-danger';
            } else if (progressPercentage > 75) {
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-success';
            }
            
            // Update budget breakdown chart
            updateBudgetBreakdownChart(data.budget_items);
            
            // Update budget timeline chart
            updateBudgetTimelineChart(data.budget_timeline);
            
            // Update budget items table
            updateBudgetItemsTable(data.budget_items);
            
            // Update expense tracking table
            updateExpenseTrackingTable(data.expenses);
        })
        .catch(error => {
            console.error('Error loading budget data:', error);
            showError('Failed to load budget data. Please try again.');
        });
    }
    
    // More functions...
});
```

## Task 3.6: Offline Mode Enhancements

### Offline Detection and Synchronization

```javascript
// app/web/static/saas/js/offline.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize IndexedDB
    const dbPromise = initDatabase();
    
    // Set up network status monitoring
    setupNetworkMonitoring();
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/saas/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    }
    
    // Initialize sync manager
    const syncManager = new SyncManager(dbPromise);
    
    // Database initialization
    function initDatabase() {
        return idb.openDB('event-planner-db', 1, {
            upgrade(db) {
                // Create object stores
                if (!db.objectStoreNames.contains('events')) {
                    const eventStore = db.createObjectStore('events', { keyPath: 'id' });
                    eventStore.createIndex('organization_id', 'organization_id');
                    eventStore.createIndex('updated_at', 'updated_at');
                }
                
                if (!db.objectStoreNames.contains('conversations')) {
                    const conversationStore = db.createObjectStore('conversations', { keyPath: 'conversation_id' });
                    conversationStore.createIndex('organization_id', 'organization_id');
                    conversationStore.createIndex('updated_at', 'updated_at');
                }
                
                if (!db.objectStoreNames.contains('sync_queue')) {
                    const syncQueueStore = db.createObjectStore('sync_queue', { keyPath: 'id', autoIncrement: true });
                    syncQueueStore.createIndex('status', 'status');
                    syncQueueStore.createIndex('created_at', 'created_at');
                }
            }
        });
    }
    
    // Network monitoring
    function setupNetworkMonitoring() {
        const offlineIndicator = document.createElement('div');
        offlineIndicator.className = 'offline-indicator';
        offlineIndicator.innerHTML = '<i class="bi bi-wifi-off"></i> Offline Mode';
        document.body.appendChild(offlineIndicator);
        
        function updateOnlineStatus() {
            if (navigator.onLine) {
                document.body.classList.remove('offline');
                offlineIndicator.classList.remove('visible');
                
                // Attempt to sync when coming back online
                syncManager.syncAll().then(result => {
                    if (result.success) {
                        showNotification('Synchronized data with server', 'success');
                    } else {
                        showNotification('Some items failed to synchronize', 'warning');
                    }
                });
            } else {
                document.body.classList.add('offline');
                offlineIndicator.classList.add('visible');
                showNotification('You are offline. Changes will be saved locally and synchronized when you reconnect.', 'info');
            }
        }
