document.addEventListener("DOMContentLoaded", function () {
    initSortable();
    initEditModalTriggers();
    initFormHandlers();
});

// Helper for unified fetch calls
async function fetchJSON(url, options = {}) {
    const defaultHeaders = { 'Content-Type': 'application/json' };
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

// 1. MENU ITEM DELETION
async function deleteMenuItem(itemId, itemName) {
    if (!confirm(`Are you sure you want to permanently delete "${itemName}"?`)) return;

    try {
        await fetchJSON(`/api/menu/${itemId}`, { method: 'DELETE' });
        
        const itemRow = document.getElementById(`menu-item-row-${itemId}`);
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

// 2. CATEGORY DELETION
async function deleteCategory(categoryId, categoryName) {
    if (!confirm(`Are you sure you want to delete category "${categoryName}"?`)) return;

    try {
        await fetchJSON(`/api/categories/delete/${categoryId}`, { method: 'POST' });
        
        // Dynamic DOM Removal instead of window.location.reload()
        const catElement = document.getElementById(`category-row-${categoryId}`);
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

// 3. SORTABLE CATEGORIES
function initSortable() {
    const container = document.getElementById('categoryList');
    if (!container) return;

    const sortable = new Sortable(container, {
        animation: 200,
        handle: '.drag-handle',
        onEnd: function () {
            const orderedIds = sortable.toArray().map(id => parseInt(id, 10));

            // Update visible badge position counters
            container.querySelectorAll('.drag-item').forEach((item, index) => {
                const posBadge = item.querySelector('.badge-pos');
                if (posBadge) posBadge.textContent = index;
            });

            saveNewOrder(orderedIds);
        }
    });
}

async function saveNewOrder(orderedIds) {
    try {
        await fetchJSON('/api/categories/reorder', {
            method: 'POST',
            body: JSON.stringify({ ordered_ids: orderedIds })
        });
        console.log('Order sync complete.');
        // No page reload necessary - Sortable already updated DOM visually!
    } catch (error) {
        console.error('Error updating order:', error);
        alert("Failed to save category order.");
    }
}

// 4. EDIT MODAL TRIGGER
function initEditModalTriggers() {
    document.body.addEventListener("click", async function (event) {
        
        // --- A. MENU ITEM EDIT TRIGGER ---
        const itemTrigger = event.target.closest('[data-action="edit"]');
        if (itemTrigger) {
            const itemId = itemTrigger.getAttribute("data-item-id");
            try {
                const data = await fetchJSON(`/api/menu/${itemId}`);
                
                document.getElementById("edit_item_id").value = data.id;
                document.getElementById("edit_name").value = data.name;
                document.getElementById("edit_price").value = data.price;
                document.getElementById("edit_category").value = data.category;
                document.getElementById("edit_description").value = data.description;
                
                document.getElementById("editItemForm").action = `/api/menu/update/${data.id}`;

                const editModalEl = document.getElementById('editItemModal');
                bootstrap.Modal.getOrCreateInstance(editModalEl).show();
            } catch (err) {
                console.error("Could not fetch item details:", err);
                alert("Could not load item details.");
            }
            return; // Exit function after handling item
        }

        // --- B. CATEGORY EDIT TRIGGER ---
        const categoryTrigger = event.target.closest('[data-action="edit-category"]');
        if (categoryTrigger) {
            const categoryId = categoryTrigger.getAttribute("data-category-id");
            const categoryName = categoryTrigger.getAttribute("data-category-name");

            // Populate the static modal inputs directly from the button's data attributes
            document.getElementById("edit_category_id").value = categoryId;
            document.getElementById("edit_category_name").value = categoryName;

            const editModalEl = document.getElementById('editCategoryModal');
            bootstrap.Modal.getOrCreateInstance(editModalEl).show();
        }
    });
}
// 5. FORM SUBMISSIONS (ADD & EDIT)
function initFormHandlers() {
    // Edit Form Handler
    const editItemForm = document.getElementById("editItemForm");
    if (editItemForm) {
        editItemForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const itemId = document.getElementById("edit_item_id").value;
            const payload = {
                name: document.getElementById("edit_name").value,
                price: parseFloat(document.getElementById("edit_price").value),
                category: document.getElementById("edit_category").value,
                description: document.getElementById("edit_description").value
            };

            const targetUrl = editItemForm.getAttribute("action") || `/api/menu/update/${itemId}`;

            try {
                await fetchJSON(targetUrl, {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });

                const modalEl = document.getElementById('editItemModal');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) modalInstance.hide();

                window.location.reload(); 
            } catch (err) {
                console.error("Error saving edit:", err);
                alert("Failed to save changes.");
            }
        });
    }

    // Add Form Handler
    const addItemForm = document.getElementById("addItemForm");
    if (addItemForm) {
        addItemForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const payload = {
                name: document.getElementById("name").value,
                category: document.getElementById("category").value,
                price: parseFloat(document.getElementById("price").value),
                description: document.getElementById("description").value
            };

            try {
                await fetchJSON('/api/menu/', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });

                const modalEl = document.getElementById('addItemModal');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) modalInstance.hide();

                window.location.reload();
            } catch (err) {
                console.error("Error adding item:", err);
                alert("Failed to add item.");
            }
        });
    }

    // --- Category Edit Form Handler ---
    const editCategoryForm = document.getElementById("editCategoryForm");
    if (editCategoryForm) {
        editCategoryForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const categoryId = document.getElementById("edit_category_id").value;
            const updatedName = document.getElementById("edit_category_name").value;
            console.log("Submitting category edit for ID:", categoryId, "with new name:", updatedName);
            try {
                
                fetchJSON(`/api/categories/update/${categoryId}`, {
                    method: 'POST',
                    body: JSON.stringify({ name: updatedName })
                });

                //Hide Modal
                const modalEl = document.getElementById('editCategoryModal');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) modalInstance.hide();

                // Reload the page to show the new name, matching your menu item behavior
                window.location.reload(); 
            } catch (err) {
                console.error("Error saving category edit:", err);
                alert("Failed to save category changes.");
            }
        });
    }
    
}