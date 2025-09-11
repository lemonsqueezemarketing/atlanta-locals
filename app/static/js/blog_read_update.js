// static/js/blog_read_update.js
console.log('blog_read_update.js (WTForms) loaded');

document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('blog-read-update-form');
  const delForm    = document.getElementById('delete-form');
  const inputTitle = document.getElementById('title');
  const inputSlug  = document.getElementById('slug');
  const fileImage  = document.getElementById('image');
  const imgPrev    = document.getElementById('image-preview');

  // --- helpers ---
  const slugify = (s) =>
    (s || '')
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');

  // Auto-fill slug unless user edits slug manually
  if (inputTitle) {
    inputTitle.addEventListener('input', () => {
      if (inputSlug && !inputSlug.dataset.userEdited) {
        inputSlug.value = slugify(inputTitle.value.trim());
      }
    });
  }
  if (inputSlug) {
    inputSlug.addEventListener('input', () => {
      inputSlug.dataset.userEdited = '1';
    });
  }

  // Image preview on choose
  if (fileImage && imgPrev) {
    fileImage.addEventListener('change', () => {
      const f = fileImage.files && fileImage.files[0];
      if (!f) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        imgPrev.src = e.target.result;
        imgPrev.style.display = 'block';
      };
      reader.readAsDataURL(f);
    });
  }

  // Guard against double submit on update
  if (form) {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = true;
      // ensure slug exists
      if (inputSlug && (!inputSlug.value || !inputSlug.value.trim()) && inputTitle) {
        inputSlug.value = slugify(inputTitle.value.trim());
      }
    });
  }

  // Delete confirm
  if (delForm) {
    delForm.addEventListener('submit', (e) => {
      const ok = confirm('Delete this post? This cannot be undone.');
      if (!ok) e.preventDefault();
    });
  }
});
