// Employer Profile Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Change Banner functionality
    const changeBannerBtn = document.querySelector('.btn-change-banner');
    const bannerImg = document.getElementById('banner-img');
    
    if (changeBannerBtn) {
        changeBannerBtn.addEventListener('click', function() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        bannerImg.src = event.target.result;
                        
                        // Here you would typically upload to server
                        console.log('Banner image selected:', file.name);
                        showNotification('Banner image updated successfully!', 'success');
                    };
                    reader.readAsDataURL(file);
                }
            };
            
            input.click();
        });
    }
    
    // Change Logo functionality
    const changeLogoBtn = document.querySelector('.btn-change-logo');
    const logoImg = document.getElementById('logo-img');
    
    if (changeLogoBtn) {
        changeLogoBtn.addEventListener('click', function() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        logoImg.src = event.target.result;
                        
                        // Here you would typically upload to server
                        console.log('Logo image selected:', file.name);
                        showNotification('Company logo updated successfully!', 'success');
                    };
                    reader.readAsDataURL(file);
                }
            };
            
            input.click();
        });
    }
    
    // Social links - prevent default for demo
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') {
                e.preventDefault();
                const platform = this.querySelector('span').textContent;
                showNotification(`Opening ${platform}...`, 'info');
            }
        });
    });
    
    // Job items hover effect enhancement
    const jobItems = document.querySelectorAll('.job-item-small');
    jobItems.forEach(item => {
        item.addEventListener('click', function() {
            const jobTitle = this.querySelector('.job-title-small').textContent;
            console.log('Viewing job:', jobTitle);
            // Navigate to job detail or open modal
            // window.location.href = `/dashboard/employer/job-detail/?title=${encodeURIComponent(jobTitle)}`;
        });
    });
    
    // Animate stats on scroll
    const statNumbers = document.querySelectorAll('.stat-number');
    
    function animateStats() {
        statNumbers.forEach(stat => {
            const target = parseInt(stat.textContent.replace(/,/g, ''));
            const duration = 1500;
            const increment = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                stat.textContent = Math.floor(current).toLocaleString();
            }, 16);
        });
    }
    
    // Use Intersection Observer to trigger animation when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    const statsContainer = document.querySelector('.company-stats');
    if (statsContainer) {
        observer.observe(statsContainer);
    }
    
    // Copy contact information
    const infoValues = document.querySelectorAll('.info-value');
    infoValues.forEach(value => {
        // Add click to copy for phone and email
        const text = value.textContent.trim();
        
        if (text.includes('@') || text.includes('+')) {
            value.style.cursor = 'pointer';
            value.title = 'Click to copy';
            
            value.addEventListener('click', function() {
                navigator.clipboard.writeText(text).then(() => {
                    showNotification('Copied to clipboard!', 'success');
                }).catch(err => {
                    console.error('Failed to copy:', err);
                });
            });
        }
    });
    
    // Quick actions button tracking
    const actionBtns = document.querySelectorAll('.action-btn');
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const actionText = this.textContent.trim();
            console.log('Quick action clicked:', actionText);
            // Track analytics or perform additional actions
        });
    });
    
    // Load company data from API (placeholder)
    function loadCompanyProfile() {
        // This would typically fetch from your Django backend
        console.log('Loading company profile data...');
        
        // Example:
        // fetch('/api/employer/profile/')
        //     .then(response => response.json())
        //     .then(data => {
        //         updateProfileUI(data);
        //     });
    }
    
    // Update profile UI with data
    function updateProfileUI(data) {
        // Update company name, stats, info, etc.
        console.log('Updating profile UI with data:', data);
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Print functionality
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            window.print();
        }
    });
    
    // Initialize on load
    loadCompanyProfile();
});

// Notification helper function
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        backgroundColor: type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3',
        color: 'white',
        borderRadius: '6px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        zIndex: '9999',
        animation: 'slideInRight 0.3s ease',
        fontSize: '14px',
        fontWeight: '500'
    });
    
    // Add to body
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add notification animations to head
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
