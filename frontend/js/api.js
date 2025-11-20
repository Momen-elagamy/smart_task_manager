// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Unified API Client with support for both CSRF and Bearer token authentication
 */
const API = {
    baseURL: '',
    
    /**
     * Get authentication headers
     */
    getHeaders(options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Try Bearer token first (for JWT)
        const accessToken = localStorage.getItem('accessToken');
        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        } else {
            // Fall back to CSRF token (for session-based auth)
            const csrftoken = getCookie('csrftoken');
            if (csrftoken) {
                headers['X-CSRFToken'] = csrftoken;
            }
        }
        
        return headers;
    },
    
    /**
     * Refresh access token if expired
     */
    async refreshToken() {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) return false;
        
        try {
            const response = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('accessToken', data.access);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    },
    
    /**
     * Main API request function
     */
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
        const headers = this.getHeaders(options);
        
        const config = {
            ...options,
            headers,
            credentials: 'same-origin'
        };
        
        // Add body if provided
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            config.body = JSON.stringify(options.body);
        } else if (options.body) {
            config.body = options.body;
        }
        
        try {
            let response = await fetch(url, config);
            
            // Handle 401 Unauthorized - try to refresh token
            if (response.status === 401 && localStorage.getItem('refreshToken')) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry with new token
                    headers['Authorization'] = `Bearer ${localStorage.getItem('accessToken')}`;
                    response = await fetch(url, { ...config, headers });
                } else {
                    // Token refresh failed - redirect to login
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    window.location.href = '/login/';
                    throw new Error('Session expired');
                }
            }
            
            // Handle redirects (session expired)
            if (response.status === 302 || response.redirected) {
                console.error(`API call to ${url} was redirected. Session might have expired.`);
                window.location.href = '/login/';
                throw new Error('Authentication session may have expired.');
            }
            
            // Handle errors
            if (!response.ok) {
                // Handle 403 Forbidden - authentication issue
                if (response.status === 403) {
                    console.error(`❌ API Error: 403 ${url} - Access forbidden. Check authentication.`);
                    // Don't redirect on 403, let the calling code handle it
                    const errorData = await response.json().catch(() => ({}));
                    const error = new Error(errorData.detail || errorData.message || 'Access forbidden');
                    error.status = 403;
                    error.response = response;
                    throw error;
                }
                
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    const error = new Error(`HTTP error! Status: ${response.status} while fetching ${url}`);
                    error.status = response.status;
                    error.response = response;
                    throw error;
                }
                console.error(`❌ API Error: ${response.status} ${url}`, errorData);
                const error = new Error(errorData.detail || errorData.message || `HTTP error! Status: ${response.status}`);
                error.status = response.status;
                error.response = response;
                error.data = errorData;
                throw error;
            }
            
            // Handle empty responses (204 No Content)
            if (response.status === 204) {
                return null;
            }
            
            // Parse and return JSON
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // Tasks API
    tasks: {
        async getAll() {
            return await API.request('/api/tasks/');
        },
        async getById(id) {
            return await API.request(`/api/tasks/${id}/`);
        },
        async create(data) {
            return await API.request('/api/tasks/', {
                method: 'POST',
                body: data
            });
        },
        async update(id, data) {
            return await API.request(`/api/tasks/${id}/`, {
                method: 'PUT',
                body: data
            });
        },
        async patch(id, data) {
            return await API.request(`/api/tasks/${id}/`, {
                method: 'PATCH',
                body: data
            });
        },
        async delete(id) {
            return await API.request(`/api/tasks/${id}/`, {
                method: 'DELETE'
            });
        }
    },
    
    // Projects API
    projects: {
        async getAll() {
            return await API.request('/api/projects/');
        },
        async getById(id) {
            return await API.request(`/api/projects/${id}/`);
        },
        async create(data) {
            return await API.request('/api/projects/', {
                method: 'POST',
                body: data
            });
        },
        async update(id, data) {
            return await API.request(`/api/projects/${id}/`, {
                method: 'PUT',
                body: data
            });
        },
        async delete(id) {
            return await API.request(`/api/projects/${id}/`, {
                method: 'DELETE'
            });
        }
    },
    
    // Stats API
    stats: {
        async getStats() {
            return await API.request('/api/dashboard/stats/');
        }
    },
    
    // Profile API
    profile: {
        async get() {
            return await API.request('/api/profile/');
        }
    }
};

// Legacy function exports for backward compatibility
async function getTasks() {
    return await API.tasks.getAll();
}

async function createTask(taskData) {
    return await API.tasks.create(taskData);
}

async function updateTask(taskId, taskData) {
    return await API.tasks.patch(taskId, taskData);
}

async function deleteTask(taskId) {
    return await API.tasks.delete(taskId);
}

async function getProjects() {
    return await API.projects.getAll();
}

async function getStats() {
    return await API.stats.getStats();
}

async function getProfile() {
    return await API.profile.get();
}

// Make API available globally
window.API = API;
window.getTasks = getTasks;
window.createTask = createTask;
window.updateTask = updateTask;
window.deleteTask = deleteTask;
window.getProjects = getProjects;
window.getStats = getStats;
window.getProfile = getProfile;

// Log API initialization
if (typeof window !== 'undefined') {
    console.log('✅ API client initialized', {
        hasAPI: typeof window.API !== 'undefined',
        hasProjects: typeof window.API?.projects !== 'undefined',
        hasTasks: typeof window.API?.tasks !== 'undefined',
        hasStats: typeof window.API?.stats !== 'undefined',
        hasProfile: typeof window.API?.profile !== 'undefined'
    });
    
    // Dispatch custom event when API is ready
    window.dispatchEvent(new CustomEvent('apiReady', { detail: { API: window.API } }));
}
