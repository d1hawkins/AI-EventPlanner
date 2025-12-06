/**
 * Team JavaScript
 * Handles functionality for the team management pages in the AI Event Planner SaaS application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the team page
    const isTeamPage = window.location.pathname.endsWith('/team.html');
    // Check if we're on the team invite page
    const isTeamInvitePage = window.location.pathname.endsWith('/team-invite.html');
    
    if (isTeamPage) {
        initializeTeamPage();
    } else if (isTeamInvitePage) {
        initializeTeamInvitePage();
    }
    
    // Initialize sidebar toggle functionality
    initializeSidebar();
});

/**
 * Initialize the team page functionality
 */
function initializeTeamPage() {
    // Initialize refresh button
    const refreshButton = document.getElementById('refreshTeam');
    if (refreshButton) {
        refreshButton.addEventListener('click', function(event) {
            event.preventDefault();
            loadTeamMembers();
        });
    }
    
    // Initialize view options
    const viewOptions = {
        viewAll: document.getElementById('viewAll'),
        viewActive: document.getElementById('viewActive'),
        viewAdmins: document.getElementById('viewAdmins'),
        exportTeam: document.getElementById('exportTeam')
    };
    
    if (viewOptions.viewAll) {
        viewOptions.viewAll.addEventListener('click', function(event) {
            event.preventDefault();
            filterTeamMembers('all');
        });
    }
    
    if (viewOptions.viewActive) {
        viewOptions.viewActive.addEventListener('click', function(event) {
            event.preventDefault();
            filterTeamMembers('active');
        });
    }
    
    if (viewOptions.viewAdmins) {
        viewOptions.viewAdmins.addEventListener('click', function(event) {
            event.preventDefault();
            filterTeamMembers('admin');
        });
    }
    
    if (viewOptions.exportTeam) {
        viewOptions.exportTeam.addEventListener('click', function(event) {
            event.preventDefault();
            exportTeamList();
        });
    }
    
    // Initialize edit member buttons
    initializeEditMemberButtons();
    
    // Initialize remove member buttons
    initializeRemoveMemberButtons();
    
    // Load team members
    loadTeamMembers();
}

/**
 * Initialize the team invite page functionality
 */
function initializeTeamInvitePage() {
    // Initialize invite form
    const inviteForm = document.getElementById('inviteForm');
    if (inviteForm) {
        inviteForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            if (!inviteForm.checkValidity()) {
                event.stopPropagation();
                inviteForm.classList.add('was-validated');
                return;
            }
            
            sendInvitations();
        });
    }
    
    // Initialize bulk import form
    const bulkImportForm = document.getElementById('bulkImportForm');
    if (bulkImportForm) {
        bulkImportForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            if (!bulkImportForm.checkValidity()) {
                event.stopPropagation();
                bulkImportForm.classList.add('was-validated');
                return;
            }
            
            importTeamMembers();
        });
    }
    
    // Initialize download template button
    const downloadTemplateButton = document.getElementById('downloadTemplate');
    if (downloadTemplateButton) {
        downloadTemplateButton.addEventListener('click', function(event) {
            event.preventDefault();
            downloadCSVTemplate();
        });
    }
    
    // Initialize refresh invitations button
    const refreshInvitationsButton = document.getElementById('refreshInvitations');
    if (refreshInvitationsButton) {
        refreshInvitationsButton.addEventListener('click', function(event) {
            event.preventDefault();
            loadPendingInvitations();
        });
    }
    
    // Load pending invitations
    loadPendingInvitations();
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
 * Load team members
 */
async function loadTeamMembers() {
    const teamTable = document.getElementById('teamTableBody');
    if (!teamTable) return;

    teamTable.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';

    try {
        // Get auth token and organization ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token) {
            throw new Error('Not authenticated');
        }

        if (!orgId) {
            throw new Error('Organization ID not found');
        }

        // Make API call to get organization details (which includes team members)
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        if (orgId) {
            headers['X-Organization-ID'] = orgId;
        }

        const response = await fetch(`/api/subscription/organizations/${orgId}`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            throw new Error(`Failed to load team members: ${response.statusText}`);
        }

        const data = await response.json();

        // Transform organization data to member format
        // Note: This is a placeholder. In a real app, you'd have a specific endpoint for members
        const members = [];

        // For now, show a message that team management is being loaded from the backend
        if (!members.length) {
            teamTable.innerHTML = '<tr><td colspan="6" class="text-center">No team members found. Use the "Invite Member" button to add team members.</td></tr>';
            return;
        }

        // Render members
        renderTeamMembers(members);

        // Initialize edit member buttons
        initializeEditMemberButtons();

        // Initialize remove member buttons
        initializeRemoveMemberButtons();
    } catch (error) {
        console.error('Error loading team members:', error);
        teamTable.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error loading team members: ${error.message}</td></tr>`;
    }
}

/**
 * Render team members in the table
 * @param {Array} members - Array of member objects
 */
function renderTeamMembers(members) {
    const teamTable = document.getElementById('teamTableBody');
    if (!teamTable) return;
    
    if (members.length === 0) {
        teamTable.innerHTML = '<tr><td colspan="6" class="text-center">No team members found</td></tr>';
        return;
    }
    
    let html = '';
    
    members.forEach(member => {
        // Get role badge class
        let roleBadgeClass = getRoleBadgeClass(member.role);
        
        // Get status badge class
        let statusBadgeClass = getStatusBadgeClass(member.status);
        
        // Determine icon based on status
        let icon = member.status === 'invited' ? 'bi-envelope' : 'bi-person-circle';
        
        // Determine actions based on role and status
        let actions = '';
        
        if (member.isCurrentUser) {
            // Current user can only edit themselves, not remove
            actions = `
                <div class="btn-group" role="group" aria-label="Member actions">
                    <button type="button" class="btn btn-primary btn-sm edit-member" data-member-id="${member.id}" aria-label="Edit ${member.name}">
                        <i class="bi bi-pencil" aria-hidden="true"></i>
                    </button>
                </div>
            `;
        } else if (member.status === 'invited') {
            // Invited members can be resent invitations or have invitations canceled
            actions = `
                <div class="btn-group" role="group" aria-label="Member actions">
                    <button type="button" class="btn btn-info btn-sm resend-invitation" data-member-id="${member.id}" aria-label="Resend invitation to ${member.name}">
                        <i class="bi bi-envelope" aria-hidden="true"></i>
                    </button>
                    <button type="button" class="btn btn-danger btn-sm cancel-invitation" data-member-id="${member.id}" data-member-name="${member.name}" aria-label="Cancel invitation to ${member.name}">
                        <i class="bi bi-x-circle" aria-hidden="true"></i>
                    </button>
                </div>
            `;
        } else {
            // Active members can be edited or removed
            actions = `
                <div class="btn-group" role="group" aria-label="Member actions">
                    <button type="button" class="btn btn-primary btn-sm edit-member" data-member-id="${member.id}" aria-label="Edit ${member.name}">
                        <i class="bi bi-pencil" aria-hidden="true"></i>
                    </button>
                    <button type="button" class="btn btn-danger btn-sm remove-member" data-member-id="${member.id}" data-member-name="${member.name}" aria-label="Remove ${member.name}">
                        <i class="bi bi-trash" aria-hidden="true"></i>
                    </button>
                </div>
            `;
        }
        
        html += `
            <tr data-member-id="${member.id}" data-member-role="${member.role}" data-member-status="${member.status}">
                <td class="d-flex align-items-center">
                    <i class="bi ${icon} me-2" style="font-size: 24px;" aria-hidden="true"></i>
                    <div>
                        <div>${member.name}</div>
                        ${member.isCurrentUser ? '<div class="small text-muted">You</div>' : ''}
                    </div>
                </td>
                <td>${member.email}</td>
                <td><span class="badge ${roleBadgeClass}">${capitalizeFirstLetter(member.role)}</span></td>
                <td><span class="badge ${statusBadgeClass}">${capitalizeFirstLetter(member.status)}</span></td>
                <td>${member.lastActive}</td>
                <td>${actions}</td>
            </tr>
        `;
    });
    
    teamTable.innerHTML = html;
}

/**
 * Filter team members
 * @param {string} filter - Filter type (all, active, admin)
 */
function filterTeamMembers(filter) {
    const rows = document.querySelectorAll('#teamTableBody tr');
    
    rows.forEach(row => {
        const role = row.getAttribute('data-member-role');
        const status = row.getAttribute('data-member-status');
        
        if (filter === 'all') {
            row.style.display = '';
        } else if (filter === 'active') {
            row.style.display = status === 'active' ? '' : 'none';
        } else if (filter === 'admin') {
            row.style.display = (role === 'admin' || role === 'owner') ? '' : 'none';
        }
    });
    
    // Show message if no results
    const visibleRows = document.querySelectorAll('#teamTableBody tr[style=""]');
    if (visibleRows.length === 0) {
        const teamTable = document.getElementById('teamTableBody');
        teamTable.innerHTML = `<tr><td colspan="6" class="text-center">No team members found matching the filter "${filter}"</td></tr>`;
    }
}

/**
 * Initialize edit member buttons
 */
function initializeEditMemberButtons() {
    const editButtons = document.querySelectorAll('.edit-member');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            openEditMemberModal(memberId);
        });
    });
    
    // Initialize save member changes button
    const saveMemberChangesButton = document.getElementById('saveMemberChanges');
    if (saveMemberChangesButton) {
        saveMemberChangesButton.addEventListener('click', function() {
            saveMemberChanges();
        });
    }
}

/**
 * Open edit member modal
 * @param {string} memberId - Member ID
 */
function openEditMemberModal(memberId) {
    // In a real application, this would fetch the member data from the API
    // For now, we'll just use the data from the table
    
    const row = document.querySelector(`tr[data-member-id="${memberId}"]`);
    if (!row) return;
    
    const name = row.querySelector('td:first-child div div:first-child').textContent;
    const email = row.querySelector('td:nth-child(2)').textContent;
    const role = row.getAttribute('data-member-role');
    
    // Set form values
    document.getElementById('editMemberId').value = memberId;
    document.getElementById('editMemberName').value = name;
    document.getElementById('editMemberEmail').value = email;
    document.getElementById('editMemberRole').value = role;
    
    // Show modal
    const editModal = new bootstrap.Modal(document.getElementById('editMemberModal'));
    editModal.show();
}

/**
 * Save member changes
 */
async function saveMemberChanges() {
    try {
        // Get form values
        const memberId = document.getElementById('editMemberId').value;
        const name = document.getElementById('editMemberName').value;
        const email = document.getElementById('editMemberEmail').value;
        const role = document.getElementById('editMemberRole').value;

        // Validate input
        if (!name || !email || !role) {
            showAlert('All fields are required', 'warning');
            return;
        }

        // Get auth token and organization ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            showAlert('Authentication required. Please log in again.', 'danger');
            return;
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Make API call to update member
        const response = await fetch(`/api/subscription/organizations/${orgId}/members/${memberId}`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify({
                name: name,
                email: email,
                role: role
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to update member: ${response.statusText}`);
        }

        // Update the table row with new data
        const row = document.querySelector(`tr[data-member-id="${memberId}"]`);
        if (row) {
            // Update row data
            row.setAttribute('data-member-role', role);

            // Update name
            row.querySelector('td:first-child div div:first-child').textContent = name;

            // Update email
            row.querySelector('td:nth-child(2)').textContent = email;

            // Update role
            const roleBadge = row.querySelector('td:nth-child(3) span');
            roleBadge.className = `badge ${getRoleBadgeClass(role)}`;
            roleBadge.textContent = capitalizeFirstLetter(role);
        }

        // Close modal
        const editModal = bootstrap.Modal.getInstance(document.getElementById('editMemberModal'));
        editModal.hide();

        // Show success message
        showAlert('Team member updated successfully', 'success');

    } catch (error) {
        console.error('Error updating team member:', error);
        showAlert('Failed to update team member: ' + error.message, 'danger');
    }
}

/**
 * Initialize remove member buttons
 */
function initializeRemoveMemberButtons() {
    const removeButtons = document.querySelectorAll('.remove-member');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            const memberName = this.getAttribute('data-member-name');
            
            // Set the member name in the modal
            document.getElementById('removeMemberName').textContent = memberName;
            
            // Store the member ID for the confirm button
            document.getElementById('confirmRemoveMember').setAttribute('data-member-id', memberId);
            
            // Show the modal
            const removeModal = new bootstrap.Modal(document.getElementById('removeMemberModal'));
            removeModal.show();
        });
    });
    
    // Initialize confirm remove button
    const confirmRemoveButton = document.getElementById('confirmRemoveMember');
    if (confirmRemoveButton) {
        confirmRemoveButton.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            removeMember(memberId);
            
            // Hide the modal
            const removeModal = bootstrap.Modal.getInstance(document.getElementById('removeMemberModal'));
            removeModal.hide();
        });
    }
    
    // Initialize cancel invitation buttons
    const cancelButtons = document.querySelectorAll('.cancel-invitation');
    
    cancelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            const memberName = this.getAttribute('data-member-name');
            
            if (confirm(`Are you sure you want to cancel the invitation for ${memberName}?`)) {
                removeMember(memberId);
            }
        });
    });
    
    // Initialize resend invitation buttons
    const resendButtons = document.querySelectorAll('.resend-invitation');
    
    resendButtons.forEach(button => {
        button.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            resendInvitation(memberId);
        });
    });
}

/**
 * Remove a member
 * @param {string} memberId - Member ID
 */
async function removeMember(memberId) {
    try {
        // Get auth token and organization ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            showAlert('Authentication required. Please log in again.', 'danger');
            return;
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'X-Organization-ID': orgId
        };

        // Make API call to remove member
        const response = await fetch(`/api/subscription/organizations/${orgId}/members/${memberId}`, {
            method: 'DELETE',
            headers: headers
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to remove member: ${response.statusText}`);
        }

        // Remove the row from the table
        const row = document.querySelector(`tr[data-member-id="${memberId}"]`);
        if (row) {
            row.remove();
        }

        // Show success message
        showAlert('Team member removed successfully', 'success');

        // Update team size
        updateTeamSize();

    } catch (error) {
        console.error('Error removing team member:', error);
        showAlert('Failed to remove team member: ' + error.message, 'danger');
    }
}

/**
 * Resend invitation
 * @param {string} memberId - Member ID
 */
function resendInvitation(memberId) {
    // In a real application, this would make an API call to resend the invitation
    // For now, we'll just show a success message
    
    // Show success message
    showAlert('Invitation resent successfully', 'success');
}

/**
 * Update team size
 */
function updateTeamSize() {
    // In a real application, this would be updated based on the API response
    // For now, we'll just count the rows in the table
    
    const rows = document.querySelectorAll('#teamTableBody tr');
    const teamSizeElement = document.querySelector('.card-body .h5');
    
    if (teamSizeElement) {
        const availableSeats = 10; // This would come from the subscription plan
        const teamSize = rows.length;
        
        teamSizeElement.textContent = `${teamSize} / ${availableSeats}`;
        
        // Update available seats
        const availableSeatsElement = document.querySelector('.card-body .small.text-muted');
        if (availableSeatsElement) {
            availableSeatsElement.textContent = `${availableSeats - teamSize} available seats`;
        }
    }
}

/**
 * Export team list
 */
function exportTeamList() {
    try {
        // Get all team member rows from the table
        const rows = document.querySelectorAll('#teamTableBody tr');

        if (rows.length === 0) {
            showAlert('No team members to export', 'warning');
            return;
        }

        // Create CSV content with headers
        let csvContent = 'Name,Email,Role,Status\n';

        // Add each team member to CSV
        rows.forEach(row => {
            const name = row.querySelector('td:first-child div div:first-child')?.textContent.trim() || '';
            const email = row.querySelector('td:nth-child(2)')?.textContent.trim() || '';
            const role = row.querySelector('td:nth-child(3) span')?.textContent.trim() || '';
            const status = row.querySelector('td:nth-child(4) span')?.textContent.trim() || '';

            // Escape commas and quotes in data
            const escapeCsv = (str) => {
                if (str.includes(',') || str.includes('"') || str.includes('\n')) {
                    return `"${str.replace(/"/g, '""')}"`;
                }
                return str;
            };

            csvContent += `${escapeCsv(name)},${escapeCsv(email)},${escapeCsv(role)},${escapeCsv(status)}\n`;
        });

        // Create a blob from the CSV content
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

        // Create a link element and trigger download
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            const timestamp = new Date().toISOString().slice(0, 10);
            link.setAttribute('href', url);
            link.setAttribute('download', `team_members_${timestamp}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }

        showAlert('Team list exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting team list:', error);
        showAlert('Failed to export team list: ' + error.message, 'danger');
    }
}

/**
 * Send invitations
 */
async function sendInvitations() {
    try {
        // Get form values
        const emailsText = document.getElementById('inviteEmails').value;
        const role = document.getElementById('inviteRole').value;
        const message = document.getElementById('inviteMessage').value;
        const sendCopy = document.getElementById('sendCopy').checked;

        // Parse emails (one per line)
        const emails = emailsText.split('\n')
            .map(email => email.trim())
            .filter(email => email.length > 0);

        if (emails.length === 0) {
            throw new Error('Please enter at least one email address');
        }

        // Get auth token and organization ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token) {
            throw new Error('Not authenticated');
        }

        if (!orgId) {
            throw new Error('Organization ID not found');
        }

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Send invitation for each email
        const invitationPromises = emails.map(email =>
            fetch(`/api/subscription/organizations/${orgId}/members/invite`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    email: email,
                    role: role,
                    message: message
                })
            })
        );

        const responses = await Promise.all(invitationPromises);

        // Check for failures
        const failures = [];
        for (let i = 0; i < responses.length; i++) {
            if (!responses[i].ok) {
                failures.push(emails[i]);
            }
        }

        if (failures.length > 0) {
            throw new Error(`Failed to send invitations to: ${failures.join(', ')}`);
        }

        // Show success message
        showAlert(`Successfully sent ${emails.length} invitation(s)!`, 'success');

        // Reset form
        document.getElementById('inviteForm').reset();
        document.getElementById('inviteForm').classList.remove('was-validated');

        // Reload pending invitations
        loadPendingInvitations();
    } catch (error) {
        console.error('Error sending invitations:', error);
        showAlert('Failed to send invitations: ' + error.message, 'danger');
    }
}

/**
 * Import team members
 */
async function importTeamMembers() {
    try {
        // Get form values
        const csvFile = document.getElementById('csvFile').files[0];

        if (!csvFile) {
            throw new Error('Please select a CSV file');
        }

        // Get auth token and organization ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            showAlert('Authentication required. Please log in again.', 'danger');
            return;
        }

        // Read the CSV file
        const text = await csvFile.text();
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        if (lines.length < 2) {
            throw new Error('CSV file must contain headers and at least one data row');
        }

        // Parse CSV headers
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const emailIndex = headers.indexOf('email');
        const nameIndex = headers.indexOf('name');
        const roleIndex = headers.indexOf('role');

        if (emailIndex === -1) {
            throw new Error('CSV file must contain an "email" column');
        }

        // Parse CSV data rows
        const members = [];
        const errors = [];

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());

            if (values.length === 0 || values[0] === '') {
                continue; // Skip empty lines
            }

            const email = values[emailIndex] || '';
            const name = nameIndex !== -1 ? values[nameIndex] : '';
            const role = roleIndex !== -1 ? values[roleIndex] : 'member';

            if (!email) {
                errors.push(`Row ${i + 1}: Missing email address`);
                continue;
            }

            members.push({ email, name, role });
        }

        if (members.length === 0) {
            throw new Error('No valid members found in CSV file. ' + (errors.length > 0 ? errors.join('; ') : ''));
        }

        // Prepare headers for API calls
        const apiHeaders = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Send invitations for each member
        const invitationPromises = members.map(member =>
            fetch(`/api/subscription/organizations/${orgId}/members/invite`, {
                method: 'POST',
                headers: apiHeaders,
                body: JSON.stringify({
                    email: member.email,
                    role: member.role,
                    message: `You have been invited to join our team${member.name ? ' as ' + member.name : ''}`
                })
            })
        );

        const responses = await Promise.all(invitationPromises);

        // Check for failures
        const failures = [];
        for (let i = 0; i < responses.length; i++) {
            if (!responses[i].ok) {
                failures.push(members[i].email);
            }
        }

        // Show appropriate message
        if (failures.length === 0) {
            showAlert(`Successfully sent ${members.length} invitation(s)!`, 'success');
        } else if (failures.length < members.length) {
            showAlert(`Sent ${members.length - failures.length} invitation(s). Failed: ${failures.join(', ')}`, 'warning');
        } else {
            throw new Error(`Failed to send invitations to: ${failures.join(', ')}`);
        }

        // Reset form
        document.getElementById('bulkImportForm').reset();
        document.getElementById('bulkImportForm').classList.remove('was-validated');

        // Close modal
        const importModal = bootstrap.Modal.getInstance(document.getElementById('bulkImportModal'));
        if (importModal) {
            importModal.hide();
        }

        // Reload pending invitations
        loadPendingInvitations();

    } catch (error) {
        console.error('Error importing team members:', error);
        showAlert('Failed to import team members: ' + error.message, 'danger');
    }
}

/**
 * Download CSV template
 */
function downloadCSVTemplate() {
    try {
        // Create CSV content with headers
        const csvContent = 'email,name,role\n' +
                          'john@example.com,John Smith,member\n' +
                          'jane@example.com,Jane Doe,admin\n' +
                          'bob@example.com,Bob Johnson,member\n';

        // Create a blob from the CSV content
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

        // Create a link element and trigger download
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', 'team_invite_template.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }

        showAlert('CSV template downloaded successfully', 'success');
    } catch (error) {
        console.error('Error downloading CSV template:', error);
        showAlert('Failed to download CSV template: ' + error.message, 'danger');
    }
}

/**
 * Load pending invitations
 */
async function loadPendingInvitations() {
    const invitationsTable = document.getElementById('invitationsTableBody');
    if (!invitationsTable) return;

    invitationsTable.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';

    try {
        // For now, show empty state as the backend doesn't have a dedicated invitations endpoint yet
        // In a future implementation, you would call GET /api/subscription/organizations/{orgId}/invitations
        const invitations = [];

        // Render invitations
        renderPendingInvitations(invitations);
    } catch (error) {
        console.error('Error loading invitations:', error);
        invitationsTable.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error loading invitations: ${error.message}</td></tr>`;
    }
}

/**
 * Render pending invitations in the table
 * @param {Array} invitations - Array of invitation objects
 */
function renderPendingInvitations(invitations) {
    const invitationsTable = document.getElementById('invitationsTableBody');
    if (!invitationsTable) return;
    
    if (invitations.length === 0) {
        invitationsTable.innerHTML = '<tr><td colspan="6" class="text-center">No pending invitations</td></tr>';
        return;
    }
    
    let html = '';
    
    invitations.forEach(invitation => {
        // Get role badge class
        let roleBadgeClass = getRoleBadgeClass(invitation.role);
        
        // Get status badge class
        let statusBadgeClass = getStatusBadgeClass(invitation.status);
        
        html += `
            <tr data-invitation-id="${invitation.id}">
                <td>${invitation.email}</td>
                <td><span class="badge ${roleBadgeClass}">${capitalizeFirstLetter(invitation.role)}</span></td>
                <td>${invitation.invitedBy}</td>
                <td>${invitation.dateSent}</td>
                <td><span class="badge ${statusBadgeClass}">${capitalizeFirstLetter(invitation.status)}</span></td>
                <td>
                    <div class="btn-group" role="group" aria-label="Invitation actions">
                        <button type="button" class="btn btn-info btn-sm resend-invitation" data-invitation-id="${invitation.id}" aria-label="Resend invitation to ${invitation.email}">
                            <i class="bi bi-envelope" aria-hidden="true"></i>
                        </button>
                        <button type="button" class="btn btn-danger btn-sm cancel-invitation" data-invitation-id="${invitation.id}" data-invitation-email="${invitation.email}" aria-label="Cancel invitation to ${invitation.email}">
                            <i class="bi bi-x-circle" aria-hidden="true"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    invitationsTable.innerHTML = html;
    
    // Initialize invitation buttons
    initializeInvitationButtons();
}

/**
 * Initialize invitation buttons
 */
function initializeInvitationButtons() {
    // Initialize cancel invitation buttons
    const cancelButtons = document.querySelectorAll('#invitationsTableBody .cancel-invitation');
    
    cancelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const invitationId = this.getAttribute('data-invitation-id');
            const invitationEmail = this.getAttribute('data-invitation-email');
            
            if (confirm(`Are you sure you want to cancel the invitation for ${invitationEmail}?`)) {
                cancelInvitation(invitationId);
            }
        });
    });
    
    // Initialize resend invitation buttons
    const resendButtons = document.querySelectorAll('#invitationsTableBody .resend-invitation');
    
    resendButtons.forEach(button => {
        button.addEventListener('click', function() {
            const invitationId = this.getAttribute('data-invitation-id');
            resendInvitationFromTable(invitationId);
        });
    });
}

/**
 * Cancel invitation
 * @param {string} invitationId - Invitation ID
 */
function cancelInvitation(invitationId) {
    // In a real application, this would make an API call to cancel the invitation
    // For now, we'll just remove the row from the table
    
    const row = document.querySelector(`#invitationsTableBody tr[data-invitation-id="${invitationId}"]`);
    if (row) {
        row.remove();
    }
    
    // Show success message
    showAlert('Invitation cancelled successfully', 'success');
}

/**
 * Resend invitation from table
 * @param {string} invitationId - Invitation ID
 */
function resendInvitationFromTable(invitationId) {
    // In a real application, this would make an API call to resend the invitation
    // For now, we'll just show a success message
    
    // Show success message
    showAlert('Invitation resent successfully', 'success');
}

/**
 * Get the appropriate badge class for a role
 * @param {string} role - Member role
 * @returns {string} Bootstrap badge class
 */
function getRoleBadgeClass(role) {
    switch (role) {
        case 'owner':
            return 'bg-danger';
        case 'admin':
            return 'bg-primary';
        case 'member':
            return 'bg-secondary';
        case 'viewer':
            return 'bg-info';
        default:
            return 'bg-secondary';
    }
}

/**
 * Get the appropriate badge class for a status
 * @param {string} status - Member status
 * @returns {string} Bootstrap badge class
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case 'active':
            return 'bg-success';
        case 'invited':
        case 'pending':
            return 'bg-warning';
        case 'inactive':
            return 'bg-secondary';
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
