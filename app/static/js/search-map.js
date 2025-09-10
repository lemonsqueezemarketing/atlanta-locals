console.log('search-map.js loaded for /search-map route');

document.addEventListener('DOMContentLoaded', function () {
  // ----- Leaflet Map (Atlanta center) -----
  const map = L.map('map').setView([33.749, -84.388], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);

  // ----- Emoji icons -----
  function emojiIcon(emoji) {
    return L.divIcon({
      html: `<div class="emoji-pin">${emoji}</div>`,
      className: 'emoji-icon',
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

  // ----- Helpers -----
  function pickIconKey(categories) {
    const cats = (categories || []).map(c => String(c).toLowerCase());
    if (cats.some(c => c.includes('barber'))) return 'barber';
    if (cats.some(c => c.includes('coffee'))) return 'coffee';
    if (cats.some(c => c.includes('tea'))) return 'tea';
    if (cats.some(c => c.includes('sake'))) return 'sake';
    if (cats.some(c => c.includes('ice cream'))) return 'icecream';
    if (cats.some(c => c.includes('juice'))) return 'juice';
    if (cats.some(c => c.includes('healthy') || c.includes('salad'))) return 'healthy';
    return 'default';
  }

  // Robust numeric parsing: handles whitespace, commas, stray chars
  function parseNumber(val) {
    if (val == null) return null;
    const cleaned = String(val).trim().replace(/[^\d.+-]/g, '');
    const num = parseFloat(cleaned);
    return Number.isFinite(num) ? num : null;
  }

  // Separate overlapping markers a bit if they share coords
  const dupCount = {};
  function jitterIfDuplicate(lat, lng, dx = 0.00025, dy = 0.00018) {
    const key = `${lat.toFixed(6)},${lng.toFixed(6)}`;
    dupCount[key] = (dupCount[key] || 0) + 1;
    if (dupCount[key] > 1) {
      return [lat + (Math.random() - 0.5) * dy, lng + (Math.random() - 0.5) * dx];
    }
    return [lat, lng];
  }

  // ----- Load from Flask API (fallback to window.ATL_PLACES if present) -----
  async function loadPlaces() {
    try {
      const res = await fetch('/api/atl-places', { headers: { 'Accept': 'application/json' } });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return await res.json();
    } catch (e) {
      console.warn('Falling back to window.ATL_PLACES:', e);
      return Array.isArray(window.ATL_PLACES) ? window.ATL_PLACES : [];
    }
  }

  // ----- Fetch → normalize → plot -----
  const markersLayer = L.layerGroup().addTo(map);

  loadPlaces()
    .then(raw => {
      const places = (raw || [])
        .map(p => {
          const lat = parseNumber(p.lat);
          const lng = parseNumber(p.lng);
          if (lat == null || lng == null) return null; // skip bad coords

          return {
            id: p.atl_place_id,
            name: p.title,
            categoryKey: pickIconKey(p.categories),
            address: p.address,
            lat, lng,
            rating: parseNumber(p.rating),
            reviews: parseNumber(p.review_count) || 0,
            verified: !!p.is_atl_verified,
            status: p.open_status,          // "open", "temporarily closed", etc.
            openNow: !!p.open_now_status
          };
        })
        .filter(Boolean);

      places.forEach(p => {
        const [lat, lng] = jitterIfDuplicate(p.lat, p.lng);
        const icon = iconMap[p.categoryKey] || iconMap.default;
        const badge = p.verified ? '<span class="map-badge">Verified ATL Local</span>' : '';
        const closed = p.status ? `<div class="map-closed">${p.status}</div>` : '';
        const addr = p.address ? `<div class="popup-addr">${p.address}</div>` : '';

        const popup = `
          <div class="popup">
            <div class="popup-title">${p.name} ${badge}</div>
            ${addr}
            <div class="popup-meta">⭐ ${p.rating ?? ''} • ${Number(p.reviews).toLocaleString()} reviews</div>
            ${closed}
          </div>
        `;

        L.marker([lat, lng], { icon }).addTo(markersLayer).bindPopup(popup);
      });

      if (places.length) {
        map.fitBounds(markersLayer.getBounds(), { padding: [24, 24] });
      }
    })
    .catch(err => {
      console.error('Failed to load places:', err);
    });

  // ----- Existing search handlers (still alerts for now) -----
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

  // Hook up your existing inputs
  bindSearchHandler('.search-map-input', '.direction-icon');
  bindSearchHandler('.map-search-input', '.map-search-btn');
  bindSearchHandler('#top-search-input', '#top-search-btn');
});
