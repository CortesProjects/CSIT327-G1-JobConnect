// employer_settings.js
// UI-only behaviors for employer settings page. All validation is server-side.

(function () {
    'use strict';

    // Tab switching functionality
    function initTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetTab = this.getAttribute('data-tab');

                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Add active class to clicked button and corresponding content
                this.classList.add('active');
                document.getElementById(targetTab).classList.add('active');
            });
        });
    }

    // Password toggle visibility (UI-only)
    function initPasswordToggles() {
        document.querySelectorAll('.toggle-password').forEach(toggle => {
            toggle.addEventListener('click', function () {
                const input = this.previousElementSibling;
                if (!input) return;
                
                if (input.type === 'password') {
                    input.type = 'text';
                    this.classList.remove('fa-eye');
                    this.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    this.classList.remove('fa-eye-slash');
                    this.classList.add('fa-eye');
                }
            });
        });
    }

    // Password change UX: strength meter and match indicator (visual only, no validation)
    function initPasswordChangeUX() {
        const newPass = document.querySelector('input[name="new_password1"]');
        const confirmPass = document.querySelector('input[name="new_password2"]');
        if (!newPass && !confirmPass) return;

        function createStrengthNode() {
            const container = document.createElement('div');
            container.className = 'password-strength';
            container.innerHTML = `
                <div class="bar" aria-hidden="true"><span></span></div>
                <div class="label">&nbsp;</div>
            `;
            return container;
        }

        function createMatchNode() {
            const container = document.createElement('div');
            container.className = 'password-match';
            container.innerHTML = `<div class="match">&nbsp;</div>`;
            return container;
        }

        let strengthNode, matchNode;
        if (newPass) {
            const parent = newPass.closest('.form-group') || newPass.parentNode;
            strengthNode = createStrengthNode();
            parent.appendChild(strengthNode);
        }

        if (confirmPass) {
            const parent = confirmPass.closest('.form-group') || confirmPass.parentNode;
            matchNode = createMatchNode();
            parent.appendChild(matchNode);
        }

        function scorePassword(pwd) {
            let score = 0;
            if (!pwd) return score;
            if (pwd.length >= 8) score += 1;
            if (/[A-Z]/.test(pwd)) score += 1;
            if (/[0-9]/.test(pwd)) score += 1;
            if (/[^A-Za-z0-9]/.test(pwd)) score += 1;
            if (pwd.length >= 12) score += 1;
            return score; // 0-5
        }

        function updateStrength(pwd) {
            if (!strengthNode) return;
            const score = scorePassword(pwd);
            const bar = strengthNode.querySelector('.bar span');
            const label = strengthNode.querySelector('.label');
            const percentage = Math.min(100, Math.round((score / 5) * 100));
            bar.style.width = percentage + '%';
            
            let text = 'Too weak';
            let cls = 'weak';
            if (score >= 4) { text = 'Strong'; cls = 'strong'; }
            else if (score >= 3) { text = 'Good'; cls = 'good'; }
            else if (score >= 1) { text = 'Weak'; cls = 'weak'; }
            if (!pwd) { text = ''; cls = ''; bar.style.width = '0%'; }
            
            strengthNode.classList.remove('weak', 'good', 'strong');
            if (cls) strengthNode.classList.add(cls);
            label.textContent = text;
        }

        function updateMatch() {
            if (!matchNode) return;
            const matchEl = matchNode.querySelector('.match');
            const a = newPass ? newPass.value : '';
            const b = confirmPass ? confirmPass.value : '';
            
            if (!b && !a) {
                matchEl.textContent = '';
                matchNode.classList.remove('good', 'bad');
                return;
            }
            
            if (a === b && a.length > 0) {
                matchEl.textContent = 'Passwords match';
                matchNode.classList.remove('bad');
                matchNode.classList.add('good');
            } else {
                matchEl.textContent = 'Passwords do not match';
                matchNode.classList.remove('good');
                matchNode.classList.add('bad');
            }
        }

        if (newPass) {
            newPass.addEventListener('input', function () {
                updateStrength(this.value);
                updateMatch();
                this.classList.toggle('valid', scorePassword(this.value) >= 3);
            });
        }

        if (confirmPass) {
            confirmPass.addEventListener('input', function () {
                updateMatch();
            });
        }
    }

    // Dynamic input styling (visual feedback only, no validation)
    function initInputStyling() {
        // Clear error state on input focus
        document.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('focus', function() {
                this.classList.remove('error');
            });
        });

        // Auto-dismiss messages after 5 seconds
        const messages = document.querySelectorAll('.alert, .messages-container .alert-success, .messages-container .alert-error');
        if (messages.length > 0) {
            setTimeout(() => {
                messages.forEach(msg => {
                    msg.style.transition = 'opacity 0.5s ease';
                    msg.style.opacity = '0';
                    setTimeout(() => msg.remove(), 500);
                });
            }, 5000);
        }
    }

    // Social links UI (no validation)
    function initSocialLinks() {
        const addButton = document.querySelector('[data-action="show-add-social-link"]');
        const addForm = document.getElementById('add-social-link-form');
        const cancelBtn = document.querySelector('[data-action="cancel-add-social-link"]');

        function hideAdd() {
            if (addForm) addForm.classList.add('is-hidden');
            if (addButton) addButton.classList.remove('is-hidden');
        }

        function showAdd() {
            if (addForm) addForm.classList.remove('is-hidden');
            if (addButton) addButton.classList.add('is-hidden');
        }

        if (addButton) addButton.addEventListener('click', showAdd);
        if (cancelBtn) cancelBtn.addEventListener('click', hideAdd);

        document.addEventListener('click', function (e) {
            if (e.target && e.target.dataset && e.target.dataset.action === 'delete-link') {
                const item = e.target.closest('.social-link-item');
                if (item && confirm('Remove this social link? (Changes will apply after clicking Save Changes)')) {
                    item.remove();
                }
            }
        });
    }

    // Delete account modal functionality
    function initDeleteAccount() {
        const deleteBtn = document.getElementById('delete-account-btn');
        const modal = document.getElementById('deleteAccountModal');
        const confirmInput = document.getElementById('delete-confirm-text');
        const confirmBtn = document.getElementById('confirm-delete-btn');
        
        window.openDeleteAccountModal = function() {
            if (modal) {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        };
        
        window.closeDeleteAccountModal = function() {
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
                const form = document.getElementById('deleteAccountForm');
                if (form) form.reset();
                if (confirmBtn) confirmBtn.disabled = true;
            }
        };
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', window.openDeleteAccountModal);
        }
        
        // Enable delete button only when "DELETE" is typed
        if (confirmInput && confirmBtn) {
            confirmInput.addEventListener('input', function() {
                confirmBtn.disabled = this.value.trim() !== 'DELETE';
            });
        }
        
        // Close modal on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
                window.closeDeleteAccountModal();
            }
        });
    }

    // Init all
    document.addEventListener('DOMContentLoaded', function () {
        initTabs();
        initPasswordToggles();
        initPasswordChangeUX();
        initInputStyling();
        initSocialLinks();
        initDeleteAccount();
    });

})();
