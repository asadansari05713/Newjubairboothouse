// Admin Session Manager for Jubair Boot House
// Handles admin-specific session management and header updates

class AdminSessionManager {
    constructor() {
        this.sessionData = null;
        this.isInitialized = false;
        this.init();
    }

    async init() {
        console.log('Initializing AdminSessionManager...');
        
        // Check if we're on the login page
        this.isLoginPage = window.location.pathname === '/auth/login';
        
        // Hide navbar on login page
        if (this.isLoginPage) {
            this.hideNavbar();
        }
        
        // Check for existing session data in localStorage
        this.loadSessionFromStorage();
        
        // Update header based on stored session (immediate feedback)
        if (this.sessionData) {
            this.updateHeader();
        } else {
            this.showLoginState();
        }
        
        // Check current session status from server
        await this.checkSessionStatus();
        
        // Update header based on server response
        this.updateHeader();
        
        this.isInitialized = true;
        console.log('AdminSessionManager initialized');
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
            console.log('Checking admin session status...');
            const response = await fetch('/auth/session/status', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Session status response:', data);
                
                if (data.logged_in && data.user_type === 'admin') {
                    this.saveSessionToStorage(data);
                    return data;
                } else {
                    this.clearSessionFromStorage();
                    return null;
                }
            } else {
                console.log('Session check failed:', response.status);
                this.clearSessionFromStorage();
                return null;
            }
        } catch (error) {
            console.error('Error checking session status:', error);
            this.clearSessionFromStorage();
            return null;
        }
    }

    updateHeader() {
        const authSection = document.getElementById('adminAuthSection');
        const dashboardNav = document.getElementById('adminDashboardNav');
        
        if (!authSection) {
            console.log('Admin auth section not found');
            return;
        }

        if (this.sessionData && this.sessionData.logged_in && this.sessionData.user_type === 'admin') {
            console.log('Admin is logged in, showing profile dropdown');
            this.showAdminProfileDropdown(authSection);
            if (dashboardNav) {
                dashboardNav.style.display = 'block';
            }
            // Show navbar when admin is logged in
            if (!this.isLoginPage) {
                this.showNavbar();
            }
        } else {
            console.log('Admin is not logged in, showing login state');
            this.showLoginState(authSection);
            if (dashboardNav) {
                dashboardNav.style.display = 'none';
            }
            // Hide navbar on login page when not logged in
            if (this.isLoginPage) {
                this.hideNavbar();
            }
        }
    }

    hideNavbar() {
        const navbar = document.getElementById('adminNavbar');
        if (navbar) {
            navbar.style.display = 'none';
        }
    }

    showNavbar() {
        const navbar = document.getElementById('adminNavbar');
        if (navbar) {
            navbar.style.display = 'block';
        }
    }

    showLoginState(authSection) {
        if (!authSection) return;
        
        // For admin login page, don't show any login buttons
        // Just show a clean header
        authSection.innerHTML = '';
    }

    showAdminProfileDropdown(authSection) {
        const { username } = this.sessionData;
        
        authSection.innerHTML = `
            <div class="dropdown">
                <a class="btn btn-primary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-user-shield me-2"></i>${username}
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="/products/admin/dashboard">
                        <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                    </a></li>
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

        // Reinitialize dropdown functionality
        this.initializeBootstrapDropdowns();
    }

    initializeBootstrapDropdowns() {
        // Initialize Bootstrap dropdowns
        const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }

    // Public method to refresh session
    async refreshSession() {
        await this.checkSessionStatus();
        this.updateHeader();
    }

    // Public method to logout
    async logout() {
        try {
            const response = await fetch('/auth/logout', {
                method: 'GET',
                credentials: 'include'
            });
            
            this.clearSessionFromStorage();
            this.updateHeader();
            
            // Redirect to admin login page
            window.location.href = '/auth/login';
        } catch (error) {
            console.error('Error during logout:', error);
            // Still clear local session and redirect
            this.clearSessionFromStorage();
            this.updateHeader();
            window.location.href = '/auth/login';
        }
    }
}

// Initialize admin session manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminSessionManager = new AdminSessionManager();
});

// Export for use in other scripts
window.AdminSessionManager = AdminSessionManager;
