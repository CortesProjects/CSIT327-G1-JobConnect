/**
 * Applicant Profile Creation - Dynamic Styling & UI Only
 * All validation is handled by Django backend
 */

document.addEventListener('DOMContentLoaded', function() {
    // Resume file upload display
    const resumeUploadArea = document.querySelector('.resume-upload-area');
    if (resumeUploadArea) {
        const fileInput = resumeUploadArea.querySelector('input[type="file"]');
        const placeholder = resumeUploadArea.querySelector('.upload-content-placeholder');
        const fileDisplay = resumeUploadArea.querySelector('.file-attached-display');
        const fileNameSpan = fileDisplay ? fileDisplay.querySelector('.file-name') : null;
        const removeFileBtn = fileDisplay ? fileDisplay.querySelector('.remove-file-btn') : null;

        function updateFileDisplay() {
            if (fileInput && fileInput.files.length > 0) {
                const file = fileInput.files[0];
                if (fileNameSpan) fileNameSpan.textContent = file.name;
                if (placeholder) placeholder.style.display = 'none';
                if (fileDisplay) fileDisplay.style.display = 'flex';
                resumeUploadArea.classList.add('file-attached');
            } else {
                const existingFileName = fileNameSpan ? fileNameSpan.textContent.trim() : '';
                if (!existingFileName || existingFileName === '') {
                    if (placeholder) placeholder.style.display = 'flex'; 
                    if (fileDisplay) fileDisplay.style.display = 'none';
                    resumeUploadArea.classList.remove('file-attached');
                }
            }
        }

        if (fileInput) fileInput.addEventListener('change', updateFileDisplay);
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

    // Profile picture preview
    const imageInput = document.getElementById('id_profile_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('profile-preview-setup');
                    if (preview) {
                        let img = preview.querySelector('img');
                        if (img) {
                            img.src = event.target.result;
                        } else {
                            img = document.createElement('img');
                            img.src = event.target.result;
                            img.alt = 'Profile Preview';
                            preview.innerHTML = '';
                            preview.appendChild(img);
                            
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
    
    // Clear error styling on input (visual feedback only)
    document.querySelectorAll('input, select, textarea').forEach(field => {
        const clearError = function() {
            this.classList.remove('error', 'is-invalid');
            this.style.borderColor = '';
            const errorDiv = document.getElementById(this.name.replace(/_/g, '-') + '-error');
            if (errorDiv && (this.value.trim() || this.checked)) {
                errorDiv.textContent = '';
                errorDiv.style.display = 'none';
            }
        };
        field.addEventListener('input', clearError);
        field.addEventListener('change', clearError);
        field.addEventListener('focus', function() {
            this.classList.remove('error', 'is-invalid');
            this.style.borderColor = '';
        });
    });

    // Scroll to first error if present (visual aid)
    const firstError = document.querySelector('.error-text:not(:empty)');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Step 4: Resume Upload Functionality
    const resumeForm = document.getElementById('resumeUploadForm');
    if (resumeForm) {
        const resumeFileInput = resumeForm.querySelector('input[type="file"]');
        const resumeUploadArea = document.getElementById('uploadArea');
        const resumeUploadPrompt = document.getElementById('uploadPrompt');
        const resumeFilePreview = document.getElementById('filePreview');
        const resumeFileName = document.getElementById('fileName');
        const resumeNameInput = resumeForm.querySelector('input[name="resume_name"]');

        // Format file size
        function formatFileSize(bytes) {
            if (!bytes) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }

        // Validate file
        function validateResumeFile(file) {
            const maxSize = 5 * 1024 * 1024; // 5MB
            const allowedExtensions = ['pdf', 'doc', 'docx'];
            const fileExtension = file.name.split('.').pop().toLowerCase();

            if (file.size > maxSize) {
                return `File size (${formatFileSize(file.size)}) exceeds the 5MB limit.`;
            }

            if (!allowedExtensions.includes(fileExtension)) {
                return `File type ".${fileExtension}" is not allowed. Please upload PDF, DOC, or DOCX files only.`;
            }

            return null;
        }

        // Show error
        function showResumeError(elementId, message) {
            const errorEl = document.getElementById(elementId);
            if (errorEl) {
                errorEl.textContent = message;
                errorEl.classList.add('active');
            }
        }

        // Clear errors
        function clearResumeErrors() {
            document.querySelectorAll('.error-message').forEach(el => {
                el.textContent = '';
                el.classList.remove('active');
            });
        }

        // Display file
        function displayResumeFile(file) {
            const error = validateResumeFile(file);
            if (error) {
                showResumeError('resume-file-error', error);
                resumeFileInput.value = '';
                return;
            }

            clearResumeErrors();
            resumeFileName.textContent = file.name + ' (' + formatFileSize(file.size) + ')';
            resumeUploadArea.classList.add('file-attached');
            resumeUploadPrompt.style.display = 'none';
            resumeFilePreview.style.display = 'flex';
        }

        // Remove file
        window.removeFile = function() {
            resumeFileInput.value = '';
            resumeUploadArea.classList.remove('file-attached');
            resumeUploadPrompt.style.display = 'block';
            resumeFilePreview.style.display = 'none';
            clearResumeErrors();
        };

        // File input change
        if (resumeFileInput) {
            resumeFileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    displayResumeFile(file);
                } else {
                    window.removeFile();
                }
            });
        }

        // Drag and drop
        if (resumeUploadArea) {
            resumeUploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.classList.add('drag-over');
            });

            resumeUploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.classList.remove('drag-over');
            });

            resumeUploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.classList.remove('drag-over');

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    resumeFileInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    resumeFileInput.dispatchEvent(event);
                }
            });
        }

        // Form validation
        resumeForm.addEventListener('submit', function(e) {
            clearResumeErrors();
            let hasErrors = false;

            // Validate resume name
            if (!resumeNameInput || !resumeNameInput.value.trim()) {
                showResumeError('resume-name-error', 'Please enter a resume name.');
                if (resumeNameInput) resumeNameInput.focus();
                hasErrors = true;
                e.preventDefault();
                return;
            }

            // Validate file
            if (!resumeFileInput || !resumeFileInput.files || resumeFileInput.files.length === 0) {
                showResumeError('resume-file-error', 'Please select a file to upload.');
                hasErrors = true;
                e.preventDefault();
                return;
            }

            if (!hasErrors) {
                const submitBtn = resumeForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
                }
            }
        });

        // Clear error on input
        if (resumeNameInput) {
            resumeNameInput.addEventListener('input', function() {
                clearResumeErrors();
            });
        }
    }
});
