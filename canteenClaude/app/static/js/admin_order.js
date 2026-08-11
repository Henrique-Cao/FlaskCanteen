const STATUS_CONFIG = {
    pending: { next: 'confirmed', btnText: 'Start Prep', btnClass: 'btn-primary' },
    confirmed: { next: 'ready', btnText: 'Mark Ready', btnClass: 'btn-success' },
    ready: { next: 'collected', btnText: 'Complete Order', btnClass: 'btn-info' },
    collected: { next: null, btnText: null, btnClass: null }
};

async function fetchAndRenderOrders() {
    try {
        const response = await fetch('/api/order');
        if (!response.ok) return;
        const orders = await response.json();

        const statuses = ['pending', 'confirmed', 'ready', 'collected'];
        const counts = { pending: 0, confirmed: 0, ready: 0, collected: 0 };
        let activeTotal = 0;

        // Clear existing containers
        statuses.forEach(status => {
            const dCol = document.getElementById(`col-${status}`);
            const mCol = document.getElementById(`m-col-${status}`);
            if (dCol) dCol.innerHTML = '';
            if (mCol) mCol.innerHTML = '';
        });

        const template = document.getElementById('order-card-template');

        orders.forEach(order => {
            const status = order.status;
            if (!counts.hasOwnProperty(status)) return;

            counts[status]++;
            const config = STATUS_CONFIG[status];

            // Render order card helper
            const createCardNode = () => {
                const clone = template.content.cloneNode(true);
                const card = clone.querySelector('.order-card');
                card.dataset.orderId = order.id;

                // Safe field assignments
                clone.querySelector('.order-id').textContent = `#${order.id}`;
                
                const orderType = order.order_type || order.type || 'Dine-in';
                const tableInfo = order.table_info || order.table_number || order.table || 'Table N/A';
                clone.querySelector('.order-meta').textContent = `${orderType} / ${tableInfo}`;

                const elapsedMins = order.elapsed_mins ?? order.elapsed_time ?? 0;
                const timerBadge = clone.querySelector('.order-timer');
                timerBadge.textContent = `${elapsedMins}m`;
                timerBadge.classList.add(status === 'pending' ? 'bg-warning' : 'bg-primary', 'text-dark');

                // Items list
                const itemsList = clone.querySelector('.order-items');
                (order.items || []).forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'mb-1';
                    li.textContent = `${item.quantity || 1}x ${item.name || item.title}`;
                    itemsList.appendChild(li);
                });

                // Notes
                if (order.special_notes || order.notes) {
                    const notesContainer = clone.querySelector('.order-notes');
                    notesContainer.classList.remove('d-none');
                    clone.querySelector('.notes-text').textContent = order.special_notes || order.notes;
                }

                // Action button
                const actionBtn = clone.querySelector('.action-btn');
                if (config.next) {
                    actionBtn.textContent = config.btnText;
                    actionBtn.classList.add(config.btnClass);
                    actionBtn.dataset.orderId = order.id;
                    actionBtn.dataset.nextStatus = config.next;
                } else {
                    actionBtn.remove();
                }

                return clone;
            };

            // Append card to desktop & mobile containers
            const dCol = document.getElementById(`col-${status}`);
            const mCol = document.getElementById(`m-col-${status}`);
            if (dCol) dCol.appendChild(createCardNode());
            if (mCol) mCol.appendChild(createCardNode());
        });

        // Update counts and toggle empty placeholders dynamically
        statuses.forEach(status => {
            const count = counts[status];
            if (status !== 'completed') activeTotal += count;

            // Ensure outer column wrappers remain visible on desktop
            const wrapper = document.getElementById(`col-wrapper-${status}`);
            if (wrapper) wrapper.classList.remove('d-none');

            // Badges
            const dCount = document.getElementById(`count-${status}`);
            const mCount = document.getElementById(`m-count-${status}`);
            if (dCount) dCount.textContent = count;
            if (mCount) mCount.textContent = count;

            // Toggle active cards container vs empty placeholder
            const colEl = document.getElementById(`col-${status}`);
            const emptyEl = document.getElementById(`empty-${status}`);

            if (count === 0) {
                if (colEl) colEl.classList.add('d-none');
                if (emptyEl) emptyEl.classList.remove('d-none');
            } else {
                if (colEl) colEl.classList.remove('d-none');
                if (emptyEl) emptyEl.classList.add('d-none');
            }
        });

        const activeCountEl = document.getElementById('activeOrdersCount');
        if (activeCountEl) activeCountEl.textContent = activeTotal;

    } catch (err) {
        console.error("Error fetching live orders:", err);
    }
}

// Initial fetch and 5-second polling interval
document.addEventListener('DOMContentLoaded', () => {
    fetchAndRenderOrders();
    setInterval(fetchAndRenderOrders, 5000);
});


function handleActionButtonClick(event) {
    const btn = event.target.closest('.action-btn');
    if (!btn) return;
    const orderId = btn.dataset.orderId;
    const nextStatus = btn.dataset.nextStatus;

    if (!orderId || !nextStatus) return;

    // Make an API call to update the order status
    fetch(`/api/order/${orderId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: nextStatus })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        // Optionally, re-fetch and render orders
        fetchAndRenderOrders();
    })
    .catch(err => {
        console.error('Error updating order status:', err);
    });
}

// Event delegation for action buttons
document.addEventListener('click', handleActionButtonClick);