// static/js/blog_create.js
console.log('blog_create.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  if (!form) {
    console.warn('[blog_create] No form found on page.');
    return;
  }

  const get = (name) => {
    const el = form.querySelector(`[name="${name}"]`);
    return el ? el.value.trim() : '';
  };

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

  // simple slugify helper (fallback if slug input is blank)
  const slugify = (s) =>
    s
      .toLowerCase()
      .normalize('NFKD')                // strip diacritics
      .replace(/[\u0300-\u036f]/g, '')  // combining marks
      .replace(/[^a-z0-9]+/g, '-')      // non-alphanum -> dash
      .replace(/(^-|-$)/g, '');         // trim dashes

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    // ensure native HTML5 validation runs
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    // Top-level fields
    const title = get('title');
    let title_slug = get('slug');
    if (!title_slug) title_slug = slugify(title);

    // Helper to read a 3-paragraph section
    const section3 = (key) => ({
      title: get(`content[${key}][title]`),
      'paragraph-1': get(`content[${key}][paragraph-1]`),
      'paragraph-2': get(`content[${key}][paragraph-2]`),
      'paragraph-3': get(`content[${key}][paragraph-3]`),
    });

    const content = {
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
    };

    const payload = {
      // post_id: undefined, // include later when wired to SQL
      title,
      title_slug,
      content,
    };

    alert('Blog post created');
    console.log('[blog_create] Payload to Mongo:', payload);
    console.log(JSON.stringify(payload, null, 2));

    // Redirect to admin index
    window.location.href = '/admin'; // adjust if your admin index path differs
  });
});
