import type { TableDef } from '../hooks/useDatabase';

interface TableListProps {
  tables: TableDef[];
  selectedTableId: string | null;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDrop: (id: string) => void;
}

export default function TableList({ tables, selectedTableId, onSelect, onCreate, onDrop }: TableListProps) {
  return (
    <div className="table-list">
      <div className="table-list-header">
        <span>Tables</span>
        <button className="table-list-add" onClick={onCreate} title="New table">+</button>
      </div>
      <div className="table-list-items">
        {tables.map((t) => (
          <div
            key={t.id}
            className={`table-list-item ${t.id === selectedTableId ? 'active' : ''}`}
            onClick={() => onSelect(t.id)}
          >
            <span className="table-list-item-name">
              <span>🗃️</span>
              <span>{t.name}</span>
            </span>
            <button
              className="table-list-delete"
              onClick={(e) => { e.stopPropagation(); onDrop(t.id); }}
              title="Drop table"
            >✕</button>
          </div>
        ))}
        {tables.length === 0 && (
          <div style={{ padding: '16px 12px', color: 'var(--text-tertiary)', fontSize: 12, textAlign: 'center' }}>
            No tables yet
          </div>
        )}
      </div>
    </div>
  );
}
