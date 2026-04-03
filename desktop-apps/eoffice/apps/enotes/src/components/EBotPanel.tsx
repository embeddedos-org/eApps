import { useState } from 'react';
import type { Note } from '../App';
import { useEBot } from '../hooks/useEBot';

interface EBotPanelProps {
  note: Note;
  isOpen: boolean;
  onToggle: () => void;
  onApplyTags: (tags: string[]) => void;
}

type EBotAction = 'summarize' | 'auto-tag' | 'extract-tasks' | 'find-related';

interface EBotResult {
  action: EBotAction;
  result: string;
  tags?: string[];
}

function parseTags(raw: string): string[] {
  try {
    const trimmed = raw.trim();
    const jsonStart = trimmed.indexOf('[');
    const jsonEnd = trimmed.lastIndexOf(']') + 1;
    if (jsonStart !== -1 && jsonEnd > jsonStart) {
      const parsed = JSON.parse(trimmed.slice(jsonStart, jsonEnd));
      if (Array.isArray(parsed)) return parsed.map(String);
    }
  } catch {
    // fall through
  }
  return raw
    .split(/[,\n]+/)
    .map((s) => s.replace(/^[\s#*\-\d.]+/, '').trim().toLowerCase())
    .filter((s) => s.length > 0)
    .slice(0, 5);
}

export default function EBotPanel({ note, isOpen, onToggle, onApplyTags }: EBotPanelProps) {
  const [response, setResponse] = useState<EBotResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { connected, loading, summarize, autoTag, extractTasks, findRelated } = useEBot();

  const handleAction = async (action: EBotAction) => {
    setError(null);
    setResponse(null);

    const content = note.content || note.title || '';
    if (!content.trim()) {
      setError('Note is empty. Add some content first.');
      return;
    }

    try {
      let result = '';
      let tags: string[] | undefined;

      switch (action) {
        case 'summarize':
          result = await summarize(content);
          result = `📋 **Summary:**\n${result}`;
          break;

        case 'auto-tag': {
          const raw = await autoTag(content);
          tags = parseTags(raw);
          result = `🏷️ **Suggested Tags:** ${tags.join(', ')}`;
          break;
        }

        case 'extract-tasks':
          result = await extractTasks(content);
          result = `📌 **Extracted Tasks:**\n${result}`;
          break;

        case 'find-related':
          result = await findRelated(content);
          result = `🔗 **Related Notes:**\n${result}`;
          break;
      }

      setResponse({ action, result, tags });
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(`eBot unavailable: ${msg}`);
    }
  };

  const handleApplyTags = () => {
    if (response?.tags) {
      onApplyTags(response.tags);
    }
  };

  return (
    <div className={`ebot-panel ${isOpen ? 'open' : ''}`}>
      <button className="ebot-toggle" onClick={onToggle}>
        <span className="ebot-toggle-label">
          🤖 eBot AI {!connected && '(offline)'}
        </span>
        <span className="ebot-toggle-arrow">{isOpen ? '▼' : '▲'}</span>
      </button>

      {isOpen && (
        <div className="ebot-body">
          {!connected && (
            <div className="ebot-error">
              eBot is unavailable. Check that the server is running at http://localhost:3001.
            </div>
          )}

          <div className="ebot-actions">
            <button
              className="ebot-action-btn"
              onClick={() => handleAction('summarize')}
              disabled={loading || !connected}
            >
              📋 Summarize
            </button>
            <button
              className="ebot-action-btn"
              onClick={() => handleAction('auto-tag')}
              disabled={loading || !connected}
            >
              🏷️ Auto-Tag
            </button>
            <button
              className="ebot-action-btn"
              onClick={() => handleAction('extract-tasks')}
              disabled={loading || !connected}
            >
              📌 Extract Tasks
            </button>
            <button
              className="ebot-action-btn"
              onClick={() => handleAction('find-related')}
              disabled={loading || !connected}
            >
              🔗 Find Related
            </button>
          </div>

          <div className="ebot-response-area">
            {loading && (
              <div className="ebot-loading">
                <span className="spinner" />
                eBot is thinking…
              </div>
            )}
            {error && <div className="ebot-error">{error}</div>}
            {response && !loading && (
              <div className="ebot-result">
                <pre className="ebot-result-text">{response.result}</pre>
                {response.tags && (
                  <button className="btn-apply-tags" onClick={handleApplyTags}>
                    ✅ Apply Suggested Tags
                  </button>
                )}
              </div>
            )}
            {!loading && !error && !response && (
              <div className="ebot-placeholder">
                Select an action above to get AI-powered insights on your note.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
