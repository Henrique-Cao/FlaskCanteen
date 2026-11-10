/**
 * static/js/features/dragDrop.js
 * Reusable wrapper for SortableJS drag-and-drop lists.
 */

export function initDragAndDrop({ containerId, handleClass, onReorder }) {
    const container = document.getElementById(containerId);
    
    // Safety check: ensure the container exists and Sortable was loaded via CDN
    if (!container || typeof Sortable === 'undefined') return;

    new Sortable(container, {
        animation: 150,
        handle: handleClass,
        ghostClass: 'bg-light',
        
        onEnd: () => {
            // 1. Gather all the elements in their new physical order
            const items = container.querySelectorAll('[data-id]');
            
            // 2. Extract the IDs into an array (e.g., [4, 1, 3, 2])
            const orderedIds = Array.from(items).map(item => parseInt(item.getAttribute('data-id'), 10));

            // 3. Optional UI touch: Update the visual numbers/badges on the screen
            items.forEach((item, index) => {
                const posBadge = item.querySelector('.badgePos');
                if (posBadge) posBadge.textContent = index;
            });

            // 4. Send the new array back to the controller to handle the database save
            onReorder(orderedIds);
        }
    });
}