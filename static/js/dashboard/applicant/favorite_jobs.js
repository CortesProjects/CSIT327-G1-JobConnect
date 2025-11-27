/**
 * Favorite Jobs functionality
 * Handles favoriting/unfavoriting jobs via AJAX
 */

document.addEventListener('DOMContentLoaded', function() {
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

    // Handle favorite/bookmark button clicks (supports legacy bookmark classes)
    document.addEventListener('click', function(e) {
        const favoriteBtn = e.target.closest('.favorite-btn, .bookmark-btn, .btn-bookmark');
        if (!favoriteBtn) return;

        e.preventDefault();
        e.stopPropagation();

        // Some older templates used data-job-id on a parent or used data-job-id attribute on span
        const jobId = favoriteBtn.dataset.jobId || favoriteBtn.getAttribute('data-job-id');
        if (!jobId) return;

        // Disable button during request
        favoriteBtn.disabled = true;

        // Make AJAX request to toggle favorite
        fetch(`/jobs/${jobId}/favorite/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Toggle button state
                const icon = favoriteBtn.querySelector('i');
                if (data.is_favorited) {
                    favoriteBtn.classList.add('active');
                    // Ensure icon is a heart
                    icon.classList.remove('far', 'fa-bookmark');
                    icon.classList.add('fas', 'fa-heart');
                    favoriteBtn.title = 'Remove from favorites';
                    
                    // Show success message (optional)
                    showNotification('Job added to favorites!', 'success');
                } else {
                    favoriteBtn.classList.remove('active');
                    icon.classList.remove('fas', 'fa-heart');
                    icon.classList.add('far', 'fa-heart');
                    favoriteBtn.title = 'Add to favorites';
                    
                    // If on favorites page, remove the job card
                    if (window.location.pathname.includes('favorite')) {
                        const jobCard = favoriteBtn.closest('.job-card');
                        if (jobCard) {
                            jobCard.style.transition = 'opacity 0.3s ease';
                            jobCard.style.opacity = '0';
                            setTimeout(() => jobCard.remove(), 300);
                            
                            // Check if there are any jobs left
                            setTimeout(() => {
                                const remainingCards = document.querySelectorAll('.job-card');
                                if (remainingCards.length === 0) {
                                    location.reload(); // Reload to show empty state
                                }
                            }, 400);
                        }
                    }
                    
                    showNotification('Job removed from favorites', 'info');
                }
            } else {
                showNotification(data.error || 'An error occurred', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to update favorites', 'error');
        })
        .finally(() => {
            favoriteBtn.disabled = false;
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
