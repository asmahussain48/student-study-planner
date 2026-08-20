// Global utilities for the application

// Format date to YYYY-MM-DD
function formatDate(date) {
    if (typeof date === 'string') return date;
    return date.toISOString().split('T')[0];
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Disable button during submission
function disableButton(btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
}

// Enable button
function enableButton(btn, text) {
    btn.disabled = false;
    btn.innerHTML = text;
}

// Initialize tooltips (Bootstrap)
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});

// API error handler
async function handleApiError(response) {
    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'An error occurred');
    }
    return response;
}
