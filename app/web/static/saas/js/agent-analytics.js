/**
 * Agent Analytics Dashboard JavaScript
 * 
 * This file handles the functionality for the agent analytics dashboard,
 * including data loading, chart rendering, and filter handling.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    const timeChartCtx = document.getElementById('conversationsTimeChart').getContext('2d');
    const agentChartCtx = document.getElementById('conversationsAgentChart').getContext('2d');
    const feedbackDistChartCtx = document.getElementById('feedbackDistributionChart').getContext('2d');
    const agentRatingsChartCtx = document.getElementById('agentRatingsChart').getContext('2d');
    
    // Chart.js configuration for time chart
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
    
    // Chart.js configuration for agent distribution chart
    let agentChart = new Chart(agentChartCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    'rgba(78, 115, 223, 0.8)',  // Primary
                    'rgba(28, 200, 138, 0.8)',  // Success
                    'rgba(54, 185, 204, 0.8)',  // Info
                    'rgba(246, 194, 62, 0.8)',  // Warning
                    'rgba(231, 74, 59, 0.8)',   // Danger
                    'rgba(133, 135, 150, 0.8)', // Secondary
                    'rgba(105, 70, 180, 0.8)',  // Purple
                    'rgba(0, 150, 136, 0.8)'    // Teal
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
    
    // Chart.js configuration for feedback distribution chart
    let feedbackDistChart = new Chart(feedbackDistChartCtx, {
        type: 'bar',
        data: {
            labels: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
            datasets: [{
                label: 'Number of Ratings',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(231, 74, 59, 0.8)',   // 1 star - Red
                    'rgba(246, 194, 62, 0.8)',  // 2 stars - Yellow
                    'rgba(133, 135, 150, 0.8)', // 3 stars - Gray
                    'rgba(54, 185, 204, 0.8)',  // 4 stars - Blue
                    'rgba(28, 200, 138, 0.8)',  // 5 stars - Green
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Chart.js configuration for agent ratings chart
    let agentRatingsChart = new Chart(agentRatingsChartCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Average Rating',
                data: [],
                backgroundColor: 'rgba(78, 115, 223, 0.8)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
    
    // Agent name mapping for display
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
    
    // Load analytics data on page load
    loadAnalyticsData();
    
    // Set up event listeners
    document.getElementById('refreshAnalytics').addEventListener('click', loadAnalyticsData);
    document.getElementById('analyticsFilters').addEventListener('submit', function(e) {
        e.preventDefault();
        loadAnalyticsData();
    });
    
    // Set up export buttons
    document.getElementById('exportCSV').addEventListener('click', exportCSV);
    document.getElementById('exportPDF').addEventListener('click', exportPDF);
    document.getElementById('printReport').addEventListener('click', printReport);
    
    // Set default date values (last 30 days)
    setDefaultDateRange();
    
    /**
     * Load analytics data from the API
     */
    function loadAnalyticsData() {
        // Show loading state
        showLoading();
        
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
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update dashboard with data
            updateDashboard(data);
        })
        .catch(error => {
            console.error('Error loading analytics data:', error);
            showError('Failed to load analytics data. Please try again.');
            
            // Hide loading state
            hideLoading();
        });
    }
    
    /**
     * Update the dashboard with analytics data
     * @param {Object} data - Analytics data from the API
     */
    function updateDashboard(data) {
        // Update overview metrics
        document.getElementById('totalConversations').textContent = data.total_conversations || 0;
        
        // Calculate total messages
        let totalMessages = 0;
        if (data.messages_by_agent) {
            data.messages_by_agent.forEach(item => {
                totalMessages += item.count;
            });
        }
        document.getElementById('totalMessages').textContent = totalMessages;
        
        // Calculate average messages per conversation
        const avgMessages = data.total_conversations > 0 ? Math.round(totalMessages / data.total_conversations) : 0;
        document.getElementById('avgMessages').textContent = avgMessages;
        
        // Update feedback metrics
        if (data.feedback) {
            document.getElementById('avgRating').textContent = data.feedback.average_rating || '0.0';
            document.getElementById('totalFeedback').textContent = data.feedback.total_count || 0;
            
            // Update feedback distribution chart
            updateFeedbackDistributionChart(data.feedback);
            
            // Update agent ratings chart
            updateAgentRatingsChart(data.feedback);
            
            // Update feedback table
            updateFeedbackTable(data.feedback);
        } else {
            document.getElementById('avgRating').textContent = '0.0';
            document.getElementById('totalFeedback').textContent = '0';
        }
        
        // Update time chart
        updateTimeChart(data);
        
        // Update agent chart
        updateAgentChart(data);
        
        // Update agent usage table
        updateAgentTable(data);
        
        // Update usage trends
        updateUsageTrends(data);
        
        // Hide loading state
        hideLoading();
    }
    
    /**
     * Update the feedback distribution chart with analytics data
     * @param {Object} feedback - Feedback data from the API
     */
    function updateFeedbackDistributionChart(feedback) {
        if (!feedback || !feedback.distribution || feedback.distribution.length === 0) {
            // No data available
            feedbackDistChart.data.datasets[0].data = [0, 0, 0, 0, 0];
            feedbackDistChart.update();
            return;
        }
        
        // Initialize data array with zeros
        const ratingCounts = [0, 0, 0, 0, 0];
        
        // Fill in the data from the feedback distribution
        feedback.distribution.forEach(item => {
            if (item.rating >= 1 && item.rating <= 5) {
                ratingCounts[item.rating - 1] = item.count;
            }
        });
        
        // Update chart
        feedbackDistChart.data.datasets[0].data = ratingCounts;
        feedbackDistChart.update();
    }
    
    /**
     * Update the agent ratings chart with analytics data
     * @param {Object} feedback - Feedback data from the API
     */
    function updateAgentRatingsChart(feedback) {
        if (!feedback || !feedback.by_agent || feedback.by_agent.length === 0) {
            // No data available
            agentRatingsChart.data.labels = [];
            agentRatingsChart.data.datasets[0].data = [];
            agentRatingsChart.update();
            return;
        }
        
        // Format agent names for display
        const agentLabels = feedback.by_agent.map(item => {
            return agentNames[item.agent_type] || item.agent_type;
        });
        
        const ratingData = feedback.by_agent.map(item => item.average_rating);
        
        // Update chart
        agentRatingsChart.data.labels = agentLabels;
        agentRatingsChart.data.datasets[0].data = ratingData;
        agentRatingsChart.update();
    }
    
    /**
     * Update the feedback table with analytics data
     * @param {Object} feedback - Feedback data from the API
     */
    function updateFeedbackTable(feedback) {
        const tableBody = document.querySelector('#feedbackTable tbody');
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        if (!feedback || !feedback.by_agent || feedback.by_agent.length === 0) {
            // No data available
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="4" class="text-center">No feedback data available</td>';
            tableBody.appendChild(row);
            return;
        }
        
        // Add a row for each agent
        feedback.by_agent.forEach(item => {
            const agentType = item.agent_type;
            const totalRatings = item.count;
            const avgRating = item.average_rating;
            
            // Create rating distribution visualization
            let distributionHtml = '<div class="d-flex align-items-center">';
            
            // Add stars for each rating
            for (let i = 1; i <= 5; i++) {
                const ratingCount = item.ratings_distribution.find(r => r.rating === i)?.count || 0;
                const percentage = totalRatings > 0 ? Math.round((ratingCount / totalRatings) * 100) : 0;
                
                distributionHtml += `
                    <div class="me-2" title="${i} stars: ${ratingCount} ratings (${percentage}%)">
                        <div class="text-center small">${i}★</div>
                        <div class="progress" style="height: 8px; width: 30px;">
                            <div class="progress-bar bg-${i <= 2 ? 'danger' : i === 3 ? 'warning' : 'success'}" 
                                role="progressbar" style="width: ${percentage}%" 
                                aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <div class="text-center x-small">${percentage}%</div>
                    </div>
                `;
            }
            
            distributionHtml += '</div>';
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${agentNames[agentType] || agentType}</td>
                <td>${totalRatings}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="me-2">${avgRating}</div>
                        <div class="rating-stars">
                            ${getRatingStars(avgRating)}
                        </div>
                    </div>
                </td>
                <td>${distributionHtml}</td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    /**
     * Get HTML for rating stars
     * @param {number} rating - Rating value (0-5)
     * @returns {string} HTML for rating stars
     */
    function getRatingStars(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        let starsHtml = '';
        
        // Add full stars
        for (let i = 0; i < fullStars; i++) {
            starsHtml += '<i class="bi bi-star-fill text-warning"></i>';
        }
        
        // Add half star if needed
        if (halfStar) {
            starsHtml += '<i class="bi bi-star-half text-warning"></i>';
        }
        
        // Add empty stars
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += '<i class="bi bi-star text-warning"></i>';
        }
        
        return starsHtml;
    }
    
    /**
     * Update the time chart with analytics data
     * @param {Object} data - Analytics data from the API
     */
    function updateTimeChart(data) {
        if (!data.conversations_by_date || data.conversations_by_date.length === 0) {
            // No data available
            timeChart.data.labels = [];
            timeChart.data.datasets[0].data = [];
            timeChart.update();
            return;
        }
        
        // Sort dates chronologically
        const sortedData = [...data.conversations_by_date].sort((a, b) => {
            return new Date(a.date) - new Date(b.date);
        });
        
        // Format dates for display
        const timeLabels = sortedData.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString();
        });
        
        const timeData = sortedData.map(item => item.count);
        
        // Update chart
        timeChart.data.labels = timeLabels;
        timeChart.data.datasets[0].data = timeData;
        timeChart.update();
    }
    
    /**
     * Update the agent distribution chart with analytics data
     * @param {Object} data - Analytics data from the API
     */
    function updateAgentChart(data) {
        if (!data.conversations_by_agent || data.conversations_by_agent.length === 0) {
            // No data available
            agentChart.data.labels = [];
            agentChart.data.datasets[0].data = [];
            agentChart.update();
            return;
        }
        
        // Format agent names for display
        const agentLabels = data.conversations_by_agent.map(item => {
            return agentNames[item.agent_type] || item.agent_type;
        });
        
        const agentData = data.conversations_by_agent.map(item => item.count);
        
        // Update chart
        agentChart.data.labels = agentLabels;
        agentChart.data.datasets[0].data = agentData;
        agentChart.update();
    }
    
    /**
     * Update the agent usage table with analytics data
     * @param {Object} data - Analytics data from the API
     */
    function updateAgentTable(data) {
        const tableBody = document.querySelector('#agentUsageTable tbody');
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        if (!data.conversations_by_agent || data.conversations_by_agent.length === 0) {
            // No data available
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="5" class="text-center">No data available</td>';
            tableBody.appendChild(row);
            return;
        }
        
        // Create a map of agent types to message counts
        const messagesByAgentMap = {};
        if (data.messages_by_agent) {
            data.messages_by_agent.forEach(item => {
                messagesByAgentMap[item.agent_type] = item.count;
            });
        }
        
        // Calculate total conversations for percentage
        const totalConversations = data.total_conversations || 0;
        
        // Add a row for each agent
        data.conversations_by_agent.forEach(item => {
            const agentType = item.agent_type;
            const conversations = item.count;
            const messages = messagesByAgentMap[agentType] || 0;
            const avgMessages = conversations > 0 ? Math.round(messages / conversations) : 0;
            const usagePercent = totalConversations > 0 ? Math.round((conversations / totalConversations) * 100) : 0;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${agentNames[agentType] || agentType}</td>
                <td>${conversations}</td>
                <td>${messages}</td>
                <td>${avgMessages}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <span class="me-2">${usagePercent}%</span>
                        <div class="progress" style="height: 8px; width: 100px;">
                            <div class="progress-bar" role="progressbar" style="width: ${usagePercent}%" 
                                aria-valuenow="${usagePercent}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    /**
     * Update the usage trends section with analytics data
     * @param {Object} data - Analytics data from the API
     */
    function updateUsageTrends(data) {
        // Fetch usage limits from the subscription API
        const organizationId = localStorage.getItem('organizationId') || '1';

        fetch(`/api/subscription/organizations/${organizationId}/usage-limits`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(limits => {
            // Get limits from API response
            const conversationsLimit = limits.max_conversations === -1 ? '∞' : limits.max_conversations;
            const messagesLimit = limits.max_messages === -1 ? '∞' : limits.max_messages;

            // Get current month's usage
            const currentDate = new Date();
            const currentMonth = currentDate.getMonth();
            const currentYear = currentDate.getFullYear();

            // Filter conversations for current month
            let currentMonthConversations = 0;
            let currentMonthMessages = 0;

            if (data.conversations_by_date) {
                data.conversations_by_date.forEach(item => {
                    const date = new Date(item.date);
                    if (date.getMonth() === currentMonth && date.getFullYear() === currentYear) {
                        currentMonthConversations += item.count;
                    }
                });
            }

            // Assume messages are proportional to conversations for this example
            // In a real implementation, you would filter messages by date as well
            if (data.total_conversations > 0 && data.messages_by_agent) {
                let totalMessages = 0;
                data.messages_by_agent.forEach(item => {
                    totalMessages += item.count;
                });

                currentMonthMessages = Math.round((currentMonthConversations / data.total_conversations) * totalMessages);
            }

            // Update usage displays
            document.getElementById('conversationsQuota').textContent = `${currentMonthConversations}/${conversationsLimit}`;
            document.getElementById('messagesQuota').textContent = `${currentMonthMessages}/${messagesLimit}`;

            // Update progress bars (handle unlimited case)
            const conversationsPercent = conversationsLimit === '∞'
                ? 0
                : Math.min(Math.round((currentMonthConversations / conversationsLimit) * 100), 100);

            const messagesPercent = messagesLimit === '∞'
                ? 0
                : Math.min(Math.round((currentMonthMessages / messagesLimit) * 100), 100);

            const conversationsProgress = document.getElementById('conversationsProgress');
            conversationsProgress.style.width = `${conversationsPercent}%`;
            conversationsProgress.setAttribute('aria-valuenow', conversationsPercent);
            conversationsProgress.setAttribute('aria-label', `${conversationsPercent} percent of conversation quota used`);

            const messagesProgress = document.getElementById('messagesProgress');
            messagesProgress.style.width = `${messagesPercent}%`;
            messagesProgress.setAttribute('aria-valuenow', messagesPercent);
            messagesProgress.setAttribute('aria-label', `${messagesPercent} percent of message quota used`);
        })
        .catch(error => {
            console.error('Error fetching usage limits:', error);
            // Fallback to displaying current usage without limits
            document.getElementById('conversationsQuota').textContent = 'N/A';
            document.getElementById('messagesQuota').textContent = 'N/A';
        });
    }
    
    /**
     * Set default date range (last 30 days)
     */
    function setDefaultDateRange() {
        const today = new Date();
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(today.getDate() - 30);
        
        // Format dates as YYYY-MM-DD
        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        
        document.getElementById('startDate').value = formatDate(thirtyDaysAgo);
        document.getElementById('endDate').value = formatDate(today);
    }
    
    /**
     * Show loading state
     */
    function showLoading() {
        // Add loading indicators if needed
        document.getElementById('totalConversations').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        document.getElementById('totalMessages').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        document.getElementById('avgMessages').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        document.getElementById('mostUsedAgent').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }
    
    /**
     * Hide loading state
     */
    function hideLoading() {
        // Remove loading indicators if needed
    }
    
    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        // Create alert element
        const alertElement = document.createElement('div');
        alertElement.className = 'alert alert-danger alert-dismissible fade show';
        alertElement.setAttribute('role', 'alert');
        alertElement.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the main content
        const mainContent = document.getElementById('main-content');
        mainContent.insertBefore(alertElement, mainContent.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }, 5000);
    }
    
    /**
     * Export analytics data as CSV
     */
    function exportCSV() {
        // Get filter values for filename
        const startDate = document.getElementById('startDate').value || 'all';
        const endDate = document.getElementById('endDate').value || 'all';
        const agentType = document.getElementById('agentType').value || 'all-agents';
        
        // Create filename
        const filename = `agent-analytics-${agentType}-${startDate}-to-${endDate}.csv`;
        
        // Get table data
        const table = document.getElementById('agentUsageTable');
        let csvContent = "data:text/csv;charset=utf-8,";
        
        // Add headers
        const headers = [];
        table.querySelectorAll('thead th').forEach(th => {
            headers.push(th.textContent);
        });
        csvContent += headers.join(',') + '\r\n';
        
        // Add rows
        table.querySelectorAll('tbody tr').forEach(tr => {
            const row = [];
            tr.querySelectorAll('td').forEach((td, index) => {
                // For the last column (Usage %), extract just the percentage number
                if (index === 4) {
                    const percentText = td.textContent.trim();
                    const percentMatch = percentText.match(/(\d+)%/);
                    row.push(percentMatch ? percentMatch[1] : '0');
                } else {
                    row.push(td.textContent);
                }
            });
            csvContent += row.join(',') + '\r\n';
        });
        
        // Create download link
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        
        // Trigger download
        link.click();
        
        // Clean up
        document.body.removeChild(link);
    }
    
    /**
     * Export analytics data as PDF
     */
    function exportPDF() {
        // Alert user that this feature is not implemented
        alert('PDF export functionality will be implemented in a future update.');
    }
    
    /**
     * Print analytics report
     */
    function printReport() {
        window.print();
    }
});
