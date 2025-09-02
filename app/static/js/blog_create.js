// static/js/blog_create.js
console.log('blog_create.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  if (!form) {
    console.warn('[blog_create] No form found on page.');
    return;
  }

  // Elements
  const selCategory = document.getElementById('category');
  const selAuthor   = document.getElementById('author');
  const fileImage   = document.getElementById('image');
  const inputTitle  = document.getElementById('title');
  const inputSlug   = document.getElementById('slug');

  // Endpoints
  const API_BLOG_POSTS   = '/api/v1/blog-posts';
  const API_CATEGORIES   = '/api/v1/blog-categories?per_page=200';
  const API_USERS        = '/api/v1/users?per_page=200';
  const REDIRECT_LIST    = '/admin/blog'; // list-view route

  // Helpers
  const get = (name) => {
    const el = form.querySelector(`[name="${name}"]`);
    return el ? el.value.trim() : '';
  };

  const slugify = (s) =>
    (s || '')
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');

  const getFaqs = () => {
    const items = form.querySelectorAll('.content-section[data-section="section-8-faqs"] .faq-item');
    const out = [];
    items.forEach((wrap) => {
      const q = wrap.querySelector('input[name^="content[section-8-faqs]"][name$="[question]"]');
      const a = wrap.querySelector('textarea[name^="content[section-8-faqs]"][name$="[answer]"]');
      const question = q ? q.value.trim() : '';
      const answer = a ? a.value.trim() : '';
      if (question || answer) out.push({ question, answer });
    });
    return out;
  };

  const section3 = (key) => ({
    title: get(`content[${key}][title]`),
    'paragraph-1': get(`content[${key}][paragraph-1]`),
    'paragraph-2': get(`content[${key}][paragraph-2]`),
    'paragraph-3': get(`content[${key}][paragraph-3]`),
  });

  const readContentFromForm = () => ({
    'section-1': section3('section-1'),
    'section-2': section3('section-2'),
    'section-3': section3('section-3'),
    'section-4': section3('section-4'),
    'section-5': section3('section-5'),
    'section-6-conclusion': section3('section-6-conclusion'),
    'section-7-assoc-press': {
      title: get('content[section-7-assoc-press][title]'),
      'paragraph-1': get('content[section-7-assoc-press][paragraph-1]'),
    },
    'section-8-faqs': getFaqs(),
  });

  // Auto-suggest slug when title changes or when slug is empty
  const maybeAutoFillSlug = () => {
    if (!inputSlug) return;
    if (!inputSlug.value.trim() && inputTitle && inputTitle.value.trim()) {
      inputSlug.value = slugify(inputTitle.value.trim());
    }
  };
  if (inputTitle) {
    inputTitle.addEventListener('input', () => {
      if (inputSlug && !inputSlug.dataset.userEdited) {
        maybeAutoFillSlug();
      }
    });
  }
  if (inputSlug) {
    inputSlug.addEventListener('input', () => {
      inputSlug.dataset.userEdited = '1';
    });
  }

  // Populate <select> helpers
  const fillSelect = (selectEl, items, toValue, toLabel) => {
    if (!selectEl) return;
    selectEl.innerHTML = ''; // clear "Loading..."
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = `Select ${selectEl.id === 'category' ? 'a category' : 'an author'}`;
    placeholder.disabled = true;
    placeholder.selected = true;
    selectEl.appendChild(placeholder);

    items.forEach((item) => {
      const opt = document.createElement('option');
      opt.value = String(toValue(item));
      opt.textContent = toLabel(item);
      selectEl.appendChild(opt);
    });
  };

  // Fetch categories & users
  const loadLookups = async () => {
    try {
      const [catRes, userRes] = await Promise.all([
        fetch(API_CATEGORIES, { headers: { Accept: 'application/json' } }),
        fetch(API_USERS, { headers: { Accept: 'application/json' } }),
      ]);

      if (!catRes.ok) throw new Error(`categories ${catRes.status}`);
      if (!userRes.ok) throw new Error(`users ${userRes.status}`);

      const catJson = await catRes.json();
      const userJson = await userRes.json();

      const categories = Array.isArray(catJson.items) ? catJson.items : [];
      const users = Array.isArray(userJson.items) ? userJson.items : [];

      fillSelect(
        selCategory,
        categories,
        (c) => c.blog_cat_id,
        (c) => `${c.title} (${c.slug})`
      );

      fillSelect(
        selAuthor,
        users,
        (u) => u.my_user_id,
        (u) => {
          const first = u.first_name || '';
          const last = u.last_name || '';
          const email = u.email ? ` — ${u.email}` : '';
          return `${first} ${last}`.trim() + email;
        }
      );
    } catch (err) {
      console.error('[blog_create] Failed to load lookups:', err);
      if (selCategory) {
        selCategory.innerHTML = '<option value="" disabled selected>Failed to load categories</option>';
      }
      if (selAuthor) {
        selAuthor.innerHTML = '<option value="" disabled selected>Failed to load authors</option>';
      }
    }
  };

  loadLookups();

  // Map field names from server errors to DOM elements (for focusing)
  const fieldToEl = {
    title: inputTitle,
    slug: inputSlug,
    blog_cat_id: selCategory,
    author_id: selAuthor,
    image: fileImage,
  };

  // Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Guard: prevent duplicate submits or double bindings
    if (form.dataset.submitting === '1') return;

    // Run native HTML5 validation first
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    // Gather main fields
    const title = get('title');
    let slug = get('slug');
    if (!slug) slug = slugify(title);

    // Validate category/author selection
    const blog_cat_id = selCategory ? parseInt(selCategory.value, 10) : NaN;
    const author_id   = selAuthor ? parseInt(selAuthor.value, 10) : NaN;

    if (!Number.isInteger(blog_cat_id) || blog_cat_id <= 0) {
      alert('Please select a valid category.');
      selCategory && selCategory.focus();
      return;
    }
    if (!Number.isInteger(author_id) || author_id <= 0) {
      alert('Please select a valid author.');
      selAuthor && selAuthor.focus();
      return;
    }

    // Image handling (string path expected by API)
    let image = '';
    if (fileImage && fileImage.files && fileImage.files[0]) {
      image = `uploads/${fileImage.files[0].name}`;
    } else {
      image = 'images/placeholder.jpg'; // ensure this exists under /static/images/
    }

    // Build content payload from form
    const content = readContentFromForm();

    // Final payload for /api/v1/blog-posts
    const payload = {
      title,
      slug,
      blog_cat_id,
      author_id,
      image,
      content, // server will store in Mongo and set content_mongo_id
    };

    console.log('[blog_create] POST payload:', payload);

    // Disable submit to prevent duplicate clicks
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    form.dataset.submitting = '1';

    try {
      const formData = new FormData();
      formData.append('image', fileImage.files[0]); // image file
      formData.append('payload', JSON.stringify(payload)); // all other data
      
      const res = await fetch(API_BLOG_POSTS, {
        method: 'POST',
        body: formData,
      });

      // Try to parse JSON (fallback to raw text)
      let body;
      let raw = '';
      try {
        body = await res.json();
      } catch {
        try { raw = await res.text(); } catch {}
      }

      if (!res.ok) {
        console.error('[blog_create] POST failed', res.status, body || raw);

        // Surface field errors if present
        let firstField = null;
        if (body && body.error && typeof body.error === 'object') {
          const parts = [];
          Object.entries(body.error).forEach(([field, msgs]) => {
            const msg = Array.isArray(msgs) ? msgs.join(', ') : String(msgs);
            parts.push(`${field}: ${msg}`);
            if (!firstField && fieldToEl[field]) firstField = fieldToEl[field];
          });
          alert(`Validation error:\n\n${parts.join('\n')}`);
        } else if (body && body.error) {
          alert(String(body.error));
        } else {
          alert(raw || `Failed to create post (HTTP ${res.status}).`);
        }

        if (firstField && typeof firstField.focus === 'function') firstField.focus();
        return;
      }

      console.log('[blog_create] Created:', body);
      alert('Blog post created!');
      window.location.href = REDIRECT_LIST;
    } catch (err) {
      console.error('[blog_create] Network/JS error:', err);
      alert('Network error. Please try again.');
    } finally {
      // If we didn’t redirect yet, re-enable
      form.dataset.submitting = '';
      if (submitBtn) submitBtn.disabled = false;
    }
  });
});
