/**
 * AI Event Planner SaaS - Authentication JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Login Form Handling
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const usernameField = document.getElementById('username');
            const passwordField = document.getElementById('password');
            
            const username = usernameField.value;
            const password = passwordField.value;
            const rememberMe = document.getElementById('rememberMe') ? document.getElementById('rememberMe').checked : false;
            
            // Validate form
            let isValid = true;
            let errorMessage = '';
            
            if (!username) {
                isValid = false;
                errorMessage += 'Username or email is required.\n';
            }
            
            if (!password) {
                isValid = false;
                errorMessage += 'Password is required.\n';
            }
            
            if (!isValid) {
                showToast(errorMessage, 'error');
                return;
            }
            
            // Make API call to authenticate the user
            console.log('Login form submitted:', { username, password, rememberMe });
            
            showLoading();
            
            // Disable form elements during login
            const submitButton = loginForm.querySelector('button[type="submit"]');
            const formInputs = loginForm.querySelectorAll('input');

            submitButton.disabled = true;
            submitButton.textContent = 'Logging in...';
            formInputs.forEach(input => input.disabled = true);
            
            // Create form data for OAuth2PasswordRequestForm
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            
            fetch('/auth/token', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Invalid credentials');
                }
                return response.json();
            })
            .then(data => {
                // Store the token
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('tokenType', data.token_type);
                
                hideLoading();
                
                // Re-enable form elements
                const submitButton = loginForm.querySelector('button[type="submit"]');
                const formInputs = loginForm.querySelectorAll('input');
                submitButton.disabled = false;
                submitButton.textContent = 'Login';
                formInputs.forEach(input => input.disabled = false);
                
                showToast('Login successful!', 'success');
                
                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = '/saas/dashboard.html';
                }, 1000);
            })
            .catch(error => {
                hideLoading();
                console.error('Login error:', error);
                
                // Re-enable form elements
                const submitButton = loginForm.querySelector('button[type="submit"]');
                const formInputs = loginForm.querySelectorAll('input');
                submitButton.disabled = false;
                submitButton.textContent = 'Login';
                formInputs.forEach(input => input.disabled = false);
                
                // Parse different error types
                let errorMessage = 'Login failed. Please try again.';
                
                if (error.message === 'Invalid credentials') {
                    errorMessage = 'Invalid username/email or password. Please check your credentials and try again.';
                } else if (error.message === 'Failed to fetch') {
                    errorMessage = 'Unable to connect to server. Please check your internet connection.';
                } else if (error.message.includes('401')) {
                    errorMessage = 'Invalid username/email or password.';
                } else if (error.message.includes('500')) {
                    errorMessage = 'Server error. Please try again later.';
                }
                
                showToast(errorMessage, 'error');
            });
        });
    }
    
    // Signup Form Handling
    const signupForm = document.getElementById('signupForm');
    
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values - handle both single-step and multi-step forms
            const currentStep = document.querySelector('.signup-step:not([style*="display: none"])');
            const isMultiStep = currentStep !== null;
            
            if (isMultiStep && currentStep.id === 'step3') {
                // Multi-step form - final step
                const termsCheck = document.getElementById('termsCheck').checked;
                
                if (!termsCheck) {
                    showToast('You must agree to the Terms of Service and Privacy Policy to continue.', 'error');
                    return;
                }
                
                // Collect all form data
                const formData = {
                    fullName: document.getElementById('fullName').value,
                    email: document.getElementById('email').value,
                    password: document.getElementById('password').value,
                    orgName: document.getElementById('orgName').value,
                    orgSlug: document.getElementById('orgSlug').value,
                    plan: document.querySelector('input[name="plan"]:checked').value,
                    marketingConsent: document.getElementById('marketingCheck').checked
                };
                
                console.log('Signup form submitted:', formData);
                showLoading();
                
                // TODO: Implement full organization signup
                setTimeout(function() {
                    hideLoading();
                    window.location.href = '/saas/dashboard.html';
                }, 1500);
            } else {
                // Simple registration form
                const email = document.getElementById('email').value;
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                // Validate form
                let isValid = true;
                let errorMessage = '';
                
                if (!email) {
                    isValid = false;
                    errorMessage += 'Email is required.\n';
                } else if (!isValidEmail(email)) {
                    isValid = false;
                    errorMessage += 'Please enter a valid email address.\n';
                }
                
                if (!username) {
                    isValid = false;
                    errorMessage += 'Username is required.\n';
                }
                
                if (!password) {
                    isValid = false;
                    errorMessage += 'Password is required.\n';
                } else if (password.length < 8) {
                    isValid = false;
                    errorMessage += 'Password must be at least 8 characters long.\n';
                }
                
                if (!isValid) {
                    showToast(errorMessage, 'error');
                    return;
                }
                
                // Make API call to register the user
                console.log('Registration form submitted:', { email, username, password });
                
                showLoading();
                
                fetch('/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        username: username,
                        password: password,
                        is_active: true
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.detail || 'Registration failed');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    hideLoading();
                    showToast('Registration successful! Please login.', 'success');
                    
                    // Redirect to login page
                    setTimeout(() => {
                        window.location.href = '/saas/login.html';
                    }, 2000);
                })
                .catch(error => {
                    hideLoading();
                    console.error('Registration error:', error);
                    showToast(error.message || 'Registration failed', 'error');
                });
            }
        });
    }
    
    // Password strength meter
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            if (confirmPasswordInput && confirmPasswordInput.value) {
                validatePasswordMatch();
            }
            
            // Update password strength indicator if it exists
            const strengthMeter = document.getElementById('passwordStrength');
            if (strengthMeter) {
                const strength = calculatePasswordStrength(this.value);
                updatePasswordStrengthUI(strength, strengthMeter);
            }
        });
    }
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }
    
    // Organization slug generator
    const orgNameInput = document.getElementById('orgName');
    const orgSlugInput = document.getElementById('orgSlug');
    
    if (orgNameInput && orgSlugInput) {
        orgNameInput.addEventListener('input', function() {
            // Only auto-generate slug if user hasn't manually edited it
            if (!orgSlugInput.dataset.userEdited) {
                orgSlugInput.value = generateSlug(this.value);
            }
        });
        
        orgSlugInput.addEventListener('input', function() {
            // Mark that user has manually edited the slug
            this.dataset.userEdited = 'true';
        });
    }
    
    // Helper Functions
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (password !== confirmPassword) {
            confirmPasswordInput.setCustomValidity('Passwords do not match');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    }
    
    function calculatePasswordStrength(password) {
        let strength = 0;
        
        // Length check
        if (password.length >= 8) strength += 1;
        if (password.length >= 12) strength += 1;
        
        // Character type checks
        if (/[a-z]/.test(password)) strength += 1; // lowercase
        if (/[A-Z]/.test(password)) strength += 1; // uppercase
        if (/[0-9]/.test(password)) strength += 1; // numbers
        if (/[^a-zA-Z0-9]/.test(password)) strength += 1; // special characters
        
        return Math.min(strength, 5); // Max strength of 5
    }
    
    function updatePasswordStrengthUI(strength, element) {
        // Remove all classes
        element.className = 'password-strength-meter';
        
        // Add appropriate class based on strength
        switch (strength) {
            case 0:
            case 1:
                element.classList.add('very-weak');
                element.textContent = 'Very Weak';
                break;
            case 2:
                element.classList.add('weak');
                element.textContent = 'Weak';
                break;
            case 3:
                element.classList.add('medium');
                element.textContent = 'Medium';
                break;
            case 4:
                element.classList.add('strong');
                element.textContent = 'Strong';
                break;
            case 5:
                element.classList.add('very-strong');
                element.textContent = 'Very Strong';
                break;
        }
    }
    
    function generateSlug(text) {
        return text
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }
    
    function showLoading() {
        // Create loading overlay if it doesn't exist
        if (!document.getElementById('loadingOverlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.body.appendChild(overlay);
            
            // Add styles
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '9999';
        }
        
        document.getElementById('loadingOverlay').style.display = 'flex';
    }
    
    function hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.style.position = 'fixed';
            toastContainer.style.top = '20px';
            toastContainer.style.right = '20px';
            toastContainer.style.zIndex = '10000';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        toast.style.minWidth = '300px';
        toast.style.marginBottom = '10px';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Log to console for debugging
        console.log(`Toast: ${message} (${type})`);
    }
});

// Functions for multi-step form navigation
function nextStep(step) {
    // Validate current step before proceeding
    const currentStep = parseInt(document.querySelector('.signup-step:not([style*="display: none"])').id.replace('step', ''));
    
    if (currentStep === 1) {
        // Validate personal information
        const fullName = document.getElementById('fullName').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        let isValid = true;
        let errorMessage = '';
        
        if (!fullName) {
            isValid = false;
            errorMessage += 'Full name is required.\n';
        }
        
        if (!email) {
            isValid = false;
            errorMessage += 'Email is required.\n';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            isValid = false;
            errorMessage += 'Please enter a valid email address.\n';
        }
        
        if (!password) {
            isValid = false;
            errorMessage += 'Password is required.\n';
        } else if (password.length < 8) {
            isValid = false;
            errorMessage += 'Password must be at least 8 characters long.\n';
        }
        
        if (password !== confirmPassword) {
            isValid = false;
            errorMessage += 'Passwords do not match.\n';
        }
        
        if (!isValid) {
            alert(errorMessage);
            return;
        }
    } else if (currentStep === 2) {
        // Validate organization information
        const orgName = document.getElementById('orgName').value;
        const orgSlug = document.getElementById('orgSlug').value;
        
        let isValid = true;
        let errorMessage = '';
        
        if (!orgName) {
            isValid = false;
            errorMessage += 'Organization name is required.\n';
        }
        
        if (!orgSlug) {
            isValid = false;
            errorMessage += 'Organization slug is required.\n';
        } else if (!/^[a-z0-9-]+$/.test(orgSlug)) {
            isValid = false;
            errorMessage += 'Organization slug can only contain lowercase letters, numbers, and hyphens.\n';
        }
        
        if (!isValid) {
            alert(errorMessage);
            return;
        }
    }
    
    // Hide all steps
    document.querySelectorAll('.signup-step').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show the requested step
    document.getElementById('step' + step).style.display = 'block';
}

function prevStep(step) {
    // Hide all steps
    document.querySelectorAll('.signup-step').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show the requested step
    document.getElementById('step' + step).style.display = 'block';
}
