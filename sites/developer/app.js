/* ============================================================
   arifOS MCP Developer Documentation — App JavaScript
   Sidebar, copy buttons, search, mobile menu, tabs, TOC
   ============================================================ */

(function () {
  'use strict';

  // --- Copy-to-clipboard for code blocks ---
  function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrapper = btn.closest('.code-block-wrapper');
        var code = wrapper ? wrapper.querySelector('code') : null;
        if (!code) return;
        var text = code.textContent;
        navigator.clipboard.writeText(text).then(function () {
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          setTimeout(function () {
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
          }, 2000);
        }).catch(function () {
          // Fallback
          var ta = document.createElement('textarea');
          ta.value = text;
          ta.style.position = 'fixed';
          ta.style.opacity = '0';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          setTimeout(function () {
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
          }, 2000);
        });
      });
    });
  }

  // --- Sidebar collapsible groups ---
  function initSidebarGroups() {
    document.querySelectorAll('.sidebar-group-title').forEach(function (title) {
      title.addEventListener('click', function () {
        var group = title.closest('.sidebar-group');
        if (group) group.classList.toggle('collapsed');
      });
    });
  }

  // --- Sidebar search filter ---
  function initSidebarSearch() {
    var input = document.querySelector('.sidebar-search input');
    if (!input) return;
    input.addEventListener('input', function () {
      var query = input.value.toLowerCase().trim();
      document.querySelectorAll('.sidebar-group').forEach(function (group) {
        var links = group.querySelectorAll('.sidebar-link');
        var anyVisible = false;
        links.forEach(function (link) {
          var text = link.textContent.toLowerCase();
          if (!query || text.indexOf(query) !== -1) {
            link.style.display = '';
            anyVisible = true;
          } else {
            link.style.display = 'none';
          }
        });
        // Show group if any link matches
        if (query) {
          group.classList.remove('collapsed');
          group.style.display = anyVisible ? '' : 'none';
        } else {
          group.style.display = '';
        }
      });
    });
  }

  // --- Sidebar active state ---
  function initSidebarActive() {
    var path = window.location.pathname;
    var hash = window.location.hash;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
      var href = link.getAttribute('href');
      if (!href) return;
      // Match by page path
      if (path.indexOf(href.replace(/^\.\.\//, '/').replace(/^\.\//, '/')) !== -1) {
        link.classList.add('active');
        // Ensure parent group is expanded
        var group = link.closest('.sidebar-group');
        if (group) group.classList.remove('collapsed');
      }
      // Match by hash on same page
      if (hash && href.indexOf(hash) !== -1) {
        document.querySelectorAll('.sidebar-link.active').forEach(function (a) {
          a.classList.remove('active');
        });
        link.classList.add('active');
      }
    });
  }

  // --- Mobile hamburger menu ---
  function initMobileMenu() {
    var hamburger = document.querySelector('.nav-hamburger');
    var sidebar = document.querySelector('.sidebar');
    var overlay = document.querySelector('.sidebar-overlay');
    if (!hamburger || !sidebar) return;

    hamburger.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active');
    });

    if (overlay) {
      overlay.addEventListener('click', function () {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
      });
    }

    // Close sidebar on link click (mobile)
    sidebar.querySelectorAll('.sidebar-link').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 768) {
          sidebar.classList.remove('open');
          if (overlay) overlay.classList.remove('active');
        }
      });
    });
  }

  // --- Integration Tabs ---
  function initTabs() {
    document.querySelectorAll('.tab-container').forEach(function (container) {
      var btns = container.querySelectorAll('.tab-btn');
      var panels = container.querySelectorAll('.tab-panel');
      btns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var target = btn.getAttribute('data-tab');
          btns.forEach(function (b) { b.classList.remove('active'); });
          panels.forEach(function (p) { p.classList.remove('active'); });
          btn.classList.add('active');
          var panel = container.querySelector('#' + target);
          if (panel) panel.classList.add('active');
        });
      });
    });
  }

  // --- Right-side TOC scroll tracking ---
  function initTocTracking() {
    var tocLinks = document.querySelectorAll('.toc a');
    if (!tocLinks.length) return;

    var headings = [];
    tocLinks.forEach(function (link) {
      var href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        var el = document.getElementById(href.slice(1));
        if (el) headings.push({ el: el, link: link });
      }
    });

    if (!headings.length) return;

    function update() {
      var scrollY = window.scrollY + 120;
      var current = headings[0];
      for (var i = 0; i < headings.length; i++) {
        if (headings[i].el.offsetTop <= scrollY) {
          current = headings[i];
        }
      }
      tocLinks.forEach(function (l) { l.classList.remove('active'); });
      if (current) current.link.classList.add('active');
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  // --- Smooth scroll for anchor links ---
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var target = document.getElementById(a.getAttribute('href').slice(1));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          history.replaceState(null, '', a.getAttribute('href'));
        }
      });
    });
  }

  // --- Initialize all on DOMContentLoaded ---
  document.addEventListener('DOMContentLoaded', function () {
    initCopyButtons();
    initSidebarGroups();
    initSidebarSearch();
    initSidebarActive();
    initMobileMenu();
    initTabs();
    initTocTracking();
    initSmoothScroll();

    // Re-run Prism if loaded
    if (window.Prism) {
      Prism.highlightAll();
    }
  });
})();
