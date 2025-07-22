// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("menu-toggle");
  const modal = document.getElementById("mobile-nav-modal");

  if (toggleButton && modal) {
    toggleButton.addEventListener("click", () => {
      modal.classList.toggle("active");
    });
  }
});
