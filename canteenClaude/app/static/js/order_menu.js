/* ==========================================================================
   1. API & NETWORK SERVICES
   ========================================================================== */

/**
 * Fetch current cart summary from the Flask backend.
 */
async function fetchCartContents() {
    try {
        const response = await fetch('/api/cart/get_cart');
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching cart contents:', error);
        throw error;
    }
}

/**
 * Send request to add a single item to the cart.
 */
async function sendAddToCartRequest(itemId) {
    try {
        const response = await fetch('/api/cart/add_to_cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId }),
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        console.log('Success response from server:', data);

        // Update UI using data returned directly from server
        await updateCartUI();
    } catch (error) {
        console.error('Error adding item to cart:', error);
    }
}

/**
 * Send request to clear all items from the cart.
 */
async function sendClearCartRequest() {
    try {
        const response = await fetch('/api/cart/clear', { method: 'POST' });
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        
        // Refresh both global UI elements and drawer items
        updateCartUI(data);
        renderCartDrawer(data);
    } catch (error) {
        console.error('Error clearing cart:', error);
    }
}

// API Service call to update quantity
async function sendUpdateQuantityRequest(itemId, newQty) {
    try {
        const response = await fetch('/api/cart/update_quantity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, quantity: newQty }),
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        
        // Re-render both global badges and drawer contents with updated calculations
        updateCartUI(data);
        renderCartDrawer(data);
    } catch (error) {
        console.error('Error updating quantity:', error);
    }
}

// Event Delegation inside Cart Drawer for Stepper Buttons
document.getElementById('cart-items-container')?.addEventListener('click', (event) => {
    const qtyBtn = event.target.closest('.qty-btn');
    if (!qtyBtn) return;

    const itemId = qtyBtn.getAttribute('data-item-id');
    const currentQty = parseInt(qtyBtn.getAttribute('data-qty'), 10);
    const action = qtyBtn.getAttribute('data-action');

    let newQty = currentQty;
    if (action === 'increase') {
        newQty += 1;
    } else if (action === 'decrease') {
        newQty -= 1;
    }

    sendUpdateQuantityRequest(itemId, newQty);
});

/* ==========================================================================
   2. UI RENDERERS & DOM UPDATERS
   ========================================================================== */

/**
 * Update global badges, totals, and floating cart bar visibility.
 */
async function updateCartUI(summaryData) {
    try {
        // Use passed data or fetch fresh cart payload if omitted
        const data = summaryData || (await fetchCartContents());

        const badge = document.getElementById('bar-item-count');
        const grandTotal = document.getElementById('bar-total');

        const totalItems = data.total_items ?? 0;
        const totalPrice = data.total_price ?? 0.0;
        console.log(`data:`, data);
        // Update sticky bar badge
        if (badge) {
            badge.textContent = `${totalItems} ${totalItems === 1 ? 'Item' : 'Items'}`;
            badge.classList.toggle('d-none', totalItems === 0);
        }

        // Update sticky bar price ($XX.XX)
        if (grandTotal) {
            grandTotal.textContent = `$${totalPrice.toFixed(2)}`;
        }
    } catch (error) {
        console.error('Failed to update cart UI:', error);
    }
}

/**
 * Render itemized line items and totals inside the Offcanvas Drawer.
 */
function renderCartDrawer(data) {
    const container = document.getElementById('cart-items-container');
    const grandTotalEl = document.getElementById('drawer-grand-total');

    if (!container) return;

    if (!data.items || data.items.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4">Your cart is empty</div>';
        if (grandTotalEl) grandTotalEl.textContent = '$0.00';
        return;
    }

    // Render line items with quantity steppers
    container.innerHTML = data.items.map(item => `
        <div class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
            <div class="flex-grow-1 me-2">
                <div class="fw-bold text-dark">${item.name}</div>
                <div class="text-muted small">$${item.unit_price.toFixed(2)} each</div>
            </div>
            
            <!-- Quantity Stepper Controls -->
            <div class="d-flex align-items-center gap-2 me-3">
                <button class="btn btn-sm btn-outline-secondary px-2 qty-btn" 
                        data-item-id="${item.id}" 
                        data-qty="${item.quantity}" 
                        data-action="decrease">-</button>
                <span class="fw-bold px-1">${item.quantity}</span>
                <button class="btn btn-sm btn-outline-secondary px-2 qty-btn" 
                        data-item-id="${item.id}" 
                        data-qty="${item.quantity}" 
                        data-action="increase">+</button>
            </div>

            <div class="fw-bold text-end style="min-width: 60px;">
                $${item.subtotal.toFixed(2)}
            </div>
        </div>
    `).join('');

    if (grandTotalEl) {
        grandTotalEl.textContent = `$${(data.total_price || 0).toFixed(2)}`;
    }
}

/* ==========================================================================
   3. EVENT LISTENERS & INITIALIZATION
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial UI update on page load
    updateCartUI();

    // 2. Offcanvas Cart Drawer Listener (loads fresh items when opened)
    const cartDrawer = document.getElementById('cartDrawer');
    if (cartDrawer) {
        cartDrawer.addEventListener('shown.bs.offcanvas', async () => {
            try {
                const data = await fetchCartContents();
                renderCartDrawer(data);
            } catch (error) {
                console.error('Error loading cart drawer:', error);
            }
        });
    }

    // 3. Clear Cart Button Listener
    const clearBtn = document.getElementById('clear-cart-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear your cart?')) {
                sendClearCartRequest();
                renderCartDrawer({ items: [], total_items: 0, total_price: 0.0 });
            }
        });
    }
});

// 4. Global Event Delegation for "Add to Cart" Buttons
document.addEventListener('click', (event) => {
    const btn = event.target.closest('.add-to-cart-btn');
    if (!btn) return;

    const itemId = btn.getAttribute('data-item-id');
    if (itemId) {
        sendAddToCartRequest(itemId);
    }
});