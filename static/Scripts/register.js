function suggestPassword() {
  let length = prompt("How many characters should the password be?", "12");

  // Validate input
  if (!length || isNaN(length) || length < 8 || length > 16) {
    console.error("Password generation: Please enter a valid number between 8 and 16.");
    return;
  }

  const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$_";
  let password = "";
  for (let i = 0; i < Number(length); i++) {
    const char = charset[Math.floor(Math.random() * charset.length)];
    password += char;
  }

  const pwInput = document.getElementById("password");
  pwInput.value = password;

  const confirmInput = document.getElementById("confirm-password");
  if (confirmInput) confirmInput.value = password;

  pwInput.focus();
}


function togglePasswordVisibility() {
  const inputs = document.querySelectorAll(".PP");
  inputs.forEach(input => {
    input.type = input.type === "password" ? "text" : "password";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirm-password");

  form.addEventListener("submit", (e) => {
    if (password.value !== confirmPassword.value) {
      e.preventDefault();
      console.error("Password mismatch during registration.");
      confirmPassword.focus();
    }
  });
});

document.getElementById('login-form').addEventListener('keydown', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // Prevent double submit if needed
    this.querySelector('.Btn').click(); // Clicks the login button
  }
});

document.getElementById('register-form').addEventListener('keydown', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // To avoid accidental double-submit
    this.querySelector('.Btn').click();
  }
});

// Handle form submission
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




