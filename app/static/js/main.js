console.log('main.js loaded for /home route');

// Toggle mobile nav modal
document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const navModal = document.getElementById("nav-modal");

  if (menuToggle && navModal) {
    menuToggle.addEventListener("click", () => {
      navModal.style.display = navModal.style.display === "block" ? "none" : "block";
    });
  }
});
