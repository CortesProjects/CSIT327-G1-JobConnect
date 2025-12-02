// applicant_settings.js
// UI-only behaviors for applicant settings page. All validation is server-side.

(function () {
    'use strict';

    // Helpers
    function formatFileSize(bytes) {
        if (!bytes) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    // Profile picture preview (no validation here; server validates on submit)
    function initProfilePreview() {
        const input = document.querySelector('input[name="profile_image"]') || document.getElementById('id_profile_image');
        if (!input) return;

        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (ev) {
                const preview = document.getElementById('profile-preview');
                if (preview) {
                    let img = preview.querySelector('img');
                    if (img) {
                        img.src = ev.target.result;
                    } else {
                        preview.innerHTML = `\n                            <img src="${ev.target.result}" alt="Profile Preview">\n                            <div class="hover-overlay">\n                                <i class="fas fa-cloud-upload-alt"></i>\n                                <p><span>Browse photo</span> or drop here</p>\n                                <small>Max photo size 5 MB</small>\n                            </div>`;
                    }
                    preview.classList.add('has-image');
                } else {
                    const emptyBox = document.querySelector('.profile-picture .empty-state-box');
                    if (emptyBox) {
                        const previewDiv = document.createElement('div');
                        previewDiv.className = 'image-preview has-image';
                        previewDiv.id = 'profile-preview';
                        previewDiv.onclick = function () { (document.querySelector('input[name="profile_image"]') || document.getElementById('id_profile_image')).click(); };
                        previewDiv.innerHTML = `\n                            <img src="${ev.target.result}" alt="Profile Preview">\n                            <div class="hover-overlay">\n                                <i class="fas fa-cloud-upload-alt"></i>\n                                <p><span>Browse photo</span> or drop here</p>\n                                <small>Max photo size 5 MB</small>\n                            </div>`;
                        emptyBox.parentNode.insertBefore(previewDiv, emptyBox);
                        emptyBox.style.display = 'none';
                    }
                }
            };
            reader.readAsDataURL(file);
        });
    }

    // Tabs
    function initTabs() {
        const tabLinks = Array.from(document.querySelectorAll('.settings-nav a'));
        const tabPanels = Array.from(document.querySelectorAll('.tab-content'));
        if (!tabLinks.length || !tabPanels.length) return;

        function activateTab(targetTab, { updateHash = true, resetTransient = true } = {}) {
            tabLinks.forEach(link => {
                const isActive = link.dataset.tab === targetTab;
                link.classList.toggle('active', isActive);
                link.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });

            tabPanels.forEach(panel => {
                const isActive = panel.id === `${targetTab}-tab`;
                panel.classList.toggle('active', isActive);
                panel.toggleAttribute('hidden', !isActive);
                if (isActive) panel.removeAttribute('aria-hidden'); else panel.setAttribute('aria-hidden', 'true');
            });

            if (resetTransient) {
                document.querySelectorAll('.action-menu').forEach(menu => menu.classList.remove('active'));
                const resumeModal = document.getElementById('resumeModal');
                if (resumeModal && resumeModal.classList.contains('active')) {
                    resumeModal.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }

            if (updateHash) {
                if (window.history && typeof history.replaceState === 'function') {
                    history.replaceState(null, '', `#${targetTab}`);
                } else {
                    window.location.hash = targetTab;
                }
            }
        }

        tabLinks.forEach(link => {
            link.setAttribute('role', 'tab');
            link.setAttribute('aria-controls', `${link.dataset.tab}-tab`);
            link.addEventListener('click', event => {
                event.preventDefault();
                activateTab(link.dataset.tab);
            });
        });

        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.replace('#', '');
            if (hash && tabLinks.some(link => link.dataset.tab === hash)) {
                activateTab(hash, { updateHash: false });
            }
        });

        const initialTab = (() => {
            const hash = window.location.hash.replace('#', '');
            if (hash && tabLinks.some(link => link.dataset.tab === hash)) return hash;
            const activeLink = tabLinks.find(link => link.classList.contains('active'));
            return activeLink ? activeLink.dataset.tab : tabLinks[0]?.dataset.tab;
        })();

        if (initialTab) activateTab(initialTab, { updateHash: false, resetTransient: false });
    }

    // Resume modal & upload area (no validation)
    function initResumeModal() {
        const resumeModal = document.getElementById('resumeModal');
        const uploadArea = document.getElementById('uploadArea');
        const fileAttached = document.getElementById('fileAttached');
        const attachedFileName = document.getElementById('attachedFileName');
        const attachedFileSize = document.getElementById('attachedFileSize');
        const uploadPrompt = document.getElementById('uploadPrompt');
        const resumeInput = document.getElementById('id_file');

        window.openResumeModal = function () {
            if (resumeModal) {
                resumeModal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        };

        window.closeResumeModal = function () {
            if (resumeModal) resumeModal.classList.remove('active');
            document.body.style.overflow = '';
            const form = document.getElementById('resumeForm');
            if (form) form.reset();
            resetUploadArea();
        };

        function resetUploadArea() {
            if (!uploadArea) return;
            uploadArea.classList.remove('has-file');
            if (fileAttached) fileAttached.style.display = 'none';
            if (uploadPrompt) uploadPrompt.style.display = 'flex';
            if (attachedFileName) attachedFileName.textContent = '';
            if (attachedFileSize) attachedFileSize.textContent = '';
        }

        window.resetUploadArea = resetUploadArea;
        window.removeFile = function(event) {
            event.preventDefault();
            event.stopPropagation();
            if (resumeInput) resumeInput.value = '';
            resetUploadArea();
        };

        // Click upload area to trigger file input
        if (uploadArea) {
            uploadArea.addEventListener('click', function() {
                if (resumeInput) resumeInput.click();
            });
        }

        // Handle file selection
        if (resumeInput) {
            resumeInput.addEventListener('change', function (e) {
                const file = e.target.files[0];
                if (!file) { 
                    resetUploadArea(); 
                    return; 
                }
                
                // Update file details display
                if (attachedFileName) attachedFileName.textContent = file.name;
                if (attachedFileSize) attachedFileSize.textContent = formatFileSize(file.size);
                
                // Show file attached section
                if (uploadArea) uploadArea.classList.add('has-file');
                if (fileAttached) fileAttached.style.display = 'flex';
                if (uploadPrompt) uploadPrompt.style.display = 'none';
            });
        }

        // Drag and drop support
        if (uploadArea) {
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.style.borderColor = '#dc3545';
                this.style.backgroundColor = '#fff5f5';
            });

            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.style.borderColor = '#e0e0e0';
                this.style.backgroundColor = '#fafafa';
            });

            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.style.borderColor = '#e0e0e0';
                this.style.backgroundColor = '#fafafa';

                const files = e.dataTransfer.files;
                if (files.length > 0 && resumeInput) {
                    resumeInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    resumeInput.dispatchEvent(event);
                }
            });
        }
    }

    // Social links UI
    function initSocialLinks() {
        const addButton = document.querySelector('[data-action="show-add-social-link"]');
        const addForm = document.getElementById('add-social-link-form');
        const cancelBtn = document.querySelector('[data-action="cancel-add-social-link"]');
        const socialLinksList = document.getElementById('social-links-list');

        function hideAdd() { if (addForm) addForm.classList.add('is-hidden'); if (addButton) addButton.classList.remove('is-hidden'); }
        function showAdd() { if (addForm) addForm.classList.remove('is-hidden'); if (addButton) addButton.classList.add('is-hidden'); }

        if (addButton) addButton.addEventListener('click', showAdd);
        if (cancelBtn) cancelBtn.addEventListener('click', hideAdd);

        document.addEventListener('click', function (e) {
            if (e.target && e.target.dataset && e.target.dataset.action === 'delete-link') {
                const item = e.target.closest('.social-link-item');
                if (item && confirm('Remove this social link? (Changes will apply after clicking Save Changes)')) item.remove();
            }
        });
    }

    // Password toggle visibility
    function initPasswordToggles() {
        document.querySelectorAll('.toggle-password').forEach(toggle => {
            toggle.addEventListener('click', function () {
                const input = this.previousElementSibling;
                if (!input) return;
                if (input.type === 'password') { input.type = 'text'; this.classList.remove('fa-eye'); this.classList.add('fa-eye-slash'); }
                else { input.type = 'password'; this.classList.remove('fa-eye-slash'); this.classList.add('fa-eye'); }
            });
        });
    }

    // Password change UX: strength meter and match indicator (visual only)
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
            if (!b && !a) { matchEl.textContent = '' ; matchNode.classList.remove('good','bad'); return; }
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
        const messages = document.querySelectorAll('.alert');
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

    // Resume action menu toggle
    function initResumeMenuToggle() {
        document.querySelectorAll('.action-menu-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const menu = this.nextElementSibling;
                document.querySelectorAll('.action-menu').forEach(m => { if (m !== menu) m.classList.remove('active'); });
                if (menu) menu.classList.toggle('active');
            });
        });

        document.addEventListener('click', function (e) {
            if (!e.target.closest('.resume-card')) document.querySelectorAll('.action-menu').forEach(menu => menu.classList.remove('active'));
        });
    }

    // Privacy toggle auto-submit functionality
    function initPrivacyToggle() {
        const privacyCheckbox = document.querySelector('#privacy-form input[name="is_public"]');
        const privacyStatus = document.querySelector('.privacy-status');
        const privacyDescription = document.querySelector('.privacy-description');
        
        if (privacyCheckbox && privacyStatus) {
            privacyCheckbox.addEventListener('change', function() {
                // Update UI immediately for better UX
                const isPublic = this.checked;
                privacyStatus.textContent = isPublic ? 'Public' : 'Private';
                if (privacyDescription) {
                    privacyDescription.innerHTML = `Your profile is currently <strong>${isPublic ? 'public' : 'private'}</strong>. ${isPublic ? 'Employers can view your profile.' : 'Only you can view your profile.'}`;
                }
            });
        }
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

    // Resume management functions
    window.toggleResumeMenu = function(btn) {
        const menu = btn.nextElementSibling;
        document.querySelectorAll('.action-menu').forEach(m => { 
            if (m !== menu) m.classList.remove('active'); 
        });
        if (menu) menu.classList.toggle('active');
    };

    window.confirmDeleteResume = function(resumeId, resumeName) {
        if (!confirm(`Are you sure you want to delete "${resumeName}"?`)) {
            return;
        }
        
        fetch(`/resumes/delete/${resumeId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Failed to delete resume');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete resume');
        });
    };

    window.setDefaultResume = function(resumeId) {
        fetch(`/resumes/set-default/${resumeId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Failed to set default resume');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to set default resume');
        });
    };

    // Resume Upload Modal Functions
    window.openResumeModal = function() {
        const modal = document.getElementById('uploadResumeModal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Check if user has no resumes and auto-check "set as default"
            const hasResumes = document.querySelectorAll('.resume-card').length > 0;
            const setDefaultCheckbox = document.getElementById('set_as_default');
            if (setDefaultCheckbox && !hasResumes) {
                setDefaultCheckbox.checked = true;
            }
        }
    };

    window.closeResumeModal = function() {
        const modal = document.getElementById('uploadResumeModal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            const form = document.getElementById('uploadResumeForm');
            if (form) form.reset();
            resetUploadArea();
        }
    };

    function resetUploadArea() {
        const uploadArea = document.getElementById('uploadArea');
        const fileAttached = document.getElementById('fileAttached');
        const uploadPrompt = document.getElementById('uploadPrompt');
        const fileInput = document.getElementById('resume_file');
        
        if (fileInput) fileInput.value = '';
        if (uploadArea) uploadArea.classList.remove('has-file');
        if (fileAttached) fileAttached.style.display = 'none';
        if (uploadPrompt) uploadPrompt.style.display = 'flex';
    }

    window.removeFile = function(event) {
        if (event) event.preventDefault();
        resetUploadArea();
    };

    // Set Default Resume (AJAX)
    window.setDefaultResume = function(resumeId) {
        if (!resumeId) return;
        
        fetch(`/dashboard/applicant/set-default-resume/${resumeId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload page to update UI
                location.reload();
            } else {
                alert(data.message || 'Failed to set default resume');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while setting default resume');
        });
    };

    // Delete Resume Confirmation
    window.confirmDeleteResume = function(resumeId, resumeName) {
        const modal = document.getElementById('deleteResumeModal');
        const nameSpan = document.getElementById('deleteResumeName');
        const idInput = document.getElementById('deleteResumeId');
        
        if (modal && nameSpan && idInput) {
            nameSpan.textContent = resumeName;
            idInput.value = resumeId;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeDeleteResumeModal = function() {
        const modal = document.getElementById('deleteResumeModal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize upload resume modal file handling
    function initUploadResumeModal() {
        const fileInput = document.getElementById('resume_file');
        const uploadArea = document.getElementById('uploadArea');
        const fileAttached = document.getElementById('fileAttached');
        const uploadPrompt = document.getElementById('uploadPrompt');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        if (!fileInput) return;

        // Click to browse
        if (uploadArea) {
            uploadArea.addEventListener('click', function(e) {
                if (e.target.id !== 'removeFileBtn' && !e.target.closest('#removeFileBtn')) {
                    fileInput.click();
                }
            });
        }

        // File input change handler
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) {
                resetUploadArea();
                return;
            }

            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = formatFileSize(file.size);
            if (uploadArea) uploadArea.classList.add('has-file');
            if (fileAttached) fileAttached.style.display = 'flex';
            if (uploadPrompt) uploadPrompt.style.display = 'none';
        });

        // Drag and drop functionality
        if (uploadArea) {
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.style.borderColor = '#dc3545';
                this.style.backgroundColor = '#fff5f5';
            });

            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.style.borderColor = '#e0e0e0';
                this.style.backgroundColor = '#fafafa';
            });

            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                this.style.borderColor = '#e0e0e0';
                this.style.backgroundColor = '#fafafa';

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                }
            });
        }

        // Close modals on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const uploadModal = document.getElementById('uploadResumeModal');
                const deleteModal = document.getElementById('deleteResumeModal');
                
                if (uploadModal && uploadModal.classList.contains('active')) {
                    window.closeResumeModal();
                }
                if (deleteModal && deleteModal.classList.contains('active')) {
                    window.closeDeleteResumeModal();
                }
            }
        });

        // Close modals on overlay click
        const uploadModal = document.getElementById('uploadResumeModal');
        const deleteModal = document.getElementById('deleteResumeModal');
        
        if (uploadModal) {
            const overlay = uploadModal.querySelector('.modal-overlay');
            if (overlay) {
                overlay.addEventListener('click', window.closeResumeModal);
            }
        }
        
        if (deleteModal) {
            const overlay = deleteModal.querySelector('.modal-overlay');
            if (overlay) {
                overlay.addEventListener('click', window.closeDeleteResumeModal);
            }
        }

        // Bind click on add-resume card
        const addResumeCard = document.querySelector('.add-resume-card');
        if (addResumeCard) {
            addResumeCard.addEventListener('click', function (e) {
                e.preventDefault();
                window.openResumeModal();
            });
        }
    }

    // Init all
    document.addEventListener('DOMContentLoaded', function () {
        initProfilePreview();
        initTabs();
        initResumeModal();
        initSocialLinks();
        initPasswordToggles();
        initPasswordChangeUX();
        initResumeMenuToggle();
        initInputStyling();
        initPrivacyToggle();
        initDeleteAccount();
        initUploadResumeModal();
    });

})();
