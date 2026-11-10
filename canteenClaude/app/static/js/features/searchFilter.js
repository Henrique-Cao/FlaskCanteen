/**
 * static/js/features/searchFilter.js
 * Reusable UI listeners for text inputs and category buttons.
 */

export function initSearch({ inputId, onSearch }) {
    const searchInput = document.getElementById(inputId);
    
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        // Clean the input and pass the text back to the main controller
        const query = e.target.value.toLowerCase().trim();
        onSearch(query);
    });
}

export function initCategoryFilter({ buttonSelector, activeClass = 'active', onSelect }) {
    const filterBtns = document.querySelectorAll(buttonSelector);
    
    if (filterBtns.length === 0) return;

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Visual UI update (swaps the active color)
            filterBtns.forEach(b => b.classList.remove(activeClass));
            btn.classList.add(activeClass);
            
            // Extract the data attribute and pass it back to the controller
            const categoryId = btn.getAttribute('data-category-id');
            onSelect(categoryId);
        });
    });
}