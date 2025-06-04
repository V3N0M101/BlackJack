function suggestPassword() {
  const msgText = document.querySelector('.msg-text');
  const okBtn = document.querySelector('.ok-btn');
  
  // Create input element
  const input = document.createElement('input');
  input.type = 'number';
  input.min = '8';
  input.max = '16';
  input.placeholder = '8-16 characters';
  input.style.width = '200%';
  input.style.padding = '8px';
  input.style.marginTop = '10px';
  input.style.marginLeft = '10px';
  input.style.border = '1px solid #ccc';
  input.style.borderRadius = '4px';
  
  // Clear existing content and add input
  msgText.textContent = 'Password length:';
  msgText.appendChild(input);
  
  okBtn.textContent = 'Generate';
  okBtn.onclick = function() {
    const length = parseInt(input.value);
    
    if (!length || length < 12 || length > 16) {
      msgText.textContent = 'Please enter a valid number between 8 and 16';
      okBtn.textContent = 'OK';
      okBtn.onclick = hideMessageBox;
      return;
    }

    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$_";
    let password = "";
    for (let i = 0; i < length; i++) {
      const char = charset[Math.floor(Math.random() * charset.length)];
      password += char;
    }

    const pwInput = document.getElementById("password");
    pwInput.value = password;

    const confirmInput = document.getElementById("confirm-password");
    if (confirmInput) confirmInput.value = password;

    hideMessageBox();
    pwInput.focus();
  };
  
  showMessageBox();
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
