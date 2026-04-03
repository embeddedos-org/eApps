import { Router, Request, Response } from 'express';
import crypto from 'crypto';

const boards = new Map<string, any>();

export const tasksRouter = Router();

tasksRouter.get('/boards', (_req: Request, res: Response) => {
  const items = Array.from(boards.values());
  res.json({ boards: items, total: items.length });
});

tasksRouter.post('/boards', (req: Request, res: Response) => {
  const { title, columns } = req.body;
  if (!title) { res.status(400).json({ error: 'title is required' }); return; }
  const now = new Date();
  const board = { id: crypto.randomUUID(), title, columns: columns ?? ['To Do', 'In Progress', 'Done'], tasks: [], created_at: now, updated_at: now };
  boards.set(board.id, board);
  res.status(201).json(board);
});

tasksRouter.get('/boards/:id', (req: Request, res: Response) => {
  const board = boards.get(req.params.id);
  if (!board) { res.status(404).json({ error: 'Board not found' }); return; }
  res.json(board);
});

tasksRouter.delete('/boards/:id', (req: Request, res: Response) => {
  if (!boards.has(req.params.id)) { res.status(404).json({ error: 'Board not found' }); return; }
  boards.delete(req.params.id);
  res.status(204).send();
});

tasksRouter.post('/boards/:id/tasks', (req: Request, res: Response) => {
  const board = boards.get(req.params.id);
  if (!board) { res.status(404).json({ error: 'Board not found' }); return; }
  const { title, description, column, assignee, priority } = req.body;
  if (!title) { res.status(400).json({ error: 'title is required' }); return; }
  const task = { id: crypto.randomUUID(), title, description: description ?? '', column: column ?? board.columns[0], assignee: assignee ?? null, priority: priority ?? 'medium', created_at: new Date() };
  board.tasks.push(task);
  board.updated_at = new Date();
  res.status(201).json(task);
});

tasksRouter.put('/boards/:id/tasks/:taskId', (req: Request, res: Response) => {
  const board = boards.get(req.params.id);
  if (!board) { res.status(404).json({ error: 'Board not found' }); return; }
  const idx = board.tasks.findIndex((t: any) => t.id === req.params.taskId);
  if (idx === -1) { res.status(404).json({ error: 'Task not found' }); return; }
  board.tasks[idx] = { ...board.tasks[idx], ...req.body, id: board.tasks[idx].id };
  board.updated_at = new Date();
  res.json(board.tasks[idx]);
});

tasksRouter.delete('/boards/:id/tasks/:taskId', (req: Request, res: Response) => {
  const board = boards.get(req.params.id);
  if (!board) { res.status(404).json({ error: 'Board not found' }); return; }
  board.tasks = board.tasks.filter((t: any) => t.id !== req.params.taskId);
  board.updated_at = new Date();
  res.status(204).send();
});
