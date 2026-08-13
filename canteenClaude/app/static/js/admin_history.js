function openOrderModal(order) {
    // 1. Populate Order & Customer Info
    document.getElementById('modalOrderId').textContent = order.orderNumber.startsWith('#') ? order.orderNumber : '#' + order.orderNumber;
    document.getElementById('modalOrderTime').textContent = order.time;
    document.getElementById('modalCustomerName').textContent = order.customer || 'N/A';
    document.getElementById('modalCustomerPhone').textContent = order.phone || 'N/A';
    document.getElementById('modalOrderTotal').textContent = '$' + parseFloat(order.total).toFixed(2);
    
    // 2. Status Pill Styling
    const statusPill = document.getElementById('modalOrderStatus');
    statusPill.textContent = '✓ ' + order.status.toUpperCase();
    statusPill.className = 'status-pill ';
    
    const lowerStatus = order.status.toLowerCase();
    if (lowerStatus.includes('picked') || lowerStatus.includes('paid') || lowerStatus.includes('completed') || lowerStatus.includes('ready')) {
        statusPill.classList.add('pill-success');
    } else if (lowerStatus.includes('cancel')) {
        statusPill.classList.add('pill-danger');
    } else {
        statusPill.classList.add('pill-warning');
    }

    // 3. Render Order Items
    const itemsContainer = document.getElementById('modalOrderItemsList');
    itemsContainer.innerHTML = '';
    
    if (order.items && order.items.length > 0) {
        
        order.items.forEach(item => {
            const itemRow = document.createElement('div');
            itemRow.className = 'd-flex justify-content-between align-items-center py-1 border-bottom';
            itemRow.innerHTML = `
                <div>${item.name}</div>
                <div>Qty: ${item.qty}</div>
                <div>Price: $${parseFloat(item.price).toFixed(2)}</div>
            `;
            itemsContainer.appendChild(itemRow);
        });

    } else {
        itemsContainer.innerHTML = '<div class="text-muted text-center py-2">No item details available</div>';
    }

    // 4. Trigger Modal
    const modalElement = document.getElementById('orderDetailsModal');
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
    modalInstance.show();
}