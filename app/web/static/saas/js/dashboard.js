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
    
    // Load real chart data from analytics API
    if (typeof Chart !== 'undefined') {
        loadDashboardCharts();
    }
});

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
