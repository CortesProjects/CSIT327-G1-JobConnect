// Post Job Form Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Handle rich text editor toolbar buttons
    const toolbarButtons = document.querySelectorAll('.toolbar-btn');
    
    toolbarButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const command = this.getAttribute('data-command');
            
            if (command === 'link') {
                const url = prompt('Enter the URL:');
                if (url) {
                    document.execCommand('createLink', false, url);
                }
            } else {
                document.execCommand(command, false, null);
            }
        });
    });

    // Check for success message and show modal
    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
        const successMessages = messagesContainer.querySelectorAll('.alert-success');
        if (successMessages.length > 0) {
            // Hide messages container
            messagesContainer.style.display = 'none';
            
            // Show success modal
            const modal = document.getElementById('successModal');
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        }
    }

    // Close modal functionality
    const closeModal = document.getElementById('closeModal');
    const successModal = document.getElementById('successModal');
    
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            successModal.classList.remove('show');
            document.body.style.overflow = 'auto';
        });
    }
    
    // Close modal when clicking outside
    if (successModal) {
        successModal.addEventListener('click', function(e) {
            if (e.target === successModal) {
                successModal.classList.remove('show');
                document.body.style.overflow = 'auto';
            }
        });
    }

    // Save editor content to hidden inputs before form submission
    const form = document.querySelector('.post-job-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Clear previous errors
            document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
            document.querySelectorAll('.form-control, .editor-content').forEach(el => {
                el.classList.remove('error');
            });

            let hasError = false;

            // Get description content
            const descriptionEditor = document.getElementById('description');
            const descriptionHidden = document.getElementById('description_hidden');
            if (descriptionEditor && descriptionHidden) {
                const textContent = descriptionEditor.textContent.trim();
                descriptionHidden.value = descriptionEditor.innerHTML;
                
                // Validate description length (minimum 50 characters)
                if (!textContent) {
                    showError(descriptionEditor, 'Job description cannot be empty.');
                    hasError = true;
                } else if (textContent.length < 50) {
                    showError(descriptionEditor, 'Description must be at least 50 characters.');
                    hasError = true;
                }
            }

            // Get responsibilities content
            const responsibilitiesEditor = document.getElementById('responsibilities');
            const responsibilitiesHidden = document.getElementById('responsibilities_hidden');
            if (responsibilitiesEditor && responsibilitiesHidden) {
                responsibilitiesHidden.value = responsibilitiesEditor.innerHTML;
            }

            // Validate required fields
            const requiredFields = [
                { id: 'job_title', message: 'Job title cannot be empty.' },
                { id: 'job_role', message: 'Please select a job role.' },
                { id: 'location', message: 'Location cannot be empty.' },
                { id: 'min_salary', message: 'Minimum salary is required.' },
                { id: 'max_salary', message: 'Maximum salary is required.' },
                { id: 'salary_type', message: 'Please select salary type.' },
                { id: 'education', message: 'Please select education level.' },
                { id: 'experience', message: 'Please select experience level.' },
                { id: 'job_type', message: 'Please select job type.' },
                { id: 'vacancies', message: 'Please select number of vacancies.' },
                { id: 'expiration_date', message: 'Expiration date is required.' },
                { id: 'job_level', message: 'Please select job level.' }
            ];

            requiredFields.forEach(field => {
                const element = document.getElementById(field.id);
                if (element && !element.value.trim()) {
                    showError(element, field.message);
                    hasError = true;
                }
            });

            // Validate salary range
            const minSalary = parseFloat(document.getElementById('min_salary')?.value) || 0;
            const maxSalary = parseFloat(document.getElementById('max_salary')?.value) || 0;
            
            if (minSalary > maxSalary) {
                showError(document.getElementById('min_salary'), 'Minimum salary cannot be greater than maximum salary.');
                hasError = true;
            }

            // Validate expiration date is in the future
            const expirationDate = document.getElementById('expiration_date')?.value;
            if (expirationDate) {
                const selectedDate = new Date(expirationDate);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate < today) {
                    showError(document.getElementById('expiration_date'), 'Deadline must be a future date.');
                    hasError = true;
                }
            }

            if (hasError) {
                e.preventDefault();
                // Scroll to first error
                const firstError = document.querySelector('.error-message:not(:empty)');
                if (firstError) {
                    firstError.closest('.form-group').scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return false;
            }
        });
    }

    function showError(element, message) {
        element.classList.add('error');
        const errorId = element.id + '_error';
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    // Date input formatting (simple implementation)
    const dateInput = document.getElementById('expiration_date');
    if (dateInput) {
        dateInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove non-digits
            
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            if (value.length >= 5) {
                value = value.substring(0, 5) + '/' + value.substring(5, 9);
            }
            
            e.target.value = value;
        });

        // Optionally, you can use a date picker library or HTML5 date input
        // For better UX, consider using a library like flatpickr or converting to type="date"
    }

    // Salary validation - ensure max is greater than min
    const minSalary = document.getElementById('min_salary');
    const maxSalary = document.getElementById('max_salary');

    if (minSalary && maxSalary) {
        maxSalary.addEventListener('blur', function() {
            const min = parseFloat(minSalary.value) || 0;
            const max = parseFloat(maxSalary.value) || 0;

            if (max > 0 && min > 0 && max < min) {
                alert('Maximum salary must be greater than minimum salary');
                maxSalary.value = '';
                maxSalary.focus();
            }
        });
    }

    // Add focus styling to editor content
    const editorContents = document.querySelectorAll('.editor-content');
    editorContents.forEach(editor => {
        editor.addEventListener('focus', function() {
            this.parentElement.querySelector('.editor-toolbar').style.borderColor = 'var(--primary-color)';
        });

        editor.addEventListener('blur', function() {
            this.parentElement.querySelector('.editor-toolbar').style.borderColor = '#e0e0e0';
        });
    });

    // Modal functionality
    const modal = document.getElementById('successModal');
    const closeModalBtn = document.getElementById('closeModal');

    // Function to show modal
    function showModal() {
        if (modal) {
            modal.classList.add('show');
        }
    }

    // Function to hide modal
    function hideModal() {
        if (modal) {
            modal.classList.remove('show');
        }
    }

    // Close modal when clicking the X button
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', hideModal);
    }

    // Close modal when clicking outside the modal content
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideModal();
            }
        });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('show')) {
            hideModal();
        }
    });

    // Show modal on successful form submission
    // This would typically be triggered after a successful AJAX request
    // or you can add a URL parameter check if redirecting back after success
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true') {
        showModal();
    }
});

