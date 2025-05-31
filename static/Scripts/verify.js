// Function to show the custom message box
function showCustomMessageBox(message) {
    const customMessageBox = document.getElementById('customMessageBox');
    const messageBoxText = document.getElementById('messageBoxText');
    const messageBoxCloseBtn = document.getElementById('messageBoxCloseBtn');

    if (!customMessageBox || !messageBoxText || !messageBoxCloseBtn) {
        console.error("Custom message box elements not found!");
        alert(message); // Fallback to browser alert if elements are missing
        return;
    }

    messageBoxText.textContent = message;
    customMessageBox.classList.add('show');

    messageBoxCloseBtn.onclick = function() {
        customMessageBox.classList.remove('show');
    };

    window.onclick = function(event) {
        if (event.target == customMessageBox) {
            customMessageBox.classList.remove('show');
        }
    };
}

// Function for auto-tabbing and backspace navigation in code inputs
document.addEventListener('DOMContentLoaded', () => {
    const verificationBoxes = document.querySelector('.verification-boxes');
    if (verificationBoxes) {
        const inputs = Array.from(verificationBoxes.querySelectorAll('input[type="tel"]'));

        inputs.forEach((input, index) => {
            input.addEventListener('input', (e) => {
                // Move to next input if current one is filled
                if (e.target.value.length === e.target.maxLength) {
                    if (index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                }
            });

            input.addEventListener('keydown', (e) => {
                // Move to previous input on Backspace if current one is empty
                if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                    inputs[index - 1].focus();
                }
            });
        });
    }
});

// Main function to submit verification code via fetch API
function submitVerificationCode() {
    let inputs = document.querySelectorAll(".verification-boxes input");
    let code = Array.from(inputs).map(input => input.value).join("");

    console.log("Frontend DEBUG (verify.js): Attempting to submit code:", code);
    console.log("Frontend DEBUG (verify.js): Sending payload:", JSON.stringify({ code: code }));

    fetch('/verify-code', { // This is the API endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: code })
    })
    .then(res => {
        console.log("Frontend DEBUG (verify.js): Received response status:", res.status);
        // Ensure to parse JSON even if response is not 'ok' to get error messages
        return res.json();
    })
    .then(data => {
        console.log("Frontend DEBUG (verify.js): Received response data:", data);
        if (data.success) {
            console.log("Code verification successful!");
            alert(data.message || "Verification successful!"); // Use browser alert
            // Redirect based on the 'type' of verification (registration vs. password reset)
            if (data.type === 'registration') {
                window.location.href = "/login"; // Redirect to login after successful registration
            } else if (data.type === 'reset_password') {
                window.location.href = "/reset-password"; // Redirect to password reset page
            }
        } else {
            console.error("Code verification failed. Message:", data.message || "Unknown error.");
            alert(data.message || "Incorrect verification code. Please try again."); // Use browser alert
            // Clear inputs and refocus on the first one for retry
            inputs.forEach(input => input.value = '');
            inputs[0].focus();
        }
    })
    .catch(error => {
        console.error("Frontend DEBUG (verify.js): Error during code verification fetch:", error);
        alert("An unexpected error occurred during verification. Please try again later."); // Use browser alert
    });
}

document.querySelectorAll('.verification-boxes input').forEach(input => {
  input.addEventListener('input', function() {
    this.value = this.value.replace(/[^0-9]/g, '').slice(0, 1);
  });
  input.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      // Clicks the submit button if Enter is pressed
      document.querySelector('.Btn').click();
    }
  });
});
