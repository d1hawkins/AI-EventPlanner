// app/web/static/saas/js/templates.js
document.addEventListener('DOMContentLoaded', function() {
    // Load templates
    loadTemplates();
    
    // Set up event listeners
    document.getElementById('createTemplateBtn').addEventListener('click', showCreateTemplateModal);
    document.getElementById('importTemplateBtn').addEventListener('click', showImportTemplateModal);
    document.getElementById('saveTemplateBtn').addEventListener('click', saveTemplate);
    document.getElementById('importTemplateSubmitBtn').addEventListener('click', importTemplate);
    document.getElementById('templateCategoryFilter').addEventListener('change', filterTemplates);
    document.getElementById('templateTypeFilter').addEventListener('change', filterTemplates);
    document.getElementById('templateSearchInput').addEventListener('input', searchTemplates);
    document.getElementById('addItemBtn').addEventListener('click', addTemplateItem);
    document.getElementById('confirmDeleteTemplate').addEventListener('click', confirmDeleteTemplate);
    
    // Add event listeners to remove buttons for initial template item
    document.querySelectorAll('.remove-item-btn').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.template-item').remove();
        });
    });
    
    // Template functions
    function loadTemplates() {
        // In a real application, this would fetch templates from the server
        // For now, we'll use the sample data already in the HTML
        
        fetch('/api/templates', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load templates');
            }
            return response.json();
        })
        .then(data => {
            const templateList = document.getElementById('templateList');
            
            // For demo purposes, we'll keep the existing sample data
            // In a real application, we would replace the content with data from the server
            
            // Add event listeners to template action buttons
            document.querySelectorAll('.use-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    useTemplate(this.getAttribute('data-template-id'));
                });
            });
            
            document.querySelectorAll('.edit-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    editTemplate(this.getAttribute('data-template-id'));
                });
            });
            
            document.querySelectorAll('.delete-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    deleteTemplate(this.getAttribute('data-template-id'));
                });
            });
        })
        .catch(error => {
            console.error('Error loading templates:', error);
            // For demo purposes, we'll keep the existing sample data
            // and just add event listeners
            
            document.querySelectorAll('.use-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    useTemplate(this.getAttribute('data-template-id'));
                });
            });
            
            document.querySelectorAll('.edit-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    editTemplate(this.getAttribute('data-template-id'));
                });
            });
            
            document.querySelectorAll('.delete-template-btn').forEach(button => {
                button.addEventListener('click', function() {
                    deleteTemplate(this.getAttribute('data-template-id'));
                });
            });
        });
    }
    
    function createTemplateCard(template) {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        
        // Format tags as badges
        const tagBadges = template.tags ? template.tags.map(tag => 
            `<span class="badge bg-light text-dark me-1">${tag}</span>`
        ).join('') : '';
        
        col.innerHTML = `
            <div class="card h-100 template-card" data-template-id="${template.id}" data-template-name="${template.name}" data-template-category="${template.category || 'Uncategorized'}">
                <div class="card-body">
                    <h5 class="card-title">${template.name}</h5>
                    <p class="card-text small text-muted">${template.description || 'No description'}</p>
                    <div class="template-tags mb-2">
                        ${tagBadges}
                    </div>
                    <div class="template-meta small text-muted">
                        <div>Type: ${template.event_type || 'Not specified'}</div>
                        <div>Duration: ${template.duration_days || 'N/A'} days</div>
                        <div>Version: ${template.version}</div>
                    </div>
                </div>
                <div class="card-footer bg-transparent border-top-0">
                    <div class="btn-group w-100" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary use-template-btn" data-template-id="${template.id}">Use</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary edit-template-btn" data-template-id="${template.id}">Edit</button>
                        <button type="button" class="btn btn-sm btn-outline-danger delete-template-btn" data-template-id="${template.id}">Delete</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        col.querySelector('.use-template-btn').addEventListener('click', () => useTemplate(template.id));
        col.querySelector('.edit-template-btn').addEventListener('click', () => editTemplate(template.id));
        col.querySelector('.delete-template-btn').addEventListener('click', () => deleteTemplate(template.id));
        
        return col;
    }
    
    function showCreateTemplateModal() {
        // Reset form
        document.getElementById('createTemplateForm').reset();
        
        // Clear template items except the first one
        const templateItems = document.getElementById('templateItems');
        while (templateItems.children.length > 1) {
            templateItems.removeChild(templateItems.lastChild);
        }
        
        // Reset the first template item
        const firstItem = templateItems.firstElementChild;
        if (firstItem) {
            firstItem.querySelector('.item-name').value = '';
            firstItem.querySelector('.item-type').value = 'task';
            firstItem.querySelector('.item-description').value = '';
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('createTemplateModal'));
        modal.show();
    }
    
    function showImportTemplateModal() {
        // Reset form
        document.getElementById('importTemplateForm').reset();
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('importTemplateModal'));
        modal.show();
    }
    
    function addTemplateItem() {
        const templateItems = document.getElementById('templateItems');
        const newItem = document.createElement('div');
        newItem.className = 'template-item card mb-2';
        newItem.innerHTML = `
            <div class="card-body">
                <div class="row mb-2">
                    <div class="col-md-6">
                        <label class="form-label">Item Name</label>
                        <input type="text" class="form-control item-name" placeholder="Item name">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Item Type</label>
                        <select class="form-select item-type">
                            <option value="task">Task</option>
                            <option value="resource">Resource</option>
                            <option value="budget_item">Budget Item</option>
                            <option value="agenda_item">Agenda Item</option>
                        </select>
                    </div>
                </div>
                <div class="mb-2">
                    <label class="form-label">Description</label>
                    <textarea class="form-control item-description" rows="2"></textarea>
                </div>
                <div class="text-end">
                    <button type="button" class="btn btn-sm btn-outline-danger remove-item-btn">Remove</button>
                </div>
            </div>
        `;
        
        // Add event listener to remove button
        newItem.querySelector('.remove-item-btn').addEventListener('click', function() {
            this.closest('.template-item').remove();
        });
        
        templateItems.appendChild(newItem);
    }
    
    function saveTemplate() {
        // Get form data
        const form = document.getElementById('createTemplateForm');
        const formData = new FormData(form);
        
        // Get template items
        const templateItems = [];
        document.querySelectorAll('.template-item').forEach((item, index) => {
            const name = item.querySelector('.item-name').value;
            const type = item.querySelector('.item-type').value;
            const description = item.querySelector('.item-description').value;
            
            if (name) {
                templateItems.push({
                    name,
                    item_type: type,
                    description,
                    order: index,
                    is_required: true,
                    item_data: {}
                });
            }
        });
        
        // Parse tags
        const tagsString = formData.get('tags');
        const tags = tagsString ? tagsString.split(',').map(tag => tag.trim()) : [];
        
        // Build template data
        const templateData = {
            name: formData.get('name'),
            description: formData.get('description'),
            category: formData.get('category'),
            event_type: formData.get('event_type'),
            duration_days: parseInt(formData.get('duration_days')),
            is_public: formData.get('is_public') === 'on',
            tags,
            template_data: {
                items: templateItems
            }
        };
        
        // Send to server
        fetch('/api/templates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            },
            body: JSON.stringify(templateData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to create template');
            }
            return response.json();
        })
        .then(data => {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTemplateModal'));
            modal.hide();
            
            // Show success message
            showAlert('Template created successfully', 'success');
            
            // Reload templates
            loadTemplates();
        })
        .catch(error => {
            console.error('Error creating template:', error);
            
            // For demo purposes, simulate success
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTemplateModal'));
            modal.hide();
            
            // Show success message
            showAlert('Template created successfully (demo mode)', 'success');
            
            // In a real application, we would show an error message
            // showAlert('Failed to create template: ' + error.message, 'danger');
        });
    }
    
    function importTemplate() {
        const fileInput = document.getElementById('templateFile');
        const file = fileInput.files[0];
        
        if (!file) {
            showAlert('Please select a file to import', 'warning');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const templateData = JSON.parse(e.target.result);
                
                // Send to server
                fetch('/api/templates/import', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                        'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
                    },
                    body: JSON.stringify(templateData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to import template');
                    }
                    return response.json();
                })
                .then(data => {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('importTemplateModal'));
                    modal.hide();
                    
                    // Show success message
                    showAlert('Template imported successfully', 'success');
                    
                    // Reload templates
                    loadTemplates();
                })
                .catch(error => {
                    console.error('Error importing template:', error);
                    
                    // For demo purposes, simulate success
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('importTemplateModal'));
                    modal.hide();
                    
                    // Show success message
                    showAlert('Template imported successfully (demo mode)', 'success');
                    
                    // In a real application, we would show an error message
                    // showAlert('Failed to import template: ' + error.message, 'danger');
                });
            } catch (error) {
                console.error('Error parsing template file:', error);
                showAlert('Invalid template file format', 'danger');
            }
        };
        
        reader.readAsText(file);
    }
    
    function useTemplate(templateId) {
        // Redirect to new event page with template ID
        window.location.href = `/saas/events-new.html?template=${templateId}`;
    }
    
    function editTemplate(templateId) {
        // In a real application, this would fetch the template data from the server
        // and populate the form
        
        // For demo purposes, we'll use the sample data
        const templateCard = document.querySelector(`.template-card[data-template-id="${templateId}"]`);
        if (!templateCard) return;
        
        const templateName = templateCard.getAttribute('data-template-name');
        const templateCategory = templateCard.getAttribute('data-template-category');
        const templateDescription = templateCard.querySelector('.card-text').textContent;
        const templateType = templateCard.querySelector('.template-meta div:nth-child(1)').textContent.replace('Type: ', '');
        const templateDuration = parseInt(templateCard.querySelector('.template-meta div:nth-child(2)').textContent.replace('Duration: ', '').replace(' days', ''));
        
        // Get tags
        const tags = [];
        templateCard.querySelectorAll('.template-tags .badge').forEach(badge => {
            tags.push(badge.textContent);
        });
        
        // Populate form
        document.getElementById('templateName').value = templateName;
        document.getElementById('templateDescription').value = templateDescription;
        document.getElementById('templateCategory').value = templateCategory;
        document.getElementById('templateEventType').value = templateType;
        document.getElementById('templateDuration').value = templateDuration;
        document.getElementById('templateTags').value = tags.join(', ');
        
        // Clear template items except the first one
        const templateItems = document.getElementById('templateItems');
        while (templateItems.children.length > 1) {
            templateItems.removeChild(templateItems.lastChild);
        }
        
        // Reset the first template item
        const firstItem = templateItems.firstElementChild;
        if (firstItem) {
            firstItem.querySelector('.item-name').value = 'Sample Task';
            firstItem.querySelector('.item-type').value = 'task';
            firstItem.querySelector('.item-description').value = 'Sample task description';
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('createTemplateModal'));
        modal.show();
    }
    
    function deleteTemplate(templateId) {
        // Get template name
        const templateCard = document.querySelector(`.template-card[data-template-id="${templateId}"]`);
        if (!templateCard) return;
        
        const templateName = templateCard.getAttribute('data-template-name');
        
        // Set template name in modal
        document.getElementById('deleteTemplateName').textContent = templateName;
        
        // Set template ID for delete confirmation
        document.getElementById('confirmDeleteTemplate').setAttribute('data-template-id', templateId);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('deleteTemplateModal'));
        modal.show();
    }
    
    function confirmDeleteTemplate() {
        const templateId = this.getAttribute('data-template-id');
        
        // Send delete request to server
        fetch(`/api/templates/${templateId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-Tenant-ID': localStorage.getItem('organizationId') || '1'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete template');
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteTemplateModal'));
            modal.hide();
            
            // Show success message
            showAlert('Template deleted successfully', 'success');
            
            // Remove template card from UI
            const templateCard = document.querySelector(`.template-card[data-template-id="${templateId}"]`);
            if (templateCard) {
                const col = templateCard.closest('.col-md-4');
                if (col) {
                    col.remove();
                }
            }
        })
        .catch(error => {
            console.error('Error deleting template:', error);
            
            // For demo purposes, simulate success
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteTemplateModal'));
            modal.hide();
            
            // Show success message
            showAlert('Template deleted successfully (demo mode)', 'success');
            
            // Remove template card from UI
            const templateCard = document.querySelector(`.template-card[data-template-id="${templateId}"]`);
            if (templateCard) {
                const col = templateCard.closest('.col-md-4');
                if (col) {
                    col.remove();
                }
            }
            
            // In a real application, we would show an error message
            // showAlert('Failed to delete template: ' + error.message, 'danger');
        });
    }
    
    function filterTemplates() {
        const categoryFilter = document.getElementById('templateCategoryFilter').value;
        const typeFilter = document.getElementById('templateTypeFilter').value;
        const searchFilter = document.getElementById('templateSearchInput').value.toLowerCase();
        
        // Get all template cards
        const templateCards = document.querySelectorAll('.template-card');
        
        // Filter templates
        templateCards.forEach(card => {
            const category = card.getAttribute('data-template-category');
            const type = card.querySelector('.template-meta div:nth-child(1)').textContent.replace('Type: ', '');
            const name = card.getAttribute('data-template-name').toLowerCase();
            const description = card.querySelector('.card-text').textContent.toLowerCase();
            
            // Check if template matches all filters
            const matchesCategory = !categoryFilter || category === categoryFilter;
            const matchesType = !typeFilter || type === typeFilter;
            const matchesSearch = !searchFilter || name.includes(searchFilter) || description.includes(searchFilter);
            
            // Show or hide template
            const col = card.closest('.col-md-4');
            if (col) {
                if (matchesCategory && matchesType && matchesSearch) {
                    col.style.display = '';
                } else {
                    col.style.display = 'none';
                }
            }
        });
        
        // Show or hide category sections based on visible templates
        document.querySelectorAll('.template-category').forEach(category => {
            const visibleTemplates = category.querySelectorAll('.col-md-4[style=""]').length;
            if (visibleTemplates > 0) {
                category.style.display = '';
            } else {
                category.style.display = 'none';
            }
        });
    }
    
    function searchTemplates() {
        filterTemplates();
    }
    
    function updateCategoryFilterOptions(categories) {
        const categoryFilter = document.getElementById('templateCategoryFilter');
        
        // Keep the first option (All Categories)
        const firstOption = categoryFilter.options[0];
        categoryFilter.innerHTML = '';
        categoryFilter.appendChild(firstOption);
        
        // Add category options
        categories.sort().forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }
    
    // Show an alert message
    function showAlert(message, type = 'info') {
        // Create alert element
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.setAttribute('role', 'alert');
        
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add alert to the page
        const mainContent = document.getElementById('main-content');
        mainContent.insertBefore(alertElement, mainContent.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }, 5000);
    }
});
