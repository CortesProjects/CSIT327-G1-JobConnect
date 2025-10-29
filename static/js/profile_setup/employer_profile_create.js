// accounts/static/js/employer_profile_create.js

document.addEventListener("DOMContentLoaded", function () {
    // Select main elements
    const richTextToolbar = document.querySelector('.rich-text-toolbar');
    const uploadColumns = document.querySelectorAll('.upload-column');
    const form = document.querySelector('form'); 
    
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

    uploadColumns.forEach(column => {
        const uploadArea = column.querySelector('.upload-area');
        const fileInput = uploadArea.querySelector('input[type="file"]');
        const contentPlaceholder = uploadArea.querySelector('.upload-content-placeholder');
        const fileAttachedDisplay = uploadArea.querySelector('.file-attached-display');
        const fileNameSpan = fileAttachedDisplay.querySelector('.file-name');
        const removeFileBtn = fileAttachedDisplay.querySelector('.remove-file-btn');

        // Function to update display based on file presence
        const updateFileDisplay = () => {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                fileNameSpan.textContent = fileName;
                
                // Hide placeholder, Show file display
                contentPlaceholder.style.display = 'none';
                fileAttachedDisplay.style.display = 'flex'; 
                
                // Update CSS classes for visual feedback
                uploadArea.classList.add('file-attached'); 
                uploadArea.classList.remove('drag-over'); 
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
        }

        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', (e) => {
                e.preventDefault(); 
                e.stopPropagation(); 
                
                // Reset file input value
                fileInput.value = ''; 
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
             form.addEventListener('submit', function() {
                // Ensure all editors are synced before submitting the form
                editorPairs.forEach(pair => {
                    const hiddenInputId = pair.editor.dataset.linkedInput;
                    const hiddenInput = document.querySelector(hiddenInputId);
                    if (hiddenInput) {
                        hiddenInput.value = pair.editor.innerHTML;
                    }
                });
            });
        }
    }
});
