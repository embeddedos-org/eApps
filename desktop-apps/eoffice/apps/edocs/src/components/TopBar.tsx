import React from 'react';

interface TopBarProps {
  title: string;
  onTitleChange: (title: string) => void;
  ebotSidebarOpen: boolean;
  onToggleEBot: () => void;
  connected: boolean;
}

export default function TopBar({
  title,
  onTitleChange,
  ebotSidebarOpen,
  onToggleEBot,
  connected,
}: TopBarProps) {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="topbar-logo">📝</span>
        <h1 className="topbar-title">eDocs</h1>
      </div>

      <div className="topbar-center">
        <input
          className="topbar-doc-title"
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Untitled Document"
          aria-label="Document title"
        />
      </div>

      <div className="topbar-right">
        <div className={`topbar-status ${connected ? 'connected' : 'disconnected'}`}>
          <span className="topbar-status-dot" />
          <span className="topbar-status-label">
            {connected ? 'eBot Connected' : 'eBot Offline'}
          </span>
        </div>
        <button
          className={`topbar-ebot-btn ${ebotSidebarOpen ? 'active' : ''}`}
          onClick={onToggleEBot}
          title="Toggle eBot AI Assistant"
          aria-label="Toggle eBot AI sidebar"
        >
          <span className="ebot-icon">⚡</span>
          <span className="ebot-label">eBot</span>
        </button>
      </div>
    </header>
  );
}
