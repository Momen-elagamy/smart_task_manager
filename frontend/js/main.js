// Smart Task Manager - Enhanced Main JavaScript

// Global App State
const AppState = {
    isLoading: false,
    currentUser: null, // Will be populated after authentication
    notifications: [],
    theme: localStorage.getItem('theme') || 'dark',
    sidebarCollapsed: localStorage.getItem('sidebarCollapsed') === 'true'
};

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Smart Task Manager...');
    
    // First, check authentication. If not authenticated, stop further execution.
    if (!checkAuthentication()) {
        return; // Stop initialization if user is not authenticated and will be redirected.
    }
    
    // If authenticated, proceed with initializing the rest of the app.
    initializeTheme();
    initializeSidebar();
    setupEventListeners();
    setupInteractiveBackground();
    
    // Load user data if authenticated
    // Note: window.API doesn't have a client.isAuthenticated() method
    // Check if API is available and user has token
    if (window.API && localStorage.getItem('accessToken')) {
        loadCurrentUser(); // Load user data without blocking the main thread
    }
    
    console.log('App initialized successfully');
});

// --- INITIALIZATION FUNCTIONS ---

// Setup global event listeners
function setupEventListeners() {
    // Modal close on outside click
    document.addEventListener('click', handleModalOutsideClick);
    
    // Modal close on escape key
    document.addEventListener('keydown', handleEscapeKey);
    
    // Handle navigation links
    setupNavigationHandlers();
    
    // Setup form validation
    setupFormValidation();
    
    // Handle online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
    
    // Handle visibility change for auto-refresh
    document.addEventListener('visibilitychange', handleVisibilityChange);
}

// Initialize theme
function initializeTheme() {
    document.body.classList.toggle('dark-theme', AppState.theme === 'dark');
    document.body.classList.toggle('light-theme', AppState.theme === 'light');
}

// Initialize sidebar state
function initializeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar && AppState.sidebarCollapsed) {
        sidebar.classList.add('collapsed');
    }
}

// Setup interactive background
function setupInteractiveBackground() {
    const throttledMove = throttle((e) => {
        document.body.style.setProperty('--mouse-x', `${e.clientX}px`);
        document.body.style.setProperty('--mouse-y', `${e.clientY}px`);
    }, 100); // Optimize mousemove event

    document.addEventListener('mousemove', throttledMove);
}

// Setup navigation handlers
function setupNavigationHandlers() {
    // Add active class to current page nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Setup form validation
function setupFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

// --- AUTHENTICATION FUNCTIONS ---

// Check authentication
function checkAuthentication() {
    const token = localStorage.getItem('accessToken');
    const currentPath = window.location.pathname;
    const publicPages = ['/login/', '/register/', '/forgot-password/', '/'];
    
    if (!token && !publicPages.includes(currentPath)) {
        // Redirect immediately without waiting
        window.location.href = `/login/?next=${currentPath}`;
        return false;
    }
    
    // Check token expiration using the stored expiration time for faster initial check
    const tokenExp = localStorage.getItem('accessTokenExp');
    if (token && tokenExp) { // Check if token and its expiration are present
        const now = Date.now() / 1000;
        if (parseFloat(tokenExp) < now) { // Compare current time with expiration time
            handleSessionExpired(); // Handle expired token
            return false; // Token is expired, so authentication fails
        }
    }
    
    return true;
}

// Load current user data
async function loadCurrentUser() {
    try {
        if (!window.API || !window.API.profile) {
            console.warn('API not available for loading user profile');
            return;
        }
        const user = await window.API.profile.get();
        AppState.currentUser = user;
        updateUserUI(user);
    } catch (error) {
        console.error('Failed to load user:', error);
        if (error.status === 401 || error.status === 403) {
            // Don't redirect on profile load failure, just log it
            console.warn('User profile load failed - authentication issue');
        }
    }
}

// Update user UI elements
function updateUserUI(user) {
    // Update user name displays
    document.querySelectorAll('.user-name').forEach(el => {
        el.textContent = user.name || user.email;
    });
    
    // Update user email displays
    document.querySelectorAll('.user-email').forEach(el => {
        el.textContent = user.email;
    });
    
    // Update profile pictures
    document.querySelectorAll('.user-avatar').forEach(el => {
        if (user.profile_picture) {
            el.src = user.profile_picture;
        } else {
            el.src = getDefaultAvatar(user.name || user.email);
        }
    });
}

// Handle session expired
function handleSessionExpired() {
    showToast('Your session has expired. Please login again.', 'error');
    logout();
}

// Logout handler
async function handleLogout(event) {
    if (event) event.preventDefault();
    
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }
    
    logout();
}

// Logout function
async function logout() {
    showLoadingOverlay('Logging out...');
    
    try {
        if (window.API) {
            await window.API.auth.logout();
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        
        if (window.API) {
            window.API.client.clearTokens();
        }
        
        hideLoadingOverlay();
        window.location.href = '/login/';
    }
}

// --- MODAL FUNCTIONS ---

// Open modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) {
        console.warn(`Modal with id "${modalId}" not found`);
        return;
    }
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Focus first input
    setTimeout(() => {
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) firstInput.focus();
    }, 100);
    
    // Dispatch custom event
    modal.dispatchEvent(new CustomEvent('modalOpened'));
}

// Close modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.classList.remove('active');
    document.body.style.overflow = '';
    
    // Reset form if exists
    const form = modal.querySelector('form');
    if (form && !modal.classList.contains('no-reset')) {
        form.reset();
    }
    
    // Dispatch custom event
    modal.dispatchEvent(new CustomEvent('modalClosed'));
}

// Close all modals
function closeAllModals() {
    document.querySelectorAll('.modal.active').forEach(modal => {
        closeModal(modal.id);
    });
}

// Handle modal outside click
function handleModalOutsideClick(e) {
    if (e.target.classList.contains('modal') && e.target.classList.contains('active')) {
        closeModal(e.target.id);
    }
}

// Handle escape key
function handleEscapeKey(e) {
    if (e.key === 'Escape') {
        closeAllModals();
    }
}

// --- NOTIFICATION FUNCTIONS ---

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
    // Limit the number of toasts to prevent DOM overload
    if (document.querySelectorAll('.toast').length > 5) {
        console.warn('Too many toasts, skipping new one.');
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Create icon based on type
    const icon = getToastIcon(type);
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${escapeHtml(message)}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Apply styles
    const styles = {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '16px 20px',
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        zIndex: '10000',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        minWidth: '300px',
        maxWidth: '500px',
        animation: 'slideInRight 0.3s ease',
        color: 'white'
    };
    
    const typeColors = {
        success: 'rgba(16, 185, 129, 0.9)',
        error: 'rgba(239, 68, 68, 0.9)',
        warning: 'rgba(245, 158, 11, 0.9)',
        info: 'rgba(6, 182, 212, 0.9)'
    };
    
    styles.background = typeColors[type] || typeColors.info;
    Object.assign(toast.style, styles);
    
    // Add to DOM
    document.body.appendChild(toast);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    return toast;
}

// Get toast icon based on type
function getToastIcon(type) {
    const icons = {
        success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
        error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
    };
    return icons[type] || icons.info;
}

// Show notification (alias for showToast)
function showNotification(message, type = 'info') {
    return showToast(message, type);
}

// --- LOADING FUNCTIONS ---

// Show loading overlay
function showLoadingOverlay(message = 'Loading...') {
    let overlay = document.getElementById('loading-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner-container">
                <div class="loading-spinner"></div>
                <p class="loading-message">${escapeHtml(message)}</p>
            </div>
        `;
        
        const styles = {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            background: 'rgba(0, 0, 0, 0.6)', // Removed expensive blur
            // backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: '9999'
        };
        
        Object.assign(overlay.style, styles);
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.loading-message').textContent = message;
        overlay.style.display = 'flex';
    }
    
    AppState.isLoading = true;
}

// Hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    AppState.isLoading = false;
}

// Show button loading state
function setButtonLoading(button, loading = true, originalText = null) {
    if (loading) {
        button.dataset.originalText = originalText || button.textContent;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-small"></span> Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || 'Submit';
        delete button.dataset.originalText;
    }
}

// --- UTILITY FUNCTIONS ---

// Format date
function formatDate(dateString, format = 'short') {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        
        if (format === 'short') {
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        } else if (format === 'long') {
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } else if (format === 'relative') {
            return getRelativeTime(date);
        }
        
        return date.toLocaleDateString();
    } catch (e) {
        return 'N/A';
    }
}

// Get relative time (e.g., "2 hours ago")
function getRelativeTime(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) return 'just now';
    if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
    
    return formatDate(date, 'short');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || typeof text === 'undefined') return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Debounce function
function debounce(func, wait = 300) {
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

// Throttle function
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success', 2000);
        return true;
    } catch (error) {
        console.error('Failed to copy:', error);
        showToast('Failed to copy to clipboard', 'error');
        return false;
    }
}

// Download file
function downloadFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Get default avatar URL
function getDefaultAvatar(name) {
    const initial = name ? name.charAt(0).toUpperCase() : '?';
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=06b6d4&color=fff&size=128`;
}

// Validate email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate password strength
function validatePasswordStrength(password) {
    const minLength = password.length >= 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    const strength = [minLength, hasUpper, hasLower, hasNumber, hasSpecial].filter(Boolean).length;
    
    return {
        isValid: strength >= 3 && minLength,
        strength: strength,
        message: strength < 3 ? 'Password is too weak' : 
                 strength === 3 ? 'Password strength: Medium' :
                 strength === 4 ? 'Password strength: Strong' :
                 'Password strength: Very Strong'
    };
}

// --- FORM HANDLING ---

// Handle form submit
function handleFormSubmit(e) {
    const form = e.target;
    
    // Validate form
    if (!form.checkValidity()) {
        e.preventDefault();
        showToast('Please fill in all required fields', 'error');
        return;
    }
}

// Get form data as object
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        // Handle multiple values (checkboxes, multiple selects)
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

// --- EVENT HANDLERS ---

let lastToastType = null;

// Handle online status
function handleOnlineStatus() {
    if (lastToastType !== 'online') {
        showToast('Connection restored', 'success', 2000);
        lastToastType = 'online';
    }
}

// Handle offline status
function handleOfflineStatus() {
    if (lastToastType !== 'offline') {
        showToast('You are offline', 'warning', 0);
        lastToastType = 'offline';
    }
}

// Handle visibility change
function handleVisibilityChange() {
    if (document.hidden) {
        console.log('Page hidden');
    } else {
        console.log('Page visible');
        // Refresh data if needed
        if (window.API && window.API.client.isAuthenticated()) {
            // Optionally refresh user data or notifications
        }
    }
}

// --- SIDEBAR FUNCTIONS ---

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    
    sidebar.classList.toggle('collapsed');
    AppState.sidebarCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', AppState.sidebarCollapsed);
}

// --- THEME FUNCTIONS ---

// Toggle theme
function toggleTheme() {
    AppState.theme = AppState.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', AppState.theme);
    initializeTheme();
    showToast(`Switched to ${AppState.theme} theme`, 'success', 2000);
}

// --- EXPORT FUNCTIONS ---

// Make functions globally available
window.AppState = AppState;
window.openModal = openModal;
window.closeModal = closeModal;
window.closeAllModals = closeAllModals;
window.handleLogout = handleLogout;
window.logout = logout;
window.showToast = showToast;
window.showNotification = showNotification;
window.showLoadingOverlay = showLoadingOverlay;
window.hideLoadingOverlay = hideLoadingOverlay;
window.setButtonLoading = setButtonLoading;
window.formatDate = formatDate;
window.getRelativeTime = getRelativeTime;
window.escapeHtml = escapeHtml;
window.debounce = debounce;
window.throttle = throttle;
window.copyToClipboard = copyToClipboard;
window.downloadFile = downloadFile;
window.getDefaultAvatar = getDefaultAvatar;
window.isValidEmail = isValidEmail;
window.validatePasswordStrength = validatePasswordStrength;
window.getFormData = getFormData;
window.toggleSidebar = toggleSidebar;
window.toggleTheme = toggleTheme;
window.checkAuthentication = checkAuthentication;
window.loadCurrentUser = loadCurrentUser;

// Add CSS animations if not exist
if (!document.getElementById('app-animations')) {
    const style = document.createElement('style');
    style.id = 'app-animations';
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100px); opacity: 0; }
        }
        .toast-close {
            background: transparent;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        .toast-close:hover {
            opacity: 1;
        }
        .spinner-small {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        .loading-spinner-container {
            text-align: center;
            color: white;
        }
        .loading-message {
            margin-top: 20px;
            font-size: 16px;
        }
    `;
    document.head.appendChild(style);
}

console.log('Main JavaScript loaded successfully');