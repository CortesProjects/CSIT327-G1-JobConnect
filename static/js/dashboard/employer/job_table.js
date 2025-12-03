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
                // Show loading state
                this.setButtonLoading(confirmBtn, true, 'Mark as Expired');
                
                // Submit via AJAX
                this.submitMarkExpired(`/jobs/${jobId}/mark-expired/`, jobId, modal, confirmBtn);
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
                // Show loading state
                this.setButtonLoading(confirmBtn, true, 'Delete');
                
                // Submit delete request
                this.submitDelete(`/jobs/${jobId}/delete/`, jobId, modal, confirmBtn);
            };
            modal.style.display = 'flex';
        }
    }

    /**
     * Set button loading state
     * @param {HTMLElement} button - Button element
     * @param {boolean} loading - Loading state
     * @param {string} originalText - Original button text
     */
    setButtonLoading(button, loading, originalText) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = originalText || button.textContent;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || originalText;
        }
    }

    /**
     * Submit mark as expired request
     * @param {string} url - URL to submit to
     * @param {string} jobId - Job ID
     * @param {HTMLElement} modal - Modal element
     * @param {HTMLElement} button - Button element
     */
    submitMarkExpired(url, jobId, modal, button) {
        const csrfToken = this.getCsrfToken();
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Reset button state
                this.setButtonLoading(button, false);
                
                // Close modal
                modal.style.display = 'none';

                // Update UI: find the row and set status to expired
                const actionBtn = document.querySelector(`.action-mark-expired[data-job-id="${jobId}"]`);
                if (actionBtn) {
                    const row = actionBtn.closest('.jt-row');
                    if (row) {
                        const statusCol = row.querySelector('.col-status');
                        if (statusCol) {
                            statusCol.innerHTML = '<span class="status expired">✕ Expired</span>';
                        }
                        // Remove mark-expired button from dropdown
                        actionBtn.remove();
                    }
                }

                // Show message
                this.showMessage(data.message || 'Job marked as expired.', 'success');
            } else {
                // Reset button state on error
                this.setButtonLoading(button, false);
                
                const err = (data && data.error) ? data.error : 'Failed to mark job as expired.';
                this.showMessage(err, 'error');
            }
        })
        .catch((err) => {
            // Reset button state on error
            this.setButtonLoading(button, false);
            
            console.error('Mark expired error:', err);
            this.showMessage('Network error while marking job expired.', 'error');
        });
    }

    /**
     * Submit delete request
     * @param {string} url - URL to submit to
     * @param {string} jobId - Job ID
     * @param {HTMLElement} modal - Modal element
     * @param {HTMLElement} button - Button element
     */
    submitDelete(url, jobId, modal, button) {
        const csrfToken = this.getCsrfToken();
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Reset button state
                this.setButtonLoading(button, false);
                
                // Close modal
                modal.style.display = 'none';

                // Remove the row from UI
                const actionBtn = document.querySelector(`.action-delete[data-job-id="${jobId}"]`);
                if (actionBtn) {
                    const row = actionBtn.closest('.jt-row');
                    if (row) {
                        row.style.transition = 'opacity 0.3s ease';
                        row.style.opacity = '0';
                        setTimeout(() => row.remove(), 300);
                    }
                }

                // Show message
                this.showMessage(data.message || 'Job deleted successfully.', 'success');
                
                // Reload page after 1 second to refresh the list
                setTimeout(() => window.location.reload(), 1000);
            } else {
                // Reset button state on error
                this.setButtonLoading(button, false);
                
                const err = (data && data.error) ? data.error : 'Failed to delete job.';
                this.showMessage(err, 'error');
            }
        })
        .catch((err) => {
            // Reset button state on error
            this.setButtonLoading(button, false);
            
            console.error('Delete error:', err);
            this.showMessage('Network error while deleting job.', 'error');
        });
    }

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
