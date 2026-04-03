import React from 'react';
import { useCallback, useRef, useEffect } from 'react';
import type { Cell } from '@eoffice/core';

const NUM_ROWS = 50;
const NUM_COLS = 26;

interface SpreadsheetGridProps {
  activeCell: { row: number; col: number } | null;
  editingCell: { row: number; col: number } | null;
  editValue: string;
  revision: number;
  getCell: (row: number, col: number) => Cell | undefined;
  getCellAddress: (row: number, col: number) => string;
  onSelectCell: (row: number, col: number) => void;
  onStartEditing: (row: number, col: number) => void;
  onEditValueChange: (value: string) => void;
  onCommitEdit: () => void;
  onCancelEdit: () => void;
}

function colToLetter(col: number): string {
  let result = '';
  let c = col;
  do {
    result = String.fromCharCode(65 + (c % 26)) + result;
    c = Math.floor(c / 26) - 1;
  } while (c >= 0);
  return result;
}

function getCellDisplayValue(cell: Cell | undefined): string {
  if (!cell) return '';
  if (cell.computedValue !== undefined) return String(cell.computedValue);
  return cell.value;
}

function isErrorValue(value: string): boolean {
  return value.startsWith('#') && value.endsWith('!');
}

export default function SpreadsheetGrid({
  activeCell,
  editingCell,
  editValue,
  revision: _revision,
  getCell,
  onSelectCell,
  onStartEditing,
  onEditValueChange,
  onCommitEdit,
  onCancelEdit,
}: SpreadsheetGridProps) {
  const editInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingCell && editInputRef.current) {
      editInputRef.current.focus();
    }
  }, [editingCell]);

  const handleCellClick = useCallback(
    (row: number, col: number) => {
      if (editingCell) {
        onCommitEdit();
      }
      onSelectCell(row, col);
    },
    [editingCell, onCommitEdit, onSelectCell],
  );

  const handleCellDoubleClick = useCallback(
    (row: number, col: number) => {
      onStartEditing(row, col);
    },
    [onStartEditing],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!activeCell) return;

      if (editingCell) {
        if (e.key === 'Enter') {
          e.preventDefault();
          onCommitEdit();
          onSelectCell(activeCell.row + 1, activeCell.col);
        } else if (e.key === 'Escape') {
          e.preventDefault();
          onCancelEdit();
        } else if (e.key === 'Tab') {
          e.preventDefault();
          onCommitEdit();
          onSelectCell(activeCell.row, activeCell.col + (e.shiftKey ? -1 : 1));
        }
        return;
      }

      const { row, col } = activeCell;
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          if (row > 0) onSelectCell(row - 1, col);
          break;
        case 'ArrowDown':
        case 'Enter':
          e.preventDefault();
          if (row < NUM_ROWS - 1) onSelectCell(row + 1, col);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          if (col > 0) onSelectCell(row, col - 1);
          break;
        case 'ArrowRight':
        case 'Tab':
          e.preventDefault();
          if (col < NUM_COLS - 1) onSelectCell(row, col + 1);
          break;
        case 'Delete':
        case 'Backspace':
          e.preventDefault();
          onStartEditing(row, col);
          onEditValueChange('');
          break;
        case 'F2':
          e.preventDefault();
          onStartEditing(row, col);
          break;
        default:
          if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
            onStartEditing(row, col);
            onEditValueChange(e.key);
          }
      }
    },
    [activeCell, editingCell, onSelectCell, onStartEditing, onCommitEdit, onCancelEdit, onEditValueChange],
  );

  return (
    <div
      className="grid-container"
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      <table className="grid-table">
        <thead>
          <tr>
            <th className="grid-corner" />
            {Array.from({ length: NUM_COLS }, (_, c) => (
              <th
                key={c}
                className={`grid-col-header ${activeCell?.col === c ? 'selected' : ''}`}
              >
                {colToLetter(c)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: NUM_ROWS }, (_, r) => (
            <tr key={r}>
              <td className={`grid-row-header ${activeCell?.row === r ? 'selected' : ''}`}>
                {r + 1}
              </td>
              {Array.from({ length: NUM_COLS }, (_, c) => {
                const isActive = activeCell?.row === r && activeCell?.col === c;
                const isEditing = editingCell?.row === r && editingCell?.col === c;
                const cell = getCell(r, c);
                const displayValue = getCellDisplayValue(cell);
                const align = cell?.format?.align || (cell && !isNaN(Number(displayValue)) && displayValue !== '' ? 'right' : 'left');
                const isError = isErrorValue(displayValue);

                const cellStyle: React.CSSProperties = {};
                if (cell?.format?.bold) cellStyle.fontWeight = 700;
                if (cell?.format?.italic) cellStyle.fontStyle = 'italic';
                if (cell?.format?.underline) cellStyle.textDecoration = 'underline';
                if (cell?.format?.color) cellStyle.color = cell.format.color;
                if (cell?.format?.backgroundColor) cellStyle.backgroundColor = cell.format.backgroundColor;

                return (
                  <td
                    key={c}
                    className={[
                      'grid-cell',
                      isActive ? 'active' : '',
                      isEditing ? 'editing' : '',
                      `align-${align}`,
                      isError ? 'cell-error' : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    style={cellStyle}
                    onClick={() => handleCellClick(r, c)}
                    onDoubleClick={() => handleCellDoubleClick(r, c)}
                  >
                    {isEditing ? (
                      <input
                        ref={editInputRef}
                        className="grid-cell-input"
                        value={editValue}
                        onChange={(e) => onEditValueChange(e.target.value)}
                        onBlur={onCommitEdit}
                      />
                    ) : (
                      displayValue
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
