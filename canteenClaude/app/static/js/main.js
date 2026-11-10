
const loginForm  = document.getElementById('adminLoginForm')

loginForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const form = e.target;
    const alertBox = document.getElementById('adminLoginAlert');
    const submitBtn = document.getElementById('adminLoginSubmitBtn');
    
    // Reset alert & set loading state
    alertBox.classList.add('d-none');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Logging in...';

    const payload = {
        username: form.adminUsername.value.trim(),
        password: form.adminPassword.value
    };
   
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
       
        if (response.ok && data.success) {
            console.log('Login successful, redirecting to:', data.redirect_url || '/admin/');
            window.location.href = data.redirect_url || '/admin/';
        } else {
            alertBox.textContent = data.message || 'Invalid username or password.';
            alertBox.classList.remove('d-none');
        }
    } catch (err) {
        alertBox.textContent = 'A connection error occurred. Please try again.';
        alertBox.classList.remove('d-none');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
});



