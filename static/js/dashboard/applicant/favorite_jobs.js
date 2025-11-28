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

    // Handle favorite forms with AJAX for better UX
    // Django handles all validation, JS only updates UI dynamically
    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.favorite-form');
        if (!form) return;

        e.preventDefault(); // Intercept for AJAX

        const submitBtn = form.querySelector('button[type="submit"]');
        const icon = submitBtn.querySelector('i');
        const jobId = submitBtn.dataset.jobId;

        if (!jobId) {
            // Fallback: let form submit normally if no job ID
            form.submit();
            return;
        }

        // Disable button during request
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');

        // Send AJAX request to Django view (validation handled server-side)
        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            credentials: 'same-origin'
        })
        .then(async response => {
            const contentType = (response.headers.get('content-type') || '').toLowerCase();

            // Handle non-OK responses
            if (!response.ok) {
                let errMsg = 'Request failed';

                if (contentType.includes('application/json')) {
                    const data = await response.json();
                    errMsg = data.error || data.message || JSON.stringify(data);
                } else {
                    // Could be HTML (login page or error page)
                    const text = await response.text();
                    console.error('Non-JSON error response:', text);
                    if (response.status === 401 || response.status === 403) {
                        errMsg = 'You must be logged in to perform that action.';
                    } else {
                        errMsg = 'Server returned an unexpected response. Please try again.';
                    }
                }

                throw new Error(errMsg);
            }

            // For OK responses, ensure it's JSON before parsing
            if (contentType.includes('application/json')) {
                return response.json();
            }

            // If we got HTML instead of JSON (e.g., login redirect), surface a helpful message
            const text = await response.text();
            console.error('Expected JSON but received HTML:', text.slice(0, 500));
            throw new Error('Unexpected server response (received HTML). You may need to log in.');
        })
        .then(data => {
            if (data && data.success) {
                // Update UI based on Django's response
                if (data.is_favorited) {
                    submitBtn.classList.add('active');
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    submitBtn.title = 'Remove bookmark';
                    showNotification(data.message || 'Job bookmarked!', 'success');
                } else {
                    submitBtn.classList.remove('active');
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    submitBtn.title = 'Add bookmark';

                    // If on favorites page, remove the job card
                    if (window.location.pathname.includes('favorite')) {
                        const jobCard = submitBtn.closest('.job-card');
                        if (jobCard) {
                            jobCard.style.transition = 'opacity 0.3s ease';
                            jobCard.style.opacity = '0';
                            setTimeout(() => {
                                jobCard.remove();
                                // Check if any jobs left
                                const remainingCards = document.querySelectorAll('.job-card');
                                if (remainingCards.length === 0) {
                                    location.reload(); // Show empty state
                                }
                            }, 300);
                        }
                    }

                    showNotification(data.message || 'Bookmark removed', 'info');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification(error.message || 'Failed to update bookmark', 'error');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        });
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
