/**
 * Toast Notification System
 * Auto-dismisses messages after 5 seconds with smooth fade-out animation
 */

document.addEventListener('DOMContentLoaded', function() {
    const toastContainer = document.getElementById('toastContainer');
    
    if (!toastContainer) return;
    
    const toasts = toastContainer.querySelectorAll('.toast');
    
    toasts.forEach((toast, index) => {
        // Stagger the animation slightly for multiple toasts
        toast.style.animationDelay = `${index * 0.1}s`;
        
        // Auto-dismiss after 5 seconds
        const dismissTimeout = setTimeout(() => {
            dismissToast(toast);
        }, 5000);
        
        // Store timeout ID so we can cancel it if manually closed
        toast.dataset.timeoutId = dismissTimeout;
    });
});

/**
 * Dismiss a toast notification with fade-out animation
 * @param {HTMLElement} toastElement - The toast element to dismiss
 */
function dismissToast(toastElement) {
    // Clear the auto-dismiss timeout if it exists
    if (toastElement.dataset.timeoutId) {
        clearTimeout(parseInt(toastElement.dataset.timeoutId));
    }
    
    // Add fade-out class
    toastElement.classList.add('fade-out');
    
    // Remove from DOM after animation completes
    setTimeout(() => {
        toastElement.remove();
        
        // Remove container if no toasts left
        const container = document.getElementById('toastContainer');
        if (container && container.children.length === 0) {
            container.remove();
        }
    }, 400); // Match the animation duration
}

/**
 * Close toast when close button is clicked
 * @param {HTMLElement} closeButton - The close button element
 */
function closeToast(closeButton) {
    const toast = closeButton.closest('.toast');
    if (toast) {
        dismissToast(toast);
    }
}

/**
 * Programmatically create and show a toast notification
 * Useful for client-side notifications without page reload
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    
    // Create container if it doesn't exist
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Icon based on type
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const iconClass = icons[type] || icons.info;
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${iconClass}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <button class="toast-close" onclick="closeToast(this)" aria-label="Close notification">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-dismiss after 5 seconds
    const dismissTimeout = setTimeout(() => {
        dismissToast(toast);
    }, 5000);
    
    toast.dataset.timeoutId = dismissTimeout;
}

/**
 * Escape HTML to prevent XSS when creating toasts programmatically
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
