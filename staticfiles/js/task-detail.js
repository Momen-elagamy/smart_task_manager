/**
 * Task Detail Page
 * Displays task info, attachments, and comments
 */

let currentTaskId = null;
let timerInterval = null;
let activeTracking = null;
let timerStartTime = null;

// Initialize page
document.addEventListener('DOMContentLoaded', async function() {
    // Get task ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    currentTaskId = urlParams.get('id');
    
    if (!currentTaskId) {
        alert('Task ID not found');
        window.location.href = '/tasks/';
        return;
    }
    
    await loadTaskDetails();
    await loadAttachments();
    await loadComments();
    await loadActiveTracking();
    await loadTimeLogs();
    
    // File input preview
    document.getElementById('file-input').addEventListener('change', handleFileSelect);
});

async function loadTaskDetails() {
    try {
        const response = await window.API.client.get(`/api/tasks/${currentTaskId}/`);
        const task = response;
        
        // Update page
        document.getElementById('task-title').textContent = task.title;
        document.getElementById('task-description').textContent = task.description || 'No description';
        document.getElementById('task-due-date').textContent = task.due_date || 'Not set';
        document.getElementById('task-assigned').textContent = task.assigned_to ? task.assigned_to_email : 'Unassigned';
        
        // Status badge
        const statusBadge = document.getElementById('task-status');
        statusBadge.textContent = task.status.replace('_', ' ').toUpperCase();
        statusBadge.className = 'status-badge status-' + task.status;
        
        // Priority badge
        const priorityBadge = document.getElementById('task-priority');
        priorityBadge.textContent = task.priority.toUpperCase();
        priorityBadge.className = 'priority-badge priority-' + task.priority;
        
    } catch (error) {
        console.error('Error loading task:', error);
        alert('Failed to load task details');
    }
}

async function loadAttachments() {
    try {
        const response = await window.API.client.get(`/api/attachments/?task=${currentTaskId}`);
        const attachments = Array.isArray(response) ? response : response.results || [];
        
        document.getElementById('attachments-count').textContent = attachments.length;
        
        const list = document.getElementById('attachments-list');
        const empty = document.getElementById('attachments-empty');
        
        if (attachments.length === 0) {
            list.style.display = 'none';
            empty.style.display = 'flex';
            return;
        }
        
        list.innerHTML = attachments.map(att => createAttachmentCard(att)).join('');
        list.style.display = 'grid';
        empty.style.display = 'none';
        
    } catch (error) {
        console.error('Error loading attachments:', error);
    }
}

function createAttachmentCard(attachment) {
    const icon = attachment.is_image ? 'fa-image' : 
                 attachment.is_document ? 'fa-file-pdf' : 'fa-file';
    
    const date = new Date(attachment.created_at).toLocaleDateString();
    
    return `
        <div class="attachment-card">
            <div class="attachment-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="attachment-info">
                <div class="attachment-name">${escapeHtml(attachment.original_filename)}</div>
                <div class="attachment-meta">
                    ${attachment.file_size_mb} MB • ${date}
                </div>
                <div class="attachment-uploader">
                    by ${escapeHtml(attachment.uploaded_by_name)}
                </div>
            </div>
            <div class="attachment-actions">
                <a href="${attachment.file}" target="_blank" class="btn-icon" title="Download">
                    <i class="fas fa-download"></i>
                </a>
                <button class="btn-icon btn-danger" onclick="deleteAttachment('${attachment.id}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

async function loadComments() {
    try {
        const response = await window.API.client.get(`/api/comments/?task=${currentTaskId}`);
        const comments = Array.isArray(response) ? response : response.results || [];
        
        document.getElementById('comments-count').textContent = comments.length;
        
        const list = document.getElementById('comments-list');
        const empty = document.getElementById('comments-empty');
        
        if (comments.length === 0) {
            list.style.display = 'none';
            empty.style.display = 'flex';
            return;
        }
        
        list.innerHTML = comments.map(comment => createCommentCard(comment)).join('');
        list.style.display = 'block';
        empty.style.display = 'none';
        
    } catch (error) {
        console.error('Error loading comments:', error);
    }
}

function createCommentCard(comment) {
    const date = new Date(comment.created_at).toLocaleString();
    const edited = comment.edited ? ` <span class="comment-edited">(edited)</span>` : '';
    
    return `
        <div class="comment-card">
            <div class="comment-header">
                <div class="comment-author">
                    <i class="fas fa-user-circle"></i>
                    <strong>${escapeHtml(comment.author_name)}</strong>
                </div>
                <div class="comment-date">${date}${edited}</div>
            </div>
            <div class="comment-content">${escapeHtml(comment.content)}</div>
        </div>
    `;
}

async function submitComment() {
    const input = document.getElementById('comment-input');
    const content = input.value.trim();
    
    if (!content) {
        alert('Please enter a comment');
        return;
    }
    
    try {
        await window.API.client.post('/api/comments/', {
            task: currentTaskId,
            content: content
        });
        
        input.value = '';
        await loadComments();
        
    } catch (error) {
        console.error('Error posting comment:', error);
        alert('Failed to post comment');
    }
}

function openUploadDialog() {
    document.getElementById('upload-dialog').style.display = 'flex';
    document.getElementById('file-input').value = '';
    document.getElementById('file-preview').style.display = 'none';
}

function closeUploadDialog() {
    document.getElementById('upload-dialog').style.display = 'none';
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const preview = document.getElementById('file-preview');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    fileName.textContent = file.name;
    fileSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
    preview.style.display = 'flex';
    
    // Check size
    if (file.size > 10 * 1024 * 1024) {
        alert('File too large! Maximum 10MB');
        e.target.value = '';
        preview.style.display = 'none';
    }
}

async function submitUpload() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('task', currentTaskId);
    
    try {
        await window.API.client.post('/api/attachments/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        closeUploadDialog();
        await loadAttachments();
        
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Failed to upload file');
    }
}

async function deleteAttachment(attachmentId) {
    if (!confirm('Are you sure you want to delete this attachment?')) {
        return;
    }
    
    try {
        await window.API.client.delete(`/api/attachments/${attachmentId}/`);
        await loadAttachments();
        
    } catch (error) {
        console.error('Error deleting attachment:', error);
        alert('Failed to delete attachment');
    }
}

function editTask() {
    window.location.href = `/tasks/edit/?id=${currentTaskId}`;
}

async function deleteTask() {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        await window.API.client.delete(`/api/tasks/${currentTaskId}/`);
        window.location.href = '/tasks/';
        
    } catch (error) {
        console.error('Error deleting task:', error);
        alert('Failed to delete task');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===========================
// TIME TRACKING FUNCTIONS
// ===========================

async function loadActiveTracking() {
    try {
        const response = await window.API.client.get('/api/analytics/time-tracking/active_tracking/');
        
        if (response && response.id) {
            activeTracking = response;
            
            // Check if this tracking is for current task
            if (activeTracking.task === currentTaskId) {
                timerStartTime = new Date(activeTracking.start_time);
                startTimerDisplay();
                
                document.getElementById('start-timer-btn').style.display = 'none';
                document.getElementById('stop-timer-btn').style.display = 'inline-block';
            }
        }
    } catch (error) {
        console.log('No active tracking');
    }
}

async function loadTimeLogs() {
    try {
        const response = await window.API.client.get(`/api/analytics/time-tracking/?task=${currentTaskId}`);
        const logs = Array.isArray(response) ? response : response.results || [];
        
        const listEl = document.getElementById('time-logs-list');
        
        if (logs.length === 0) {
            listEl.innerHTML = '<p class="text-muted">No time logs yet</p>';
            return;
        }
        
        listEl.innerHTML = logs.map(log => {
            const duration = log.duration ? formatDuration(log.duration) : 'In progress';
            const startDate = new Date(log.start_time).toLocaleString();
            
            return `
                <div class="time-log-item">
                    <div class="time-log-duration">${duration}</div>
                    <div class="time-log-date">${startDate}</div>
                    ${log.description ? `<div class="time-log-desc">${escapeHtml(log.description)}</div>` : ''}
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading time logs:', error);
    }
}

async function startTimer() {
    try {
        const response = await window.API.client.post('/api/analytics/time-tracking/start_tracking/', {
            task: currentTaskId,
            description: ''
        });
        
        activeTracking = response;
        timerStartTime = new Date(response.start_time);
        
        startTimerDisplay();
        
        document.getElementById('start-timer-btn').style.display = 'none';
        document.getElementById('stop-timer-btn').style.display = 'inline-block';
        
    } catch (error) {
        console.error('Error starting timer:', error);
        alert(error.response?.data?.error || 'Failed to start timer');
    }
}

async function stopTimer() {
    if (!activeTracking) return;
    
    try {
        await window.API.client.post(`/api/analytics/time-tracking/${activeTracking.id}/stop_tracking/`);
        
        stopTimerDisplay();
        
        document.getElementById('start-timer-btn').style.display = 'inline-block';
        document.getElementById('stop-timer-btn').style.display = 'none';
        
        activeTracking = null;
        timerStartTime = null;
        
        // Reload logs
        await loadTimeLogs();
        
    } catch (error) {
        console.error('Error stopping timer:', error);
        alert('Failed to stop timer');
    }
}

function startTimerDisplay() {
    updateTimerDisplay();
    timerInterval = setInterval(updateTimerDisplay, 1000);
}

function stopTimerDisplay() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    document.getElementById('timer-display').textContent = '00:00:00';
}

function updateTimerDisplay() {
    if (!timerStartTime) return;
    
    const now = new Date();
    const elapsed = Math.floor((now - timerStartTime) / 1000); // seconds
    
    const hours = Math.floor(elapsed / 3600);
    const minutes = Math.floor((elapsed % 3600) / 60);
    const seconds = elapsed % 60;
    
    const display = [hours, minutes, seconds]
        .map(n => n.toString().padStart(2, '0'))
        .join(':');
    
    document.getElementById('timer-display').textContent = display;
}

function formatDuration(durationStr) {
    // durationStr format: "HH:MM:SS" or "D days, HH:MM:SS"
    const parts = durationStr.split(',');
    const timePart = parts.length > 1 ? parts[1].trim() : parts[0].trim();
    const daysPart = parts.length > 1 ? parts[0].trim() : '';
    
    const [hours, minutes, seconds] = timePart.split(':').map(Number);
    
    let result = '';
    if (daysPart) result += daysPart + ' ';
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0) result += `${minutes}m `;
    result += `${seconds}s`;
    
    return result.trim();
}
