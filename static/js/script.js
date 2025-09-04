// Jubair Boot House - Enhanced Modern JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Enhanced smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enhanced fade-in animation with intersection observer
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                // Add staggered animation for multiple elements
                if (entry.target.parentElement && entry.target.parentElement.children.length > 1) {
                    const children = Array.from(entry.target.parentElement.children);
                    const index = children.indexOf(entry.target);
                    entry.target.style.animationDelay = `${index * 0.1}s`;
                }
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.category-card, .feature-card, .product-card, .testimonial-card, .stats-card').forEach(el => {
        observer.observe(el);
    });

    // Enhanced form validation with better UX
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Add shake animation to invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('shake');
                    setTimeout(() => field.classList.remove('shake'), 500);
                });
            }
            form.classList.add('was-validated');
        });
    });

    // Enhanced search functionality with debouncing
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchInput.classList.add('loading');
            
            searchTimeout = setTimeout(() => {
                // Simulate search delay (remove in production)
                setTimeout(() => {
                    searchInput.classList.remove('loading');
                }, 500);
            }, 300);
        });
    }

    // Enhanced product card interactions
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
            this.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });

    // Enhanced category card interactions
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.category-icon i');
            const hoverEffect = this.querySelector('.category-hover-effect');
            
            if (icon) {
                icon.style.transform = 'scale(1.15) rotate(5deg)';
                icon.style.color = 'var(--accent-yellow)';
            }
            
            if (hoverEffect) {
                hoverEffect.style.transform = 'translateX(0) scale(1.1)';
                hoverEffect.style.opacity = '1';
            }
            
            // Add ripple effect
            this.style.transform = 'translateY(-12px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.category-icon i');
            const hoverEffect = this.querySelector('.category-hover-effect');
            
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
                icon.style.color = 'var(--primary-blue)';
            }
            
            if (hoverEffect) {
                hoverEffect.style.transform = 'translateX(20px) scale(1)';
                hoverEffect.style.opacity = '0';
            }
            
            // Reset transform
            this.style.transform = 'translateY(0) scale(1)';
        });
        
        // Add click effect
        card.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
    
    // Ensure icons are properly displayed
    function ensureIconsDisplay() {
        const bootIcon = document.querySelector('.fa-boot');
        const sandalIcon = document.querySelector('.fa-sandal');
        const dumbbellIcon = document.querySelector('.fa-dumbbell');
        const homeIcon = document.querySelector('.fa-home');
        const userTieIcon = document.querySelector('.fa-user-tie');
        const runningIcon = document.querySelector('.fa-running');
        
        if (bootIcon && !bootIcon.offsetWidth) {
            // Fallback for boots icon
            bootIcon.innerHTML = '👢';
            bootIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
        }
        
        if (sandalIcon && !sandalIcon.offsetWidth) {
            // Fallback for sandals icon
            sandalIcon.innerHTML = '🩴';
            sandalIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
        }
        
        if (dumbbellIcon && !dumbbellIcon.offsetWidth) {
            // Fallback for sports icon
            dumbbellIcon.innerHTML = '🏋️';
            dumbbellIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
        }
        
        if (homeIcon && !homeIcon.offsetWidth) {
            // Fallback for casual icon
            homeIcon.innerHTML = '🏠';
            homeIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
        }
        
        if (userTieIcon && !userTieIcon.offsetWidth) {
            // Fallback for formal icon
            userTieIcon.innerHTML = '👔';
            userTieIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
        }
        
        if (runningIcon && !runningIcon.offsetWidth) {
            // Fallback for sneakers icon
            runningIcon.innerHTML = '🏃';
            runningIcon.style.fontFamily = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
        }
    }
    
    // Check icons after page load
    setTimeout(ensureIconsDisplay, 1000);
    
    // Also check when Font Awesome might load
    document.addEventListener('DOMContentLoaded', ensureIconsDisplay);

    // Enhanced modal interactions
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            this.querySelector('.modal-content').style.transform = 'scale(0.8)';
            this.querySelector('.modal-content').style.opacity = '0';
        });
        
        modal.addEventListener('shown.bs.modal', function() {
            this.querySelector('.modal-content').style.transform = 'scale(1)';
            this.querySelector('.modal-content').style.opacity = '1';
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
            }
        });
    });

    // Enhanced image lazy loading with fade-in effect
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('fade-in');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }



    // Enhanced filter form with auto-submit and better UX
    const filterForm = document.querySelector('form[action="/products/"]');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input');
        
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit form when filters change (except search)
                if (this.type !== 'search') {
                    // Add loading state to form
                    filterForm.classList.add('loading');
                    
                    // Submit with slight delay for better UX
                    setTimeout(() => {
                        filterForm.submit();
                    }, 300);
                }
            });
        });
    }

    // Enhanced status toggle with confirmation and better feedback
    document.querySelectorAll('form[action*="toggle-status"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const currentStatus = this.querySelector('button').textContent.trim();
            const newStatus = currentStatus === 'Available' ? 'Out of Stock' : 'Available';
            
            if (!confirm(`Are you sure you want to change the status to "${newStatus}"?`)) {
                e.preventDefault();
            } else {
                // Add loading state
                const btn = this.querySelector('button');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';
                btn.disabled = true;
            }
        });
    });

    // Enhanced delete confirmation with better UX
    document.querySelectorAll('form[action*="delete"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const productName = this.closest('tr').querySelector('td:nth-child(2) strong').textContent;
            
            if (!confirm(`Are you sure you want to delete "${productName}"? This action cannot be undone.`)) {
                e.preventDefault();
            } else {
                // Add loading state
                const btn = this.querySelector('button');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Deleting...';
                btn.disabled = true;
            }
        });
    });

    // Enhanced responsive table with better mobile experience
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        if (table.scrollWidth > table.clientWidth) {
            table.style.overflowX = 'auto';
            
            // Add scroll indicator
            const scrollIndicator = document.createElement('div');
            scrollIndicator.className = 'scroll-indicator';
            scrollIndicator.innerHTML = '<i class="fas fa-arrows-alt-h me-2"></i>Scroll to see more';
            scrollIndicator.style.cssText = 'text-align: center; padding: 0.5rem; color: var(--text-muted); font-size: 0.875rem;';
            
            table.parentNode.insertBefore(scrollIndicator, table);
        }
    });

    // Enhanced keyboard navigation for modals and forms
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const closeBtn = openModal.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        }
        
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }
    });

    // Enhanced toast notifications with better styling
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Auto-remove after toast is hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
    
    function getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // Make toast function globally available
    window.showToast = showToast;

    // Enhanced navbar scroll effects
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const scrolled = window.pageYOffset;
            const navbar = document.querySelector('.navbar');
            
            if (scrolled > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }, 10);
    });

    // Enhanced newsletter form with better validation
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (emailInput.checkValidity()) {
                // Add loading state
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Subscribing...';
                submitBtn.disabled = true;
                
                // Simulate API call
                setTimeout(() => {
                    showToast('Successfully subscribed to newsletter!', 'success');
                    emailInput.value = '';
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 1500);
            }
        });
    }

    // Enhanced floating action button (if needed)
    function createFloatingActionButton() {
        const fab = document.createElement('button');
        fab.className = 'floating-action-btn';
        fab.innerHTML = '<i class="fas fa-arrow-up"></i>';
        fab.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary-blue), var(--primary-dark));
            color: white;
            border: none;
            box-shadow: var(--shadow-lg);
            cursor: pointer;
            transition: var(--transition-normal);
            z-index: 1000;
            opacity: 0;
            transform: scale(0);
        `;
        
        fab.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        document.body.appendChild(fab);
        
        // Show/hide based on scroll
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                fab.style.opacity = '1';
                fab.style.transform = 'scale(1)';
            } else {
                fab.style.opacity = '0';
                fab.style.transform = 'scale(0)';
            }
        });
        
        return fab;
    }
    
    // Create FAB if needed
    if (document.querySelector('.product-card, .category-card')) {
        createFloatingActionButton();
    }

    // Enhanced performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData.loadEventEnd - perfData.loadEventStart < 1000) {
                    console.log('%c🚀 Fast loading detected!', 'color: #10b981; font-size: 14px; font-weight: bold;');
                }
            }, 1000);
        });
    }

    // Filter dropdown functionality
    const filterToggle = document.getElementById('filterToggle');
    const filterToggleMobile = document.getElementById('filterToggleMobile');
    const filterDropdown = document.getElementById('filterDropdown');
    const closeFilter = document.getElementById('closeFilter');
    
    // Function to handle filter toggle
    function toggleFilterDropdown(e) {
        e.stopPropagation();
        filterDropdown.classList.toggle('show');
        
        // Update button appearance
        const activeButton = filterDropdown.classList.contains('show') ? e.target.closest('button') : null;
        if (activeButton) {
            activeButton.classList.add('active');
            activeButton.style.background = 'var(--primary-blue)';
            activeButton.style.color = 'white';
        } else {
            // Reset both buttons
            if (filterToggle) {
                filterToggle.classList.remove('active');
                filterToggle.style.background = 'transparent';
                filterToggle.style.color = 'var(--primary-blue)';
            }
            if (filterToggleMobile) {
                filterToggleMobile.classList.remove('active');
                filterToggleMobile.style.background = 'transparent';
                filterToggleMobile.style.color = 'var(--primary-blue)';
            }
        }
        
        // Add overlay for mobile
        if (window.innerWidth <= 767 && filterDropdown.classList.contains('show')) {
            const overlay = document.createElement('div');
            overlay.className = 'filter-overlay';
            overlay.id = 'filterOverlay';
            document.body.appendChild(overlay);
            
            // Close filter when overlay is clicked
            overlay.addEventListener('click', function() {
                filterDropdown.classList.remove('show');
                document.body.removeChild(overlay);
                if (filterToggle) {
                    filterToggle.classList.remove('active');
                    filterToggle.style.background = 'transparent';
                    filterToggle.style.color = 'var(--primary-blue)';
                }
                if (filterToggleMobile) {
                    filterToggleMobile.classList.remove('active');
                    filterToggleMobile.style.background = 'transparent';
                    filterToggleMobile.style.color = 'var(--primary-blue)';
                }
            });
        }
    }
    
    // Function to close filter dropdown
    function closeFilterDropdown() {
        filterDropdown.classList.remove('show');
        if (filterToggle) {
            filterToggle.classList.remove('active');
            filterToggle.style.background = 'transparent';
            filterToggle.style.color = 'var(--primary-blue)';
        }
        if (filterToggleMobile) {
            filterToggleMobile.classList.remove('active');
            filterToggleMobile.style.background = 'transparent';
            filterToggleMobile.style.color = 'var(--primary-blue)';
        }
        
        // Remove overlay if exists
        const overlay = document.getElementById('filterOverlay');
        if (overlay) {
            document.body.removeChild(overlay);
        }
    }
    
    if (filterToggle && filterDropdown) {
        // Desktop filter toggle
        filterToggle.addEventListener('click', toggleFilterDropdown);
    }
    
    if (filterToggleMobile && filterDropdown) {
        // Mobile filter toggle
        filterToggleMobile.addEventListener('click', toggleFilterDropdown);
    }
    
    // Close filter dropdown when clicking close button
    if (closeFilter) {
        closeFilter.addEventListener('click', closeFilterDropdown);
    }
    
    // Close filter dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (filterDropdown && filterDropdown.classList.contains('show')) {
            const isFilterButton = (filterToggle && filterToggle.contains(e.target)) || 
                                 (filterToggleMobile && filterToggleMobile.contains(e.target));
            const isFilterDropdown = filterDropdown.contains(e.target);
            
            if (!isFilterButton && !isFilterDropdown) {
                closeFilterDropdown();
            }
        }
    });
    
    // Close filter dropdown on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && filterDropdown && filterDropdown.classList.contains('show')) {
            closeFilterDropdown();
        }
    });
    
    // Handle window resize for filter dropdown
    window.addEventListener('resize', function() {
        if (filterDropdown && filterDropdown.classList.contains('show')) {
            // Remove overlay on desktop
            if (window.innerWidth > 767) {
                const overlay = document.getElementById('filterOverlay');
                if (overlay) {
                    document.body.removeChild(overlay);
                }
            }
        }
    });

    // Console welcome message
    console.log('%c👟 Welcome to Jubair Boot House! 👟', 'color: #2563eb; font-size: 20px; font-weight: bold;');
    console.log('%cEnhanced with modern UI/UX and smooth animations', 'color: #6b7280; font-size: 14px;');
});

// Enhanced utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(price);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function animateElement(element, animation, duration = 1000) {
    element.style.animation = `${animation} ${duration}ms ease-out`;
    setTimeout(() => {
        element.style.animation = '';
    }, duration);
}

// Export functions for global use
window.formatPrice = formatPrice;
window.debounce = debounce;
window.animateElement = animateElement;

// Add CSS for enhanced animations
const enhancedStyles = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes fade-in {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .shake {
        animation: shake 0.5s ease-in-out;
    }
    
    .fade-in {
        animation: fade-in 0.5s ease-out;
    }
    
    .btn-loading {
        position: relative;
        overflow: hidden;
    }
    
    .btn-loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: loading-shine 1s infinite;
    }
    
    @keyframes loading-shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .floating-action-btn:hover {
        transform: scale(1.1) translateY(-2px);
        box-shadow: var(--shadow-xl);
    }
    
    .scroll-indicator {
        background: var(--bg-light);
        border-radius: var(--radius-lg);
        margin-bottom: 1rem;
        border: 1px solid var(--border-light);
    }
`;

// Inject enhanced styles
const styleSheet = document.createElement('style');
styleSheet.textContent = enhancedStyles;
document.head.appendChild(styleSheet);
