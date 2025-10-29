document.addEventListener("DOMContentLoaded", () => {
  // --- PASSWORD ELEMENTS (only exist on register page) ---
  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm_password');
  const passwordError = document.getElementById('password-error');
  const confirmError = document.getElementById('confirm-password-error');

  // --- PASSWORD VALIDATION (only runs if confirm field exists) ---
    if (passwordInput && confirmInput) {
    function validatePassword() {
      const password = passwordInput.value;
      if (password.length < 8) {
        passwordError.textContent = "Password must be at least 8 characters.";
        passwordInput.classList.add("invalid");
        passwordInput.classList.remove("valid");
      } else {
        passwordError.textContent = "";
        passwordInput.classList.add("valid");
        passwordInput.classList.remove("invalid");
      }
      validateConfirmPassword();
    }

    function validateConfirmPassword() {
      const password = passwordInput.value;
      const confirmPassword = confirmInput.value;
      if (confirmPassword && password !== confirmPassword) {
        confirmError.textContent = "Passwords do not match.";
        confirmInput.classList.add("invalid");
        confirmInput.classList.remove("valid");
      } else if (confirmPassword) {
        confirmError.textContent = "";
        confirmInput.classList.add("valid");
        confirmInput.classList.remove("invalid");
      } else {
        confirmError.textContent = "";
        confirmInput.classList.remove("valid", "invalid");
      }
    }

    passwordInput.addEventListener('input', validatePassword);
    confirmInput.addEventListener('input', validateConfirmPassword);
  }

  // --- EYE ICON PASSWORD TOGGLE FUNCTIONALITY (works on all pages) ---
  const toggleButtons = document.querySelectorAll('.toggle-password');

  toggleButtons.forEach(button => {
    const icon = button.querySelector('i');
    const targetId = button.getAttribute('data-target');
    const passwordInput = document.getElementById(targetId);

    if (!passwordInput || !icon) return;

    button.addEventListener('click', () => {
      const isHidden = passwordInput.type === 'password';
      passwordInput.type = isHidden ? 'text' : 'password';
      
      // Toggle icon
      icon.classList.toggle('fa-eye', !isHidden);
      icon.classList.toggle('fa-eye-slash', isHidden);
      
      passwordInput.focus();
    });
  });
});
