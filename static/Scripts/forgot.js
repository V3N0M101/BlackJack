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
    const verificationBoxes = document.querySelector('#code-section .verification-boxes'); // Target code-section specifically
    if (verificationBoxes) {
        const inputs = Array.from(verificationBoxes.querySelectorAll('input[type="tel"]'));

        inputs.forEach((input, index) => {
            // Event listener for 'input' (when value changes, e.g., after typing a digit)
            input.addEventListener('input', (e) => {
                // Ensure only one digit is in the box and it's a number
                e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 1);

                // Move to next input if current one is filled
                if (e.target.value.length === e.target.maxLength) {
                    if (index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                }
            });

            // Event listener for 'keydown' (for Backspace and Arrow keys)
            input.addEventListener('keydown', (e) => {
                // Move to previous input on Backspace if current one is empty
                if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                    e.preventDefault(); // Prevent default backspace behavior (going back in history)
                    inputs[index - 1].focus();
                    // Optionally clear the previous input as well if you want to delete
                    // inputs[index - 1].value = '';
                }

                // Arrow Right navigation
                if (e.key === 'ArrowRight' && index < inputs.length - 1) {
                    e.preventDefault(); // Prevent default browser scroll
                    inputs[index + 1].focus();
                }

                // Arrow Left navigation
                if (e.key === 'ArrowLeft' && index > 0) {
                    e.preventDefault(); // Prevent default browser scroll
                    inputs[index - 1].focus();
                }

                // Submit on Enter key press
                if (e.key === 'Enter') {
                    e.preventDefault(); // Prevent default form submission
                    // Trigger the submitVerificationCode function
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
    alert(message); // Or your custom modal logic
}
