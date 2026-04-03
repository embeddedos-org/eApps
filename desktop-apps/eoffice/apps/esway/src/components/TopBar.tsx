interface TopBarProps {
  onPresent: () => void;
  ebotOpen: boolean;
  onToggleEBot: () => void;
  connected: boolean;
}

export default function TopBar({ onPresent, ebotOpen, onToggleEBot, connected }: TopBarProps) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <span className="topbar-logo">🎯</span>
        <span className="topbar-title">eSway</span>
      </div>
      <div className="topbar-right">
        <button className="topbar-action-btn" onClick={onPresent}>▶ Present</button>
        <div className={`topbar-status ${connected ? 'connected' : 'disconnected'}`}>
          <span className="topbar-status-dot" />
          <span>eBot {connected ? 'Online' : 'Offline'}</span>
        </div>
        <button className={`topbar-ebot-btn ${ebotOpen ? 'active' : ''}`} onClick={onToggleEBot}>
          🤖 eBot
        </button>
      </div>
    </div>
  );
}
