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

  const suggestFormula = useCallback(
    (description: string, context?: string) =>
      callEBot('chat', {
        message: `Suggest a spreadsheet formula for the following requirement. Return ONLY the formula (starting with =), no explanation.\n\nRequirement: ${description}${context ? `\nContext: ${context}` : ''}`,
      }),
    [callEBot],
  );

  const explainFormula = useCallback(
    (formula: string) =>
      callEBot('chat', {
        message: `Explain this spreadsheet formula step by step in plain language:\n\n${formula}`,
      }),
    [callEBot],
  );

  const analyzeData = useCallback(
    (data: string) =>
      callEBot('chat', {
        message: `Analyze this spreadsheet data and provide key insights, trends, and suggestions:\n\n${data}`,
      }),
    [callEBot],
  );

  return { connected, loading, suggestFormula, explainFormula, analyzeData, callEBot };
}
