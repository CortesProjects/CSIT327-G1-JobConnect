// Candidate Detail Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Bookmark button toggle
    const bookmarkBtn = document.querySelector('.btn-bookmark');
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.style.backgroundColor = '#fff3cd';
                this.style.borderColor = '#ffc107';
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.style.backgroundColor = 'white';
                this.style.borderColor = '#e0e0e0';
            }
        });
    }

    // Send Mail button
    const sendMailBtn = document.querySelector('.btn-send-mail');
    if (sendMailBtn) {
        sendMailBtn.addEventListener('click', function() {
            const candidateName = document.querySelector('.candidate-name').textContent;
            const candidateEmail = document.querySelector('.info-value a[href^="mailto:"]');
            
            if (candidateEmail) {
                window.location.href = candidateEmail.getAttribute('href');
            } else {
                console.log('Opening mail composer for:', candidateName);
                // You can implement a modal for composing email here
            }
        });
    }

    // Hire button
    const hireBtn = document.querySelector('.btn-hire');
    if (hireBtn) {
        hireBtn.addEventListener('click', function() {
            const candidateName = document.querySelector('.candidate-name').textContent;
            
            if (confirm(`Are you sure you want to hire ${candidateName}?`)) {
                console.log('Hiring candidate:', candidateName);
                // Implement your hire logic here
                // You might want to redirect to a contract page or show a success modal
                alert(`Hiring process initiated for ${candidateName}`);
            }
        });
    }

    // Filter and Sort buttons
    const filterBtn = document.querySelector('.btn-filter');
    const sortBtn = document.querySelector('.btn-sort');

    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            console.log('Filter toggled');
            // Implement filter logic here
        });
    }

    if (sortBtn) {
        sortBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            console.log('Sort toggled');
            // Implement sort logic here
        });
    }

    // Download Resume button
    const downloadBtn = document.querySelector('.btn-download-resume');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const candidateName = document.querySelector('.candidate-name').textContent;
            console.log('Downloading resume for:', candidateName);
            
            // Implement actual download logic
            // For demo purposes, show an alert
            alert(`Downloading resume for ${candidateName}`);
            
            // In a real application, you would do something like:
            // window.location.href = '/download-resume/candidate-id/';
        });
    }

    // Social media links
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const platform = this.className.split(' ')[1];
            console.log(`Opening ${platform} profile`);
            
            // In a real application, these would be actual URLs
            // For now, just show which platform was clicked
            alert(`Opening ${platform} profile`);
        });
    });

    // Phone number click to call
    const phoneNumbers = document.querySelectorAll('.info-value');
    phoneNumbers.forEach(element => {
        const text = element.textContent.trim();
        if (text.match(/^\+\d/)) {
            element.style.cursor = 'pointer';
            element.style.color = '#0066ff';
            
            element.addEventListener('click', function() {
                window.location.href = `tel:${text}`;
            });
        }
    });

    // Website link
    const websiteLink = document.querySelector('.info-value a[href^="http"]');
    if (websiteLink) {
        websiteLink.addEventListener('click', function(e) {
            // Allow default behavior, just log it
            console.log('Opening website:', this.href);
        });
    }

    // Email link
    const emailLink = document.querySelector('.info-value a[href^="mailto:"]');
    if (emailLink) {
        emailLink.addEventListener('click', function(e) {
            // Allow default behavior, just log it
            console.log('Opening email client:', this.href);
        });
    }

    // Close button
    const closeBtn = document.querySelector('.btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            // Go back in history or redirect to applications page
            if (document.referrer) {
                window.history.back();
            } else {
                window.location.href = '/dashboard/employer/my-jobs/';
            }
        });
    }

    // Smooth scroll for any anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Print functionality (optional)
    // You can add a print button if needed
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            window.print();
        }
    });
});
