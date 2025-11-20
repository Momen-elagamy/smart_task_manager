<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tasks - Loop AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-primary: #0a0e27; --bg-secondary: #151933; --bg-tertiary: #1e2139;
            --text-primary: #ffffff; --text-secondary: #a0aec0; --text-muted: #718096;
            --border: #2d3548; --accent-cyan: #06b6d4; --accent-pink: #ec4899;
            --accent-green: #10b981; --accent-orange: #f59e0b; --accent-red: #ef4444;
            --accent-purple: #8b5cf6; --hover: #252a41;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0a0e27, #1a1f3a, #0f1429, #2c1a3a);
            background-size: 400% 400%; background-attachment: fixed; color: var(--text-primary);
            line-height: 1.6; overflow-x: hidden; position: relative;
            animation: gradientBG 15s ease infinite;
        }
        body::before {
            content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(6, 182, 212, 0.15) 0%, transparent 40%),
                        radial-gradient(circle at 20% 80%, rgba(236, 72, 153, 0.2) 0%, transparent 50%),
                        radial-gradient(circle at 80% 30%, rgba(16, 185, 129, 0.15) 0%, transparent 50%);
            animation: float 30s ease-in-out infinite; pointer-events: none; z-index: 0;
        }
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes float { 0%, 100% { transform: translate(0, 0) rotate(0deg); opacity: 0.8; } 25% { transform: translate(40px, -60px) rotate(45deg); opacity: 1; } 50% { transform: translate(-30px, 30px) rotate(90deg); opacity: 0.7; } 75% { transform: translate(60px, 40px) rotate(135deg); opacity: 1; } }
        .dashboard-container { display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%); border-right: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2); display: flex; flex-direction: column; position: fixed; height: 100vh; overflow-y: auto; z-index: 100; }
        .sidebar-header { padding: 24px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .logo { display: flex; align-items: center; gap: 12px; }
        .logo-icon { width: 40px; height: 40px; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-pink)); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(6, 182, 212, 0.3); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 18px; color: white; }
        .logo-text { font-size: 20px; font-weight: 700; color: var(--text-primary); }
        .sidebar-nav { flex: 1; padding: 20px 16px; }
        .nav-section { margin-bottom: 32px; }
        .nav-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; padding: 0 12px; margin-bottom: 8px; display: block; }
        .nav-link { display: flex; align-items: center; gap: 12px; padding: 12px; margin: 4px 0; border-radius: 10px; color: var(--text-secondary); text-decoration: none; font-size: 15px; font-weight: 500; transition: all 0.2s; position: relative; }
        .nav-link:hover { background: rgba(6, 182, 212, 0.1); color: var(--text-primary); }
        .nav-link.active { background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(236, 72, 153, 0.3)); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); color: white; box-shadow: 0 8px 32px rgba(6, 182, 212, 0.3); }
        .nav-icon { width: 20px; height: 20px; stroke-width: 2; }
        .sidebar-footer { padding: 16px; border-top: 1px solid rgba(255, 255, 255, 0.1); }
        .logout-btn { margin: 0 !important; }
        .main-content { margin-left: 280px; flex: 1; padding: 32px; background: transparent; position: relative; z-index: 1; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
        .header-left h1 { font-size: 28px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
        .header-left p { color: var(--text-secondary); font-size: 14px; }
        .header-right { display: flex; gap: 12px; align-items: center; }
        .icon-button { width: 44px; height: 44px; border: 1px solid rgba(255, 255, 255, 0.3); background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(5px); border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 20px rgba(31, 38, 135, 0.2); }
        .icon-button:hover { background: rgba(6, 182, 212, 0.2); border-color: rgba(6, 182, 212, 0.3); box-shadow: 0 8px 32px rgba(6, 182, 212, 0.2); }
        .icon-button svg { width: 20px; height: 20px; color: var(--text-secondary); }
        .primary-button { padding: 12px 20px; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-pink)); color: white; box-shadow: 0 8px 32px rgba(6, 182, 212, 0.3); }
        .primary-button:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(6, 182, 212, 0.4); }
        .primary-button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .primary-button svg { width: 18px; height: 18px; }
        .filter-tabs { display: flex; gap: 12px; margin-bottom: 32px; padding: 8px; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); overflow-x: auto; }
        .tab { padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 500; color: var(--text-muted); cursor: pointer; transition: all 0.2s; border: none; background: transparent; white-space: nowrap; }
        .tab:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-primary); }
        .tab.active { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-pink)); color: white; box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3); }
        .tasks-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 24px; }
        .task-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2); padding: 24px; transition: all 0.3s; animation: fadeInUp 0.5s ease; }
        .task-card:hover { transform: translateY(-4px); border-color: var(--accent-cyan); box-shadow: 0 12px 32px rgba(6, 182, 212, 0.2); }
        .task-card.completed { opacity: 0.7; border-color: var(--accent-green); }
        .task-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; gap: 12px; }
        .task-title { font-size: 18px; font-weight: 600; color: var(--text-primary); flex: 1; word-break: break-word; }
        .task-priority { padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; }
        .priority-high { background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }
        .priority-medium { background: rgba(245, 158, 11, 0.2); color: var(--accent-orange); }
        .priority-low { background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); }
        .task-description { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; word-break: break-word; }
        .task-meta { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.1); }
        .task-meta span { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted); }
        .task-meta svg { width: 16px; height: 16px; flex-shrink: 0; }
        .task-footer { display: flex; gap: 8px; }
        .task-actions { display: flex; gap: 8px; width: 100%; flex-wrap: wrap; }
        .btn-small { padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(255, 255, 255, 0.05); color: var(--text-primary); cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-small:hover:not(:disabled) { background: rgba(255, 255, 255, 0.1); border-color: var(--accent-cyan); }
        .btn-small:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-success { background: rgba(16, 185, 129, 0.1); border-color: var(--accent-green); color: var(--accent-green); }
        .btn-success:hover:not(:disabled) { background: rgba(16, 185, 129, 0.2); }
        .btn-danger { background: rgba(239, 68, 68, 0.1); border-color: var(--accent-red); color: var(--accent-red); }
        .btn-danger:hover:not(:disabled) { background: rgba(239, 68, 68, 0.2); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); z-index: 1000; align-items: center; justify-content: center; }
        .modal.active { display: flex; }
        .modal-content { background: rgba(21, 25, 51, 0.95); backdrop-filter: blur(20px); border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.2); padding: 32px; max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto; animation: modalSlideIn 0.3s ease; }
        .modal-small { max-width: 400px; }
        @keyframes modalSlideIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .modal-header h2 { font-size: 24px; font-weight: 700; color: var(--text-primary); }
        .modal-close { width: 36px; height: 36px; border-radius: 50%; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(255, 255, 255, 0.05); color: var(--text-primary); font-size: 24px; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
        .modal-close:hover { background: rgba(239, 68, 68, 0.2); border-color: var(--accent-red); color: var(--accent-red); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
        .form-input, .form-textarea, .form-select { width: 100%; padding: 12px 16px; font-size: 14px; color: var(--text-primary); background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; transition: all 0.3s; }
        .form-input:focus, .form-textarea:focus, .form-select:focus { outline: none; background: rgba(255, 255, 255, 0.08); border-color: var(--accent-cyan); box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.1); }
        .form-textarea { resize: vertical; min-height: 100px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .modal-actions { display: flex; gap: 12px; margin-top: 24px; justify-content: flex-end; }
        .btn { padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; border: none; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-secondary { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); color: var(--text-primary); }
        .btn-secondary:hover:not(:disabled) { background: rgba(255, 255, 255, 0.1); }
        .btn-primary { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-pink)); color: white; box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3); }
        .btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(6, 182, 212, 0.4); }
        .toast { position: fixed; top: 20px; right: 20px; padding: 16px 24px; background: rgba(21, 25, 51, 0.95); backdrop-filter: blur(20px); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.2); color: var(--text-primary); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); z-index: 2000; animation: slideInRight 0.3s ease; display: flex; align-items: center; gap: 12px; max-width: 400px; }
        .toast.success { border-color: var(--accent-green); }
        .toast.error { border-color: var(--accent-red); }
        @keyframes slideInRight { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(400px); opacity: 0; } }
        .loading-spinner { text-align: center; padding: 60px 20px; color: var(--text-muted); font-size: 16px; }
        .no-tasks-found, .error-message { text-align: center; padding: 60px 20px; color: var(--text-secondary); background: rgba(255, 255, 255, 0.05); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); grid-column: 1 / -1; }
        .no-tasks-found p, .error-message p { font-size: 16px; margin-bottom: 20px; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 1200px) { .tasks-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); } }
        @media (max-width: 768px) { .sidebar { width: 70px; } .logo-text, .nav-label, .nav-link span { display: none; } .main-content { margin-left: 70px; padding: 16px; } .tasks-grid { grid-template-columns: 1fr; } .form-row { grid-template-columns: 1fr; } .filter-tabs { overflow-x: auto; } .page-header { flex-direction: column; align-items: flex-start; gap: 16px; } .header-right { width: 100%; } .toast { max-width: calc(100% - 40px); } }
    </style>
</head>
<body>
<script>
// API Configuration - CHANGE THIS URL TO YOUR BACKEND
const API_BASE_URL = 'http://localhost:8000';

// Global API Client
window.API = {
    client: {
        baseURL: API_BASE_URL,
        async request(endpoint, options = {}) {
            const token = localStorage.getItem('accessToken');
            const headers = { 'Content-Type': 'application/json', ...options.headers };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            const config = { ...options, headers };
            try {
                const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
                if (response.status === 401) {
                    const refreshed = await this.refreshToken();
                    if (refreshed) {
                        headers['Authorization'] = `Bearer ${localStorage.getItem('accessToken')}`;
                        return await fetch(`${API_BASE_URL}${endpoint}`, config);
                    } else {
                        localStorage.removeItem('accessToken');
                        localStorage.removeItem('refreshToken');
                        window.location.href = '/login/';
                        throw new Error('Session expired');
                    }
                }
                return response;
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        },
        async refreshToken() {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) return false;
            try {
                const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: refreshToken })
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
        }
    },
    tasks: {
        async getAll() {
            const response = await window.API.client.request('/api/tasks/', { method: 'GET' });
            return await response.json();
        },
        async getById(id) {
            const response = await window.API.client.request(`/api/tasks/${id}/`, { method: 'GET' });
            return await response.json();
        },
        async create(data) {
            return await window.API.client.request('/api/tasks/', { method: 'POST', body: JSON.stringify(data) });
        },
        async update(id, data) {
            return await window.API.client.request(`/api/tasks/${id}/`, { method: 'PUT', body: JSON.stringify(data) });
        },
        async patch(id, data) {
            return await window.API.client.request(`/api/tasks/${id}/`, { method: 'PATCH', body: JSON.stringify(data) });
        },
        async delete(id) {
            return await window.API.client.request(`/api/tasks/${id}/`, { method: 'DELETE' });
        }
    },
    projects: {
        async getAll() {
            const response = await window.API.client.request('/api/projects/', { method: 'GET' });
            return await response.json();
        }
    }
};

// Toast Function
window.showToast = function(message, type = 'success') {
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${type === 'success' ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>' : '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>'}</svg><span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// Interactive Background
document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth) * 100;
    const y = (e.clientY / window.innerHeight) * 100;
    document.body.style.setProperty('--mouse-x', x + '%');
    document.body.style.setProperty('--mouse-y', y + '%');
});

// Check Auth
if (!localStorage.getItem('accessToken')) {
    window.location.href = '/login/';
}
</script>

    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="logo">
                    <div class="logo-icon">L</div>
                    <span class="logo-text">Loop AI</span>
                </div>
            </div>
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <span class="nav-label">MENU</span>
                    <a href="/dashboard/" class="nav-link">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                        <span>Dashboard</span>
                    </a>
                    <a href="/projects/" class="nav-link">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                        <span>Projects</span>
                    </a>
                    <a href="/tasks/" class="nav-link active">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
                        <span>Tasks</span>
                    </a>
                    <a href="/chat/" class="nav-link">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                        <span>Chat</span>
                    </a>
                </div>
                <div class="nav-section">
                    <span class="nav-label">WORKSPACE</span>
                    <a href="/team/" class="nav-link">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                        <span>Team</span>
                    </a>
                    <a href="/analytics/" class="nav-link">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                        <span>Analytics</span>
                    </a>
                    <a href="/settings/" class="nav-link">
                        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                        <span>Settings</span>
                    </a>
                </div>
            </nav>
            <div class="sidebar-footer">
                <a href="#" onclick="handleLogout(event)" class="nav-link logout-btn">
                    <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    <span>Logout</span>
                </a>
            </div>
        </aside>

        <main class="main-content">
            <header class="page-header">
                <div class="header-left">
                    <h1>My Tasks</h1>
                    <p>Manage and track your tasks efficiently</p>
                </div>
                <div class="header-right">
                    <button class="icon-button" id="filter-btn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
                    </button>
                    <button class="primary-button" id="new-task-btn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                        New Task
                    </button>
                </div>
            </header>

            <div class="filter-tabs">
                <button class="tab active" data-filter="all">All Tasks</button>
                <button class="tab" data-filter="pending">Pending</button>
                <button class="tab" data-filter="in_progress">In Progress</button>
                <button class="tab" data-filter="completed">Completed</button>
                <button class="tab" data-filter="high">High Priority</button>
            </div>

            <div class="tasks-grid" id="tasks-grid">
                <div class="loading-spinner">Loading tasks...</div>
            </div>
        </main>
    </div>

    <div class="modal" id="new-task-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Create New Task</h2>
                <button class="modal-close" onclick="closeModal('new-task-modal')">&times;</button>
            </div>
            <form id="new-task-form">
                <div class="form-group">
                    <label>Title *</label>
                    <input type="text" name="title" class="form-input" placeholder="Enter task title" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" class="form-textarea" placeholder="Enter task description"></textarea>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Priority *</label>
                        <select name="priority" class="form-select" required>
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Status *</label>
                        <select name="status" class="form-select" required>
                            <option value="pending" selected>Pending</option>
                            <option value="in_progress">In Progress</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Due Date</label>
                        <input type="date" name="due_date" class="form-input">
                    </div>
                    <div class="form-group">
                        <label>Project</label>
                        <select name="project" class="form-select" id="project-select">
                            <option value="">No Project</option>
                        </select>
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('new-task-modal')">Cancel</button>
                    <button type="submit" class="btn btn-primary" id="create-task-btn">Create Task</button>
                </div>
            </form>
        </div>
    </div>

    <div class="modal" id="edit-task-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Task</h2>
                <button class="modal-close" onclick="closeModal('edit-task-modal')">&times;</button>
            </div>
            <form id="edit-task-form">
                <input type="hidden" name="task_id" id="edit-task-id">
                <div class="form-group">
                    <label>Title *</label>
                    <input type="text" name="title" id="edit-title" class="form-input" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" id="edit-description" class="form-textarea"></textarea>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Priority *</label>
                        <select name="priority" id="edit-priority" class="form-select" required>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Status *</label>
                        <select name="status" id="edit-status" class="form-select" required>
                            <option value="pending">Pending</option>
                            <option value="in_progress">In Progress</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Due Date</label>
                        <input type="date" name="due_date" id="edit-due-date" class="form-input">
                    </div>
                    <div class="form-group">
                        <label>Project</label>
                        <select name="project" id="edit-project" class="form-select">
                            <option value="">No Project</option>
                        </select>
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('edit-task-modal')">Cancel</button>
                    <button type="submit" class="btn btn-primary" id="update-task-btn">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <div class="modal" id="filter-modal">
        <div class="modal-content modal-small">
            <div class="modal-header">
                <h2>Filter Tasks</h2>
                <button class="modal-close" onclick="closeModal('filter-modal')">&times;</button>
            </div>
            <form id="filter-form">
                <div class="form-group">
                    <label>Status</label>
                    <select name="status" class="form-select">
                        <option value="">All</option>
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Priority</label>
                    <select name="priority" class="form-select">
                        <option value="">All</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Project</label>
                    <select name="project" class="form-select" id="filter-project">
                        <option value="">All Projects</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="resetFilters()">Reset</button>
                    <button type="submit" class="btn btn-primary">Apply Filters</button>
                </div>
            </form>
        </div>
    </div>

<script>
let currentFilter = 'all';
let allTasks = [];

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) {
        return 'N/A';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadTasks();
    loadProjects();
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('new') === 'true') openModal('new-task-modal');
    
    document.getElementById('new-task-btn').addEventListener('click', () => openModal('new-task-modal'));
    document.getElementById('filter-btn').addEventListener('click', () => openModal('filter-modal'));
    document.getElementById('new-task-form').addEventListener('submit', handleCreateTask);
    document.getElementById('edit-task-form').addEventListener('submit', handleEditTask);
    document.getElementById('filter-form').addEventListener('submit', handleFilter);
    
    document.querySelectorAll('.filter-tabs .tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.filter-tabs .tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            filterTasks();
        });
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.active').forEach(modal => modal.classList.remove('active'));
        }
    });
});

async function loadTasks() {
    try {
        const tasksContainer = document.getElementById('tasks-grid');
        tasksContainer.innerHTML = '<div class="loading-spinner">Loading tasks...</div>';
        const data = await window.API.tasks.getAll();
        allTasks = data.results || data;
        if (Array.isArray(allTasks)) {
            displayTasks(allTasks);
        } else {
            throw new Error('Invalid data format');
        }
    } catch (error) {
        console.error('Failed to load tasks:', error);
        document.getElementById('tasks-grid').innerHTML = '<div class="error-message"><p>Error loading tasks. Please try again later.</p><button class="btn btn-primary" onclick="loadTasks()" style="margin-top: 16px;">Retry</button></div>';
    }
}

function displayTasks(tasks) {
    const tasksContainer = document.getElementById('tasks-grid');
    if (tasks && tasks.length > 0) {
        tasksContainer.innerHTML = tasks.map(task => {
            const title = escapeHtml(task.title || 'Untitled Task');
            const description = escapeHtml(task.description || 'No description provided.');
            const projectName = escapeHtml(task.project_name || 'No Project');
            const priority = task.priority ? task.priority.toLowerCase() : 'medium';
            const isCompleted = task.status === 'completed';
            return `<div class="task-card ${isCompleted ? 'completed' : ''}" data-task-id="${task.id}">
                <div class="task-header">
                    <h3 class="task-title">${title}</h3>
                    <span class="task-priority priority-${priority}">${task.priority || 'Medium'}</span>
                </div>
                <p class="task-description">${description}</p>
                <div class="task-meta">
                    <span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>${projectName}</span>
                    <span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>Due: ${formatDate(task.due_date)}</span>
                </div>
                <div class="task-footer">
                    <div class="task-actions">
                        <button class="btn-small" onclick="editTask('${task.id}')">Edit</button>
                        <button class="btn-small btn-success" onclick="completeTask('${task.id}', this)" ${isCompleted ? 'disabled' : ''}>${isCompleted ? 'Completed' : 'Complete'}</button>
                        <button class="btn-small btn-danger" onclick="deleteTask('${task.id}')">Delete</button>
                    </div>
                </div>
            </div>`;
        }).join('');
    } else {
        tasksContainer.innerHTML = '<div class="no-tasks-found"><p>No tasks found. Create one to get started!</p><button class="btn btn-primary" onclick="openModal(\'new-task-modal\')" style="margin-top: 16px;">Create Your First Task</button></div>';
    }
}

function filterTasks() {
    let filtered = [...allTasks];
    if (currentFilter !== 'all') {
        if (currentFilter === 'high') {
            filtered = filtered.filter(task => task.priority === 'high');
        } else {
            filtered = filtered.filter(task => task.status === currentFilter);
        }
    }
    displayTasks(filtered);
}

async function loadProjects() {
    try {
        const data = await window.API.projects.getAll();
        const projects = data.results || data;
        if (!Array.isArray(projects)) return;
        const projectSelects = [document.getElementById('project-select'), document.getElementById('edit-project'), document.getElementById('filter-project')];
        projectSelects.forEach(select => {
            if (select) {
                const currentValue = select.value;
                const options = projects.map(project => {
                    const name = escapeHtml(project.name || 'Unnamed Project');
                    return `<option value="${project.id}">${name}</option>`;
                }).join('');
                if (select.id === 'filter-project') {
                    select.innerHTML = '<option value="">All Projects</option>' + options;
                } else {
                    select.innerHTML = '<option value="">No Project</option>' + options;
                }
                if (currentValue) select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Failed to load projects:', error);
    }
}

async function handleCreateTask(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('create-task-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';
    const formData = new FormData(e.target);
    const taskData = {
        title: formData.get('title').trim(),
        description: formData.get('description').trim(),
        priority: formData.get('priority'),
        status: formData.get('status'),
        due_date: formData.get('due_date') || null,
        project: formData.get('project') || null
    };
    if (!taskData.title) {
        showToast('Please enter a task title', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Task';
        return;
    }
    try {
        const response = await window.API.tasks.create(taskData);
        if (response.ok) {
            showToast('Task created successfully!', 'success');
            closeModal('new-task-modal');
            e.target.reset();
            await loadTasks();
        } else {
            showToast('Failed to create task. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showToast('An error occurred while creating the task.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Task';
    }
}

async function editTask(taskId) {
    try {
        const task = await window.API.tasks.getById(taskId);
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-title').value = task.title || '';
        document.getElementById('edit-description').value = task.description || '';
        document.getElementById('edit-priority').value = task.priority || 'medium';
        document.getElementById('edit-status').value = task.status || 'pending';
        document.getElementById('edit-due-date').value = task.due_date || '';
        document.getElementById('edit-project').value = task.project || '';
        openModal('edit-task-modal');
    } catch (error) {
        console.error('Error loading task:', error);
        showToast('Failed to load task details.', 'error');
    }
}

async function handleEditTask(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('update-task-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';
    const formData = new FormData(e.target);
    const taskId = formData.get('task_id');
    const taskData = {
        title: formData.get('title').trim(),
        description: formData.get('description').trim(),
        priority: formData.get('priority'),
        status: formData.get('status'),
        due_date: formData.get('due_date') || null,
        project: formData.get('project') || null
    };
    if (!taskData.title) {
        showToast('Please enter a task title', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Changes';
        return;
    }
    try {
        const response = await window.API.tasks.update(taskId, taskData);
        if (response.ok) {
            showToast('Task updated successfully!', 'success');
            closeModal('edit-task-modal');
            await loadTasks();
        } else {
            showToast('Failed to update task. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showToast('An error occurred while updating the task.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Changes';
    }
}

async function completeTask(taskId, button) {
    const taskCard = button.closest('.task-card');
    if (taskCard.classList.contains('completed')) return;
    button.disabled = true;
    button.textContent = 'Completing...';
    try {
        const response = await window.API.tasks.patch(taskId, { status: 'completed' });
        if (response.ok) {
            taskCard.classList.add('completed');
            button.textContent = 'Completed';
            button.disabled = true;
            showToast('Task marked as completed!', 'success');
            await loadTasks();
        } else {
            showToast('Failed to complete task.', 'error');
            button.disabled = false;
            button.textContent = 'Complete';
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showToast('An error occurred while completing the task.', 'error');
        button.disabled = false;
        button.textContent = 'Complete';
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) return;
    try {
        const response = await window.API.tasks.delete(taskId);
        if (response.ok || response.status === 204) {
            const taskCard = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                taskCard.style.opacity = '0';
                taskCard.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    taskCard.remove();
                    allTasks = allTasks.filter(t => t.id != taskId);
                    if (!document.querySelector('.task-card')) displayTasks([]);
                }, 500);
            }
            showToast('Task deleted successfully!', 'success');
        } else {
            showToast('Failed to delete task.', 'error');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showToast('An error occurred while deleting the task.', 'error');
    }
}

function handleFilter(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    let filtered = [...allTasks];
    const status = formData.get('status');
    const priority = formData.get('priority');
    const project = formData.get('project');
    if (status) filtered = filtered.filter(task => task.status === status);
    if (priority) filtered = filtered.filter(task => task.priority === priority);
    if (project) filtered = filtered.filter(task => task.project == project);
    displayTasks(filtered);
    closeModal('filter-modal');
    showToast('Filters applied successfully!', 'success');
}

function resetFilters() {
    document.getElementById('filter-form').reset();
    currentFilter = 'all';
    document.querySelectorAll('.filter-tabs .tab').forEach(t => t.classList.remove('active'));
    document.querySelector('.filter-tabs .tab[data-filter="all"]').classList.add('active');
    displayTasks(allTasks);
    closeModal('filter-modal');
    showToast('Filters cleared', 'success');
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) setTimeout(() => firstInput.focus(), 100);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        const form = modal.querySelector('form');
        if (form && !form.id.includes('edit')) form.reset();
    }
}

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', function(e) {
        if (e.target === this) this.classList.remove('active');
    });
});

function handleLogout(e) {
    e.preventDefault();
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        showToast('Logged out successfully', 'success');
        setTimeout(() => window.location.href = '/login/', 1000);
    }
}
</script>
</body>
</html>