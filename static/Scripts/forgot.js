const inputs = document.querySelectorAll('.verification-boxes input');

inputs.forEach((input, index) => {
input.addEventListener('keydown', (e) => {
    if (e.key === 'Backspace' && input.value === '' && index > 0) {
    inputs[index - 1].focus();
    }

    if (e.key >= '0' && e.key <= '9') {
    input.value = ''; // Clear existing value before typing
    setTimeout(() => {
        if (index < inputs.length - 1) {
        inputs[index + 1].focus();
        }
    }, 10);
    }

    if (e.key === 'ArrowRight' && index < inputs.length - 1) {
    inputs[index + 1].focus();
    }

    if (e.key === 'ArrowLeft' && index > 0) {
    inputs[index - 1].focus();
    }
});
});


// Only allow 0-9 in each box
document.addEventListener('DOMContentLoaded', () => {
    const verificationBoxes = document.querySelector('#code-section .verification-boxes');
    if (verificationBoxes) {
        const inputs = Array.from(verificationBoxes.querySelectorAll('input[type="tel"]'));

        // Handle paste event on any input
        inputs.forEach(input => {
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').replace(/[^0-9]/g, '').slice(0, 6);
                
                // Distribute the pasted numbers across the inputs
                for (let i = 0; i < inputs.length; i++) {
                    if (i < pastedData.length) {
                        inputs[i].value = pastedData[i];
                    }
                }

                // Focus the next empty input or the last input if all filled
                const nextEmptyIndex = inputs.findIndex(input => !input.value);
                if (nextEmptyIndex !== -1) {
                    inputs[nextEmptyIndex].focus();
                } else {
                    inputs[inputs.length - 1].focus();
                }
            });
        });

        inputs.forEach((input, index) => {
            // Handle regular input
            input.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 1);
                if (e.target.value.length === e.target.maxLength && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            });

            // Handle keyboard navigation
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                    e.preventDefault();
                    inputs[index - 1].focus();
                }
                if (e.key === 'ArrowRight' && index < inputs.length - 1) {
                    e.preventDefault();
                    inputs[index + 1].focus();
                }
                if (e.key === 'ArrowLeft' && index > 0) {
                    e.preventDefault();
                    inputs[index - 1].focus();
                }
                if (e.key === 'Enter') {
                    e.preventDefault();
                    submitVerificationCode();
                }
            });
        });
    }

    // Initial display logic based on URL parameter
    if (window.location.search.includes("verify=true")) {
        const emailSection = document.getElementById("email-section");
        const codeSection = document.getElementById("code-section");
        if (emailSection) emailSection.style.display = "none";
        if (codeSection) {
            codeSection.style.display = "block";
            // Set focus to the first input in the code section if it's displayed
            const firstCodeInput = codeSection.querySelector('input[type="tel"]');
            if (firstCodeInput) firstCodeInput.focus();
        }
    }
});


// Main function to submit verification code via fetch API
function submitVerificationCode() {
    let inputs = document.querySelectorAll("#code-section .verification-boxes input"); // Target code-section specifically
    let code = Array.from(inputs).map(input => input.value).join("");

    console.log("Frontend DEBUG (forgot.js): Attempting to submit code:", code);
    console.log("Frontend DEBUG (forgot.js): Sending payload to /api/verify-code:", JSON.stringify({ code: code }));

    fetch('/api/verify-code', { // This is the API endpoint for password reset verification
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: code })
    })
    .then(res => {
        console.log("Frontend DEBUG (forgot.js): Received response status:", res.status);
        // Ensure to parse JSON even if response is not 'ok' to get error messages
        return res.json();
    })
    .then(data => {
        console.log("Frontend DEBUG (forgot.js): Received response data:", data);
        if (data.success) {
            console.log("Code verification successful for password reset!");
            showCustomMessageBox(data.message || "Verification successful! Redirecting to password reset page...");

            // The Flask /api/verify-code route should return redirect_url
            if (data.type === 'reset_password' && data.redirect_url) {
                window.location.href = data.redirect_url; // Redirect to /reset-password
            } else {
                // Fallback if type or redirect_url is missing, but success is true
                window.location.href = "/reset-password"; // Default redirect for successful reset verification
            }
        } else {
            console.error("Code verification failed. Message:", data.message || "Unknown error.");
            showCustomMessageBox(data.message || "Incorrect verification code. Please try again.");
            // Clear inputs and refocus on the first one for retry
            inputs.forEach(input => input.value = '');
            inputs[0].focus();
        }
    })
    .catch(error => {
        console.error("Frontend DEBUG (forgot.js): Error during code verification fetch:", error);
        showCustomMessageBox("An unexpected error occurred during verification. Please try again later.");
    });
}

function showCustomMessageBox(message, type = "info") {
    console.log(`CustomMessage: [${type}] ${message}`); // Replaced alert with console.log
    // If you have a custom modal element, you would activate it here instead.
}

// Function to submit email for reset code
function submitEmailForm() {
    const form = document.getElementById('email-form');
    const formData = new FormData(form);

    fetch('/send-reset-code', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const msgText = document.querySelector('.msg-text');
        const okBtn = document.querySelector('.ok-btn');
        
        if (data.success) {
            msgText.textContent = "Password reset link sent";
            okBtn.textContent = "OK";
            okBtn.onclick = function() {
                hideMessageBox();
                // Show code section and hide email section
                document.getElementById('email-section').style.display = 'none';
                document.getElementById('code-section').style.display = 'block';
                // Focus on first code input
                document.querySelector('.verification-boxes input').focus();
            };
        } else {
            msgText.textContent = data.message || "Email not found";
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
}

// Function to submit verification code
function submitVerificationCode() {
    const inputs = document.querySelectorAll("#code-section .verification-boxes input");
    const code = Array.from(inputs).map(input => input.value).join("");

    fetch('/api/verify-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: code })
    })
    .then(response => response.json())
    .then(data => {
        const msgText = document.querySelector('.msg-text');
        const okBtn = document.querySelector('.ok-btn');
        
        if (data.success) {
            msgText.textContent = "Code verified successfully!";
            okBtn.textContent = "OK";
            okBtn.onclick = function() {
                hideMessageBox();
                window.location.href = "/reset-password";
            };
        } else {
            msgText.textContent = "Wrong verification code entered";
            okBtn.textContent = "OK";
            okBtn.onclick = function() {
                hideMessageBox();
                // Clear inputs and refocus on first one
                inputs.forEach(input => input.value = '');
                inputs[0].focus();
            };
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
}
