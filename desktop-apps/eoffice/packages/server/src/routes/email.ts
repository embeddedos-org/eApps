import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const messages = new Map<string, any>();
const events = new Map<string, any>();

export const emailRouter = Router();

emailRouter.get('/messages', (_req: Request, res: Response) => {
  const items = Array.from(messages.values());
  res.json({ messages: items, total: items.length });
});

emailRouter.post('/messages', (req: Request, res: Response) => {
  const { to, subject, body, from } = req.body;
  if (!to || !subject) { res.status(400).json({ error: 'to and subject are required' }); return; }
  const msg = { id: crypto.randomUUID(), from: from ?? 'me@eoffice.local', to, subject, body: body ?? '', read: false, starred: false, sent_at: new Date() };
  messages.set(msg.id, msg);
  res.status(201).json(msg);
});

emailRouter.get('/messages/:id', (req: Request, res: Response) => {
  const msg = messages.get(req.params.id);
  if (!msg) { res.status(404).json({ error: 'Message not found' }); return; }
  res.json(msg);
});

emailRouter.delete('/messages/:id', (req: Request, res: Response) => {
  if (!messages.has(req.params.id)) { res.status(404).json({ error: 'Message not found' }); return; }
  messages.delete(req.params.id);
  res.status(204).send();
});

emailRouter.put('/messages/:id/read', (req: Request, res: Response) => {
  const msg = messages.get(req.params.id);
  if (!msg) { res.status(404).json({ error: 'Message not found' }); return; }
  msg.read = req.body.read ?? true;
  res.json(msg);
});

emailRouter.put('/messages/:id/star', (req: Request, res: Response) => {
  const msg = messages.get(req.params.id);
  if (!msg) { res.status(404).json({ error: 'Message not found' }); return; }
  msg.starred = req.body.starred ?? !msg.starred;
  res.json(msg);
});

emailRouter.get('/events', (_req: Request, res: Response) => {
  const items = Array.from(events.values());
  res.json({ events: items, total: items.length });
});

emailRouter.post('/events', (req: Request, res: Response) => {
  const { title, start, end } = req.body;
  if (!title || !start) { res.status(400).json({ error: 'title and start are required' }); return; }
  const evt = { id: crypto.randomUUID(), title, start, end: end ?? null, attendees: req.body.attendees ?? [], created_at: new Date() };
  events.set(evt.id, evt);
  res.status(201).json(evt);
});

emailRouter.delete('/events/:id', (req: Request, res: Response) => {
  if (!events.has(req.params.id)) { res.status(404).json({ error: 'Event not found' }); return; }
  events.delete(req.params.id);
  res.status(204).send();
});
