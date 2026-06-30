async function deleteMenuItem(itemId, itemName) {
    console.log(`Attempting to delete menu item with ID: ${itemId} and Name: "${itemName}"`);
    // 1. Confirm with the user before committing the deletion
    if (!confirm(`Are you sure you want to permanently delete "${itemName}"?`)) {
        return;
    }

    try {
        // 2. Perform the API call targeting the configured endpoint
        const response = await fetch(`/api/menu/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (response.ok) {
            // 3. Target the DOM container row element and cleanly drop it from layout tree
            const itemRow = document.getElementById(`menu-item-row-${itemId}`);
            if (itemRow) {
                // Apply a quick smooth fade out animation right before deletion
                itemRow.style.transition = 'all 0.3s ease';
                itemRow.style.opacity = '0';
                itemRow.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    itemRow.remove();
                }, 300);
                console.log(`Menu item removed: ${itemId}`);
            }
        } else {
            // Display structured fallback error messages handled from your API 
            alert(`Error: ${result.error || 'Failed to remove menu item.'}`);
        }
    } catch (error) {
        console.error("API call execution error:", error);
        alert("Unable to reach network server. Please check your system context connections.");
    }
}