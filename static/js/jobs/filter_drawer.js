// static/js/jobs/filter_drawer.js
(function () {
  function debug(...args) {
    try { console.debug('[filter_drawer]', ...args); } catch (e) {}
  }

  function init() {
    debug('init start');

    // find elements (robust selectors)
    const toggleBtn = document.querySelector('#filter-toggle-btn');
    const drawer = document.querySelector('#filter-drawer');
    const closeBtn = document.querySelector('#filter-close-btn');

    if (!toggleBtn) {
      debug('toggle button (#filter-toggle-btn) NOT found');
      return;
    }
    debug('toggle button found');

    if (!drawer) {
      debug('drawer (#filter-drawer) NOT found — creating fallback');
      // Create inline fallback drawer so toggle still shows something
      const fallback = document.createElement('div');
      fallback.id = 'filter-drawer';
      fallback.className = 'filter-drawer';
      fallback.innerHTML = '<div style="padding:18px">Filters unavailable. Reload the page.</div>';
      // Insert right after the top-search-bar if possible
      const topBar = document.querySelector('.top-search-bar');
      if (topBar && topBar.parentNode) topBar.parentNode.insertBefore(fallback, topBar.nextSibling);
      else document.body.appendChild(fallback);
    }

    const D = document.querySelector('#filter-drawer'); // re-query in case created
    if (!D) {
      debug('Failed to create/find drawer after fallback. Aborting.');
      return;
    }
    debug('drawer now present');

    // Ensure drawer is hidden initially
    D.style.display = D.classList.contains('open') ? 'block' : 'none';
    D.setAttribute('aria-hidden', D.classList.contains('open') ? 'false' : 'true');

    function openDrawer() {
      debug('openDrawer');
      D.classList.add('open');
      D.style.display = 'block';
      D.setAttribute('aria-hidden', 'false');
      // trap focus to first focusable element if exists
      const focusable = D.querySelector('select, input, button, a');
      if (focusable) focusable.focus();
    }

    function closeDrawer() {
      debug('closeDrawer');
      D.classList.remove('open');
      D.style.display = 'none';
      D.setAttribute('aria-hidden', 'true');
      toggleBtn.focus();
    }

    function toggle() {
      if (D.classList.contains('open')) closeDrawer();
      else openDrawer();
    }

    // Attach click handler
    toggleBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      debug('toggleBtn clicked');
      toggle();
    });

    // close button if present
    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        debug('closeBtn clicked');
        closeDrawer();
      });
    } else {
      debug('closeBtn not found (optional)');
    }

    // click outside -> close
    document.addEventListener('click', function (e) {
      // if drawer not open nothing to do
      if (!D.classList.contains('open')) return;
      // if click inside drawer or on toggleBtn, ignore
      if (D.contains(e.target) || toggleBtn.contains(e.target)) return;
      debug('click outside drawer -> close');
      closeDrawer();
    });

    // prevent clicks inside the drawer from bubbling up (helps some UIs)
    D.addEventListener('click', function (e) {
      e.stopPropagation();
    });

    // ESC closes
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && D.classList.contains('open')) {
        debug('Escape pressed -> close');
        closeDrawer();
      }
    });

    debug('initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
