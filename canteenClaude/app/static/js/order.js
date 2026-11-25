//Create order when checkout button is clicked
document.addEventListener('DOMContentLoaded', () => {
    const checkoutBtn = document.getElementById('checkout-button');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', async () => {
            try {
                console.log('Checkout button clicked. Sending request to create order...');
                const response = await fetch('/api/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ customer_name: 'John Doe', phone: '12345678', items: [] }),
                });
                if (!response.ok) {
                    throw new Error(`Server returned status ${response.status}`);
                }
                const data = await response.json();
                console.log('Order created successfully:', data);
                // Redirect to order confirmation page
                console.log('Redirecting to order confirmation page:', data.redirect_url);
                window.location.href = data.redirect_url; // Redirect to order confirmation page
            } catch (error) {
                console.error('Error creating order:', error);
            }
        });
    }
});


async function refreshMenuControls() {
    const response = await fetch('/api/cart/get_cart');

    if (!response.ok) {
        throw new Error(`Could not load cart: ${response.status}`);
    }

    const cart = await response.json();
    const quantities = new Map(
        cart.items.map(item => [String(item.id), item.quantity])
    );

    document.querySelectorAll('.menu-item-controls').forEach(control => {
        const quantity = quantities.get(control.dataset.itemId) ?? 0;

        control.querySelector('.menu-add-btn')
            .classList.toggle('d-none', quantity > 0);

        control.querySelector('.menu-stepper')
            .classList.toggle('d-none', quantity === 0);

        control.querySelector('.menu-quantity').textContent = quantity;
    });
}

document.body.addEventListener('cartUpdated', () => {
    refreshMenuControls().catch(error => {
        console.error('Failed to refresh menu quantities:', error);
        // Show a visible error message in the menu.
    });
});


