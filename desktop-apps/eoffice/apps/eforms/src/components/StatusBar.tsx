interface StatusBarProps {
  fieldCount: number;
  connected: boolean;
  previewMode: boolean;
}

export default function StatusBar({ fieldCount, connected, previewMode }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Fields: {fieldCount}</span>
        <span className="statusbar-item">{previewMode ? '👁 Preview' : '✏️ Edit'}</span>
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
