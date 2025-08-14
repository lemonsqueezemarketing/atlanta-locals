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

  // Simple HTML escaper for text we inject
  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Handles nested: post.content.content["section-1"]["paragraph-1"]
  function firstParagraph(post) {
    try {
      const c = post?.content;
      const inner = c?.content || c; // tolerate either shape
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
      const snippet =
        (post?.content?.content?.['section-1']?.['paragraph-1']) ||
        firstParagraph(post) ||
        '';
      descEl.textContent = snippet.length > 150 ? `${snippet.slice(0, 150)}…` : snippet;
    }
    if (linkEl) {
      linkEl.href = `/news/${post.post_id}`;
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
      const href  = `/news/${item?.post_id ?? ''}`;
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
      const href   = `/news/${item?.post_id ?? ''}`;
      const imgSrc = item?.image_url || resolveImage(item?.image || '');
  
      // pull section-1.paragraph-1 (support both content or content.content)
      let snippet = '';
      try {
        const c = item?.content;
        const inner = c?.content || c;
        const s1 = inner?.['section-1'] || inner?.section1 || inner?.section_1 || inner?.section || null;
        const p1 = s1?.['paragraph-1'] || s1?.paragraph1 || s1?.paragraph || '';
        if (typeof p1 === 'string') snippet = p1.trim();
      } catch {}
      const short = snippet.length > 150 ? `${escapeHtml(snippet.slice(0, 150))}…` : escapeHtml(snippet);
  
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
  // Ask the API for full content and only the top 3 latest
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
        if (posts.length) {
          console.log('[news] posts list:', posts);
        } else {
          console.warn('[news] no posts found in response (checked `items` and `news`).');
        }
      }

      // ----- Main story -----
      let mainItem = null;
      if (!mainRes.ok) {
        console.error('[news] main fetch failed', mainRes.status, await mainRes.text());
      } else {
        const payload = await mainRes.json();
        console.log('[news] news_main payload:', payload);
        const first = Array.isArray(payload?.items) ? payload.items[0] : null;
        if (first) {
          console.log('[news] news_main first item:', first);
          mainItem = first.post || null;
        } else {
          console.warn('[news] no active main story found in payload.items');
        }
      }

      // ----- Most Read News (top 10 from view; we will show 7) -----
      if (!mostReadRes.ok) {
        console.error('[news] most-read news fetch failed', mostReadRes.status, await mostReadRes.text());
      } else {
        const mr = await mostReadRes.json();
        const mostReadItems = Array.isArray(mr?.items) ? mr.items : [];
        console.log('[news] most_read_news (top N):', mostReadItems);
        renderMostRead(mostReadItems);
      }

      // ----- Latest News (top 3, full content) -----
      if (!latestNewsRes.ok) {
        console.error('[news] latest news fetch failed', latestNewsRes.status, await latestNewsRes.text());
      } else {
        const ln = await latestNewsRes.json();
        const latestNewsItems = Array.isArray(ln?.items) ? ln.items : [];
        console.log('[news] latest_news_posts (top N):', latestNewsItems);
        renderLatestNews(latestNewsItems);
      }

      // Apply to DOM: main if present, else fallback to first post
      applyMainToDom(mainItem || posts[0] || null);

    } catch (err) {
      console.error('[news] error:', err);
    }
  })();
})();

