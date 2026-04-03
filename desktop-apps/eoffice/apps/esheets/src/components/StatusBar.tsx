interface StatusBarProps {
  cellCount: number;
  sheetCount: number;
  connected: boolean;
  selectionStats: { sum: number; avg: number; count: number } | null;
}

export default function StatusBar({
  cellCount,
  sheetCount,
  connected,
  selectionStats,
}: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">
          Cells: {cellCount}
        </span>
        <span className="statusbar-item">
          Sheets: {sheetCount}
        </span>
      </div>
      <div className="statusbar-right">
        {selectionStats && (
          <>
            <span className="statusbar-item">
              Sum: {selectionStats.sum}
            </span>
            <span className="statusbar-item">
              Avg: {selectionStats.avg}
            </span>
            <span className="statusbar-item">
              Count: {selectionStats.count}
            </span>
          </>
        )}
        <span className={`statusbar-connection ${connected ? 'connected' : 'disconnected'}`}>
          <span className="statusbar-dot" />
          <span>eBot</span>
        </span>
      </div>
    </div>
  );
}
