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
  const [descInput, setDescInput] = useState('');

  return (
    <div className={`ebot-sidebar ${open ? 'open' : ''}`}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <div className="ebot-sidebar-title">
            <span>🤖</span>
            <span>eBot — Forms AI</span>
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
              <div className="ebot-actions-label">Suggest Fields</div>
              <textarea
                className="ebot-input"
                value={descInput}
                onChange={(e) => setDescInput(e.target.value)}
                placeholder="Describe your form purpose (e.g., 'Employee feedback survey')"
              />
              <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading || !descInput.trim()}
                  onClick={() => onAction('suggest-fields', descInput)}
                  style={{ flex: 1 }}
                >
                  <span className="ebot-action-icon">✨</span>
                  <span>Suggest Fields</span>
                </button>
              </div>

              <div className="ebot-actions-label" style={{ marginTop: 16 }}>
                Form Tools
              </div>
              <div className="ebot-actions-grid">
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('improve-questions')}
                >
                  <span className="ebot-action-icon">💡</span>
                  <span>Improve</span>
                </button>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('validate')}
                >
                  <span className="ebot-action-icon">✅</span>
                  <span>Validate</span>
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
                  Describe your form to get field suggestions or improve existing questions.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
