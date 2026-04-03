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
  const [formulaInput, setFormulaInput] = useState('');

  return (
    <div className={`ebot-sidebar ${open ? 'open' : ''}`}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <div className="ebot-sidebar-title">
            <span>🤖</span>
            <span>eBot — Sheets AI</span>
          </div>
          <button className="ebot-sidebar-close" onClick={onClose}>
            ✕
          </button>
        </div>

        {!connected ? (
          <div className="ebot-offline">
            <div className="ebot-offline-icon">🔌</div>
            <div className="ebot-offline-title">eBot Offline</div>
            <div className="ebot-offline-desc">
              Cannot connect to eBot server. Make sure the server is running at
              http://localhost:3001.
            </div>
          </div>
        ) : (
          <>
            <div className="ebot-actions">
              <div className="ebot-actions-label">Formula Assistant</div>
              <input
                className="ebot-formula-input"
                value={formulaInput}
                onChange={(e) => setFormulaInput(e.target.value)}
                placeholder="Describe what you need (e.g., 'sum of column A')"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && formulaInput.trim()) {
                    onAction('suggest-formula', formulaInput);
                  }
                }}
              />
              <div className="ebot-actions-grid" style={{ marginTop: 8 }}>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading || !formulaInput.trim()}
                  onClick={() => onAction('suggest-formula', formulaInput)}
                >
                  <span className="ebot-action-icon">💡</span>
                  <span>Suggest</span>
                </button>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading || !formulaInput.trim()}
                  onClick={() => onAction('explain-formula', formulaInput)}
                >
                  <span className="ebot-action-icon">📖</span>
                  <span>Explain</span>
                </button>
              </div>

              <div className="ebot-actions-label" style={{ marginTop: 16 }}>
                Data Tools
              </div>
              <div className="ebot-actions-grid">
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('analyze-data')}
                >
                  <span className="ebot-action-icon">📊</span>
                  <span>Analyze</span>
                </button>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('summarize')}
                >
                  <span className="ebot-action-icon">📋</span>
                  <span>Summarize</span>
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
                  Ask eBot for formula suggestions, explanations, or data analysis.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
