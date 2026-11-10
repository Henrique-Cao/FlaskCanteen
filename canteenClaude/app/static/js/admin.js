// Logout button

const logoutBtn = document.getElementById('adminLogoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        console.log('Logging out...');
        logoutBtn.disabled = true;

        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            let data = {};
            try {
                data = await response.json();
            } catch (_) {}

            window.location.href = data.redirect_url || '/';
        } catch (err) {
            console.error('Logout failed:', err);
            logoutBtn.disabled = false;
            alert('A connection error occurred. Please try again.');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
            const toastElList = document.querySelectorAll('.toast');
            const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl));
            toastList.forEach(toast => toast.show());
            console.log('Toasts initialized');
        });


