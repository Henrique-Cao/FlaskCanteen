function sendAddToCartRequest(itemId) {    
    fetch('/api/cart/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id: itemId }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Success response from server:', data);
        updateCartBadge();  // Update the cart badge after adding an item
        // You can update badges or UI elements using `data.cart` here
    })
    .catch(error => {
        console.error('Error adding item to cart:', error);
    });
}

// 1. Mark the function as 'async' so 'await' can pause execution
async function updateCartBadge() {
    try {
        const data = await fetchCartContents();
        const badge = document.getElementById('bar-item-count');
        const totalPrice = document.getElementById('bar-total');

        if (badge) {
            // Extract the cart object whether Flask returns { cart: {...} } or {...} directly
            const cartObj = data.cart || data.items || data;

            // Handle both object-maps { item_id: qty } and arrays of item objects [{ qty: 1 }]
            let totalItems = 0;
            if (Array.isArray(cartObj)) {
                totalItems = cartObj.reduce((sum, item) => sum + (item.qty || 1), 0);
            } else if (typeof cartObj === 'object' && cartObj !== null) {
                totalItems = Object.values(cartObj).reduce((sum, quantity) => {
                    return sum + (typeof quantity === 'number' ? quantity : (quantity.qty || 0));
                }, 0);
            }

            badge.textContent = `${totalItems} Items`;
            
            

            // Optionally toggle visibility if cart is empty
            badge.classList.toggle('d-none', totalItems === 0);
        }
    } catch (error) {
        console.error('Failed to update cart badge:', error);
    }
}

async function fetchCartContents() {
    return fetch('/api/cart/get_cart')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Fetched cart contents:', data);
            return data;
        })
        .catch(error => {
            console.error('Error fetching cart contents:', error);
            throw error;
        });
}

document.addEventListener('click', (event) => {
    const btn = event.target.closest('.add-to-cart-btn');
    if (!btn) return;

    const itemId = btn.getAttribute('data-item-id');
    sendAddToCartRequest(itemId);
});

updateCartBadge();  // Initial call to update the badge on page load