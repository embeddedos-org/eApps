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

  const draftReply = useCallback(
    (emailContent: string) =>
      callEBot('chat', {
        message: `Draft a professional reply to this email:\n\n${emailContent}\n\nKeep it concise and professional.`,
      }),
    [callEBot],
  );

  const summarizeThread = useCallback(
    (emails: string) =>
      callEBot('chat', {
        message: `Summarize this email thread in 2-3 bullet points:\n\n${emails}`,
      }),
    [callEBot],
  );

  const smartCompose = useCallback(
    (context: string) =>
      callEBot('chat', {
        message: `Help me compose an email about: ${context}\n\nProvide a subject line and body. Format as:\nSubject: ...\n\nBody:\n...`,
      }),
    [callEBot],
  );

  return { connected, loading, draftReply, summarizeThread, smartCompose, callEBot };
}
