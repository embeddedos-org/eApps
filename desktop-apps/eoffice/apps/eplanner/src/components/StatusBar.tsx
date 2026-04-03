interface StatusBarProps {
  total: number;
  todo: number;
  inProgress: number;
  done: number;
  connected: boolean;
}

export default function StatusBar({ total, todo, inProgress, done, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Total: {total}</span>
        <span className="statusbar-item">📝 {todo}</span>
        <span className="statusbar-item">🔄 {inProgress}</span>
        <span className="statusbar-item">✅ {done}</span>
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
