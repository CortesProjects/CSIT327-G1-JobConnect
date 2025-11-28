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
            // Allow the form to submit normally so Django handles the POST.
            // We do minimal UI changes: disable the submit button to prevent double submits.
            if (!form) return;

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Applying...';
            }

            // Do not call e.preventDefault(); let the browser submit the form.
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
