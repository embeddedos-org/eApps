interface TopBarProps {
  title: string;
  onTitleChange: (title: string) => void;
  ebotSidebarOpen: boolean;
  onToggleEBot: () => void;
  connected: boolean;
  onNewSheet: () => void;
  onExportCSV: () => void;
  onImportCSV: () => void;
}

export default function TopBar({
  title,
  onTitleChange,
  ebotSidebarOpen,
  onToggleEBot,
  connected,
  onNewSheet,
  onExportCSV,
  onImportCSV,
}: TopBarProps) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <span className="topbar-logo">📊</span>
        <span className="topbar-title">eSheets</span>
      </div>
      <div className="topbar-center">
        <input
          className="topbar-doc-title"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Untitled Spreadsheet"
        />
      </div>
      <div className="topbar-right">
        <div className="topbar-actions">
          <button className="topbar-action-btn" onClick={onNewSheet} title="New Spreadsheet">
            📄 New
          </button>
          <button className="topbar-action-btn" onClick={onImportCSV} title="Import CSV">
            📥 Import
          </button>
          <button className="topbar-action-btn" onClick={onExportCSV} title="Export CSV">
            📤 Export
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
