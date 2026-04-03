import type { CellFormat } from '@eoffice/core';

interface ToolbarProps {
  cellFormat: CellFormat;
  onFormatChange: (format: Partial<CellFormat>) => void;
}

export default function Toolbar({ cellFormat, onFormatChange }: ToolbarProps) {
  return (
    <div className="toolbar">
      <div className="toolbar-group">
        <button
          className={`toolbar-btn fmt-bold ${cellFormat.bold ? 'active' : ''}`}
          onClick={() => onFormatChange({ bold: !cellFormat.bold })}
          title="Bold (Ctrl+B)"
        >
          B
        </button>
        <button
          className={`toolbar-btn fmt-italic ${cellFormat.italic ? 'active' : ''}`}
          onClick={() => onFormatChange({ italic: !cellFormat.italic })}
          title="Italic (Ctrl+I)"
        >
          I
        </button>
        <button
          className={`toolbar-btn fmt-underline ${cellFormat.underline ? 'active' : ''}`}
          onClick={() => onFormatChange({ underline: !cellFormat.underline })}
          title="Underline (Ctrl+U)"
        >
          U
        </button>
      </div>
      <div className="toolbar-divider" />
      <div className="toolbar-group">
        <button
          className={`toolbar-btn ${cellFormat.align === 'left' ? 'active' : ''}`}
          onClick={() => onFormatChange({ align: 'left' })}
          title="Align Left"
        >
          ≡
        </button>
        <button
          className={`toolbar-btn ${cellFormat.align === 'center' ? 'active' : ''}`}
          onClick={() => onFormatChange({ align: 'center' })}
          title="Align Center"
        >
          ≡
        </button>
        <button
          className={`toolbar-btn ${cellFormat.align === 'right' ? 'active' : ''}`}
          onClick={() => onFormatChange({ align: 'right' })}
          title="Align Right"
        >
          ≡
        </button>
      </div>
      <div className="toolbar-divider" />
      <div className="toolbar-group">
        <select
          className="toolbar-select"
          value={cellFormat.numberFormat || 'general'}
          onChange={(e) =>
            onFormatChange({
              numberFormat: e.target.value as CellFormat['numberFormat'],
            })
          }
          title="Number Format"
        >
          <option value="general">General</option>
          <option value="number">Number</option>
          <option value="currency">Currency</option>
          <option value="percent">Percent</option>
          <option value="date">Date</option>
        </select>
      </div>
      <div className="toolbar-divider" />
      <div className="toolbar-group">
        <label title="Text Color" style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <span style={{ fontSize: 13, marginRight: 2, color: cellFormat.color || 'var(--text-secondary)' }}>A</span>
          <input
            type="color"
            value={cellFormat.color || '#000000'}
            onChange={(e) => onFormatChange({ color: e.target.value })}
            style={{ width: 16, height: 16, border: 'none', cursor: 'pointer', padding: 0 }}
          />
        </label>
        <label title="Background Color" style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', marginLeft: 4 }}>
          <span style={{ fontSize: 13, marginRight: 2 }}>🎨</span>
          <input
            type="color"
            value={cellFormat.backgroundColor || '#ffffff'}
            onChange={(e) => onFormatChange({ backgroundColor: e.target.value })}
            style={{ width: 16, height: 16, border: 'none', cursor: 'pointer', padding: 0 }}
          />
        </label>
      </div>
    </div>
  );
}
