/**
 * Events JavaScript
 * Handles functionality for the events pages in the AI Event Planner SaaS application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the events page
    const isEventsPage = window.location.pathname.endsWith('/events.html');
    const isNewEventPage = window.location.pathname.endsWith('/events-new.html');
    
    if (isEventsPage) {
        initializeEventsPage();
    } else if (isNewEventPage) {
        initializeNewEventPage();
    }
    
    // Initialize sidebar toggle functionality
    initializeSidebar();
});

/**
 * Initialize the new event page functionality
 */
function initializeNewEventPage() {
    // Initialize the new event form
    const newEventForm = document.getElementById('newEventForm');
    if (newEventForm) {
        newEventForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Validate form
            if (!newEventForm.checkValidity()) {
                event.stopPropagation();
                newEventForm.classList.add('was-validated');
                return;
            }
            
            // Get form data
            const formData = new FormData(newEventForm);
            
            // Build recurrence rule if this is a recurring event
            let recurrenceRule = null;
            let recurrenceEndDate = null;
            let isRecurring = formData.get('is_recurring') === 'on';
            
            if (isRecurring) {
                recurrenceRule = buildRecurrenceRule(formData);
                recurrenceEndDate = getRecurrenceEndDate(formData);
            }
            
            // Prepare event data
            const eventData = {
                title: formData.get('title'),
                event_type: formData.get('event_type'),
                description: formData.get('description'),
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date'),
                location: buildLocationString(formData),
                budget: formData.get('budget') ? Math.round(parseFloat(formData.get('budget')) * 100) : null, // Convert to cents
                attendee_count: formData.get('attendee_count') ? parseInt(formData.get('attendee_count')) : null,
                status: formData.get('status') || 'draft',
                
                // Recurrence fields
                is_recurring: isRecurring,
                recurrence_rule: recurrenceRule,
                recurrence_end_date: recurrenceEndDate
            };
            
            // Submit the event data
            createEvent(eventData);
        });
    }
}

/**
 * Build a location string from form data
 * @param {FormData} formData - Form data
 * @returns {string} Location string
 */
function buildLocationString(formData) {
    const locationType = formData.get('location_type');
    
    if (locationType === 'physical') {
        const venue = formData.get('venue') || '';
        const address = formData.get('address') || '';
        const city = formData.get('city') || '';
        const state = formData.get('state') || '';
        const zip = formData.get('zip') || '';
        const country = formData.get('country') || '';
        
        // Build location string
        let location = venue;
        
        if (address) {
            location += location ? `, ${address}` : address;
        }
        
        let cityStateZip = '';
        if (city) cityStateZip += city;
        if (state) cityStateZip += cityStateZip ? `, ${state}` : state;
        if (zip) cityStateZip += cityStateZip ? ` ${zip}` : zip;
        
        if (cityStateZip) {
            location += location ? `, ${cityStateZip}` : cityStateZip;
        }
        
        if (country) {
            location += location ? `, ${country}` : country;
        }
        
        return location;
    } else if (locationType === 'virtual') {
        const platform = formData.get('virtual_platform') || '';
        const link = formData.get('virtual_link') || '';
        
        if (platform && link) {
            return `${platform}: ${link}`;
        } else if (platform) {
            return platform;
        } else if (link) {
            return link;
        } else {
            return 'Virtual';
        }
    } else if (locationType === 'hybrid') {
        const physical = buildLocationString(new FormData(document.getElementById('newEventForm')));
        const virtual = formData.get('virtual_link') || '';
        
        if (physical && virtual) {
            return `${physical} & ${virtual}`;
        } else if (physical) {
            return `${physical} (Hybrid)`;
        } else if (virtual) {
            return `${virtual} (Hybrid)`;
        } else {
            return 'Hybrid';
        }
    }
    
    return '';
}

/**
 * Build a recurrence rule from form data
 * @param {FormData} formData - Form data
 * @returns {string} Recurrence rule in iCalendar RRULE format
 */
function buildRecurrenceRule(formData) {
    const frequency = formData.get('recurrence_frequency');
    const interval = formData.get('recurrence_interval') || 1;
    
    // Start with basic rule
    let rule = `FREQ=${frequency.toUpperCase()};INTERVAL=${interval}`;
    
    // Add weekdays for weekly recurrence
    if (frequency === 'weekly') {
        const weekdays = [];
        if (formData.get('weekday_sun') === 'on') weekdays.push('SU');
        if (formData.get('weekday_mon') === 'on') weekdays.push('MO');
        if (formData.get('weekday_tue') === 'on') weekdays.push('TU');
        if (formData.get('weekday_wed') === 'on') weekdays.push('WE');
        if (formData.get('weekday_thu') === 'on') weekdays.push('TH');
        if (formData.get('weekday_fri') === 'on') weekdays.push('FR');
        if (formData.get('weekday_sat') === 'on') weekdays.push('SA');
        
        if (weekdays.length > 0) {
            rule += `;BYDAY=${weekdays.join(',')}`;
        }
    }
    
    // Add monthly repeat options
    if (frequency === 'monthly') {
        const repeatBy = formData.get('monthly_repeat_by');
        
        if (repeatBy === 'day_position') {
            // Get the day of month from the start date
            const startDate = new Date(formData.get('start_date'));
            const dayOfMonth = startDate.getDate();
            
            // Calculate the position (1st, 2nd, 3rd, 4th, last)
            let position;
            if (dayOfMonth <= 7) position = 1;
            else if (dayOfMonth <= 14) position = 2;
            else if (dayOfMonth <= 21) position = 3;
            else if (dayOfMonth <= 28) position = 4;
            else position = -1; // last
            
            // Get the day of week
            const dayOfWeek = startDate.getDay(); // 0 = Sunday, 1 = Monday, etc.
            const days = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'];
            
            rule += `;BYDAY=${position}${days[dayOfWeek]}`;
        }
    }
    
    // Add count or until for recurrence end
    const endType = formData.get('recurrence_end_type');
    
    if (endType === 'after') {
        const count = formData.get('recurrence_end_after_count') || 10;
        rule += `;COUNT=${count}`;
    } else if (endType === 'on') {
        const endDate = formData.get('recurrence_end_date');
        if (endDate) {
            // Format date as YYYYMMDD for UNTIL
            const date = new Date(endDate);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            rule += `;UNTIL=${year}${month}${day}T235959Z`;
        }
    }
    
    return rule;
}

/**
 * Get the recurrence end date from form data
 * @param {FormData} formData - Form data
 * @returns {string|null} Recurrence end date in ISO format, or null if not specified
 */
function getRecurrenceEndDate(formData) {
    const endType = formData.get('recurrence_end_type');
    
    if (endType === 'on') {
        return formData.get('recurrence_end_date');
    } else if (endType === 'after') {
        // Calculate end date based on count and frequency
        const count = parseInt(formData.get('recurrence_end_after_count') || 10);
        const frequency = formData.get('recurrence_frequency');
        const interval = parseInt(formData.get('recurrence_interval') || 1);
        const startDate = new Date(formData.get('start_date'));
        
        let endDate = new Date(startDate);
        
        switch (frequency) {
            case 'daily':
                endDate.setDate(endDate.getDate() + (count * interval));
                break;
            case 'weekly':
                endDate.setDate(endDate.getDate() + (count * interval * 7));
                break;
            case 'monthly':
                endDate.setMonth(endDate.getMonth() + (count * interval));
                break;
            case 'yearly':
                endDate.setFullYear(endDate.getFullYear() + (count * interval));
                break;
        }
        
        return endDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    }
    
    return null;
}

/**
 * Create a new event
 * @param {Object} eventData - Event data
 */
function createEvent(eventData) {
    // In a real application, this would make an API call to create the event
    // For now, we'll just simulate creation
    
    console.log('Creating event:', eventData);
    
    // Simulate API call
    setTimeout(function() {
        // Redirect to events page
        showAlert('Event created successfully', 'success');
        
        // In a real app, we would redirect after the API call succeeds
        setTimeout(function() {
            window.location.href = '/saas/events.html';
        }, 1500);
    }, 1000);
}

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
    
    // Initialize export buttons
    const exportButton = document.getElementById('exportEvents');
    if (exportButton) {
        exportButton.addEventListener('click', function(event) {
            event.preventDefault();
            exportEvents();
        });
    }
    
    const exportCalendarButton = document.getElementById('exportCalendar');
    if (exportCalendarButton) {
        exportCalendarButton.addEventListener('click', function(event) {
            event.preventDefault();
            exportEvents(); // Reuse the same export function
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
            },
            {
                id: 6,
                title: 'Weekly Team Meeting',
                start_date: '2025-04-01',
                end_date: '2025-04-01',
                location: 'Conference Room A',
                attendee_count: 15,
                status: 'confirmed',
                is_recurring: true,
                recurrence_rule: 'FREQ=WEEKLY;INTERVAL=1;BYDAY=TU'
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
        
        // Add recurrence indicator
        if (event.is_recurring) {
            dateDisplay += ' <span class="badge bg-info">Recurring</span>';
        }
        
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
    // Create a hidden iframe to handle the download
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    document.body.appendChild(iframe);
    
    try {
        // Try to fetch from the API endpoint
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
            
            // For demo/development, create a mock ICS file
            const mockIcsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Event Planner//NONSGML v1.0//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:AI Event Planner Calendar
X-WR-TIMEZONE:America/New_York
BEGIN:VEVENT
UID:event-1@aieventplanner.com
SUMMARY:Tech Conference 2025
DESCRIPTION:Annual technology conference with industry leaders
LOCATION:San Francisco, CA
DTSTART:20250415T000000Z
DTEND:20250417T235959Z
STATUS:TENTATIVE
CATEGORIES:conference
END:VEVENT
BEGIN:VEVENT
UID:event-2@aieventplanner.com
SUMMARY:Company Retreat
DESCRIPTION:Team building and strategy planning retreat
LOCATION:Lake Tahoe, CA
DTSTART:20250510T000000Z
DTEND:20250512T235959Z
STATUS:CONFIRMED
CATEGORIES:social
END:VEVENT
BEGIN:VEVENT
UID:event-3@aieventplanner.com
SUMMARY:Product Launch
DESCRIPTION:Launch event for our new product line
LOCATION:New York, NY
DTSTART:20250605T000000Z
DTEND:20250605T235959Z
STATUS:TENTATIVE
CATEGORIES:marketing
END:VEVENT
END:VCALENDAR`;
            
            const blob = new Blob([mockIcsContent], { type: 'text/calendar' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'calendar.ics';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            showAlert('Calendar exported successfully (demo mode)', 'success');
        })
        .finally(() => {
            // Clean up
            document.body.removeChild(iframe);
        });
    } catch (error) {
        console.error('Error in export function:', error);
        showAlert('Failed to export calendar', 'danger');
        document.body.removeChild(iframe);
    }
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
    // Hide the placeholder message
    const calendarContainer = document.getElementById('calendar');
    calendarContainer.innerHTML = '';
    
    // Show loading indicator
    const loadingIndicator = document.getElementById('calendarLoading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    
    // Load calendar script if not already loaded
    if (typeof FullCalendar === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js';
        script.onload = function() {
            initializeCalendar();
        };
        document.head.appendChild(script);
    } else {
        initializeCalendar();
    }
    
    function initializeCalendar() {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        showAlert('Calendar view enabled', 'success');
    }
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
