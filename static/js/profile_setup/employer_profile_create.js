// accounts/static/js/employer_profile_create.js

document.addEventListener("DOMContentLoaded", function () {
    // Select main elements
    const richTextToolbar = document.querySelector('.rich-text-toolbar');
    const uploadColumns = document.querySelectorAll('.upload-column');
    const form = document.querySelector('form');

    // Small helper to show a field-level error when applicable
    function showFieldError(fieldName, message) {
        try {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) field.classList.add('is-invalid');
            const id = `${fieldName.replace(/_/g,'-')}-error`;
            const err = document.getElementById(id);
            if (err) { err.textContent = message; err.style.display = 'block'; }
        } catch (e) { console.warn('showFieldError:', e); }
    }
    
    // =========================================================
    // ERROR HANDLING: Auto-scroll to first error on page load
    // =========================================================
    const firstError = document.querySelector('.error-text:not(:empty)');
    if (firstError) {
        // Scroll to the first error message
        setTimeout(() => {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    }
    
    // --- NEW: Date Picker Logic Setup ---
    document.querySelectorAll('.date-input-wrapper').forEach(wrapper => {
        const dateInput = wrapper.querySelector('.date-picker-input');
        const dateIcon = wrapper.querySelector('.date-icon');

        if (dateInput && dateIcon) {
            // Add a click listener to the custom icon
            dateIcon.addEventListener('click', () => {
                // Programmatically trigger a click event on the hidden input field
                dateInput.click();
            });
        }
    });
    // --- END NEW DATE PICKER LOGIC ---


    // --- Select ALL potential editor/toolbar pairs ---
    // This allows the script to work on both step1 (About Us) and step2 (Company Vision)
    const editorPairs = [];
    const aboutUsEditor = document.querySelector('#about-us-editor');
    const companyVisionEditor = document.querySelector('#company-vision-editor');
    // Note: richTextToolbar is selected earlier in the file

    // Add pairs if they exist on the current page
    if (aboutUsEditor && richTextToolbar) {
        editorPairs.push({ editor: aboutUsEditor, toolbar: richTextToolbar });
    }
    if (companyVisionEditor && richTextToolbar) {
        // Note: Assuming both editors share the same single toolbar element.
        editorPairs.push({ editor: companyVisionEditor, toolbar: richTextToolbar });
    }

    // =========================================================
    // 0. INITIALIZATION ROUTINE (FIX FOR DATA LOSS)
    // =========================================================
    const initializeEditor = (editor) => {
        if (editor) {
            const hiddenInputId = editor.dataset.linkedInput;
            const hiddenInput = document.querySelector(hiddenInputId);
            
            if (hiddenInput && hiddenInput.value.length > 0) {
                // If saved data exists in the hidden input, load it into the visible div
                editor.innerHTML = hiddenInput.value;
            }
        }
    };
    
    // Initialize ALL editors found on the page
    editorPairs.forEach(pair => initializeEditor(pair.editor));


    // =========================================================
    // 1. FILE INPUT AND DRAG & DROP UX (Step 1 Logic)
    // =========================================================

    // Logo upload handling
    const logoPreview = document.getElementById('logo-preview');
    // Try multiple possible field names to support form/model renames
    const logoInput = document.querySelector(
        'input[id="id_logo"], input[id="id_company_profile_image"], input[name="logo"], input[name="company_profile_image"], input[name="company_logo"], input[name="profile_image"]'
    );
    
    if (logoPreview && logoInput) {
        // Add click handler to the preview container (works for initial and after upload)
        logoPreview.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            logoInput.click();
        });

        logoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate image type and size
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (!validTypes.includes(file.type)) {
                    showFieldError('logo', 'Please upload a valid image (JPG, PNG or GIF).');
                    logoInput.value = '';
                    return;
                }
                if (file.size > maxSize) {
                    showFieldError('logo', 'Image size must be less than 5MB.');
                    logoInput.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(event) {
                    // Clear existing content
                    logoPreview.innerHTML = '';
                    
                    // Create image element
                    const img = document.createElement('img');
                    img.src = event.target.result;
                    img.alt = 'Company Logo';
                    logoPreview.appendChild(img);
                    
                    // Create overlay
                    const overlay = document.createElement('div');
                    overlay.className = 'hover-overlay-setup';
                    overlay.innerHTML = `
                        <i class="fas fa-cloud-upload-alt"></i>
                        <p><span>Change photo</span> or drop here</p>
                        <small>Max photo size 5 MB</small>
                    `;
                    logoPreview.appendChild(overlay);
                    
                    logoPreview.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            }
        });

        // Drag and drop for logo
        ['dragover', 'dragleave', 'drop'].forEach(event => {
            logoPreview.addEventListener(event, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        logoPreview.addEventListener('dragover', () => {
            logoPreview.style.borderColor = '#DC3545';
        });
        
        logoPreview.addEventListener('dragleave', () => {
            logoPreview.style.borderColor = '';
        });

        logoPreview.addEventListener('drop', (e) => {
            logoPreview.style.borderColor = '';
            if (e.dataTransfer.files.length) {
                logoInput.files = e.dataTransfer.files;
                logoInput.dispatchEvent(new Event('change'));
            }
        });
    }

    // Business permit upload handling
    const permitPreview = document.getElementById('permit-preview');
    const permitInput = document.querySelector(
        'input[id="id_business_permit"], input[id="id_company_business_permit"], input[name="business_permit"], input[name="company_business_permit"], input[name="business_permit_file"]'
    );
    
    if (permitPreview && permitInput) {
        // Add click handler to the preview container (works for initial and after upload)
        permitPreview.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            permitInput.click();
        });

        permitInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type and size
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (!validTypes.includes(file.type)) {
                    showFieldError('business_permit', 'Please upload a valid image or PDF.');
                    permitInput.value = '';
                    return;
                }
                if (file.size > maxSize) {
                    showFieldError('business_permit', 'File size must be less than 5MB.');
                    permitInput.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(event) {
                    // Clear existing content
                    permitPreview.innerHTML = '';
                    
                    if (file.type === 'application/pdf') {
                        // Show PDF icon for PDF files
                        const placeholder = document.createElement('div');
                        placeholder.className = 'upload-content-placeholder';
                        placeholder.innerHTML = `
                            <i class="fas fa-file-pdf" style="font-size: 3rem; color: #dc3545;"></i>
                            <h4>${file.name}</h4>
                            <p class="upload-hint">PDF Document</p>
                        `;
                        permitPreview.appendChild(placeholder);
                    } else {
                        // Show image preview for image files
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        img.alt = 'Business Permit';
                        permitPreview.appendChild(img);
                    }
                    
                    // Create overlay
                    const overlay = document.createElement('div');
                    overlay.className = 'hover-overlay-setup';
                    overlay.innerHTML = `
                        <i class="fas fa-cloud-upload-alt"></i>
                        <p><span>Change file</span> or drop here</p>
                        <small>Max file size 5 MB</small>
                    `;
                    permitPreview.appendChild(overlay);
                    
                    permitPreview.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            }
        });

        // Drag and drop for permit
        ['dragover', 'dragleave', 'drop'].forEach(event => {
            permitPreview.addEventListener(event, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        permitPreview.addEventListener('dragover', () => {
            permitPreview.style.borderColor = '#DC3545';
        });
        
        permitPreview.addEventListener('dragleave', () => {
            permitPreview.style.borderColor = '';
        });

        permitPreview.addEventListener('drop', (e) => {
            permitPreview.style.borderColor = '';
            if (e.dataTransfer.files.length) {
                permitInput.files = e.dataTransfer.files;
                permitInput.dispatchEvent(new Event('change'));
            }
        });
    }

    // OLD LOGIC - Keep for backward compatibility if other pages use .upload-column
    uploadColumns.forEach(column => {
        const uploadArea = column.querySelector('.upload-area');
        if (!uploadArea) return; // Skip if no upload area in this column
        
        const fileInput = uploadArea.querySelector('input[type="file"]');
        if (!fileInput) return;
        
        const contentPlaceholder = uploadArea.querySelector('.upload-content-placeholder');
        const fileAttachedDisplay = uploadArea.querySelector('.file-attached-display');
        if (!fileAttachedDisplay) return;
        
        const fileNameSpan = fileAttachedDisplay.querySelector('.file-name');
        const removeFileBtn = fileAttachedDisplay.querySelector('.remove-file-btn');
        const existingFile = uploadArea.dataset.existingFile;

        // Function to update display based on file presence
        const updateFileDisplay = () => {
            const hasNewFile = fileInput.files.length > 0;
            const hasExistingFile = existingFile && existingFile.trim() !== '';

            if (hasNewFile) {
                const file = fileInput.files[0];
                const fileName = file.name;

                // If image file, render inline preview (like applicant setup)
                if (file.type && file.type.startsWith('image/')) {
                    // Validate image type and size (match applicant rules)
                    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                    const maxSize = 5 * 1024 * 1024; // 5MB
                    if (!validTypes.includes(file.type)) {
                        showFieldError(fileInput.name || 'image', 'Please upload a valid image (JPG, PNG or GIF).');
                        fileInput.value = '';
                        return;
                    }
                    if (file.size > maxSize) {
                        showFieldError(fileInput.name || 'image', 'Image size must be less than 5MB.');
                        fileInput.value = '';
                        return;
                    }

                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Build preview image + overlay to match applicant setup design
                        contentPlaceholder.innerHTML = '';
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = 'Preview';
                        img.className = 'upload-inline-image';
                        contentPlaceholder.appendChild(img);

                        const overlay = document.createElement('div');
                        overlay.className = 'hover-overlay-setup';
                        overlay.innerHTML = `\
                            <i class="fas fa-cloud-upload-alt"></i>\
                            <p><span>Change file</span> or drop here</p>\
                            <small>Max file size 5 MB</small>`;
                        contentPlaceholder.appendChild(overlay);

                        contentPlaceholder.style.display = 'flex';
                        contentPlaceholder.style.flexDirection = 'column';
                        fileAttachedDisplay.style.display = 'none';

                        // Add a flag class to allow CSS to style previews consistently
                        uploadArea.classList.add('has-image');
                    };
                    reader.readAsDataURL(file);
                } else {
                    // Non-image files: show filename
                    fileNameSpan.textContent = fileName;
                    contentPlaceholder.style.display = 'none';
                    fileAttachedDisplay.style.display = 'flex';
                }

                uploadArea.classList.add('file-attached');
                uploadArea.classList.remove('drag-over');
            } else if (hasExistingFile) {
                // Show existing file name or preview if image
                const fileName = existingFile.split('/').pop();
                const lower = fileName.toLowerCase();
                if (lower.match(/\.(jpg|jpeg|png|gif)$/)) {
                    // show image in placeholder — assume media URL handling elsewhere
                    contentPlaceholder.innerHTML = '';
                    const img = document.createElement('img');
                    img.src = '/' + existingFile;
                    img.alt = 'Preview';
                    img.className = 'upload-inline-image';
                    contentPlaceholder.appendChild(img);

                    const overlay = document.createElement('div');
                    overlay.className = 'hover-overlay-setup';
                    overlay.innerHTML = `\
                        <i class="fas fa-cloud-upload-alt"></i>\
                        <p><span>Change file</span> or drop here</p>\
                        <small>Max file size 5 MB</small>`;
                    contentPlaceholder.appendChild(overlay);

                    contentPlaceholder.style.display = 'flex';
                    contentPlaceholder.style.flexDirection = 'column';
                    fileAttachedDisplay.style.display = 'none';
                    uploadArea.classList.add('has-image');
                } else {
                    fileNameSpan.textContent = fileName + ' (uploaded)';
                    contentPlaceholder.style.display = 'none';
                    fileAttachedDisplay.style.display = 'flex';
                    uploadArea.classList.remove('has-image');
                }
                uploadArea.classList.add('file-attached');
            } else {
                // Show placeholder, Hide file display
                contentPlaceholder.style.display = 'flex';
                contentPlaceholder.style.flexDirection = 'column'; // Ensure vertical centering
                fileAttachedDisplay.style.display = 'none';

                // Update CSS classes
                uploadArea.classList.remove('file-attached');
            }
        };

        // --- Event Listeners ---
        if (fileInput) {
            fileInput.addEventListener('change', updateFileDisplay);
            // Make the entire upload area clickable to open the file dialog
            if (uploadArea) {
                uploadArea.addEventListener('click', function(e) {
                    // Prevent triggering when clicking the remove button
                    if (e.target && e.target.closest && e.target.closest('.remove-file-btn')) return;
                    fileInput.click();
                });
            }
        }

        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', (e) => {
                e.preventDefault(); 
                e.stopPropagation(); 
                
                // Reset file input value
                fileInput.value = '';
                // Clear the existing file reference
                uploadArea.dataset.existingFile = '';
                updateFileDisplay(); 
            });
        }

        // --- Drag & Drop UX Logic ---
        ['dragover', 'dragleave', 'drop'].forEach(event => {
            uploadArea.addEventListener(event, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        uploadArea.addEventListener('dragover', () => {
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            uploadArea.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files; 
                // Manually trigger change event to update the UI
                fileInput.dispatchEvent(new Event('change')); 
            }
        });

        // Initialize display on page load
        updateFileDisplay(); 
    });

    // =========================================================
    // 2. RICH TEXT TOOLBAR (Functional Implementation)
    // =========================================================
    
    if (editorPairs.length > 0) {
        
        // --- A. Toolbar Functionality (Applied once to the single toolbar) ---
        richTextToolbar.addEventListener('click', function(e) {
            e.preventDefault();
            const button = e.target.closest('button');

            if (button) {
                let command = button.dataset.command; 

                // Execute standard formatting commands
                if (command && command !== 'createLink') {
                    document.execCommand(command, false, null);
                
                } else if (command === 'createLink') {
                    const url = prompt('Enter the URL:', 'http://');
                    if (url) {
                        document.execCommand('createLink', false, url);
                    }
                }
                
                // Find the currently focused editor to ensure focus after command
                const currentEditor = document.activeElement;
                if (currentEditor.contentEditable === 'true') {
                    currentEditor.focus();
                } else {
                    editorPairs[0].editor.focus();
                }
            }
        });
        
        // --- B. Data Sync on Input (Applied to all editors) ---
        editorPairs.forEach(pair => {
            pair.editor.addEventListener('input', function() {
                const hiddenInputId = pair.editor.dataset.linkedInput;
                const hiddenInput = document.querySelector(hiddenInputId);
                if (hiddenInput) {
                    // Copy the HTML content into the hidden field
                    hiddenInput.value = pair.editor.innerHTML;
                }
            });
        });


        // --- C. Data Sync on Form Submission (CRITICAL) ---
        if (form) {
             form.addEventListener('submit', function(e) {
                // Ensure all editors are synced before submitting the form
                editorPairs.forEach(pair => {
                    const hiddenInputId = pair.editor.dataset.linkedInput;
                    const hiddenInput = document.querySelector(hiddenInputId);
                    if (hiddenInput) {
                        hiddenInput.value = pair.editor.innerHTML;
                    }
                });
                // Backend will handle validation
            });
        }

        // === Phone code auto-detection (Step 3) ===
        const phoneCodeSelect = document.getElementById('phone-code-select');
        const phoneInput = document.querySelector('input[name="contact_phone_number"]');
        if (phoneCodeSelect && phoneInput) {
            const normalize = s => (s||"").toString().replace(/^\+|\s|\-|\.|\(|\)/g,'');
            const tryDetect = () => {
                const raw = phoneInput.value.trim();
                if (!raw) return;
                // 1) +NNN prefix
                let match = raw.match(/^(\+\d{1,3})/);
                let code = null;
                if (match) code = match[1];
                else {
                    // 2) 00NNN prefix
                    let m2 = raw.match(/^00(\d{1,3})/);
                    if (m2) code = '+' + m2[1];
                    else {
                        // 3) try to match available options by numeric prefix without plus
                        const norm = normalize(raw);
                        for (const opt of phoneCodeSelect.options) {
                            const optCode = normalize(opt.value);
                            if (optCode && norm.startsWith(optCode)) { code = '+' + optCode; break; }
                        }
                    }
                }
                if (code) {
                    if (phoneCodeSelect.value !== code) phoneCodeSelect.value = code;
                    // remove the detected code from the input so number holds the national part
                    const codeNoPlus = code.replace('+','');
                    let cleaned = raw.replace(new RegExp('^\\+?' + codeNoPlus), '');
                    // handle leading 0s, spaces, dashes
                    cleaned = cleaned.replace(/^[-.\s\(\)0]+/, '');
                    phoneInput.value = cleaned;
                }
            };
            // run on blur and on load
            phoneInput.addEventListener('blur', tryDetect);
            tryDetect();

            // when select changes, ensure number doesn't duplicate code
            phoneCodeSelect.addEventListener('change', () => {
                const raw = phoneInput.value.trim();
                if (!raw) return;
                const normRaw = normalize(raw);
                const selected = normalize(phoneCodeSelect.value);
                if (selected && normRaw.startsWith(selected)) {
                    phoneInput.value = raw.replace(new RegExp('^\\+?' + selected), '');
                }
            });
        }
    }
});
