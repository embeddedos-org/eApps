/* ── EoS Marketplace – Dynamic App Loader ── */
(function () {
  'use strict';

  const DATA_URL = 'data/apps.json';
  let allApps = [];
  let categories = [];
  let activeCategory = 'all';
  let searchQuery = '';

  const CATEGORY_ICONS = {
    extensions: '🧩',
    desktop: '🖥️',
    mobile: '📱',
    service: '☁️',
    native: '⚙️',
    web: '🌐'
  };

  const PLATFORM_LABELS = {
    chrome: 'Chrome', firefox: 'Firefox', safari: 'Safari',
    vscode: 'VS Code', jetbrains: 'JetBrains', obsidian: 'Obsidian',
    slack: 'Slack', raycast: 'Raycast', github: 'GitHub',
    'google-workspace': 'Google WS', office365: 'Office 365',
    windows: 'Windows', macos: 'macOS', linux: 'Linux',
    android: 'Android', ios: 'iOS', eos: 'EoS',
    web: 'Web', firebase: 'Firebase', cloud: 'Cloud', docker: 'Docker'
  };

  async function init() {
    try {
      const res = await fetch(DATA_URL);
      const data = await res.json();
      categories = data.categories || [];
      allApps = data.apps || [];
      renderStats(data);
      renderFilters();
      renderGrid();
      bindEvents();
    } catch (err) {
      console.error('Failed to load apps:', err);
      document.getElementById('app-grid').innerHTML =
        '<div class="empty-state"><div class="icon">⚠️</div><p>Failed to load app catalog. Check console for details.</p></div>';
    }
  }

  function renderStats(data) {
    const el = document.getElementById('stats');
    if (!el) return;
    const counts = {};
    allApps.forEach(a => { counts[a.category] = (counts[a.category] || 0) + 1; });
    el.innerHTML = `
      <div class="stat"><div class="stat-number">${allApps.length}</div><div class="stat-label">Total Apps</div></div>
      <div class="stat"><div class="stat-number">${counts.extensions || 0}</div><div class="stat-label">Extensions</div></div>
      <div class="stat"><div class="stat-number">${counts.desktop || 0}</div><div class="stat-label">Desktop</div></div>
      <div class="stat"><div class="stat-number">${counts.mobile || 0}</div><div class="stat-label">Mobile</div></div>
      <div class="stat"><div class="stat-number">${counts.service || 0}</div><div class="stat-label">Services</div></div>
      <div class="stat"><div class="stat-number">${counts.native || 0}</div><div class="stat-label">Native</div></div>
      <div class="stat"><div class="stat-number">${counts.web || 0}</div><div class="stat-label">Web</div></div>
    `;
  }

  function renderFilters() {
    const el = document.getElementById('filters');
    if (!el) return;
    let html = '<button class="pill active" data-cat="all"><span class="pill-icon">📦</span>All</button>';
    categories.forEach(c => {
      html += `<button class="pill" data-cat="${c.id}"><span class="pill-icon">${c.icon}</span>${c.name}</button>`;
    });
    el.innerHTML = html;
  }

  function getDownloadUrl(app) {
    if (app.downloadUrl) return app.downloadUrl;
    if (app.downloads) {
      return app.downloads.windows || app.downloads.android || app.downloads.macos || app.downloads.linux || app.releaseUrl;
    }
    return app.releaseUrl;
  }

  function renderCard(app) {
    const icon = CATEGORY_ICONS[app.category] || '📦';
    const platforms = (app.platform || []).map(p =>
      `<span class="platform-badge">${PLATFORM_LABELS[p] || p}</span>`
    ).join('');
    const tags = (app.tags || []).slice(0, 4).map(t =>
      `<span class="tag">#${t}</span>`
    ).join('');

    const downloadUrl = getDownloadUrl(app);
    let downloadBtn = '';
    if (app.downloads && Object.keys(app.downloads).length > 1) {
      const entries = Object.entries(app.downloads);
      downloadBtn = entries.map(([plat, url]) =>
        `<a href="${url}" class="btn btn-primary" target="_blank">⬇ ${PLATFORM_LABELS[plat] || plat}</a>`
      ).join('');
    } else if (downloadUrl) {
      downloadBtn = `<a href="${downloadUrl}" class="btn btn-primary" target="_blank">⬇ Download</a>`;
    }

    return `
    <div class="card" data-category="${app.category}">
      <div class="card-header">
        <div class="card-icon">${icon}</div>
        <div class="card-title">${app.name}</div>
        <span class="card-version">v${app.version}</span>
      </div>
      <div class="card-desc">${app.description}</div>
      <div class="card-platforms">${platforms}</div>
      <div class="card-tags">${tags}</div>
      <div class="card-actions">
        ${downloadBtn}
        <a href="${app.repo}" class="btn btn-outline" target="_blank">📂 Source</a>
      </div>
    </div>`;
  }

  function renderGrid() {
    const el = document.getElementById('app-grid');
    if (!el) return;
    const filtered = allApps.filter(app => {
      const catMatch = activeCategory === 'all' || app.category === activeCategory;
      const q = searchQuery.toLowerCase();
      const searchMatch = !q ||
        app.name.toLowerCase().includes(q) ||
        app.description.toLowerCase().includes(q) ||
        (app.tags || []).some(t => t.toLowerCase().includes(q));
      return catMatch && searchMatch;
    });

    if (filtered.length === 0) {
      el.innerHTML = '<div class="empty-state"><div class="icon">🔎</div><p>No apps found matching your criteria.</p></div>';
      return;
    }
    el.innerHTML = filtered.map(renderCard).join('');
  }

  function bindEvents() {
    document.getElementById('filters').addEventListener('click', e => {
      const pill = e.target.closest('.pill');
      if (!pill) return;
      document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeCategory = pill.dataset.cat;
      renderGrid();
    });

    const searchInput = document.getElementById('search');
    if (searchInput) {
      searchInput.addEventListener('input', e => {
        searchQuery = e.target.value;
        renderGrid();
      });
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
