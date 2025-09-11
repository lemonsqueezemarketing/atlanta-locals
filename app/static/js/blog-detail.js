// static/js/blog-detail.js
console.log('blog-detail.js loaded (slug-based)');

(() => {
  // --- helpers ---
  const $ = (sel, root = document) => root.querySelector(sel);

  function formatPostDate(dateString) {
    if (!dateString) return '';
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

  // ---------- RENDERERS (SQL BlogContent field names) ----------
// --- Watch Now (YouTube) from content.yt_vid_id ---
function renderWatchNow(post) {
  const wrap = document.querySelector('.section-4-watch-now');
  if (!wrap) return;

  const target = wrap.querySelector('.watch-now-video');
  if (!target) return;

  const ytId = post?.content?.yt_vid_id;
  if (!ytId) {
    // Hide the section entirely if there is no video id
    wrap.style.display = 'none';
    return;
  }

  target.innerHTML = `
    <iframe width="100%" height="500"
      src="https://www.youtube.com/embed/${encodeURIComponent(ytId)}"
      title="YouTube video player"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen>
    </iframe>
  `;
}

  // Generic section renderer for section_1..section_5 and section_6_conclusion
  function renderSection(content, basePrefix) {
    if (!content || !basePrefix) return '';
    const titleKey = `${basePrefix}_title`;

    // Collect paragraph_x keys under the base prefix
    const paraRegex = new RegExp(`^${basePrefix}_paragraph_(\\d+)$`);
    const paras = Object.keys(content)
      .map(k => {
        const m = k.match(paraRegex);
        return m ? { idx: Number(m[1]), key: k } : null;
      })
      .filter(Boolean)
      .sort((a, b) => a.idx - b.idx);

    if (!content[titleKey] && paras.length === 0) return '';

    let html = `
      <hr class="section-divider" />
      <div class="section-content">
        ${content[titleKey] ? `<h3 class="section-title">${escapeHtml(content[titleKey])}</h3>` : ''}
    `;

    paras.forEach(p => {
      html += `<p>${escapeHtml(content[p.key])}</p>`;
    });

    html += `
      </div>
      <hr class="section-divider" />
    `;
    return html;
  }

  function renderAssocPress(content) {
    if (!content) return '';
    const title = escapeHtml(content.section_7_assoc_press_title || '');
    const text  = escapeHtml(content.section_7_assoc_press_paragraph_1 || '');
    if (!title && !text) return '';

    return `
      <hr class="section-divider" />
      <div class="section-content">
        <h3 class="section-title">Associated Press Journalist: ${title}</h3>
        <p><span class="copyright-text">${text}</span></p>
      </div>
      <hr class="section-divider" />
    `;
  }

  function renderFaqs(content, articleTitle) {
    if (!content) return '';
    const qRegex = /^faq_q_(\d+)$/;
    const aRegex = /^faq_a_(\d+)$/;

    const qs = {};
    const as = {};
    for (const k of Object.keys(content)) {
      const qm = k.match(qRegex);
      if (qm) qs[qm[1]] = content[k];
      const am = k.match(aRegex);
      if (am) as[am[1]] = content[k];
    }

    const idxs = Object.keys(qs)
      .concat(Object.keys(as))
      .filter((v, i, arr) => arr.indexOf(v) === i)
      .map(Number)
      .sort((a, b) => a - b);

    if (idxs.length === 0) return '';

    const itemsHtml = idxs.map(i => {
      const q = escapeHtml(qs[String(i)] || `Question ${i}`);
      const a = escapeHtml(as[String(i)] || '');
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
        <h2 class="faq-title">FAQs About ${escapeHtml(articleTitle || 'This Article')}</h2>
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
      const href  = item?.slug ? `/blog/${encodeURIComponent(item.slug)}` : '#';
      const img   = item?.image_url || resolveImage(item?.image || 'images/post_img_1.png');
      return `
        <div class="most-read-item">
          <a href="${href}">
            <img src="${img}" alt="${title}">
          </a>
          <a href="${href}" class="most-read-link">${title}</a>
        </div>
      `;
    }).join('');
  }

  // Build HTML for Section 10 "Read Next"
  function buildReadNextHTML(posts) {
    const items = Array.isArray(posts) ? posts : [];
    const trackHtml = items.map((p, i) => {
      const title = escapeHtml(p.title || `Post ${i + 1}`);
      const img   = p.image_url || resolveImage(p.image || '');
      const href  = p.slug ? `/blog/${encodeURIComponent(p.slug)}` : '#';

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

    container.innerHTML = list.map((item) => {
      const title = escapeHtml(item?.title || 'Untitled');
      const img   = item?.image_url || resolveImage(item?.image || '');
      const href  = item?.slug ? `/blog/${encodeURIComponent(item.slug)}` : '#';
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

  // ---------- MAIN DOM POPULATION ----------

  function applyMainToDom(post) {
    if (!post) return;

    const imgEl   = document.querySelector('.article-img img');
    const catEl   = document.querySelector('.article-category');
    const titleEl = document.querySelector('.article-title');
    const authorEl = document.querySelector('.article-meta');
    const createdEl = document.querySelector('.aricle-date-created'); // class name kept as-is

    const s1El = document.querySelector('.section-1-article-deats');
    const s2El = document.querySelector('.section-2-article-deats');
    const s3El = document.querySelector('.section-3-article-deats');
    const s4El = document.querySelector('.section-4-article-deats');
    const s5El = document.querySelector('.section-5-article-deats');
    const s6El = document.querySelector('.section-6-article-deats');
    const s7El = document.querySelector('.section-7-assoc-press');
    const s8El = document.querySelector('.section-8-article-faqs');

    const commentCountEl = document.querySelector('.comment-count');

    const imgSrc = post.image_url || resolveImage(post.image || '');
    if (imgEl) {
      imgEl.src = imgSrc || '';
      imgEl.alt = post.title || 'Story image';
    }
    if (catEl)   catEl.textContent   = post.category_title || '';
    if (titleEl) titleEl.textContent = post.title || 'Untitled';
    if (authorEl) authorEl.textContent = post.author_first_name ? `By ${post.author_first_name}` : '';
    if (createdEl) createdEl.textContent = formatPostDate(post.created_at) || '';

    // render watch now
    renderWatchNow(post);
    const content = post.content || {};

    if (s1El) s1El.innerHTML = renderSection(content, 'section_1');
    if (s2El) s2El.innerHTML = renderSection(content, 'section_2');
    if (s3El) s3El.innerHTML = renderSection(content, 'section_3');
    if (s4El) s4El.innerHTML = renderSection(content, 'section_4');
    if (s5El) s5El.innerHTML = renderSection(content, 'section_5');
    if (s6El) s6El.innerHTML = renderSection(content, 'section_6_conclusion');
    if (s7El) s7El.innerHTML = renderAssocPress(content);
    if (s8El) {
      s8El.innerHTML = renderFaqs(content, post.title);
      wireFaqToggles(s8El);
    }

    if (commentCountEl) {
      const comments = post?.analytics?.comments ?? 0;
      commentCountEl.textContent = `(${comments} comments)`;
    }
  }

  // ---------- FETCH & INIT (slug-first) ----------

  // get last non-empty path segment as slug
  const pathParts = window.location.pathname.split('/').filter(Boolean);
  const slug = decodeURIComponent(pathParts[pathParts.length - 1] || '');

  // API endpoints:
  // - main post by slug (includes content)
  //   ✅ Correct endpoint shape: /api/v1/blog-posts/<ident>
  const postURLBySlug = `/api/v1/blog-posts/${encodeURIComponent(slug)}?include_content=true`;
  const mostReadBlogURL = `/api/v1/analytics/most-read/blog`;

  (async () => {
    try {
      // 1) Fetch the main post by slug
      const postRes = await fetch(postURLBySlug, { headers: { 'Accept': 'application/json' } });
      if (!postRes.ok) {
        console.error('[blog] post (by slug) fetch failed', postRes.status, await postRes.text());
        return;
      }
      const post = await postRes.json();
      console.log('[blog] post payload (slug):', post);

      // Render the main article immediately
      applyMainToDom(post);

      // 2) Fire off dependent requests that need the numeric id
      const postId = post?.post_id;
      const readNextURL = postId ? `/api/v1/blog/${postId}/read-next` : null;
      const relatedURL  = postId ? `/api/v1/blog/${postId}/related`   : null;

      const fetches = [
        fetch(mostReadBlogURL, { headers: { 'Accept': 'application/json' } }),
        readNextURL ? fetch(readNextURL, { headers: { 'Accept': 'application/json' } }) : Promise.resolve(null),
        relatedURL  ? fetch(relatedURL,  { headers: { 'Accept': 'application/json' } }) : Promise.resolve(null),
      ];

      const [mostReadRes, readNextRes, relatedRes] = await Promise.all(fetches);

      // Most Read
      if (mostReadRes && mostReadRes.ok) {
        const mr = await mostReadRes.json();
        const mostReadItems = Array.isArray(mr?.items) ? mr.items : [];
        renderMostReadGrid(mostReadItems);
      } else if (mostReadRes) {
        console.error('[most-read] fetch failed', mostReadRes.status, await mostReadRes.text());
      }

      // Read Next
      if (readNextRes) {
        if (!readNextRes.ok) {
          console.error('[readNext] fetch failed', readNextRes.status, await readNextRes.text());
        } else {
          const data = await readNextRes.json();
          const readNext = Array.isArray(data.items) ? data.items : [];
          renderReadNextCarousel(readNext);
        }
      }

      // Related
      if (relatedRes) {
        if (!relatedRes.ok) {
          console.error('[related] fetch failed', relatedRes.status, await relatedRes.text());
        } else {
          const data = await relatedRes.json();
          const relatedItems = Array.isArray(data.items) ? data.items : [];
          renderRelatedArticles(relatedItems);
        }
      }

    } catch (err) {
      console.warn('error loading blog detail:', err);
    }
  })();
})();
