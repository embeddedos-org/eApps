import { describe, it, expect } from 'vitest';
import { SpreadsheetModel } from '../spreadsheet-model';

describe('SpreadsheetModel', () => {
  // ── Constructor ──────────────────────────────────────────────────

  describe('Constructor', () => {
    it('creates with one default sheet', () => {
      const model = new SpreadsheetModel();
      expect(model.sheets).toHaveLength(1);
    });

    it('default sheet is named "Sheet 1"', () => {
      const model = new SpreadsheetModel();
      expect(model.sheets[0].name).toBe('Sheet 1');
    });
  });

  // ── Sheet management ─────────────────────────────────────────────

  describe('Sheet management', () => {
    it('addSheet creates a new sheet with given name', () => {
      const model = new SpreadsheetModel();
      const sheet = model.addSheet('Data');
      expect(sheet.name).toBe('Data');
      expect(model.sheets).toHaveLength(2);
    });

    it('removeSheet removes an existing sheet', () => {
      const model = new SpreadsheetModel();
      const sheet2 = model.addSheet('Sheet 2');
      const result = model.removeSheet(sheet2.id);
      expect(result).toBe(true);
      expect(model.sheets).toHaveLength(1);
    });

    it('removeSheet cannot remove the last sheet', () => {
      const model = new SpreadsheetModel();
      const result = model.removeSheet(model.sheets[0].id);
      expect(result).toBe(false);
      expect(model.sheets).toHaveLength(1);
    });

    it('renameSheet updates the sheet name', () => {
      const model = new SpreadsheetModel();
      const id = model.sheets[0].id;
      const result = model.renameSheet(id, 'Renamed');
      expect(result).toBe(true);
      expect(model.getSheet(id)?.name).toBe('Renamed');
    });

    it('getSheet returns undefined for unknown id', () => {
      const model = new SpreadsheetModel();
      expect(model.getSheet('nonexistent')).toBeUndefined();
    });

    it('getActiveSheet returns the active sheet', () => {
      const model = new SpreadsheetModel();
      const active = model.getActiveSheet();
      expect(active.id).toBe(model.activeSheetId);
    });

    it('active sheet switches when removing the active sheet', () => {
      const model = new SpreadsheetModel();
      const sheet2 = model.addSheet('Sheet 2');
      const originalActiveId = model.activeSheetId;
      model.activeSheetId = sheet2.id;
      model.removeSheet(sheet2.id);
      expect(model.activeSheetId).toBe(originalActiveId);
    });
  });

  // ── Cell operations ──────────────────────────────────────────────

  describe('Cell operations', () => {
    it('setCell stores a plain value', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'Hello');
      const cell = model.getCell(sheetId, 0, 0);
      expect(cell?.value).toBe('Hello');
      expect(cell?.formula).toBeUndefined();
    });

    it('setCell stores a formula when value starts with =', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '=SUM(A1:A3)');
      const cell = model.getCell(sheetId, 0, 0);
      expect(cell?.formula).toBe('=SUM(A1:A3)');
    });

    it('getCell returns undefined for empty cell', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      expect(model.getCell(sheetId, 5, 5)).toBeUndefined();
    });

    it('clearCell removes the cell', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'test');
      model.clearCell(sheetId, 0, 0);
      expect(model.getCell(sheetId, 0, 0)).toBeUndefined();
    });

    it('clearRange removes all cells in range', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'A');
      model.setCell(sheetId, 0, 1, 'B');
      model.setCell(sheetId, 1, 0, 'C');
      model.setCell(sheetId, 1, 1, 'D');
      model.clearRange(sheetId, 0, 0, 1, 1);
      expect(model.getCell(sheetId, 0, 0)).toBeUndefined();
      expect(model.getCell(sheetId, 0, 1)).toBeUndefined();
      expect(model.getCell(sheetId, 1, 0)).toBeUndefined();
      expect(model.getCell(sheetId, 1, 1)).toBeUndefined();
    });

    it('setCellFormat applies format to existing cell', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'styled');
      model.setCellFormat(sheetId, 0, 0, { bold: true, color: '#ff0000' });
      const cell = model.getCell(sheetId, 0, 0);
      expect(cell?.format?.bold).toBe(true);
      expect(cell?.format?.color).toBe('#ff0000');
    });
  });

  // ── Cell address ─────────────────────────────────────────────────

  describe('Cell address', () => {
    it('getCellAddress(0, 0) returns "A1"', () => {
      const model = new SpreadsheetModel();
      expect(model.getCellAddress(0, 0)).toBe('A1');
    });

    it('getCellAddress(0, 25) returns "Z1"', () => {
      const model = new SpreadsheetModel();
      expect(model.getCellAddress(0, 25)).toBe('Z1');
    });

    it('getCellAddress(0, 26) returns "AA1"', () => {
      const model = new SpreadsheetModel();
      expect(model.getCellAddress(0, 26)).toBe('AA1');
    });
  });

  // ── Formula engine ───────────────────────────────────────────────

  describe('Formula engine', () => {
    it('SUM(A1:A3) computes sum of range', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '10');
      model.setCell(sheetId, 1, 0, '20');
      model.setCell(sheetId, 2, 0, '30');
      model.setCell(sheetId, 3, 0, '=SUM(A1:A3)');
      const cell = model.getCell(sheetId, 3, 0);
      expect(cell?.computedValue).toBe(60);
    });

    it('AVERAGE computes mean of range', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '10');
      model.setCell(sheetId, 1, 0, '20');
      model.setCell(sheetId, 2, 0, '30');
      model.setCell(sheetId, 3, 0, '=AVERAGE(A1:A3)');
      const cell = model.getCell(sheetId, 3, 0);
      expect(cell?.computedValue).toBe(20);
    });

    it('COUNT counts numeric values in range', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '10');
      model.setCell(sheetId, 1, 0, '20');
      model.setCell(sheetId, 2, 0, 'text');
      model.setCell(sheetId, 3, 0, '=COUNT(A1:A3)');
      const cell = model.getCell(sheetId, 3, 0);
      expect(cell?.computedValue).toBe(2);
    });

    it('MIN returns minimum numeric value', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '10');
      model.setCell(sheetId, 1, 0, '5');
      model.setCell(sheetId, 2, 0, '30');
      model.setCell(sheetId, 3, 0, '=MIN(A1:A3)');
      const cell = model.getCell(sheetId, 3, 0);
      expect(cell?.computedValue).toBe(5);
    });

    it('MAX returns maximum numeric value', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '10');
      model.setCell(sheetId, 1, 0, '5');
      model.setCell(sheetId, 2, 0, '30');
      model.setCell(sheetId, 3, 0, '=MAX(A1:A3)');
      const cell = model.getCell(sheetId, 3, 0);
      expect(cell?.computedValue).toBe(30);
    });

    it('IF returns true branch when condition is met', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '10');
      model.setCell(sheetId, 1, 0, '=IF(A1>5, "yes", "no")');
      const cell = model.getCell(sheetId, 1, 0);
      expect(cell?.computedValue).toBe('yes');
    });

    it('IF returns false branch when condition is not met', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '3');
      model.setCell(sheetId, 1, 0, '=IF(A1>5, "yes", "no")');
      const cell = model.getCell(sheetId, 1, 0);
      expect(cell?.computedValue).toBe('no');
    });

    it('CONCATENATE joins string arguments', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '=CONCATENATE("hello", " ", "world")');
      const cell = model.getCell(sheetId, 0, 0);
      expect(cell?.computedValue).toBe('hello world');
    });

    it('cell reference resolves to referenced cell value', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '42');
      model.setCell(sheetId, 1, 0, '=A1');
      const cell = model.getCell(sheetId, 1, 0);
      expect(cell?.computedValue).toBe(42);
    });

    it('simple arithmetic =A1+B1', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '15');
      model.setCell(sheetId, 0, 1, '25');
      model.setCell(sheetId, 0, 2, '=A1+B1');
      const cell = model.getCell(sheetId, 0, 2);
      expect(cell?.computedValue).toBe(40);
    });

    it('detects circular references', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, '=B1');
      model.setCell(sheetId, 0, 1, '=A1');
      const cellA = model.getCell(sheetId, 0, 0);
      const cellB = model.getCell(sheetId, 0, 1);
      expect(cellA?.computedValue).toBe('#CIRCULAR!');
      expect(cellB?.computedValue).toBe('#CIRCULAR!');
    });
  });

  // ── CSV ──────────────────────────────────────────────────────────

  describe('CSV', () => {
    it('exportCSV produces comma-separated output', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'Name');
      model.setCell(sheetId, 0, 1, 'Age');
      model.setCell(sheetId, 1, 0, 'Alice');
      model.setCell(sheetId, 1, 1, '30');
      const csv = model.exportCSV(sheetId);
      expect(csv).toBe('Name,Age\nAlice,30');
    });

    it('exportCSV returns empty string for empty sheet', () => {
      const model = new SpreadsheetModel();
      const csv = model.exportCSV(model.sheets[0].id);
      expect(csv).toBe('');
    });

    it('importCSV populates cells from CSV string', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.importCSV('X,Y\n1,2', sheetId);
      expect(model.getCell(sheetId, 0, 0)?.value).toBe('X');
      expect(model.getCell(sheetId, 0, 1)?.value).toBe('Y');
      expect(model.getCell(sheetId, 1, 0)?.value).toBe('1');
      expect(model.getCell(sheetId, 1, 1)?.value).toBe('2');
    });

    it('importCSV handles quoted fields with commas', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.importCSV('"Last, First",Age\n"Doe, Jane",25', sheetId);
      expect(model.getCell(sheetId, 0, 0)?.value).toBe('Last, First');
      expect(model.getCell(sheetId, 1, 0)?.value).toBe('Doe, Jane');
    });
  });

  // ── JSON serialization ──────────────────────────────────────────

  describe('JSON serialization', () => {
    it('toJSON returns serializable object with sheets and activeSheetId', () => {
      const model = new SpreadsheetModel();
      const json = model.toJSON() as Record<string, unknown>;
      expect(json).toHaveProperty('sheets');
      expect(json).toHaveProperty('activeSheetId');
      expect(Array.isArray(json.sheets)).toBe(true);
    });

    it('fromJSON reconstructs the model from JSON', () => {
      const model = new SpreadsheetModel();
      model.addSheet('Extra');
      const json = model.toJSON() as any;
      const restored = SpreadsheetModel.fromJSON(json);
      expect(restored.sheets).toHaveLength(2);
      expect(restored.sheets[1].name).toBe('Extra');
    });

    it('roundtrip preserves cell data', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'test');
      model.setCell(sheetId, 0, 1, '42');
      const json = model.toJSON() as any;
      const restored = SpreadsheetModel.fromJSON(json);
      const restoredSheetId = restored.sheets[0].id;
      expect(restored.getCell(restoredSheetId, 0, 0)?.value).toBe('test');
      expect(restored.getCell(restoredSheetId, 0, 1)?.value).toBe('42');
    });
  });

  // ── Statistics ───────────────────────────────────────────────────

  describe('Statistics', () => {
    it('getCellCount returns number of non-empty cells', () => {
      const model = new SpreadsheetModel();
      const sheetId = model.sheets[0].id;
      model.setCell(sheetId, 0, 0, 'A');
      model.setCell(sheetId, 0, 1, 'B');
      model.setCell(sheetId, 1, 0, 'C');
      expect(model.getCellCount()).toBe(3);
    });

    it('getSheetCount returns number of sheets', () => {
      const model = new SpreadsheetModel();
      expect(model.getSheetCount()).toBe(1);
      model.addSheet('Sheet 2');
      expect(model.getSheetCount()).toBe(2);
    });
  });
});
