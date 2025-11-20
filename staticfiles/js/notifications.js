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
        if (notificationsPanel.style.display === 'flex') {
            closeNotifications();
        } else {
            openNotifications();
        }
    }

    async function openNotifications() {
        notificationsPanel.style.display = 'flex';
        notificationsOverlay.style.display = 'block';
        await loadNotifications();
    }

    function closeNotifications() {
        notificationsPanel.style.display = 'none';
        notificationsOverlay.style.display = 'none';
    }

    async function loadUnreadCount() {
        try {
            const data = await window.API.notifications.getCount();
            updateBadge(data.unread_count);
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

            body.innerHTML = '';
            notifications.forEach(notification => {
                body.appendChild(createNotificationElement(notification));
            });
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

        item.innerHTML = `
            <div class="notification-title">${escapeHtml(notification.title || 'Notification')}</div>
            <div class="notification-message">${escapeHtml(notification.message)}</div>
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

    async function markAllAsRead() {
        try {
            await window.API.notifications.markAllRead();
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                item.classList.remove('unread');
            });
            updateBadge(0);
        } catch (error) {
            console.error('Failed to mark all as read:', error);
        }
    }

    function updateBadge(count) {
        if (!notificationBadge) return;

        if (count > 0) {
            notificationBadge.textContent = count > 99 ? '99+' : count;
            notificationBadge.style.display = 'block';
        } else {
            notificationBadge.style.display = 'none';
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
