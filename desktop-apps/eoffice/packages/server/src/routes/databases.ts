import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const tables = new Map<string, any>();

export const databasesRouter = Router();

databasesRouter.get('/tables', (_req: Request, res: Response) => {
  const items = Array.from(tables.values());
  res.json({ tables: items, total: items.length });
});

databasesRouter.post('/tables', (req: Request, res: Response) => {
  const { name, columns } = req.body;
  if (!name) { res.status(400).json({ error: 'name is required' }); return; }
  const now = new Date();
  const table = { id: crypto.randomUUID(), name, columns: columns ?? [], rows: [], created_at: now, updated_at: now };
  tables.set(table.id, table);
  res.status(201).json(table);
});

databasesRouter.get('/tables/:id', (req: Request, res: Response) => {
  const table = tables.get(req.params.id);
  if (!table) { res.status(404).json({ error: 'Table not found' }); return; }
  res.json(table);
});

databasesRouter.delete('/tables/:id', (req: Request, res: Response) => {
  if (!tables.has(req.params.id)) { res.status(404).json({ error: 'Table not found' }); return; }
  tables.delete(req.params.id);
  res.status(204).send();
});

databasesRouter.post('/tables/:id/rows', (req: Request, res: Response) => {
  const table = tables.get(req.params.id);
  if (!table) { res.status(404).json({ error: 'Table not found' }); return; }
  const row = req.body.row ?? req.body;
  table.rows.push(row);
  table.updated_at = new Date();
  res.status(201).json({ index: table.rows.length - 1, row });
});

databasesRouter.put('/tables/:id/rows/:index', (req: Request, res: Response) => {
  const table = tables.get(req.params.id);
  if (!table) { res.status(404).json({ error: 'Table not found' }); return; }
  const idx = parseInt(req.params.index, 10);
  if (idx < 0 || idx >= table.rows.length) { res.status(404).json({ error: 'Row not found' }); return; }
  table.rows[idx] = req.body.row ?? req.body;
  table.updated_at = new Date();
  res.json({ index: idx, row: table.rows[idx] });
});

databasesRouter.delete('/tables/:id/rows/:index', (req: Request, res: Response) => {
  const table = tables.get(req.params.id);
  if (!table) { res.status(404).json({ error: 'Table not found' }); return; }
  const idx = parseInt(req.params.index, 10);
  if (idx < 0 || idx >= table.rows.length) { res.status(404).json({ error: 'Row not found' }); return; }
  table.rows.splice(idx, 1);
  table.updated_at = new Date();
  res.status(204).send();
});
