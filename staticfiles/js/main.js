// IT Support System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // File upload drag and drop
    initializeFileUpload();
    
    // Chat functionality
    initializeChat();
    
    // Search functionality
    initializeSearch();
    
    // Dark mode functionality
    initializeDarkMode();
});

// Dark Mode Toggle
function toggleDarkMode() {
    fetch('/api/toggle-dark-mode/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Toggle the theme
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', newTheme);
            
            // Update the toggle button text and icon
            const icon = document.getElementById('dark-mode-icon');
            const text = document.getElementById('dark-mode-text');
            
            if (newTheme === 'dark') {
                icon.className = 'bi bi-sun';
                text.textContent = 'Light Mode';
            } else {
                icon.className = 'bi bi-moon';
                text.textContent = 'Dark Mode';
            }
        }
    })
    .catch(error => {
        console.error('Error toggling dark mode:', error);
    });
}

function initializeDarkMode() {
    // Set initial dark mode state
    const html = document.documentElement;
    const isDark = html.getAttribute('data-bs-theme') === 'dark';
    const icon = document.getElementById('dark-mode-icon');
    const text = document.getElementById('dark-mode-text');
    
    if (icon && text) {
        if (isDark) {
            icon.className = 'bi bi-sun';
            text.textContent = 'Light Mode';
        } else {
            icon.className = 'bi bi-moon';
            text.textContent = 'Dark Mode';
        }
    }
}

// File Upload with Drag and Drop
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const container = input.closest('.card-body') || input.parentElement;
        
        // Create drag and drop area
        const dropArea = document.createElement('div');
        dropArea.className = 'file-upload-area';
        dropArea.innerHTML = `
            <i class="bi bi-cloud-upload fs-1 text-muted"></i>
            <p class="mt-2 mb-0">Drag and drop files here or click to browse</p>
            <small class="text-muted">Max 10MB per file</small>
        `;
        
        // Insert drop area before the input
        input.parentNode.insertBefore(dropArea, input);
        input.style.display = 'none';
        
        // Click to browse
        dropArea.addEventListener('click', () => input.click());
        
        // Drag and drop events
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.classList.add('dragover');
        });
        
        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('dragover');
        });
        
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                updateFileDisplay(input, files);
            }
        });
        
        // File selection change
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateFileDisplay(input, e.target.files);
            }
        });
    });
}

function updateFileDisplay(input, files) {
    const dropArea = input.previousElementSibling;
    const fileList = Array.from(files).map(file => 
        `<div class="badge bg-primary me-1 mb-1">${file.name} (${formatFileSize(file.size)})</div>`
    ).join('');
    
    dropArea.innerHTML = `
        <i class="bi bi-check-circle-fill text-success fs-1"></i>
        <p class="mt-2 mb-2">Selected ${files.length} file(s)</p>
        <div class="file-list">${fileList}</div>
        <small class="text-muted">Click to change files</small>
    `;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Chat Functionality
function initializeChat() {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;
    
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const userSelect = document.getElementById('user-select');
    
    if (messageInput && sendButton && userSelect) {
        // Send message on button click
        sendButton.addEventListener('click', sendMessage);
        
        // Send message on Enter key
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Load messages when user is selected
        userSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                loadMessages(e.target.value);
            }
        });
        
        // Auto-refresh messages every 5 seconds
        setInterval(() => {
            if (userSelect.value) {
                loadMessages(userSelect.value);
            }
        }, 5000);
    }
}

function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const userSelect = document.getElementById('user-select');
    const sendButton = document.getElementById('send-button');
    
    if (!messageInput.value.trim() || !userSelect.value) return;
    
    // Disable send button
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';
    
    fetch('/api/send-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            receiver_id: userSelect.value,
            message: messageInput.value.trim()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageInput.value = '';
            loadMessages(userSelect.value);
        } else {
            alert('Error sending message: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error sending message');
    })
    .finally(() => {
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="bi bi-send"></i> Send';
    });
}

function loadMessages(userId) {
    fetch(`/api/get-messages/${userId}/`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayMessages(data.messages);
        }
    })
    .catch(error => {
        console.error('Error loading messages:', error);
    });
}

function displayMessages(messages) {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) return;
    
    messagesContainer.innerHTML = messages.map(msg => `
        <div class="d-flex mb-3 ${msg.is_sender ? 'justify-content-end' : 'justify-content-start'}">
            <div class="chat-message ${msg.is_sender ? 'sent' : 'received'}">
                <div class="message-content">${escapeHtml(msg.message)}</div>
                <div class="message-time small text-muted mt-1">
                    ${new Date(msg.timestamp).toLocaleTimeString()}
                </div>
            </div>
        </div>
    `).join('');
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            // Auto-submit search form after 500ms of no typing
            const form = e.target.closest('form');
            if (form && e.target.value.length >= 2) {
                form.submit();
            }
        }, 500);
    });
}

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Form Validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add form validation to all forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Loading States
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// Confirmation Dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    Copied to clipboard!
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    });
}

// Ticket ID click to copy
document.addEventListener('DOMContentLoaded', function() {
    const ticketIds = document.querySelectorAll('.ticket-id');
    ticketIds.forEach(id => {
        id.addEventListener('click', () => {
            copyToClipboard(id.textContent);
        });
        id.style.cursor = 'pointer';
        id.title = 'Click to copy';
    });
});

// Auto-save form data
function autoSaveForm(formId, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    const storageKey = `autosave_${formId}`;
    
    // Load saved data
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            inputs.forEach(input => {
                if (data[input.name]) {
                    input.value = data[input.name];
                }
            });
        } catch (e) {
            console.error('Error loading saved form data:', e);
        }
    }
    
    // Save data periodically
    setInterval(() => {
        const formData = {};
        inputs.forEach(input => {
            if (input.name && input.value) {
                formData[input.name] = input.value;
            }
        });
        localStorage.setItem(storageKey, JSON.stringify(formData));
    }, interval);
    
    // Clear saved data on successful submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(storageKey);
    });
}

// Initialize auto-save for create ticket form
document.addEventListener('DOMContentLoaded', function() {
    autoSaveForm('create-ticket-form');
});
