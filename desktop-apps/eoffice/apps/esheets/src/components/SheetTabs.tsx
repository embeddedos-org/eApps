import type { Sheet } from '@eoffice/core';

interface SheetTabsProps {
  sheets: Sheet[];
  activeSheetId: string;
  onSwitchSheet: (id: string) => void;
  onAddSheet: () => void;
  onRemoveSheet: (id: string) => void;
  onRenameSheet: (id: string, name: string) => void;
}

export default function SheetTabs({
  sheets,
  activeSheetId,
  onSwitchSheet,
  onAddSheet,
  onRemoveSheet,
}: SheetTabsProps) {
  return (
    <div className="sheet-tabs">
      {sheets.map((sheet) => (
        <div
          key={sheet.id}
          className={`sheet-tab ${sheet.id === activeSheetId ? 'active' : ''}`}
          onClick={() => onSwitchSheet(sheet.id)}
        >
          <span>{sheet.name}</span>
          {sheets.length > 1 && (
            <button
              className="sheet-tab-close"
              onClick={(e) => {
                e.stopPropagation();
                onRemoveSheet(sheet.id);
              }}
              title="Remove sheet"
            >
              ×
            </button>
          )}
        </div>
      ))}
      <button className="sheet-tab-add" onClick={onAddSheet} title="Add sheet">
        +
      </button>
    </div>
  );
}
