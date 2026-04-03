import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import type { NoteEntry } from '@eoffice/core';

const store = new Map<string, NoteEntry>();

export const notesRouter = Router();

// GET /api/notes — list all notes (supports ?search=query and ?tag=tagname)
notesRouter.get('/', (req: Request, res: Response) => {
  let notes = Array.from(store.values());

  const search = req.query.search as string | undefined;
  if (search) {
    const query = search.toLowerCase();
    notes = notes.filter(
      (n) =>
        n.title.toLowerCase().includes(query) ||
        n.content.toLowerCase().includes(query),
    );
  }

  const tag = req.query.tag as string | undefined;
  if (tag) {
    notes = notes.filter((n) => n.tags.includes(tag));
  }

  res.json({ notes, total: notes.length });
});

// GET /api/notes/:id — get a note
notesRouter.get('/:id', (req: Request, res: Response) => {
  const note = store.get(req.params.id);
  if (!note) {
    res.status(404).json({ error: `Note not found: ${req.params.id}` });
    return;
  }
  res.json(note);
});

// POST /api/notes — create a note
notesRouter.post('/', (req: Request, res: Response) => {
  const { title, content, tags, pinned } = req.body;

  if (!title) {
    res.status(400).json({ error: 'title is required' });
    return;
  }

  const now = new Date();
  const note: NoteEntry = {
    id: crypto.randomUUID(),
    title,
    content: content ?? '',
    tags: tags ?? [],
    created_at: now,
    updated_at: now,
    pinned: pinned ?? false,
  };

  store.set(note.id, note);
  res.status(201).json(note);
});

// PUT /api/notes/:id — update a note
notesRouter.put('/:id', (req: Request, res: Response) => {
  const existing = store.get(req.params.id);
  if (!existing) {
    res.status(404).json({ error: `Note not found: ${req.params.id}` });
    return;
  }

  const { title, content, tags, pinned } = req.body;
  const updated: NoteEntry = {
    ...existing,
    title: title ?? existing.title,
    content: content ?? existing.content,
    tags: tags ?? existing.tags,
    pinned: pinned ?? existing.pinned,
    updated_at: new Date(),
  };

  store.set(updated.id, updated);
  res.json(updated);
});

// DELETE /api/notes/:id — delete a note
notesRouter.delete('/:id', (req: Request, res: Response) => {
  if (!store.has(req.params.id)) {
    res.status(404).json({ error: `Note not found: ${req.params.id}` });
    return;
  }
  store.delete(req.params.id);
  res.status(204).send();
});
