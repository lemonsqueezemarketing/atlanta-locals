// static/js/admin.js
console.log('admin.js loaded');

(function () {
  const INIT = () => {
    const sidebar   = document.querySelector('.admin-sidebar');
    const toggleBtns = document.querySelectorAll('.hamburger-btn'); // support multiple placements
    const OPEN_CLASS = 'is-open';       // applied to sidebar
    const BODY_OPEN  = 'sidebar-open';  // applied to body for scrolling/backdrop
    const BACKDROP_CLASS = 'sidebar-backdrop';

    if (!sidebar) {
      console.warn('[admin.js] .admin-sidebar not found — toggle disabled');
      return;
    }
    if (!toggleBtns.length) {
      console.warn('[admin.js] .hamburger-btn not found — toggle button missing');
      return;
    }

    // Ensure backdrop exists
    let backdrop = document.querySelector(`.${BACKDROP_CLASS}`);
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = BACKDROP_CLASS;
      document.body.appendChild(backdrop);
    }

    const openSidebar = () => {
      sidebar.classList.add(OPEN_CLASS);
      document.body.classList.add(BODY_OPEN);
      toggleBtns.forEach(btn => btn.setAttribute('aria-expanded', 'true'));
      backdrop.style.display = 'block';
    };

    const closeSidebar = () => {
      sidebar.classList.remove(OPEN_CLASS);
      document.body.classList.remove(BODY_OPEN);
      toggleBtns.forEach(btn => btn.setAttribute('aria-expanded', 'false'));
      backdrop.style.display = 'none';
    };

    const toggleSidebar = () => {
      if (sidebar.classList.contains(OPEN_CLASS)) closeSidebar();
      else openSidebar();
    };

    // Wire up all toggle buttons
    toggleBtns.forEach(btn => {
      // ARIA wiring
      btn.setAttribute('aria-controls', 'admin-sidebar');
      btn.setAttribute('aria-expanded', 'false');

      btn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleSidebar();
      });
    });

    // Click backdrop to close
    backdrop.addEventListener('click', closeSidebar);

    // Escape to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSidebar();
    });

    // Close when resizing to desktop
    const MQ = window.matchMedia('(min-width: 768px)');
    const onResize = () => {
      if (MQ.matches) closeSidebar();
    };
    if (MQ.addEventListener) MQ.addEventListener('change', onResize);
    else MQ.addListener(onResize); // Safari fallback

    // Ensure sidebar has an id for aria-controls
    if (!sidebar.id) sidebar.id = 'admin-sidebar';

    console.log(`[admin.js] initialized: ${toggleBtns.length} toggle button(s)`);
  };

  // Wait until DOM is fully parsed so partials are present
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', INIT);
  } else {
    INIT();
  }
})();
