document.getElementById("checkoutForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("checkout form submitted");
    const btn = document.getElementById("place-order-btn");
    const errorBox = document.getElementById("checkout-error");
    const formData = new FormData(e.target);

    btn.disabled = true;
    // errorBox.innerHTML = "";

    try {
        console.log("sending")
        const res = await fetch("/api/order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(Object.fromEntries(formData)),
        });
        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.error || "Unable to place order.");
        }
        console.log("order created:", data);
        console.log("redirecting to:", data.redirect_url || `/order_confirmation/${data.order_number}`);
        // Redirect using the URL or order ID returned by your JSON API
        window.location.href = data.redirect_url || `/order_confirmation/${data.order_number}`;
    } catch (err) {
        errorBox.innerHTML = `<div class="alert alert-danger py-2 small mb-3">${err.message}</div>`;
        btn.disabled = false;
    }
});