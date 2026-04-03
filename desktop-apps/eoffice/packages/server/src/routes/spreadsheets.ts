import { Router, Request, Response } from 'express';
import crypto from 'crypto';

interface CellData {
  value: string;
  formula?: string;
  computedValue?: string | number;
}

interface Sheet {
  id: string;
  name: string;
  cells: Record<string, CellData>;
}

interface StoredSpreadsheet {
  id: string;
  title: string;
  sheets: Sheet[];
  activeSheetId: string;
  created_at: Date;
  updated_at: Date;
}

const store = new Map<string, StoredSpreadsheet>();
export const spreadsheetsRouter = Router();

// List all spreadsheets
spreadsheetsRouter.get('/', (_req: Request, res: Response) => {
  const spreadsheets = Array.from(store.values());
  res.json({ spreadsheets, total: spreadsheets.length });
});

// Create a new spreadsheet
spreadsheetsRouter.post('/', (req: Request, res: Response) => {
  const { title } = req.body;
  if (!title) {
    return res.status(400).json({ error: 'title is required' });
  }

  const defaultSheetId = crypto.randomUUID();
  const spreadsheet: StoredSpreadsheet = {
    id: crypto.randomUUID(),
    title,
    sheets: [
      {
        id: defaultSheetId,
        name: 'Sheet1',
        cells: {},
      },
    ],
    activeSheetId: defaultSheetId,
    created_at: new Date(),
    updated_at: new Date(),
  };

  store.set(spreadsheet.id, spreadsheet);
  res.status(201).json(spreadsheet);
});

// Get spreadsheet by ID
spreadsheetsRouter.get('/:id', (req: Request, res: Response) => {
  const spreadsheet = store.get(req.params.id);
  if (!spreadsheet) {
    return res.status(404).json({ error: 'Spreadsheet not found' });
  }
  res.json(spreadsheet);
});

// Update spreadsheet metadata (title)
spreadsheetsRouter.put('/:id', (req: Request, res: Response) => {
  const spreadsheet = store.get(req.params.id);
  if (!spreadsheet) {
    return res.status(404).json({ error: 'Spreadsheet not found' });
  }

  const { title } = req.body;
  if (title) {
    spreadsheet.title = title;
  }
  spreadsheet.updated_at = new Date();
  store.set(spreadsheet.id, spreadsheet);
  res.json(spreadsheet);
});

// Delete spreadsheet
spreadsheetsRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) {
    return res.status(404).json({ error: 'Spreadsheet not found' });
  }
  store.delete(req.params.id);
  res.status(204).send();
});

// Batch cell update
spreadsheetsRouter.put('/:id/cells', (req: Request, res: Response) => {
  const spreadsheet = store.get(req.params.id);
  if (!spreadsheet) {
    return res.status(404).json({ error: 'Spreadsheet not found' });
  }

  const { sheetId, cells } = req.body;
  if (!sheetId || !Array.isArray(cells)) {
    return res
      .status(400)
      .json({ error: 'sheetId and cells array are required' });
  }

  const sheet = spreadsheet.sheets.find((s) => s.id === sheetId);
  if (!sheet) {
    return res.status(404).json({ error: 'Sheet not found' });
  }

  for (const cell of cells) {
    const { row, col, value } = cell;
    const key = `${row}:${col}`;
    sheet.cells[key] = {
      value,
      formula: cell.formula,
      computedValue: cell.computedValue,
    };
  }

  spreadsheet.updated_at = new Date();
  store.set(spreadsheet.id, spreadsheet);
  res.json(spreadsheet);
});

// Add a new sheet
spreadsheetsRouter.post('/:id/sheets', (req: Request, res: Response) => {
  const spreadsheet = store.get(req.params.id);
  if (!spreadsheet) {
    return res.status(404).json({ error: 'Spreadsheet not found' });
  }

  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: 'name is required' });
  }

  const newSheet: Sheet = {
    id: crypto.randomUUID(),
    name,
    cells: {},
  };

  spreadsheet.sheets.push(newSheet);
  spreadsheet.updated_at = new Date();
  store.set(spreadsheet.id, spreadsheet);
  res.status(201).json(newSheet);
});

// Remove a sheet
spreadsheetsRouter.delete(
  '/:id/sheets/:sheetId',
  (req: Request, res: Response) => {
    const spreadsheet = store.get(req.params.id);
    if (!spreadsheet) {
      return res.status(404).json({ error: 'Spreadsheet not found' });
    }

    const sheetIndex = spreadsheet.sheets.findIndex(
      (s) => s.id === req.params.sheetId,
    );
    if (sheetIndex === -1) {
      return res.status(404).json({ error: 'Sheet not found' });
    }

    if (spreadsheet.sheets.length <= 1) {
      return res
        .status(400)
        .json({ error: 'Cannot delete the last sheet' });
    }

    spreadsheet.sheets.splice(sheetIndex, 1);
    if (spreadsheet.activeSheetId === req.params.sheetId) {
      spreadsheet.activeSheetId = spreadsheet.sheets[0].id;
    }
    spreadsheet.updated_at = new Date();
    store.set(spreadsheet.id, spreadsheet);
    res.status(204).send();
  },
);
