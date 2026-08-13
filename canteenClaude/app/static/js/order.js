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



