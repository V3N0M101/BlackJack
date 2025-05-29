window.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".page-transition");
  if (page) page.classList.add("loaded");

  document.querySelectorAll('a').forEach(link => {
    const href = link.getAttribute("href");
    if (
      href &&
      !href.startsWith("#") &&
      !link.hasAttribute("target") &&
      !link.getAttribute("href").startsWith("javascript:")
    ) {
      link.addEventListener("click", e => {
        e.preventDefault();

        const overlay = document.querySelector(".overlay-transition");
        if (overlay) overlay.classList.add("active");
        if (page) page.classList.add("exiting");

        setTimeout(() => {
          window.location.href = href;
        }, 300); // Match CSS duration
      });
    }
  });
});

function jumpAndRedirect(url) {
  const page = document.querySelector('.page-transition');
  if (page) {
    page.classList.add('jumping');
    setTimeout(() => {
      window.location.href = url;
    }, 350); // match animation duration (0.35s)
  } else {
    window.location.href = url;
  }
}


