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

  const suggestContent = useCallback(
    (topic: string, count: number) =>
      callEBot('chat', {
        message: `Generate ${count} presentation slide titles and bullet points for the topic: "${topic}". Format each slide as "Slide N: Title\\n- bullet1\\n- bullet2\\n- bullet3". Return only the slide content.`,
      }),
    [callEBot],
  );

  const generateTalkingPoints = useCallback(
    (content: string) =>
      callEBot('chat', {
        message: `Generate speaker talking points for this presentation slide content:\n\n${content}\n\nProvide 3-5 concise talking points the presenter should cover.`,
      }),
    [callEBot],
  );

  return { connected, loading, suggestContent, generateTalkingPoints, callEBot };
}
