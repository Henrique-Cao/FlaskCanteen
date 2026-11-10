/**
 * Reusable form binder and image input handler.
 */
export function bindFormSubmit({ formId, onSubmit }) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn ? submitBtn.innerHTML : '';

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';
            }
            const formData = new FormData(form);
            console.log(formData);
            await onSubmit(formData, form);
        } catch (error) {
            console.error(`Form submission error on #${formId}:`, error);
            alert("Failed to submit form.");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        }
    });
}

export function initImageClearBtn({ inputId, buttonId }) {
    const imageInput = document.getElementById(inputId);
    const clearImageBtn = document.getElementById(buttonId);

    if (imageInput && clearImageBtn) {
        imageInput.addEventListener('change', () => {
            clearImageBtn.classList.toggle('d-none', imageInput.files.length === 0);
        });
        clearImageBtn.addEventListener('click', () => {
            imageInput.value = ''; 
            clearImageBtn.classList.add('d-none'); 
        });
    }
}