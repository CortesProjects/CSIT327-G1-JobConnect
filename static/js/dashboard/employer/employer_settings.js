// Employer Settings Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // Image upload functionality
    setupImageUpload('logo');
    setupImageUpload('banner');

    function setupImageUpload(type) {
        const input = document.getElementById(`${type}-upload`);
        const preview = document.getElementById(`${type}-preview`);
        const replaceBtn = document.querySelector(`[data-target="${type}"].replace-btn`);
        const removeBtn = document.querySelector(`[data-target="${type}"].remove-btn`);

        // Click on preview to trigger file input
        if (preview) {
            preview.addEventListener('click', function() {
                input.click();
            });
        }

        // Replace button
        if (replaceBtn) {
            replaceBtn.addEventListener('click', function(e) {
                e.preventDefault();
                input.click();
            });
        }

        // Remove button
        if (removeBtn) {
            removeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                input.value = '';
                preview.innerHTML = `
                    <div class="preview-placeholder">
                        <i class="fas fa-image"></i>
                    </div>
                `;
            });
        }

        // Handle file selection
        if (input) {
            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.innerHTML = `<img src="${e.target.result}" alt="${type}">`;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    // Rich text editor toolbar
    const editorToolbars = document.querySelectorAll('.editor-toolbar');
    editorToolbars.forEach(toolbar => {
        const buttons = toolbar.querySelectorAll('.toolbar-btn');
        buttons.forEach(button => {
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
    });

    // Save editor content to hidden inputs before form submission
    const forms = document.querySelectorAll('.settings-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // About Us
            const aboutUsEditor = document.getElementById('about-us');
            const aboutUsHidden = document.getElementById('about-us-hidden');
            if (aboutUsEditor && aboutUsHidden) {
                aboutUsHidden.value = aboutUsEditor.innerHTML;
            }

            // Company Vision
            const visionEditor = document.getElementById('company-vision');
            const visionHidden = document.getElementById('company-vision-hidden');
            if (visionEditor && visionHidden) {
                visionHidden.value = visionEditor.innerHTML;
            }
        });
    });

    // Social links management
    const addSocialBtn = document.getElementById('add-social-link');
    const socialLinksContainer = document.getElementById('social-links-container');
    let socialLinkCount = 4;

    if (addSocialBtn) {
        addSocialBtn.addEventListener('click', function() {
            socialLinkCount++;
            const newRow = document.createElement('div');
            newRow.className = 'social-link-row';
            newRow.innerHTML = `
                <div class="form-group">
                    <label>Social Link ${socialLinkCount}</label>
                    <select class="social-select" name="social_platform_${socialLinkCount}">
                        <option value="facebook">Facebook</option>
                        <option value="twitter">Twitter</option>
                        <option value="instagram">Instagram</option>
                        <option value="linkedin">LinkedIn</option>
                        <option value="youtube">YouTube</option>
                        <option value="pinterest">Pinterest</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>&nbsp;</label>
                    <input type="url" name="social_url_${socialLinkCount}" placeholder="Profile link/url...">
                </div>
                <button type="button" class="btn-remove-social">
                    <i class="fas fa-times-circle"></i>
                </button>
            `;
            socialLinksContainer.appendChild(newRow);

            // Add remove functionality to new button
            const removeBtn = newRow.querySelector('.btn-remove-social');
            removeBtn.addEventListener('click', function() {
                newRow.remove();
            });
        });
    }

    // Remove social link functionality for existing rows
    const removeSocialBtns = document.querySelectorAll('.btn-remove-social');
    removeSocialBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Are you sure you want to remove this social link?')) {
                this.closest('.social-link-row').remove();
            }
        });
    });

    // Password toggle functionality
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Password validation
    const newPasswordInput = document.getElementById('new-password');
    const confirmPasswordInput = document.getElementById('confirm-password');

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('blur', function() {
            if (newPasswordInput && this.value !== newPasswordInput.value) {
                this.setCustomValidity('Passwords do not match');
                this.reportValidity();
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Close account functionality
    const closeAccountBtn = document.getElementById('close-account-btn');
    if (closeAccountBtn) {
        closeAccountBtn.addEventListener('click', function() {
            const confirmed = confirm(
                'Are you sure you want to close your account? This action cannot be undone. ' +
                'You will lose access to all job postings, applications, and company data.'
            );

            if (confirmed) {
                const doubleConfirm = confirm(
                    'This is your final warning. Closing your account will permanently delete all your data. ' +
                    'Do you really want to proceed?'
                );

                if (doubleConfirm) {
                    // Submit form or make API call to close account
                    console.log('Account closure requested');
                    // window.location.href = '/close-account/';
                    alert('Account closure request submitted. Please check your email for further instructions.');
                }
            }
        });
    }

    // Date input formatting for establishment year
    const establishmentYearInput = document.getElementById('establishment-year');
    if (establishmentYearInput) {
        establishmentYearInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove non-digits

            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            if (value.length >= 5) {
                value = value.substring(0, 5) + '/' + value.substring(5, 9);
            }

            e.target.value = value;
        });
    }

    // Form validation
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#e74c3c';
                } else {
                    field.style.borderColor = '#e0e0e0';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });

    // Auto-save draft (optional feature)
    let autoSaveTimeout;
    const autoSaveInputs = document.querySelectorAll('input, textarea, select');

    autoSaveInputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                // Save draft to localStorage
                const formData = {};
                autoSaveInputs.forEach(inp => {
                    if (inp.name) {
                        formData[inp.name] = inp.value;
                    }
                });
                localStorage.setItem('employer_settings_draft', JSON.stringify(formData));
                console.log('Draft auto-saved');
            }, 2000);
        });
    });

    // Load draft on page load
    const savedDraft = localStorage.getItem('employer_settings_draft');
    if (savedDraft) {
        const formData = JSON.parse(savedDraft);
        Object.keys(formData).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input && !input.value) {
                input.value = formData[key];
            }
        });
    }

    // Clear draft after successful submission
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            localStorage.removeItem('employer_settings_draft');
        });
    });
});
