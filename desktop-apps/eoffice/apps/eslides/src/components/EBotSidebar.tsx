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
  const [topic, setTopic] = useState('');
  const [slideCount, setSlideCount] = useState('5');

  return (
    <div className={`ebot-sidebar ${open ? 'open' : ''}`}>
      <div className="ebot-sidebar-inner">
        <div className="ebot-sidebar-header">
          <div className="ebot-sidebar-title">
            <span>🤖</span>
            <span>eBot — Slides AI</span>
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
              <div className="ebot-actions-label">Generate Slides</div>
              <input
                className="ebot-input"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter topic (e.g., 'AI in Healthcare')"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && topic.trim()) {
                    onAction('generate-slides', `${topic}|||${slideCount}`);
                  }
                }}
              />
              <div className="ebot-row">
                <input
                  className="ebot-input"
                  type="number"
                  min="1"
                  max="20"
                  value={slideCount}
                  onChange={(e) => setSlideCount(e.target.value)}
                  style={{ width: 60, marginTop: 0 }}
                />
                <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>slides</span>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading || !topic.trim()}
                  onClick={() => onAction('generate-slides', `${topic}|||${slideCount}`)}
                  style={{ marginLeft: 'auto' }}
                >
                  <span className="ebot-action-icon">✨</span>
                  <span>Generate</span>
                </button>
              </div>

              <div className="ebot-actions-label" style={{ marginTop: 16 }}>
                Slide Tools
              </div>
              <div className="ebot-actions-grid">
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('talking-points')}
                >
                  <span className="ebot-action-icon">🎤</span>
                  <span>Talking Points</span>
                </button>
                <button
                  className="ebot-action-btn"
                  disabled={isLoading}
                  onClick={() => onAction('improve-slide')}
                >
                  <span className="ebot-action-icon">💡</span>
                  <span>Improve</span>
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
                  Generate slides from a topic or get talking points for your current slide.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
