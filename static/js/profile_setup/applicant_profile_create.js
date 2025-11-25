document.addEventListener('DOMContentLoaded', function() {
    // ========================================
    // ERROR HANDLING & DYNAMIC STYLING
    // ========================================
    
    /**
     * Display error for a specific field
     * @param {string} fieldName - The name attribute of the form field
     * @param {string} errorMessage - The error message to display
     */
    function showFieldError(fieldName, errorMessage) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        const errorDiv = document.getElementById(`${fieldName.replace(/_/g, '-')}-error`);
        
        if (field) {
            field.classList.add('is-invalid');
            field.style.borderColor = '#dc3545';
        }
        
        if (errorDiv) {
            errorDiv.textContent = errorMessage;
            errorDiv.style.display = 'block';
            errorDiv.style.color = '#dc3545';
        }
    }
    
    /**
     * Clear error for a specific field
     * @param {string} fieldName - The name attribute of the form field
     */
    function clearFieldError(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        const errorDiv = document.getElementById(`${fieldName.replace(/_/g, '-')}-error`);
        
        if (field) {
            field.classList.remove('is-invalid');
            field.style.borderColor = '';
        }
        
        if (errorDiv) {
            errorDiv.textContent = '';
            errorDiv.style.display = 'none';
        }
    }
    
    /**
     * Real-time validation for text inputs
     */
    function attachFieldValidation() {
        // First Name validation
        const firstNameField = document.querySelector('[name="first_name"]');
        if (firstNameField) {
            firstNameField.addEventListener('blur', function() {
                const value = this.value.trim();
                clearFieldError('first_name');
                
                if (!value) {
                    showFieldError('first_name', 'First name is required.');
                } else if (value.length < 2) {
                    showFieldError('first_name', 'First name must be at least 2 characters long.');
                } else if (!/^[a-zA-Z\s\-]+$/.test(value)) {
                    showFieldError('first_name', 'First name can only contain letters, spaces, and hyphens.');
                }
            });
            
            firstNameField.addEventListener('input', function() {
                if (this.value.trim()) {
                    clearFieldError('first_name');
                }
            });
        }
        
        // Last Name validation
        const lastNameField = document.querySelector('[name="last_name"]');
        if (lastNameField) {
            lastNameField.addEventListener('blur', function() {
                const value = this.value.trim();
                clearFieldError('last_name');
                
                if (!value) {
                    showFieldError('last_name', 'Last name is required.');
                } else if (value.length < 2) {
                    showFieldError('last_name', 'Last name must be at least 2 characters long.');
                } else if (!/^[a-zA-Z\s\-]+$/.test(value)) {
                    showFieldError('last_name', 'Last name can only contain letters, spaces, and hyphens.');
                }
            });
            
            lastNameField.addEventListener('input', function() {
                if (this.value.trim()) {
                    clearFieldError('last_name');
                }
            });
        }
        
        // Middle Name validation (optional but format check)
        const middleNameField = document.querySelector('[name="middle_name"]');
        if (middleNameField) {
            middleNameField.addEventListener('blur', function() {
                const value = this.value.trim();
                clearFieldError('middle_name');
                
                if (value && !/^[a-zA-Z\s\-]+$/.test(value)) {
                    showFieldError('middle_name', 'Middle name can only contain letters, spaces, and hyphens.');
                }
            });
            
            middleNameField.addEventListener('input', function() {
                clearFieldError('middle_name');
            });
        }
        
        // Contact Number validation (Step 3)
        const contactField = document.querySelector('[name="contact_number"]');
        if (contactField) {
            contactField.addEventListener('blur', function() {
                const value = this.value.trim();
                clearFieldError('contact_number');
                
                if (!value) {
                    showFieldError('contact_number', 'Contact number is required.');
                } else {
                    const digitsOnly = value.replace(/\D/g, '');
                    if (digitsOnly.length < 10) {
                        showFieldError('contact_number', 'Contact number must be at least 10 digits.');
                    } else if (digitsOnly.length > 15) {
                        showFieldError('contact_number', 'Contact number cannot exceed 15 digits.');
                    }
                }
            });
            
            contactField.addEventListener('input', function() {
                if (this.value.trim()) {
                    clearFieldError('contact_number');
                }
            });
        }
        
        // Date of Birth validation (Step 2)
        const dobField = document.querySelector('[name="date_of_birth"]');
        if (dobField) {
            dobField.addEventListener('change', function() {
                clearFieldError('date_of_birth');
                
                if (this.value) {
                    const dob = new Date(this.value);
                    const today = new Date();
                    const age = today.getFullYear() - dob.getFullYear();
                    const monthDiff = today.getMonth() - dob.getMonth();
                    const dayDiff = today.getDate() - dob.getDate();
                    const actualAge = (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) ? age - 1 : age;
                    
                    if (actualAge < 16) {
                        showFieldError('date_of_birth', 'You must be at least 16 years old.');
                    } else if (actualAge > 100) {
                        showFieldError('date_of_birth', 'Please enter a valid date of birth.');
                    }
                }
            });
        }
        
        // Select fields - clear error on change
        const selectFields = ['experience', 'education_level', 'gender', 'marital_status'];
        selectFields.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.addEventListener('change', function() {
                    if (this.value) {
                        clearFieldError(fieldName);
                    }
                });
            }
        });
        
        // Text fields - clear error on input
        const textFields = ['title', 'nationality', 'biography'];
        textFields.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.addEventListener('input', function() {
                    clearFieldError(fieldName);
                });
            }
        });
    }
    
    // Initialize field validation
    attachFieldValidation();
    
    // Scroll to first error if present
    const firstError = document.querySelector('.error-text:not(:empty)');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // ========================================
    // RESUME FILE UPLOAD
    // ========================================
    
    const resumeUploadArea = document.querySelector('.resume-upload-area');
    if (resumeUploadArea) {
        const fileInput = resumeUploadArea.querySelector('input[type="file"]');
        const placeholder = resumeUploadArea.querySelector('.upload-content-placeholder');
        const fileDisplay = resumeUploadArea.querySelector('.file-attached-display');
        const fileNameSpan = fileDisplay ? fileDisplay.querySelector('.file-name') : null;
        const removeFileBtn = fileDisplay ? fileDisplay.querySelector('.remove-file-btn') : null;

        function updateFileDisplay() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                // Clear previous errors
                clearFieldError('resume');
                
                // Validate file type
                const validExtensions = ['.pdf', '.doc', '.docx'];
                const fileName = file.name.toLowerCase();
                const isValid = validExtensions.some(ext => fileName.endsWith(ext));
                
                if (!isValid) {
                    showFieldError('resume', 'Please upload a PDF, DOC, or DOCX file');
                    fileInput.value = '';
                    return;
                }
                
                // Validate file size (5MB max)
                const maxSize = 5 * 1024 * 1024;
                if (file.size > maxSize) {
                    showFieldError('resume', 'File size must be less than 5MB');
                    fileInput.value = '';
                    return;
                }
                
                if (fileNameSpan) {
                    fileNameSpan.textContent = file.name;
                }
                
                if (placeholder) placeholder.style.display = 'none';
                if (fileDisplay) fileDisplay.style.display = 'flex';
                
                resumeUploadArea.classList.add('file-attached');

            } else {
                // Check if there's an existing file from the server
                const existingFileName = fileNameSpan ? fileNameSpan.textContent.trim() : '';
                if (!existingFileName || existingFileName === '') {
                    if (placeholder) placeholder.style.display = 'flex'; 
                    if (fileDisplay) fileDisplay.style.display = 'none';
                    resumeUploadArea.classList.remove('file-attached');
                }
            }
        }

        if (fileInput) {
            fileInput.addEventListener('change', updateFileDisplay);
        }

        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                fileInput.value = '';
                if (fileNameSpan) fileNameSpan.textContent = '';
                updateFileDisplay(); 
            });
        }

        updateFileDisplay();
    }

    // ========================================
    // PROFILE PICTURE PREVIEW
    // ========================================
    
    const imageInput = document.getElementById('id_profile_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Clear previous errors
                clearFieldError('profile_image');
                
                // Validate file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    showFieldError('profile_image', 'Please upload a valid image file (JPG, PNG, or GIF)');
                    e.target.value = '';
                    return;
                }

                // Validate file size (5MB max)
                const maxSize = 5 * 1024 * 1024;
                if (file.size > maxSize) {
                    showFieldError('profile_image', 'File size must be less than 5MB');
                    e.target.value = '';
                    return;
                }

                // Read and display the image
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('profile-preview-setup');
                    if (preview) {
                        // Check if img already exists
                        let img = preview.querySelector('img');
                        if (img) {
                            img.src = event.target.result;
                        } else {
                            // Create new img element
                            img = document.createElement('img');
                            img.src = event.target.result;
                            img.alt = 'Profile Preview';
                            preview.innerHTML = '';
                            preview.appendChild(img);
                            
                            // Re-add hover overlay
                            const overlay = document.createElement('div');
                            overlay.className = 'hover-overlay-setup';
                            overlay.innerHTML = `
                                <i class="fas fa-cloud-upload-alt"></i>
                                <p><span>Change photo</span> or drop here</p>
                                <small>Max photo size 5 MB</small>
                            `;
                            preview.appendChild(overlay);
                        }
                        preview.classList.add('has-image');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // ========================================
    // FORM SUBMISSION VALIDATION
    // ========================================
    
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            let hasErrors = false;
            
            // Step 1 validations
            const firstNameField = document.querySelector('[name="first_name"]');
            if (firstNameField) {
                const value = firstNameField.value.trim();
                if (!value) {
                    showFieldError('first_name', 'First name is required.');
                    hasErrors = true;
                } else if (value.length < 2) {
                    showFieldError('first_name', 'First name must be at least 2 characters long.');
                    hasErrors = true;
                }
            }
            
            const lastNameField = document.querySelector('[name="last_name"]');
            if (lastNameField) {
                const value = lastNameField.value.trim();
                if (!value) {
                    showFieldError('last_name', 'Last name is required.');
                    hasErrors = true;
                } else if (value.length < 2) {
                    showFieldError('last_name', 'Last name must be at least 2 characters long.');
                    hasErrors = true;
                }
            }
            
            const experienceField = document.querySelector('[name="experience"]');
            if (experienceField && !experienceField.value) {
                showFieldError('experience', 'Please select your years of experience.');
                hasErrors = true;
            }
            
            const educationField = document.querySelector('[name="education_level"]');
            if (educationField && !educationField.value) {
                showFieldError('education_level', 'Please select your education level.');
                hasErrors = true;
            }
            
            const resumeField = document.querySelector('[name="resume"]');
            if (resumeField && resumeField.required && !resumeField.value && !resumeField.dataset.hasExisting) {
                showFieldError('resume', 'Please upload your resume.');
                hasErrors = true;
            }
            
            // Step 2 validations
            const dobField = document.querySelector('[name="date_of_birth"]');
            if (dobField && dobField.required && !dobField.value) {
                showFieldError('date_of_birth', 'Date of birth is required.');
                hasErrors = true;
            }
            
            // Step 3 validations
            const contactField = document.querySelector('[name="contact_number"]');
            if (contactField) {
                const value = contactField.value.trim();
                if (!value) {
                    showFieldError('contact_number', 'Contact number is required.');
                    hasErrors = true;
                } else {
                    const digitsOnly = value.replace(/\D/g, '');
                    if (digitsOnly.length < 10) {
                        showFieldError('contact_number', 'Contact number must be at least 10 digits.');
                        hasErrors = true;
                    }
                }
            }
            
            if (hasErrors) {
                e.preventDefault();
                // Scroll to first error
                const firstError = document.querySelector('.error-text:not(:empty)');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
});