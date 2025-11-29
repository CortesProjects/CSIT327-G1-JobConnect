// Terms and Conditions Modal Functionality

document.addEventListener('DOMContentLoaded', function() {
    const termsModal = document.getElementById('termsModal');
    const termsLinks = document.querySelectorAll('.terms-link, a[href*="terms"]');
    const closeTermsBtn = document.getElementById('closeTermsModal');
    const acceptTermsBtn = document.getElementById('acceptTermsBtn');
    const declineTermsBtn = document.getElementById('declineTermsBtn');

    // Open modal when clicking any terms link
    termsLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            openTermsModal();
        });
    });

    // Close modal
    if (closeTermsBtn) {
        closeTermsBtn.addEventListener('click', closeTermsModal);
    }

    // Accept terms
    if (acceptTermsBtn) {
        acceptTermsBtn.addEventListener('click', function() {
            // Check the terms checkbox if it exists
            const termsCheckbox = document.getElementById('id_terms_and_conditions');
            if (termsCheckbox) {
                termsCheckbox.checked = true;
            }
            closeTermsModal();
        });
    }

    // Decline terms
    if (declineTermsBtn) {
        declineTermsBtn.addEventListener('click', function() {
            // Uncheck the terms checkbox if it exists
            const termsCheckbox = document.getElementById('id_terms_and_conditions');
            if (termsCheckbox) {
                termsCheckbox.checked = false;
            }
            closeTermsModal();
        });
    }

    // Close modal when clicking outside
    if (termsModal) {
        termsModal.addEventListener('click', function(e) {
            if (e.target === termsModal) {
                closeTermsModal();
            }
        });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && termsModal && termsModal.classList.contains('show')) {
            closeTermsModal();
        }
    });

    function openTermsModal() {
        if (termsModal) {
            termsModal.classList.add('show');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    }

    function closeTermsModal() {
        if (termsModal) {
            termsModal.classList.remove('show');
            document.body.style.overflow = ''; // Restore scrolling
        }
    }
});
