// search-results.js — renders the search results <ul> from the API
console.log('search-results.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('search-result-list');
  if (!listEl) return;

  // Build the exact API URL and carry over the page's ?q=...
  function currentApiUrl() {
    const url = new URL('/api/atl-places', window.location.origin);
    const qs = window.location.search;
    url.search = qs.startsWith('?') ? qs.slice(1) : qs;
    return url.toString();
  }

  // Helpers
  const parseNumber = (v) => {
    if (v == null) return null;
    const n = parseFloat(String(v).trim().replace(/[^\d.+-]/g, ''));
    return Number.isFinite(n) ? n : null;
  };

  const buildImageUrl = (img) => {
    if (!img) return '/static/images/placeholder.png';
    const s = String(img).replace(/^\/+/, '');              // strip leading slashes
    return s.startsWith('static/') ? `/${s}` : `/static/${s}`;
  };

  const titleCase = (s) =>
    String(s || '')
      .toLowerCase()
      .replace(/\b\w/g, (c) => c.toUpperCase());

  const STAR_PATH = 'M10 1.5l2.7 5.5 6.1.9-4.4 4.3 1 6.1L10 15.8 4.6 18.3l1-6.1L1.2 7.9l6.1-.9L10 1.5z';

  const starFull = () =>
    `<svg class="search-result-star full" viewBox="0 0 20 20" aria-hidden="true"><path d="${STAR_PATH}"/></svg>`;

  const starEmpty = () =>
    `<svg class="search-result-star empty" viewBox="0 0 20 20" aria-hidden="true"><path d="${STAR_PATH}"/></svg>`;

  const starHalf = (id) => `
    <svg class="search-result-star half" viewBox="0 0 20 20" aria-hidden="true">
      <defs>
        <clipPath id="half-clip-${id}">
          <rect x="0" y="0" width="10" height="20"></rect>
        </clipPath>
      </defs>
      <path class="star-empty" d="${STAR_PATH}" fill="#e0e0e0"/>
      <path class="star-fill"  d="${STAR_PATH}" fill="#ffb400" clip-path="url(#half-clip-${id})"/>
    </svg>`;

  // Fetch and render
  fetch(currentApiUrl(), { headers: { 'Accept': 'application/json' } })
    .then((res) => {
      if (!res.ok) throw new Error(`API ${res.status}`);
      return res.json();
    })
    .then((raw) => {
      const places = (raw || []).map((p) => {
        const rating = parseNumber(p.rating) ?? 0;
        return {
          id: p.atl_place_id,
          slug: p.slug || `place-${p.atl_place_id || Math.random().toString(36).slice(2)}`,
          title: p.title || '',
          img: buildImageUrl(p.img),
          rating,
          reviewCount: parseNumber(p.review_count) || 0,
          categories: Array.isArray(p.categories)
            ? p.categories
            : String(p.categories || '').split(','),
          isVerified: !!p.is_atl_verified,
          openStatus: p.open_status || '',
          openNow: !!p.open_now_status,
          reviewLink: p.review_link || null,
        };
      });

      // Build the entire list HTML (kept very close to your Jinja structure)
      let html = '';
      for (const p of places) {
        const full = Math.floor(p.rating);
        const hasHalf = (p.rating - full) >= 0.5 ? 1 : 0;
        const empty = Math.max(0, 5 - full - hasHalf);

        let stars = '';
        for (let i = 0; i < full; i++) stars += starFull();
        if (hasHalf) stars += starHalf(p.id || p.slug);
        for (let i = 0; i < empty; i++) stars += starEmpty();

        const cats = p.categories
          .map((c) => titleCase(String(c).trim()))
          .filter(Boolean)
          .join(' • ');

        html += `
<li class="search-item">
  <img class="search-result-thumb" src="${p.img}" alt="${escapeHtml(p.title)}" />
  <div class="search-result-info">
    <div class="search-result-name">${escapeHtml(p.title)}</div>
    <div class="search-result-rating" aria-label="Rating" id="${escapeAttr(p.slug)}-rating">
      <div class="search-result-rating-label">${p.rating.toFixed(1)}</div>
      <span class="search-result-stars" aria-label="${p.rating.toFixed(1)} out of 5 stars">
        ${stars}
      </span>
      <span class="search-result-review-count" id="${escapeAttr(p.slug)}-reviews">
        ${p.reviewCount.toLocaleString()}
      </span>
    </div>
    <div class="search-result-category">${escapeHtml(cats)}</div>
    ${p.isVerified ? `<p class="vetted-badge">(Verified by ATL Locals)</p>` : ``}
  </div>

  <div class="search-result-status">
    <div class="status-row">
      <span class="status-label">Open Status:</span>
      <span class="status-pill" data-status="${escapeAttr(p.openStatus)}">
        ${escapeHtml(p.openStatus)}
      </span>
    </div>
    <div class="status-row">
      <span class="status-label">Open Now:</span>
      <span class="status-pill" data-open-now="${p.openNow ? 'True' : 'False'}">
        ${p.openNow ? 'True' : 'False'}
      </span>
    </div>
  </div>

  ${p.reviewLink ? `
    <a href="${escapeAttr(p.reviewLink)}" class="btn read-more" target="_blank" rel="noopener noreferrer">
      Read Full Review
    </a>` : ``}
</li>`;
      }

      listEl.innerHTML = html || '';
    })
    .catch((err) => {
      console.error('Failed to load results:', err);
      listEl.innerHTML = ''; // keep it empty on error
    });

  // Basic HTML escaping helpers to keep things safe in template literals
  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (m) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[m]));
  }
  function escapeAttr(str) { return escapeHtml(str).replace(/\s+/g, '-'); }
});
