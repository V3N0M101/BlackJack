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
