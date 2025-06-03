// Handle form submissionAdd commentMore actions
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        // Basic client-side validation
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        const username = formData.get('username');
        
        if (password !== confirmPassword) {
            const msgText = document.querySelector('.msg-text');
            const okBtn = document.querySelector('.ok-btn');
            msgText.textContent = "Passwords do not match";
            okBtn.textContent = "OK";
            okBtn.onclick = hideMessageBox;
            showMessageBox();
            return;
        }

        if (username.length > 16) {
            const msgText = document.querySelector('.msg-text');
            const okBtn = document.querySelector('.ok-btn');
            msgText.textContent = "Username must be 16 characters or less";
            okBtn.textContent = "OK";
            okBtn.onclick = hideMessageBox;
            showMessageBox();
            return;
        }
        
        fetch('/register', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const msgText = document.querySelector('.msg-text');
            const okBtn = document.querySelector('.ok-btn');
            
            if (data.success) {
                msgText.textContent = data.message || "Registration successful! Please verify your email.";
                okBtn.textContent = "OK";
                okBtn.onclick = function() {
                    hideMessageBox();
                    window.location.href = data.redirect_url || '/verify';
                };
            } else {
                msgText.textContent = data.message || "Username or email already exists";
                okBtn.textContent = "OK";
                okBtn.onclick = hideMessageBox;
            }
            showMessageBox();
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
});

// Handle page cache
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        window.location.reload();
    }
});