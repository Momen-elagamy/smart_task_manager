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
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) return null;
    try {
        const resp = await fetch('/api/users/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        if (!resp.ok) return null;
        const data = await resp.json();
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            return data.access;
        }
    } catch (_) {}
    return null;
}

async function apiFetch(url, options = {}) {
    // Normalize URL: if caller passed a relative path like 'rooms/'
    // convert it to an absolute path so fetch does not resolve it
    // relative to the current HTML path (which caused 404s returning HTML).
    function resolveApiUrl(u){
        if (!u) return u;
        // Already absolute
        if (/^https?:\/\//i.test(u)) return u;
        // Leading slash -> absolute to origin
        if (u.startsWith('/')) return u;
        // Otherwise treat as root-relative
        try{
            return new URL('/' + u.replace(/^\/+/, ''), window.location.origin).toString();
        }catch(e){
            return '/' + u.replace(/^\/+/, '');
        }
    }
    const originalUrl = url;
    url = resolveApiUrl(url);
    if (originalUrl && !originalUrl.startsWith('/') && !/^https?:\/\//i.test(originalUrl)) {
        console.warn('apiFetch: converted relative URL to absolute:', originalUrl, '->', url);
    }
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
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
        mergedOptions.headers['Authorization'] = `Bearer ${accessToken}`;
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
                    const err = new Error('Token expired. Please log in again.');
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
                        // If this was a short/relative URL (e.g. 'rooms/') try a safe retry
                        // by prefixing the chat API base. This covers cached scripts or
                        // service-workers calling relative endpoints.
                        if (!url.includes('/chat/api/') && originalUrl) {
                            try{
                                const alt = originalUrl.startsWith('/') ? '/chat/api' + originalUrl : '/chat/api/' + originalUrl.replace(/^\/+/, '');
                                console.warn('apiFetch: detected HTML error on', url, 'attempting fallback to', alt);
                                const retryResp = await fetch(alt, mergedOptions);
                                if (retryResp.ok) {
                                    const ct = retryResp.headers.get('content-type') || '';
                                    if (ct.includes('application/json')) return await retryResp.json();
                                    const t2 = await retryResp.text();
                                    return { message: t2 };
                                }
                            }catch(retryErr){
                                console.warn('apiFetch fallback failed', retryErr);
                            }
                        }
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
        
        // If it's a 401 or explicit token expiry, redirect to login
        if (error.status === 401 || (error.message && (error.message.includes('Token expired') || error.message.includes('Invalid token')))) {
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
        password: user.password
    };
    return await apiFetch('/api/users/register/', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

// Auth (JWT based)
async function login(email, password) {
    const resp = await apiFetch('/api/users/login/', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
    if (resp && resp.access && resp.refresh) {
        localStorage.setItem('accessToken', resp.access);
        localStorage.setItem('refreshToken', resp.refresh);
    }
    return resp;
}

function logout() {
    try {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    } catch(_) {}
    window.location.href = '/login/';
}

// Tasks (DRF router exposes under /api/tasks/tasks/)
async function getTasks() {
    return await apiFetch('/tasks/api/tasks/');
}

async function getTaskById(taskId) {
    return await apiFetch(`/tasks/api/tasks/${taskId}/`);
}

async function createTask(taskData) {
    return await apiFetch('/tasks/api/tasks/', {
        method: 'POST',
        body: JSON.stringify(taskData),
    });
}

async function updateTask(taskId, taskData) {
    return await apiFetch(`/tasks/api/tasks/${taskId}/`, {
        method: 'PUT',
        body: JSON.stringify(taskData),
    });
}

async function patchTask(taskId, taskData) {
    return await apiFetch(`/tasks/api/tasks/${taskId}/`, {
        method: 'PATCH',
        body: JSON.stringify(taskData),
    });
}

async function deleteTask(taskId) {
    return await apiFetch(`/tasks/api/tasks/${taskId}/`, {
        method: 'DELETE',
    });
}

// Projects (DRF router exposes under /api/projects/projects/)
async function getProjects() {
    const response = await apiFetch('/projects/api/projects/');
    return response.results || response;
}

async function getProjectById(projectId) {
    return await apiFetch(`/projects/api/projects/${projectId}/`);
}

async function createProject(projectData) {
    return await apiFetch('/projects/api/projects/', {
        method: 'POST',
        body: JSON.stringify(projectData),
    });
}

async function updateProject(projectId, projectData) {
    return await apiFetch(`/projects/api/projects/${projectId}/`, {
        method: 'PUT',
        body: JSON.stringify(projectData),
    });
}

async function patchProject(projectId, projectData) {
    return await apiFetch(`/projects/api/projects/${projectId}/`, {
        method: 'PATCH',
        body: JSON.stringify(projectData),
    });
}

async function deleteProject(projectId) {
    return await apiFetch(`/projects/api/projects/${projectId}/`, {
        method: 'DELETE',
    });
}

// Dashboard stats
async function getStats() {
    return await apiFetch('/dashboard/stats/');
}

// Recent activity
async function getRecentActivity() {
    return await apiFetch('/api/activity/recent/');
}

// Notifications
async function getNotifications(unreadOnly = false) {
    const params = unreadOnly ? '?unread=true' : '';
    return await apiFetch(`/notifications/${params}`);
}

async function getNotificationCount() {
    return await apiFetch('/notifications/count/');
}

async function markNotificationRead(notificationId) {
    // Backend view expects POST to mark as read
    return await apiFetch(`/notifications/${notificationId}/`, {
        method: 'POST',
    });
}

async function markAllNotificationsRead() {
    return await apiFetch('/notifications/mark-all-read/', {
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
            const resp = await apiFetch('/chat/api/rooms/ensure_dm/', {
                method: 'POST',
                body: JSON.stringify({ user_id: userId }),
            });
            return resp; // { id, name, room_type }
        },
        getMessages: async (roomId) => {
            const qs = new URLSearchParams({ room: roomId }).toString();
            return await apiFetch(`/chat/api/messages/?${qs}`);
        },
        sendMessage: async (roomId, content) => {
            return await apiFetch('/chat/api/messages/', {
                method: 'POST',
                body: JSON.stringify({ room: roomId, content }),
            });
        },
        getRooms: async () => apiFetch('/chat/api/rooms/'),
        createRoom: async (payload) => apiFetch('/chat/api/rooms/', { method: 'POST', body: JSON.stringify(payload) }),
        addMembers: async (roomId, members) => apiFetch(`/chat/api/rooms/${roomId}/add_members/`, {
            method: 'POST',
            body: JSON.stringify({ members }),
        }),
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
