// Session Manager for Jubair Boot House
// Handles login state persistence and dynamic header updates

class SessionManager {
    constructor() {
        this.sessionData = null;
        this.isInitialized = false;
        this.init();
    }

    async init() {
        console.log('Initializing SessionManager...');
        
        // Check for existing session data in localStorage
        this.loadSessionFromStorage();
        
        // Update header based on stored session (immediate feedback)
        if (this.sessionData) {
            this.updateHeader();
            // Immediately update footer visibility
            this.updateFooterVisibility();
        } else {
            // Hide admin nav for non-logged in users
            this.hideAdminNav();
            // Show footer for non-logged in users
            this.showFooter();
        }
        
        // Check current session status from server
        await this.checkSessionStatus();
        
        // Update header based on server response
        this.updateHeader();
        
        // Set up periodic session checks
        this.setupPeriodicChecks();
        
        // Set up page refresh handling
        this.setupPageRefreshHandling();
        
        this.isInitialized = true;
        console.log('SessionManager initialized');
    }

    loadSessionFromStorage() {
        try {
            const stored = localStorage.getItem('jubair_session');
            if (stored) {
                this.sessionData = JSON.parse(stored);
                // Check if stored session is still valid (within 7 days)
                if (this.sessionData.timestamp) {
                    const age = Date.now() - this.sessionData.timestamp;
                    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
                    if (age > maxAge) {
                        localStorage.removeItem('jubair_session');
                        this.sessionData = null;
                    }
                }
            }
        } catch (error) {
            console.error('Error loading session from localStorage:', error);
            localStorage.removeItem('jubair_session');
            this.sessionData = null;
        }
    }

    saveSessionToStorage(sessionData) {
        try {
            const sessionToStore = {
                ...sessionData,
                timestamp: Date.now()
            };
            localStorage.setItem('jubair_session', JSON.stringify(sessionToStore));
            this.sessionData = sessionData;
        } catch (error) {
            console.error('Error saving session to localStorage:', error);
        }
    }

    clearSessionFromStorage() {
        try {
            localStorage.removeItem('jubair_session');
            this.sessionData = null;
        } catch (error) {
            console.error('Error clearing session from localStorage:', error);
        }
    }

    async checkSessionStatus() {
        try {
            console.log('Checking session status...');
            const response = await fetch('/auth/session/status', {
                method: 'GET',
                credentials: 'include', // Include cookies
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const sessionData = await response.json();
                console.log('Session status response:', sessionData);
                if (sessionData.logged_in) {
                    this.saveSessionToStorage(sessionData);
                    console.log('Session saved, updating header...');
                    this.updateHeader();
                } else {
                    this.clearSessionFromStorage();
                    console.log('Session cleared, updating header...');
                    this.updateHeader();
                }
            } else {
                console.log('Session status response not ok:', response.status);
                this.clearSessionFromStorage();
                console.log('Session cleared due to response error, updating header...');
                this.updateHeader();
            }
        } catch (error) {
            console.error('Error checking session status:', error);
            // Fall back to localStorage data if server is unreachable
            console.log('Using cached session data...');
            this.updateHeader();
        }
    }

    updateHeader() {
        const authSection = document.getElementById('authSection');
        const mobileAuthSection = document.getElementById('mobileAuthSection');
        
        if (!authSection && !mobileAuthSection) {
            console.log('Auth sections not found!');
            return;
        }

        console.log('Updating header with session data:', this.sessionData);
        
        if (this.sessionData && this.sessionData.logged_in) {
            console.log('User is logged in, showing profile dropdown...');
            // User is logged in - show profile dropdown
            if (authSection) this.showProfileDropdown(authSection);
            if (mobileAuthSection) this.showMobileProfileDropdown(mobileAuthSection);
            // Show admin nav item only for admin users
            this.updateAdminNavVisibility();
            // Update footer visibility based on user type
            this.updateFooterVisibility();
            // Update admin welcome box visibility
            this.updateAdminWelcomeBoxVisibility();
        } else {
            console.log('User is not logged in, showing login buttons...');
            // User is not logged in - show login buttons
            if (authSection) this.showLoginButtons(authSection);
            if (mobileAuthSection) this.showMobileLoginButtons(mobileAuthSection);
            // Hide admin nav item for non-logged in users
            this.hideAdminNav();
            // Show footer for non-logged in users
            this.showFooter();
            // Hide admin welcome box for non-logged in users
            this.updateAdminWelcomeBoxVisibility();
        }
    }

    showProfileDropdown(authSection) {
        const { user_type, username } = this.sessionData;
        
        // Debug logging
        console.log('Session data:', this.sessionData);
        console.log('User type:', user_type);
        console.log('Username:', username);
        console.log('Rendering profile dropdown for user type:', user_type);
        
        if (user_type === 'admin') {
            console.log('Rendering ADMIN dropdown with User Feedback option...');
            authSection.innerHTML = `
                <div class="dropdown">
                    <a class="nav-link admin-profile-btn dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-user-shield me-2"></i>${username}
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="/admin/users">
                            <i class="fas fa-users me-2"></i>User Data
                        </a></li>
                        <li><a class="dropdown-item" href="/admin/feedback">
                            <i class="fas fa-comments me-2"></i>User Feedback
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/auth/logout">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            `;
            console.log('Admin dropdown HTML rendered successfully');
        } else {
            authSection.innerHTML = `
                <div class="dropdown">
                    <a class="nav-link user-profile-btn dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-user me-2"></i>${username}
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="/auth/user/profile">
                            <i class="fas fa-user-circle me-2"></i>My Profile
                        </a></li>
                        <li><a class="dropdown-item" href="/auth/user/favourites">
                            <i class="fas fa-heart me-2"></i>My Favourites
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/auth/user/logout">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            `;
        }

        // Reinitialize dropdown functionality
        this.initializeBootstrapDropdowns();
    }

    showLoginButtons(authSection) {
        authSection.innerHTML = `
            <a class="nav-link admin-login-btn" href="/auth/login" title="Admin Login">
                <i class="fas fa-user-shield me-2"></i>Admin Login
            </a>
            
            <a class="nav-link user-login-btn" href="/auth/user/login" title="User Login">
                <i class="fas fa-user me-2"></i>User Login
            </a>
        `;
    }

    showMobileProfileDropdown(mobileAuthSection) {
        const { user_type, username } = this.sessionData;
        
        if (user_type === 'admin') {
            mobileAuthSection.innerHTML = `
                <div class="dropdown">
                    <a class="btn btn-primary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-user-shield me-2"></i>${username}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="/admin/users">
                            <i class="fas fa-users me-2"></i>User Data
                        </a></li>
                        <li><a class="dropdown-item" href="/admin/feedback">
                            <i class="fas fa-comments me-2"></i>User Feedback
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/auth/logout">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            `;
        } else {
            mobileAuthSection.innerHTML = `
                <div class="dropdown">
                    <a class="btn btn-primary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-user me-2"></i>${username}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="/auth/user/profile">
                            <i class="fas fa-user-circle me-2"></i>My Profile
                        </a></li>
                        <li><a class="dropdown-item" href="/auth/user/favourites">
                            <i class="fas fa-heart me-2"></i>My Favourites
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/auth/user/logout">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            `;
        }

        // Reinitialize dropdown functionality
        this.initializeBootstrapDropdowns();
    }

    showMobileLoginButtons(mobileAuthSection) {
        mobileAuthSection.innerHTML = `
            <a class="btn btn-outline-primary" href="/auth/login" title="Admin Login">
                <i class="fas fa-user-shield me-2"></i>Admin
            </a>
            
            <a class="btn btn-outline-primary" href="/auth/user/login" title="User Login">
                <i class="fas fa-user me-2"></i>User
            </a>
        `;
    }

    updateAdminNavVisibility() {
        const adminNavItem = document.getElementById('adminNavItem');
        const mobileAdminNavItem = document.getElementById('mobileAdminNavItem');
        
        if (adminNavItem) {
            if (this.sessionData && this.sessionData.user_type === 'admin') {
                adminNavItem.style.display = 'block';
            } else {
                adminNavItem.style.display = 'none';
            }
        }
        
        if (mobileAdminNavItem) {
            if (this.sessionData && this.sessionData.user_type === 'admin') {
                mobileAdminNavItem.style.display = 'block';
            } else {
                mobileAdminNavItem.style.display = 'none';
            }
        }
    }

    hideAdminNav() {
        const adminNavItem = document.getElementById('adminNavItem');
        const mobileAdminNavItem = document.getElementById('mobileAdminNavItem');
        
        if (adminNavItem) {
            adminNavItem.style.display = 'none';
        }
        
        if (mobileAdminNavItem) {
            mobileAdminNavItem.style.display = 'none';
        }
    }

    updateFooterVisibility() {
        const footer = document.getElementById('mainFooter');
        if (footer) {
            if (this.sessionData && this.sessionData.user_type === 'admin') {
                // Hide footer for admin users
                footer.style.display = 'none';
                document.body.classList.add('admin-mode');
                console.log('Footer hidden for admin user:', this.sessionData);
            } else {
                // Show footer for regular users
                footer.style.display = 'block';
                document.body.classList.remove('admin-mode');
                console.log('Footer shown for regular user:', this.sessionData);
            }
        } else {
            console.log('Footer element not found');
        }
    }

    updateAdminWelcomeBoxVisibility() {
        const adminWelcomeBox = document.getElementById('adminWelcomeBox');
        if (adminWelcomeBox) {
            if (this.sessionData && this.sessionData.user_type === 'admin') {
                // Show admin welcome box for admin users
                adminWelcomeBox.style.display = 'block';
                console.log('Admin welcome box shown for admin user:', this.sessionData);
            } else {
                // Hide admin welcome box for regular users
                adminWelcomeBox.style.display = 'none';
                console.log('Admin welcome box hidden for regular user:', this.sessionData);
            }
        } else {
            console.log('Admin welcome box element not found');
        }
    }

    showFooter() {
        const footer = document.getElementById('mainFooter');
        if (footer) {
            footer.style.display = 'block';
            console.log('Footer shown for non-logged in user');
        }
    }

    initializeBootstrapDropdowns() {
        // Initialize Bootstrap dropdowns properly
        const dropdownElements = document.querySelectorAll('.navbar-nav .dropdown');
        
        dropdownElements.forEach(dropdown => {
            const button = dropdown.querySelector('.dropdown-toggle');
            
            if (button) {
                // Create new Bootstrap Dropdown instance
                new bootstrap.Dropdown(button, {
                    autoClose: true,
                    boundary: 'viewport'
                });
            }
        });
    }

    setupPeriodicChecks() {
        // Check session status every 5 minutes
        setInterval(() => {
            this.checkSessionStatus();
        }, 5 * 60 * 1000);

        // Check session status when page becomes visible
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkSessionStatus();
            }
        });

        // Check session status when window gains focus
        window.addEventListener('focus', () => {
            this.checkSessionStatus();
        });
    }

    setupPageRefreshHandling() {
        // Handle page refresh/visibility changes
        window.addEventListener('beforeunload', () => {
            // Save current session state before page unload
            if (this.sessionData) {
                this.saveSessionToStorage(this.sessionData);
            }
        });
        
        // Handle page focus to refresh session
        window.addEventListener('focus', () => {
            if (this.isInitialized) {
                this.checkSessionStatus();
            }
        });
        
        // Handle online/offline status
        window.addEventListener('online', () => {
            console.log('Browser came online, checking session...');
            this.checkSessionStatus();
        });
        
        window.addEventListener('offline', () => {
            console.log('Browser went offline, using cached session');
        });
    }

    // Public methods for external use
    getSessionData() {
        return this.sessionData;
    }

    isLoggedIn() {
        return this.sessionData && this.sessionData.logged_in;
    }

    getUserType() {
        return this.sessionData ? this.sessionData.user_type : null;
    }

    async logout() {
        try {
            const logoutUrl = this.sessionData?.user_type === 'admin' ? '/auth/logout' : '/auth/user/logout';
            await fetch(logoutUrl, { credentials: 'include' });
        } catch (error) {
            console.error('Error during logout:', error);
        } finally {
            this.clearSessionFromStorage();
            this.updateHeader();
            // Hide admin nav when logging out
            this.hideAdminNav();
            // Show footer when logging out
            this.showFooter();
            // Redirect to home page
            window.location.href = '/';
        }
    }
}

// Initialize session manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.sessionManager = new SessionManager();
    
    // Force footer visibility check after a short delay
    setTimeout(() => {
        if (window.sessionManager) {
            console.log('Forcing footer visibility check...');
            window.sessionManager.updateFooterVisibility();
        }
    }, 200);
    
    // Check session status after a short delay to ensure everything is loaded
    setTimeout(() => {
        window.sessionManager.checkSessionStatus();
    }, 100);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
}
