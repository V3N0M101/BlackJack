// static/Scripts/verify.js
// Function to show the custom message box
function showCustomMessageBox(message) {
    const msgBoxContainer = document.getElementById('msgBoxContainer');
    const msgText = document.querySelector('.msg-text');
    const okBtn = document.querySelector('.ok-btn');

    if (!msgBoxContainer || !msgText || !okBtn) {
        console.error("Message box elements not found! Message was: ", message);
        return;
    }

    msgText.textContent = message;
    okBtn.textContent = "OK";
    showMessageBox(); // Use the global showMessageBox function from display_box.html
}

// Function for auto-tabbing and backspace navigation in code inputs
document.addEventListener('DOMContentLoaded', () => {
    const verificationBoxes = document.querySelector('.verification-boxes');
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
            input.addEventListener('input', (e) => {
                // Handle regular input
                e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 1);
                if (e.target.value.length === e.target.maxLength && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            });

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

    // Show code section if verify=true in URL
    if (window.location.search.includes("verify=true")) {
        const emailSection = document.getElementById("email-section");
        const codeSection = document.getElementById("code-section");
        if (emailSection) emailSection.style.display = "none";
        if (codeSection) {
            codeSection.style.display = "block";
            const firstCodeInput = codeSection.querySelector('input[type="tel"]');
            if (firstCodeInput) firstCodeInput.focus();
        }
    }
});

// Auto-advance to next input and handle backspace
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.verification-boxes').addEventListener('keyup', function(e) {
        const target = e.target;
        const key = e.key;

        if (key === 'Backspace' || key === 'Delete') {
            if (target.value === '') {
                const prev = target.previousElementSibling;
                if (prev) {
                    prev.focus();
                }
            }
        } else if (target.value.length === target.maxLength) {
            const next = target.nextElementSibling;
            if (next) {
                next.focus();
            }
        }
    });
});

function submitVerificationCode() {
    const inputs = document.querySelectorAll('.verification-boxes input');
    const code = Array.from(inputs).map(input => input.value).join('');
    
    if (code.length !== 6 || !/^\d+$/.test(code)) {
        const msgText = document.querySelector('.msg-text');
        const okBtn = document.querySelector('.ok-btn');
        msgText.textContent = "Please enter a valid 6-digit code";
        okBtn.textContent = "OK";
        okBtn.onclick = hideMessageBox;
        showMessageBox();
        return;
    }

    fetch('/verify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code })
    })
    .then(response => response.json())
    .then(data => {
        const msgText = document.querySelector('.msg-text');
        const okBtn = document.querySelector('.ok-btn');
        
        if (data.success) {
            msgText.textContent = data.message || "Verification successful!";
            okBtn.textContent = "OK";
            okBtn.onclick = function() {
                hideMessageBox();
                window.location.href = data.redirect_url || '/login';
            };
        } else {
            msgText.textContent = "Wrong verification code entered";
            okBtn.textContent = "OK";
            okBtn.onclick = function() {
                hideMessageBox();
                // Clear inputs and focus on first one
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