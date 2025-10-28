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
            let events = [];
            
            // Process each event
            data.events.forEach(event => {
                // Create the base event object
                const baseEvent = {
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
                        status: event.status,
                        is_recurring: event.is_recurring,
                        recurrence_rule: event.recurrence_rule,
                        recurrence_end_date: event.recurrence_end_date,
                        parent_event_id: event.parent_event_id
                    },
                    backgroundColor: getEventColor(event.status),
                    borderColor: getEventColor(event.status)
                };
                
                // Add the base event
                events.push(baseEvent);
                
                // If it's a recurring event, expand it
                if (event.is_recurring && event.recurrence_rule) {
                    const expandedEvents = expandRecurringEvent(event, info.start, info.end);
                    events = events.concat(expandedEvents);
                }
            });
            
            successCallback(events);
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            failureCallback(error);
            showAlert('Failed to load calendar events: ' + error.message, 'danger');
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
    
    function handleDateClick(info) {
        // Handle click on a date (create new event)
        const modal = new bootstrap.Modal(document.getElementById('newEventModal'));
        
        // Set the date in the form
        const dateStr = info.dateStr;
        document.getElementById('newEventStartDate').value = dateStr;
        document.getElementById('newEventEndDate').value = dateStr;
        
        modal.show();
    }
    
    function handleDateSelect(info) {
        // Handle date range selection
        const modal = new bootstrap.Modal(document.getElementById('newEventModal'));
        
        // Set the date range in the form
        document.getElementById('newEventStartDate').value = info.startStr;
        document.getElementById('newEventEndDate').value = info.endStr;
        
        modal.show();
        
        // Clear the selection
        calendar.unselect();
    }
    
    function handleEventDrop(info) {
        // Handle event drag and drop
        updateEventDates(info.event);
    }
    
    function handleEventResize(info) {
        // Handle event resize
        updateEventDates(info.event);
    }
    
    function handleLoading(isLoading) {
        // Show/hide loading indicator
        const loadingIndicator = document.getElementById('calendarLoading');
        if (loadingIndicator) {
            loadingIndicator.style.display = isLoading ? 'block' : 'none';
        }
    }
    
    function updateEventDates(event) {
        // Update event dates after drag/resize
        const eventId = event.id;
        const startDate = event.start;
        const endDate = event.end || startDate;
        
        fetch(`/api/events/${eventId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            },
            body: JSON.stringify({
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString()
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update event dates');
            }
            return response.json();
        })
        .then(data => {
            showAlert('Event dates updated successfully', 'success');
        })
        .catch(error => {
            console.error('Error updating event dates:', error);
            showAlert('Failed to update event dates: ' + error.message, 'danger');
            info.revert();
        });
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
    
    function formatTimeRange(start, end) {
        if (!start || !end) return '';
        
        const startTime = start.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        const endTime = end.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        
        return `${startTime} - ${endTime}`;
    }
    
    function formatEventType(type) {
        if (!type) return 'Not specified';
        
        return type.charAt(0).toUpperCase() + type.slice(1);
    }
    
    function formatStatus(status) {
        if (!status) return 'Not specified';
        
        return status.charAt(0).toUpperCase() + status.slice(1);
    }
    
    // Initialize calendar view options
    document.querySelectorAll('#calendarViewDropdown a').forEach(option => {
        option.addEventListener('click', function(event) {
            event.preventDefault();
            
            const viewType = this.id;
            
            switch (viewType) {
                case 'monthView':
                    calendar.changeView('dayGridMonth');
                    break;
                case 'weekView':
                    calendar.changeView('timeGridWeek');
                    break;
                case 'dayView':
                    calendar.changeView('timeGridDay');
                    break;
                case 'printCalendar':
                    window.print();
                    break;
            }
        });
    });
    
    // Initialize new event form
    const newEventForm = document.getElementById('newEventForm');
    if (newEventForm) {
        newEventForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const formData = new FormData(newEventForm);
            const eventData = {
                title: formData.get('title'),
                description: formData.get('description'),
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date'),
                location: formData.get('location'),
                event_type: formData.get('event_type'),
                attendee_count: formData.get('attendee_count'),
                status: 'draft'
            };
            
            fetch('/api/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
                },
                body: JSON.stringify(eventData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to create event');
                }
                return response.json();
            })
            .then(data => {
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('newEventModal'));
                modal.hide();
                
                // Reset the form
                newEventForm.reset();
                
                // Refresh the calendar
                calendar.refetchEvents();
                
                showAlert('Event created successfully', 'success');
            })
            .catch(error => {
                console.error('Error creating event:', error);
                showAlert('Failed to create event: ' + error.message, 'danger');
            });
        });
    }
    
    // Initialize event details modal buttons
    const editEventBtn = document.getElementById('editEventBtn');
    if (editEventBtn) {
        editEventBtn.addEventListener('click', function() {
            const eventId = this.getAttribute('data-event-id');
            window.location.href = `/saas/events-edit.html?id=${eventId}`;
        });
    }
    
    const deleteEventBtn = document.getElementById('deleteEventBtn');
    if (deleteEventBtn) {
        deleteEventBtn.addEventListener('click', function() {
            const eventId = this.getAttribute('data-event-id');
            
            // Close the details modal
            const detailsModal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
            detailsModal.hide();
            
            // Show the delete confirmation modal
            document.getElementById('deleteEventName').textContent = document.getElementById('eventTitle').textContent;
            document.getElementById('confirmDeleteEvent').setAttribute('data-event-id', eventId);
            
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteEventModal'));
            deleteModal.show();
        });
    }
    
    // Initialize export calendar button
    const exportCalendarBtn = document.getElementById('exportCalendar');
    if (exportCalendarBtn) {
        exportCalendarBtn.addEventListener('click', function() {
            fetch('/api/events/export', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to export calendar');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'calendar.ics';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                showAlert('Calendar exported successfully', 'success');
            })
            .catch(error => {
                console.error('Error exporting calendar:', error);
                showAlert('Failed to export calendar: ' + error.message, 'danger');
            });
        });
    }
});

// Function to expand recurring events based on recurrence rule
function expandRecurringEvent(event, rangeStart, rangeEnd) {
    // If no recurrence rule or not a recurring event, return empty array
    if (!event.is_recurring || !event.recurrence_rule) {
        return [];
    }
    
    const expandedEvents = [];
    const baseStart = new Date(event.start_date);
    const baseEnd = new Date(event.end_date);
    const duration = baseEnd - baseStart; // Duration in milliseconds
    
    // Parse the recurrence rule (simplified implementation)
    // In a real app, use a library like rrule.js for full RFC 5545 support
    const rrule = parseRecurrenceRule(event.recurrence_rule);
    
    // Determine the recurrence end date
    let recurrenceEndDate = null;
    if (event.recurrence_end_date) {
        recurrenceEndDate = new Date(event.recurrence_end_date);
    } else if (rrule.count) {
        // If count is specified, calculate the end date based on count
        // This is a simplified implementation
        const maxDate = new Date(baseStart);
        maxDate.setDate(maxDate.getDate() + (rrule.count * rrule.interval * 7)); // Rough estimate
        recurrenceEndDate = maxDate;
    } else {
        // If no end date or count, use the range end as the limit
        recurrenceEndDate = new Date(rangeEnd);
    }
    
    // Limit the recurrence end date to the range end
    if (recurrenceEndDate > rangeEnd) {
        recurrenceEndDate = new Date(rangeEnd);
    }
    
    // Generate occurrences based on frequency
    let currentDate = new Date(baseStart);
    
    // Skip the first occurrence as it's already included as the base event
    switch (rrule.freq) {
        case 'daily':
            currentDate.setDate(currentDate.getDate() + rrule.interval);
            break;
        case 'weekly':
            currentDate.setDate(currentDate.getDate() + (rrule.interval * 7));
            break;
        case 'monthly':
            currentDate.setMonth(currentDate.getMonth() + rrule.interval);
            break;
        case 'yearly':
            currentDate.setFullYear(currentDate.getFullYear() + rrule.interval);
            break;
    }
    
    // Generate occurrences until the end date
    while (currentDate <= recurrenceEndDate) {
        // Check if this occurrence falls within the requested range
        if (currentDate >= rangeStart) {
            // Calculate the end date for this occurrence
            const occurrenceEnd = new Date(currentDate.getTime() + duration);
            
            // Check if this date should be excluded (simplified)
            const shouldExclude = event.recurrence_exceptions && 
                event.recurrence_exceptions.some(exDate => {
                    const exclusionDate = new Date(exDate);
                    return exclusionDate.toDateString() === currentDate.toDateString();
                });
            
            if (!shouldExclude) {
                // Create a new event object for this occurrence
                expandedEvents.push({
                    id: `${event.id}_${currentDate.toISOString()}`,
                    title: event.title,
                    start: currentDate.toISOString(),
                    end: occurrenceEnd.toISOString(),
                    allDay: !event.start_time,
                    location: event.location,
                    extendedProps: {
                        ...event.extendedProps,
                        parent_event_id: event.id,
                        is_recurring_instance: true
                    },
                    backgroundColor: getEventColor(event.status),
                    borderColor: getEventColor(event.status)
                });
            }
        }
        
        // Move to the next occurrence
        switch (rrule.freq) {
            case 'daily':
                currentDate.setDate(currentDate.getDate() + rrule.interval);
                break;
            case 'weekly':
                currentDate.setDate(currentDate.getDate() + (rrule.interval * 7));
                break;
            case 'monthly':
                currentDate.setMonth(currentDate.getMonth() + rrule.interval);
                break;
            case 'yearly':
                currentDate.setFullYear(currentDate.getFullYear() + rrule.interval);
                break;
        }
    }
    
    return expandedEvents;
}

// Helper function to parse recurrence rule (simplified)
function parseRecurrenceRule(rruleStr) {
    // Default values
    const rrule = {
        freq: 'daily',
        interval: 1,
        count: null,
        byDay: null
    };
    
    // Parse the rule string (simplified)
    // Example: "FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR"
    if (rruleStr) {
        const parts = rruleStr.split(';');
        
        parts.forEach(part => {
            const [key, value] = part.split('=');
            
            switch (key) {
                case 'FREQ':
                    if (value === 'DAILY') rrule.freq = 'daily';
                    else if (value === 'WEEKLY') rrule.freq = 'weekly';
                    else if (value === 'MONTHLY') rrule.freq = 'monthly';
                    else if (value === 'YEARLY') rrule.freq = 'yearly';
                    break;
                case 'INTERVAL':
                    rrule.interval = parseInt(value) || 1;
                    break;
                case 'COUNT':
                    rrule.count = parseInt(value);
                    break;
                case 'BYDAY':
                    rrule.byDay = value.split(',');
                    break;
            }
        });
    }
    
    return rrule;
}

// Show an alert message (reused from events.js)
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
