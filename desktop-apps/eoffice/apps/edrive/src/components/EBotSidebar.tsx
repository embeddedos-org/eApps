import { useState } from 'react';

interface EBotSidebarProps {
  open: boolean;
  connected: boolean;
  loading: boolean;
  onClose: () => void;
  onSearchFiles: (query: string) => Promise<string>;
  onSummarizeFile: (content: string) => Promise<string>;
}

export default function EBotSidebar({ open, connected, loading, onClose, onSearchFiles, onSummarizeFile }: EBotSidebarProps) {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');

  const handleAction = async (action: 'search' | 'summarize') => {
    if (!input.trim()) return;
    try {
      const result = action === 'search'
        ? await onSearchFiles(input)
        : await onSummarizeFile(input);
      setResponse(result);
    } catch (err) {
      setResponse(`❌ ${err instanceof Error ? err.message : 'Error'}`);
    }
  };

  return (
    <div className={`ebot-sidebar ${open ? 'open' : ''}`}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <div className="ebot-sidebar-title"><span>🤖</span><span>eBot — Drive AI</span></div>
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
              <div className="ebot-actions-label">File Assistant</div>
              <input
                className="ebot-formula-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Search files or describe content..."
                onKeyDown={(e) => { if (e.key === 'Enter') handleAction('search'); }}
              />
              <div className="ebot-actions-grid" style={{ marginTop: 8 }}>
                <button className="ebot-action-btn" disabled={loading || !input.trim()} onClick={() => handleAction('search')}>
                  <span className="ebot-action-icon">🔍</span><span>Search</span>
                </button>
                <button className="ebot-action-btn" disabled={loading || !input.trim()} onClick={() => handleAction('summarize')}>
                  <span className="ebot-action-icon">📋</span><span>Summarize</span>
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
                <div className="ebot-empty">Ask eBot to search files or summarize content.</div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
