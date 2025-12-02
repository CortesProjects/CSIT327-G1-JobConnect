document.addEventListener('DOMContentLoaded', function() {
    const termsModal = document.getElementById('termsModal');
    const termsLinks = document.querySelectorAll('.terms-link, a[href*="terms"]');
    const closeTermsBtn = document.getElementById('closeTermsModal');
    const acceptTermsBtn = document.getElementById('acceptTermsBtn');
    const declineTermsBtn = document.getElementById('declineTermsBtn');

    termsLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            openTermsModal();
        });
    });

    if (closeTermsBtn) {
        closeTermsBtn.addEventListener('click', closeTermsModal);
    }

    if (acceptTermsBtn) {
        acceptTermsBtn.addEventListener('click', function() {
            const termsCheckbox = document.getElementById('id_terms_and_conditions');
            if (termsCheckbox) {
                termsCheckbox.checked = true;
            }
            closeTermsModal();
        });
    }

    if (declineTermsBtn) {
        declineTermsBtn.addEventListener('click', function() {
            const termsCheckbox = document.getElementById('id_terms_and_conditions');
            if (termsCheckbox) {
                termsCheckbox.checked = false;
            }
            closeTermsModal();
        });
    }

    if (termsModal) {
        termsModal.addEventListener('click', function(e) {
            if (e.target === termsModal) {
                closeTermsModal();
            }
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && termsModal && termsModal.classList.contains('show')) {
            closeTermsModal();
        }
    });

    function openTermsModal() {
        if (termsModal) {
            termsModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeTermsModal() {
        if (termsModal) {
            termsModal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }
});
