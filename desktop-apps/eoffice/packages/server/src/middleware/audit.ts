import { Request, Response, NextFunction } from 'express';

export function auditLog(req: Request, _res: Response, next: NextFunction): void {
  const user = (req as any).user?.username || 'anonymous';
  // eslint-disable-next-line no-console
  console.log(`[AUDIT] ${new Date().toISOString()} ${req.method} ${req.path} user=${user}`);
  next();
}
