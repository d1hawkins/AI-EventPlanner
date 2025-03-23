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
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;
            
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
            
            if (!password) {
                isValid = false;
                errorMessage += 'Password is required.\n';
            }
            
            if (!isValid) {
                alert(errorMessage);
                return;
            }
            
            // In a real application, this would make an API call to authenticate the user
            // For demo purposes, we'll just redirect to the dashboard
            console.log('Login form submitted:', { email, password, rememberMe });
            
            // Simulate API call with a timeout
            showLoading();
            
            setTimeout(function() {
                hideLoading();
                window.location.href = '/static/saas/dashboard.html';
            }, 1500);
        });
    }
    
    // Signup Form Handling
    const signupForm = document.getElementById('signupForm');
    
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values from the current step
            const currentStep = document.querySelector('.signup-step:not([style*="display: none"])');
            const stepId = currentStep.id;
            
            if (stepId === 'step3') {
                // Final step - validate terms acceptance
                const termsCheck = document.getElementById('termsCheck').checked;
                
                if (!termsCheck) {
                    alert('You must agree to the Terms of Service and Privacy Policy to continue.');
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
                
                // In a real application, this would make an API call to create the user and organization
                console.log('Signup form submitted:', formData);
                
                // Simulate API call with a timeout
                showLoading();
                
                setTimeout(function() {
                    hideLoading();
                    window.location.href = '/static/saas/dashboard.html';
                }, 1500);
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
