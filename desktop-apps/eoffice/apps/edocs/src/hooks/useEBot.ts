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

  const summarize = useCallback(
    (text: string) => callEBot('summarize', { text }),
    [callEBot],
  );

  const rewrite = useCallback(
    (text: string, tone: string) =>
      callEBot('chat', { message: `Rewrite the following text in a ${tone} tone. Return only the rewritten text, no commentary.\n\n${text}` }),
    [callEBot],
  );

  const grammarCheck = useCallback(
    (text: string) =>
      callEBot('chat', { message: `Check grammar and spelling in the following text. List issues found and provide the corrected version:\n\n${text}` }),
    [callEBot],
  );

  const translate = useCallback(
    (text: string, lang: string) =>
      callEBot('chat', { message: `Translate the following text to ${lang}. Return only the translation, no commentary.\n\n${text}` }),
    [callEBot],
  );

  return { connected, loading, summarize, rewrite, grammarCheck, translate, callEBot };
}
