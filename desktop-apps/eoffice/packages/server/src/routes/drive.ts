import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const store = new Map<string, any>();

export const driveRouter = Router();

driveRouter.get('/', (_req: Request, res: Response) => {
  const items = Array.from(store.values());
  res.json({ files: items, total: items.length });
});

driveRouter.post('/', (req: Request, res: Response) => {
  const { name, type, parentId, content } = req.body;
  if (!name) { res.status(400).json({ error: 'name is required' }); return; }
  const now = new Date();
  const file = { id: crypto.randomUUID(), name, type: type ?? 'file', parentId: parentId ?? null, content: content ?? '', size: (content ?? '').length, created_at: now, updated_at: now };
  store.set(file.id, file);
  res.status(201).json(file);
});

driveRouter.get('/folder/:parentId', (req: Request, res: Response) => {
  const items = Array.from(store.values()).filter((f) => f.parentId === req.params.parentId);
  res.json({ files: items, total: items.length });
});

driveRouter.get('/:id', (req: Request, res: Response) => {
  const file = store.get(req.params.id);
  if (!file) { res.status(404).json({ error: 'File not found' }); return; }
  res.json(file);
});

driveRouter.put('/:id', (req: Request, res: Response) => {
  const file = store.get(req.params.id);
  if (!file) { res.status(404).json({ error: 'File not found' }); return; }
  const updated = { ...file, ...req.body, id: file.id, updated_at: new Date() };
  if (req.body.content) updated.size = req.body.content.length;
  store.set(updated.id, updated);
  res.json(updated);
});

driveRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) { res.status(404).json({ error: 'File not found' }); return; }
  store.delete(req.params.id);
  res.status(204).send();
});
