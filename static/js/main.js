// Hospital Queue Management System - Main JavaScript

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#28a745';
            break;
        case 'error':
            notification.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ffc107';
            notification.style.color = '#212529';
            break;
        default:
            notification.style.backgroundColor = '#17a2b8';
    }
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Format datetime for input fields
function formatDateTimeForInput(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Validate phone number
function validatePhone(phone) {
    const phoneRegex = /^\d{10,15}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
}

// Validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Generic API call function
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (response.ok) {
            return { success: true, data: result };
        } else {
            return { success: false, error: result.error || 'An error occurred' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Initialize page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit') {
                const originalText = this.textContent;
                this.textContent = 'Loading...';
                this.disabled = true;
                
                // Re-enable after 3 seconds (fallback)
                setTimeout(() => {
                    this.textContent = originalText;
                    this.disabled = false;
                }, 3000);
            }
        });
    });
    
    // REMOVED FORM VALIDATION - Let page-specific handlers manage forms
    });
    
    // Add search functionality to tables
    addTableSearch();
});

// Add search functionality to data tables
function addTableSearch() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Create search input
        const searchContainer = document.createElement('div');
        searchContainer.style.cssText = 'margin-bottom: 1rem; text-align: right;';
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search table...';
        searchInput.style.cssText = `
            padding: 0.5rem;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            width: 250px;
        `;
        
        searchContainer.appendChild(searchInput);
        table.parentNode.insertBefore(searchContainer, table);
        
        // Add search functionality
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Export functions for use in other scripts
window.hospitalQueue = {
    showNotification,
    formatDateTimeForInput,
    validatePhone,
    validateEmail,
    apiCall
};