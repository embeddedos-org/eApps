import { useState, useCallback, useMemo } from 'react';
import type { Cell, CellFormat } from '@eoffice/core';
import { SpreadsheetModel } from '@eoffice/core';

interface SpreadsheetState {
  model: SpreadsheetModel;
  activeCell: { row: number; col: number } | null;
  selection: { startRow: number; startCol: number; endRow: number; endCol: number } | null;
  editingCell: { row: number; col: number } | null;
  editValue: string;
  revision: number;
}

export function useSpreadsheet() {
  const [state, setState] = useState<SpreadsheetState>(() => ({
    model: new SpreadsheetModel(),
    activeCell: null,
    selection: null,
    editingCell: null,
    editValue: '',
    revision: 0,
  }));



  const setCell = useCallback((row: number, col: number, value: string) => {
    setState((s) => {
      s.model.setCell(s.model.activeSheetId, row, col, value);
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const selectCell = useCallback((row: number, col: number) => {
    setState((s) => {
      const cell = s.model.getCell(s.model.activeSheetId, row, col);
      const displayValue = cell?.formula ? `=${cell.formula}` : cell?.value || '';
      return {
        ...s,
        activeCell: { row, col },
        selection: { startRow: row, startCol: col, endRow: row, endCol: col },
        editingCell: null,
        editValue: displayValue,
      };
    });
  }, []);

  const startEditing = useCallback((row: number, col: number) => {
    setState((s) => {
      const cell = s.model.getCell(s.model.activeSheetId, row, col);
      const editVal = cell?.formula ? `=${cell.formula}` : cell?.value || '';
      return {
        ...s,
        editingCell: { row, col },
        editValue: editVal,
      };
    });
  }, []);

  const commitEdit = useCallback(() => {
    setState((s) => {
      if (!s.editingCell) return s;
      s.model.setCell(s.model.activeSheetId, s.editingCell.row, s.editingCell.col, s.editValue);
      return {
        ...s,
        editingCell: null,
        revision: s.revision + 1,
      };
    });
  }, []);

  const cancelEdit = useCallback(() => {
    setState((s) => ({ ...s, editingCell: null, editValue: '' }));
  }, []);

  const setEditValue = useCallback((value: string) => {
    setState((s) => ({ ...s, editValue: value }));
  }, []);

  const setCellFormat = useCallback((row: number, col: number, format: CellFormat) => {
    setState((s) => {
      s.model.setCellFormat(s.model.activeSheetId, row, col, format);
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const addSheet = useCallback((name: string) => {
    setState((s) => {
      const sheet = s.model.addSheet(name);
      s.model.activeSheetId = sheet.id;
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const removeSheet = useCallback((id: string) => {
    setState((s) => {
      s.model.removeSheet(id);
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const switchSheet = useCallback((id: string) => {
    setState((s) => ({
      ...s,
      activeCell: null,
      editingCell: null,
      editValue: '',
    }));
    setState((s) => {
      s.model.activeSheetId = id;
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const renameSheet = useCallback((id: string, name: string) => {
    setState((s) => {
      s.model.renameSheet(id, name);
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const exportCSV = useCallback((): string => {
    return state.model.exportCSV();
  }, [state.model]);

  const importCSV = useCallback((csv: string) => {
    setState((s) => {
      s.model.importCSV(csv);
      return { ...s, revision: s.revision + 1 };
    });
  }, []);

  const newSpreadsheet = useCallback(() => {
    setState({
      model: new SpreadsheetModel(),
      activeCell: null,
      selection: null,
      editingCell: null,
      editValue: '',
      revision: 0,
    });
  }, []);

  const getCell = useCallback((row: number, col: number): Cell | undefined => {
    return state.model.getCell(state.model.activeSheetId, row, col);
  }, [state.model, state.revision]);

  const getCellAddress = useCallback((row: number, col: number): string => {
    return state.model.getCellAddress(row, col);
  }, [state.model]);

  const activeCellFormat = useMemo((): CellFormat => {
    if (!state.activeCell) return {};
    const cell = state.model.getCell(
      state.model.activeSheetId,
      state.activeCell.row,
      state.activeCell.col,
    );
    return cell?.format || {};
  }, [state.activeCell, state.model, state.revision]);

  const cellAddress = useMemo(() => {
    if (!state.activeCell) return '';
    return state.model.getCellAddress(state.activeCell.row, state.activeCell.col);
  }, [state.activeCell, state.model]);

  const selectionStats = useMemo(() => {
    if (!state.selection) return null;
    const sheet = state.model.getActiveSheet();
    const values: number[] = [];
    for (let r = state.selection.startRow; r <= state.selection.endRow; r++) {
      for (let c = state.selection.startCol; c <= state.selection.endCol; c++) {
        const cell = sheet.cells[`${r}:${c}`];
        if (cell) {
          const v = cell.computedValue !== undefined ? cell.computedValue : cell.value;
          const num = Number(v);
          if (!isNaN(num) && v !== '') values.push(num);
        }
      }
    }
    if (values.length === 0) return null;
    const sum = values.reduce((a, b) => a + b, 0);
    return {
      sum: Math.round(sum * 1000) / 1000,
      avg: Math.round((sum / values.length) * 1000) / 1000,
      count: values.length,
    };
  }, [state.selection, state.model, state.revision]);

  return {
    model: state.model,
    sheets: state.model.sheets,
    activeSheetId: state.model.activeSheetId,
    activeCell: state.activeCell,
    selection: state.selection,
    editingCell: state.editingCell,
    editValue: state.editValue,
    cellAddress,
    activeCellFormat,
    selectionStats,
    revision: state.revision,
    setCell,
    selectCell,
    startEditing,
    commitEdit,
    cancelEdit,
    setEditValue,
    setCellFormat,
    addSheet,
    removeSheet,
    switchSheet,
    renameSheet,
    exportCSV,
    importCSV,
    newSpreadsheet,
    getCell,
    getCellAddress,
  };
}
