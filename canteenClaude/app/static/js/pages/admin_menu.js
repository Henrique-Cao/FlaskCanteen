import { fetchJSON } from '../api/api.js';
import { initSearch, initCategoryFilter } from '../features/searchFilter.js';
import { showModal, populateForm, animateRowRemoval, updateCategoryOrder } from '../ui/ui.js';
import { initDragAndDrop } from '../features/dragDrop.js';
import { bindFormSubmit, initImageClearBtn } from '../features/forms.js';


// ==========================================
// 1. THE MASTER STATE
// ==========================================
// This holds the exact truth of what is happening in the app right now
const state = {
    allMenuItems: [],    // The raw data from SQLite
    currentSearch: '',   // What the user is typing
    currentCategory: 'all' // What category they clicked
};

function applyFilters() {
    const categorySections = document.querySelectorAll('.category-section');
    
    categorySections.forEach(section => {
        const sectionCatId = section.getAttribute('data-section-category');
        const cards = section.querySelectorAll('.menu-item-card');
        let hasVisibleCards = false;

        cards.forEach(card => {
            const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
            const desc = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
            
            const matchesCat = (state.currentCategory === 'all' || sectionCatId === state.currentCategory);
            const matchesSearch = title.includes(state.currentSearch) || desc.includes(state.currentSearch);

            if (matchesCat && matchesSearch) {
                card.classList.remove('d-none');
                hasVisibleCards = true;
            } else {
                card.classList.add('d-none');
            }
        });

        section.classList.toggle('d-none', !hasVisibleCards);
    });
}

// ==========================================
// 2. ACTION HANDLERS (EDIT / DELETE)
// ==========================================
async function handleEditItem(btn) {
    const { itemId } = btn.dataset;
    try {
        const data = await fetchJSON(`/api/menu/${itemId}`);
        populateForm({
            'editItemId': data.id,
            'editName': data.name,
            'editPrice': data.price,
            'editCategory': data.category_id ?? '', 
            'editDescription': data.description
        });
        document.getElementById("editItemForm").action = `/api/menu/update/${data.id}`;
        showModal('editItemModal');
    } catch (err) {
        alert("Could not load item details.");
    }
}

function handleEditCategory(btn) {
    const { categoryId, categoryName } = btn.dataset;
    populateForm({ 'editCategoryId': categoryId, 'editCategoryName': categoryName });
    showModal('editCategoryModal');
}

async function handleDeleteItem(btn) {
    const { itemId, itemName } = btn.dataset;
    if (!confirm(`Permanently delete "${itemName}"?`)) return;

    try {
        console.log("deleting", itemId, itemName);
        await fetchJSON(`/api/menu/${itemId}`, { method: 'DELETE' });
        animateRowRemoval(document.getElementById(`menuItemCard-${itemId}`));
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

async function handleDeleteCategory(btn) {
    const { categoryId, categoryName } = btn.dataset;
    if (!confirm(`Delete category "${categoryName}"?`)) return;

    try {
        await fetchJSON(`/api/categories/delete/${categoryId}`, { method: 'POST' });
        const catElement = document.getElementById(`categoryRow-${categoryId}`);
        if (catElement) catElement.remove();
        else window.location.reload();
    } catch (err) {
        alert(`Failed to delete category: ${err.message}`);
    }
}

function initActionTriggers() {
    const actions = {
        'edit': handleEditItem,
        'edit-category': handleEditCategory,
        'delete-item': handleDeleteItem,
        'delete-category': handleDeleteCategory
    };

    document.body.addEventListener("click", (event) => {
        
        const btn = event.target.closest('[data-action]');
        console.log(btn);
        if (!btn) return;
        const handler = actions[btn.dataset.action];
        if (handler) handler(btn);
    });
}
// ==========================================
// 3. INITIALIZATION
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    initActionTriggers();
    // 2. Initialize UI Filters
    initSearch({
        inputId: 'searchInput',
        onSearch: (query) => {
            state.currentSearch = query;
            applyFilters();
        }
    });
    initCategoryFilter({
        buttonSelector: '.btn-category',
        onSelect: (categoryId) => {
            state.currentCategory = categoryId;
            applyFilters();
        }
    });

    // 3. Initialize Drag & Drop
    initDragAndDrop({
        containerId: 'sortableCategoryList',
        handleClass: '.dragHandle',
        onReorder: async (orderedIds) => {
            // Controller handles the API call, not the feature file
            try {
                await fetchJSON('/api/categories/reorder', { 
                    method: 'POST', 
                    body: JSON.stringify({ ordered_ids: orderedIds }) 
                });
                updateCategoryOrder(orderedIds);
            } catch (err) {
                alert("Failed to save the new category order.");
            }
        }
    });

    // 4. Initialize Forms
    bindFormSubmit({
        formId: 'addItemForm',
        onSubmit: async (formData) => {
            const res = await fetch('/api/menu/', { method: 'POST', body: formData });
            if (!res.ok) throw new Error("Server rejected item");
            window.location.reload(); 
        }
    });

    bindFormSubmit({
        formId: 'editItemForm',
        onSubmit: async (formData, formEl) => {
            const targetUrl = formEl.getAttribute("action");
            const res = await fetch(targetUrl, { method: 'POST', body: formData });
            if (!res.ok) throw new Error("Server rejected edit");
            window.location.reload(); 
        }
    });

    bindFormSubmit({
        formId: 'addCategoryForm',
        onSubmit: async (formData) => {
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            await fetchJSON('/api/categories/add', { method: 'POST', body: JSON.stringify(data) });
            window.location.reload();
        }
    });

    bindFormSubmit({
        formId: 'editCategoryForm',
        onSubmit: async (formData) => {
            const id = formData.get("editCategoryId");
            const name = formData.get("editCategoryName");
            console.log(id, name);
            await fetchJSON(`/api/categories/update/${id}`, { method: 'POST', body: JSON.stringify({ name }) });
            window.location.reload();
        }
    });
    // 5. Initialize Independent UI Widgets
    initImageClearBtn({ inputId: 'editImage', buttonId: 'clearEditImageBtn' });
    initImageClearBtn({ inputId: 'add_image_filename', buttonId: 'clearAddImageBtn' }); // Repeat for Add Item form if needed
});
