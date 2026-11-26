/**
 * Global Dark Pill Toast Utility
 * @param {string} message - The main text of the toast (e.g., "Order #444 Cancelled").
 * @param {string} type - 'success', 'danger', or 'info'.
 * @param {string} actionText - The text for the action button (e.g., "Undo").
 * @param {function} onAction - The JS function to run if the action button is clicked.
 */
function showToast(message, type = 'success', actionText = null, onAction = null) {
    const container = document.getElementById('globalToastContainer');
    if (!container) return;

    // Define crisp, high-contrast icons
    let icon = 'bi-check-circle-fill text-success';
    if (type === 'danger' || type === 'error') icon = 'bi-exclamation-circle-fill text-danger';
    if (type === 'info') icon = 'bi-info-circle-fill text-info';

    const toastEl = document.createElement('div');
    
    // Native Bootstrap dark theme ensures 0% transparency and perfect contrast
    toastEl.className = 'toast align-items-center text-bg-dark border-0 shadow-lg rounded-pill mb-2';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.setAttribute('data-bs-delay', actionText ? '8000' : '4000'); 

    // Build a distinct, brightly colored action button (like Undo) separated by a border line
    const actionHtml = actionText 
        ? `<div class="ms-auto pe-2 border-start border-secondary ps-3">
             <button class="btn btn-sm btn-link text-warning text-decoration-none fw-bold p-0 toast-action-btn">${actionText}</button>
           </div>` 
        : '';

    toastEl.innerHTML = `
        <div class="d-flex align-items-center px-2 py-1">
            <div class="toast-body d-flex align-items-center flex-grow-1 p-1 gap-2 pe-3">
                <i class="bi ${icon} fs-5"></i>
                <span class="fw-medium text-white" style="letter-spacing: 0.2px;">${message}</span>
            </div>
            
            ${actionHtml}
            
            <button type="button" class="btn-close btn-close-white ms-2 me-1" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl);
    bsToast.show();

    // If an action (Undo) is provided, bind the click event to your custom function
    if (actionText && onAction) {
        const actionBtn = toastEl.querySelector('.toast-action-btn');
        actionBtn.addEventListener('click', () => {
            onAction();
            bsToast.hide(); // Hide the toast immediately after they click undo
        });
    }

    // Clean up DOM
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}