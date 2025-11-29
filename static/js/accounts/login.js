/**
 * Login Form - Dynamic Styling Only
 * All validation is handled by Django backend
 */
document.addEventListener("DOMContentLoaded", function () {
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
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('error');
            const errorDiv = this.parentElement.querySelector('.error-text');
            if (errorDiv && this.value.trim()) {
                errorDiv.style.opacity = '0';
            }
        });
    });
});