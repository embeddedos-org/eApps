import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const store = new Map<string, any[]>();

function versionKey(type: string, id: string): string {
  return `${type}:${id}`;
}

export const versionsRouter = Router();

versionsRouter.get('/:resourceType/:resourceId', (req: Request, res: Response) => {
  const key = versionKey(req.params.resourceType, req.params.resourceId);
  const versions = store.get(key) ?? [];
  res.json({ versions, total: versions.length });
});

versionsRouter.post('/:resourceType/:resourceId', (req: Request, res: Response) => {
  const key = versionKey(req.params.resourceType, req.params.resourceId);
  const versions = store.get(key) ?? [];
  const version = { id: crypto.randomUUID(), resourceType: req.params.resourceType, resourceId: req.params.resourceId, data: req.body.data ?? {}, message: req.body.message ?? '', created_at: new Date(), number: versions.length + 1 };
  versions.push(version);
  store.set(key, versions);
  res.status(201).json(version);
});

versionsRouter.get('/:resourceType/:resourceId/:versionId', (req: Request, res: Response) => {
  const key = versionKey(req.params.resourceType, req.params.resourceId);
  const versions = store.get(key) ?? [];
  const version = versions.find((v) => v.id === req.params.versionId);
  if (!version) { res.status(404).json({ error: 'Version not found' }); return; }
  res.json(version);
});
