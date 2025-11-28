// Job Alerts - Dynamic Styling and Modal Management
// All validation is handled server-side by Django

document.addEventListener('DOMContentLoaded', function() {
    // Modal elements
    const modal = document.getElementById('alertModal');
    const modalTitle = document.getElementById('modalTitle');
    const alertForm = document.getElementById('alertForm');
    const createAlertBtn = document.getElementById('createAlertBtn');
    const manageAlertsBtn = document.getElementById('manageAlertsBtn');
    const emptyStateAlertBtn = document.getElementById('emptyStateAlertBtn');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');
    const modalSubmitBtn = document.getElementById('modalSubmitBtn');
    const closeAlertsBtn = document.getElementById('closeAlertsBtn');
    const alertsConfigSection = document.getElementById('alertsConfigSection');
    
    let currentAlertId = null;
    let isEditMode = false;

    // Show/hide alerts configuration section
    if (manageAlertsBtn) {
        manageAlertsBtn.addEventListener('click', function() {
            alertsConfigSection.style.display = 'block';
            alertsConfigSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // Hide empty state if present when opening alerts list
            const emptyStateEl = document.querySelector('.empty-state');
            if (emptyStateEl) {
                emptyStateEl.style.display = 'none';
            }
        });
    }

    // Header-level edit button (opens modal populated with the first alert)
    const editAlertBtn = document.getElementById('editAlertBtn');
    if (editAlertBtn) {
        editAlertBtn.addEventListener('click', function() {
            const alertId = this.getAttribute('data-alert-id');
            if (alertId) {
                openModal('edit', alertId);
            }
        });
    }

    if (closeAlertsBtn) {
        closeAlertsBtn.addEventListener('click', function() {
            alertsConfigSection.style.display = 'none';
            // If there are no matching jobs shown, restore the empty state
            const emptyStateEl = document.querySelector('.empty-state');
            if (emptyStateEl) {
                // Determine if there are any job results on the page
                const jobListEl = document.querySelector('.job-alerts-list');
                const jobCards = document.querySelectorAll('.job-card');
                const hasJobResults = (jobListEl && jobCards.length > 0);

                // Show empty state when there are no job results (even if alerts exist)
                if (!hasJobResults) {
                    emptyStateEl.style.display = 'block';
                }
            }
        });
    }

    // Open modal for creating alert
    if (createAlertBtn) {
        createAlertBtn.addEventListener('click', function() {
            openModal('create');
        });
    }

    if (emptyStateAlertBtn) {
        emptyStateAlertBtn.addEventListener('click', function() {
            if (document.querySelectorAll('.alert-card').length > 0) {
                // If alerts exist, show manage alerts section
                alertsConfigSection.style.display = 'block';
                alertsConfigSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                // Otherwise open create modal
                openModal('create');
            }
        });
    }

    // Edit alert buttons
    document.querySelectorAll('.alert-action-btn.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const alertId = this.getAttribute('data-alert-id');
            openModal('edit', alertId);
        });
    });

    // Close modal
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }

    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', closeModal);
    }

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Handle form submission
    if (alertForm) {
        alertForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAlertForm();
        });
    }

    // Handle delete confirmations
    document.querySelectorAll('.delete-alert-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this job alert?')) {
                submitFormWithAjax(this);
            }
        });
    });

    // Handle toggle active status
    document.querySelectorAll('.toggle-alert-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitFormWithAjax(this);
        });
    });

    /**
     * Open modal for creating or editing alert
     */
    function openModal(mode, alertId = null) {
        isEditMode = mode === 'edit';
        currentAlertId = alertId;

        // Reset form
        alertForm.reset();
        clearErrors();

        if (isEditMode && alertId) {
            modalTitle.textContent = 'Edit Job Alert';
            document.querySelector('#modalSubmitBtn .btn-text').textContent = 'Update Alert';
            
            // Fetch alert data and populate form
            fetchAlertData(alertId);
        } else {
            modalTitle.textContent = 'Create Job Alert';
            document.querySelector('#modalSubmitBtn .btn-text').textContent = 'Create Alert';
        }

        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close modal
     */
    function closeModal() {
        modal.classList.remove('show');
        document.body.style.overflow = '';
        alertForm.reset();
        clearErrors();
        currentAlertId = null;
        isEditMode = false;
    }

    /**
     * Fetch alert data for editing
     */
    function fetchAlertData(alertId) {
        showLoading(true);

        fetch(`/dashboard/applicant/job-alerts/${alertId}/edit/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateForm(data.alert);
            } else {
                showError('Failed to load alert data.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while loading alert data.');
        })
        .finally(() => {
            showLoading(false);
        });
    }

    /**
     * Populate form with alert data
     */
    function populateForm(alert) {
        document.getElementById('alert_name').value = alert.alert_name || '';
        document.getElementById('job_title').value = alert.job_title || '';
        document.getElementById('location').value = alert.location || '';
        document.getElementById('job_type').value = alert.job_type || '';
        document.getElementById('job_category').value = alert.job_category || '';
        document.getElementById('min_salary').value = alert.min_salary || '';
        document.getElementById('max_salary').value = alert.max_salary || '';
        document.getElementById('keywords').value = alert.keywords || '';
        document.getElementById('is_active').checked = alert.is_active;
    }

    /**
     * Submit alert form via AJAX
     */
    function submitAlertForm() {
        clearErrors();
        showLoading(true);

        const formData = new FormData(alertForm);
        const url = isEditMode 
            ? `/dashboard/applicant/job-alerts/${currentAlertId}/edit/`
            : '/dashboard/applicant/job-alerts/create/';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message and reload page
                showSuccessToast(data.message);
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Display errors
                if (data.errors) {
                    displayErrors(data.errors);
                } else if (data.error) {
                    showError(data.error);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while saving the alert.');
        })
        .finally(() => {
            showLoading(false);
        });
    }

    /**
     * Submit form via AJAX (for toggle/delete)
     */
    function submitFormWithAjax(form) {
        const formData = new FormData(form);
        const url = form.action;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccessToast(data.message);
                setTimeout(() => {
                    window.location.reload();
                }, 800);
            } else {
                showError(data.error || 'An error occurred.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred.');
        });
    }

    /**
     * Display form errors
     */
    function displayErrors(errors) {
        // Handle non-field errors
        if (errors.__all__) {
            showError(errors.__all__.join(' '));
        }

        // Display field-specific errors
        Object.keys(errors).forEach(field => {
            if (field !== '__all__') {
                const errorElement = document.getElementById(`${field}_error`);
                const inputElement = document.getElementById(field);
                
                if (errorElement && errors[field]) {
                    errorElement.textContent = errors[field].join(' ');
                    errorElement.style.display = 'block';
                }
                
                if (inputElement) {
                    inputElement.classList.add('is-invalid');
                    inputElement.style.borderColor = '#dc3545';
                }
            }
        });
    }

    /**
     * Clear all error messages
     */
    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.textContent = '';
            el.style.display = 'none';
        });

        document.querySelectorAll('.form-control').forEach(el => {
            el.classList.remove('is-invalid');
            el.style.borderColor = '';
        });

        const formErrorMessage = document.getElementById('formErrorMessage');
        if (formErrorMessage) {
            formErrorMessage.textContent = '';
            formErrorMessage.classList.remove('show');
        }
    }

    /**
     * Show general error message
     */
    function showError(message) {
        const formErrorMessage = document.getElementById('formErrorMessage');
        if (formErrorMessage) {
            formErrorMessage.textContent = message;
            formErrorMessage.classList.add('show');
        }
    }

    /**
     * Show loading state on submit button
     */
    function showLoading(loading) {
        const btnText = modalSubmitBtn.querySelector('.btn-text');
        const btnSpinner = modalSubmitBtn.querySelector('.btn-spinner');
        
        if (loading) {
            btnText.style.display = 'none';
            btnSpinner.style.display = 'inline-block';
            modalSubmitBtn.disabled = true;
        } else {
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
            modalSubmitBtn.disabled = false;
        }
    }

    /**
     * Show success toast notification
     */
    function showSuccessToast(message) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'success-toast';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // Add CSS animations
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
});
