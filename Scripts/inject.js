function loadComponent(id, file) {
  fetch(file)
    .then(response => {
      if (!response.ok) throw new Error("Failed to load component");
      return response.text();
    })
    .then(data => {
      document.getElementById(id).innerHTML = data;
      console.log(`✅ Injected ${file} into #${id}`);

      // Run your hover logic NOW that the DOM is ready
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
    })
    .catch(error => {
      console.error("❌ Component load failed:", error);
    });
}
