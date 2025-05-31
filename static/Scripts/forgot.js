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
            input.addEventListener('input', (e) => {
                if (e.target.value.length === e.target.maxLength) {
                    if (index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                }
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                    inputs[index - 1].focus();
                }
            });
        });
    }
});

function submitVerificationCode() {
    let inputs = document.querySelectorAll("#code-section .verification-boxes input"); // Target code-section specifically
    let code = Array.from(inputs).map(input => input.value).join("");

    console.log("Frontend DEBUG (forgot.js): Attempting to submit code:", code);
    console.log("Frontend DEBUG (forgot.js): Sending payload:", JSON.stringify({ code: code }));

    fetch('/verify-code', { // This is the API endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: code })
    })
    .then(res => {
        console.log("Frontend DEBUG (forgot.js): Received response status:", res.status);
        return res.json();
    })
    .then(data => {
        console.log("Frontend DEBUG (forgot.js): Received response data:", data);
        if (data.success) {
            console.log("Code verification successful for password reset!");
            alert(data.message || "Verification successful! Redirecting to password reset page..."); // Use browser alert
            window.location.href = "/reset-password"; // Redirect to password reset page
        } else {
            console.error("Code verification failed. Message:", data.message || "Unknown error.");
            alert(data.message || "Incorrect verification code. Please try again."); // Use browser alert
            // Clear inputs and refocus on the first one for retry
            inputs.forEach(input => input.value = '');
            inputs[0].focus();
        }
    })
    .catch(error => {
        console.error("Frontend DEBUG (forgot.js): Error during code verification fetch:", error);
        alert("An unexpected error occurred during verification. Please try again later."); // Use browser alert
    });
}


