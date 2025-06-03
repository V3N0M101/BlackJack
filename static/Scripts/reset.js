function submitPasswordReset() {
    const form = document.getElementById('reset-form');
    const formData = new FormData(form);
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (newPassword !== confirmPassword) {
      const msgText = document.querySelector('.msg-text');
      const okBtn = document.querySelector('.ok-btn');
      msgText.textContent = "Passwords do not match";
      okBtn.textContent = "OK";
      okBtn.onclick = hideMessageBox;
      showMessageBox();
      return;
    }

    fetch('/reset-password', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      const msgText = document.querySelector('.msg-text');
      const okBtn = document.querySelector('.ok-btn');
      
      if (data.success) {
        msgText.textContent = "Your password has been reset";
        okBtn.textContent = "OK";
        okBtn.onclick = function() {
          hideMessageBox();
          window.location.href = "/login";
        };
      } else {
        msgText.textContent = data.message || "An error occurred";
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

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) window.location.reload();
  });