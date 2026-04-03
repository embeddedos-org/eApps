import { useState } from 'react';
import type { TableDef } from '../hooks/useDatabase';

interface TableViewProps {
  table: TableDef | null;
  onInsertRow: (tableId: string) => void;
  onUpdateRow: (tableId: string, rowIdx: number, col: string, value: string) => void;
  onDeleteRow: (tableId: string, rowIdx: number) => void;
}

export default function TableView({ table, onInsertRow, onUpdateRow, onDeleteRow }: TableViewProps) {
  const [editCell, setEditCell] = useState<{ row: number; col: string } | null>(null);
  const [editValue, setEditValue] = useState('');

  if (!table) {
    return (
      <div className="table-empty">
        <div className="table-empty-icon">🗄️</div>
        <div>Select a table or create a new one</div>
      </div>
    );
  }

  const startEdit = (rowIdx: number, col: string, value: string) => {
    setEditCell({ row: rowIdx, col });
    setEditValue(value);
  };

  const commitEdit = () => {
    if (editCell) {
      onUpdateRow(table.id, editCell.row, editCell.col, editValue);
      setEditCell(null);
    }
  };

  return (
    <div className="table-view">
      <div className="table-view-toolbar">
        <button onClick={() => onInsertRow(table.id)}>➕ Add Row</button>
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
          {table.name} — {table.rows.length} rows, {table.columns.length} columns
        </span>
      </div>
      <div className="table-grid-container">
        <table className="table-grid">
          <thead>
            <tr>
              <th className="row-actions">#</th>
              {table.columns.map((c) => (
                <th key={c.name}>{c.name} <span style={{ fontWeight: 400, opacity: 0.6 }}>({c.type})</span></th>
              ))}
              <th className="row-actions" />
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, ri) => (
              <tr key={ri}>
                <td className="row-actions" style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>{ri + 1}</td>
                {table.columns.map((c) => (
                  <td key={c.name} onDoubleClick={() => startEdit(ri, c.name, row[c.name] || '')}>
                    {editCell?.row === ri && editCell?.col === c.name ? (
                      <input
                        autoFocus
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={commitEdit}
                        onKeyDown={(e) => { if (e.key === 'Enter') commitEdit(); if (e.key === 'Escape') setEditCell(null); }}
                      />
                    ) : (
                      row[c.name] || ''
                    )}
                  </td>
                ))}
                <td className="row-actions">
                  <button className="row-delete-btn" onClick={() => onDeleteRow(table.id, ri)} title="Delete row">✕</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
