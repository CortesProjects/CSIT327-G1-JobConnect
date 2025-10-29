document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#registration-form");

    const fullName = document.querySelector("#id_full_name");
    const username = document.querySelector("#id_username");
    const email = document.querySelector("#id_email");
    const password1 = document.querySelector("#id_password1");
    const password2 = document.querySelector("#id_password2");
    const terms = document.querySelector("#id_terms_and_conditions");
    const submitBtn = document.querySelector(".register-submit");

    const errors = {
        fullName: document.querySelector("#full-name-error"),
        username: document.querySelector("#username-error"),
        email: document.querySelector("#email-error"),
        password1: document.querySelector("#password1-error"),
        password2: document.querySelector("#password2-error"),
        terms: document.querySelector("#terms-error"),
    };

    const accountTypeSelect = document.querySelector("#id_account_type");
    
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

    function validateFullName() {
        const value = fullName.value.trim();
        errors.fullName.textContent = value.length < 2 ? "Full name must be at least 2 characters." : "";
        return !errors.fullName.textContent;
    }

    function validateUsername() {
        const value = username.value.trim();
        if (value.length < 3) {
            errors.username.textContent = "Username must be at least 3 characters.";
            return false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            errors.username.textContent = "Username can only contain letters, numbers, and underscores.";
            return false;
        }
        errors.username.textContent = "";
        return true;
    }

    function validateEmail() {
        const value = email.value.trim();
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        errors.email.textContent = !pattern.test(value) ? "Enter a valid email address." : "";
        return !errors.email.textContent;
    }

    function validatePassword1() {
        const value = password1.value;
        let error = "";

        if (value.length < 8) {
            error = "Password must be at least 8 characters.";
        } else if (!/[A-Z]/.test(value)) {
            error = "Password must include an uppercase letter.";
        } else if (!/[0-9]/.test(value)) {
            error = "Password must include a number.";
        } else if (!/[!@#$%^&*()\-_=+\[\]{}|;:'\",.<>?/`~]/.test(value)) {
            error = "Password must include a special character.";
        }

        errors.password1.textContent = error;
        return !error;
    }

    function validatePassword2() {
        const error = password1.value !== password2.value ? "Passwords do not match." : "";
        errors.password2.textContent = error;
        return !error;
    }

    function validateTerms() {
        errors.terms.textContent = !terms.checked ? "You must accept the terms to continue." : "";
        return terms.checked;
    }

    fullName.addEventListener("input", validateFullName);
    username.addEventListener("input", validateUsername);
    email.addEventListener("input", validateEmail);
    password1.addEventListener("input", () => {
        validatePassword1();
        validatePassword2(); 
    });
    password2.addEventListener("input", validatePassword2);
    terms.addEventListener("change", validateTerms);
    
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

    form.addEventListener("submit", function (e) {
        const valid =
            validateFullName() &&
            validateUsername() &&
            validateEmail() &&
            validatePassword1() &&
            validatePassword2() &&
            validateTerms();

        if (!valid) {
            e.preventDefault();
        }
    });
});
