console.log('search-map.js loaded for /search-map route');

document.addEventListener('DOMContentLoaded', function () {
  // Init Leaflet Map (Atlanta center)
  const map = L.map('map').setView([33.749, -84.388], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);

  // ---------- Emoji markers (no external image dependencies) ----------
  function emojiIcon(emoji) {
    return L.divIcon({
      html: `<div class="emoji-pin">${emoji}</div>`,
      className: 'emoji-icon', // keep Leaflet classes clean
      iconSize: [28, 28],
      iconAnchor: [14, 28],
      popupAnchor: [0, -28],
    });
  }

  const iconMap = {
    healthy: emojiIcon('🥗'),
    icecream: emojiIcon('🍦'),
    sake: emojiIcon('🍶'),
    coffee: emojiIcon('☕'),
    tea: emojiIcon('🫖'),
    barber: emojiIcon('💈'),
    juice: emojiIcon('🧃'),
    default: emojiIcon('📍'),
  };

  // Slight jitter to separate markers located in the same plaza
  function jitter([lat, lng], dx = 0.00025, dy = 0.00018) {
    return [lat + (Math.random() - 0.5) * dy, lng + (Math.random() - 0.5) * dx];
  }

  // ---------- Mike's visited places ----------
  const places = [
    {
      name: "Salata",
      category: "healthy",
      address: "650 Ponce de Leon Ave NE, Atlanta, GA 30308",
      lat: 33.775006, lng: -84.365838,
      rating: 4.0, reviews: 238, verified: true
    },
    {
      name: "Gusto! Healthy Bowls & Wraps (West End)",
      category: "healthy",
      address: "1020 White St SW, Atlanta, GA 30310",
      lat: 33.7368, lng: -84.4216,
      rating: 4.5, reviews: 75, verified: true, plaza: "west-end"
    },
    {
      name: "Honeysuckle Gelato (West End)",
      category: "icecream",
      address: "1020 White St SW, Atlanta, GA 30310",
      lat: 33.7368, lng: -84.4216,
      rating: 4.6, reviews: 30, verified: true, plaza: "west-end"
    },
    {
      name: "Sakera Sake Bar & Bottles (West End)",
      category: "sake",
      address: "1020 White St SW, Atlanta, GA 30310",
      lat: 33.7368, lng: -84.4216,
      rating: 4.9, reviews: 50, verified: true, plaza: "west-end"
    },
    {
      name: "Starbucks (Moreland Ave NE)",
      category: "coffee",
      address: "406 Moreland Ave NE, Atlanta, GA 30307",
      lat: 33.7599, lng: -84.3494,
      rating: 4.2, reviews: 735, verified: true
    },
    {
      name: "Tea’z Social",
      category: "tea",
      address: "337 Moreland Ave NE, Atlanta, GA 30307",
      lat: 33.7608, lng: -84.3499,
      rating: 4.9, reviews: 74, verified: true, status: "Temporarily Closed"
    },
    {
      name: "Mr. Everything Cafe (MLK)",
      category: "healthy",
      address: "882 Martin Luther King Jr Dr SW, Atlanta, GA 30314",
      lat: 33.7537, lng: -84.4163,
      rating: 4.3, reviews: 1378, verified: true
    },
    {
      name: "Busy Bee Cafe",
      category: "healthy",
      address: "810 Martin Luther King Jr Dr SW, Atlanta, GA 30314",
      lat: 33.7489, lng: -84.4141,
      rating: 4.0, reviews: 3380, verified: true
    },
    {
      name: "King Jai the Barber (Groomsmen Gentleman’s Refinery)",
      category: "barber",
      address: "1107 Euclid Ave NE, Atlanta, GA 30307",
      lat: 33.7656, lng: -84.3491,
      rating: 4.8, reviews: 81, verified: true
    },
    {
      name: "Liquid Wizdom",
      category: "juice",
      address: "1133 Euclid Ave NE, Atlanta, GA 30307",
      lat: 33.7662, lng: -84.3477,
      rating: 4.8, reviews: 24, verified: true
    },
  ];

  // ---------- Plot markers with popups ----------
  places.forEach(p => {
    let [lat, lng] = [p.lat, p.lng];
    if (p.plaza === "west-end") {
      [lat, lng] = jitter([lat, lng]); // avoid exact overlap in that plaza
    }

    const icon = iconMap[p.category] || iconMap.default;
    const badge = p.verified
      ? '<span class="map-badge">Verified ATL Local</span>'
      : '';
    const closed = p.status ? `<div class="map-closed">${p.status}</div>` : '';
    const popup = `
      <div class="popup">
        <div class="popup-title">${p.name} ${badge}</div>
        <div class="popup-addr">${p.address}</div>
        <div class="popup-meta">⭐ ${p.rating} • ${Number(p.reviews).toLocaleString()} reviews</div>
        ${closed}
      </div>
    `;

    L.marker([lat, lng], { icon }).addTo(map).bindPopup(popup);
  });

  // ---------- Existing search handlers (unchanged) ----------
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

  // Top menu search
  bindSearchHandler('#top-search-input', '#top-search-btn');

});
