import type { Email } from '../hooks/useMailbox';

interface InboxListProps {
  emails: Email[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onToggleStar: (id: string) => void;
  folderLabel: string;
}

export default function InboxList({
  emails,
  selectedId,
  onSelect,
  onToggleStar,
  folderLabel,
}: InboxListProps) {
  return (
    <div className="inbox-list">
      <div className="inbox-list-header">{folderLabel} ({emails.length})</div>
      <div className="inbox-list-body">
        {emails.length === 0 ? (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-tertiary)', fontSize: 12 }}>
            No messages
          </div>
        ) : (
          emails.map((email) => (
            <div
              key={email.id}
              className={`inbox-item ${email.id === selectedId ? 'active' : ''} ${!email.read ? 'unread' : ''}`}
              onClick={() => onSelect(email.id)}
            >
              <div className="inbox-item-row">
                <div className="inbox-item-meta">
                  {!email.read && <span className="inbox-item-unread-dot" />}
                  <span className="inbox-item-from">{email.from}</span>
                </div>
                <span className="inbox-item-date">{email.date}</span>
              </div>
              <div className="inbox-item-row">
                <span className="inbox-item-subject">{email.subject}</span>
                <button
                  className="inbox-item-star"
                  onClick={(e) => { e.stopPropagation(); onToggleStar(email.id); }}
                >
                  {email.starred ? '⭐' : '☆'}
                </button>
              </div>
              <span className="inbox-item-preview">{email.body.slice(0, 60)}...</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
