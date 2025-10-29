document.addEventListener('DOMContentLoaded', function() {
    const resumeUploadArea = document.querySelector('.resume-upload-area');
    if (!resumeUploadArea) return;

    const fileInput = resumeUploadArea.querySelector('.actual-file-input');
    const placeholder = resumeUploadArea.querySelector('.upload-content-placeholder');
    const fileDisplay = resumeUploadArea.querySelector('.file-attached-display');
    const fileNameSpan = fileDisplay.querySelector('.file-name');
    const removeFileBtn = fileDisplay.querySelector('.remove-file-btn');

    function updateFileDisplay() {
        if (fileInput.files.length > 0) {
            // A file IS selected
            const file = fileInput.files[0];
            fileNameSpan.textContent = file.name;
            
            placeholder.style.display = 'none';
            fileDisplay.style.display = 'flex';
            
            // ADD THIS LINE to add the class for compact styling
            resumeUploadArea.classList.add('file-attached');

        } else {
            // NO file is selected
            placeholder.style.display = 'flex'; // Use flex for better centering
            fileDisplay.style.display = 'none';

            // ADD THIS LINE to remove the class and restore initial styling
            resumeUploadArea.classList.remove('file-attached');
        }
    }

    // Event listener for when a file is chosen
    fileInput.addEventListener('change', updateFileDisplay);

    // Event listener for the remove button
    removeFileBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileInput.value = '';
        updateFileDisplay(); // This will now also remove the class
    });

    // Initial check
    updateFileDisplay();
});