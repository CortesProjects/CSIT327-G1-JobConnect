/**
 * Job Table Management
 * Handles job listing interactions, dropdowns, and actions
 */

class JobTableManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEventListeners();
        this.setupOutsideClickHandler();
    }

    /**
     * Bind all event listeners
     */
    bindEventListeners() {
        // Action menu toggle buttons
        document.querySelectorAll('.btn-action-menu').forEach(button => {
            button.addEventListener('click', (e) => this.toggleActionMenu(e));
        });

        // View detail buttons
        document.querySelectorAll('.action-view-detail').forEach(button => {
            button.addEventListener('click', (e) => this.handleViewDetail(e));
        });

        // Edit buttons
        document.querySelectorAll('.action-edit').forEach(button => {
            button.addEventListener('click', (e) => this.handleEdit(e));
        });

        // Mark as expired buttons
        document.querySelectorAll('.action-mark-expired').forEach(button => {
            button.addEventListener('click', (e) => this.handleMarkExpired(e));
        });

        // Delete buttons
        document.querySelectorAll('.action-delete').forEach(button => {
            button.addEventListener('click', (e) => this.handleDelete(e));
        });
    }

    /**
     * Toggle action dropdown menu
     * @param {Event} event - Click event
     */
    toggleActionMenu(event) {
        event.stopPropagation();
        const dropdown = event.currentTarget.nextElementSibling;
        
        // Close all other dropdowns
        document.querySelectorAll('.action-dropdown').forEach(d => {
            if (d !== dropdown) {
                d.classList.remove('show');
            }
        });
        
        // Toggle current dropdown
        dropdown.classList.toggle('show');
    }

    /**
     * Setup handler to close dropdowns when clicking outside
     */
    setupOutsideClickHandler() {
        document.addEventListener('click', (event) => {
            // Check if click is outside any dropdown
            if (!event.target.closest('.btn-action-menu') && 
                !event.target.closest('.action-dropdown')) {
                document.querySelectorAll('.action-dropdown').forEach(dropdown => {
                    dropdown.classList.remove('show');
                });
            }
        });
    }

    /**
     * Handle view detail action
     * @param {Event} event - Click event
     */
    handleViewDetail(event) {
        const jobId = event.currentTarget.dataset.jobId;
        if (!jobId) {
            console.error('Job ID not found');
            return;
        }
        
        // Navigate to job detail page
        window.location.href = `/jobs/${jobId}/`;
    }

    /**
     * Handle edit action
     * @param {Event} event - Click event
     */
    handleEdit(event) {
        const jobId = event.currentTarget.dataset.jobId;
        if (!jobId) {
            console.error('Job ID not found');
            return;
        }
        
        // Navigate to edit page
        window.location.href = `/dashboard/employer/edit-job/${jobId}/`;
    }

    /**
     * Handle mark as expired action
     * @param {Event} event - Click event
     */
    handleMarkExpired(event) {
        const jobId = event.currentTarget.dataset.jobId;
        if (!jobId) {
            console.error('Job ID not found');
            return;
        }

        // Show modal instead of confirm dialog
        this.showMarkExpiredModal(jobId);
    }

    /**
     * Handle delete action
     * @param {Event} event - Click event
     */
    handleDelete(event) {
        const jobId = event.currentTarget.dataset.jobId;
        if (!jobId) {
            console.error('Job ID not found');
            return;
        }

        // Show modal instead of confirm dialog
        this.showDeleteModal(jobId);
    }

    /**
     * Show mark as expired modal
     * @param {string} jobId - Job ID
     */
    showMarkExpiredModal(jobId) {
        const modal = document.getElementById('markExpiredModal');
        if (modal) {
            const confirmBtn = modal.querySelector('#confirmMarkExpired');
            confirmBtn.onclick = () => {
                // Submit a POST form so Django performs all validation and handling server-side
                this.submitPost(`/jobs/${jobId}/mark-expired/`);
            };
            modal.style.display = 'flex';
        }
    }

    /**
     * Show delete modal
     * @param {string} jobId - Job ID
     */
    showDeleteModal(jobId) {
        const modal = document.getElementById('deleteJobModal');
        if (modal) {
            const confirmBtn = modal.querySelector('#confirmDelete');
            confirmBtn.onclick = () => {
                // Submit a POST form so Django performs all validation and handling server-side
                this.submitPost(`/jobs/${jobId}/delete/`);
            };
            modal.style.display = 'flex';
        }
    }

    /**
     * Close modal
     * @param {string} modalId - Modal ID
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Mark job as expired via AJAX
     * @param {string} jobId - Job ID
     */
    // Submit a POST form to the given URL so Django handles validation and response.
    submitPost(url) {
        // Create a hidden form and submit it. This keeps server-side validation centralised.
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        form.style.display = 'none';

        // CSRF token
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
        }

        document.body.appendChild(form);
        form.submit();
    }

    /**
     * Delete job via AJAX
     * @param {string} jobId - Job ID
     */
    // deleteJob removed — use submitPost(url) instead to let Django validate and process the request.

    /**
     * Get CSRF token from cookie
     * @returns {string} CSRF token
     */
    getCsrfToken() {
        const name = 'csrftoken';
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

    /**
     * Show message to user
     * @param {string} message - Message text
     * @param {string} type - Message type (success, error, warning, info)
     */
    showMessage(message, type = 'info') {
        // Check if Django messages framework element exists
        const messagesContainer = document.querySelector('.messages');
        
        if (messagesContainer) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = message;
            messagesContainer.appendChild(messageDiv);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        } else {
            // Fallback to alert
            alert(message);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new JobTableManager();
});

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobTableManager;
}
