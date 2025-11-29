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
});
