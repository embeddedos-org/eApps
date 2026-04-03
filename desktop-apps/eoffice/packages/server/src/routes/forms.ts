import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const store = new Map<string, any>();
const submissions = new Map<string, any[]>();

export const formsRouter = Router();

formsRouter.get('/', (_req: Request, res: Response) => {
  const items = Array.from(store.values());
  res.json({ forms: items, total: items.length });
});

formsRouter.post('/', (req: Request, res: Response) => {
  const { title, fields } = req.body;
  if (!title) { res.status(400).json({ error: 'title is required' }); return; }
  const now = new Date();
  const form = { id: crypto.randomUUID(), title, fields: fields ?? [], created_at: now, updated_at: now };
  store.set(form.id, form);
  submissions.set(form.id, []);
  res.status(201).json(form);
});

formsRouter.get('/:id', (req: Request, res: Response) => {
  const form = store.get(req.params.id);
  if (!form) { res.status(404).json({ error: 'Form not found' }); return; }
  res.json(form);
});

formsRouter.put('/:id', (req: Request, res: Response) => {
  const form = store.get(req.params.id);
  if (!form) { res.status(404).json({ error: 'Form not found' }); return; }
  const updated = { ...form, ...req.body, id: form.id, updated_at: new Date() };
  store.set(updated.id, updated);
  res.json(updated);
});

formsRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) { res.status(404).json({ error: 'Form not found' }); return; }
  store.delete(req.params.id);
  submissions.delete(req.params.id);
  res.status(204).send();
});

formsRouter.post('/:id/submit', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) { res.status(404).json({ error: 'Form not found' }); return; }
  const entry = { id: crypto.randomUUID(), formId: req.params.id, data: req.body.data ?? {}, submitted_at: new Date() };
  const list = submissions.get(req.params.id) ?? [];
  list.push(entry);
  submissions.set(req.params.id, list);
  res.status(201).json(entry);
});

formsRouter.get('/:id/submissions', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) { res.status(404).json({ error: 'Form not found' }); return; }
  const list = submissions.get(req.params.id) ?? [];
  res.json({ submissions: list, total: list.length });
});
