/**
 * Favorite Jobs functionality
 * Handles favoriting/unfavoriting jobs via AJAX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Prevent initializing the favorite handlers multiple times
    if (window.__favoriteJobsInitialized) return;
    window.__favoriteJobsInitialized = true;
    // Get CSRF token for Django POST requests
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

    // Handle favorite forms by delegating submission to Django (no AJAX)
    // JS will not fetch data; Django will reload the page and provide updated state.
    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.favorite-form');
        if (!form) return;

        // Do not intercept the submit. Let Django handle the POST and reload the page.
        // Provide small UX improvement: disable the submit button to avoid duplicate submits.
        try {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
            }
        } catch (err) {
            // silent fallback
            console.error('favorite form submit handler error', err);
        }
        // Allow normal form submission (no e.preventDefault())
    });

    // Simple notification function
    function showNotification(message, type = 'info') {
        // Check if notification container exists
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;

        container.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        });
    }
});
