// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  // Toggle mobile nav
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

  // Assign STATIC_URL if defined in template
  const staticBaseUrl = typeof STATIC_URL !== 'undefined' ? STATIC_URL : '/static/';

  // Populate Latest News section
  const newsSection = document.getElementById("news-container");

  if (newsSection && typeof newsData !== 'undefined' && Array.isArray(newsData)) {
    newsSection.innerHTML = ""; // Clear any existing placeholder

    newsData.forEach(item => {
      const imageSrc = staticBaseUrl + "images/" + item.image;

      const newsCard = document.createElement("div");
      newsCard.className = "news-card";
      newsCard.innerHTML = `
        <div class="explore-card">
          <div class="explore-image">
            <img src="${imageSrc}" alt="${item.title}">
          </div>
          <div class="explore-content">
            <h3>${item.title}</h3>
            <p>${item.summary}</p>
          </div>
        </div>`;
      newsSection.appendChild(newsCard);
    });
  }

  // Populate Weather Data section
  const weatherContainer = document.getElementById("weather-container");

  if (weatherContainer && typeof weatherData === 'object') {
    weatherContainer.innerHTML = `
      <div class="weather-card">
        <img src="${weatherData.icon}" alt="${weatherData.condition}" class="weather-icon" />
        <div class="weather-details">
          <h3>${weatherData.temperature}</h3>
          <p>${weatherData.condition}</p>
          <small>${weatherData.location}</small>
        </div>
      </div>
    `;
  }

  console.log("News Data:", newsData);
  console.log("Weather Data:", weatherData);
});
