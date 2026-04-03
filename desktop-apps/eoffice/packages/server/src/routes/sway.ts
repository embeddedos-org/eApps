import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const store = new Map<string, any>();

export const swayRouter = Router();

swayRouter.get('/', (_req: Request, res: Response) => {
  const items = Array.from(store.values());
  res.json({ presentations: items, total: items.length });
});

swayRouter.post('/', (req: Request, res: Response) => {
  const { title, theme } = req.body;
  if (!title) { res.status(400).json({ error: 'title is required' }); return; }
  const now = new Date();
  const sway = { id: crypto.randomUUID(), title, theme: theme ?? 'default', slides: [], created_at: now, updated_at: now };
  store.set(sway.id, sway);
  res.status(201).json(sway);
});

swayRouter.get('/:id', (req: Request, res: Response) => {
  const item = store.get(req.params.id);
  if (!item) { res.status(404).json({ error: 'Sway not found' }); return; }
  res.json(item);
});

swayRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) { res.status(404).json({ error: 'Sway not found' }); return; }
  store.delete(req.params.id);
  res.status(204).send();
});

swayRouter.post('/:id/slides', (req: Request, res: Response) => {
  const sway = store.get(req.params.id);
  if (!sway) { res.status(404).json({ error: 'Sway not found' }); return; }
  const slide = { id: crypto.randomUUID(), type: req.body.type ?? 'content', content: req.body.content ?? '', interactive: req.body.interactive ?? null, responses: [] };
  sway.slides.push(slide);
  sway.updated_at = new Date();
  res.status(201).json(slide);
});

swayRouter.delete('/:id/slides/:slideId', (req: Request, res: Response) => {
  const sway = store.get(req.params.id);
  if (!sway) { res.status(404).json({ error: 'Sway not found' }); return; }
  sway.slides = sway.slides.filter((s: any) => s.id !== req.params.slideId);
  sway.updated_at = new Date();
  res.status(204).send();
});

swayRouter.post('/:id/slides/:slideId/respond', (req: Request, res: Response) => {
  const sway = store.get(req.params.id);
  if (!sway) { res.status(404).json({ error: 'Sway not found' }); return; }
  const slide = sway.slides.find((s: any) => s.id === req.params.slideId);
  if (!slide) { res.status(404).json({ error: 'Slide not found' }); return; }
  const response = { id: crypto.randomUUID(), answer: req.body.answer ?? '', user: req.body.user ?? 'anonymous', submitted_at: new Date() };
  slide.responses.push(response);
  res.status(201).json(response);
});
