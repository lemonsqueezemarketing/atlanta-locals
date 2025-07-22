// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("menu-toggle");
  const modal = document.getElementById("mobile-nav-modal");
  const menuIcon = document.getElementById("menu-icon");
  const closeIcon = document.getElementById("close-icon");

  if (toggleButton && modal && menuIcon && closeIcon) {
    toggleButton.addEventListener("click", () => {
      modal.classList.toggle("active");

      const isActive = modal.classList.contains("active");
      menuIcon.style.display = isActive ? "none" : "inline";
      closeIcon.style.display = isActive ? "inline" : "none";
    });
  }
});
