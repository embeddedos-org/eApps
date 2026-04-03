interface StatusBarProps {
  messageCount: number;
  unreadCount: number;
  connected: boolean;
}

export default function StatusBar({ messageCount, unreadCount, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Messages: {messageCount}</span>
        <span className="statusbar-item">Unread: {unreadCount}</span>
      </div>
      <div className="statusbar-right">
        <span className={`statusbar-connection ${connected ? 'connected' : 'disconnected'}`}>
          <span className="statusbar-dot" />
          <span>eBot</span>
        </span>
      </div>
    </div>
  );
}
