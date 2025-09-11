// static/js/news.js
console.log('news.js loaded for /news route');

(() => {
  // --- helpers ---
  const $ = (sel, root = document) => root.querySelector(sel);

  function resolveImage(path) {
    if (!path) return '';
    if (/^https?:\/\//i.test(path)) return path;
    return `/static/${String(path).replace(/^\/+/, '')}`;
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Prefer new flat BlogContent fields; fall back to legacy nested
  function firstParagraph(post) {
    try {
      const c = post?.content;
      if (!c) return '';

      // ✅ FLAT (SQL) fields first
      if (typeof c.section_1_paragraph_1 === 'string' && c.section_1_paragraph_1.trim()) {
        return c.section_1_paragraph_1.trim();
      }
      const flatKeys = [
        'section_1_paragraph_2',
        'section_2_paragraph_1',
        'section_3_paragraph_1'
      ];
      for (const k of flatKeys) {
        if (typeof c[k] === 'string' && c[k].trim()) return c[k].trim();
      }

      // 🧯 Legacy nested (Mongo-style) fallback
      const inner = c?.content || c;
      const s1 = inner?.['section-1'] || inner?.section1 || inner?.section_1 || inner?.section || null;
      const p1 = s1?.['paragraph-1'] || s1?.paragraph1 || s1?.paragraph || null;
      if (typeof p1 === 'string' && p1.trim()) return p1.trim();
    } catch {}
    return '';
  }

  // Render the main story card
  function applyMainToDom(post) {
    if (!post) return;

    const imgEl   = document.querySelector('.main-story-image img');
    const titleEl = document.querySelector('[data-main-title]');
    const descEl  = document.querySelector('[data-main-desc]');
    const linkEl  = document.querySelector('[data-main-link]');

    const imgSrc = post.image_url || resolveImage(post.image || '');

    if (imgEl) {
      imgEl.src = imgSrc || '';
      imgEl.alt = post.title || 'Main story image';
    }
    if (titleEl) {
      titleEl.textContent = post.title || 'Untitled';
    }
    if (descEl) {
      const snippet = firstParagraph(post);
      descEl.textContent = snippet.length > 150 ? `${snippet.slice(0, 150)}…` : snippet;
    }
    if (linkEl) {
      linkEl.href = `/news/${post.slug ?? post.post_id ?? ''}`;
    }
  }

  // Render the Most Read list (top 7)
  function renderMostRead(items) {
    const ul = document.querySelector('[data-most-read-list]');
    if (!ul) return;

    const top = (Array.isArray(items) ? items : []).slice(0, 7);
    if (!top.length) {
      ul.innerHTML = `<li class="muted">No data yet.</li>`;
      return;
    }

    ul.innerHTML = top.map((item, i) => {
      const rank  = i + 1;
      const title = escapeHtml(item?.title || 'Untitled');
      const href  = `/news/${item?.slug ?? item?.post_id ?? ''}`;
      return `
        <li>
          <span class="most-read-rank">${rank}</span>
          <a class="most-read-link" href="${href}">${title}</a>
        </li>
      `;
    }).join('');
  }

  // Render the Latest News cards (top 3), matching the Jinja structure
  function renderLatestNews(items) {
    const container = document.querySelector('[data-latest-news-list]');
    if (!container) return;

    const top = (Array.isArray(items) ? items : []).slice(0, 3);
    if (!top.length) {
      container.innerHTML = `<div class="muted">No latest news available.</div>`;
      return;
    }

    container.innerHTML = top.map(item => {
      const title  = escapeHtml(item?.title || 'Untitled');
      const href   = `/news/${item?.slug ?? item?.post_id ?? ''}`;
      const imgSrc = item?.image_url || resolveImage(item?.image || '');

      const snippet = firstParagraph(item);
      const short   = snippet.length > 150 ? `${escapeHtml(snippet.slice(0, 150))}…` : escapeHtml(snippet);

      return `
        <article class="news-card">
          <img src="${imgSrc}" alt="${title}">
          <div class="news-content">
            <h3>${title}</h3>
            <p>${short}</p>
            <a href="${href}" class="read-more">Read More</a>
          </div>
        </article>
      `;
    }).join('');
  }

  // --- build URLs ---
  const params = new URLSearchParams();
  params.set('per_page', '10');
  params.set('include_content', 'true');

  const postsURL        = `/api/v1/news-posts?${params.toString()}`;
  const mainURL         = `/api/v1/news-main?active=1&include_content=true`;
  const mostReadNewsURL = `/api/v1/analytics/most-read/news`;
  const latestNewsURL   = `/api/v1/analytics/latest-news?include_content=true&per_page=3`;

  (async () => {
    try {
      const [postsRes, mainRes, mostReadRes, latestNewsRes] = await Promise.all([
        fetch(postsURL,        { headers: { 'Accept': 'application/json' } }),
        fetch(mainURL,         { headers: { 'Accept': 'application/json' } }),
        fetch(mostReadNewsURL, { headers: { 'Accept': 'application/json' } }),
        fetch(latestNewsURL,   { headers: { 'Accept': 'application/json' } })
      ]);

      // ----- Posts (for fallback) -----
      let posts = [];
      if (!postsRes.ok) {
        console.error('[news] posts fetch failed', postsRes.status, await postsRes.text());
      } else {
        const data = await postsRes.json();
        console.log('[news] posts payload:', data);
        posts = Array.isArray(data.items) ? data.items
              : (Array.isArray(data.news) ? data.news : []);
      }

      // ----- Main story -----
      let mainItem = null;
      if (!mainRes.ok) {
        console.error('[news] main fetch failed', mainRes.status, await mainRes.text());
      } else {
        const payload = await mainRes.json();
        const first = Array.isArray(payload?.items) ? payload.items[0] : null;
        if (first) {
          mainItem = first.post || null; // server returns { news_main: {...}, post: {...} }
        }
      }

      // ----- Most Read News (top 10 from view; we will show 7) -----
      if (mostReadRes.ok) {
        const mr = await mostReadRes.json();
        renderMostRead(Array.isArray(mr?.items) ? mr.items : []);
      } else {
        console.error('[news] most-read news fetch failed', mostReadRes.status, await mostReadRes.text());
      }

      // ----- Latest News (top 3, full content) -----
      if (latestNewsRes.ok) {
        const ln = await latestNewsRes.json();
        renderLatestNews(Array.isArray(ln?.items) ? ln.items : []);
      } else {
        console.error('[news] latest news fetch failed', latestNewsRes.status, await latestNewsRes.text());
      }

      // Apply to DOM: main if present, else fallback to first post
      applyMainToDom(mainItem || posts[0] || null);

    } catch (err) {
      console.error('[news] error:', err);
    }
  })();
})();
