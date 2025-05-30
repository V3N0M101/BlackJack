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


function submitVerificationCode() {
    let inputs = document.querySelectorAll(".verification-boxes input");
    let code = Array.from(inputs).map(input => input.value).join("");

    fetch('/verify-code', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ code: code })
    })
    .then(res => {
        if (res.ok) {
            // Verification success — redirect to reset page
            window.location.href = "/reset-password";
        } else {
            alert("Invalid code, please try again.");
        }
    });
}



