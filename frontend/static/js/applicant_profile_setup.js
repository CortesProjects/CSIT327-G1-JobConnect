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
            const file = fileInput.files[0];
            
            fileNameSpan.textContent = file.name;
            placeholder.style.display = 'none';
            fileDisplay.style.display = 'flex';
            resumeUploadArea.classList.add('file-attached');

        } else {
            placeholder.style.display = 'flex'; 
            fileDisplay.style.display = 'none';
            resumeUploadArea.classList.remove('file-attached');
        }
    }

    fileInput.addEventListener('change', updateFileDisplay);

    removeFileBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileInput.value = '';
        updateFileDisplay(); 
    });

    updateFileDisplay();
});