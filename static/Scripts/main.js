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

function toggleFullscreen() {
  const iframe = document.getElementById("game-preview");
  if (!document.fullscreenElement) {
    if (iframe.requestFullscreen) iframe.requestFullscreen();
    else if (iframe.webkitRequestFullscreen) iframe.webkitRequestFullscreen();
    else if (iframe.msRequestFullscreen) iframe.msRequestFullscreen();

    iframe.src = "/game?fullscreen=true"; // reload iframe with fullscreen param
  } else {
    if (document.exitFullscreen) document.exitFullscreen();
    else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
    else if (document.msExitFullscreen) document.msExitFullscreen();

    iframe.src = "/game?fullscreen=false"; // reload iframe without fullscreen param
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