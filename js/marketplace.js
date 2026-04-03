/* ── EoS Marketplace v2.0 – Dynamic App Loader ── */
(function () {
  'use strict';

  const DATA_URL = 'data/apps.json';
  let allApps = [];
  let categories = [];
  let activeCategory = 'all';
  let searchQuery = '';

  const CATEGORY_ICONS = {
    'browser-ext': '🌐',
    'ide-ext': '🛠️',
    'mobile-android': '📱',
    'mobile-ios': '🍎',
    desktop: '🖥️',
    native: '⚙️',
    service: '☁️',
    'os-images': '💿'
  };

  const PLATFORM_LABELS = {
    chrome: 'Chrome', firefox: 'Firefox', safari: 'Safari',
    edge: 'Edge', opera: 'Opera', brave: 'Brave',
    vscode: 'VS Code', jetbrains: 'JetBrains', obsidian: 'Obsidian',
    sublime: 'Sublime', neovim: 'Neovim',
    slack: 'Slack', raycast: 'Raycast', github: 'GitHub',
    'google-workspace': 'Google WS', office365: 'Office 365',
    windows: 'Windows', macos: 'macOS', linux: 'Linux',
    'windows-x64': 'Win x64', 'windows-arm64': 'Win ARM',
    'macos-intel': 'macOS Intel', 'macos-apple-silicon': 'macOS M-series',
    'linux-x64': 'Linux x64', 'linux-arm64': 'Linux ARM',
    android: 'Android', 'android-tv': 'Android TV',
    'android-tablet': 'Tablet', 'wear-os': 'Wear OS',
    ios: 'iOS', ipados: 'iPadOS', 'apple-tv': 'Apple TV',
    eos: 'EoS', freebsd: 'FreeBSD',
    web: 'Web', pwa: 'PWA', wasm: 'WASM',
    firebase: 'Firebase', cloud: 'Cloud', docker: 'Docker',
    x86_64: 'x86_64', arm64: 'ARM64', riscv: 'RISC-V',
    iso: 'ISO', img: 'IMG',
    stm32: 'STM32', esp32: 'ESP32', rpi: 'RPi',
    firmware: 'Firmware',
    virtualbox: 'VirtualBox', vmware: 'VMware',
    qemu: 'QEMU', ova: 'OVA', vmdk: 'VMDK', qcow2: 'qcow2'
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
    let html = `<div class="stat"><div class="stat-number">${allApps.length}</div><div class="stat-label">Total Apps</div></div>`;
    categories.forEach(c => {
      html += `<div class="stat"><div class="stat-number">${counts[c.id] || 0}</div><div class="stat-label">${c.name}</div></div>`;
    });
    el.innerHTML = html;
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
      const keys = Object.keys(app.downloads);
      return app.downloads[keys[0]] || app.releaseUrl;
    }
    return app.releaseUrl;
  }

  function renderCard(app) {
    const icon = CATEGORY_ICONS[app.category] || '📦';
    const platforms = (app.platform || []).slice(0, 6).map(p =>
      `<span class="platform-badge">${PLATFORM_LABELS[p] || p}</span>`
    ).join('');
    const extraPlatforms = (app.platform || []).length > 6
      ? `<span class="platform-badge">+${app.platform.length - 6}</span>` : '';
    const tags = (app.tags || []).slice(0, 4).map(t =>
      `<span class="tag">#${t}</span>`
    ).join('');

    const downloadUrl = getDownloadUrl(app);
    let downloadBtn = '';
    if (app.downloads && Object.keys(app.downloads).length > 1) {
      const entries = Object.entries(app.downloads).slice(0, 3);
      downloadBtn = entries.map(([plat, url]) =>
        `<a href="${url}" class="btn btn-primary" target="_blank">⬇ ${PLATFORM_LABELS[plat] || plat}</a>`
      ).join('');
      if (Object.keys(app.downloads).length > 3) {
        downloadBtn += `<a href="${app.releaseUrl}" class="btn btn-outline" target="_blank">+${Object.keys(app.downloads).length - 3} more</a>`;
      }
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
      <div class="card-platforms">${platforms}${extraPlatforms}</div>
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
        (app.tags || []).some(t => t.toLowerCase().includes(q)) ||
        (app.platform || []).some(p => p.toLowerCase().includes(q));
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
