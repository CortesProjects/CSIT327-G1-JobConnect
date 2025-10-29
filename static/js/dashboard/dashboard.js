// This file can be used for any dashboard-specific JavaScript functions.
// For example, handling interactions for job alerts, settings, etc.

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JavaScript loaded.');

    // Settings Tab Switching
    const tabLinks = document.querySelectorAll('.settings-nav a[data-tab]');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabLinks.forEach(tab => tab.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab contents
            document.querySelectorAll('.settings-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show selected tab content
            const tabName = this.getAttribute('data-tab');
            const tabContent = document.getElementById(tabName + '-tab');
            if (tabContent) {
                tabContent.style.display = 'flex';
            }
        });
    });

    // Modal handling for "Add CV/Resume"
    const addCvModal = document.getElementById('addCvModal');
    const addCvBtn = document.getElementById('addCvBtn');
    const closeButton = document.querySelector('.modal .close-button');
    const cancelBtn = document.querySelector('.modal .btn-cancel');

    if (addCvBtn) {
        addCvBtn.onclick = function() {
            if (addCvModal) {
                addCvModal.style.display = 'block';
            }
        }
    }

    if (closeButton) {
        closeButton.onclick = function() {
            if (addCvModal) {
                addCvModal.style.display = 'none';
            }
        }
    }

    if (cancelBtn) {
        cancelBtn.onclick = function() {
            if (addCvModal) {
                addCvModal.style.display = 'none';
            }
        }
    }

    window.onclick = function(event) {
        if (event.target == addCvModal) {
            addCvModal.style.display = 'none';
        }
    }

    // Logic for resume item menu
    const resumeItems = document.querySelectorAll('.resume-item');
    resumeItems.forEach(item => {
        const menuIcon = item.querySelector('.menu-icon');
        const actionsMenu = item.querySelector('.resume-actions');

        if (menuIcon && actionsMenu) {
            menuIcon.addEventListener('click', (event) => {
                event.stopPropagation();
                // Hide all other action menus
                document.querySelectorAll('.resume-actions').forEach(menu => {
                    if (menu !== actionsMenu) {
                        menu.style.display = 'none';
                    }
                });
                // Toggle current menu
                actionsMenu.style.display = actionsMenu.style.display === 'block' ? 'none' : 'block';
            });
        }
    });

    // Close menus when clicking outside
    window.addEventListener('click', () => {
        document.querySelectorAll('.resume-actions').forEach(menu => {
            menu.style.display = 'none';
        });
    });

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
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

    // Privacy toggle status update
    const privacyToggles = document.querySelectorAll('.privacy-toggle');
    privacyToggles.forEach(toggle => {
        const statusSpan = toggle.closest('.privacy-info').querySelector('.privacy-status');
        const descriptionSpan = toggle.closest('.privacy-toggle-row').querySelector('.privacy-description');
        
        toggle.addEventListener('change', function() {
            if (this.checked) {
                statusSpan.textContent = 'Yes';
                if (descriptionSpan.textContent.includes('resume')) {
                    descriptionSpan.textContent = 'Your resume is public now';
                } else {
                    descriptionSpan.textContent = 'Your profile is public now';
                }
            } else {
                statusSpan.textContent = 'No';
                if (descriptionSpan.textContent.includes('resume')) {
                    descriptionSpan.textContent = 'Your resume is private now';
                } else {
                    descriptionSpan.textContent = 'Your profile is private now';
                }
            }
        });
    });
});
