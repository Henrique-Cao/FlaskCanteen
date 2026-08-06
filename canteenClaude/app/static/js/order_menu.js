function sendAddToCartRequest(itemId) {
    console.log(`Sending request to add item ID: ${itemId} to cart`);
    
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
        // You can update badges or UI elements using `data.cart` here
    })
    .catch(error => {
        console.error('Error adding item to cart:', error);
    });
}

document.addEventListener('click', (event) => {
    const btn = event.target.closest('.add-to-cart-btn');
    if (!btn) return;

    const itemId = btn.getAttribute('data-item-id');
    console.log(`Button clicked for item ID: ${itemId}`);
    sendAddToCartRequest(itemId);
});