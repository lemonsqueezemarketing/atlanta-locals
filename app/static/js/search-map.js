console.log('search-map.js loaded for /search-map route');

document.addEventListener('DOMContentLoaded', function () {
  const map = L.map('map').setView([33.749, -84.388], 12); // Atlanta center

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);
});
