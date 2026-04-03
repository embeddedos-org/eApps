import React from 'react';

interface FormatState {
  bold: boolean;
  italic: boolean;
  underline: boolean;
  heading: boolean;
  list: boolean;
}

interface ToolbarProps {
  formatState: FormatState;
  onFormat: (command: string) => void;
  onHeading: () => void;
  onUndo: () => void;
  onRedo: () => void;
}

interface ToolbarButton {
  label: string;
  icon: string;
  command: string;
  stateKey?: keyof FormatState;
  action?: () => void;
  title: string;
}

export default function Toolbar({
  formatState,
  onFormat,
  onHeading,
  onUndo,
  onRedo,
}: ToolbarProps) {
  const buttons: ToolbarButton[] = [
    { label: 'Bold', icon: 'B', command: 'bold', stateKey: 'bold', title: 'Bold (Ctrl+B)' },
    { label: 'Italic', icon: 'I', command: 'italic', stateKey: 'italic', title: 'Italic (Ctrl+I)' },
    {
      label: 'Underline',
      icon: 'U',
      command: 'underline',
      stateKey: 'underline',
      title: 'Underline (Ctrl+U)',
    },
    { label: 'Heading', icon: 'H', command: 'heading', stateKey: 'heading', title: 'Heading' },
    {
      label: 'List',
      icon: '☰',
      command: 'insertUnorderedList',
      stateKey: 'list',
      title: 'Bullet List',
    },
  ];

  const historyButtons: ToolbarButton[] = [
    { label: 'Undo', icon: '↩', command: 'undo', action: onUndo, title: 'Undo (Ctrl+Z)' },
    { label: 'Redo', icon: '↪', command: 'redo', action: onRedo, title: 'Redo (Ctrl+Y)' },
  ];

  return (
    <div className="toolbar" role="toolbar" aria-label="Formatting toolbar">
      <div className="toolbar-group">
        {buttons.map((btn) => {
          const isActive = btn.stateKey ? formatState[btn.stateKey] : false;
          return (
            <button
              key={btn.command}
              className={`toolbar-btn ${isActive ? 'active' : ''} ${btn.command === 'bold' ? 'fmt-bold' : ''} ${btn.command === 'italic' ? 'fmt-italic' : ''} ${btn.command === 'underline' ? 'fmt-underline' : ''}`}
              onClick={() => (btn.command === 'heading' ? onHeading() : onFormat(btn.command))}
              title={btn.title}
              aria-pressed={isActive}
              aria-label={btn.label}
            >
              {btn.icon}
            </button>
          );
        })}
      </div>

      <div className="toolbar-divider" />

      <div className="toolbar-group">
        {historyButtons.map((btn) => (
          <button
            key={btn.command}
            className="toolbar-btn"
            onClick={btn.action}
            title={btn.title}
            aria-label={btn.label}
          >
            {btn.icon}
          </button>
        ))}
      </div>
    </div>
  );
}
