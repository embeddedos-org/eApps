interface StatusBarProps {
  slideCount: number;
  totalResponses: number;
  connected: boolean;
}

export default function StatusBar({ slideCount, totalResponses, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Slides: {slideCount}</span>
        <span className="statusbar-item">Responses: {totalResponses}</span>
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
