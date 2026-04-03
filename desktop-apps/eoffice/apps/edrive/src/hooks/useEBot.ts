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

  const callEBot = useCallback(async (message: string): Promise<string> => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      if (!resp.ok) throw new Error(`eBot error (${resp.status})`);
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

  const searchFiles = useCallback(
    (query: string) => callEBot(`Search for files matching this description: ${query}`),
    [callEBot],
  );

  const summarizeFile = useCallback(
    (content: string) => callEBot(`Summarize this file content:\n\n${content}`),
    [callEBot],
  );

  return { connected, loading, searchFiles, summarizeFile };
}
