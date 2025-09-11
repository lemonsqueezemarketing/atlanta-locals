// static/js/blog_create.js
console.log('blog_create.js (WTForms) loaded');

(() => {
  const form = document.querySelector('.admin-main form');
  if (!form) {
    console.warn('[blog_create] form not found');
    return;
  }

  // WTForms field ids match field names by default
  const inputTitle = document.getElementById('title');
  const inputSlug  = document.getElementById('slug');
  const selCat     = document.getElementById('blog_cat_id');
  const selAuthor  = document.getElementById('author_id');
  const fileImage  = document.getElementById('image');

  // Preview area from the template
  const previewWrap = document.querySelector('[data-image-preview]');
  const previewImg  = previewWrap ? previewWrap.querySelector('img') : null;

  // ----- helpers -----
  const slugify = (s) =>
    (s || '')
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')  // strip accents
      .replace(/[^a-z0-9]+/g, '-')      // non-alnum -> dashes
      .replace(/(^-|-$)/g, '');         // trim dashes

  const maybeAutoFillSlug = () => {
    if (!inputSlug || !inputTitle) return;
    if (!inputSlug.value.trim() && inputTitle.value.trim()) {
      inputSlug.value = slugify(inputTitle.value.trim());
    }
  };

  // ----- behaviors -----
  // Auto-slug (don’t overwrite if user edits slug)
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

  // Image preview (client-side only)
  if (fileImage && previewWrap && previewImg) {
    fileImage.addEventListener('change', () => {
      const f = fileImage.files && fileImage.files[0];
      if (!f) {
        previewWrap.style.display = 'none';
        previewImg.src = '';
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewWrap.style.display = 'block';
      };
      reader.readAsDataURL(f);
    });
  }

  // Submit: ensure slug present, then let the browser submit normally (WTForms/Flask handles it)
  form.addEventListener('submit', () => {
    if (inputSlug && (!inputSlug.value || !inputSlug.value.trim()) && inputTitle && inputTitle.value.trim()) {
      inputSlug.value = slugify(inputTitle.value.trim());
    }
    // guard against double-submit
    const btn = form.querySelector('button[type="submit"]');
    if (btn) btn.disabled = true;
  });
})();
