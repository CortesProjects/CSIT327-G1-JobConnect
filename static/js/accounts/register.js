/**
 * Registration Form - Dynamic Styling Only
 * All validation is handled by Django backend
 */
document.addEventListener("DOMContentLoaded", function () {
    const accountTypeSelect = document.querySelector("#id_account_type");
    
    // Pre-select account type from URL parameter
    function preSelectAccountType() {
        const urlParams = new URLSearchParams(window.location.search);
        const selectedType = urlParams.get('account_type'); 
        
        if (selectedType && accountTypeSelect) {
            if (selectedType === 'applicant' || selectedType === 'employer') {
                accountTypeSelect.value = selectedType;
            }
        }
    }
    preSelectAccountType();
    
    // Password visibility toggle
    document.querySelectorAll(".password-toggle").forEach(toggle => {
        toggle.addEventListener("click", function () {
            const parentContainer = this.closest('.password-field'); 
            const input = parentContainer.querySelector('input'); 

            if (input && input.type === "password") {
                input.type = "text";
                this.classList.remove("fa-eye");
                this.classList.add("fa-eye-slash");
            } else if (input) {
                input.type = "password";
                this.classList.remove("fa-eye-slash");
                this.classList.add("fa-eye");
            }
        });
    });

    // Clear error styling when user starts typing (visual feedback only)
    document.querySelectorAll('input, select').forEach(field => {
        field.addEventListener('input', function() {
            this.classList.remove('error');
            const errorDiv = this.parentElement.querySelector('.error-text');
            if (errorDiv && (this.value.trim() || this.checked)) {
                errorDiv.style.opacity = '0';
            }
        });

        field.addEventListener('change', function() {
            this.classList.remove('error');
            const errorDiv = this.parentElement.querySelector('.error-text');
            if (errorDiv && (this.value.trim() || this.checked)) {
                errorDiv.style.opacity = '0';
            }
        });
    });
});
