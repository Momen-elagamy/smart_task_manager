// Notification Center Management
(function() {
    'use strict';

    let notificationsPanel = null;
    let notificationsOverlay = null;
    let notificationsTrigger = null;
    let notificationBadge = null;

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        initializeNotifications();
    });

    function initializeNotifications() {
        notificationsPanel = document.getElementById('notifications-panel');
        notificationsOverlay = document.getElementById('notifications-overlay');
        notificationsTrigger = document.getElementById('notifications-trigger');
        notificationBadge = document.getElementById('notification-badge');

        if (!notificationsPanel || !notificationsTrigger) return;

        // Bind events
        notificationsTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            toggleNotifications();
        });

        document.getElementById('close-notifications-btn')?.addEventListener('click', closeNotifications);
        document.getElementById('mark-all-read-btn')?.addEventListener('click', markAllAsRead);
        notificationsOverlay?.addEventListener('click', closeNotifications);

        // Load unread count
        loadUnreadCount();

        // Poll for new notifications every 30 seconds
        setInterval(loadUnreadCount, 30000);
    }

    async function toggleNotifications() {
        if (notificationsPanel.classList.contains('open')) {
            closeNotifications();
        } else {
            openNotifications();
        }
    }

    async function openNotifications() {
        notificationsPanel.style.display = 'flex';
        notificationsPanel.classList.add('open');
        notificationsOverlay.style.display = 'block';
        notificationsOverlay.classList.add('show');
        document.body.classList.add('notifications-open');
        await loadNotifications();
    }

    function closeNotifications() {
        notificationsPanel.classList.remove('open');
        notificationsOverlay.classList.remove('show');
        document.body.classList.remove('notifications-open');
        // Keep panel rendered for smooth slide-out; optional display reset
        notificationsPanel.style.display = 'flex';
        notificationsOverlay.style.display = 'block';
        setTimeout(() => {
            if (!notificationsPanel.classList.contains('open')) {
                notificationsOverlay.style.display = 'none';
            }
        }, 300);
    }

    async function loadUnreadCount() {
        try {
            const data = await window.API.notifications.getCount();
            // API may return {count} or {unread_count}; normalize to a number
            const count = Number(data?.unread_count ?? data?.count ?? data?.unread ?? 0);
            updateBadge(Number.isFinite(count) ? count : 0);
        } catch (error) {
            console.error('Failed to load notification count:', error);
        }
    }

    async function loadNotifications() {
        const body = document.getElementById('notifications-body');
        if (!body) return;

        body.innerHTML = '<div class="loading-spinner">Loading notifications...</div>';

        try {
            const data = await window.API.notifications.getAll();
            const notifications = data.results || data;

            if (notifications.length === 0) {
                body.innerHTML = `
                    <div class="no-notifications">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                        </svg>
                        <p>No notifications yet</p>
                    </div>
                `;
                return;
            }

            // Categorize notifications for nicer grouping
            const buckets = categorizeNotifications(notifications);

            body.innerHTML = '';
            renderSection(body, 'Incoming Messages', buckets.messages, 'chat');
            renderSection(body, 'Tasks & Deadlines', buckets.tasks, 'tasks');
            renderSection(body, 'Other Updates', buckets.others, 'info');
        } catch (error) {
            console.error('Failed to load notifications:', error);
            body.innerHTML = `
                <div class="no-notifications">
                    <p style="color: var(--accent-red);">Failed to load notifications</p>
                    <button class="btn-text" onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }

    function createNotificationElement(notification) {
        const item = document.createElement('div');
        item.className = 'notification-item' + (!notification.is_read ? ' unread' : '');
        item.dataset.id = notification.id;

        const timeAgo = formatTimeAgo(new Date(notification.created_at));

        const icon = pickIcon(notification);

        item.innerHTML = `
            <div class="notification-top">
                <div class="notification-icon">${icon}</div>
                <div class="notification-meta">
                    <div class="notification-title">${escapeHtml(notification.title || notification.room_name || 'Notification')}</div>
                    <div class="notification-message">${escapeHtml(notification.message || notification.message_content || '')}</div>
                </div>
            </div>
            <div class="notification-time">${timeAgo}</div>
        `;

        item.addEventListener('click', () => {
            markAsRead(notification.id);
            if (notification.link) {
                window.location.href = notification.link;
            }
        });

        return item;
    }

    function renderSection(container, title, items, accent = 'info'){
        const section = document.createElement('div');
        section.className = 'notif-section';
        section.innerHTML = `
            <div class="notif-section-header">
                <span class="pill pill-${accent}">${escapeHtml(title)}</span>
                <span class="pill-count">${items.length}</span>
            </div>
        `;
        const list = document.createElement('div');
        list.className = 'notif-section-body';
        if(!items.length){
            const empty = document.createElement('div');
            empty.className = 'no-notifications mini';
            empty.innerHTML = '<p>No updates here.</p>';
            list.appendChild(empty);
        } else {
            items.forEach(n => list.appendChild(createNotificationElement(n)));
        }
        section.appendChild(list);
        container.appendChild(section);
    }

    function categorizeNotifications(notifications){
        const res = { messages: [], tasks: [], others: [] };
        notifications.forEach(n => {
            const text = `${n.title || ''} ${n.message || ''} ${n.message_content || ''}`.toLowerCase();
            const hasRoom = !!(n.room || n.room_name || (n.link && n.link.includes('/chat')));
            const isTasky = /task|due|deadline|project|تسليم|موعد/.test(text) || (n.link && n.link.includes('/tasks'));
            if(hasRoom){ res.messages.push(n); return; }
            if(isTasky){ res.tasks.push(n); return; }
            res.others.push(n);
        });
        return res;
    }

    function pickIcon(notification){
        const text = `${notification.title || ''} ${notification.message || ''} ${notification.message_content || ''}`.toLowerCase();
        if(notification.room || notification.room_name){
            return '<i class="fas fa-comment-dots"></i>';
        }
        if(/task|due|deadline|project|تسليم|موعد/.test(text)){
            return '<i class="fas fa-check-circle"></i>';
        }
        return '<i class="fas fa-bell"></i>';
    }

    async function markAsRead(notificationId) {
        try {
            await window.API.notifications.markRead(notificationId);
            const item = document.querySelector(`[data-id="${notificationId}"]`);
            if (item) {
                item.classList.remove('unread');
            }
            await loadUnreadCount();
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }

    function inlineToast(message, type = 'info') {
        const body = document.getElementById('notifications-body');
        if (!body) return;
        const toast = document.createElement('div');
        toast.className = `notification-inline-toast ${type}`;
        toast.textContent = message;
        body.prepend(toast);
        setTimeout(() => toast.remove(), 2500);
    }

    async function markAllAsRead() {
        try {
            await window.API.notifications.markAllRead();
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                item.classList.remove('unread');
            });
            updateBadge(0);
            inlineToast('Marked all as read', 'success');
            // Reload to refresh grouping/counts
            await loadNotifications();
        } catch (error) {
            console.error('Failed to mark all as read:', error);
            inlineToast('Could not mark all read. Try again.', 'error');
        }
    }

    function updateBadge(count) {
        if (!notificationBadge) return;

        if (count > 0) {
            notificationBadge.textContent = count > 99 ? '99+' : count;
            notificationBadge.style.display = 'block';
            notificationsTrigger?.classList.add('has-unread');
        } else {
            notificationBadge.style.display = 'none';
            notificationsTrigger?.classList.remove('has-unread');
        }
    }

    function formatTimeAgo(date) {
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // seconds

        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
        return date.toLocaleDateString();
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Expose to global scope if needed
    window.NotificationCenter = {
        loadUnreadCount,
        openNotifications,
        closeNotifications
    };
})();
