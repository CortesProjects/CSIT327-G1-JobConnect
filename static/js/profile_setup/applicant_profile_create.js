document.addEventListener('DOMContentLoaded', function() {
    const firstError = document.querySelector('.error-text:not(:empty)');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    const resumeUploadArea = document.querySelector('.resume-upload-area');
    if (resumeUploadArea) {
        const fileInput = resumeUploadArea.querySelector('input[type="file"]');
        const placeholder = resumeUploadArea.querySelector('.upload-content-placeholder');
        const fileDisplay = resumeUploadArea.querySelector('.file-attached-display');
        const fileNameSpan = fileDisplay.querySelector('.file-name');
        const removeFileBtn = fileDisplay.querySelector('.remove-file-btn');

        function updateFileDisplay() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                // Validate file type
                const validExtensions = ['.pdf', '.doc', '.docx'];
                const fileName = file.name.toLowerCase();
                const isValid = validExtensions.some(ext => fileName.endsWith(ext));
                
                if (!isValid) {
                    alert('Please upload a PDF, DOC, or DOCX file');
                    fileInput.value = '';
                    return;
                }
                
                // Validate file size (5MB max)
                const maxSize = 5 * 1024 * 1024;
                if (file.size > maxSize) {
                    alert('File size must be less than 5MB');
                    fileInput.value = '';
                    return;
                }
                
                fileNameSpan.textContent = file.name;
                
                placeholder.style.display = 'none';
                fileDisplay.style.display = 'flex';
                
                resumeUploadArea.classList.add('file-attached');

            } else {
                // Check if there's an existing file from the server
                const existingFileName = fileNameSpan.textContent.trim();
                if (!existingFileName || existingFileName === '') {
                    placeholder.style.display = 'flex'; 
                    fileDisplay.style.display = 'none';
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
                fileNameSpan.textContent = '';
                updateFileDisplay(); 
            });
        }

        updateFileDisplay();
    }

    // Profile picture preview functionality
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    alert('Please upload a valid image file (JPG, PNG, or GIF)');
                    e.target.value = '';
                    return;
                }

                // Validate file size (5MB max)
                const maxSize = 5 * 1024 * 1024; // 5MB in bytes
                if (file.size > maxSize) {
                    alert('File size must be less than 5MB');
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
});