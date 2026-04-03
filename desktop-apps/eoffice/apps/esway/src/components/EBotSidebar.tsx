import { useState } from 'react';

interface EBotSidebarProps {
  open: boolean;
  connected: boolean;
  loading: boolean;
  onClose: () => void;
  onGenerateQuiz: (topic: string, count: number) => Promise<string>;
  onSuggestPoll: (topic: string) => Promise<string>;
}

export default function EBotSidebar({ open, connected, loading, onClose, onGenerateQuiz, onSuggestPoll }: EBotSidebarProps) {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');

  const handleAction = async (action: 'quiz' | 'poll') => {
    if (!input.trim()) return;
    try {
      const result = action === 'quiz'
        ? await onGenerateQuiz(input, 3)
        : await onSuggestPoll(input);
      setResponse(result);
    } catch (err) {
      setResponse(`❌ ${err instanceof Error ? err.message : 'Error'}`);
    }
  };

  return (
    <div className={`ebot-sidebar ${open ? 'open' : ''}`}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <div className="ebot-sidebar-title"><span>🤖</span><span>eBot — Sway AI</span></div>
          <button className="ebot-sidebar-close" onClick={onClose}>✕</button>
        </div>
        {!connected ? (
          <div className="ebot-offline">
            <div className="ebot-offline-icon">🔌</div>
            <div className="ebot-offline-title">eBot Offline</div>
            <div className="ebot-offline-desc">Cannot connect to eBot server at localhost:3001.</div>
          </div>
        ) : (
          <>
            <div className="ebot-actions">
              <div className="ebot-actions-label">Presentation Assistant</div>
              <input
                className="ebot-formula-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter a topic (e.g., JavaScript)..."
                onKeyDown={(e) => { if (e.key === 'Enter') handleAction('quiz'); }}
              />
              <div className="ebot-actions-grid" style={{ marginTop: 8 }}>
                <button className="ebot-action-btn" disabled={loading || !input.trim()} onClick={() => handleAction('quiz')}>
                  <span className="ebot-action-icon">❓</span><span>Gen Quiz</span>
                </button>
                <button className="ebot-action-btn" disabled={loading || !input.trim()} onClick={() => handleAction('poll')}>
                  <span className="ebot-action-icon">📊</span><span>Suggest Poll</span>
                </button>
              </div>
            </div>
            <div className="ebot-response-area">
              {loading ? (
                <div className="ebot-loading"><div className="ebot-spinner" /><span>eBot is thinking...</span></div>
              ) : response ? (
                <div className="ebot-response">
                  <div className="ebot-response-header"><span>🤖</span><span>eBot Response</span></div>
                  <div className="ebot-response-body">{response}</div>
                </div>
              ) : (
                <div className="ebot-empty">Ask eBot to generate quizzes or suggest polls.</div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
