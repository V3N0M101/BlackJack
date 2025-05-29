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

function submitVerificationCode() {
  const inputs = document.querySelectorAll(".verification-boxes input");
  let code = "";

  inputs.forEach(input => {
    code += input.value;
  });

  if (code.length !== 6 || !/^\d{6}$/.test(code)) {
    alert("Please enter a valid 6-digit numeric code.");
    return;
  }

  // Handle code submission
  alert("Verification code entered: " + code);
  // alert("Invalid Verification Code")
}

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






