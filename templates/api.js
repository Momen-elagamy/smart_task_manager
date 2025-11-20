// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/**
 * A wrapper around the native fetch function that automatically adds
 * the CSRF token to the request headers for methods other than GET, HEAD, OPTIONS.
 * @param {string} url - The URL to fetch.
 * @param {object} options - The options for the fetch request.
 * @returns {Promise<Response>} - A promise that resolves to the response.
 */
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
        // By default, fetch sends cookies for same-origin requests.
        // Explicitly setting it to 'same-origin' ensures this behavior.
        credentials: 'same-origin', 
    };

    // For GET requests, we don't need CSRF token, but it doesn't hurt to send it.
    // Django's CsrfViewMiddleware doesn't check GET/HEAD/OPTIONS requests.

    try {
        const response = await fetch(url, mergedOptions);
        if (!response.ok) {
            // If the response is a redirect, it means the session might have expired.
            if (response.status === 302 || response.redirected) {
                 console.error(`API call to ${url} was redirected. Session might have expired. Please log in again.`);
                 // Optionally, redirect to login page
                 // window.location.href = '/login/';
                 throw new Error('Authentication session may have expired.');
            }
            // Try to parse error response from the server
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                throw new Error(`HTTP error! Status: ${response.status} while fetching ${url}. Failed to parse error JSON.`);
            }
            console.error(`API Error for ${url}:`, errorData);
            throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
        }
        // Handle cases where the server returns an empty body for success (e.g., 204 No Content)
        if (response.status === 204) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch API call failed:', error);
        throw error;
    }
}

// --- API Functions ---

/**
 * Fetches the user's profile data.
 */
async function getProfile() {
    return await apiFetch('/api/profile/');
}

/**
 * Fetches all tasks.
 */
async function getTasks() {
    // This is the call that was failing. Now it should work.
    return await apiFetch('/api/tasks/');
}

/**
 * Creates a new task.
 * @param {object} taskData - The data for the new task.
 */
async function createTask(taskData) {
    return await apiFetch('/api/tasks/', {
        method: 'POST',
        body: JSON.stringify(taskData),
    });
}

/**
 * Updates an existing task.
 * @param {number} taskId - The ID of the task to update.
 * @param {object} taskData - The updated data for the task.
 */
async function updateTask(taskId, taskData) {
    return await apiFetch(`/api/tasks/${taskId}/`, {
        method: 'PUT', // or 'PATCH'
        body: JSON.stringify(taskData),
    });
}

/**
 * Deletes a task.
 * @param {number} taskId - The ID of the task to delete.
 */
async function deleteTask(taskId) {
    return await apiFetch(`/api/tasks/${taskId}/`, {
        method: 'DELETE',
    });
}

/**
 * Fetches projects.
 */
async function getProjects() {
    const response = await apiFetch('/api/projects/');
    // If the response is paginated (like from Django REST Framework),
    // return the 'results' array. Otherwise, assume the response is the array itself.
    return response.results || response;
}

/**
 * Fetches stats.
 */
async function getStats() {
    return await apiFetch('/api/stats/');
}

// Example of how you might use these functions in your main.js
/*
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const tasks = await getTasks();
        console.log('Tasks loaded successfully:', tasks);
        // Now render the tasks on the page
    } catch (error) {
        console.error('Failed to load tasks:', error);
        // Display an error message to the user
    }
});
*/