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
                //window.location.href = '/order_confirmation';
            } catch (error) {
                console.error('Error creating order:', error);
            }
        });
    }
});