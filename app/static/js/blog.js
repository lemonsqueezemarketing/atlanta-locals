// static/js/blog.js
console.log('blog.js loaded for /blog route');

(() => {
  // --- helpers (mirroring news.js) ---
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

  /**
   * Extract a first paragraph snippet from the post content.
   * Supports the new flat BlogContent shape (section_1_paragraph_1)
   * and falls back to the older nested {content: {'section-1': {'paragraph-1': ...}}} shape.
   */
  function firstParagraph(post) {
    try {
      const c = post?.content;
      if (!c) return '';

      // ✅ Prefer new flat BlogContent fields
      if (typeof c.section_1_paragraph_1 === 'string' && c.section_1_paragraph_1.trim()) {
        return c.section_1_paragraph_1.trim();
      }

      // Fallbacks: try other first paragraphs if present
      const flatKeys = [
        'section_1_paragraph_1',
        'section_1_paragraph_2',
        'section_2_paragraph_1',
        'section_3_paragraph_1'
      ];
      for (const k of flatKeys) {
        if (typeof c[k] === 'string' && c[k].trim()) return c[k].trim();
      }

      // 🧯 Legacy nested (Mongo-style) content support
      const inner = c?.content || c;
      const s1 = inner?.['section-1'] || inner?.section1 || inner?.section_1 || inner?.section || null;
      const p1 = s1?.['paragraph-1'] || s1?.paragraph1 || s1?.paragraph || null;
      if (typeof p1 === 'string' && p1.trim()) return p1.trim();
    } catch {}
    return '';
  }

  // ======================================================
  // DEBUG BLOCK (kept from earlier): log a page of blog posts
  // ======================================================
  (async () => {
    const params = new URLSearchParams();
    params.set('per_page', '10');
    params.set('include_content', 'true'); // NOTE: server should return BlogContent for lists in backlog
    const blogURL = `/api/v1/analytics/latest-blog?${params.toString()}`;
    try {
      console.log('[blog] (debug) fetching:', blogURL);
      const res = await fetch(blogURL, { headers: { 'Accept': 'application/json' } });
      if (!res.ok) {
        console.error('[blog] (debug) posts fetch failed', res.status, await res.text());
      } else {
        const payload = await res.json();
        console.log('[blog] (debug) posts payload:', payload);
        const items = Array.isArray(payload?.items) ? payload.items : [];
        console.log('[blog] (debug) posts list:', items);
      }
    } catch (err) {
      console.error('[blog] (debug) error:', err);
    }
  })();
  // ======================================================

  // --- DOM targets for rendered list + pager ---
  const listEl   = document.querySelector('[data-latest-blog-list]');
  const pagerEl  = document.querySelector('[data-blog-pager]');
  const prevBtn  = document.querySelector('[data-blog-prev]');
  const nextBtn  = document.querySelector('[data-blog-next]');
  const pageLbl  = document.querySelector('[data-blog-page-label]');

  // Ensure pagination styling classes are present (so CSS applies)
  if (pagerEl) pagerEl.classList.add('pager');
  if (prevBtn) prevBtn.classList.add('pager__btn');
  if (nextBtn) nextBtn.classList.add('pager__btn');
  if (pageLbl) pageLbl.classList.add('pager__label');

  // If the page has no container, bail gracefully (keeps console-only behavior)
  if (!listEl) return;

  // --- pagination state ---
  let state = {
    page: 1,
    perPage: 6, // smaller so pagination becomes visible sooner
    pages: 1,
    total: 0
  };

  // --- render cards (modeled after news latest cards) ---
  function renderBlogCards(items, { append = false } = {}) {
    const posts = Array.isArray(items) ? items : [];
    if (!append) listEl.innerHTML = '';
    if (!posts.length && !append) {
      listEl.innerHTML = `<div class="muted">No blog posts found.</div>`;
      return;
    }

    const html = posts.map(item => {
      const title  = escapeHtml(item?.title || 'Untitled');
      const href   = `/blog/${item?.slug ?? ''}`; // ✅ slug route
      const imgSrc = item?.image_url || resolveImage(item?.image || '');

      // ✅ Use flat BlogContent first, fallback to legacy nested
      const snippet = firstParagraph(item);
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

    listEl.insertAdjacentHTML('beforeend', html);
  }

  // --- update pager controls (always visible) ---
  function updatePager(meta) {
    const { page, pages, total, per_page } = meta || {};
    state.pages = pages ?? state.pages;
    state.total = total ?? state.total;

    console.log('[blog] pager meta:', { page: page || state.page, pages: state.pages, total: state.total });

    if (pageLbl) {
      pageLbl.textContent = `Page ${page || state.page} of ${state.pages}`;
    }
    if (prevBtn) prevBtn.disabled = (state.page <= 1);
    if (nextBtn) nextBtn.disabled = (state.page >= state.pages);

    if (pagerEl) pagerEl.style.display = ''; // force visible
  }

  // --- fetch & render one page ---
  async function loadPage(page = 1) {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('per_page', String(state.perPage));
    params.set('include_content', 'true'); // 🔔 expects BlogContent on list; server backlog if missing

    const url = `/api/v1/analytics/latest-blog?${params.toString()}`;
    console.log('[blog] fetching (paged):', url);

    try {
      const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
      if (!res.ok) {
        console.error('[blog] posts fetch failed', res.status, await res.text());
        return;
      }
      const payload = await res.json();
      console.log('[blog] posts payload (paged):', payload);

      const items = Array.isArray(payload?.items) ? payload.items : [];
      state.page    = payload?.page ?? page;
      state.perPage = payload?.per_page ?? state.perPage;
      state.pages   = payload?.pages ?? state.pages;
      state.total   = payload?.total ?? state.total;

      renderBlogCards(items, { append: false });
      updatePager({
        page: state.page,
        pages: state.pages,
        total: state.total,
        per_page: state.perPage
      });
    } catch (err) {
      console.error('[blog] error:', err);
    }
  }

  // --- wire up pager ---
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (state.page > 1) {
        console.log('[blog] pager: prev clicked');
        loadPage(state.page - 1);
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (state.page < state.pages) {
        console.log('[blog] pager: next clicked');
        loadPage(state.page + 1);
      }
    });
  }

  // initial load
  loadPage(1);
})();
