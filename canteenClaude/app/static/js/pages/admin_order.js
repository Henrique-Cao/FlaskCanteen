
import { fetchJSON } from '../api/api.js';

async function syncOrders() {
    try {
        const orders = await fetchJSON('/api/order');
        for (const order of orders ?? []) {
            const orderId = String(order.id ?? order.order_id ?? '');
            const exists = Array.from(document.querySelectorAll('.order-card'))
                .some(card => card.dataset.orderId === orderId);

            if (order.status === 'pending' && !exists) {
                createOrderCard(order);
            }
        }
    } catch (error) {
        console.error(error);
    }
    initializeOrderCardClickListeners();
    
    
}




function createOrderCard(order) {
    const template = document.getElementById('order-card-template');
    const card = template.content.cloneNode(true);
    const orderCard = card.querySelector('.order-card');
    orderCard.dataset.orderId = order.id ?? order.order_id ?? '';
    orderCard.querySelector('.order-number').textContent = `#${order.id ?? order.order_id ?? ''}`;
    // orderCard.querySelector('.order-status-badge').textContent = order.status;
    for (const item of order.items ?? []) {
        const itemNumber = document.createElement('div');
        itemNumber.classList.add('fw-bold');
        itemNumber.textContent = item.quantity + 'x';
        const itemElement = document.createElement('div');
        itemElement.classList.add('d-flex', 'gap-1', 'mb-1');
        itemElement.textContent = (item.name ?? item.item_name ?? '');
        itemElement.prepend(itemNumber);
        orderCard.querySelector('.order-items-preview').appendChild(itemElement);
    }
    orderCard.addEventListener('click', () => renderOrderDetails(order));
    document.getElementById('order-scroll-section').appendChild(card);
}

function removeOrderCard(orderId) {
    const orderCard = document.querySelector(`.order-card[data-order-id='${orderId}']`);
    if (orderCard) {
        orderCard.remove();
    }
}

function renderOrderDetails(order) {
    const template = document.getElementById('order-details-shell-template');
    const details = template.content.cloneNode(true);
    document.querySelector('.order-details-section').replaceChildren(details);
    const detailNumber = document.querySelector('.detail-number');
    detailNumber.textContent = " #" + order.id ?? order.order_id ?? '';
    // const detailStatusBadge = document.querySelector('.detail-status-badge');
    // detailStatusBadge.textContent = order.status;
    const detailCustomerName = document.querySelector('.detail-customer-name');
    detailCustomerName.textContent = order.customer_name ?? 'Walk-in';
    const detailCustomerPhone = document.querySelector('.detail-customer-phone');
    detailCustomerPhone.textContent = order.phone ?? '';
    const detailTime = document.querySelector('.detail-time');
    detailTime.textContent = order.placed_time ?? 'just now';
    const detailItemsList = document.querySelector('.detail-items-list');
    for (const item of order.items ?? []) {
        const itemTemplate = document.getElementById('order-detail-item-template');
        const itemElement = itemTemplate.content.cloneNode(true);
        itemElement.querySelector('.item-qty').textContent = `${item.quantity}x`;
        itemElement.querySelector('.item-name').textContent = item.name ?? item.item_name ?? '';
        detailItemsList.appendChild(itemElement);
    }
    const detailTotalPrice = document.querySelector('.detail-total-price');
    detailTotalPrice.textContent = `$${order.total_price ?? order.total ?? '0.00'}`;
    const detailBtnPrimary = document.getElementById('markAsCompletedBtn');
    detailBtnPrimary.addEventListener('click', () => markOrderAsCompleted(order.id));
    const detailBtnSecondary = document.getElementById('cancelOrderBtn');
    detailBtnSecondary.addEventListener('click', () => markOrderAsCancelled(order.id));
    
}

syncOrders();


function initializeOrderCardClickListeners() {
    const orderCards = document.querySelectorAll('.order-card');
    const activeCard = document.querySelector('.active-order')
    if (orderCards.length > 0) {
        orderCards.forEach(card => {
            card.addEventListener('click', function() {
                const orderId = this.dataset.orderId;
                setActiveOrderCard(orderId);
            });
        });
        if (!activeCard) {
            orderCards[0].click();
            setActiveOrderCard(orderCards[0].dataset.orderId);
        }
    }
    
}

function setActiveOrderCard(orderId) {
    const orderCards = document.querySelectorAll('.order-card');
    orderCards.forEach(card => {
        if (card.dataset.orderId === orderId) {
            card.classList.add('active-order');
        } else {
            card.classList.remove('active-order');
        }
    });
}

function markOrderAsCompleted(orderId) {
    fetch(`/api/order/${orderId}/complete`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            
            removeOrderCard(orderId);
            syncOrders();
            showToast(`Order #${orderId} Completed`, 'success');
        } else {
            console.error('Failed to mark order as completed:', data);
        }
    })
    .catch(error => console.error('Error:', error));
}

function markOrderAsCancelled(orderId) {
    fetch(`/api/order/${orderId}/cancel`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            removeOrderCard(orderId);
            syncOrders();
            showToast(`Order #${orderId} Cancelled`, 'danger');
        } else {
            console.error('Failed to cancel order:', data);
        }
    })
    .catch(error => console.error('Error:', error));
}
