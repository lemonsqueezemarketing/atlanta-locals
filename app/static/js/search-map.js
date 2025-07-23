console.log('search-map.js loaded for /search-map route');

document.addEventListener('DOMContentLoaded', function () {
  // Init Leaflet Map
  const map = L.map('map').setView([33.749, -84.388], 12); // Atlanta center

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);

  // Search input alert handlers
  function bindSearchHandler(inputSelector, buttonSelector) {
    const input = document.querySelector(inputSelector);
    const button = document.querySelector(buttonSelector);

    if (input && button) {
      button.addEventListener('click', () => {
        const query = input.value.trim();
        if (query) alert(`You searched: ${query}`);
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const query = input.value.trim();
          if (query) alert(`You searched: ${query}`);
        }
      });
    }
  }

  // Top bar
  bindSearchHandler('.search-map-input', '.direction-icon');

  // Filter search
  bindSearchHandler('.map-search-input', '.map-search-btn');
});
