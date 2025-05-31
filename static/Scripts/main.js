const navButtons = document.querySelectorAll('.nav-bar .nav-link');
const hoverBack = document.querySelector('.hover-back');

navButtons.forEach(btn => {
  btn.addEventListener('mouseenter', () => {
    const rect = btn.getBoundingClientRect();
    const navRect = btn.parentElement.getBoundingClientRect();
    hoverBack.style.left = (rect.left - navRect.left) + "px";
    hoverBack.style.width = rect.width + "px";
  });
});

document.querySelector('.nav-bar').addEventListener('mouseleave', () => {
  hoverBack.style.width = "0";
});

document.addEventListener('DOMContentLoaded', () => {
    // Other main.js functionalities if any
});

function toggleFullscreen() {
    const iframe = document.getElementById('game-preview');

    if (iframe && iframe.contentWindow) {
        const iframeDocument = iframe.contentWindow.document;
        const bodyElement = iframeDocument.documentElement; // Or iframeDocument.body if preferred

        // Check if currently in fullscreen (of the iframe's content)
        // Note: document.fullscreenElement refers to the *main* document
        // You need to check the iframe's document for its fullscreen state
        const isFullscreen = iframeDocument.fullscreenElement ||
                             iframeDocument.mozFullScreenElement ||
                             iframeDocument.webkitFullscreenElement ||
                             iframeDocument.msFullscreenElement;

        if (!isFullscreen) {
            // Request fullscreen for the iframe's content
            if (bodyElement.requestFullscreen) {
                bodyElement.requestFullscreen();
            } else if (bodyElement.mozRequestFullScreen) { /* Firefox */
                bodyElement.mozRequestFullScreen();
            } else if (bodyElement.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
                bodyElement.webkitRequestFullscreen();
            } else if (bodyElement.msRequestFullscreen) { /* IE/Edge */
                bodyElement.msRequestFullscreen();
            }
            // Optional: Add a class to main.html's body if needed for styling outside the iframe
            document.body.classList.add('iframe-fullscreen-active');
        } else {
            // Exit fullscreen for the iframe's content
            if (iframeDocument.exitFullscreen) {
                iframeDocument.exitFullscreen();
            } else if (iframeDocument.mozCancelFullScreen) {
                iframeDocument.mozCancelFullScreen();
            } else if (iframeDocument.webkitExitFullscreen) {
                iframeDocument.webkitExitFullscreen();
            } else if (iframeDocument.msExitFullscreen) {
                iframeDocument.msExitFullscreen();
            }
            // Optional: Remove class from main.html's body
            document.body.classList.remove('iframe-fullscreen-active');
        }
    } else {
        console.error("Iframe 'game-preview' or its contentWindow not found.");
    }
}

document.addEventListener("fullscreenchange", () => {
  const iframe = document.getElementById("game-preview");
  if (!document.fullscreenElement) {
    iframe.src = "/game?fullscreen=false";
  } else {
    iframe.src = "/game?fullscreen=true";
  }
});