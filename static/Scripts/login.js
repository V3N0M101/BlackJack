// Function to ensure message box is ready
function ensureMessageBoxReady() {
    return new Promise((resolve) => {
        const checkElements = () => {
            const msgText = document.querySelector('.msg-text');
            const okBtn = document.querySelector('.ok-btn');
            if (msgText && okBtn) {
                resolve();
            } else {
                setTimeout(checkElements, 100);
            }
        };
        checkElements();
    });
}

// Initialize login page
window.addEventListener("DOMContentLoaded", async () => {
    loadComponent("navbar", "navbar.html");
    
    // Wait for message box elements to be ready
    await ensureMessageBoxReady();

    // Check for verification success parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('verified') === 'true') {
        const msgText = document.querySelector('.msg-text');
        const okBtn = document.querySelector('.ok-btn');
        msgText.textContent = "Account verified successfully! You can now log in.";
        okBtn.textContent = "OK";
        okBtn.onclick = hideMessageBox;
        showMessageBox();
        // Remove the parameter from URL without refreshing
        window.history.replaceState({}, document.title, "/login");
    }
});

// Handle form submission
document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            const msgText = document.querySelector('.msg-text');
            const okBtn = document.querySelector('.ok-btn');
            msgText.textContent = "Login successful";
            okBtn.textContent = "OK";
            okBtn.onclick = function() {
                hideMessageBox();
                window.location.href = '/';
            };
            showMessageBox();
        } else {
            // Show error message
            const msgText = document.querySelector('.msg-text');
            const okBtn = document.querySelector('.ok-btn');
            msgText.textContent = data.message || "Invalid username or password";
            okBtn.textContent = "OK";
            okBtn.onclick = hideMessageBox;
            showMessageBox();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const msgText = document.querySelector('.msg-text');
        const okBtn = document.querySelector('.ok-btn');
        msgText.textContent = "An error occurred. Please try again.";
        okBtn.textContent = "OK";
        okBtn.onclick = hideMessageBox;
        showMessageBox();
    });
});

// Handle page cache
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        // Page was loaded from back/forward cache — reload it
        window.location.reload();
    }
}); 