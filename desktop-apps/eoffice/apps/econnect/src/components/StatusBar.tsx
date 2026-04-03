interface StatusBarProps {
  channelCount: number;
  messageCount: number;
  connected: boolean;
}

export default function StatusBar({ channelCount, messageCount, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Channels: {channelCount}</span>
        <span className="statusbar-item">Messages: {messageCount}</span>
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
