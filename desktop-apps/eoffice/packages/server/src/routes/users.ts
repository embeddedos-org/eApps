import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { users, createToken, simpleHash, authenticateToken } from '../middleware/auth';

export const usersRouter = Router();

usersRouter.post('/register', (req: Request, res: Response) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password) {
    res.status(400).json({ error: 'username, email, and password are required' });
    return;
  }
  const existing = Array.from(users.values()).find((u) => u.username === username || u.email === email);
  if (existing) {
    res.status(409).json({ error: 'User already exists' });
    return;
  }
  const user = { id: crypto.randomUUID(), username, email, passwordHash: simpleHash(password), role: 'user' };
  users.set(user.id, user);
  const token = createToken({ id: user.id, username, email, role: user.role });
  res.status(201).json({ user: { id: user.id, username, email, role: user.role }, token });
});

usersRouter.post('/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  if (!username || !password) {
    res.status(400).json({ error: 'username and password are required' });
    return;
  }
  const user = Array.from(users.values()).find((u) => u.username === username);
  if (!user || user.passwordHash !== simpleHash(password)) {
    res.status(401).json({ error: 'Invalid credentials' });
    return;
  }
  const token = createToken({ id: user.id, username: user.username, email: user.email, role: user.role });
  res.json({ user: { id: user.id, username: user.username, email: user.email, role: user.role }, token });
});

usersRouter.post('/refresh', authenticateToken, (req: Request, res: Response) => {
  const user = (req as any).user;
  const token = createToken({ id: user.id, username: user.username, email: user.email, role: user.role });
  res.json({ token });
});

usersRouter.get('/profile', authenticateToken, (req: Request, res: Response) => {
  const payload = (req as any).user;
  const user = users.get(payload.id);
  if (!user) {
    res.status(404).json({ error: 'User not found' });
    return;
  }
  res.json({ id: user.id, username: user.username, email: user.email, role: user.role });
});
