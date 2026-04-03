import { useState } from 'react';

interface EBotSidebarProps {
  open: boolean;
  connected: boolean;
  response: string;
  isLoading: boolean;
  onAction: (action: string, input?: string) => void;
  onClose: () => void;
}

export default function EBotSidebar({
  open,
  connected,
  response,
  isLoading,
  onAction,
  onClose,
}: EBotSidebarProps) {
  const [textInput, setTextInput] = useState('');

  return (
    <div className={`ebot-sidebar ${open ? 'open' : ''}`}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <div className="ebot-sidebar-title">
            <span>🤖</span>
            <span>eBot — Planner AI</span>
          </div>
          <button className="ebot-sidebar-close" onClick={onClose}>✕</button>
        </div>

        {!connected ? (
          <div className="ebot-offline">
            <div className="ebot-offline-icon">🔌</div>
            <div className="ebot-offline-title">eBot Offline</div>
            <div className="ebot-offline-desc">
              Cannot connect to eBot server at http://localhost:3001.
            </div>
          </div>
        ) : (
          <>
            <div className="ebot-actions">
              <div className="ebot-actions-label">Extract Tasks</div>
              <textarea
                className="ebot-input"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste meeting notes, email, or any text to extract tasks..."
              />
              <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading || !textInput.trim()}
                  onClick={() => onAction('extract-tasks', textInput)}
                  style={{ flex: 1 }}
                >
                  <span className="ebot-action-icon">📝</span>
                  <span>Extract Tasks</span>
                </button>
              </div>

              <div className="ebot-actions-label" style={{ marginTop: 16 }}>
                Task Tools
              </div>
              <div className="ebot-actions-grid">
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('prioritize')}
                >
                  <span className="ebot-action-icon">🎯</span>
                  <span>Prioritize</span>
                </button>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('summarize')}
                >
                  <span className="ebot-action-icon">📊</span>
                  <span>Summary</span>
                </button>
              </div>
            </div>

            <div className="ebot-response-area">
              {isLoading ? (
                <div className="ebot-loading">
                  <div className="ebot-spinner" />
                  <span>eBot is thinking...</span>
                </div>
              ) : response ? (
                <div className="ebot-response">
                  <div className="ebot-response-header">
                    <span>🤖</span>
                    <span>eBot Response</span>
                  </div>
                  <div className="ebot-response-body">{response}</div>
                </div>
              ) : (
                <div className="ebot-empty">
                  Paste text to extract tasks or let eBot prioritize your board.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
