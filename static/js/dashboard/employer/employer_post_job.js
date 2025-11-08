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

    // Save editor content to hidden inputs before form submission
    const form = document.querySelector('.post-job-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Get description content
            const descriptionEditor = document.getElementById('description');
            const descriptionHidden = document.getElementById('description_hidden');
            if (descriptionEditor && descriptionHidden) {
                descriptionHidden.value = descriptionEditor.innerHTML;
            }

            // Get responsibilities content
            const responsibilitiesEditor = document.getElementById('responsibilities');
            const responsibilitiesHidden = document.getElementById('responsibilities_hidden');
            if (responsibilitiesEditor && responsibilitiesHidden) {
                responsibilitiesHidden.value = responsibilitiesEditor.innerHTML;
            }

            // Basic validation
            if (!descriptionEditor.textContent.trim()) {
                e.preventDefault();
                alert('Please add a job description');
                descriptionEditor.focus();
                return false;
            }

            if (!responsibilitiesEditor.textContent.trim()) {
                e.preventDefault();
                alert('Please add job responsibilities');
                responsibilitiesEditor.focus();
                return false;
            }
        });
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
            this.parentElement.querySelector('.editor-toolbar').style.borderColor = '#0066ff';
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

