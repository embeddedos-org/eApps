import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import type { Document } from '@eoffice/core';

const store = new Map<string, Document>();

export const documentsRouter = Router();

// GET /api/documents — list all documents
documentsRouter.get('/', (_req: Request, res: Response) => {
  const documents = Array.from(store.values());
  res.json({ documents, total: documents.length });
});

// GET /api/documents/:id — get a document
documentsRouter.get('/:id', (req: Request, res: Response) => {
  const doc = store.get(req.params.id);
  if (!doc) {
    res.status(404).json({ error: `Document not found: ${req.params.id}` });
    return;
  }
  res.json(doc);
});

// POST /api/documents — create a document
documentsRouter.post('/', (req: Request, res: Response) => {
  const { title, content, app_id, tags } = req.body;

  if (!title || !app_id) {
    res.status(400).json({ error: 'title and app_id are required' });
    return;
  }

  const now = new Date();
  const doc: Document = {
    id: crypto.randomUUID(),
    title,
    content: content ?? '',
    app_id,
    created_at: now,
    updated_at: now,
    tags: tags ?? [],
  };

  store.set(doc.id, doc);
  res.status(201).json(doc);
});

// PUT /api/documents/:id — update a document
documentsRouter.put('/:id', (req: Request, res: Response) => {
  const existing = store.get(req.params.id);
  if (!existing) {
    res.status(404).json({ error: `Document not found: ${req.params.id}` });
    return;
  }

  const { title, content, app_id, tags } = req.body;
  const updated: Document = {
    ...existing,
    title: title ?? existing.title,
    content: content ?? existing.content,
    app_id: app_id ?? existing.app_id,
    tags: tags ?? existing.tags,
    updated_at: new Date(),
  };

  store.set(updated.id, updated);
  res.json(updated);
});

// DELETE /api/documents/:id — delete a document
documentsRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) {
    res.status(404).json({ error: `Document not found: ${req.params.id}` });
    return;
  }
  store.delete(req.params.id);
  res.status(204).send();
});
