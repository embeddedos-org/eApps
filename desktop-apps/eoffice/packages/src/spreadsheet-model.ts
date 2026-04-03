import type { Cell, Sheet, CellFormat } from './types';
import { generateId } from './utils';

export class SpreadsheetModel {
  public sheets: Sheet[];
  public activeSheetId: string;

  constructor() {
    const defaultSheet = this.createSheet('Sheet 1');
    this.sheets = [defaultSheet];
    this.activeSheetId = defaultSheet.id;
  }

  // ── Sheet management ──────────────────────────────────────────────

  private createSheet(name: string): Sheet {
    return {
      id: generateId(),
      name,
      cells: {},
      columnWidths: {},
      rowHeights: {},
    };
  }

  addSheet(name: string): Sheet {
    const sheet = this.createSheet(name);
    this.sheets.push(sheet);
    return sheet;
  }

  removeSheet(id: string): boolean {
    if (this.sheets.length <= 1) return false;
    const index = this.sheets.findIndex((s) => s.id === id);
    if (index === -1) return false;
    this.sheets.splice(index, 1);
    if (this.activeSheetId === id) {
      this.activeSheetId = this.sheets[0].id;
    }
    return true;
  }

  renameSheet(id: string, name: string): boolean {
    const sheet = this.getSheet(id);
    if (!sheet) return false;
    sheet.name = name;
    return true;
  }

  getSheet(id: string): Sheet | undefined {
    return this.sheets.find((s) => s.id === id);
  }

  getActiveSheet(): Sheet {
    return this.sheets.find((s) => s.id === this.activeSheetId)!;
  }

  // ── Cell operations ───────────────────────────────────────────────

  setCell(sheetId: string, row: number, col: number, value: string): void {
    const sheet = this.getSheet(sheetId);
    if (!sheet) return;

    const key = this.cellKey(row, col);
    const existing = sheet.cells[key];

    if (value.startsWith('=')) {
      sheet.cells[key] = {
        value,
        formula: value,
        computedValue: undefined,
        format: existing?.format,
      };
    } else {
      sheet.cells[key] = {
        value,
        formula: undefined,
        computedValue: undefined,
        format: existing?.format,
      };
    }

    this.recalculate();
  }

  getCell(sheetId: string, row: number, col: number): Cell | undefined {
    const sheet = this.getSheet(sheetId);
    if (!sheet) return undefined;
    return sheet.cells[this.cellKey(row, col)];
  }

  clearCell(sheetId: string, row: number, col: number): void {
    const sheet = this.getSheet(sheetId);
    if (!sheet) return;
    delete sheet.cells[this.cellKey(row, col)];
    this.recalculate();
  }

  clearRange(
    sheetId: string,
    startRow: number,
    startCol: number,
    endRow: number,
    endCol: number,
  ): void {
    const sheet = this.getSheet(sheetId);
    if (!sheet) return;

    for (let r = startRow; r <= endRow; r++) {
      for (let c = startCol; c <= endCol; c++) {
        delete sheet.cells[this.cellKey(r, c)];
      }
    }
    this.recalculate();
  }

  setCellFormat(
    sheetId: string,
    row: number,
    col: number,
    format: CellFormat,
  ): void {
    const sheet = this.getSheet(sheetId);
    if (!sheet) return;

    const key = this.cellKey(row, col);
    const cell = sheet.cells[key];
    if (cell) {
      cell.format = { ...cell.format, ...format };
    } else {
      sheet.cells[key] = { value: '', format };
    }
  }

  // ── Formula engine ────────────────────────────────────────────────

  private recalculate(): void {
    const formulaCells: {
      sheetId: string;
      key: string;
      cell: Cell;
    }[] = [];

    for (const sheet of this.sheets) {
      for (const [key, cell] of Object.entries(sheet.cells)) {
        if (cell.formula) {
          formulaCells.push({ sheetId: sheet.id, key, cell });
        }
      }
    }

    if (formulaCells.length === 0) return;

    const adjacency = new Map<string, string[]>();
    const cellLookup = new Map<
      string,
      { sheetId: string; key: string; cell: Cell }
    >();

    for (const entry of formulaCells) {
      const nodeId = `${entry.sheetId}:${entry.key}`;
      cellLookup.set(nodeId, entry);
      const deps = this.extractDependencies(entry.cell.formula!, entry.sheetId);
      adjacency.set(nodeId, deps);
    }

    const visited = new Set<string>();
    const recStack = new Set<string>();
    const sorted: string[] = [];
    const circular = new Set<string>();

    const dfs = (node: string): boolean => {
      visited.add(node);
      recStack.add(node);

      const neighbors = adjacency.get(node) || [];
      for (const dep of neighbors) {
        if (!visited.has(dep)) {
          if (dfs(dep)) {
            circular.add(node);
            return true;
          }
        } else if (recStack.has(dep)) {
          circular.add(node);
          circular.add(dep);
          return true;
        }
      }

      recStack.delete(node);
      sorted.push(node);
      return false;
    };

    for (const nodeId of adjacency.keys()) {
      if (!visited.has(nodeId)) {
        dfs(nodeId);
      }
    }

    for (const nodeId of circular) {
      const circEntry = cellLookup.get(nodeId);
      if (circEntry) {
        circEntry.cell.computedValue = '#CIRCULAR!';
      }
    }
    for (const nodeId of sorted) {
      const entry = cellLookup.get(nodeId);
      if (!entry) continue;

      if (circular.has(nodeId)) {
        entry.cell.computedValue = '#CIRCULAR!';
      } else {
        entry.cell.computedValue = this.evaluateFormula(
          entry.cell.formula!,
          entry.sheetId,
        );
      }
    }
  }

  private extractDependencies(formula: string, sheetId: string): string[] {
    const deps: string[] = [];
    const expr = formula.startsWith('=') ? formula.slice(1) : formula;

    const crossSheetRange = /(\w+)!([A-Z]+\d+):([A-Z]+\d+)/gi;
    let match: RegExpExecArray | null;
    match = crossSheetRange.exec(expr);
    while (match !== null) {
      const targetSheet = this.sheets.find((s) => s.name === match![1]);
      if (targetSheet) {
        const start = this.parseCellRef(match[2]);
        const end = this.parseCellRef(match[3]);
        if (start && end) {
          for (let r = start.row; r <= end.row; r++) {
            for (let c = start.col; c <= end.col; c++) {
              deps.push(`${targetSheet.id}:${this.cellKey(r, c)}`);
            }
          }
        }
      }
      match = crossSheetRange.exec(expr);
    }

    const crossSheetRef = /(\w+)!([A-Z]+\d+)(?!:)/gi;
    match = crossSheetRef.exec(expr);
    while (match !== null) {
      const targetSheet = this.sheets.find((s) => s.name === match![1]);
      if (targetSheet) {
        const ref = this.parseCellRef(match[2]);
        if (ref) {
          deps.push(`${targetSheet.id}:${this.cellKey(ref.row, ref.col)}`);
        }
      }
      match = crossSheetRef.exec(expr);
    }

    const rangePattern = /(?<!\w!)([A-Z]+\d+):([A-Z]+\d+)/gi;
    match = rangePattern.exec(expr);
    while (match !== null) {
      const start = this.parseCellRef(match[1]);
      const end = this.parseCellRef(match[2]);
      if (start && end) {
        for (let r = start.row; r <= end.row; r++) {
          for (let c = start.col; c <= end.col; c++) {
            deps.push(`${sheetId}:${this.cellKey(r, c)}`);
          }
        }
      }
      match = rangePattern.exec(expr);
    }

    const singleRef = /(?<!\w!)(?<![A-Z])([A-Z]+\d+)(?!:)(?!\d)/gi;
    match = singleRef.exec(expr);
    while (match !== null) {
      const ref = this.parseCellRef(match[1]);
      if (ref) {
        deps.push(`${sheetId}:${this.cellKey(ref.row, ref.col)}`);
      }
      match = singleRef.exec(expr);
    }

    return deps;
  }

  private evaluateFormula(formula: string, sheetId: string): string | number {
    try {
      const expr = formula.startsWith('=') ? formula.slice(1).trim() : formula.trim();
      return this.evalExpression(expr, sheetId);
    } catch {
      return '#ERROR!';
    }
  }

  private evalExpression(expr: string, sheetId: string): string | number {
    const funcMatch = expr.match(/^([A-Z]+)\((.+)\)$/i);
    if (funcMatch) {
      const funcName = funcMatch[1].toUpperCase();
      const argsStr = funcMatch[2];
      return this.evalFunction(funcName, argsStr, sheetId);
    }

    const ifMatch = expr.match(/^IF\((.+)\)$/i);
    if (ifMatch) {
      return this.evalFunction('IF', ifMatch[1], sheetId);
    }

    return this.evalSimpleExpression(expr, sheetId);
  }

  private evalFunction(
    name: string,
    argsStr: string,
    sheetId: string,
  ): string | number {
    switch (name) {
      case 'SUM': {
        const values = this.resolveRangeOrArgs(argsStr, sheetId);
        return values.reduce<number>((sum, v) => sum + (typeof v === 'number' ? v : 0), 0);
      }
      case 'AVG':
      case 'AVERAGE': {
        const values = this.resolveRangeOrArgs(argsStr, sheetId);
        const nums = values.filter((v): v is number => typeof v === 'number');
        if (nums.length === 0) return 0;
        return nums.reduce((sum, v) => sum + v, 0) / nums.length;
      }
      case 'COUNT': {
        const values = this.resolveRangeOrArgs(argsStr, sheetId);
        return values.filter((v) => typeof v === 'number').length;
      }
      case 'MIN': {
        const values = this.resolveRangeOrArgs(argsStr, sheetId);
        const nums = values.filter((v): v is number => typeof v === 'number');
        if (nums.length === 0) return 0;
        return Math.min(...nums);
      }
      case 'MAX': {
        const values = this.resolveRangeOrArgs(argsStr, sheetId);
        const nums = values.filter((v): v is number => typeof v === 'number');
        if (nums.length === 0) return 0;
        return Math.max(...nums);
      }
      case 'IF': {
        const parts = this.splitTopLevelCommas(argsStr);
        if (parts.length < 3) return '#ERROR!';
        const condition = this.evalCondition(parts[0].trim(), sheetId);
        const trueBranch = parts[1].trim();
        const falseBranch = parts[2].trim();
        const branch = condition ? trueBranch : falseBranch;
        return this.resolveValue(branch, sheetId);
      }
      case 'CONCATENATE': {
        const parts = this.splitTopLevelCommas(argsStr);
        return parts
          .map((p) => {
            const v = this.resolveValue(p.trim(), sheetId);
            return String(v);
          })
          .join('');
      }
      default:
        return '#ERROR!';
    }
  }

  private splitTopLevelCommas(str: string): string[] {
    const parts: string[] = [];
    let depth = 0;
    let current = '';
    for (const ch of str) {
      if (ch === '(') depth++;
      else if (ch === ')') depth--;
      if (ch === ',' && depth === 0) {
        parts.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
    parts.push(current);
    return parts;
  }

  private resolveRangeOrArgs(
    argsStr: string,
    sheetId: string,
  ): (string | number)[] {
    const parts = this.splitTopLevelCommas(argsStr);
    const values: (string | number)[] = [];

    for (const part of parts) {
      const trimmed = part.trim();

      const crossSheetRange = trimmed.match(/^(\w+)!([A-Z]+\d+):([A-Z]+\d+)$/i);
      if (crossSheetRange) {
        const targetSheet = this.sheets.find((s) => s.name === crossSheetRange[1]);
        if (!targetSheet) {
          values.push('#REF!' as string);
          continue;
        }
        values.push(
          ...this.expandRange(crossSheetRange[2], crossSheetRange[3], targetSheet.id),
        );
        continue;
      }

      const rangeMatch = trimmed.match(/^([A-Z]+\d+):([A-Z]+\d+)$/i);
      if (rangeMatch) {
        values.push(...this.expandRange(rangeMatch[1], rangeMatch[2], sheetId));
        continue;
      }

      values.push(this.resolveValue(trimmed, sheetId));
    }

    return values;
  }

  private expandRange(
    startRef: string,
    endRef: string,
    sheetId: string,
  ): (string | number)[] {
    const start = this.parseCellRef(startRef);
    const end = this.parseCellRef(endRef);
    if (!start || !end) return [];

    const sheet = this.getSheet(sheetId);
    if (!sheet) return [];

    const values: (string | number)[] = [];
    for (let r = start.row; r <= end.row; r++) {
      for (let c = start.col; c <= end.col; c++) {
        const cell = sheet.cells[this.cellKey(r, c)];
        if (cell) {
          const v =
            cell.computedValue !== undefined ? cell.computedValue : cell.value;
          const num = Number(v);
          values.push(isNaN(num) ? String(v) : num);
        }
      }
    }
    return values;
  }

  private resolveValue(token: string, sheetId: string): string | number {
    if (
      (token.startsWith('"') && token.endsWith('"')) ||
      (token.startsWith("'") && token.endsWith("'"))
    ) {
      return token.slice(1, -1);
    }

    const num = Number(token);
    if (!isNaN(num) && token.length > 0) return num;

    const crossRef = token.match(/^(\w+)!([A-Z]+\d+)$/i);
    if (crossRef) {
      const targetSheet = this.sheets.find((s) => s.name === crossRef[1]);
      if (!targetSheet) return '#REF!';
      const ref = this.parseCellRef(crossRef[2]);
      if (!ref) return '#REF!';
      const cell = targetSheet.cells[this.cellKey(ref.row, ref.col)];
      if (!cell) return 0;
      const v =
        cell.computedValue !== undefined ? cell.computedValue : cell.value;
      const n = Number(v);
      return isNaN(n) ? String(v) : n;
    }

    const ref = this.parseCellRef(token);
    if (ref) {
      const sheet = this.getSheet(sheetId);
      if (!sheet) return '#REF!';
      const cell = sheet.cells[this.cellKey(ref.row, ref.col)];
      if (!cell) return 0;
      const v =
        cell.computedValue !== undefined ? cell.computedValue : cell.value;
      const n = Number(v);
      return isNaN(n) ? String(v) : n;
    }

    return token;
  }

  private evalCondition(condition: string, sheetId: string): boolean {
    const operators = ['>=', '<=', '!=', '<>', '>', '<', '='] as const;

    for (const op of operators) {
      const idx = condition.indexOf(op);
      if (idx !== -1) {
        const left = this.resolveValue(
          condition.slice(0, idx).trim(),
          sheetId,
        );
        const right = this.resolveValue(
          condition.slice(idx + op.length).trim(),
          sheetId,
        );
        const l = typeof left === 'number' ? left : Number(left);
        const r = typeof right === 'number' ? right : Number(right);

        switch (op) {
          case '>':
            return l > r;
          case '<':
            return l < r;
          case '>=':
            return l >= r;
          case '<=':
            return l <= r;
          case '!=':
          case '<>':
            return l !== r;
          case '=':
            return l === r;
        }
      }
    }
    return false;
  }

  private evalSimpleExpression(expr: string, sheetId: string): string | number {
    const ref = this.parseCellRef(expr.trim());
    if (ref) {
      return this.resolveValue(expr.trim(), sheetId);
    }

    const num = Number(expr.trim());
    if (!isNaN(num) && expr.trim().length > 0) return num;

    const addSub = expr.match(/^(.+?)([+-])([^+-]+)$/);
    if (addSub) {
      const left = this.evalSimpleExpression(addSub[1], sheetId);
      const right = this.evalSimpleExpression(addSub[3], sheetId);
      const l = typeof left === 'number' ? left : Number(left);
      const r = typeof right === 'number' ? right : Number(right);
      if (isNaN(l) || isNaN(r)) return '#ERROR!';
      return addSub[2] === '+' ? l + r : l - r;
    }

    const mulDiv = expr.match(/^(.+?)([*/])([^*/]+)$/);
    if (mulDiv) {
      const left = this.evalSimpleExpression(mulDiv[1], sheetId);
      const right = this.evalSimpleExpression(mulDiv[3], sheetId);
      const l = typeof left === 'number' ? left : Number(left);
      const r = typeof right === 'number' ? right : Number(right);
      if (isNaN(l) || isNaN(r)) return '#ERROR!';
      if (mulDiv[2] === '/' && r === 0) return '#ERROR!';
      return mulDiv[2] === '*' ? l * r : l / r;
    }

    return this.resolveValue(expr.trim(), sheetId);
  }

  // ── Helper methods ────────────────────────────────────────────────

  private cellKey(row: number, col: number): string {
    return `${row}:${col}`;
  }

  private parseCellRef(ref: string): { col: number; row: number } | null {
    const match = ref.match(/^([A-Z]+)(\d+)$/i);
    if (!match) return null;
    const col = this.colLetterToIndex(match[1].toUpperCase());
    const row = parseInt(match[2], 10) - 1;
    if (row < 0) return null;
    return { col, row };
  }

  private colToLetter(col: number): string {
    let result = '';
    let c = col;
    while (c >= 0) {
      result = String.fromCharCode((c % 26) + 65) + result;
      c = Math.floor(c / 26) - 1;
    }
    return result;
  }

  private colLetterToIndex(letters: string): number {
    let result = 0;
    for (let i = 0; i < letters.length; i++) {
      result = result * 26 + (letters.charCodeAt(i) - 64);
    }
    return result - 1;
  }

  getCellAddress(row: number, col: number): string {
    return `${this.colToLetter(col)}${row + 1}`;
  }

  // ── Statistics ────────────────────────────────────────────────────

  getCellCount(): number {
    let count = 0;
    for (const sheet of this.sheets) {
      for (const cell of Object.values(sheet.cells)) {
        if (cell.value !== '' || cell.formula) {
          count++;
        }
      }
    }
    return count;
  }

  getSheetCount(): number {
    return this.sheets.length;
  }

  // ── CSV ───────────────────────────────────────────────────────────

  exportCSV(sheetId?: string): string {
    const sheet = sheetId ? this.getSheet(sheetId) : this.getActiveSheet();
    if (!sheet) return '';

    let maxRow = -1;
    let maxCol = -1;
    for (const key of Object.keys(sheet.cells)) {
      const [r, c] = key.split(':').map(Number);
      if (r > maxRow) maxRow = r;
      if (c > maxCol) maxCol = c;
    }

    if (maxRow < 0 || maxCol < 0) return '';

    const rows: string[] = [];
    for (let r = 0; r <= maxRow; r++) {
      const cols: string[] = [];
      for (let c = 0; c <= maxCol; c++) {
        const cell = sheet.cells[this.cellKey(r, c)];
        if (cell) {
          const val =
            cell.computedValue !== undefined
              ? String(cell.computedValue)
              : cell.value;
          if (val.includes(',') || val.includes('"') || val.includes('\n')) {
            cols.push(`"${val.replace(/"/g, '""')}"`);
          } else {
            cols.push(val);
          }
        } else {
          cols.push('');
        }
      }
      rows.push(cols.join(','));
    }
    return rows.join('\n');
  }

  importCSV(csv: string, sheetId?: string): void {
    const sheet = sheetId ? this.getSheet(sheetId) : this.getActiveSheet();
    if (!sheet) return;

    sheet.cells = {};

    const lines = csv.split('\n');
    for (let r = 0; r < lines.length; r++) {
      const values = this.parseCSVLine(lines[r]);
      for (let c = 0; c < values.length; c++) {
        const val = values[c];
        if (val !== '') {
          sheet.cells[this.cellKey(r, c)] = { value: val };
        }
      }
    }

    this.recalculate();
  }

  private parseCSVLine(line: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQuotes) {
        if (ch === '"') {
          if (i + 1 < line.length && line[i + 1] === '"') {
            current += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else {
          current += ch;
        }
      } else {
        if (ch === '"') {
          inQuotes = true;
        } else if (ch === ',') {
          result.push(current);
          current = '';
        } else {
          current += ch;
        }
      }
    }
    result.push(current);
    return result;
  }

  // ── JSON serialization ───────────────────────────────────────────

  toJSON(): object {
    return {
      sheets: this.sheets.map((sheet) => ({
        id: sheet.id,
        name: sheet.name,
        cells: sheet.cells,
        columnWidths: sheet.columnWidths,
        rowHeights: sheet.rowHeights,
      })),
      activeSheetId: this.activeSheetId,
    };
  }

  static fromJSON(json: {
    sheets: Sheet[];
    activeSheetId: string;
  }): SpreadsheetModel {
    const model = new SpreadsheetModel();
    model.sheets = json.sheets.map((s) => ({
      id: s.id,
      name: s.name,
      cells: { ...s.cells },
      columnWidths: s.columnWidths ? { ...s.columnWidths } : {},
      rowHeights: s.rowHeights ? { ...s.rowHeights } : {},
    }));
    model.activeSheetId = json.activeSheetId;
    return model;
  }
}
