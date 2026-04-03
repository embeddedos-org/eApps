import type { DBTable } from './types';
import { generateId } from './utils';

export class DatabaseModel {
  public tables: DBTable[];

  constructor(tables: DBTable[] = []) {
    this.tables = tables;
  }

  createTable(name: string, columns: Array<{ name: string; type: string }>): DBTable {
    const table: DBTable = { id: generateId(), name, columns, rows: [], created_at: new Date() };
    this.tables.push(table);
    return table;
  }

  dropTable(id: string): boolean {
    const index = this.tables.findIndex((t) => t.id === id);
    if (index === -1) return false;
    this.tables.splice(index, 1);
    return true;
  }

  insertRow(tableId: string, row: Record<string, unknown>): boolean {
    const table = this.tables.find((t) => t.id === tableId);
    if (!table) return false;
    table.rows.push(row);
    return true;
  }

  updateRow(tableId: string, rowIndex: number, data: Record<string, unknown>): boolean {
    const table = this.tables.find((t) => t.id === tableId);
    if (!table || rowIndex < 0 || rowIndex >= table.rows.length) return false;
    table.rows[rowIndex] = { ...table.rows[rowIndex], ...data };
    return true;
  }

  deleteRow(tableId: string, rowIndex: number): boolean {
    const table = this.tables.find((t) => t.id === tableId);
    if (!table || rowIndex < 0 || rowIndex >= table.rows.length) return false;
    table.rows.splice(rowIndex, 1);
    return true;
  }

  query(tableId: string, predicate: (row: Record<string, unknown>) => boolean): Record<string, unknown>[] {
    const table = this.tables.find((t) => t.id === tableId);
    if (!table) return [];
    return table.rows.filter(predicate);
  }

  toJSON(): object {
    return { tables: this.tables };
  }

  static fromJSON(json: { tables: DBTable[] }): DatabaseModel {
    return new DatabaseModel(
      json.tables.map((t) => ({ ...t, created_at: new Date(t.created_at) })),
    );
  }
}
