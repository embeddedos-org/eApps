import type { Email } from '../hooks/useMailbox';

interface EmailViewerProps {
  email: Email | null;
  onReply: () => void;
  onForward: () => void;
  onDelete: (id: string) => void;
}

export default function EmailViewer({ email, onReply, onForward, onDelete }: EmailViewerProps) {
  if (!email) {
    return (
      <div className="email-viewer">
        <div className="email-viewer-empty">
          <div className="email-viewer-empty-icon">✉️</div>
          <span>Select an email to read</span>
        </div>
      </div>
    );
  }

  return (
    <div className="email-viewer">
      <div className="email-header">
        <div className="email-subject">{email.subject}</div>
        <div className="email-meta">
          <span><strong>From:</strong> {email.from}</span>
          <span><strong>To:</strong> {email.to}</span>
          <span><strong>Date:</strong> {email.date}</span>
        </div>
      </div>
      <div className="email-body-content">{email.body}</div>
      <div className="email-actions">
        <button className="email-action-btn" onClick={onReply}>↩ Reply</button>
        <button className="email-action-btn" onClick={onForward}>↪ Forward</button>
        <button className="email-action-btn" onClick={() => onDelete(email.id)}>🗑 Delete</button>
      </div>
    </div>
  );
}
