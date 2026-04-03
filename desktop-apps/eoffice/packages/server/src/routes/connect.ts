import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const channels = new Map<string, any>();
const channelMessages = new Map<string, any[]>();

export const connectRouter = Router();

connectRouter.get('/channels', (_req: Request, res: Response) => {
  const items = Array.from(channels.values());
  res.json({ channels: items, total: items.length });
});

connectRouter.post('/channels', (req: Request, res: Response) => {
  const { name, description } = req.body;
  if (!name) { res.status(400).json({ error: 'name is required' }); return; }
  const ch = { id: crypto.randomUUID(), name, description: description ?? '', members: [], created_at: new Date() };
  channels.set(ch.id, ch);
  channelMessages.set(ch.id, []);
  res.status(201).json(ch);
});

connectRouter.get('/channels/:id', (req: Request, res: Response) => {
  const ch = channels.get(req.params.id);
  if (!ch) { res.status(404).json({ error: 'Channel not found' }); return; }
  res.json(ch);
});

connectRouter.delete('/channels/:id', (req: Request, res: Response) => {
  if (!channels.has(req.params.id)) { res.status(404).json({ error: 'Channel not found' }); return; }
  channels.delete(req.params.id);
  channelMessages.delete(req.params.id);
  res.status(204).send();
});

connectRouter.post('/channels/:id/messages', (req: Request, res: Response) => {
  if (!channels.has(req.params.id)) { res.status(404).json({ error: 'Channel not found' }); return; }
  const { content, author } = req.body;
  if (!content) { res.status(400).json({ error: 'content is required' }); return; }
  const msg = { id: crypto.randomUUID(), channelId: req.params.id, content, author: author ?? 'anonymous', sent_at: new Date() };
  const list = channelMessages.get(req.params.id) ?? [];
  list.push(msg);
  channelMessages.set(req.params.id, list);
  res.status(201).json(msg);
});

connectRouter.get('/channels/:id/messages', (req: Request, res: Response) => {
  if (!channels.has(req.params.id)) { res.status(404).json({ error: 'Channel not found' }); return; }
  const list = channelMessages.get(req.params.id) ?? [];
  res.json({ messages: list, total: list.length });
});
