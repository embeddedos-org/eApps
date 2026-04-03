import type { CSSProperties } from 'react';
import { useState } from 'react';
import { APP_REGISTRY, VERSION } from '@eoffice/core';
import type { AppCategory, EOfficeApp } from '@eoffice/core';

const PORT_MAP: Record<string, number> = {
  edocs: 5173,
  enotes: 5174,
  esheets: 5175,
  eslides: 5176,
  email: 5177,
  edb: 5178,
  edrive: 5179,
  econnect: 5180,
  eforms: 5181,
  esway: 5182,
  eplanner: 5183,
};

const CATEGORY_LABELS: Record<string, string> = {
  all: 'All',
  documents: 'Documents',
  communication: 'Communication',
  storage: 'Storage',
  collaboration: 'Collaboration',
};

const CATEGORY_COLORS: Record<string, string> = {
  documents: '#6366f1',
  communication: '#0ea5e9',
  storage: '#10b981',
  collaboration: '#a855f7',
};

export default function App() {
  const [filter, setFilter] = useState<'all' | AppCategory>('all');
  const filtered = filter === 'all'
    ? APP_REGISTRY
    : APP_REGISTRY.filter((app: EOfficeApp) => app.category === filter);

  return (
    <div className="launcher">
      <header className="header">
        <div className="header-content">
          <div className="brand">
            <span className="brand-icon">??</span>
            <div>
              <h1 className="brand-title">eOffice Suite</h1>
              <span className="brand-sub">Powered by eBot AI</span>
            </div>
          </div>
          <div className="header-badge">v{VERSION}</div>
        </div>
      </header>

      <nav className="filter-bar">
        {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
          <button
            key={key}
            className={`filter-btn ${filter === key ? 'active' : ''}`}
            onClick={() => setFilter(key as 'all' | AppCategory)}
          >
            {label}
            {key !== 'all' && (
              <span className="filter-count">
                {APP_REGISTRY.filter((a: EOfficeApp) => a.category === key).length}
              </span>
            )}
          </button>
        ))}
      </nav>

      <main className="grid">
        {filtered.map((app: EOfficeApp) => {
          const port = PORT_MAP[app.id] ?? 5170;
          const url = `http://localhost:${port}`;
          const catColor = CATEGORY_COLORS[app.category] ?? '#6366f1';
          return (
            <a
              key={app.id}
              href={url}
              className="card"
              target="_blank"
              rel="noopener noreferrer"
              style={{ '--accent': catColor } as CSSProperties}
            >
              <div className="card-icon">{app.icon}</div>
              <div className="card-body">
                <h2 className="card-name">{app.name}</h2>
                <p className="card-desc">{app.description}</p>
                <div className="card-meta">
                  <span
                    className="card-category"
                    style={{ background: catColor }}
                  >
                    {app.category}
                  </span>
                  <span className="card-version">v{app.version}</span>
                </div>
              </div>
            </a>
          );
        })}
      </main>

      <footer className="footer">
        <span>eOffice Suite v{VERSION}</span>
        <span className="footer-sep"></span>
        <span>{APP_REGISTRY.length} apps</span>
        <span className="footer-sep"></span>
        <span>eBot AI-Powered</span>
      </footer>
    </div>
  );
}
