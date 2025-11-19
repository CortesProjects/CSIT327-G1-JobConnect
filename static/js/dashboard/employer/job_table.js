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
        window.location.href = `/dashboard/employer/jobs/${jobId}/detail/`;
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
        window.location.href = `/dashboard/employer/jobs/${jobId}/edit/`;
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

        // Show confirmation dialog
        if (!confirm('Are you sure you want to mark this job as expired?')) {
            return;
        }

        // Send AJAX request to mark job as expired
        this.updateJobStatus(jobId, 'expired');
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

        // Show confirmation dialog
        if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
            return;
        }

        // Send AJAX request to delete job
        this.deleteJob(jobId);
    }

    /**
     * Update job status via AJAX
     * @param {string} jobId - Job ID
     * @param {string} status - New status
     */
    async updateJobStatus(jobId, status) {
        try {
            const csrfToken = this.getCsrfToken();
            
            const response = await fetch(`/dashboard/employer/jobs/${jobId}/update-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ status: status })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show success message
                this.showMessage('Job status updated successfully', 'success');
                
                // Reload page to reflect changes
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.message || 'Failed to update job status');
            }
        } catch (error) {
            console.error('Error updating job status:', error);
            this.showMessage(error.message || 'An error occurred', 'error');
        }
    }

    /**
     * Delete job via AJAX
     * @param {string} jobId - Job ID
     */
    async deleteJob(jobId) {
        try {
            const csrfToken = this.getCsrfToken();
            
            const response = await fetch(`/dashboard/employer/jobs/${jobId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show success message
                this.showMessage('Job deleted successfully', 'success');
                
                // Remove row from table
                const row = document.querySelector(`.job-row[data-job-id="${jobId}"]`);
                if (row) {
                    row.remove();
                }

                // Check if table is now empty
                const remainingRows = document.querySelectorAll('.job-row').length;
                if (remainingRows === 0) {
                    // Reload to show empty state
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            } else {
                throw new Error(data.message || 'Failed to delete job');
            }
        } catch (error) {
            console.error('Error deleting job:', error);
            this.showMessage(error.message || 'An error occurred', 'error');
        }
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
