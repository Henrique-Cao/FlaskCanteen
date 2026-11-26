
async function openOrderModal(orderNumber) {
    const modalElement = document.getElementById('orderDetailsModal');
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);

    // 1. Reset UI & show loading state
    document.getElementById('modalOrderId').textContent = orderNumber.startsWith('#') ? orderNumber : '#' + orderNumber;
    document.getElementById('modalOrderTime').textContent = 'Loading...';
    document.getElementById('modalCustomerName').textContent = 'Loading...';
    document.getElementById('modalCustomerPhone').textContent = 'Loading...';
    document.getElementById('modalOrderTotal').textContent = '$0.00';
    
    const itemsContainer = document.getElementById('modalOrderItemsList');
    itemsContainer.innerHTML = `
        <div class="text-center py-3 text-muted">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div> Loading items...
        </div>
    `;

    // 2. Open modal immediately so UI feels responsive
    modalInstance.show();

    // 3. Fetch full dataset from server
    try {
  
        const response = await fetch("/api/order/" + orderNumber);
        if (!response.ok) throw new Error('Failed to load order');

        const order = await response.json();
        
 
        // 4. Populate Customer & Order Info
        document.getElementById('modalOrderTime').textContent = order.time;
        document.getElementById('modalCustomerName').textContent = order.customer;
        document.getElementById('modalCustomerPhone').textContent = order.phone;
        document.getElementById('modalOrderTotal').textContent = '$' + parseFloat(order.total).toFixed(2);

        // 5. Update Status Pill
        const statusPill = document.getElementById('modalOrderStatus');
        const lowerStatus = (order.status || '').toLowerCase();
        statusPill.textContent = '✓ ' + (order.status || 'UNKNOWN').toUpperCase();
        statusPill.className = 'status-pill ';

        if (['picked up', 'paid', 'completed', 'ready', 'collected'].some(s => lowerStatus.includes(s))) {
            statusPill.classList.add('pill-success');
        } else if (lowerStatus.includes('cancel')) {
            statusPill.classList.add('pill-danger');
        } else {
            statusPill.classList.add('pill-warning');
        }

        // 6. Populate Items List
        itemsContainer.innerHTML = '';
        if (Array.isArray(order.items) && order.items.length > 0) {
            order.items.forEach(item => {
                const itemRow = document.createElement('div');
                itemRow.className = 'd-flex justify-content-between align-items-center py-2 border-bottom';
                
                const qty = parseInt(item.qty || 1, 10);
                const price = parseFloat(item.price || 0);
                const lineTotal = (qty * price).toFixed(2);

                itemRow.innerHTML = `
                    <div>
                        <span class="fw-bold me-1">${qty}x</span>
                        <span>${item.name}</span>
                    </div>
                    <div class="fw-semibold text-dark">$${lineTotal}</div>
                `;
                itemsContainer.appendChild(itemRow);
            });
        } else {
            itemsContainer.innerHTML = '<div class="text-muted text-center py-2">No item details available</div>';
        }

    } catch (err) {
        console.error('Error opening order modal:', err);
        itemsContainer.innerHTML = `<div class="alert alert-danger py-2 m-2">Could not fetch order data.</div>`;
    }
}