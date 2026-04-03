interface TopBarProps {
  title: string;
  onTitleChange: (title: string) => void;
  ebotSidebarOpen: boolean;
  onToggleEBot: () => void;
  connected: boolean;
  onPresent: () => void;
}

export default function TopBar({
  title,
  onTitleChange,
  ebotSidebarOpen,
  onToggleEBot,
  connected,
  onPresent,
}: TopBarProps) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <span className="topbar-logo">📽️</span>
        <span className="topbar-title">eSlides</span>
      </div>
      <div className="topbar-center">
        <input
          className="topbar-doc-title"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Untitled Presentation"
        />
      </div>
      <div className="topbar-right">
        <div className="topbar-actions">
          <button className="topbar-action-btn" onClick={onPresent} title="Present">
            ▶ Present
          </button>
        </div>
        <div className={`topbar-status ${connected ? 'connected' : 'disconnected'}`}>
          <span className="topbar-status-dot" />
          <span>eBot {connected ? 'Online' : 'Offline'}</span>
        </div>
        <button
          className={`topbar-ebot-btn ${ebotSidebarOpen ? 'active' : ''}`}
          onClick={onToggleEBot}
        >
          🤖 eBot
        </button>
      </div>
    </div>
  );
}
