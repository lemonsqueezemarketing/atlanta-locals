// static/js/admin_api.js
(function () {
  const el = document.querySelector("[data-admin-list]");
  if (!el) return;

  const resource = el.getAttribute("data-admin-list");
  const perPage  = el.getAttribute("data-per-page") || "10";
  const includeContentAttr = el.getAttribute("data-include-content");
  const includeContent = includeContentAttr == null ? null : includeContentAttr;

  const SCHEMAS = {
    "blog-posts": [
      { key: "post_id",          header: "ID",        get: (p) => p.post_id },
      { key: "title",            header: "Title",     get: (p) => p.title, className: "cell--truncate" },
      { key: "slug",             header: "Slug",      get: (p) => p.slug, className: "cell--truncate" },
      { key: "category_title",   header: "Category",  get: (p) => p.category_title || "" },
      { key: "author_first_name",header: "Author",    get: (p) => p.author_first_name || "" },
      { key: "image",            header: "Image",     get: (p) => p.image || "", className: "cell--truncate" },
      { key: "created_at",       header: "Created",   get: (p) => formatDate(p.created_at) },
      { key: "updated_at",       header: "Updated",   get: (p) => formatDate(p.updated_at) },
      { key: "__actions__",      header: "Actions",   get: renderActions, className: "cell-actions", isHtml: true }
    ],
    "blog-categories": [
      { key: "blog_cat_id", header: "ID", get: (c) => c.blog_cat_id },
      { key: "title",       header: "Title", get: (c) => c.title, className: "cell--truncate" },
      { key: "slug",        header: "Slug", get: (c) => c.slug, className: "cell--truncate" },
      { key: "description", header: "Description", get: (c) => c.description || "", className: "cell--truncate" },
      { key: "created_at",  header: "Created", get: (c) => formatDate(c.created_at) },
      { key: "updated_at",  header: "Updated", get: (c) => formatDate(c.updated_at) },
      { key: "__actions__", header: "Actions", get: renderActions, className: "cell-actions", isHtml: true }
    ],
    "news-posts": [
      { key: "post_id",          header: "ID",        get: (p) => p.post_id },
      { key: "title",            header: "Title",     get: (p) => p.title, className: "cell--truncate" },
      { key: "slug",             header: "Slug",      get: (p) => p.slug, className: "cell--truncate" },
      { key: "category_title",   header: "Category",  get: (p) => p.category_title || "" },
      { key: "author_first_name",header: "Author",    get: (p) => p.author_first_name || "" },
      { key: "image",            header: "Image",     get: (p) => p.image || "", className: "cell--truncate" },
      { key: "created_at",       header: "Created",   get: (p) => formatDate(p.created_at) },
      { key: "updated_at",       header: "Updated",   get: (p) => formatDate(p.updated_at) },
      { key: "__actions__",      header: "Actions",   get: renderActions, className: "cell-actions", isHtml: true }
    ],
    "users": [
      { key: "my_user_id",   header: "ID", get: (u) => u.my_user_id },
      { key: "first_name",   header: "First", get: (u) => u.first_name || "" },
      { key: "last_name",    header: "Last", get: (u) => u.last_name || "" },
      { key: "email",        header: "Email", get: (u) => u.email || "", className: "cell--truncate" },
      { key: "gender",       header: "Gender", get: (u) => u.gender || "" },
      { key: "dob",          header: "DOB", get: (u) => formatDate(u.dob) },
      { key: "zip_code",     header: "ZIP", get: (u) => u.zip_code || "" },
      { key: "city_state",   header: "City/State", get: (u) => u.city_state || "" },
      { key: "image",        header: "Image", get: (u) => u.image || "", className: "cell--truncate" },
      { key: "created_at",   header: "Created", get: (u) => formatDate(u.created_at) },
      { key: "updated_at",   header: "Updated", get: (u) => formatDate(u.updated_at) },
      { key: "__actions__",  header: "Actions", get: renderActions, className: "cell-actions", isHtml: true }
    ],
    "news-main": [
      { key: "news_main_id", header: "ID", get: (r) => r.news_main?.news_main_id },
      { key: "title", header: "Title", get: (r) => r.post?.title || "", className: "cell--truncate" },
      { key: "slug", header: "Slug", get: (r) => r.post?.slug || "", className: "cell--truncate" },
      { key: "category_title", header: "Category", get: (r) => r.post?.category_title || "" },
      { key: "author_first_name", header: "Author", get: (r) => r.post?.author_first_name || "" },
      { key: "image", header: "Image", get: (r) => r.post?.image || "", className: "cell--truncate" },
      { key: "window", header: "Window", get: (r) => {
          const s = formatDate(r.news_main?.start_date);
          const e = formatDate(r.news_main?.end_date);
          return [s, e].filter(Boolean).join(" – ");
        }
      },
      { key: "created_at", header: "Created", get: (r) => formatDate(r.news_main?.created_at) },
      { key: "updated_at", header: "Updated", get: (r) => formatDate(r.news_main?.updated_at) },
      { key: "notes", header: "Notes", get: (r) => r.news_main?.notes || "", className: "cell--truncate" },
      { key: "__actions__", header: "Actions", get: renderActions, className: "cell-actions", isHtml: true }
    ],
    "post-analytics": [
      { key: "post_id", header: "Post ID", get: (a) => a.post_id },
      { key: "views", header: "Views", get: (a) => a.views },
      { key: "likes", header: "Likes", get: (a) => a.likes },
      { key: "comments", header: "Comments", get: (a) => a.comments },
      { key: "shares", header: "Shares", get: (a) => a.shares },
      { key: "created_at", header: "Created", get: (a) => formatDate(a.created_at) },
      { key: "updated_at", header: "Updated", get: (a) => formatDate(a.updated_at) },
      { key: "__actions__", header: "Actions", get: renderActions, className: "cell-actions", isHtml: true }
    ],
    "analytics-most-read-blog": [
      { key: "post_id", header: "ID", get: (r) => r.post_id },
      { key: "title", header: "Title", get: (r) => r.title, className: "cell--truncate" },
      { key: "views", header: "Views", get: (r) => r.views },
      { key: "likes", header: "Likes", get: (r) => r.likes },
      { key: "comments", header: "Comments", get: (r) => r.comments },
      { key: "shares", header: "Shares", get: (r) => r.shares }
    ],
    "analytics-most-read-news": [
      { key: "post_id", header: "ID", get: (r) => r.post_id },
      { key: "title", header: "Title", get: (r) => r.title, className: "cell--truncate" },
      { key: "slug", header: "Slug", get: (r) => r.slug, className: "cell--truncate" },
      { key: "views", header: "Views", get: (r) => r.views },
      { key: "likes", header: "Likes", get: (r) => r.likes },
      { key: "comments", header: "Comments", get: (r) => r.comments },
      { key: "shares", header: "Shares", get: (r) => r.shares },
      { key: "created_at", header: "Created", get: (r) => formatDate(r.created_at) }
    ],
    "analytics-latest-news": [
      { key: "post_id", header: "ID", get: (r) => r.post_id },
      { key: "title", header: "Title", get: (r) => r.title, className: "cell--truncate" },
      { key: "slug", header: "Slug", get: (r) => r.slug, className: "cell--truncate" },
      { key: "views", header: "Views", get: (r) => r.views },
      { key: "likes", header: "Likes", get: (r) => r.likes },
      { key: "comments", header: "Comments", get: (r) => r.comments },
      { key: "shares", header: "Shares", get: (r) => r.shares },
      { key: "created_at", header: "Created", get: (r) => formatDate(r.created_at) }
    ]
  };

  const schema = SCHEMAS[resource];
  if (!schema) {
    console.warn(`[admin_api] No schema defined for resource "${resource}".`);
  }

  const params = new URLSearchParams();
  params.set("per_page", perPage);
  if (includeContent !== null) params.set("include_content", includeContent);
  const url = `/api/v1/${resource}?${params.toString()}`;

  const table = document.querySelector(".admin-table");
  const thead = table ? table.querySelector("thead") : null;
  const tbody = table ? table.querySelector("tbody") : null;

  (async () => {
    try {
      console.log(`[admin_api] Fetching: ${url}`);
      const res = await fetch(url, { method: "GET", headers: { "Accept": "application/json" } });
      if (!res.ok) {
        console.error(`[admin_api] ${resource} fetch failed`, res.status, await res.text());
        return;
      }
      const payload = await res.json();
      console.log(`[admin_api] ${resource} data:`, payload);
      const items = Array.isArray(payload?.items) ? payload.items : [];

      if (schema && thead && thead.dataset.autogen !== "false") {
        thead.innerHTML = `
          <tr>
            ${schema.map(col => {
              const width = col.key === "__actions__" ? ' style="width:160px;"' : "";
              return `<th${width}>${escapeHtml(col.header)}</th>`;
            }).join("")}
          </tr>`;
      }

      if (tbody) {
        if (!items.length) {
          tbody.innerHTML = `
            <tr>
              <td colspan="${schema ? schema.length : 1}" style="text-align:center; color: var(--muted); padding: 18px;">
                No results.
              </td>
            </tr>`;
          return;
        }

        tbody.innerHTML = items.map(item => {
          const tds = (schema || []).map(col => {
            const raw = col.get(item);
            const classAttr = col.className ? ` class="${col.className}"` : "";
            if (col.isHtml) {
              return `<td${classAttr}>${raw}</td>`;
            }
            const text = raw == null ? "" : String(raw);
            const titleAttr = (col.className && col.className.includes("cell--truncate"))
              ? ` title="${escapeHtml(text)}"` : "";
            return `<td${classAttr}${titleAttr}>${escapeHtml(text)}</td>`;
          }).join("");
          return `<tr>${tds}</tr>`;
        }).join("");
      }
    } catch (err) {
      console.error(`[admin_api] ${resource} error:`, err);
    }
  })();

  function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatDate(dt) {
    if (!dt) return "";
    try {
      const d = new Date(dt);
      const pad = (n) => String(n).padStart(2, "0");
      return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    } catch {
      return String(dt);
    }
  }

  function renderActions(row) {
    if (resource === "blog-posts" && row && row.post_id != null) {
      const id = row.post_id;
      // If your public route uses slugs, switch to `/blog/${row.slug}`
      const viewHref = `/blog/${id}`;
      const editHref = `/admin/blog-posts/${id}`;
      const delAction = `/admin/blog-posts/${id}`;

      // Pull CSRF token from a meta tag if present (add in admin_base.html: <meta name="csrf-token" content="{{ csrf_token() }}">)
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";

      return `
        <div class="row-actions" style="display:flex; gap:8px; align-items:center;">
          <a href="${viewHref}" class="btn-link" target="_blank" rel="noopener">View</a>
          <a href="${editHref}" class="btn-link">Edit</a>
          <form method="POST"
                action="${delAction}"
                style="display:inline;"
                onsubmit="return confirm('Delete post #${id}? This cannot be undone.');">
            ${csrf ? `<input type="hidden" name="csrf_token" value="${csrf}">` : ""}
            <input type="hidden" name="action" value="delete">
            <button type="submit" class="btn-link danger" style="background:none;border:none;padding:0;cursor:pointer;">
              Delete
            </button>
          </form>
        </div>
      `;
    }

    // Default for other resources (can be customized later)
    return `
      <a href="#" class="btn-link">View</a>
      <a href="#" class="btn-link">Edit</a>
      <a href="#" class="btn-link danger">Delete</a>
    `;
  }
})();
