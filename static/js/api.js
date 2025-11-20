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

const csrftoken = getCookie('csrftoken');

async function refreshAccessToken() {
    try {
        // Check if refresh token exists in localStorage or cookies
        let refreshToken = localStorage.getItem('refreshToken');
        
        // If not in localStorage, check cookies (remember me feature)
        if (!refreshToken) {
            refreshToken = getCookie('refresh_token');
        }
        
        if (!refreshToken) return null;
        
        const resp = await fetch('/api/users/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            credentials: 'same-origin',
            body: JSON.stringify({ refresh: refreshToken }),
        });
        if (!resp.ok) return null;
        const data = await resp.json();
        if (data && data.access) {
            localStorage.setItem('accessToken', data.access);
            return data.access;
        }
        return null;
    } catch (e) {
        return null;
    }
}

async function apiFetch(url, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
    };

    const mergedOptions = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
        credentials: 'same-origin',
    };

    // Attach JWT if available
    try {
        let accessToken = localStorage.getItem('accessToken');
        
        // If not in localStorage, check cookies (remember me feature)
        if (!accessToken) {
            accessToken = getCookie('access_token');
            if (accessToken) {
                // Store in localStorage for future requests
                localStorage.setItem('accessToken', accessToken);
            }
        }
        
        if (accessToken) {
            mergedOptions.headers['Authorization'] = `Bearer ${accessToken}`;
        }
    } catch (e) {
        // localStorage may be unavailable in some contexts; ignore
    }

    try {
        const response = await fetch(url, mergedOptions);
        if (!response.ok) {
            // Attempt silent refresh on 401 once
            if (response.status === 401 && !options._retried) {
                const newToken = await refreshAccessToken();
                if (newToken) {
                    const retryOptions = {
                        ...mergedOptions,
                        headers: {
                            ...mergedOptions.headers,
                            'Authorization': `Bearer ${newToken}`,
                        },
                    };
                    return await apiFetch(url, { ...retryOptions, _retried: true });
                } else {
                    // Clear tokens and bubble up a friendly message
                    try {
                        localStorage.removeItem('accessToken');
                        localStorage.removeItem('refreshToken');
                    } catch (e) {}
                    const err = new Error('Session expired. Please log in again.');
                    err.status = 401;
                    throw err;
                }
            }
            
            // Handle 403 Forbidden
            if (response.status === 403) {
                const err = new Error('Access denied. Please log in again.');
                err.status = 403;
                throw err;
            }
            
            if (response.status === 302 || response.redirected) {
                throw new Error('Authentication session may have expired.');
            }
            
            // Check if response is JSON before trying to parse
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                try {
                    const errorData = await response.json();
                    const err = new Error(errorData.detail || errorData.message || `HTTP error! Status: ${response.status}`);
                    err.status = response.status;
                    err.data = errorData;
                    throw err;
                } catch (jsonError) {
                    const err = new Error(`HTTP error! Status: ${response.status}`);
                    err.status = response.status;
                    throw err;
                }
            } else {
                // Response is not JSON (might be HTML error page)
                const text = await response.text();
                if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                    const err = new Error(`Server returned HTML instead of JSON. Status: ${response.status}. You may need to log in.`);
                    err.status = response.status;
                    throw err;
                }
                const err = new Error(`HTTP error! Status: ${response.status}`);
                err.status = response.status;
                throw err;
            }
        }
        
        if (response.status === 204) {
            return null;
        }
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            // If not JSON, return text or null
            const text = await response.text();
            if (text) {
                console.warn('Response is not JSON:', text);
                return { message: text };
            }
            return null;
        }
    } catch (error) {
        console.error('Fetch API call failed:', error);
        
        // If it's a 401 or session expired error, redirect to login
        if (error.status === 401 || (error.message && error.message.includes('Session expired'))) {
            // Clear all auth data
            try {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                sessionStorage.clear();
            } catch (e) {}
            
            // Redirect to login
            window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname + window.location.search);
        }
        
        throw error;
    }
}

// --- API Functions ---

// Profile
async function getProfile() {
    return await apiFetch('/api/users/profile/');
}

async function updateProfile(data) {
    // Allow partial updates via PATCH
    return await apiFetch('/api/users/profile/', {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

// Users - lightweight team endpoints
async function getUsersAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = '/api/team/members/' + (query ? `?${query}` : '');
    return await apiFetch(url);
}

async function createUser(user) {
    const payload = {
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        password: user.password,
        password2: user.confirm_password || user.password2 || user.password,
        role: user.role || 'client',
        department: user.department || null,
        // username is collected by the form but not used by backend auth model;
        // send for completeness but serializer will ignore it safely.
        username: user.username || '',
    };
    return await apiFetch('/api/users/register/', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

// Tasks (DRF router exposes under /api/tasks/tasks/)
async function getTasks() {
    return await apiFetch('/api/tasks/tasks/');
}

async function getTaskById(taskId) {
    return await apiFetch(`/api/tasks/tasks/${taskId}/`);
}

async function createTask(taskData) {
    return await apiFetch('/api/tasks/tasks/', {
        method: 'POST',
        body: JSON.stringify(taskData),
    });
}

async function updateTask(taskId, taskData) {
    return await apiFetch(`/api/tasks/tasks/${taskId}/`, {
        method: 'PUT',
        body: JSON.stringify(taskData),
    });
}

async function patchTask(taskId, taskData) {
    return await apiFetch(`/api/tasks/tasks/${taskId}/`, {
        method: 'PATCH',
        body: JSON.stringify(taskData),
    });
}

async function deleteTask(taskId) {
    return await apiFetch(`/api/tasks/tasks/${taskId}/`, {
        method: 'DELETE',
    });
}

// Projects (DRF router exposes under /api/projects/projects/)
async function getProjects() {
    const response = await apiFetch('/api/projects/projects/');
    return response.results || response;
}

async function getProjectById(projectId) {
    return await apiFetch(`/api/projects/projects/${projectId}/`);
}

async function createProject(projectData) {
    return await apiFetch('/api/projects/projects/', {
        method: 'POST',
        body: JSON.stringify(projectData),
    });
}

async function updateProject(projectId, projectData) {
    return await apiFetch(`/api/projects/projects/${projectId}/`, {
        method: 'PUT',
        body: JSON.stringify(projectData),
    });
}

async function patchProject(projectId, projectData) {
    return await apiFetch(`/api/projects/projects/${projectId}/`, {
        method: 'PATCH',
        body: JSON.stringify(projectData),
    });
}

async function deleteProject(projectId) {
    return await apiFetch(`/api/projects/projects/${projectId}/`, {
        method: 'DELETE',
    });
}

// Dashboard stats
async function getStats() {
    return await apiFetch('/api/dashboard/stats/');
}

// Recent activity
async function getRecentActivity() {
    return await apiFetch('/api/activity/recent/');
}

// Notifications
async function getNotifications(unreadOnly = false) {
    const params = unreadOnly ? '?unread=true' : '';
    return await apiFetch(`/api/notifications/${params}`);
}

async function getNotificationCount() {
    return await apiFetch('/api/notifications/count/');
}

async function markNotificationRead(notificationId) {
    return await apiFetch(`/api/notifications/${notificationId}/`, {
        method: 'PATCH',
    });
}

async function markAllNotificationsRead() {
    return await apiFetch('/api/notifications/mark-all-read/', {
        method: 'POST',
    });
}

// Global Search
async function globalSearch(query, type = 'all', limit = 5) {
    const params = new URLSearchParams({ q: query, type, limit }).toString();
    return await apiFetch(`/api/search/?${params}`);
}

// Namespaced global API for templates using window.API
window.API = {
    auth: {
        logout: async () => {
            try {
                await apiFetch('/api/users/logout/', { method: 'POST' });
            } catch (_) {
                // Ignore errors; frontend will clear tokens and redirect regardless
            }
        },
    },
    client: {
        clearTokens: () => {
            try {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
            } catch (_) {}
        }
    },
    users: {
        getProfile,
        update: updateProfile,
        getAll: getUsersAll,
        // Alias to prevent breakage if callers use a different name
        list: getUsersAll,
        create: createUser,
    },
    chat: {
        ensureDM: async (userId) => {
            const resp = await apiFetch('/api/chat/rooms/ensure_dm/', {
                method: 'POST',
                body: JSON.stringify({ user_id: userId }),
            });
            return resp; // { id, name, room_type }
        },
        getMessages: async (roomId) => {
            const qs = new URLSearchParams({ room: roomId }).toString();
            return await apiFetch(`/api/chat/messages/?${qs}`);
        },
        sendMessage: async (roomId, content) => {
            return await apiFetch('/api/chat/messages/', {
                method: 'POST',
                body: JSON.stringify({ room: roomId, content }),
            });
        },
        getRooms: async () => apiFetch('/api/chat/rooms/'),
    },
    tasks: {
        getAll: getTasks,
        getById: getTaskById,
        create: createTask,
        update: updateTask,
        patch: patchTask,
        delete: deleteTask,
    },
    projects: {
        getAll: getProjects,
        getById: getProjectById,
        create: createProject,
        update: updateProject,
        patch: patchProject,
        delete: deleteProject,
    },
    stats: {
        getStats,
        getRecentActivity,
    },
    notifications: {
        getAll: getNotifications,
        getCount: getNotificationCount,
        markRead: markNotificationRead,
        markAllRead: markAllNotificationsRead,
    },
    search: {
        global: globalSearch,
    },
};

// Dispatch event when API is ready
if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('apiReady'));
}
