// Job Applications Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Sort button toggle
    const sortBtn = document.getElementById('sortBtn');
    const sortDropdown = document.getElementById('sortDropdown');
    
    if (sortBtn && sortDropdown) {
        sortBtn.addEventListener('click', function() {
            sortDropdown.classList.toggle('show');
            sortBtn.classList.toggle('active');
        });
    }
    
    // Close sort dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#sortBtn') && !e.target.closest('#sortDropdown')) {
            if (sortDropdown) {
                sortDropdown.classList.remove('show');
            }
            if (sortBtn) {
                sortBtn.classList.remove('active');
            }
        }
    });
    
    // Sort functionality
    const sortOptions = document.querySelectorAll('.sort-option input[type="radio"]');
    sortOptions.forEach(option => {
        option.addEventListener('change', function() {
            const sortValue = this.value;
            console.log('Sorting by:', sortValue);
            
            // Get all application cards
            const columns = document.querySelectorAll('.applications-list');
            columns.forEach(column => {
                const cards = Array.from(column.querySelectorAll('.application-card'));
                
                // Sort based on selected option
                if (sortValue === 'newest') {
                    // Sort newest first (reverse alphabetically by name for demo)
                    cards.sort((a, b) => {
                        const nameA = a.querySelector('.applicant-name').textContent;
                        const nameB = b.querySelector('.applicant-name').textContent;
                        return nameB.localeCompare(nameA);
                    });
                } else if (sortValue === 'oldest') {
                    // Sort oldest first (alphabetically by name for demo)
                    cards.sort((a, b) => {
                        const nameA = a.querySelector('.applicant-name').textContent;
                        const nameB = b.querySelector('.applicant-name').textContent;
                        return nameA.localeCompare(nameB);
                    });
                }
                
                // Reorder cards in the column
                cards.forEach(card => column.appendChild(card));
            });
            
            // Hide dropdown after selection
            if (sortDropdown) {
                sortDropdown.classList.remove('show');
            }
            if (sortBtn) {
                sortBtn.classList.add('active');
            }
        });
    });
    
    // Column menu toggle
    const columnMenuBtns = document.querySelectorAll('.btn-menu');
    columnMenuBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.parentElement.querySelector('.column-menu-dropdown');
            
            // Close other dropdowns
            document.querySelectorAll('.column-menu-dropdown').forEach(menu => {
                if (menu !== dropdown) {
                    menu.classList.remove('show');
                }
            });
            
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });
    });
    
    // Close column menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.column-header')) {
            document.querySelectorAll('.column-menu-dropdown').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
    
    // Column menu item actions
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const text = this.textContent.trim();
            const column = this.closest('.applications-column');
            
            if (text.includes('Edit Column')) {
                // Handle edit column
                const columnTitle = column.querySelector('.column-title');
                const newName = prompt('Enter new column name:', columnTitle.textContent.split('(')[0].trim());
                if (newName) {
                    const count = columnTitle.querySelector('.count').textContent;
                    columnTitle.innerHTML = `${newName} <span class="count">${count}</span>`;
                }
            } else if (text.includes('Delete')) {
                // Handle delete column
                if (confirm('Are you sure you want to delete this column?')) {
                    column.remove();
                }
            }
            
            // Close dropdown
            this.closest('.column-menu-dropdown').classList.remove('show');
        });
    });
    
    // Card menu functionality
    const cardMenuBtns = document.querySelectorAll('.btn-card-menu');
    cardMenuBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            console.log('Card menu clicked');
            // Add dropdown menu if needed
        });
    });
    
    // Application card click
    const applicationCards = document.querySelectorAll('.application-card');
    applicationCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons
            if (e.target.closest('button')) return;
            
            const applicantName = this.querySelector('.applicant-name').textContent;
            console.log('Viewing application for:', applicantName);
            
            // Open application detail page or modal
            window.location.href = `/dashboard/employer/candidate-detail/?name=${encodeURIComponent(applicantName)}`;
        });
    });
    
    // Download CV button
    const downloadBtns = document.querySelectorAll('.btn-download');
    downloadBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const card = this.closest('.application-card');
            const applicantName = card.querySelector('.applicant-name').textContent;
            
            console.log('Downloading CV for:', applicantName);
            // Add your download logic here
            // For demo, you could trigger a download or open a modal
            alert(`Downloading CV for ${applicantName}`);
        });
    });
    
    // Create new column
    const createColumnBtn = document.querySelector('.btn-create-column');
    if (createColumnBtn) {
        createColumnBtn.addEventListener('click', function() {
            const columnName = prompt('Enter new column name:');
            if (columnName) {
                // Create new column
                const newColumn = document.createElement('div');
                newColumn.className = 'applications-column';
                newColumn.innerHTML = `
                    <div class="column-header">
                        <h2 class="column-title">${columnName} <span class="count">(0)</span></h2>
                        <button class="btn-menu">
                            <i class="fas fa-ellipsis-h"></i>
                        </button>
                        <div class="column-menu-dropdown">
                            <button class="menu-item">
                                <i class="fas fa-edit"></i>
                                Edit Column
                            </button>
                            <button class="menu-item delete">
                                <i class="fas fa-trash"></i>
                                Delete
                            </button>
                        </div>
                    </div>
                    <div class="applications-list">
                        <!-- Cards will be added here -->
                    </div>
                `;
                
                // Insert before create column button
                const createColumnContainer = this.closest('.create-column');
                createColumnContainer.parentElement.insertBefore(newColumn, createColumnContainer);
                
                // Re-initialize event listeners for new column
                initializeColumnEvents(newColumn);
            }
        });
    }
    
    // Drag and drop functionality (optional advanced feature)
    // This would allow dragging cards between columns
    initializeDragAndDrop();
});

// Function to initialize events for dynamically created columns
function initializeColumnEvents(column) {
    const menuBtn = column.querySelector('.btn-menu');
    const dropdown = column.querySelector('.column-menu-dropdown');
    
    menuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        
        // Close other dropdowns
        document.querySelectorAll('.column-menu-dropdown').forEach(menu => {
            if (menu !== dropdown) {
                menu.classList.remove('show');
            }
        });
        
        dropdown.classList.toggle('show');
    });
    
    const menuItems = column.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const text = this.textContent.trim();
            
            if (text.includes('Edit Column')) {
                const columnTitle = column.querySelector('.column-title');
                const newName = prompt('Enter new column name:', columnTitle.textContent.split('(')[0].trim());
                if (newName) {
                    const count = columnTitle.querySelector('.count').textContent;
                    columnTitle.innerHTML = `${newName} <span class="count">${count}</span>`;
                }
            } else if (text.includes('Delete')) {
                if (confirm('Are you sure you want to delete this column?')) {
                    column.remove();
                }
            }
            
            dropdown.classList.remove('show');
        });
    });
}

// Drag and drop initialization (basic implementation)
function initializeDragAndDrop() {
    const cards = document.querySelectorAll('.application-card');
    const columns = document.querySelectorAll('.applications-list');
    
    cards.forEach(card => {
        card.draggable = true;
        
        card.addEventListener('dragstart', function(e) {
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });
        
        card.addEventListener('dragend', function() {
            this.classList.remove('dragging');
        });
    });
    
    columns.forEach(column => {
        column.addEventListener('dragover', function(e) {
            e.preventDefault();
            const draggingCard = document.querySelector('.dragging');
            if (draggingCard) {
                this.appendChild(draggingCard);
                
                // Update count
                updateColumnCount(this.closest('.applications-column'));
            }
        });
    });
}

// Update column count
function updateColumnCount(column) {
    const countElement = column.querySelector('.count');
    const cardsCount = column.querySelectorAll('.application-card').length;
    countElement.textContent = `(${cardsCount})`;
}
