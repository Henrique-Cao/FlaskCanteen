/**
 * admin_menu.js
 * Core management script for Canteen Admin operations (Menu Items & Categories).
 * Handles dynamic modals, CRUD API interactions, event delegation, and drag-and-drop reordering.
 */

document.addEventListener("DOMContentLoaded", function () {
    initSortable();
    initActionTriggers();
    initFormHandlers();
});


// =============================================================================
// 1. UTILITIES & API HELPERS
// =============================================================================

/**
 * Wrapper for standard fetch API that handles JSON headers and CSRF tokens.
 * @param {string} url - API Endpoint URL
 * @param {Object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<Object>} Parsed JSON response
 */
async function fetchJSON(url, options = {}) {
    // Retrieve CSRF token from HTML meta tag if Flask-WTF is active
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    const defaultHeaders = { 
        'Content-Type': 'application/json',
        ...(csrfToken && { 'X-CSRFToken': csrfToken })
    };

    const config = {
        ...options,
        headers: { ...defaultHeaders, ...options.headers }
    };
    
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || `HTTP Error ${response.status}`);
    }
    return data;
}

/**
 * Utility: Safely shows a Bootstrap modal by element ID
 * @param {string} id - HTML ID of the modal
 */
function showModal(id) {
    const modalEl = document.getElementById(id);
    if (!modalEl) return;

    // Move the modal directly to <body> to escape parent CSS stacking contexts
    if (modalEl.parentNode !== document.body) {
        document.body.appendChild(modalEl);
    }

    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
    modalInstance.show();
}
/**
 * Utility: Populates multiple form inputs at once using a key-value object map
 * @param {Object} fieldMap - Object where keys are element IDs and values are field values
 */
function populateForm(fieldMap) {
    Object.entries(fieldMap).forEach(([id, value]) => {
        const input = document.getElementById(id);
        if (input) input.value = value ?? '';
    });
}


// =============================================================================
// 2. EVENT DELEGATION & ACTION ROUTING
// =============================================================================

/**
 * Action Dictionary: Maps data-action attribute values to handler functions
 */
const actions = {
    'edit': handleEditItem,
    'edit-category': handleEditCategory,
    'delete-item': handleDeleteItem,
    'delete-category': handleDeleteCategory
};

/**
 * Single document-level click listener using event delegation.
 * Catches clicks on elements with [data-action] and delegates to matching handler.
 */
function initActionTriggers() {
    document.body.addEventListener("click", (event) => {
        const btn = event.target.closest('[data-action]');
        if (!btn) return;

        const handler = actions[btn.dataset.action];
        if (handler) handler(btn);
    });
}


// =============================================================================
// 3. ACTION HANDLERS (CLICK ROUTE TARGETS)
// =============================================================================

/**
 * Fetches menu item data from API and opens edit modal populated with data.
 * @param {HTMLElement} btn - The clicked button element containing dataset attributes
 */
async function handleEditItem(btn) {
    const { itemId } = btn.dataset;
    try {
        const data = await fetchJSON(`/api/menu/${itemId}`);
        
        // Populates inputs using standard camelCase element IDs
        populateForm({
            'editItemId': data.id,
            'editName': data.name,
            'editPrice': data.price,
            'editCategory': data.category_id ?? '',  // Use empty string if category_id is null
            'editDescription': data.description
        });
        document.getElementById("editItemForm").action = `/api/menu/update/${data.id}`;
        showModal('editItemModal');
    } catch (err) {
        alert("Could not load item details.");
    }
}

/**
 * Opens category edit modal using data stored directly in button dataset.
 * @param {HTMLElement} btn - The clicked button element
 */
function handleEditCategory(btn) {
    const { categoryId, categoryName } = btn.dataset;
    
    populateForm({
        'editCategoryId': categoryId,
        'editCategoryName': categoryName
    });
    console.log(`Editing category: ${categoryName} (ID: ${categoryId})`);
    showModal('editCategoryModal');
}

/**
 * Handler for menu item deletion trigger.
 * @param {HTMLElement} btn 
 */
function handleDeleteItem(btn) {
    const { itemId, itemName } = btn.dataset;
    deleteMenuItem(itemId, itemName);
}

/**
 * Handler for category deletion trigger.
 * @param {HTMLElement} btn 
 */
function handleDeleteCategory(btn) {
    const { categoryId, categoryName } = btn.dataset;
    deleteCategory(categoryId, categoryName);
}


// =============================================================================
// 4. API DELETE & SORT OPERATIONS
// =============================================================================

/**
 * Sends DELETE request for a menu item and smoothly removes its row from DOM.
 */
async function deleteMenuItem(itemId, itemName) {
    if (!confirm(`Are you sure you want to permanently delete "${itemName}"?`)) return;

    try {
        await fetchJSON(`/api/menu/${itemId}`, { method: 'DELETE' });
        
        const itemRow = document.getElementById(`menuItemRow-${itemId}`);
        if (itemRow) {
            itemRow.style.transition = 'all 0.3s ease';
            itemRow.style.opacity = '0';
            itemRow.style.transform = 'scale(0.95)';
            setTimeout(() => itemRow.remove(), 300);
        }
    } catch (error) {
        console.error("Delete menu item error:", error);
        alert(`Error: ${error.message}`);
    }
}

/**
 * Sends POST request to delete a category and updates DOM dynamically.
 */
async function deleteCategory(categoryId, categoryName) {
    if (!confirm(`Are you sure you want to delete category "${categoryName}"?`)) return;

    try {
        await fetchJSON(`/api/categories/delete/${categoryId}`, { method: 'POST' });
        
        const catElement = document.getElementById(`categoryRow-${categoryId}`);
        if (catElement) {
            catElement.remove();
        } else {
            window.location.reload();
        }
    } catch (error) {
        console.error('Delete category error:', error);
        alert(`Failed to delete category: ${error.message}`);
    }
}

/**
 * Initializes SortableJS drag-and-drop on category container if present.
 */
function initSortable() {
    const container = document.getElementById('categoryList');
    if (!container) return;

    const sortable = new Sortable(container, {
        animation: 200,
        handle: '.dragHandle',
        onEnd: function () {
            const orderedIds = sortable.toArray().map(id => parseInt(id, 10));

            // Update visible position badge numbers in UI
            container.querySelectorAll('.dragItem').forEach((item, index) => {
                const posBadge = item.querySelector('.badgePos');
                if (posBadge) posBadge.textContent = index;
            });

            saveNewOrder(orderedIds);
        }
    });
}

/**
 * Syncs reordered category list to backend database.
 */
async function saveNewOrder(orderedIds) {
    try {
        await fetchJSON('/api/categories/reorder', {
            method: 'POST',
            body: JSON.stringify({ ordered_ids: orderedIds })
        });
        console.log('Order sync complete.');
    } catch (error) {
        console.error('Error updating order:', error);
        alert("Failed to save category order.");
    }
}


// =============================================================================
// 5. FORM SUBMISSION LISTENERS
// =============================================================================

function initFormHandlers() {
    
    // --- Edit Item Form ---
    const editItemForm = document.getElementById("editItemForm");
    if (editItemForm) {
        editItemForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const itemId = document.getElementById("editItemId").value;
            const payload = {
                name: document.getElementById("editName").value,
                price: parseFloat(document.getElementById("editPrice").value),
                category: document.getElementById("editCategory").value,
                description: document.getElementById("editDescription").value
            };

            const targetUrl = editItemForm.getAttribute("action") || `/api/menu/update/${itemId}`;

            try {
                await fetchJSON(targetUrl, {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                window.location.reload(); 
            } catch (err) {
                console.error("Error saving edit:", err);
                alert("Failed to save changes.");
            }
        });
    }

    // --- Add Item Form ---
    const addItemForm = document.getElementById("addItemForm");
    if (addItemForm) {
        addItemForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const payload = {
                name: document.getElementById("addName").value,
                category: parseInt(document.getElementById("addCategory").value),
                price: parseFloat(document.getElementById("addPrice").value),
                description: document.getElementById("addDescription").value
            };

            try {
                await fetchJSON('/api/menu/', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                window.location.reload();
            } catch (err) {
                console.error("Error adding item:", err);
                alert("Failed to add item.");
            }
        });
    }

    // --- Edit Category Form ---
    const editCategoryForm = document.getElementById("editCategoryForm");
    if (editCategoryForm) {
        editCategoryForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const categoryId = document.getElementById("editCategoryId").value;
            const updatedName = document.getElementById("editCategoryName").value;

            try {
                // FIXED: Await pause prevents instant reload bug
                await fetchJSON(`/api/categories/update/${categoryId}`, {
                    method: 'POST',
                    body: JSON.stringify({ name: updatedName })
                });

                window.location.reload(); 
            } catch (err) {
                console.error("Error saving category edit:", err);
                alert("Failed to save category changes.");
            }
        });
    }

    // --- Add Category Form ---
    const addCategoryForm = document.getElementById("addCategoryForm");
    if (addCategoryForm) {
        addCategoryForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const newCategoryName = document.getElementById("addCategoryName").value;
            
            try {
                await fetchJSON('/api/categories/add', {
                    method: 'POST',
                    body: JSON.stringify({ name: newCategoryName })
                });
                window.location.reload(); 
            } catch (err) {
                console.error("Error adding category:", err);
                alert("Failed to add category.");
            }          
        });
    }
}