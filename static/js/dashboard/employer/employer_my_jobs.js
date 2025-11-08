// My Jobs Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Dropdown menu functionality
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const button = dropdown.querySelector('.btn-more');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Close other dropdowns
            dropdowns.forEach(otherDropdown => {
                if (otherDropdown !== dropdown) {
                    otherDropdown.classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            dropdown.classList.toggle('active');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
    
    // Job status filter
    const statusFilter = document.getElementById('job-status');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const selectedStatus = this.value;
            const jobItems = document.querySelectorAll('.job-item');
            
            jobItems.forEach(item => {
                const statusBadge = item.querySelector('.status-badge');
                
                if (selectedStatus === 'all') {
                    item.style.display = 'grid';
                } else if (selectedStatus === 'active' && statusBadge.classList.contains('active')) {
                    item.style.display = 'grid';
                } else if (selectedStatus === 'expire' && statusBadge.classList.contains('expire')) {
                    item.style.display = 'grid';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Pagination functionality
    const paginationNumbers = document.querySelectorAll('.pagination-number');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    
    paginationNumbers.forEach(button => {
        button.addEventListener('click', function() {
            paginationNumbers.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Scroll to top of table
            document.querySelector('.jobs-table').scrollIntoView({ behavior: 'smooth' });
        });
    });
    
    if (prevButton) {
        prevButton.addEventListener('click', function() {
            const activeButton = document.querySelector('.pagination-number.active');
            const prevSibling = activeButton.previousElementSibling;
            
            if (prevSibling && prevSibling.classList.contains('pagination-number')) {
                paginationNumbers.forEach(btn => btn.classList.remove('active'));
                prevSibling.classList.add('active');
                document.querySelector('.jobs-table').scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    if (nextButton) {
        nextButton.addEventListener('click', function() {
            const activeButton = document.querySelector('.pagination-number.active');
            const nextSibling = activeButton.nextElementSibling;
            
            if (nextSibling && nextSibling.classList.contains('pagination-number')) {
                paginationNumbers.forEach(btn => btn.classList.remove('active'));
                nextSibling.classList.add('active');
                document.querySelector('.jobs-table').scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // View Applications button
    const viewApplicationBtns = document.querySelectorAll('.btn-view-applications');
    viewApplicationBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Get job title from parent job item
            const jobItem = this.closest('.job-item');
            const jobTitle = jobItem.querySelector('.job-title').textContent;
            
            // Redirect to applications page (adjust URL as needed)
            window.location.href = `/dashboard/employer/job-applications/?job=${encodeURIComponent(jobTitle)}`;
        });
    });
    
    // Dropdown item actions
    const viewDetailLinks = document.querySelectorAll('.dropdown-item');
    viewDetailLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const text = this.textContent.trim();
            
            if (text.includes('View Detail')) {
                // Handle view detail
                console.log('View detail clicked');
                // Add your view detail logic here
            } else if (text.includes('Make it Expire')) {
                // Handle expire action
                const jobItem = this.closest('.job-item');
                const statusBadge = jobItem.querySelector('.status-badge');
                
                if (confirm('Are you sure you want to expire this job?')) {
                    statusBadge.classList.remove('active');
                    statusBadge.classList.add('expire');
                    statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Expire';
                }
            }
        });
    });
});
