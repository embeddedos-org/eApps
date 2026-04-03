interface ToolbarProps {
  onInsertText: () => void;
  onInsertShape: () => void;
  onDeleteElement: () => void;
  hasSelection: boolean;
  theme: string;
  onThemeChange: (theme: string) => void;
}

const THEMES = ['Default', 'Dark', 'Ocean', 'Sunset', 'Forest'];

export default function Toolbar({
  onInsertText,
  onInsertShape,
  onDeleteElement,
  hasSelection,
  theme,
  onThemeChange,
}: ToolbarProps) {
  return (
    <div className="toolbar">
      <div className="toolbar-group">
        <button className="toolbar-btn" onClick={onInsertText} title="Insert Text">
          T Text
        </button>
        <button className="toolbar-btn" onClick={onInsertShape} title="Insert Shape">
          ■ Shape
        </button>
        <button className="toolbar-btn" title="Insert Image">
          🖼 Image
        </button>
      </div>
      <div className="toolbar-divider" />
      <div className="toolbar-group">
        <button
          className="toolbar-btn"
          onClick={onDeleteElement}
          disabled={!hasSelection}
          title="Delete Element"
        >
          🗑 Delete
        </button>
      </div>
      <div className="toolbar-divider" />
      <div className="toolbar-group">
        <select
          className="toolbar-select"
          value={theme}
          onChange={(e) => onThemeChange(e.target.value)}
        >
          {THEMES.map((t) => (
            <option key={t} value={t}>{t} Theme</option>
          ))}
        </select>
      </div>
    </div>
  );
}
