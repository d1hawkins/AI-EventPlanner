/**
 * Main JavaScript file for the SaaS application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeNavigation();
    initializeAnimations();
    
    // Handle "Get Started" button click
    const getStartedBtn = document.querySelector('.hero-section .btn-primary');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/saas/signup.html';
        });
    }
    
    // Handle "See Demo" button click
    const demoBtn = document.querySelector('.hero-section .btn-outline-light');
    if (demoBtn) {
        demoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Show demo modal or redirect to demo page
            alert('Demo functionality will be implemented soon!');
        });
    }
});

/**
 * Initialize navigation components
 */
function initializeNavigation() {
    // Mobile navigation toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse) {
                navbarCollapse.classList.toggle('show');
            }
        });
    }
    
    // Add active class to current nav item
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize animations and visual effects
 */
function initializeAnimations() {
    // Add scroll animations
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        // Simple animation on scroll
        window.addEventListener('scroll', function() {
            animatedElements.forEach(element => {
                const position = element.getBoundingClientRect();
                
                // If element is in viewport
                if (position.top < window.innerHeight && position.bottom >= 0) {
                    element.classList.add('animated');
                }
            });
        });
        
        // Trigger initial check
        window.dispatchEvent(new Event('scroll'));
    }
}
