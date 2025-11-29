/**
 * Post Job Form - Dynamic Styling & UI Only
 * All validation is handled by Django backend
 */

document.addEventListener('DOMContentLoaded', function() {
    // Rich text editor toolbar
    const toolbarButtons = document.querySelectorAll('.toolbar-btn');
    
    toolbarButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const command = this.getAttribute('data-command');
            
            if (command === 'link') {
                const url = prompt('Enter the URL:');
                if (url) { document.execCommand('createLink', false, url); }
            } else {
                document.execCommand(command, false, null);
            }
        });
    });

    // Prefill editor content when editing
    const prefillDesc = document.getElementById('description');
    const prefillResp = document.getElementById('responsibilities');
    const descHidden = document.getElementById('description_hidden') || document.getElementById('id_description');
    const respHidden = document.getElementById('responsibilities_hidden') || document.getElementById('id_responsibilities');

    if (prefillDesc && descHidden && descHidden.value) { prefillDesc.innerHTML = descHidden.value; }
    if (prefillResp && respHidden && respHidden.value) { prefillResp.innerHTML = respHidden.value; }

    // Form submission - sync editor content to hidden inputs
    const form = document.querySelector('.post-job-form');
    if (form) {
        form.addEventListener('submit', function() {
            const descEditor = document.getElementById('description');
            const descHiddenInput = document.getElementById('description_hidden');
            if (descEditor && descHiddenInput) { descHiddenInput.value = descEditor.innerHTML; }

            const respEditor = document.getElementById('responsibilities');
            const respHiddenInput = document.getElementById('responsibilities_hidden');
            if (respEditor && respHiddenInput) { respHiddenInput.value = respEditor.innerHTML; }
        });
    }

    // Editor focus styling
    document.querySelectorAll('.editor-content').forEach(editor => {
        editor.addEventListener('focus', function() {
            const toolbar = this.parentElement.querySelector('.editor-toolbar');
            if (toolbar) toolbar.style.borderColor = 'var(--primary-color)';
        });
        editor.addEventListener('blur', function() {
            const toolbar = this.parentElement.querySelector('.editor-toolbar');
            if (toolbar) toolbar.style.borderColor = '#e0e0e0';
        });
        editor.addEventListener('input', function() {
            if (this.id === 'description' && descHidden) descHidden.value = this.innerHTML;
            if (this.id === 'responsibilities' && respHidden) respHidden.value = this.innerHTML;
        });
    });

    // Clear error styling on input (visual feedback only)
    document.querySelectorAll('.form-control, .editor-content, input, select, textarea').forEach(field => {
        const clearError = function() {
            this.classList.remove('error');
            const errorEl = document.getElementById(this.id + '_error');
            if (errorEl && this.value && this.value.trim()) {
                errorEl.textContent = '';
                errorEl.style.display = 'none';
            }
        };
        field.addEventListener('input', clearError);
        field.addEventListener('change', clearError);
        field.addEventListener('focus', function() { this.classList.remove('error'); });
    });

    // Success modal handling
    const modal = document.getElementById('successModal');
    const closeModalBtn = document.getElementById('closeModal');

    function showModal() {
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    function hideModal() {
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = 'auto';
        }
    }

    if (closeModalBtn) closeModalBtn.addEventListener('click', hideModal);
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) hideModal();
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('show')) hideModal();
    });

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true') showModal();
});
