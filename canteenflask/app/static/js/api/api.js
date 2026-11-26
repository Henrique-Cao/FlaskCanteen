/**
 * static/js/api/api.js
 * Handles all network requests to the Flask backend.
 */

export async function fetchJSON(url, options = {}) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    const defaultHeaders = { 
        'Content-Type': 'application/json',
        ...(csrfToken && { 'X-CSRFToken': csrfToken })
    };

    const config = {
        ...options,
        headers: { ...defaultHeaders, ...options.headers }
    };
    
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || `HTTP Error ${response.status}`);
    }
    return data;
}