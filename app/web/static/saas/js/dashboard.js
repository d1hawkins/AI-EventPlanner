/**
 * AI Event Planner SaaS - Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const body = document.querySelector('body');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
            
            // Change the icon
            const icon = sidebarToggle.querySelector('i');
            if (icon.classList.contains('bi-arrow-left-circle')) {
                icon.classList.remove('bi-arrow-left-circle');
                icon.classList.add('bi-arrow-right-circle');
            } else {
                icon.classList.remove('bi-arrow-right-circle');
                icon.classList.add('bi-arrow-left-circle');
            }
        });
    }
    
    // Mobile Sidebar Toggle
    const sidebarToggleTop = document.getElementById('sidebarToggleTop');
    
    if (sidebarToggleTop) {
        sidebarToggleTop.addEventListener('click', function(e) {
            e.preventDefault();
            body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }
    
    // Close sidebar on small screens
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    
    function handleScreenChange(e) {
        if (e.matches && document.querySelector('.sidebar').classList.contains('toggled') === false) {
            body.classList.add('sidebar-toggled');
            document.querySelector('.sidebar').classList.add('toggled');
        }
    }
    
    mediaQuery.addEventListener('change', handleScreenChange);
    handleScreenChange(mediaQuery);
    
    // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
    document.querySelector('.sidebar').addEventListener('mousewheel', function(e) {
        if (this.classList.contains('toggled') === false) {
            const delta = e.wheelDelta || -e.detail;
            this.scrollTop += (delta < 0 ? 1 : -1) * 30;
            e.preventDefault();
        }
    });
    
    // Tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers initialization
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Dropdowns
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.map(function(dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // Modals
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function(modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
    
    // Scroll to top button
    const scrollToTopBtn = document.getElementById('scrollToTop');
    
    if (scrollToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 100) {
                scrollToTopBtn.style.display = 'block';
            } else {
                scrollToTopBtn.style.display = 'none';
            }
        });
        
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Initialize search functionality
    initializeSearch();

    // Load real chart data from analytics API
    if (typeof Chart !== 'undefined') {
        loadDashboardCharts();
    }
});

/**
 * Initialize search functionality
 */
function initializeSearch() {
    // Desktop search
    const searchButton = document.getElementById('search-button');
    const searchInput = document.querySelector('.navbar-search input[type="text"]');
    const searchForm = document.querySelector('.navbar-search');

    // Mobile search
    const mobileSearchButton = document.getElementById('mobile-search-button');
    const mobileSearchInput = document.querySelector('.dropdown-menu .navbar-search input[type="text"]');
    const mobileSearchForm = document.querySelector('.dropdown-menu .navbar-search');

    // Handle desktop search
    if (searchButton && searchInput) {
        searchButton.addEventListener('click', function(e) {
            e.preventDefault();
            performSearch(searchInput.value);
        });

        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                performSearch(searchInput.value);
            });
        }

        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value);
            }
        });
    }

    // Handle mobile search
    if (mobileSearchButton && mobileSearchInput) {
        mobileSearchButton.addEventListener('click', function(e) {
            e.preventDefault();
            performSearch(mobileSearchInput.value);
        });

        if (mobileSearchForm) {
            mobileSearchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                performSearch(mobileSearchInput.value);
            });
        }

        mobileSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value);
            }
        });
    }
}

/**
 * Perform search across the application
 * @param {string} query - Search query
 */
async function performSearch(query) {
    if (!query || query.trim() === '') {
        showAlert('Please enter a search term', 'warning');
        return;
    }

    try {
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

        // Make API call to search endpoint
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Search failed: ${response.statusText}`);
        }

        const results = await response.json();

        // Display search results
        displaySearchResults(query, results);

    } catch (error) {
        console.error('Error performing search:', error);
        showAlert('Search failed: ' + error.message, 'danger');
    }
}

/**
 * Display search results in a modal
 * @param {string} query - Search query
 * @param {Object} results - Search results
 */
function displaySearchResults(query, results) {
    // Create or get search results modal
    let modal = document.getElementById('searchResultsModal');

    if (!modal) {
        // Create modal if it doesn't exist
        modal = document.createElement('div');
        modal.id = 'searchResultsModal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-labelledby', 'searchResultsModalLabel');
        modal.setAttribute('aria-hidden', 'true');

        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="searchResultsModalLabel">Search Results</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="searchResultsBody">
                        <!-- Results will be inserted here -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    // Build results HTML
    const resultsBody = document.getElementById('searchResultsBody');
    let resultsHTML = `<h6 class="mb-3">Results for "${query}"</h6>`;

    const totalResults = (results.events?.length || 0) +
                        (results.templates?.length || 0) +
                        (results.team_members?.length || 0) +
                        (results.conversations?.length || 0);

    if (totalResults === 0) {
        resultsHTML += '<p class="text-muted">No results found.</p>';
    } else {
        // Events results
        if (results.events && results.events.length > 0) {
            resultsHTML += '<h6 class="mt-3 mb-2">Events</h6><ul class="list-group mb-3">';
            results.events.forEach(event => {
                resultsHTML += `
                    <li class="list-group-item">
                        <a href="/saas/events.html?id=${event.id}" class="text-decoration-none">
                            <strong>${event.title}</strong>
                        </a>
                        <p class="mb-0 small text-muted">${event.description || 'No description'}</p>
                        <small class="text-muted">${event.start_date || ''} - ${event.event_type || ''}</small>
                    </li>
                `;
            });
            resultsHTML += '</ul>';
        }

        // Templates results
        if (results.templates && results.templates.length > 0) {
            resultsHTML += '<h6 class="mt-3 mb-2">Templates</h6><ul class="list-group mb-3">';
            results.templates.forEach(template => {
                resultsHTML += `
                    <li class="list-group-item">
                        <a href="/saas/templates.html?id=${template.id}" class="text-decoration-none">
                            <strong>${template.name}</strong>
                        </a>
                        <p class="mb-0 small text-muted">${template.description || 'No description'}</p>
                    </li>
                `;
            });
            resultsHTML += '</ul>';
        }

        // Team members results
        if (results.team_members && results.team_members.length > 0) {
            resultsHTML += '<h6 class="mt-3 mb-2">Team Members</h6><ul class="list-group mb-3">';
            results.team_members.forEach(member => {
                resultsHTML += `
                    <li class="list-group-item">
                        <strong>${member.name || member.email}</strong>
                        <p class="mb-0 small text-muted">${member.email} - ${member.role}</p>
                    </li>
                `;
            });
            resultsHTML += '</ul>';
        }

        // Conversations results
        if (results.conversations && results.conversations.length > 0) {
            resultsHTML += '<h6 class="mt-3 mb-2">Conversations</h6><ul class="list-group mb-3">';
            results.conversations.forEach(conversation => {
                resultsHTML += `
                    <li class="list-group-item">
                        <a href="/saas/clean-chat.html?id=${conversation.id}" class="text-decoration-none">
                            <strong>Conversation ${conversation.id}</strong>
                        </a>
                        <p class="mb-0 small text-muted">${conversation.created_at || ''}</p>
                    </li>
                `;
            });
            resultsHTML += '</ul>';
        }
    }

    resultsBody.innerHTML = resultsHTML;

    // Show the modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Show an alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, info, warning, danger)
 */
function showAlert(message, type = 'info') {
    // Check if showAlert is already defined globally
    if (window.showAlert && typeof window.showAlert === 'function') {
        window.showAlert(message, type);
        return;
    }

    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');

    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Add alert to the page
    const mainContent = document.getElementById('main-content') || document.querySelector('.dashboard-content');
    if (mainContent) {
        mainContent.insertBefore(alertElement, mainContent.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }, 5000);
    }
}

/**
 * Load dashboard charts with real data from API
 */
async function loadDashboardCharts() {
    try {
        // Get auth token and organization ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token) {
            console.error('Not authenticated');
            return;
        }

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        if (orgId) {
            headers['X-Organization-ID'] = orgId;
        }

        // Fetch analytics data from API
        const response = await fetch('/api/agents/analytics', {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            throw new Error('Failed to load analytics data');
        }

        const data = await response.json();

        // Create line chart with conversations by date
        const lineCtx = document.getElementById('eventsLineChart');
        if (lineCtx && data.conversations_by_date) {
            const labels = data.conversations_by_date.map(item => item.date);
            const values = data.conversations_by_date.map(item => item.count);

            new Chart(lineCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Events',
                        data: values,
                        backgroundColor: 'rgba(78, 115, 223, 0.05)',
                        borderColor: 'rgba(78, 115, 223, 1)',
                        pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
                        lineTension: 0.3
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Create pie chart with conversations by agent
        const pieCtx = document.getElementById('eventTypesPieChart');
        if (pieCtx && data.conversations_by_agent) {
            const labels = data.conversations_by_agent.map(item => item.agent_type);
            const values = data.conversations_by_agent.map(item => item.count);

            new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69'],
                        hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#c0392b', '#636466', '#3a3b45'],
                        hoverBorderColor: 'rgba(234, 236, 244, 1)',
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading dashboard charts:', error);
        // Show error message to user
        const lineCtx = document.getElementById('eventsLineChart');
        if (lineCtx) {
            const parent = lineCtx.parentElement;
            parent.innerHTML = '<div class="text-center text-danger p-3">Failed to load chart data</div>';
        }
    }
}
