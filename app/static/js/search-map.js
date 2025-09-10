// search-map.js
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
  let dupCount = {};
  function jitterIfDuplicate(lat, lng, dx = 0.00025, dy = 0.00018) {
    const key = `${lat.toFixed(6)},${lng.toFixed(6)}`;
    dupCount[key] = (dupCount[key] || 0) + 1;
    if (dupCount[key] > 1) {
      return [lat + (Math.random() - 0.5) * dy, lng + (Math.random() - 0.5) * dx];
    }
    return [lat, lng];
  }

  // Layer for (re)plotting
  const markersLayer = L.layerGroup().addTo(map);

  // ---------- API helpers ----------
  async function loadPlaces() {
    // Initial load of *all* places, with fallback to injected window.ATL_PLACES
    try {
      const res = await fetch('/api/atl-places', { headers: { 'Accept': 'application/json' } });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      return Array.isArray(data) ? data : (data && data.places) ? data.places : [];
    } catch (e) {
      console.warn('Falling back to window.ATL_PLACES:', e);
      return Array.isArray(window.ATL_PLACES) ? window.ATL_PLACES : [];
    }
  }

  function urlForQuery(q) {
    return q ? `/api/search/places?q=${encodeURIComponent(q)}` : `/api/atl-places`;
  }

  async function fetchForQuery(q) {
    const res = await fetch(urlForQuery((q || '').trim()), { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    return Array.isArray(data) ? data : (data && data.places) ? data.places : [];
  }

  // ---------- Plotter (clears + redraws) ----------
  function plotPlaces(raw) {
    // reset duplicate-tracker for jitter each redraw
    dupCount = {};
    markersLayer.clearLayers();

    (raw || []).forEach(p => {
      const lat = parseNumber(p.lat);
      const lng = parseNumber(p.lng);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

      const key = pickIconKey(p.categories);
      const icon = iconMap[key] || iconMap.default;

      const name   = p.title || p.name || '';
      const badge  = (p.is_atl_verified || p.verified) ? '<span class="map-badge">Verified ATL Local</span>' : '';
      const addr   = p.address ? `<div class="popup-addr">${p.address}</div>` : '';
      const rating = p.rating ?? '';
      const reviews = Number(p.review_count ?? p.reviews ?? 0).toLocaleString();
      const status = p.open_status ? `<div class="map-closed">${p.open_status}</div>` : '';

      const popup = `
        <div class="popup">
          <div class="popup-title">${name} ${badge}</div>
          ${addr}
          <div class="popup-meta">⭐ ${rating} • ${reviews} reviews</div>
          ${status}
        </div>
      `;

      const [jLat, jLng] = jitterIfDuplicate(lat, lng);
      L.marker([jLat, jLng], { icon }).addTo(markersLayer).bindPopup(popup);
    });

    if (markersLayer.getLayers().length) {
      map.fitBounds(markersLayer.getBounds(), { padding: [24, 24] });
    }
  }

  // ---------- Initial load (all places) ----------
  loadPlaces()
    .then(plotPlaces)
    .catch(err => console.error('Failed to load places:', err));

  // ---------- Search handlers (click + Enter) ----------
  async function reloadMapForQuery(q) {
    try {
      const places = await fetchForQuery(q);
      plotPlaces(places);
    } catch (err) {
      console.error('Search fetch failed:', err);
    }
  }

  function bindSearchHandler(inputSelector, buttonSelector) {
    const input = document.querySelector(inputSelector);
    const button = document.querySelector(buttonSelector);
    if (!input || !button) return;

    const run = () => {
      const query = input.value.trim();
      reloadMapForQuery(query);
    };

    button.addEventListener('click', (e) => {
      e.preventDefault();
      run();
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        run();
      }
    });
  }

  // Hook up your existing inputs (kept exactly as before)
  bindSearchHandler('.search-map-input', '.direction-icon'); // legacy hook (if present)
  bindSearchHandler('.map-search-input', '.map-search-btn'); // filter search row
  bindSearchHandler('#top-search-input', '#top-search-btn'); // top white bar
});
