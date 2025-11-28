// Job Applications Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Filter button toggle
    const filterBtn = document.getElementById('filterBtn');
    const filterDropdown = document.getElementById('filterDropdown');
    
    if (filterBtn && filterDropdown) {
        filterBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            filterDropdown.classList.toggle('show');
            filterBtn.classList.toggle('active');
            // Close sort dropdown if open
            if (sortDropdown) {
                sortDropdown.classList.remove('show');
            }
            if (sortBtn) {
                sortBtn.classList.remove('active');
            }
        });
    }

    // Sort button toggle
    const sortBtn = document.getElementById('sortBtn');
    const sortDropdown = document.getElementById('sortDropdown');
    
    if (sortBtn && sortDropdown) {
        sortBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            sortDropdown.classList.toggle('show');
            sortBtn.classList.toggle('active');
            // Close filter dropdown if open
            if (filterDropdown) {
                filterDropdown.classList.remove('show');
            }
            if (filterBtn) {
                filterBtn.classList.remove('active');
            }
        });
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#filterBtn') && !e.target.closest('#filterDropdown')) {
            if (filterDropdown) {
                filterDropdown.classList.remove('show');
            }
            if (filterBtn) {
                filterBtn.classList.remove('active');
            }
        }
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

    // Filter functionality
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const filterCheckboxes = document.querySelectorAll('.filter-option input[type="checkbox"]');

    // Clear all filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            filterCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            // Reset all cards to visible
            document.querySelectorAll('.application-card').forEach(card => {
                card.style.display = '';
            });
            console.log('Filters cleared');
        });
    }

    // Apply filters
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const selectedExperience = [];
            const selectedEducation = [];

            // Gather selected filters
            filterCheckboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    if (checkbox.name === 'experience') {
                        selectedExperience.push(checkbox.value);
                    } else if (checkbox.name === 'education') {
                        selectedEducation.push(checkbox.value);
                    }
                }
            });

            console.log('Applying filters:', { experience: selectedExperience, education: selectedEducation });

            // Filter cards (this is a demo - replace with actual data attributes)
            const cards = document.querySelectorAll('.application-card');
            cards.forEach(card => {
                let showCard = true;

                // If any filters selected, apply them
                if (selectedExperience.length > 0 || selectedEducation.length > 0) {
                    // You would check card's actual data here
                    // For now, this is just demonstration logic
                    showCard = true; // Replace with actual filtering logic
                }

                card.style.display = showCard ? '' : 'none';
            });

            // Close dropdown
            if (filterDropdown) {
                filterDropdown.classList.remove('show');
            }
            if (filterBtn) {
                filterBtn.classList.remove('active');
            }
        });
    }
    
    // Column menu toggle (updated selector)
    const columnMenuBtns = document.querySelectorAll('.btn-column-menu');
    columnMenuBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.nextElementSibling;
            
            // Close other dropdowns
            document.querySelectorAll('.column-menu-dropdown').forEach(menu => {
                if (menu !== dropdown) {
                    menu.classList.remove('show');
                }
            });
            
            if (dropdown && dropdown.classList.contains('column-menu-dropdown')) {
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
            const action = this.getAttribute('data-action');
            const column = this.closest('.applications-column');
            
            if (action === 'edit') {
                // Open modal for editing
                const columnTitle = column.querySelector('.column-title');
                const currentName = columnTitle.textContent;
                
                modalMode = 'edit';
                editingColumn = column;
                modalTitle.textContent = 'Edit Column';
                confirmStageAction.textContent = 'Save Changes';
                stageNameInput.value = currentName;
                // populate hidden stage id input for form submission
                const stageIdInput = document.getElementById('stageIdInput');
                if (stageIdInput) stageIdInput.value = column.getAttribute('data-stage-id') || '';
                stageModal.classList.add('show');
                stageNameInput.focus();
                stageNameInput.select();
            } else if (action === 'delete') {
                // Open delete confirmation modal
                openDeleteModal(column);
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
    
    // Modal functionality
    const stageModal = document.getElementById('stageModal');
    const modalTitle = document.getElementById('modalTitle');
    const stageNameInput = document.getElementById('stageName');
    const createColumnBtn = document.querySelector('.btn-create-column');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const confirmStageAction = document.getElementById('confirmStageAction');
    
    // Delete modal
    const deleteModal = document.getElementById('deleteModal');
    const deleteColumnName = document.getElementById('deleteColumnName');
    const closeDeleteModalBtn = document.getElementById('closeDeleteModalBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    let modalMode = 'add'; // 'add' or 'edit'
    let editingColumn = null;
    let deletingColumn = null;

    // Open modal for adding new column
    if (createColumnBtn) {
        createColumnBtn.addEventListener('click', function() {
            modalMode = 'add';
            modalTitle.textContent = 'Add New Column';
            confirmStageAction.textContent = 'Add Column';
            stageNameInput.value = '';
            const stageIdInput = document.getElementById('stageIdInput');
            const formTypeInput = document.getElementById('formTypeInput');
            if (stageIdInput) stageIdInput.value = '';
            if (formTypeInput) formTypeInput.value = 'add_stage';
            stageModal.classList.add('show');
            stageNameInput.focus();
        });
    }

    // Close modal
    function closeModal() {
        stageModal.classList.remove('show');
        stageNameInput.value = '';
        editingColumn = null;
        modalMode = 'add';
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', closeModal);
    }

    // Close modal when clicking overlay
    if (stageModal) {
        stageModal.addEventListener('click', function(e) {
            if (e.target === stageModal) {
                closeModal();
            }
        });
    }

    // Delete modal functions
    function openDeleteModal(column) {
        const columnTitle = column.querySelector('.column-title');
        deletingColumn = column;
        deleteColumnName.textContent = columnTitle.textContent;
        deleteModal.classList.add('show');
    }

    function closeDeleteModal() {
        deleteModal.classList.remove('show');
        deletingColumn = null;
    }

    if (closeDeleteModalBtn) {
        closeDeleteModalBtn.addEventListener('click', closeDeleteModal);
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    }

    // Close delete modal when clicking overlay
    if (deleteModal) {
        deleteModal.addEventListener('click', function(e) {
            if (e.target === deleteModal) {
                closeDeleteModal();
            }
        });
    }

    // Confirm delete action
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (deletingColumn) {
                // Submit the stageForm to delete the column on the server (no AJAX)
                const stageForm = document.getElementById('stageForm');
                const formTypeInput = document.getElementById('formTypeInput');
                const stageIdInput = document.getElementById('stageIdInput');

                formTypeInput.value = 'delete_stage';
                // stage id stored in data-stage-id attribute on the column
                const sid = deletingColumn.getAttribute('data-stage-id') || deletingColumn.dataset.columnId || '';
                stageIdInput.value = sid;
                stageForm.submit();
            }
        });
    }

    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (stageModal.classList.contains('show')) {
                closeModal();
            }
            if (deleteModal.classList.contains('show')) {
                closeDeleteModal();
            }
        }
    });

    // Submit with Enter key
    if (stageNameInput) {
        stageNameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                confirmStageAction.click();
            }
        });
    }

    // Handle modal action (add or edit)
    if (confirmStageAction) {
        confirmStageAction.addEventListener('click', function() {
            const columnName = stageNameInput.value.trim();
            if (!columnName) return;

            const stageForm = document.getElementById('stageForm');
            const formTypeInput = document.getElementById('formTypeInput');
            const stageIdInput = document.getElementById('stageIdInput');

            if (modalMode === 'edit' && editingColumn) {
                // Prepare form for edit
                formTypeInput.value = 'edit_stage';
                // editingColumn should have a data-stage-id attribute when rendered from server
                const existingId = editingColumn.getAttribute('data-stage-id') || stageIdInput.value;
                stageIdInput.value = existingId || '';
                stageForm.submit();
            } else {
                // Prepare form for add
                formTypeInput.value = 'add_stage';
                stageIdInput.value = '';
                stageForm.submit();
            }
        });
    }
    
    // Drag and drop functionality (optional advanced feature)
    // This would allow dragging cards between columns
    initializeDragAndDrop();
});

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
                const sourceColumn = draggingCard.closest('.applications-list');

                // Append to target column
                this.appendChild(draggingCard);

                // Remove empty-state in target if present
                removeEmptyState(this);

                // Update counts for target and source
                updateColumnCount(this.closest('.applications-column'));
                if (sourceColumn && sourceColumn !== this) {
                    // If source column is now empty, add empty-state
                    ensureEmptyState(sourceColumn);
                    updateColumnCount(sourceColumn.closest('.applications-column'));
                }
            }
        });
        
        // On drop, persist the move to server
        column.addEventListener('drop', function(e) {
            e.preventDefault();
            const draggingCard = document.querySelector('.dragging');
            if (draggingCard) {
                persistApplicationMove(draggingCard, this);
            }
        });
    });

    // Ensure empty-state elements exist or are removed appropriately on initial load
    document.querySelectorAll('.applications-list').forEach(list => ensureEmptyState(list));
}

// Persist application move to server (non-AJAX POST via hidden form)
function persistApplicationMove(card, targetColumn) {
    const applicationId = card.dataset.applicationId || card.getAttribute('data-application-id');
    const stageId = targetColumn.dataset.stageId || targetColumn.getAttribute('data-stage-id');
    
    if (!applicationId) {
        console.warn('No application ID found on card');
        return;
    }
    
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    // Create and submit a hidden form (non-AJAX, Django POST)
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/dashboard/employer/move-application/${applicationId}/`;
    form.style.display = 'none';
    
    // CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrftoken;
    form.appendChild(csrfInput);
    
    // Stage ID (use "all" or empty for All Applications column)
    const stageInput = document.createElement('input');
    stageInput.type = 'hidden';
    stageInput.name = 'stage_id';
    stageInput.value = (stageId === 'all' || !stageId) ? '' : stageId;
    form.appendChild(stageInput);
    
    document.body.appendChild(form);
    form.submit();
}

// Update column count
function updateColumnCount(column) {
    if (!column) return;
    // The template uses `.count-badge` for column counts.
    const countElement = column.querySelector('.count-badge');
    const cardsCount = column.querySelectorAll('.application-card').length;
    if (countElement) {
        try {
            // Update to show the numeric count (matching template style)
            countElement.textContent = cardsCount;
        } catch (err) {
            console.warn('Failed to update column count element', err);
        }
    }
}

// Remove an empty-state element from a column list if present
function removeEmptyState(listEl) {
    if (!listEl) return;
    const empty = listEl.querySelector('.empty-state');
    if (empty) empty.remove();
}

// Ensure empty-state exists when a column list has no cards
function ensureEmptyState(listEl) {
    if (!listEl) return;
    const hasCards = listEl.querySelector('.application-card');
    const existingEmpty = listEl.querySelector('.empty-state');
    if (!hasCards && !existingEmpty) {
        const empty = document.createElement('div');
        empty.className = 'empty-state';
        empty.innerHTML = `<i class="fas fa-inbox"></i><p>No applications in this stage</p>`;
        listEl.appendChild(empty);
    }
    if (hasCards && existingEmpty) {
        existingEmpty.remove();
    }
}
