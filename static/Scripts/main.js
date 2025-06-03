const navButtons = document.querySelectorAll('.nav-bar .nav-link');
const hoverBack = document.querySelector('.hover-back');

navButtons.forEach(btn => {
  btn.addEventListener('mouseenter', () => {
    if (!hoverBack) return; // Prevent errors if hoverBack is null
    const rect = btn.getBoundingClientRect();
    const navRect = btn.parentElement.getBoundingClientRect();
    hoverBack.style.left = (rect.left - navRect.left) + "px";
    hoverBack.style.width = rect.width + "px";
  });
});

const navBar = document.querySelector('.nav-bar');
if (navBar && hoverBack) {
  navBar.addEventListener('mouseleave', () => {
    hoverBack.style.width = "0";
  });
}

document.querySelector('.nav-bar').addEventListener('mouseleave', () => {
  if (hoverBack) hoverBack.style.width = "0";
});

document.addEventListener('DOMContentLoaded', () => {
    // Other main.js functionalities if any
});

function toggleFullscreen() {
    const iframe = document.getElementById('game-preview');

    // Only proceed if the user was logged in when main.html was rendered
    // and the iframe is currently showing the game (not the placeholder)
    if (typeof isLoggedIn !== 'undefined' && isLoggedIn && iframe && iframe.src.includes('/game')) {
        if (iframe.contentWindow) {
            const iframeDocument = iframe.contentWindow.document;
            const bodyElement = iframeDocument.documentElement;

            const isFullscreen = iframeDocument.fullscreenElement ||
                                 iframeDocument.mozFullScreenElement ||
                                 iframeDocument.webkitFullscreenElement ||
                                 iframeDocument.msFullscreenElement;

            if (!isFullscreen) {
                if (bodyElement.requestFullscreen) bodyElement.requestFullscreen();
                else if (bodyElement.mozRequestFullScreen) bodyElement.mozRequestFullScreen();
                else if (bodyElement.webkitRequestFullscreen) bodyElement.webkitRequestFullscreen();
                else if (bodyElement.msRequestFullscreen) bodyElement.msRequestFullscreen();
                document.body.classList.add('iframe-fullscreen-active');
            } else {
                if (iframeDocument.exitFullscreen) iframeDocument.exitFullscreen();
                else if (iframeDocument.mozCancelFullScreen) iframeDocument.mozCancelFullScreen();
                else if (iframeDocument.webkitExitFullscreen) iframeDocument.webkitExitFullscreen();
                else if (iframeDocument.msExitFullscreen) iframeDocument.msExitFullscreen();
                document.body.classList.remove('iframe-fullscreen-active');
            }
        } else {
            console.error("Iframe 'game-preview' contentWindow not found for fullscreen toggle.");
        }
    } else {
        console.log("Fullscreen toggle condition not met (not logged in, or iframe not showing game).");
        // If not logged in, main.html should have already set the correct iframe src.
        // No need to force it here as it might interfere with intended navigation (e.g., after logout).
    }
}

document.addEventListener("fullscreenchange", () => {
  const iframe = document.getElementById("game-preview");
  // This event fires when the main document's fullscreen state changes.
  // We only want to modify the iframe src if the user was initially logged in
  // AND the iframe is meant to be showing the game.
  if (typeof isLoggedIn !== 'undefined' && isLoggedIn && iframe && iframe.src.includes('/game')) {
    const isInFullscreen = !!document.fullscreenElement;
    if (isInFullscreen) {
      // If entering fullscreen and game src doesn't have ?fullscreen=true, add it.
      if (!iframe.src.includes("fullscreen=true")) {
        iframe.src = "/game?fullscreen=true";
      }
    } else {
      // If exiting fullscreen and game src has ?fullscreen=true, change to ?fullscreen=false.
      if (iframe.src.includes("fullscreen=true")) {
        iframe.src = "/game?fullscreen=false";
      }
    }
  }
  // If not logged in, or iframe isn't showing the game, do nothing here.
  // The template (main.html) is responsible for the initial src.
  // Post-logout navigation should reload main.html, which will then render the correct iframe content.
});