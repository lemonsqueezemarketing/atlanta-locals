// static/js/blog_read_update.js
console.log('blog_read_update.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  // Try to read post id from the form's data attribute first
  const form = document.getElementById('blog-read-update-form');
  let postId = NaN;

  if (form && form.dataset.postId) {
    postId = parseInt(form.dataset.postId, 10);
  }

  // Fallback: parse from URL like /admin/blogs/:id
  if (!Number.isInteger(postId)) {
    const m = window.location.pathname.match(/\/admin\/blogs\/(\d+)(?:\/)?$/);
    if (m) postId = parseInt(m[1], 10);
  }

  // Last resort: use trailing path segment
  if (!Number.isInteger(postId)) {
    const parts = window.location.pathname.split('/').filter(Boolean);
    const maybe = parts[parts.length - 1];
    if (/^\d+$/.test(maybe)) postId = parseInt(maybe, 10);
  }

  if (!Number.isInteger(postId)) {
    console.error('[admin blog] Unable to determine post id from page.');
    return;
  }

  // --- Elements (match your HTML ids) ---
  const inputTitle   = document.querySelector('#title');
  const inputSlug    = document.querySelector('#slug');
  const selCategory  = document.querySelector('#category');
  const selAuthor    = document.querySelector('#author');
  const imgPreview   = document.querySelector('#image-preview');

  // --- Endpoints (match api.py) ---
  const postURL  = `/api/v1/blog-posts/${postId}`;
  const catsURL  = `/api/v1/blog-categories?per_page=200`;
  const usersURL = `/api/v1/users?per_page=200`;

  console.log('[admin blog] fetching:', postURL);

  // --- Helpers (mirror cadence used in blog-detail.js) ---
  function resolveImage(path) {
    if (!path) return '';
    if (/^https?:\/\//i.test(path)) return path;
    return `/static/${String(path).replace(/^\/+/, '')}`;
  }

  function fillSelect(selectEl, items, toValue, toLabel, selectedValue) {
    if (!selectEl) return;
    selectEl.innerHTML = '';

    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.disabled = true;
    placeholder.textContent = `Select ${selectEl.id === 'category' ? 'a category' : 'an author'}`;
    selectEl.appendChild(placeholder);

    items.forEach((item) => {
      const opt = document.createElement('option');
      opt.value = String(toValue(item));
      opt.textContent = toLabel(item);
      selectEl.appendChild(opt);
    });

    if (selectedValue != null) {
      selectEl.value = String(selectedValue);
    } else {
      placeholder.selected = true;
    }
  }

  // ---- Helpers for content mapping ----
  const innerContent = (post) => post?.content?.content || post?.content || {};

  const setByName = (name, val) => {
    const el = form ? form.querySelector(`[name="${name}"]`) : null;
    if (el) el.value = val ?? '';
  };

  const setSectionFields = (sectionKey, data) => {
    if (!data || typeof data !== 'object') return;
    setByName(`content[${sectionKey}][title]`,        data.title || '');
    setByName(`content[${sectionKey}][paragraph-1]`,  data['paragraph-1'] || '');
    setByName(`content[${sectionKey}][paragraph-2]`,  data['paragraph-2'] || '');
    setByName(`content[${sectionKey}][paragraph-3]`,  data['paragraph-3'] || '');
  };
  // -------------------------------------

  (async () => {
    try {
      // Fetch post, categories, and users in parallel
      const [postRes, catsRes, usersRes] = await Promise.all([
        fetch(postURL, { headers: { Accept: 'application/json' } }),
        fetch(catsURL, { headers: { Accept: 'application/json' } }),
        fetch(usersURL, { headers: { Accept: 'application/json' } }),
      ]);

      if (!postRes.ok) {
        const txt = await postRes.text().catch(() => '');
        console.error('[admin blog] post fetch failed', postRes.status, txt);
        return;
      }

      const post = await postRes.json();
      console.log('[admin blog] post payload:', post);
      console.log('[admin blog] post content:', post?.content ?? null);

      const categories = catsRes.ok ? (await catsRes.json())?.items || [] : [];
      const users      = usersRes.ok ? (await usersRes.json())?.items || [] : [];

      // --- Populate Title & Slug ---
      if (inputTitle) inputTitle.value = post.title || 'Untitled';
      if (inputSlug)  inputSlug.value  = post.slug || post.title_slug || 'untitled';

      // --- Preselect Category ---
      fillSelect(
        selCategory,
        categories,
        (c) => c.blog_cat_id,
        (c) => `${c.title} (${c.slug})`,
        post.blog_cat_id
      );

      // --- Preselect Author ---
      fillSelect(
        selAuthor,
        users,
        (u) => u.my_user_id,
        (u) => {
          const first = u.first_name || '';
          const last  = u.last_name || '';
          const email = u.email ? ` — ${u.email}` : '';
          return `${(first + ' ' + last).trim()}${email}`;
        },
        post.author_id
      );

      // --- Render Image Preview ---
      if (imgPreview) {
        const src = post.image_url || resolveImage(post.image || '');
        imgPreview.src = src || '';
        imgPreview.alt = post.title || 'Current image';
      }

      // ------- Populate Content Sections -------
      const inner = innerContent(post);

      // Sections 1–5 map 1:1 (title + paragraph-1..3)
      setSectionFields('section-1', inner['section-1'] || {});
      setSectionFields('section-2', inner['section-2'] || {});
      setSectionFields('section-3', inner['section-3'] || {});
      setSectionFields('section-4', inner['section-4'] || {});
      setSectionFields('section-5', inner['section-5'] || {});

      // Payload section-6 -> form section-6-conclusion
      const s6 = inner['section-6'] || inner['section-6-conclusion'] || null;
      if (s6) setSectionFields('section-6-conclusion', s6);

      // Payload section-8-assoc-press -> form section-7-assoc-press
      const s7ap = inner['section-8-assoc-press'] || inner['section-7-assoc-press'] || null;
      if (s7ap) {
        setByName('content[section-7-assoc-press][title]',        s7ap.title || '');
        setByName('content[section-7-assoc-press][paragraph-1]',  s7ap['paragraph-1'] || '');
        setByName('content[section-7-assoc-press][paragraph-2]',  s7ap['paragraph-2'] || '');
        setByName('content[section-7-assoc-press][paragraph-3]',  s7ap['paragraph-3'] || '');
      }

      // Payload section-9-faqs -> form section-8-faqs (first five rows present in HTML)
      const faqs = Array.isArray(inner['section-9-faqs'])
        ? inner['section-9-faqs']
        : (Array.isArray(inner['section-8-faqs']) ? inner['section-8-faqs'] : []);
      faqs.forEach((f, i) => {
        setByName(`content[section-8-faqs][${i}][question]`, f?.question || '');
        setByName(`content[section-8-faqs][${i}][answer]`,   f?.answer || '');
      });
      // -----------------------------------------

    } catch (err) {
      console.error('[admin blog] fetch error:', err);
    }
  })();
});
