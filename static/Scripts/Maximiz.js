window.addEventListener("DOMContentLoaded", () => {
// if we're embedded in an iframe, hide our own maximize button
if (window.self !== window.top) {
    document.querySelector(".fs-icon").style.display = "none";
}
});