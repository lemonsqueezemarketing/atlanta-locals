console.log('blog-detail.js file loaded');

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

  // Article sections (1–6)
  function renderArticleSection(post, sectionKey) {
    const inner = post?.content?.content || post?.content || {};
    const section = inner?.[sectionKey];
    if (!section) return '';

    let html = `
      <hr class="section-divider" />
      <div class="section-content">
        <h3 class="section-title">${escapeHtml(section.title)}</h3>
    `;

    Object.keys(section)
      .filter(k => k.startsWith('paragraph-'))
      .sort((a, b) => Number(a.split('-')[1]) - Number(b.split('-')[1]))
      .forEach(k => {
        html += `<p>${escapeHtml(section[k])}</p>`;
      });

    html += `
      </div>
      <hr class="section-divider" />
    `;
    return html;
  }

  function renderMostReadGrid(items) {
    const container = document.querySelector('.section-12-most-read .most-read-list');
    if (!container) return;
  
    const top = (Array.isArray(items) ? items : []).slice(0, 7); // trim if you want fewer
    if (!top.length) {
      container.innerHTML = `
        <div class="most-read-item">
          <a class="most-read-link" href="#">No data yet.</a>
        </div>`;
      return;
    }
  
    container.innerHTML = top.map((item, i) => {
      const title = escapeHtml(item?.title || `Post ${i + 1}`);
      const href  = `/blog/${item?.post_id ?? ''}`;
      const img   = item?.image_url || resolveImage(item?.image || 'images/post_img_1.png');
      return `
        <div class="most-read-item">
          <img src="${img}" alt="${title}">
          <a href="${href}" class="most-read-link">${title}</a>
        </div>
      `;
    }).join('');
  }
  
  

  // Section 7
  function renderAssocPressSection(post) {
    const inner = post?.content?.content || post?.content || {};
    const s7 = inner['section-7-assoc-press'];
    if (!s7) return '';

    const title = escapeHtml(s7.title || '');
    const text  = escapeHtml(s7['paragraph-1'] || '');

    return `
      <hr class="section-divider" />
      <div class="section-content">
        <h3 class="section-title">Associated Press Journalist: ${title}</h3>
        <p><span class="copyright-text">${text}</span></p>
      </div>
      <hr class="section-divider" />
    `;
  }

  // Section 8 (FAQs)
  function renderFaqSection(post) {
    const inner = post?.content?.content || post?.content || {};
    const faqs = inner['section-8-faqs'] || inner['sectition-8-faqs'] || [];
    const title = escapeHtml(post?.title || 'This Article');

    if (!Array.isArray(faqs) || faqs.length === 0) return '';

    const itemsHtml = faqs.map((f, i) => {
      const q = escapeHtml(f?.question || `Question ${i + 1}`);
      const a = escapeHtml(f?.answer || '');
      return `
        <div class="faq-item">
          <button class="faq-question" type="button" data-faq-idx="${i}">
            Question: ${q}
          </button>
          <div class="faq-answer">
            <p><strong>Answer:</strong> ${a}</p>
          </div>
        </div>
      `;
    }).join('');

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

  // Build HTML for Section 10 "Read Next"
  function buildReadNextHTML(posts) {
    const items = Array.isArray(posts) ? posts : [];
    const trackHtml = items.map((p, i) => {
      const title = escapeHtml(p.title || `Post ${i + 1}`);
      const img   = p.image_url || resolveImage(p.image || '');
      const id    = p.post_id ?? p.id ?? '';
      const href  = id ? `/blog/${id}` : '#';

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

  // Inject and wire the carousel (Section 10)
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

    // Auto-rotation
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

// Inject and wire related section
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
  
    container.innerHTML = list.map((item, i) => {
      const title = escapeHtml(item?.title || 'Untitled');
      const img   = item?.image_url || resolveImage(item?.image || '');
      const href  = `/blog/${item?.post_id ?? ''}`;
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
  

  // Fill the page with a single post
  function applyMainToDom(post){
    if (!post) return;

    const imgEl   = document.querySelector('.article-img img');
    const newsCatEl = document.querySelector('.article-category');
    const newsTitleEl = document.querySelector('.article-title');
    const newsAuthorEl = document.querySelector('.article-meta');
    const newsDateCreatedEl = document.querySelector('.aricle-date-created'); // note: class name kept as in HTML
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
      newsAuthorEl.textContent = `By ${post.author_first_name}` || 'Unknown';
    }
    if (newsDateCreatedEl){
      newsDateCreatedEl.textContent = formatPostDate(post.created_at) || 'Unknown';
    }

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

  // ---- fetch & init ----
  const pathParts = window.location.pathname.split('/');
  const blogId = pathParts[pathParts.length - 1];
  const postURL = `/api/v1/blog-posts/${blogId}`;
  const readNextURL = `/api/v1/blog/${blogId}/read-next`;
  const mostReadBlogURL = `/api/v1/analytics/most-read/blog`;
  const relatedURL = `/api/v1/blog/${blogId}/related`;

  console.log(postURL);
  console.log(readNextURL);
  console.log(relatedURL);

  (async () => {
    try {
      const [postRes, readNextRes, mostReadRes, relatedRes] = await Promise.all([
        fetch(postURL,     { headers: { 'Accept': 'application/json' } }),
        fetch(readNextURL, { headers: { 'Accept': 'application/json' } }),
        fetch(mostReadBlogURL, { headers: { 'Accept': 'application/json' } }),
        fetch(relatedURL,      { headers: { 'Accept': 'application/json' } }),
      ]);

      let post = null;
      if (!postRes.ok) {
        console.error('[blog] post fetch failed', postRes.status, await postRes.text());
      } else {
        const data = await postRes.json();
        console.log('[blog] post payload:', data);
        post = data;
      }

      let readNext = [];
      if (!readNextRes.ok) {
        console.error('[readNext] fetch failed', readNextRes.status, await readNextRes.text());
      } else {
        const data = await readNextRes.json(); // { items: [...], count: n }
        console.log('[readNext] payload:', data);
        readNext = Array.isArray(data.items) ? data.items : [];
        if (readNext.length) {
          console.log('[readNext] items:', readNext);
        } else {
          console.warn('[readNext] no items in response.');
        }
      }
      

        // after Promise.all([... mostReadBlogURL ...]) resolves:
        let mostReadItems = [];
        if (!mostReadRes.ok) {
        console.error('[blog-detail] most-read fetch failed', mostReadRes.status, await mostReadRes.text());
        } else {
        const mr = await mostReadRes.json();
        mostReadItems = Array.isArray(mr?.items) ? mr.items : [];
        console.log('[blog-detail] most-read items:', mostReadItems);
        }
        

        // after Promise.all([... relatedURL ...]) resolves:
        let relatedItems = [];
        if (!relatedRes.ok) {
          console.error('[related] fetch failed', relatedRes.status, await relatedRes.text());
        } else {
          const data = await relatedRes.json(); // { items: [...], count: n }
          console.log('[related] payload:', data);
          relatedItems = Array.isArray(data.items) ? data.items : [];
          if (relatedItems.length) {
            console.log('[related] items:', relatedItems);
          } else {
            console.warn('[related] no items in response.');
          }
        }
              // render "Read Next" carousel
      renderReadNextCarousel(readNext);

      renderMostReadGrid(mostReadItems);
      renderRelatedArticles(relatedItems);




      // render main article
      applyMainToDom(post || null);


      

    } catch (err) {
      console.warn('error loading blog detail:', err);
    }
  })();

})();
