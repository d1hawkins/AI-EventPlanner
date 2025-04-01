/**
 * Events JavaScript
 * Handles functionality for the events pages in the AI Event Planner SaaS application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the events page
    const isEventsPage = window.location.pathname.endsWith('/events.html');
    
    if (isEventsPage) {
        initializeEventsPage();
    }
    
    // Initialize sidebar toggle functionality
    initializeSidebar();
});

/**
 * Initialize the events page functionality
 */
function initializeEventsPage() {
    // Initialize event filters
    const filtersForm = document.getElementById('eventFilters');
    if (filtersForm) {
        filtersForm.addEventListener('submit', function(event) {
            event.preventDefault();
            applyFilters();
        });
        
        filtersForm.addEventListener('reset', function() {
            setTimeout(function() {
                applyFilters();
            }, 10);
        });
    }
    
    // Initialize refresh button
    const refreshButton = document.getElementById('refreshEvents');
    if (refreshButton) {
        refreshButton.addEventListener('click', function(event) {
            event.preventDefault();
            loadEvents();
        });
    }
    
    // Initialize export button
    const exportButton = document.getElementById('exportEvents');
    if (exportButton) {
        exportButton.addEventListener('click', function(event) {
            event.preventDefault();
            exportEvents();
        });
    }
    
    // Initialize calendar view options
    const calendarViewOptions = document.querySelectorAll('#calendarViewDropdown a');
    calendarViewOptions.forEach(option => {
        option.addEventListener('click', function(event) {
            event.preventDefault();
            const viewType = this.id;
            updateCalendarView(viewType);
        });
    });
    
    // Initialize enable calendar button
    const enableCalendarButton = document.getElementById('enableCalendar');
    if (enableCalendarButton) {
        enableCalendarButton.addEventListener('click', function() {
            enableCalendar();
        });
    }
    
    // Initialize delete event functionality
    initializeDeleteEventButtons();
    
    // Load events data
    loadEvents();
}

/**
 * Initialize the sidebar toggle functionality
 */
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarToggleTop = document.getElementById('sidebarToggleTop');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
            
            if (document.querySelector('.sidebar').classList.contains('toggled')) {
                document.querySelector('.sidebar .collapse').classList.remove('show');
                sidebarToggle.setAttribute('aria-expanded', 'false');
            } else {
                sidebarToggle.setAttribute('aria-expanded', 'true');
            }
        });
    }
    
    if (sidebarToggleTop) {
        sidebarToggleTop.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }
    
    // Close sidebar on small screens
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    function handleScreenChange(e) {
        if (e.matches) {
            document.querySelector('.sidebar').classList.add('toggled');
        }
    }
    mediaQuery.addEventListener('change', handleScreenChange);
    handleScreenChange(mediaQuery);
}

/**
 * Apply filters to the events table
 */
function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const dateRangeFilter = document.getElementById('dateRangeFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    
    // In a real application, this would make an API call with the filters
    // For now, we'll just simulate filtering with a loading state
    
    const eventsTable = document.getElementById('eventsTableBody');
    eventsTable.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';
    
    // Simulate API call delay
    setTimeout(function() {
        loadEvents(statusFilter, dateRangeFilter, typeFilter);
    }, 500);
}

/**
 * Load events data
 * @param {string} status - Status filter
 * @param {string} dateRange - Date range filter
 * @param {string} type - Event type filter
 */
function loadEvents(status = '', dateRange = '', type = '') {
    // In a real application, this would make an API call to get events
    // For now, we'll just use sample data
    
    // Simulate API call delay
    const eventsTable = document.getElementById('eventsTableBody');
    eventsTable.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';
    
    setTimeout(function() {
        // Sample data - in a real app, this would come from the API
        const events = [
            {
                id: 1,
                title: 'Tech Conference 2025',
                start_date: '2025-04-15',
                end_date: '2025-04-17',
                location: 'San Francisco, CA',
                attendee_count: 500,
                status: 'planning'
            },
            {
                id: 2,
                title: 'Company Retreat',
                start_date: '2025-05-10',
                end_date: '2025-05-12',
                location: 'Lake Tahoe, CA',
                attendee_count: 50,
                status: 'confirmed'
            },
            {
                id: 3,
                title: 'Product Launch',
                start_date: '2025-06-05',
                end_date: '2025-06-05',
                location: 'New York, NY',
                attendee_count: 200,
                status: 'draft'
            },
            {
                id: 4,
                title: 'Annual Gala',
                start_date: '2025-07-20',
                end_date: '2025-07-20',
                location: 'Chicago, IL',
                attendee_count: 300,
                status: 'confirmed'
            },
            {
                id: 5,
                title: 'Team Building Workshop',
                start_date: '2025-08-15',
                end_date: '2025-08-16',
                location: 'Austin, TX',
                attendee_count: 25,
                status: 'planning'
            }
        ];
        
        // Apply filters
        let filteredEvents = events;
        
        if (status) {
            filteredEvents = filteredEvents.filter(event => event.status === status);
        }
        
        if (type) {
            // In a real app, events would have a type property
            // For now, we'll just simulate this filter
            if (type === 'conference') {
                filteredEvents = filteredEvents.filter(event => 
                    event.title.toLowerCase().includes('conference') || 
                    event.title.toLowerCase().includes('summit')
                );
            } else if (type === 'meeting') {
                filteredEvents = filteredEvents.filter(event => 
                    event.title.toLowerCase().includes('meeting')
                );
            } else if (type === 'workshop') {
                filteredEvents = filteredEvents.filter(event => 
                    event.title.toLowerCase().includes('workshop')
                );
            } else if (type === 'social') {
                filteredEvents = filteredEvents.filter(event => 
                    event.title.toLowerCase().includes('gala') || 
                    event.title.toLowerCase().includes('party') ||
                    event.title.toLowerCase().includes('retreat')
                );
            }
        }
        
        if (dateRange) {
            const now = new Date();
            const thisMonth = now.getMonth();
            const thisYear = now.getFullYear();
            
            if (dateRange === 'upcoming') {
                filteredEvents = filteredEvents.filter(event => {
                    const eventDate = new Date(event.start_date);
                    return eventDate >= now;
                });
            } else if (dateRange === 'past') {
                filteredEvents = filteredEvents.filter(event => {
                    const eventDate = new Date(event.start_date);
                    return eventDate < now;
                });
            } else if (dateRange === 'thisMonth') {
                filteredEvents = filteredEvents.filter(event => {
                    const eventDate = new Date(event.start_date);
                    return eventDate.getMonth() === thisMonth && 
                           eventDate.getFullYear() === thisYear;
                });
            } else if (dateRange === 'nextMonth') {
                filteredEvents = filteredEvents.filter(event => {
                    const eventDate = new Date(event.start_date);
                    const nextMonth = (thisMonth + 1) % 12;
                    const yearOfNextMonth = thisMonth === 11 ? thisYear + 1 : thisYear;
                    return eventDate.getMonth() === nextMonth && 
                           eventDate.getFullYear() === yearOfNextMonth;
                });
            } else if (dateRange === 'thisYear') {
                filteredEvents = filteredEvents.filter(event => {
                    const eventDate = new Date(event.start_date);
                    return eventDate.getFullYear() === thisYear;
                });
            }
        }
        
        // Render events
        renderEvents(filteredEvents);
        
        // Initialize delete event buttons
        initializeDeleteEventButtons();
    }, 500);
}

/**
 * Render events in the table
 * @param {Array} events - Array of event objects
 */
function renderEvents(events) {
    const eventsTable = document.getElementById('eventsTableBody');
    
    if (events.length === 0) {
        eventsTable.innerHTML = '<tr><td colspan="6" class="text-center">No events found</td></tr>';
        return;
    }
    
    let html = '';
    
    events.forEach(event => {
        // Format date range
        let dateDisplay = formatDateRange(event.start_date, event.end_date);
        
        // Get status badge class
        let statusBadgeClass = getStatusBadgeClass(event.status);
        
        html += `
            <tr data-event-id="${event.id}">
                <td>${event.title}</td>
                <td>${dateDisplay}</td>
                <td>${event.location}</td>
                <td>${event.attendee_count}</td>
                <td><span class="badge ${statusBadgeClass}">${capitalizeFirstLetter(event.status)}</span></td>
                <td>
                    <div class="btn-group" role="group" aria-label="Event actions">
                        <a href="#" class="btn btn-primary btn-sm view-event" aria-label="View ${event.title}">
                            <i class="bi bi-eye" aria-hidden="true"></i>
                        </a>
                        <a href="#" class="btn btn-info btn-sm edit-event" aria-label="Edit ${event.title}">
                            <i class="bi bi-pencil" aria-hidden="true"></i>
                        </a>
                        <a href="#" class="btn btn-danger btn-sm delete-event" aria-label="Delete ${event.title}" data-event-id="${event.id}" data-event-title="${event.title}">
                            <i class="bi bi-trash" aria-hidden="true"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
    });
    
    eventsTable.innerHTML = html;
}

/**
 * Format a date range for display
 * @param {string} startDate - Start date in YYYY-MM-DD format
 * @param {string} endDate - End date in YYYY-MM-DD format
 * @returns {string} Formatted date range
 */
function formatDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    const startMonth = start.toLocaleString('default', { month: 'short' });
    const endMonth = end.toLocaleString('default', { month: 'short' });
    
    const startDay = start.getDate();
    const endDay = end.getDate();
    
    const startYear = start.getFullYear();
    const endYear = end.getFullYear();
    
    if (startDate === endDate) {
        return `${startMonth} ${startDay}, ${startYear}`;
    } else if (startMonth === endMonth && startYear === endYear) {
        return `${startMonth} ${startDay}-${endDay}, ${startYear}`;
    } else if (startYear === endYear) {
        return `${startMonth} ${startDay} - ${endMonth} ${endDay}, ${startYear}`;
    } else {
        return `${startMonth} ${startDay}, ${startYear} - ${endMonth} ${endDay}, ${endYear}`;
    }
}

/**
 * Get the appropriate badge class for a status
 * @param {string} status - Event status
 * @returns {string} Bootstrap badge class
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case 'draft':
            return 'bg-primary';
        case 'planning':
            return 'bg-warning';
        case 'confirmed':
            return 'bg-info';
        case 'completed':
            return 'bg-success';
        case 'cancelled':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

/**
 * Capitalize the first letter of a string
 * @param {string} string - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Initialize delete event buttons
 */
function initializeDeleteEventButtons() {
    const deleteButtons = document.querySelectorAll('.delete-event');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            const eventId = this.getAttribute('data-event-id');
            const eventTitle = this.getAttribute('data-event-title');
            
            // Set the event name in the modal
            document.getElementById('deleteEventName').textContent = eventTitle;
            
            // Store the event ID for the confirm button
            document.getElementById('confirmDeleteEvent').setAttribute('data-event-id', eventId);
            
            // Show the modal
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteEventModal'));
            deleteModal.show();
        });
    });
    
    // Initialize confirm delete button
    const confirmDeleteButton = document.getElementById('confirmDeleteEvent');
    if (confirmDeleteButton) {
        confirmDeleteButton.addEventListener('click', function() {
            const eventId = this.getAttribute('data-event-id');
            deleteEvent(eventId);
            
            // Hide the modal
            const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteEventModal'));
            deleteModal.hide();
        });
    }
}

/**
 * Delete an event
 * @param {string} eventId - Event ID
 */
function deleteEvent(eventId) {
    // In a real application, this would make an API call to delete the event
    // For now, we'll just simulate deletion
    
    // Remove the event from the table
    const eventRow = document.querySelector(`tr[data-event-id="${eventId}"]`);
    if (eventRow) {
        eventRow.remove();
    }
    
    // Show success message
    showAlert('Event deleted successfully', 'success');
}

/**
 * Export events
 */
function exportEvents() {
    // In a real application, this would generate a CSV or Excel file
    // For now, we'll just show a message
    showAlert('Events exported successfully', 'success');
}

/**
 * Update calendar view
 * @param {string} viewType - Calendar view type (monthView, weekView, dayView)
 */
function updateCalendarView(viewType) {
    // In a real application, this would update the calendar view
    // For now, we'll just show a message
    showAlert(`Calendar view changed to ${viewType.replace('View', '')}`, 'info');
}

/**
 * Enable calendar view
 */
function enableCalendar() {
    // In a real application, this would initialize a calendar library
    // For now, we'll just show a message
    showAlert('Calendar view will be available in a future update', 'info');
}

/**
 * Show an alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, info, warning, danger)
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add alert to the page
    const mainContent = document.getElementById('main-content');
    mainContent.insertBefore(alertElement, mainContent.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertElement);
        bsAlert.close();
    }, 5000);
}
