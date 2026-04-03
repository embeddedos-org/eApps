interface StatusBarProps {
  tableCount: number;
  rowCount: number;
  connected: boolean;
}

export default function StatusBar({ tableCount, rowCount, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Tables: {tableCount}</span>
        <span className="statusbar-item">Rows: {rowCount}</span>
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
