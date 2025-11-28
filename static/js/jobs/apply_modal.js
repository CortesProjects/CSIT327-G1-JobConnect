// apply_modal.js
(function(){
    'use strict';

    function qs(sel, root=document) { return root.querySelector(sel); }
    function qsa(sel, root=document) { return Array.from(root.querySelectorAll(sel)); }

    function init(){
        const openBtn = qs('#openApplyBtn');
        const modal = qs('#applyModal');
        const overlay = modal ? qs('.apply-modal-overlay', modal) : null;
        const closeEls = modal ? qsa('[data-close]', modal) : [];
        const form = modal ? qs('#applyForm', modal) : null;
        const resumeSelect = modal ? qs('#resumeSelect', modal) : null;
        const coverLetter = modal ? qs('#coverLetter', modal) : null;
        const submitBtn = modal ? qs('#submitApplyBtn', modal) : null;

        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        }

        function openModal(jobId) {
            if (!modal) return;
            modal.classList.add('show');
            modal.setAttribute('aria-hidden', 'false');
            if (form) form.dataset.jobId = jobId || (openBtn ? openBtn.dataset.jobId : '') || '';
            if (resumeSelect) resumeSelect.focus();
            document.body.style.overflow = 'hidden';
        }

        function closeModal() {
            if (!modal) return;
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }

        function handleSubmit(e) {
            e.preventDefault();
            if (!form) return;
            const jobId = form.dataset.jobId;
            const resumeId = resumeSelect ? resumeSelect.value : '';
            const cover = coverLetter ? coverLetter.value.trim() : '';

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Applying...';
            }

            const url = `/jobs/${jobId}/apply/`;
            const csrftoken = getCookie('csrftoken');

            // Use FormData to send POST data (Django expects form-encoded data)
            const formData = new FormData();
            formData.append('resume_id', resumeId);
            formData.append('cover_letter', cover);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken || '',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(async response => {
                const contentType = (response.headers.get('content-type') || '').toLowerCase();
                
                if (!response.ok) {
                    let errMsg = 'Failed to apply for job.';
                    
                    if (contentType.includes('application/json')) {
                        const data = await response.json();
                        errMsg = data.error || data.message || errMsg;
                    }
                    
                    throw new Error(errMsg);
                }
                
                if (contentType.includes('application/json')) {
                    return response.json();
                }
                
                throw new Error('Unexpected response from server.');
            })
            .then(data => {
                if (data && data.success) {
                    if (openBtn) {
                        openBtn.classList.add('applied');
                        openBtn.innerHTML = '<i class="fas fa-check"></i> Applied';
                        openBtn.setAttribute('disabled', 'disabled');
                    }
                    closeModal();
                    alert(data.message || 'Application submitted successfully!');
                    
                    // Reload page to update "has_applied" state
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    const err = (data && data.error) ? data.error : 'Failed to apply for job.';
                    alert(err);
                }
            })
            .catch(err => {
                console.error('Apply error', err);
                alert(err.message || 'An error occurred while sending your application.');
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Apply Now <i class="fas fa-arrow-right"></i>';
                }
            });
        }

        if (openBtn) {
            openBtn.addEventListener('click', function(e){
                e.preventDefault();
                const jobId = openBtn.dataset.jobId;
                openModal(jobId);
            });
        }

        closeEls.forEach(function(el){
            el.addEventListener('click', function(e){
                e.preventDefault();
                closeModal();
            });
        });

        if (overlay) {
            overlay.addEventListener('click', function(){ closeModal(); });
        }

        document.addEventListener('keydown', function(e){
            if (e.key === 'Escape') closeModal();
        });

        if (form) form.addEventListener('submit', handleSubmit);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
