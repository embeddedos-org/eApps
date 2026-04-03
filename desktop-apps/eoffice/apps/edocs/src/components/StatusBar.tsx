import React from 'react';

interface StatusBarProps {
  wordCount: number;
  charCount: number;
  connected: boolean;
  cursorPosition: { line: number; col: number };
  autoSaveStatus: 'saved' | 'saving' | 'unsaved';
}

export default function StatusBar({
  wordCount,
  charCount,
  connected,
  cursorPosition,
  autoSaveStatus,
}: StatusBarProps) {
  const saveIndicator = {
    saved: { icon: '✓', label: 'All changes saved', className: 'save-saved' },
    saving: { icon: '⟳', label: 'Saving...', className: 'save-saving' },
    unsaved: { icon: '●', label: 'Unsaved changes', className: 'save-unsaved' },
  }[autoSaveStatus];

  return (
    <footer className="statusbar" role="status">
      <div className="statusbar-left">
        <span className="statusbar-item">
          <span className="statusbar-label">Words:</span> {wordCount.toLocaleString()}
        </span>
        <span className="statusbar-divider">|</span>
        <span className="statusbar-item">
          <span className="statusbar-label">Characters:</span> {charCount.toLocaleString()}
        </span>
      </div>

      <div className="statusbar-center">
        <span className="statusbar-item">
          Ln {cursorPosition.line}, Col {cursorPosition.col}
        </span>
      </div>

      <div className="statusbar-right">
        <span className={`statusbar-item ${saveIndicator.className}`}>
          <span className="statusbar-save-icon">{saveIndicator.icon}</span>
          {saveIndicator.label}
        </span>
        <span className="statusbar-divider">|</span>
        <span className={`statusbar-item statusbar-connection ${connected ? 'connected' : 'disconnected'}`}>
          <span className="statusbar-dot" />
          {connected ? 'eBot Online' : 'eBot Offline'}
        </span>
      </div>
    </footer>
  );
}
