import React from 'react';

interface EBotSidebarProps {
  open: boolean;
  connected: boolean;
  response: string;
  isLoading: boolean;
  onAction: (action: string) => void;
  onClose: () => void;
}

interface ActionButton {
  id: string;
  label: string;
  icon: string;
  description: string;
}

const actions: ActionButton[] = [
  { id: 'summarize', label: 'Summarize', icon: '📋', description: 'Generate a document summary' },
  {
    id: 'rewrite-formal',
    label: 'Formal',
    icon: '🎩',
    description: 'Rewrite in formal tone',
  },
  {
    id: 'rewrite-casual',
    label: 'Casual',
    icon: '😊',
    description: 'Rewrite in casual tone',
  },
  {
    id: 'rewrite-concise',
    label: 'Concise',
    icon: '✂️',
    description: 'Make it shorter and punchier',
  },
  {
    id: 'grammar',
    label: 'Grammar Check',
    icon: '✅',
    description: 'Check grammar and spelling',
  },
  {
    id: 'translate',
    label: 'Translate',
    icon: '🌐',
    description: 'Translate to another language',
  },
];

export default function EBotSidebar({
  open,
  connected,
  response,
  isLoading,
  onAction,
  onClose,
}: EBotSidebarProps) {
  return (
    <aside className={`ebot-sidebar ${open ? 'open' : ''}`} aria-hidden={!open}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <h2 className="ebot-sidebar-title">
            <span className="ebot-sidebar-icon">🤖</span>
            eBot AI Assistant
          </h2>
          <button
            className="ebot-sidebar-close"
            onClick={onClose}
            title="Close sidebar"
            aria-label="Close eBot sidebar"
          >
            ✕
          </button>
        </div>

        {!connected ? (
          <div className="ebot-offline">
            <div className="ebot-offline-icon">🔌</div>
            <p className="ebot-offline-title">eBot Unavailable</p>
            <p className="ebot-offline-desc">
              The AI assistant is not connected. Check your network connection or try again later.
            </p>
          </div>
        ) : (
          <>
            <div className="ebot-actions">
              <p className="ebot-actions-label">What would you like to do?</p>
              <div className="ebot-actions-grid">
                {actions.map((action) => (
                  <button
                    key={action.id}
                    className="ebot-action-btn"
                    onClick={() => onAction(action.id)}
                    disabled={isLoading}
                    title={action.description}
                  >
                    <span className="ebot-action-icon">{action.icon}</span>
                    <span className="ebot-action-label">{action.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="ebot-response-area">
              {isLoading && (
                <div className="ebot-loading">
                  <div className="ebot-spinner" />
                  <p>eBot is thinking...</p>
                </div>
              )}
              {!isLoading && response && (
                <div className="ebot-response">
                  <div className="ebot-response-header">
                    <span>🤖</span>
                    <span>eBot Response</span>
                  </div>
                  <div className="ebot-response-body">
                    {response.split('\n').map((line, i) => (
                      <p key={i}>{line || '\u00A0'}</p>
                    ))}
                  </div>
                </div>
              )}
              {!isLoading && !response && (
                <div className="ebot-empty">
                  <p>Select an action above to get AI-powered suggestions for your document.</p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
