// Applicant Search Jobs JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize filter form auto-submit
    initFilterAutoSubmit();
    
    // Initialize bookmark functionality
    initBookmarks();
    
    // Initialize sort functionality
    initSortFunctionality();
    
    // Initialize job card interactions
    initJobCardInteractions();
    
});

/**
 * Auto-submit filters when checkboxes or selects change
 */
function initFilterAutoSubmit() {
    const filtersForm = document.getElementById('searchFilterForm');
    if (!filtersForm) return;
    
    // Auto-submit on select change
    const selects = filtersForm.querySelectorAll('.filter-dropdown');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            clearTimeout(window.filterSubmitTimeout);
            window.filterSubmitTimeout = setTimeout(() => {
                filtersForm.submit();
            }, 500);
        });
    });
    
    // Auto-submit on search input with debounce
    const searchInputs = filtersForm.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(window.filterSubmitTimeout);
            window.filterSubmitTimeout = setTimeout(() => {
                filtersForm.submit();
            }, 800);
        });
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
    
    // Toggle visual state immediately for better UX
    if (isBookmarked) {
        button.classList.remove('bookmarked');
        icon.classList.remove('fas');
        icon.classList.add('far');
    } else {
        button.classList.add('bookmarked');
        icon.classList.remove('far');
        icon.classList.add('fas');
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
            showNotification(isBookmarked ? 'Bookmark removed' : 'Job bookmarked!');
        } else {
            // Revert on error
            button.classList.toggle('bookmarked');
            icon.classList.toggle('fas');
            icon.classList.toggle('far');
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Bookmark error:', error);
        // Revert on error
        button.classList.toggle('bookmarked');
        icon.classList.toggle('fas');
        icon.classList.toggle('far');
        showNotification('Failed to update bookmark', 'error');
    });
    */
    
    // For now, just show a notification
    showNotification(
        isBookmarked ? 'Bookmark removed' : 'Job bookmarked!',
        isBookmarked ? 'info' : 'success'
    );
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
 * Initialize job card interactions
 */
function initJobCardInteractions() {
    // View Details buttons
    const viewDetailsButtons = document.querySelectorAll('.btn-view, .btn-action.btn-view');
    viewDetailsButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const jobId = this.getAttribute('data-job-id');
            viewJobDetails(jobId);
        });
    });
    
    // Apply Now buttons
    const applyButtons = document.querySelectorAll('.btn-apply, .btn-action.btn-apply');
    applyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const jobId = this.getAttribute('data-job-id');
            applyToJob(jobId);
        });
    });
}

function viewJobDetails(jobId) {
    // TODO: Implement job details modal or redirect to job details page
    console.log('View job details:', jobId);
    showNotification('Job details page coming soon!', 'info');
    
    // Example implementation:
    // window.location.href = `/jobs/${jobId}/`;
    // Or open a modal with job details
}

function applyToJob(jobId) {
    // TODO: Implement job application flow
    console.log('Apply to job:', jobId);
    showNotification('Application feature coming soon!', 'info');
    
    // Example implementation:
    /*
    if (!confirm('Are you sure you want to apply to this job?')) {
        return;
    }
    
    fetch(`/api/jobs/${jobId}/apply/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Application submitted successfully!', 'success');
            // Update UI to show applied state
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Application error:', error);
        showNotification('Failed to submit application', 'error');
    });
    */
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
