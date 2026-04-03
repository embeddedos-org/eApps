interface StatusBarProps {
  fileCount: number;
  totalSize: string;
  connected: boolean;
}

export default function StatusBar({ fileCount, totalSize, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Files: {fileCount}</span>
        <span className="statusbar-item">Total: {totalSize}</span>
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
