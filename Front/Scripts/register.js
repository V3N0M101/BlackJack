function suggestPassword() {
  let length = prompt("How many characters should the password be?", "12");

  // Validate input
  if (!length || isNaN(length) || length < 8 || length > 16) {
    alert("Please enter a valid number between 8 and 16.");
    return;
  }

  const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~";
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
      alert("Passwords do not match.");
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




