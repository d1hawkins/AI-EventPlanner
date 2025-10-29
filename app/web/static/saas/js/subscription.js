/**
 * Subscription JavaScript
 * Handles functionality for the subscription management page in the AI Event Planner SaaS application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar toggle functionality
    initializeSidebar();
    
    // Initialize billing cycle form
    initializeBillingCycle();
    
    // Initialize billing contact form
    initializeBillingContact();
    
    // Initialize payment method form
    initializePaymentMethod();
    
    // Initialize plan change modal
    initializePlanChangeModal();
    
    // Initialize contact sales form
    initializeContactSales();
    
    // Initialize cancellation form
    initializeCancellation();
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
 * Initialize the billing cycle form
 */
function initializeBillingCycle() {
    const updateBillingCycleButton = document.getElementById('updateBillingCycle');
    
    if (updateBillingCycleButton) {
        updateBillingCycleButton.addEventListener('click', function() {
            const annualBilling = document.getElementById('annualBilling').checked;
            const monthlyBilling = document.getElementById('monthlyBilling').checked;
            
            let billingCycle = '';
            if (annualBilling) {
                billingCycle = 'annual';
            } else if (monthlyBilling) {
                billingCycle = 'monthly';
            }
            
            if (billingCycle) {
                updateBillingCycleRequest(billingCycle);
            }
        });
    }
}

/**
 * Update billing cycle request
 * @param {string} billingCycle - Billing cycle (annual or monthly)
 */
async function updateBillingCycleRequest(billingCycle) {
    try {
        // Get auth token and org ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            throw new Error('Authentication required. Please log in again.');
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Make API call to update billing cycle
        const response = await fetch(`/api/subscription/organizations/${orgId}/billing-cycle`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify({
                billing_cycle: billingCycle
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to update billing cycle: ${response.statusText}`);
        }

        // Show success message
        showAlert(`Billing cycle updated to ${billingCycle}`, 'success');

    } catch (error) {
        console.error('Error updating billing cycle:', error);
        showAlert('Failed to update billing cycle: ' + error.message, 'danger');
    }
}

/**
 * Initialize the billing contact form
 */
function initializeBillingContact() {
    const billingContactForm = document.getElementById('billingContactForm');
    
    if (billingContactForm) {
        billingContactForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const billingEmail = document.getElementById('billingEmail').value;
            const billingName = document.getElementById('billingName').value;
            const sendInvoices = document.getElementById('sendInvoices').checked;
            
            updateBillingContactRequest(billingEmail, billingName, sendInvoices);
        });
    }
}

/**
 * Update billing contact request
 * @param {string} email - Billing email
 * @param {string} name - Billing name
 * @param {boolean} sendInvoices - Send invoices to billing email
 */
async function updateBillingContactRequest(email, name, sendInvoices) {
    try {
        // Get auth token and org ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            throw new Error('Authentication required. Please log in again.');
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Make API call to update billing contact
        const response = await fetch(`/api/subscription/organizations/${orgId}/billing-contact`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify({
                billing_email: email,
                billing_name: name,
                send_invoices: sendInvoices
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to update billing contact: ${response.statusText}`);
        }

        // Show success message
        showAlert('Billing contact updated successfully', 'success');

    } catch (error) {
        console.error('Error updating billing contact:', error);
        showAlert('Failed to update billing contact: ' + error.message, 'danger');
    }
}

/**
 * Initialize the payment method form
 */
function initializePaymentMethod() {
    const savePaymentMethodButton = document.getElementById('savePaymentMethod');
    
    if (savePaymentMethodButton) {
        savePaymentMethodButton.addEventListener('click', function() {
            const updatePaymentForm = document.getElementById('updatePaymentForm');
            
            if (updatePaymentForm.checkValidity()) {
                const cardNumber = document.getElementById('cardNumber').value;
                const expiryDate = document.getElementById('expiryDate').value;
                const cvv = document.getElementById('cvv').value;
                const cardName = document.getElementById('cardName').value;
                const billingAddress = document.getElementById('billingAddress').value;
                const city = document.getElementById('city').value;
                const zipCode = document.getElementById('zipCode').value;
                const country = document.getElementById('country').value;
                
                updatePaymentMethodRequest({
                    cardNumber,
                    expiryDate,
                    cvv,
                    cardName,
                    billingAddress,
                    city,
                    zipCode,
                    country
                });
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('updatePaymentModal'));
                modal.hide();
            } else {
                // Trigger form validation
                updatePaymentForm.classList.add('was-validated');
            }
        });
    }
}

/**
 * Update payment method request
 * @param {Object} paymentData - Payment data
 */
async function updatePaymentMethodRequest(paymentData) {
    try {
        // Get auth token and org ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            throw new Error('Authentication required. Please log in again.');
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Make API call to update payment method via Stripe
        const response = await fetch(`/api/subscription/organizations/${orgId}/payment-method`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                card_number: paymentData.cardNumber,
                exp_month: paymentData.expiryDate.split('/')[0],
                exp_year: paymentData.expiryDate.split('/')[1],
                cvc: paymentData.cvv,
                name: paymentData.cardName,
                address_line1: paymentData.billingAddress,
                address_city: paymentData.city,
                address_zip: paymentData.zipCode,
                address_country: paymentData.country
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to update payment method: ${response.statusText}`);
        }

        const result = await response.json();

        // Show success message
        showAlert('Payment method updated successfully', 'success');

        // Update payment method display
        const paymentMethodElement = document.querySelector('.card-body .h5.mb-0.font-weight-bold.text-gray-800');
        if (paymentMethodElement) {
            // Format the card number to show only the last 4 digits
            const lastFourDigits = paymentData.cardNumber.slice(-4);
            paymentMethodElement.textContent = `•••• •••• •••• ${lastFourDigits}`;
        }

        // Update expiry date
        const expiryDateElement = document.querySelector('.card-body .small.text-muted');
        if (expiryDateElement) {
            expiryDateElement.textContent = `Visa - Expires ${paymentData.expiryDate}`;
        }

    } catch (error) {
        console.error('Error updating payment method:', error);
        showAlert('Failed to update payment method: ' + error.message, 'danger');
    }
}

/**
 * Initialize the plan change modal
 */
function initializePlanChangeModal() {
    const changePlanModal = document.getElementById('changePlanModal');
    
    if (changePlanModal) {
        // Show the appropriate content based on the plan
        changePlanModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const plan = button.getAttribute('data-plan');
            
            const downgradePlanContent = document.getElementById('downgradePlanContent');
            const upgradePlanContent = document.getElementById('upgradePlanContent');
            
            if (plan === 'starter') {
                downgradePlanContent.style.display = 'block';
                upgradePlanContent.style.display = 'none';
            } else if (plan === 'enterprise') {
                downgradePlanContent.style.display = 'none';
                upgradePlanContent.style.display = 'block';
            }
            
            // Reset checkbox
            document.getElementById('confirmPlanChange').checked = false;
            document.getElementById('confirmPlanChangeBtn').disabled = true;
        });
        
        // Enable/disable confirm button based on checkbox
        const confirmPlanChangeCheckbox = document.getElementById('confirmPlanChange');
        if (confirmPlanChangeCheckbox) {
            confirmPlanChangeCheckbox.addEventListener('change', function() {
                document.getElementById('confirmPlanChangeBtn').disabled = !this.checked;
            });
        }
        
        // Handle confirm button click
        const confirmPlanChangeBtn = document.getElementById('confirmPlanChangeBtn');
        if (confirmPlanChangeBtn) {
            confirmPlanChangeBtn.addEventListener('click', function() {
                const plan = document.getElementById('downgradePlanContent').style.display === 'block' ? 'starter' : 'enterprise';
                changePlanRequest(plan);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('changePlanModal'));
                modal.hide();
            });
        }
    }
}

/**
 * Change plan request
 * @param {string} plan - Plan name
 */
async function changePlanRequest(plan) {
    try {
        // Get auth token and org ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            throw new Error('Authentication required. Please log in again.');
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Make API call to change plan
        const response = await fetch(`/api/subscription/organizations/${orgId}/plan`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify({
                plan_tier: plan
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to change plan: ${response.statusText}`);
        }

        // Show appropriate success message
        if (plan === 'starter') {
            showAlert('Your plan will be downgraded to Starter at the end of your current billing period', 'success');
        } else if (plan === 'enterprise') {
            showAlert('Your plan has been upgraded to Enterprise', 'success');
        } else {
            showAlert(`Plan changed to ${plan} successfully`, 'success');
        }

    } catch (error) {
        console.error('Error changing plan:', error);
        showAlert('Failed to change plan: ' + error.message, 'danger');
    }
}

/**
 * Initialize the contact sales form
 */
function initializeContactSales() {
    const submitContactSalesButton = document.getElementById('submitContactSales');
    
    if (submitContactSalesButton) {
        submitContactSalesButton.addEventListener('click', function() {
            const contactSalesForm = document.getElementById('contactSalesForm');
            
            if (contactSalesForm.checkValidity()) {
                const contactName = document.getElementById('contactName').value;
                const contactEmail = document.getElementById('contactEmail').value;
                const contactPhone = document.getElementById('contactPhone').value;
                const companyName = document.getElementById('companyName').value;
                const teamSize = document.getElementById('teamSize').value;
                const requirements = document.getElementById('requirements').value;
                
                contactSalesRequest({
                    contactName,
                    contactEmail,
                    contactPhone,
                    companyName,
                    teamSize,
                    requirements
                });
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('contactSalesModal'));
                modal.hide();
            } else {
                // Trigger form validation
                contactSalesForm.classList.add('was-validated');
            }
        });
    }
}

/**
 * Contact sales request
 * @param {Object} contactData - Contact data
 */
function contactSalesRequest(contactData) {
    // In a real application, this would make an API call to submit the contact request
    // For now, we'll just show a success message
    
    // Show success message
    showAlert('Your request has been submitted. Our sales team will contact you shortly.', 'success');
}

/**
 * Initialize the cancellation form
 */
function initializeCancellation() {
    const cancellationReasonSelect = document.getElementById('cancellationReason');
    const otherReasonContainer = document.getElementById('otherReasonContainer');
    
    if (cancellationReasonSelect) {
        cancellationReasonSelect.addEventListener('change', function() {
            if (this.value === 'other') {
                otherReasonContainer.style.display = 'block';
            } else {
                otherReasonContainer.style.display = 'none';
            }
        });
    }
    
    // Enable/disable confirm button based on checkbox
    const confirmCancellationCheckbox = document.getElementById('confirmCancellation');
    if (confirmCancellationCheckbox) {
        confirmCancellationCheckbox.addEventListener('change', function() {
            document.getElementById('confirmCancellationBtn').disabled = !this.checked;
        });
    }
    
    // Handle confirm button click
    const confirmCancellationBtn = document.getElementById('confirmCancellationBtn');
    if (confirmCancellationBtn) {
        confirmCancellationBtn.addEventListener('click', function() {
            const reason = document.getElementById('cancellationReason').value;
            let otherReason = '';
            
            if (reason === 'other') {
                otherReason = document.getElementById('otherReason').value;
            }
            
            cancelSubscriptionRequest(reason, otherReason);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('cancelSubscriptionModal'));
            modal.hide();
        });
    }
}

/**
 * Cancel subscription request
 * @param {string} reason - Cancellation reason
 * @param {string} otherReason - Other reason (if reason is 'other')
 */
async function cancelSubscriptionRequest(reason, otherReason) {
    try {
        // Get auth token and org ID
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId') || document.querySelector('meta[name="organization-id"]')?.content;

        if (!token || !orgId) {
            throw new Error('Authentication required. Please log in again.');
        }

        // Prepare headers
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
        };

        // Make API call to cancel subscription
        const response = await fetch(`/api/subscription/organizations/${orgId}/cancel`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                cancellation_reason: reason,
                other_reason: otherReason
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to cancel subscription: ${response.statusText}`);
        }

        const result = await response.json();

        // Show success message with cancellation date from API if available
        const cancellationDate = result.cancellation_date || 'the end of your current billing period';
        showAlert(`Your subscription has been cancelled and will end on ${cancellationDate}`, 'success');

    } catch (error) {
        console.error('Error cancelling subscription:', error);
        showAlert('Failed to cancel subscription: ' + error.message, 'danger');
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
