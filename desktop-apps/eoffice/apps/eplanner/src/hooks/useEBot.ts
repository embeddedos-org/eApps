import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:3001/api/ebot';

export function useEBot() {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then((r) => (r.ok ? setConnected(true) : setConnected(false)))
      .catch(() => setConnected(false));
  }, []);

  const callEBot = useCallback(async (endpoint: string, body?: object): Promise<string> => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/${endpoint}`, {
        method: body ? 'POST' : 'GET',
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!resp.ok) {
        const errText = await resp.text().catch(() => resp.statusText);
        throw new Error(`eBot error (${resp.status}): ${errText}`);
      }
      const data = await resp.json();
      setConnected(true);
      return data.text || data.response || JSON.stringify(data);
    } catch (err) {
      setConnected(false);
      throw err instanceof Error ? err : new Error('eBot unavailable');
    } finally {
      setLoading(false);
    }
  }, []);

  const extractTasks = useCallback(
    (text: string) =>
      callEBot('chat', {
        message: `Extract actionable tasks from the following text. Return each task on a separate line starting with "- ". Include a suggested priority (High/Medium/Low) in brackets at the end.\n\nText:\n${text}`,
      }),
    [callEBot],
  );

  const suggestPriority = useCallback(
    (description: string) =>
      callEBot('chat', {
        message: `Given this task description, suggest a priority level (High, Medium, or Low) and briefly explain why.\n\nTask: ${description}`,
      }),
    [callEBot],
  );

  return { connected, loading, extractTasks, suggestPriority, callEBot };
}
