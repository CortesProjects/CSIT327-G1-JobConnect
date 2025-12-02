// Applicant Search Jobs JavaScript - Dynamic Styling Only

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize filter toggle panel
    initFilterToggle();
    
    // Initialize bookmark functionality
    initBookmarks();
    
    // Initialize sort functionality (client-side visual sorting only)
    initSortFunctionality();
    
});

/**
 * Toggle hidden filters panel when filter button is clicked
 */
function initFilterToggle(){
    const toggleBtn = document.getElementById('toggleFiltersBtn');
    const panel = document.getElementById('filtersPanel');
    if (!toggleBtn || !panel) return;

    // Simple event listener: toggle open/close and set ARIA attributes
    toggleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const isOpen = panel.classList.toggle('open');
        panel.style.maxHeight = isOpen ? panel.scrollHeight + 'px' : '0px';
        panel.setAttribute('aria-hidden', (!isOpen).toString());
        toggleBtn.setAttribute('aria-expanded', isOpen.toString());
        toggleBtn.classList.toggle('active', isOpen);
    });

    // Close panel when clicking outside
    document.addEventListener('click', function (e) {
        if (!panel.classList.contains('open')) return;
        if (!panel.contains(e.target) && !toggleBtn.contains(e.target)) {
            panel.classList.remove('open');
            panel.style.maxHeight = '0px';
            panel.setAttribute('aria-hidden', 'true');
            toggleBtn.setAttribute('aria-expanded', 'false');
            toggleBtn.classList.remove('active');
        }
    });
}

/**
 * Handle bookmark button clicks
 */
function initBookmarks() {
    const bookmarkButtons = document.querySelectorAll('.bookmark-btn');
    
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const jobId = this.getAttribute('data-job-id');
            toggleBookmark(this, jobId);
        });
    });
}

function toggleBookmark(button, jobId) {
    const icon = button.querySelector('i');
    const isBookmarked = button.classList.contains('bookmarked');
    
    // Disable button and show loading state
    button.disabled = true;
    const originalIcon = icon.className;
    icon.className = 'fas fa-spinner fa-spin';
    
    // Toggle visual state immediately for better UX
    if (isBookmarked) {
        button.classList.remove('bookmarked');
    } else {
        button.classList.add('bookmarked');
    }
    
    // TODO: Make AJAX request to save/remove bookmark in the backend
    // Example:
    /*
    fetch('/api/jobs/bookmark/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            job_id: jobId,
            action: isBookmarked ? 'remove' : 'add'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update icon based on new state
            if (isBookmarked) {
                icon.classList.remove('fas');
                icon.classList.add('far');
            } else {
                icon.classList.remove('far');
                icon.classList.add('fas');
            }
            button.disabled = false;
            showNotification(isBookmarked ? 'Bookmark removed' : 'Job bookmarked!');
        } else {
            // Revert on error
            button.classList.toggle('bookmarked');
            icon.className = originalIcon;
            button.disabled = false;
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Bookmark error:', error);
        // Revert on error
        button.classList.toggle('bookmarked');
        icon.className = originalIcon;
        button.disabled = false;
        showNotification('Failed to update bookmark', 'error');
    });
    */
    
    // For now, just show a notification and reset state
    setTimeout(() => {
        // Update icon based on new state
        if (isBookmarked) {
            icon.className = 'far fa-bookmark';
        } else {
            icon.className = 'fas fa-bookmark';
        }
        button.disabled = false;
        showNotification(
            isBookmarked ? 'Bookmark removed' : 'Job bookmarked!',
            isBookmarked ? 'info' : 'success'
        );
    }, 500);
}

/**
 * Handle sort functionality
 */
function initSortFunctionality() {
    const sortSelect = document.getElementById('sortBy');
    if (!sortSelect) return;
    
    sortSelect.addEventListener('change', function() {
        const sortValue = this.value;
        const jobsTableBody = document.querySelector('.jobs-table tbody');
        if (!jobsTableBody) return;
        
        const jobs = Array.from(jobsTableBody.querySelectorAll('tr'));
        
        // Sort jobs based on selected option
        jobs.sort((a, b) => {
            switch(sortValue) {
                case 'recent':
                    // Default order (already sorted by posted_at desc from backend)
                    return 0;
                case 'salary-high':
                    return getSalary(b) - getSalary(a);
                case 'salary-low':
                    return getSalary(a) - getSalary(b);
                default:
                    return 0;
            }
        });
        
        // Re-append sorted jobs
        jobs.forEach(job => jobsTableBody.appendChild(job));
    });
}

function getSalary(jobRow) {
    const salaryText = jobRow.querySelector('td:nth-child(3) .salary-range').textContent;
    const salaryMatch = salaryText.match(/₱([\d,]+)/);
    return salaryMatch ? parseInt(salaryMatch[1].replace(/,/g, '')) : 0;
}



/**
 * Utility: Show notification
 */
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Utility: Get CSRF token
 */
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

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
