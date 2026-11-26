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
        
        const itemRow = document.getElementById(`menuItemCard-${itemId}`);
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
    const container = document.getElementById('sortableCategoryList');
    if (!container) return;

    const sortable = new Sortable(container, {
        animation: 200,
        handle: '.dragHandle',
        onEnd: function () {
            const orderedIds = sortable.toArray().map(id => parseInt(id, 10));

            // Update visible position badge numbers in UI
            container.querySelectorAll('[data-id]').forEach((item, index) => {
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
        updateCategoryOrder(orderedIds);
        return;
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
            // const payload = {
            //     name: document.getElementById("editName").value,
            //     price: parseFloat(document.getElementById("editPrice").value),
            //     category: document.getElementById("editCategory").value,
            //     description: document.getElementById("editDescription").value
            // };
            const formData = new FormData(editItemForm);
            const targetUrl = editItemForm.getAttribute("action") || `/api/menu/update/${itemId}`;
           
            try {
                // await fetchJSON(targetUrl, {
                //     method: 'POST',
                //     body: JSON.stringify(payload)
                // });
                const response = await fetch(targetUrl, {
                    method: 'POST',
                    body: formData 
                    // CRITICAL: Do not set headers like {'Content-Type': 'multipart/form-data'}. 
                    // The browser must do it automatically for file uploads to work.
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                // Close the modal and reload the grid to show the new item
                window.location.reload(); 
            } catch (err) {
                console.error("Error saving edit:", err);
                alert("Failed to save changes.");
            }
        });
    }

    // New Item Form
    const addItemForm = document.getElementById("addItemForm");

    if (addItemForm) {
        addItemForm.addEventListener("submit", async function (event) {
            // Stop the default HTML page refresh
            event.preventDefault();

            // 1. Automatically bundle all text inputs and file inputs
            const formData = new FormData(addItemForm);

            try {
                // 2. Use standard fetch (Do NOT use a wrapper that forces application/json)
                const response = await fetch('/api/menu/', {
                    method: 'POST',
                    body: formData 
                    // CRITICAL: Do not set headers like {'Content-Type': 'multipart/form-data'}. 
                    // The browser must do it automatically for file uploads to work.
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                // Close the modal and reload the grid to show the new item
                window.location.reload(); 
                
            } catch (err) {
                console.error("Error adding item:", err);
                alert("Failed to add item. Please try again.");
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



/**
 * Reorders the rendered category sections and filter buttons
 * according to the given ordered list of category ids.
 * Ids not in the list keep their relative order after the listed ones.
 */
function updateCategoryOrder(orderedIds) {
    const ids = orderedIds.map(String);
    const rank = (id) => {
        const i = ids.indexOf(String(id));
        return i === -1 ? ids.length : i;
    };

    const reorder = (elements, attr) => {
        if (!elements.length) return;
        const parent = elements[0].parentElement;
        elements
            .map((el, idx) => ({ el, idx }))
            .sort((a, b) =>
                rank(a.el.getAttribute(attr)) - rank(b.el.getAttribute(attr)) || a.idx - b.idx)
            .forEach(({ el }) => parent.appendChild(el));
    };

    reorder(Array.from(document.querySelectorAll('.category-section')), 'data-section-category');

    const buttons = Array.from(document.querySelectorAll('.btn-category'))
        .filter(b => b.getAttribute('data-category-id') !== 'all');
    reorder(buttons, 'data-category-id');
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Map the DOM elements
    const filterBtns = document.querySelectorAll('.btn-category');
    const categorySections = document.querySelectorAll('.category-section');

    // 2. Attach listeners to the buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            
            // --- STEP 1: VISUAL FEEDBACK ---
            // Strip active state from all buttons, apply to the clicked one
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // --- STEP 2: DOM FILTERING ---
            // Read the ID the user just clicked
            const selectedCategoryId = btn.getAttribute('data-category-id');
            
            // Loop through all the pre-loaded menu sections
            categorySections.forEach(section => {
                const sectionId = section.getAttribute('data-section-category');
                // If user clicked "All Items", or if the section matches the button
                if (selectedCategoryId === 'all' || selectedCategoryId === sectionId) {
                    section.classList.remove('d-none'); // Reveal
                } else {
                    section.classList.add('d-none');    // Hide
                }
            });
            
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Grab the input and the button
    const imageInput = document.getElementById('editImage');
    const clearImageBtn = document.getElementById('clearImageBtn');

    if (imageInput && clearImageBtn) {
        
        // 2. The Sensor: Show the 'X' button ONLY when a file is selected
        imageInput.addEventListener('change', () => {
            // If the browser detects 1 or more files in the queue
            if (imageInput.files.length > 0) {
                clearImageBtn.classList.remove('d-none'); // Show button
            } else {
                clearImageBtn.classList.add('d-none');    // Hide button
            }
        });

        // 3. The Trigger: What happens when they click 'X'
        clearImageBtn.addEventListener('click', () => {
            
            // Wipe the file from the browser's memory
            imageInput.value = ''; 
            
            // Hide the button again
            clearImageBtn.classList.add('d-none'); 
            
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const categorySections = document.querySelectorAll('.category-section');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const searchQuery = searchInput.value.toLowerCase();    
            categorySections.forEach(section => {
                const menuItems = section.querySelectorAll('.menu-item-card');
                menuItems.forEach(item => {
                    const itemName = item.querySelector('.card-title').textContent.toLowerCase();
                    item.classList.toggle('d-none', !itemName.includes(searchQuery));
                });
            });
        });
    }
});