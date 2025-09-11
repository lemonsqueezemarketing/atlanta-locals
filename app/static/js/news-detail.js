// static/js/news-detail.js
console.log('news-detail.js file loaded');

(() => {
  // --- helpers ---
  const $ = (sel, root = document) => root.querySelector(sel);

  function formatPostDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'long',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).replace(',', ' at');
  }

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

  // ---------- content helpers (flattened SQL BlogContent) ----------
  function getContent(post) {
    return post?.content || {};
  }

  // Map template’s section keys to flattened base names
  function toFlatBase(sectionKey) {
    // 'section-6-conclusion' -> 'section_6_conclusion'
    // 'section-1' -> 'section_1', etc.
    return String(sectionKey).replaceAll('-', '_');
  }

  // Render one section using flattened fields:
  //   <base>_title
  //   <base>_paragraph_1 ... _paragraph_10
  // (e.g., section_1_title, section_1_paragraph_1)
  function renderArticleSection(post, sectionKey) {
    const c = getContent(post);
    const base = toFlatBase(sectionKey);

    const titleKey = `${base}_title`;
    const paragraphs = [];
    for (let i = 1; i <= 10; i += 1) {
      const k = `${base}_paragraph_${i}`;
      if (typeof c[k] === 'string' && c[k].trim()) paragraphs.push(c[k].trim());
    }

    const hasTitle = typeof c[titleKey] === 'string' && c[titleKey].trim();
    if (!hasTitle && paragraphs.length === 0) return '';

    let html = `
      <hr class="section-divider" />
      <div class="section-content">
    `;
    if (hasTitle) {
      html += `<h3 class="section-title">${escapeHtml(c[titleKey])}</h3>`;
    }
    for (const p of paragraphs) {
      html += `<p>${escapeHtml(p)}</p>`;
    }
    html += `
      </div>
      <hr class="section-divider" />
    `;
    return html;
  }

  // Section 7: Associated Press / attribution (flattened)
  function renderAssocPressSection(post) {
    const c = getContent(post);
    const title = c.section_7_assoc_press_title;
    const p1    = c.section_7_assoc_press_paragraph_1;

    if (!title && !p1) return '';
    return `
      <hr class="section-divider" />
      <div class="section-content">
        <h3 class="section-title">Associated Press Journalist: ${escapeHtml(title || '')}</h3>
        ${p1 ? `<p><span class="copyright-text">${escapeHtml(p1)}</span></p>` : ''}
      </div>
      <hr class="section-divider" />
    `;
  }

  // Section 8: FAQs (flattened as faq_q_1/faq_a_1 …)
  function renderFaqSection(post) {
    const c = getContent(post);
    const items = [];
    for (let i = 1; i <= 12; i += 1) {
      const q = c[`faq_q_${i}`];
      const a = c[`faq_a_${i}`];
      if (typeof q === 'string' && q.trim()) {
        items.push({ q: q.trim(), a: (typeof a === 'string' ? a.trim() : '') });
      }
    }
    if (items.length === 0) return '';

    const title = escapeHtml(post?.title || 'This Article');
    const itemsHtml = items.map((f, idx) => `
      <div class="faq-item">
        <button class="faq-question" type="button" data-faq-idx="${idx}">
          Question: ${escapeHtml(f.q)}
        </button>
        <div class="faq-answer">
          <p><strong>Answer:</strong> ${escapeHtml(f.a)}</p>
        </div>
      </div>
    `).join('');

    return `
      <hr class="section-divider" />
      <div class="section-content">
        <h2 class="faq-title">FAQs About ${title}</h2>
        ${itemsHtml}
      </div>
      <hr class="section-divider" />
    `;
  }

  function wireFaqToggles(rootEl) {
    if (!rootEl) return;
    rootEl.querySelectorAll('.faq-question').forEach(btn => {
      btn.addEventListener('click', () => {
        btn.classList.toggle('active');
        const ans = btn.nextElementSibling;
        if (ans) ans.classList.toggle('show');
      });
    });
  }

  // Watch Now: inject iframe from content.yt_vid_id
  function renderWatchNow(post) {
    const c = getContent(post);
    const vid = c.yt_vid_id;
    const container = $('.watch-now-video');
    if (!container) return;

    if (!vid || !/^[\w-]{6,}$/.test(String(vid))) {
      container.innerHTML = ''; // nothing to show
      return;
    }

    container.innerHTML = `
      <iframe width="100%" height="500"
        src="https://www.youtube.com/embed/${encodeURIComponent(vid)}"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
      </iframe>
    `;
  }

  // ---------- sections that list other posts ----------
  function renderMostReadGrid(items) {
    const container = document.querySelector('.section-12-most-read .most-read-list');
    if (!container) return;

    const top = (Array.isArray(items) ? items : []).slice(0, 7);
    if (!top.length) {
      container.innerHTML = `
        <div class="most-read-item">
          <a class="most-read-link" href="#">No data yet.</a>
        </div>`;
      return;
    }

    container.innerHTML = top.map((item, i) => {
      const title = escapeHtml(item?.title || `Post ${i + 1}`);
      const slug  = item?.slug;
      const href  = slug ? `/news/${slug}` : (item?.post_id ? `/news/${item.post_id}` : '#');
      const img   = item?.image_url || resolveImage(item?.image || 'images/post_img_1.png');
      return `
        <div class="most-read-item">
          <img src="${img}" alt="${title}">
          <a href="${href}" class="most-read-link">${title}</a>
        </div>
      `;
    }).join('');
  }

  function buildReadNextHTML(posts) {
    const items = Array.isArray(posts) ? posts : [];
    const trackHtml = items.map((p, i) => {
      const title = escapeHtml(p.title || `Post ${i + 1}`);
      const img   = p.image_url || resolveImage(p.image || '');
      const href  = p?.slug ? `/news/${p.slug}` : (p?.post_id ? `/news/${p.post_id}` : '#');

      return `
        <div class="carousel-item">
          <a href="${href}">
            <img src="${img}" alt="${title}" class="carousel-img">
          </a>
          <h3 class="carousel-post-title">${title}</h3>
        </div>
      `;
    }).join('');

    const dotsHtml = items.map((_, i) =>
      `<span class="dot${i === 0 ? ' active' : ''}" data-index="${i}"></span>`
    ).join('');

    return { trackHtml, dotsHtml };
  }

  function renderReadNextCarousel(posts) {
    const container = $('.section-10-read-next');
    if (!container) return;

    const track = container.querySelector('.carousel-track');
    const dots  = container.querySelector('.carousel-dots');
    if (!track || !dots) return;

    const { trackHtml, dotsHtml } = buildReadNextHTML(posts);
    track.innerHTML = trackHtml;
    dots.innerHTML  = dotsHtml;

    // Simple carousel behavior (click dots + auto-rotate)
    let currentIndex = 0;
    const totalItems = track.children.length;

    function updateCarousel(index) {
      const clamped = Math.max(0, Math.min(index, totalItems - 1));
      track.style.transform = `translateX(${clamped * -100}%)`;
      dots.querySelectorAll('.dot').forEach((d, i) => {
        d.classList.toggle('active', i === clamped);
      });
      currentIndex = clamped;
    }

    dots.querySelectorAll('.dot').forEach((dot, index) => {
      dot.addEventListener('click', () => updateCarousel(index));
    });

    let auto = null;
    function startAuto() {
      stopAuto();
      auto = setInterval(() => {
        updateCarousel((currentIndex + 1) % totalItems);
      }, 5000);
    }
    function stopAuto() {
      if (auto) clearInterval(auto);
      auto = null;
    }

    const wrapper = container.querySelector('.carousel-wrapper');
    if (wrapper) {
      wrapper.addEventListener('mouseenter', stopAuto);
      wrapper.addEventListener('mouseleave', startAuto);
    }

    updateCarousel(0);
    if (totalItems > 1) startAuto();
  }

  function renderRelatedArticles(items) {
    const container = document.querySelector('.section-13-related .related-list');
    if (!container) return;

    const list = Array.isArray(items) ? items.slice(0, 4) : [];
    if (!list.length) {
      container.innerHTML = `
        <div class="related-item muted">
          <a class="related-link" href="#">No related articles.</a>
        </div>
      `;
      return;
    }

    container.innerHTML = list.map((item) => {
      const title = escapeHtml(item?.title || 'Untitled');
      const img   = item?.image_url || resolveImage(item?.image || '');
      const href  = item?.slug ? `/news/${item.slug}` : (item?.post_id ? `/news/${item.post_id}` : '#');
      return `
        <div class="related-item">
          <a href="${href}">
            <img src="${img}" alt="${title}">
          </a>
          <a href="${href}" class="related-link">${title}</a>
        </div>
      `;
    }).join('');
  }

  // ---------- main article fill ----------
  function applyMainToDom(post){
    if (!post) return;

    const imgEl   = document.querySelector('.article-img img');
    const newsCatEl = document.querySelector('.article-category');
    const newsTitleEl = document.querySelector('.article-title');
    const newsAuthorEl = document.querySelector('.article-meta');
    const newsDateCreatedEl = document.querySelector('.aricle-date-created');
    const newsSection1El = document.querySelector('.section-1-article-deats');
    const newsSection2El = document.querySelector('.section-2-article-deats');
    const newsSection3El = document.querySelector('.section-3-article-deats');
    const newsSection4El = document.querySelector('.section-4-article-deats');
    const newsSection5El = document.querySelector('.section-5-article-deats');
    const newsSection6El = document.querySelector('.section-6-article-deats');
    const newsSection7El = document.querySelector('.section-7-assoc-press');
    const newsSection8El = document.querySelector('.section-8-article-faqs');
    const commentCountEl = document.querySelector('.comment-count');

    const imgSrc = post.image_url || resolveImage(post.image || '');

    if (imgEl) {
      imgEl.src = imgSrc || '';
      imgEl.alt = post.title || 'Story image';
    }
    if (newsCatEl){
      newsCatEl.textContent = post.category_title || 'Untitled';
    }
    if (newsTitleEl){
      newsTitleEl.textContent = post.title || 'Untitled';
    }
    if (newsAuthorEl){
      newsAuthorEl.textContent = `By ${post.author_first_name || 'Unknown'}`;
    }
    if (newsDateCreatedEl){
      newsDateCreatedEl.textContent = post.created_at ? formatPostDate(post.created_at) : 'Unknown';
    }

    // ▶ Watch Now (YouTube) — JS injection
    renderWatchNow(post);

    // Body sections
    if (newsSection1El){ newsSection1El.innerHTML = renderArticleSection(post, 'section-1'); }
    if (newsSection2El){ newsSection2El.innerHTML = renderArticleSection(post, 'section-2'); }
    if (newsSection3El){ newsSection3El.innerHTML = renderArticleSection(post, 'section-3'); }
    if (newsSection4El){ newsSection4El.innerHTML = renderArticleSection(post, 'section-4'); }
    if (newsSection5El){ newsSection5El.innerHTML = renderArticleSection(post, 'section-5'); }
    if (newsSection6El){ newsSection6El.innerHTML = renderArticleSection(post, 'section-6-conclusion'); }
    if (newsSection7El){ newsSection7El.innerHTML = renderAssocPressSection(post); }
    if (newsSection8El){
      newsSection8El.innerHTML = renderFaqSection(post);
      wireFaqToggles(newsSection8El);
    }

    if (commentCountEl){
      const comments = post?.analytics?.comments ?? 0;
      commentCountEl.textContent = `(${comments} comments)`;
    }
  }

  // ---------- fetch & init ----------
  function getIdentFromPath() {
    // robustly grab last non-empty segment
    const parts = window.location.pathname.replace(/\/+$/, '').split('/');
    return decodeURIComponent(parts[parts.length - 1] || '');
  }

  const ident = getIdentFromPath();

  const postURL        = `/api/v1/news-posts/${encodeURIComponent(ident)}?include_content=true`;
  const readNextURL    = `/api/v1/news/${encodeURIComponent(ident)}/read-next`;
  const mostReadURL    = `/api/v1/analytics/most-read/news`;
  const relatedURL     = `/api/v1/news/${encodeURIComponent(ident)}/related`;

  console.log('[news] URLs:', { postURL, readNextURL, relatedURL, mostReadURL });

  (async () => {
    try {
      const [postRes, readNextRes, mostReadRes, relatedRes] = await Promise.all([
        fetch(postURL,     { headers: { 'Accept': 'application/json' } }),
        fetch(readNextURL, { headers: { 'Accept': 'application/json' } }),
        fetch(mostReadURL, { headers: { 'Accept': 'application/json' } }),
        fetch(relatedURL,  { headers: { 'Accept': 'application/json' } }),
      ]);

      let post = null;
      if (!postRes.ok) {
        console.error('[news] post fetch failed', postRes.status, await postRes.text());
      } else {
        post = await postRes.json();
        console.log('[news] post payload:', post);
      }

      let readNext = [];
      if (!readNextRes.ok) {
        console.error('[readNext] fetch failed', readNextRes.status, await readNextRes.text());
      } else {
        const data = await readNextRes.json(); // { items: [...], count: n }
        readNext = Array.isArray(data.items) ? data.items : [];
        console.log('[readNext] items:', readNext);
      }

      let mostReadItems = [];
      if (!mostReadRes.ok) {
        console.error('[news-detail] most-read fetch failed', mostReadRes.status, await mostReadRes.text());
      } else {
        const mr = await mostReadRes.json();
        mostReadItems = Array.isArray(mr?.items) ? mr.items : [];
        console.log('[news-detail] most-read items:', mostReadItems);
      }

      let relatedItems = [];
      if (!relatedRes.ok) {
        console.error('[related] fetch failed', relatedRes.status, await relatedRes.text());
      } else {
        const data = await relatedRes.json(); // { items: [...], count: n }
        relatedItems = Array.isArray(data.items) ? data.items : [];
        console.log('[related] items:', relatedItems);
      }

      // render side sections
      renderReadNextCarousel(readNext);
      renderMostReadGrid(mostReadItems);
      renderRelatedArticles(relatedItems);

      // render main article
      applyMainToDom(post || null);

    } catch (err) {
      console.warn('error loading news detail:', err);
    }
  })();

})();
