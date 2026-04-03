import { Router, Request, Response } from 'express';

const EAI_BASE_URL = process.env.EAI_BASE_URL || 'http://192.168.1.100:8420';

export const ebotRouter = Router();

async function proxyRequest(
  req: Request,
  res: Response,
  method: 'GET' | 'POST',
  eaiPath: string,
): Promise<void> {
  try {
    const url = `${EAI_BASE_URL}${eaiPath}`;
    const fetchOptions: { method: string; headers: Record<string, string>; body?: string } = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };

    if (method === 'POST' && req.body) {
      fetchOptions.body = JSON.stringify(req.body);
    }

    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      const errorText = await response.text();
      res.status(response.status).json({
        error: `EAI server error: ${response.statusText}`,
        details: errorText,
      });
      return;
    }

    const data = await response.json();
    res.json(data);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    // eslint-disable-next-line no-console
    console.error(`EAI proxy error [${eaiPath}]:`, message);
    res.status(502).json({
      error: 'Failed to reach EAI Ebot Server',
      details: message,
    });
  }
}

async function proxyWithChatFallback(
  req: Request,
  res: Response,
  eaiPath: string,
  chatPromptPrefix: string,
  bodyTextField: string,
): Promise<void> {
  try {
    const url = `${EAI_BASE_URL}${eaiPath}`;
    const fetchOptions: { method: string; headers: Record<string, string>; body?: string } = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    };

    const response = await fetch(url, fetchOptions);

    if (response.status === 404) {
      // eslint-disable-next-line no-console
      console.log(`EAI ${eaiPath} returned 404, falling back to /v1/chat`);
      const text = req.body?.[bodyTextField] || '';
      const chatUrl = `${EAI_BASE_URL}/v1/chat`;
      const chatResponse = await fetch(chatUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: `${chatPromptPrefix}\n\n${text}` }),
      });

      if (!chatResponse.ok) {
        const errorText = await chatResponse.text();
        res.status(chatResponse.status).json({
          error: `EAI chat fallback error: ${chatResponse.statusText}`,
          details: errorText,
        });
        return;
      }

      const data = await chatResponse.json();
      res.json(data);
      return;
    }

    if (!response.ok) {
      const errorText = await response.text();
      res.status(response.status).json({
        error: `EAI server error: ${response.statusText}`,
        details: errorText,
      });
      return;
    }

    const data = await response.json();
    res.json(data);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    // eslint-disable-next-line no-console
    console.error(`EAI proxy error [${eaiPath}]:`, message);
    res.status(502).json({
      error: 'Failed to reach EAI Ebot Server',
      details: message,
    });
  }
}

// POST /api/ebot/chat → EAI /v1/chat
ebotRouter.post('/chat', (req, res) => proxyRequest(req, res, 'POST', '/v1/chat'));

// POST /api/ebot/complete → EAI /v1/complete
ebotRouter.post('/complete', (req, res) => proxyRequest(req, res, 'POST', '/v1/complete'));

// POST /api/ebot/summarize → EAI /v1/summarize (fallback: /v1/chat)
ebotRouter.post('/summarize', (req, res) =>
  proxyWithChatFallback(
    req,
    res,
    '/v1/summarize',
    'Summarize the following text concisely:',
    'text',
  ),
);

// POST /api/ebot/task-extract → EAI /v1/task-extract (fallback: /v1/chat)
ebotRouter.post('/task-extract', (req, res) =>
  proxyWithChatFallback(
    req,
    res,
    '/v1/task-extract',
    'Extract actionable tasks from the following text. List each task with its priority (high/medium/low):',
    'text',
  ),
);

// POST /api/ebot/search → EAI /v1/search
ebotRouter.post('/search', (req, res) => proxyRequest(req, res, 'POST', '/v1/search'));

// GET /api/ebot/models → EAI /v1/models
ebotRouter.get('/models', (req, res) => proxyRequest(req, res, 'GET', '/v1/models'));

// GET /api/ebot/tools → EAI /v1/tools
ebotRouter.get('/tools', (req, res) => proxyRequest(req, res, 'GET', '/v1/tools'));

// GET /api/ebot/status → EAI /v1/status
ebotRouter.get('/status', (req, res) => proxyRequest(req, res, 'GET', '/v1/status'));

// POST /api/ebot/reset → EAI /v1/reset
ebotRouter.post('/reset', (req, res) => proxyRequest(req, res, 'POST', '/v1/reset'));
