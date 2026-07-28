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
function deleteCategory(categoryId, categoryName) {
    console.log(`Attempting to delete category with ID: ${categoryId} and Name: "${categoryName}"`);
    if (!confirm(`Are you sure you want to permanently delete the category "${categoryName}"? This action cannot be undone.`)) {
        return;
    }

    fetch(`/api/categories/delete/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json()) // Now safe because Flask sends JSON
    .then(data => {
        if (data.success) {
            // Either refresh or remove the element from DOM directly
            window.location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener("DOMContentLoaded", function() {
    // 1. Listen for clicks on elements marked with data-action="edit"
    document.body.addEventListener("click", function(event) {
        const trigger = event.target.closest('[data-action="edit"]');
        if (!trigger) return;

        const itemId = trigger.getAttribute("data-item-id");
        // 2. Fetch the clean model entry properties from our backend endpoint
        fetch(`/api/menu/${itemId}`)
            .then(response => response.json())
            .then(data => {
                // 3. Inject entity property values directly into our singular DOM skeleton fields
                document.getElementById("edit_item_id").value = data.id;
                document.getElementById("edit_name").value = data.name;
                document.getElementById("edit_price").value = data.price;
                document.getElementById("edit_category").value = data.category;
                document.getElementById("edit_description").value = data.description;
                
                // 4. Update the form action string route dynamically
                document.getElementById("editItemForm").action = `/api/menu/update/${data.id}`;

                // 5. Initialize and display the Bootstrap modal instance safely
                const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
                editModal.show();
            })
            .catch(err => console.error("Could not sync entity state logs:", err));
    });
});
document.addEventListener("DOMContentLoaded", function() {
    const editItemForm = document.getElementById("editItemForm");
    
    if (editItemForm) {
        editItemForm.addEventListener("submit", function(event) {
            // 1. Terminate native traditional page redirect submission behavior
            event.preventDefault();

            // 2. Identify the active target entity ID from our hidden field
            const itemId = document.getElementById("edit_item_id").value;
            
            // 3. Assemble fields matching your Python data parsing requirements
            const payload = {
                name: document.getElementById("edit_name").value,
                price: parseFloat(document.getElementById("edit_price").value),
                category: document.getElementById("edit_category").value,
                description: document.getElementById("edit_description").value
            };
            
            // 4. Retrieve the action route string constructed dynamically by your interceptor click handler
            const targetActionUrl = editItemForm.getAttribute("action") || `/api/menu/update/${itemId}`;

            // 5. Dispatch async JSON request package with strict header flags
            fetch(targetActionUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // Crucial flag prevents 415 error codes
                },
                body: JSON.stringify(payload) // Converts JavaScript literal to plain text string stream
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server tracking failed with status code: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                // 6. Close the active operational modal overlay cleanly via Bootstrap core APIs
                const modalEl = document.getElementById('editItemModal');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) modalInstance.hide();

                // 7. Force UI repaint loop to update the item cards dynamically
                window.location.reload();
            })
            .catch(err => {
                console.error("Could not sync edit modification payload:", err.message);
                alert("Failed to save changes. Verify terminal application status.");
            });
        });
    }
});
document.addEventListener("DOMContentLoaded", function() {
    const addItemForm = document.getElementById("addItemForm");
    
    if (addItemForm) {
        addItemForm.addEventListener("submit", function(event) {
            // 1. Stop the browser from performing a classic page-reload submission
            event.preventDefault();

            // 2. Extract values cleanly from the form inputs
            const payload = {
                name: document.getElementById("name").value,
                category: document.getElementById("category").value,
                price: parseFloat(document.getElementById("price").value),
                description: document.getElementById("description").value,

            };
            
            // 3. Fire an asynchronous request matching your exact backend JSON criteria
            fetch('/api/menu/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // Explicitly passes the missing media flag
                },
                body: JSON.stringify(payload) // Converts the JS object to a true JSON string
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server tracking failed with status code: ${response.status}`);
                }
                // Close the modal cleanly via Bootstrap's programmatic instance handler
                const modalEl = document.getElementById('addItemModal');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) modalInstance.hide();

                // Reload the page layout to display your newly appended items row
                window.location.reload();
            })
            .catch(err => {
                console.error("Could not complete JSON add payload sync:", err.message);
                alert("Failed to add item. Check terminal console logs.");
            });
        });
    }
});