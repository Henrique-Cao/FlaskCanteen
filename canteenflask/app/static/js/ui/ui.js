/**
 * static/js/ui/ui.js
 * A toolkit for visual DOM manipulation, animations, and Bootstrap interactions.
 */

/**
 * Safely finds and opens a Bootstrap modal.
 * @param {string} id - The HTML ID of the modal (e.g., 'editItemModal')
 */
export function showModal(id) {
    const modalEl = document.getElementById(id);
    if (!modalEl) return;

    // Move the modal to the <body> tag to prevent CSS stacking/z-index traps
    if (modalEl.parentNode !== document.body) {
        document.body.appendChild(modalEl);
    }

    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
    modalInstance.show();
}

/**
 * Automatically loops through a dictionary and fills HTML inputs.
 * @param {Object} fieldMap - { inputId: "Value to insert" }
 */
export function populateForm(fieldMap) {
    Object.entries(fieldMap).forEach(([id, value]) => {
        const input = document.getElementById(id);
        if (input) {
            input.value = value ?? '';
        }
    });
}

/**
 * Applies CSS transitions to smoothly shrink and fade a row before deleting it.
 * @param {HTMLElement} rowElement - The physical DOM node to remove
 */
export function animateRowRemoval(rowElement) {
    if (!rowElement) return;
    
    // Apply inline CSS for a smooth exit animation
    rowElement.style.transition = 'all 0.3s ease';
    rowElement.style.opacity = '0';
    rowElement.style.transform = 'scale(0.95)';
    
    // Wait 300ms for the animation to finish, then delete the HTML
    setTimeout(() => rowElement.remove(), 300);
}

/**
 * Physically moves category sections in the DOM to match a new order.
 * @param {Array} orderedIds - Array of category IDs (e.g., [4, 1, 3])
 */
export function updateCategoryOrder(orderedIds) {
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
            .sort((a, b) => rank(a.el.getAttribute(attr)) - rank(b.el.getAttribute(attr)) || a.idx - b.idx)
            .forEach(({ el }) => parent.appendChild(el)); // appendChild physically moves the element
    };

    // 1. Reorder the grid sections on the right
    reorder(Array.from(document.querySelectorAll('.category-section')), 'data-section-category');

    // 2. Reorder the filter buttons on the left sidebar
    const buttons = Array.from(document.querySelectorAll('.btn-category')).filter(b => b.getAttribute('data-category-id') !== 'all');
    reorder(buttons, 'data-category-id');
}