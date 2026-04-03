interface TopBarProps {
  boardName: string;
  onBoardNameChange: (name: string) => void;
  ebotSidebarOpen: boolean;
  onToggleEBot: () => void;
  connected: boolean;
  onAddTask: () => void;
}

export default function TopBar({
  boardName,
  onBoardNameChange,
  ebotSidebarOpen,
  onToggleEBot,
  connected,
  onAddTask,
}: TopBarProps) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <span className="topbar-logo">📋</span>
        <span className="topbar-title">ePlanner</span>
      </div>
      <div className="topbar-center">
        <input
          className="topbar-doc-title"
          value={boardName}
          onChange={(e) => onBoardNameChange(e.target.value)}
          placeholder="Board Name"
        />
      </div>
      <div className="topbar-right">
        <div className="topbar-actions">
          <button className="topbar-action-btn" onClick={onAddTask}>
            ＋ Add Task
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
