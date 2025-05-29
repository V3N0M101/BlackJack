function updateFSButton() {
const isIframe = window.self !== window.top;
const fsBtn = document.getElementById('fsBtn');
const fsImg = document.getElementById('fsImg');

if (isIframe) {
    fsImg.src = '../Images/Icons/maxx.png'; // Maximize icon
    fsBtn.title = "Enter Fullscreen";
    fsBtn.onclick = function() {
    window.open('game.html', '_self');
    }
} else {
    fsImg.src = '../Images/Icons/minn.png'; // Minimize icon
    fsBtn.title = "Minimize and Return";
    fsBtn.onclick = function() {
    window.open('main.html', '_self');
    }
}
}
updateFSButton();
window.addEventListener('DOMContentLoaded', updateFSButton);

