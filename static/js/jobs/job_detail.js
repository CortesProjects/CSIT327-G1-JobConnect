(function(){
    'use strict';

    function qs(sel, root=document) { return root.querySelector(sel); }
    function qsa(sel, root=document) { return Array.from(root.querySelectorAll(sel)); }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Submit POST form to Django (server-side validation)
    function submitPost(url) {
        const formEl = document.createElement('form');
        formEl.method = 'POST';
        formEl.action = url;
        formEl.style.display = 'none';

        const token = getCookie('csrftoken');
        if (token) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = token;
            formEl.appendChild(input);
        }

        document.body.appendChild(formEl);
        formEl.submit();
    }

    // Close modal helper (UI only)
    function closeModalById(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = 'none';
    }

    // Optimistic UI update when marking expired (visual feedback only)
    function markJobExpiredUI() {
        const expireText = qs('.expire-text');
        if (expireText) {
            expireText.innerHTML = '<span class="expire-badge">Expired</span>';
            expireText.classList.add('expired');
        }

        const menuBtn = qs('#jobMenuBtn');
        if (menuBtn) menuBtn.style.pointerEvents = 'none';

        const dropdown = qs('#jobMenuDropdown');
        if (dropdown) {
            qsa('.mark-expired, .delete, .action-edit', dropdown).forEach(el => {
                el.classList.add('disabled');
                el.style.pointerEvents = 'none';
                el.setAttribute('aria-disabled', 'true');
            });
        }
    }

    function init(){
        // Apply modal (applicants)
        const openBtn = qs('#openApplyBtn');
        const applyModal = qs('#applyModal');
        const overlay = applyModal ? qs('.apply-modal-overlay', applyModal) : null;
        const closeEls = applyModal ? qsa('[data-close]', applyModal) : [];
        const applyForm = applyModal ? qs('#applyForm', applyModal) : null;
        const submitBtn = applyModal ? qs('#submitApplyBtn', applyModal) : null;

        function openApplyModal(jobId) {
            if (!applyModal) return;
            applyModal.classList.add('show');
            applyModal.setAttribute('aria-hidden', 'false');
            if (applyForm) applyForm.dataset.jobId = jobId || '';
            document.body.style.overflow = 'hidden';
        }

        function closeApplyModal() {
            if (!applyModal) return;
            applyModal.classList.remove('show');
            applyModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }

        if (openBtn) {
            openBtn.addEventListener('click', function(e){
                e.preventDefault();
                openApplyModal(openBtn.dataset.jobId);
            });
        }

        closeEls.forEach(function(el){
            el.addEventListener('click', function(e){
                e.preventDefault();
                closeApplyModal();
            });
        });

        if (overlay) {
            overlay.addEventListener('click', closeApplyModal);
        }

        if (applyForm) {
            applyForm.addEventListener('submit', function() {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Applying...';
                }
            });
        }

        // Action menu (employers)
        const menuBtn = qs('#jobMenuBtn');
        const menuDropdown = qs('#jobMenuDropdown');
        if (menuBtn && menuDropdown) {
            menuBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                menuDropdown.classList.toggle('show');
            });
            document.addEventListener('click', function(e) {
                if (!menuBtn.contains(e.target)) {
                    menuDropdown.classList.remove('show');
                }
            });
        }

        // Action menu items (mark expired, delete)
        qsa('[data-action="mark-expired"], [data-action="delete"]').forEach(function(actionBtn) {
            actionBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const action = actionBtn.dataset.action;
                const jobId = actionBtn.dataset.jobId;
                if (!jobId) return;

                if (action === 'mark-expired') {
                    const modal = qs('#markExpiredModal');
                    if (modal) {
                        modal.style.display = 'flex';
                        modal.dataset.jobId = jobId;
                    }
                } else if (action === 'delete') {
                    const modal = qs('#deleteJobModal');
                    if (modal) {
                        modal.style.display = 'flex';
                        modal.dataset.jobId = jobId;
                    }
                }
            });
        });

        // Modal close buttons
        qsa('[data-modal-close]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                closeModalById(btn.dataset.modalClose);
            });
        });

        // Confirm buttons (submit POST to Django)
        qsa('[data-confirm="mark-expired"]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const modal = qs('#markExpiredModal');
                const jobId = modal ? modal.dataset.jobId : null;
                if (!jobId) return;

                // Optimistic UI update
                try { markJobExpiredUI(); } catch(e) {}
                
                // Submit to Django
                submitPost(`/jobs/${jobId}/mark-expired/`);
            });
        });

        qsa('[data-confirm="delete"]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const modal = qs('#deleteJobModal');
                const jobId = modal ? modal.dataset.jobId : null;
                if (!jobId) return;

                // Submit to Django
                submitPost(`/jobs/${jobId}/delete/`);
            });
        });

        // ESC to close modals
        document.addEventListener('keydown', function(e){
            if (e.key === 'Escape') {
                closeApplyModal();
                closeModalById('markExpiredModal');
                closeModalById('deleteJobModal');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
