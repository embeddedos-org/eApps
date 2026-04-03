import express from 'express';
import cors from 'cors';
import { ebotRouter } from './routes/ebot';
import { documentsRouter } from './routes/documents';
import { notesRouter } from './routes/notes';
import { spreadsheetsRouter } from './routes/spreadsheets';
import { presentationsRouter } from './routes/presentations';
import { usersRouter } from './routes/users';
import { tasksRouter } from './routes/tasks';
import { formsRouter } from './routes/forms';
import { versionsRouter } from './routes/versions';
import { emailRouter } from './routes/email';
import { databasesRouter } from './routes/databases';
import { driveRouter } from './routes/drive';
import { connectRouter } from './routes/connect';
import { swayRouter } from './routes/sway';
import { auditLog } from './middleware/audit';
import { sanitizeBody } from './middleware/sanitize';

const app = express();
const PORT = 3001;

const allowedOrigins = (
  process.env.CORS_ORIGINS ||
  'http://localhost:5170,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178,http://localhost:5179,http://localhost:5180,http://localhost:5181,http://localhost:5182,http://localhost:5183'
).split(',');

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
  }),
);
app.use(express.json({ limit: '10mb' }));
app.use(auditLog);
app.use(sanitizeBody);

app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    version: '0.1.0',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

app.use('/api/ebot', ebotRouter);
app.use('/api/documents', documentsRouter);
app.use('/api/notes', notesRouter);
app.use('/api/spreadsheets', spreadsheetsRouter);
app.use('/api/presentations', presentationsRouter);
app.use('/api/auth', usersRouter);
app.use('/api/tasks', tasksRouter);
app.use('/api/forms', formsRouter);
app.use('/api/versions', versionsRouter);
app.use('/api/email', emailRouter);
app.use('/api/databases', databasesRouter);
app.use('/api/drive', driveRouter);
app.use('/api/connect', connectRouter);
app.use('/api/sway', swayRouter);

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`eOffice Server v0.1.0 listening on port ${PORT}`);
});
