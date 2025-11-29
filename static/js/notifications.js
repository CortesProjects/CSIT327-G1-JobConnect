// Notifications System
document.addEventListener('DOMContentLoaded', function() {
    const notificationBell = document.querySelector('.notification-bell');
    const notificationBadge = document.querySelector('.notification-badge');
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    const notificationsList = document.getElementById('notificationsList');
    const notificationsEmpty = document.getElementById('notificationsEmpty');
    const markAllReadBtn = document.getElementById('markAllRead');

    let isDropdownOpen = false;

    // Fetch initial unread count
    fetchUnreadCount();

    // Poll for new notifications every 30 seconds
    setInterval(fetchUnreadCount, 30000);

    // Toggle notifications dropdown
    if (notificationBell) {
        notificationBell.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (isDropdownOpen) {
                closeNotificationsDropdown();
            } else {
                openNotificationsDropdown();
            }
        });
    }

    // Mark all as read
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            markAllNotificationsAsRead();
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (isDropdownOpen && 
            !notificationsDropdown.contains(e.target) && 
            !notificationBell.contains(e.target)) {
            closeNotificationsDropdown();
        }
    });

    // Close with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isDropdownOpen) {
            closeNotificationsDropdown();
        }
    });

    function openNotificationsDropdown() {
        notificationsDropdown.classList.add('show');
        isDropdownOpen = true;
        loadNotifications();
    }

    function closeNotificationsDropdown() {
        notificationsDropdown.classList.remove('show');
        isDropdownOpen = false;
    }

    function fetchUnreadCount() {
        fetch('/notifications/unread-count/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateBadge(data.unread_count);
                }
            })
            .catch(error => console.error('Error fetching unread count:', error));
    }

    function updateBadge(count) {
        if (notificationBadge) {
            if (count > 0) {
                notificationBadge.textContent = count > 99 ? '99+' : count;
                notificationBadge.classList.add('show');
            } else {
                notificationBadge.classList.remove('show');
            }
        }
    }

    function loadNotifications() {
        // Show loading state
        notificationsList.innerHTML = `
            <div class="notifications-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading notifications...</p>
            </div>
        `;
        notificationsEmpty.style.display = 'none';

        fetch('/notifications/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayNotifications(data.notifications);
                    updateBadge(data.unread_count);
                }
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                notificationsList.innerHTML = `
                    <div class="notifications-loading">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Failed to load notifications</p>
                    </div>
                `;
            });
    }

    function displayNotifications(notifications) {
        if (notifications.length === 0) {
            notificationsList.innerHTML = '';
            notificationsEmpty.style.display = 'flex';
            return;
        }

        notificationsEmpty.style.display = 'none';
        notificationsList.innerHTML = notifications.map(notif => `
            <div class="notification-item ${notif.is_read ? '' : 'unread'}" 
                 data-id="${notif.id}" 
                 data-link="${notif.link}">
                <div class="notification-content">
                    <p class="notification-title">${escapeHtml(notif.title)}</p>
                    <p class="notification-message">${escapeHtml(notif.message)}</p>
                    <p class="notification-time">${notif.time_ago}</p>
                </div>
                <div class="notification-actions">
                    ${!notif.is_read ? `
                        <button class="btn-notification-action btn-mark-read" data-id="${notif.id}">
                            Mark as read
                        </button>
                    ` : ''}
                    <button class="btn-notification-action btn-notification-delete" data-id="${notif.id}">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');

        // Add event listeners to notification items
        document.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', function(e) {
                // Don't trigger if clicking action buttons
                if (e.target.closest('.notification-actions')) {
                    return;
                }

                const notifId = this.dataset.id;
                const link = this.dataset.link;

                // Mark as read
                markNotificationAsRead(notifId);

                // Navigate to link if exists
                if (link && link !== '') {
                    window.location.href = link;
                }
            });
        });

        // Mark as read buttons
        document.querySelectorAll('.btn-mark-read').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const notifId = this.dataset.id;
                markNotificationAsRead(notifId);
            });
        });

        // Delete buttons
        document.querySelectorAll('.btn-notification-delete').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const notifId = this.dataset.id;
                deleteNotification(notifId);
            });
        });
    }

    function markNotificationAsRead(notificationId) {
        fetch(`/notifications/${notificationId}/mark-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBadge(data.unread_count);
                // Reload notifications
                loadNotifications();
            }
        })
        .catch(error => console.error('Error marking notification as read:', error));
    }

    function markAllNotificationsAsRead() {
        fetch('/notifications/mark-all-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBadge(0);
                loadNotifications();
            }
        })
        .catch(error => console.error('Error marking all as read:', error));
    }

    function deleteNotification(notificationId) {
        fetch(`/notifications/${notificationId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBadge(data.unread_count);
                loadNotifications();
            }
        })
        .catch(error => console.error('Error deleting notification:', error));
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
