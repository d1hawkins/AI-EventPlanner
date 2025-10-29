/**
 * Settings JavaScript
 * Handles functionality for the settings page in the AI Event Planner SaaS application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar toggle functionality
    initializeSidebar();
    
    // Initialize profile form
    initializeProfileForm();
    
    // Initialize password form
    initializePasswordForm();
    
    // Initialize two-factor authentication
    initializeTwoFactor();
    
    // Initialize session management
    initializeSessionManagement();
    
    // Initialize notifications form
    initializeNotificationsForm();
    
    // Initialize appearance settings
    initializeAppearanceSettings();
    
    // Initialize integrations
    initializeIntegrations();
    
    // Initialize API settings
    initializeApiSettings();
});

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
 * Initialize the profile form
 */
function initializeProfileForm() {
    const profileForm = document.getElementById('profileForm');

    if (profileForm) {
        profileForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            try {
                // Get form values
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const email = document.getElementById('email').value;
                const phone = document.getElementById('phone').value;
                const jobTitle = document.getElementById('jobTitle').value;
                const company = document.getElementById('company').value;
                const bio = document.getElementById('bio').value;
                const timezone = document.getElementById('timezone').value;

                // Get auth token
                const token = localStorage.getItem('authToken');

                if (!token) {
                    throw new Error('Authentication required. Please log in again.');
                }

                // Prepare headers
                const headers = {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                };

                // Make API call to update profile
                const response = await fetch('/api/auth/profile', {
                    method: 'PATCH',
                    headers: headers,
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        email: email,
                        phone: phone,
                        job_title: jobTitle,
                        company: company,
                        bio: bio,
                        timezone: timezone
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Failed to update profile: ${response.statusText}`);
                }

                // Show success message
                showAlert('Profile updated successfully', 'success');

            } catch (error) {
                console.error('Error updating profile:', error);
                showAlert('Failed to update profile: ' + error.message, 'danger');
            }
        });
    }
}

/**
 * Initialize the password form
 */
function initializePasswordForm() {
    const passwordForm = document.getElementById('passwordForm');

    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            try {
                // Get form values
                const currentPassword = document.getElementById('currentPassword').value;
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;

                // Validate passwords
                if (newPassword !== confirmPassword) {
                    showAlert('New passwords do not match', 'danger');
                    return;
                }

                // Validate password strength
                if (newPassword.length < 8) {
                    showAlert('Password must be at least 8 characters long', 'danger');
                    return;
                }

                // Get auth token
                const token = localStorage.getItem('authToken');

                if (!token) {
                    throw new Error('Authentication required. Please log in again.');
                }

                // Prepare headers
                const headers = {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                };

                // Make API call to update password
                const response = await fetch('/api/auth/change-password', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        current_password: currentPassword,
                        new_password: newPassword
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Failed to update password: ${response.statusText}`);
                }

                // Show success message
                showAlert('Password updated successfully', 'success');

                // Reset form
                passwordForm.reset();

            } catch (error) {
                console.error('Error updating password:', error);
                showAlert('Failed to update password: ' + error.message, 'danger');
            }
        });
    }
}

/**
 * Initialize two-factor authentication
 */
function initializeTwoFactor() {
    const enableTwoFactorCheckbox = document.getElementById('enableTwoFactor');
    const twoFactorSetup = document.getElementById('twoFactorSetup');
    const verifyTwoFactorButton = document.getElementById('verifyTwoFactor');
    
    if (enableTwoFactorCheckbox) {
        enableTwoFactorCheckbox.addEventListener('change', function() {
            if (this.checked) {
                twoFactorSetup.style.display = 'block';
                
                // In a real application, this would make an API call to generate a QR code
                // For now, we'll just show the setup section
            } else {
                twoFactorSetup.style.display = 'none';
            }
        });
    }
    
    if (verifyTwoFactorButton) {
        verifyTwoFactorButton.addEventListener('click', function() {
            const verificationCode = document.getElementById('verificationCode').value;
            
            if (!verificationCode) {
                showAlert('Please enter a verification code', 'danger');
                return;
            }
            
            // In a real application, this would make an API call to verify the code
            // For now, we'll just show a success message
            
            // Show success message
            showAlert('Two-factor authentication enabled successfully', 'success');
            
            // Hide setup section
            twoFactorSetup.style.display = 'none';
        });
    }
}

/**
 * Initialize session management
 */
function initializeSessionManagement() {
    // Initialize revoke session buttons
    const revokeButtons = document.querySelectorAll('.btn-danger.btn-sm');
    
    revokeButtons.forEach(button => {
        if (button.textContent.trim() === 'Revoke') {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                
                if (row) {
                    // In a real application, this would make an API call to revoke the session
                    // For now, we'll just remove the row
                    
                    row.remove();
                    
                    // Show success message
                    showAlert('Session revoked successfully', 'success');
                }
            });
        }
    });
    
    // Initialize revoke all sessions button
    const revokeAllButton = document.querySelector('.btn-danger:not(.btn-sm)');
    
    if (revokeAllButton && revokeAllButton.textContent.includes('Revoke All Other Sessions')) {
        revokeAllButton.addEventListener('click', function() {
            // In a real application, this would make an API call to revoke all other sessions
            // For now, we'll just remove all rows except the current session
            
            const rows = document.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                if (!row.textContent.includes('Current Session')) {
                    row.remove();
                }
            });
            
            // Show success message
            showAlert('All other sessions revoked successfully', 'success');
        });
    }
}

/**
 * Initialize the notifications form
 */
function initializeNotificationsForm() {
    const notificationsForm = document.getElementById('notificationsForm');

    if (notificationsForm) {
        notificationsForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            try {
                // Get form values
                const eventCreatedNotification = document.getElementById('eventCreatedNotification').checked;
                const eventUpdatedNotification = document.getElementById('eventUpdatedNotification').checked;
                const teamMemberNotification = document.getElementById('teamMemberNotification').checked;
                const billingNotification = document.getElementById('billingNotification').checked;
                const marketingNotification = document.getElementById('marketingNotification').checked;
                const inAppEventNotification = document.getElementById('inAppEventNotification').checked;
                const inAppTeamNotification = document.getElementById('inAppTeamNotification').checked;
                const inAppSystemNotification = document.getElementById('inAppSystemNotification').checked;

                // Get auth token
                const token = localStorage.getItem('authToken');

                if (!token) {
                    throw new Error('Authentication required. Please log in again.');
                }

                // Prepare headers
                const headers = {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                };

                // Make API call to update notification preferences
                const response = await fetch('/api/auth/notification-preferences', {
                    method: 'PATCH',
                    headers: headers,
                    body: JSON.stringify({
                        email_notifications: {
                            event_created: eventCreatedNotification,
                            event_updated: eventUpdatedNotification,
                            team_member: teamMemberNotification,
                            billing: billingNotification,
                            marketing: marketingNotification
                        },
                        in_app_notifications: {
                            events: inAppEventNotification,
                            team: inAppTeamNotification,
                            system: inAppSystemNotification
                        }
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Failed to update notification preferences: ${response.statusText}`);
                }

                // Show success message
                showAlert('Notification preferences updated successfully', 'success');

            } catch (error) {
                console.error('Error updating notification preferences:', error);
                showAlert('Failed to update notification preferences: ' + error.message, 'danger');
            }
        });
    }
}

/**
 * Initialize appearance settings
 */
function initializeAppearanceSettings() {
    const saveAppearanceSettingsButton = document.getElementById('saveAppearanceSettings');

    if (saveAppearanceSettingsButton) {
        saveAppearanceSettingsButton.addEventListener('click', async function() {
            try {
                // Get form values
                const theme = document.querySelector('input[name="theme"]:checked')?.id.replace('Theme', '') || 'light';
                const density = document.querySelector('input[name="density"]:checked')?.id.replace('Density', '') || 'comfortable';
                const fontSize = document.getElementById('fontSizeRange')?.value || 16;

                // Get auth token
                const token = localStorage.getItem('authToken');

                if (!token) {
                    throw new Error('Authentication required. Please log in again.');
                }

                // Prepare headers
                const headers = {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                };

                // Make API call to update appearance settings
                const response = await fetch('/api/auth/appearance-preferences', {
                    method: 'PATCH',
                    headers: headers,
                    body: JSON.stringify({
                        theme: theme,
                        density: density,
                        font_size: parseInt(fontSize)
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Failed to update appearance settings: ${response.statusText}`);
                }

                // Show success message
                showAlert('Appearance settings updated successfully', 'success');

            } catch (error) {
                console.error('Error updating appearance settings:', error);
                showAlert('Failed to update appearance settings: ' + error.message, 'danger');
            }
        });
    }
}

/**
 * Initialize integrations
 */
function initializeIntegrations() {
    // Initialize integration toggles
    const integrationToggles = [
        'googleCalendarToggle',
        'outlookToggle',
        'zoomToggle',
        'slackToggle'
    ];
    
    integrationToggles.forEach(toggleId => {
        const toggle = document.getElementById(toggleId);
        
        if (toggle) {
            toggle.addEventListener('change', function() {
                const serviceName = toggleId.replace('Toggle', '');
                const status = this.checked ? 'enabled' : 'disabled';
                
                // In a real application, this would make an API call to update the integration status
                // For now, we'll just show a success message
                
                // Show success message
                showAlert(`${serviceName} integration ${status} successfully`, 'success');
            });
        }
    });
    
    // Initialize connect buttons
    const connectButtons = document.querySelectorAll('.btn-primary.btn-sm');
    
    connectButtons.forEach(button => {
        if (button.textContent.trim() === 'Connect') {
            button.addEventListener('click', function() {
                const card = this.closest('.card');
                const serviceName = card.querySelector('.h6').textContent;
                
                // In a real application, this would redirect to the service's OAuth flow
                // For now, we'll just show a success message
                
                // Show success message
                showAlert(`Connecting to ${serviceName}...`, 'info');
                
                // Simulate connection success after 2 seconds
                setTimeout(() => {
                    // Update UI
                    const alertElement = card.querySelector('.alert');
                    alertElement.className = 'alert alert-success mb-3';
                    alertElement.innerHTML = '<i class="bi bi-check-circle-fill me-2" aria-hidden="true"></i> Connected as john.doe@example.com';
                    
                    // Update toggle
                    const toggle = card.querySelector('.form-check-input');
                    toggle.checked = true;
                    
                    // Update button
                    this.className = 'btn btn-outline-danger btn-sm';
                    this.innerHTML = '<i class="bi bi-x-circle" aria-hidden="true"></i> Disconnect';
                    
                    // Show success message
                    showAlert(`Connected to ${serviceName} successfully`, 'success');
                }, 2000);
            });
        }
    });
    
    // Initialize disconnect buttons
    const disconnectButtons = document.querySelectorAll('.btn-outline-danger.btn-sm');
    
    disconnectButtons.forEach(button => {
        if (button.textContent.trim() === 'Disconnect') {
            button.addEventListener('click', function() {
                const card = this.closest('.card');
                const serviceName = card.querySelector('.h6').textContent;
                
                // In a real application, this would make an API call to disconnect the service
                // For now, we'll just show a success message
                
                // Update UI
                const alertElement = card.querySelector('.alert');
                alertElement.className = 'alert alert-secondary mb-3';
                alertElement.innerHTML = '<i class="bi bi-info-circle-fill me-2" aria-hidden="true"></i> Not connected';
                
                // Update toggle
                const toggle = card.querySelector('.form-check-input');
                toggle.checked = false;
                
                // Update button
                this.className = 'btn btn-primary btn-sm';
                this.innerHTML = '<i class="bi bi-link" aria-hidden="true"></i> Connect';
                
                // Show success message
                showAlert(`Disconnected from ${serviceName} successfully`, 'success');
            });
        }
    });
}

/**
 * Initialize API settings
 */
function initializeApiSettings() {
    const generateApiKeyButton = document.getElementById('generateApiKey');
    const showApiKeyButton = document.getElementById('showApiKey');
    const copyApiKeyButton = document.getElementById('copyApiKey');
    const saveApiSettingsButton = document.getElementById('saveApiSettings');
    
    if (generateApiKeyButton) {
        generateApiKeyButton.addEventListener('click', function() {
            // In a real application, this would make an API call to generate a new API key
            // For now, we'll just show a success message
            
            // Generate a random API key
            const apiKey = generateRandomApiKey();
            
            // Update input value
            document.getElementById('apiKey').value = apiKey;
            
            // Show success message
            showAlert('New API key generated successfully', 'success');
        });
    }
    
    if (showApiKeyButton) {
        showApiKeyButton.addEventListener('click', function() {
            const apiKeyInput = document.getElementById('apiKey');
            
            if (apiKeyInput.type === 'password') {
                apiKeyInput.type = 'text';
                this.innerHTML = '<i class="bi bi-eye-slash" aria-hidden="true"></i>';
            } else {
                apiKeyInput.type = 'password';
                this.innerHTML = '<i class="bi bi-eye" aria-hidden="true"></i>';
            }
        });
    }
    
    if (copyApiKeyButton) {
        copyApiKeyButton.addEventListener('click', function() {
            const apiKeyInput = document.getElementById('apiKey');
            
            // Ensure the API key is visible
            if (apiKeyInput.type === 'password') {
                apiKeyInput.type = 'text';
                showApiKeyButton.innerHTML = '<i class="bi bi-eye-slash" aria-hidden="true"></i>';
            }
            
            // Copy to clipboard
            apiKeyInput.select();
            document.execCommand('copy');
            
            // Show success message
            showAlert('API key copied to clipboard', 'success');
        });
    }
    
    if (saveApiSettingsButton) {
        saveApiSettingsButton.addEventListener('click', function() {
            const webhookUrl = document.getElementById('webhookUrl').value;
            
            // In a real application, this would make an API call to update the webhook URL
            // For now, we'll just show a success message
            
            // Show success message
            showAlert('API settings saved successfully', 'success');
        });
    }
}

/**
 * Generate a random API key
 * @returns {string} Random API key
 */
function generateRandomApiKey() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const length = 32;
    let result = '';
    
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    return result;
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
