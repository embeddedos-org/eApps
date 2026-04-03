import type { Folder } from '../hooks/useMailbox';

interface TopBarProps {
  currentFolder: Folder;
  onFolderChange: (folder: Folder) => void;
  onCompose: () => void;
  ebotSidebarOpen: boolean;
  onToggleEBot: () => void;
  connected: boolean;
  unreadCount: number;
}

const FOLDERS: { id: Folder; label: string; emoji: string }[] = [
  { id: 'inbox', label: 'Inbox', emoji: '📥' },
  { id: 'sent', label: 'Sent', emoji: '📤' },
  { id: 'drafts', label: 'Drafts', emoji: '📝' },
];

export default function TopBar({
  currentFolder,
  onFolderChange,
  onCompose,
  ebotSidebarOpen,
  onToggleEBot,
  connected,
  unreadCount,
}: TopBarProps) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <span className="topbar-logo">✉️</span>
        <span className="topbar-title">eMail</span>
      </div>
      <div className="topbar-center">
        {FOLDERS.map((f) => (
          <button
            key={f.id}
            className={`topbar-folder-btn ${currentFolder === f.id ? 'active' : ''}`}
            onClick={() => onFolderChange(f.id)}
          >
            {f.emoji} {f.label}
            {f.id === 'inbox' && unreadCount > 0 && ` (${unreadCount})`}
          </button>
        ))}
      </div>
      <div className="topbar-right">
        <div className="topbar-actions">
          <button className="topbar-action-btn" onClick={onCompose}>
            ✏️ Compose
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
