import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const store = new Map<string, any>();

export const presentationsRouter = Router();

presentationsRouter.get('/', (_req: Request, res: Response) => {
  const items = Array.from(store.values());
  res.json({ presentations: items, total: items.length });
});

presentationsRouter.post('/', (req: Request, res: Response) => {
  const { title, theme } = req.body;
  if (!title) { res.status(400).json({ error: 'title is required' }); return; }
  const now = new Date();
  const pres = { id: crypto.randomUUID(), title, theme: theme ?? 'default', slides: [], created_at: now, updated_at: now };
  store.set(pres.id, pres);
  res.status(201).json(pres);
});

presentationsRouter.get('/:id', (req: Request, res: Response) => {
  const item = store.get(req.params.id);
  if (!item) { res.status(404).json({ error: 'Presentation not found' }); return; }
  res.json(item);
});

presentationsRouter.put('/:id', (req: Request, res: Response) => {
  const item = store.get(req.params.id);
  if (!item) { res.status(404).json({ error: 'Presentation not found' }); return; }
  const updated = { ...item, ...req.body, id: item.id, updated_at: new Date() };
  store.set(updated.id, updated);
  res.json(updated);
});

presentationsRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) { res.status(404).json({ error: 'Presentation not found' }); return; }
  store.delete(req.params.id);
  res.status(204).send();
});

presentationsRouter.post('/:id/slides', (req: Request, res: Response) => {
  const pres = store.get(req.params.id);
  if (!pres) { res.status(404).json({ error: 'Presentation not found' }); return; }
  const slide = { id: crypto.randomUUID(), content: req.body.content ?? '', notes: req.body.notes ?? '', layout: req.body.layout ?? 'blank' };
  pres.slides.push(slide);
  pres.updated_at = new Date();
  res.status(201).json(slide);
});

presentationsRouter.put('/:id/slides/:slideId', (req: Request, res: Response) => {
  const pres = store.get(req.params.id);
  if (!pres) { res.status(404).json({ error: 'Presentation not found' }); return; }
  const idx = pres.slides.findIndex((s: any) => s.id === req.params.slideId);
  if (idx === -1) { res.status(404).json({ error: 'Slide not found' }); return; }
  pres.slides[idx] = { ...pres.slides[idx], ...req.body, id: pres.slides[idx].id };
  pres.updated_at = new Date();
  res.json(pres.slides[idx]);
});

presentationsRouter.delete('/:id/slides/:slideId', (req: Request, res: Response) => {
  const pres = store.get(req.params.id);
  if (!pres) { res.status(404).json({ error: 'Presentation not found' }); return; }
  pres.slides = pres.slides.filter((s: any) => s.id !== req.params.slideId);
  pres.updated_at = new Date();
  res.status(204).send();
});

presentationsRouter.put('/:id/slides/reorder', (req: Request, res: Response) => {
  const pres = store.get(req.params.id);
  if (!pres) { res.status(404).json({ error: 'Presentation not found' }); return; }
  const { order } = req.body;
  if (!Array.isArray(order)) { res.status(400).json({ error: 'order array is required' }); return; }
  const slideMap = new Map(pres.slides.map((s: any) => [s.id, s]));
  pres.slides = order.map((id: string) => slideMap.get(id)).filter(Boolean);
  pres.updated_at = new Date();
  res.json(pres);
});
