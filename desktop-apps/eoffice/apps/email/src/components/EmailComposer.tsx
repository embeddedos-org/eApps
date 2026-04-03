import { useState } from 'react';

interface EmailComposerProps {
  initialTo?: string;
  initialSubject?: string;
  initialBody?: string;
  onSend: (to: string, subject: string, body: string) => void;
  onClose: () => void;
}

export default function EmailComposer({
  initialTo = '',
  initialSubject = '',
  initialBody = '',
  onSend,
  onClose,
}: EmailComposerProps) {
  const [to, setTo] = useState(initialTo);
  const [subject, setSubject] = useState(initialSubject);
  const [body, setBody] = useState(initialBody);

  const handleSend = () => {
    if (!to.trim() || !subject.trim()) return;
    onSend(to, subject, body);
    onClose();
  };

  return (
    <div className="composer-overlay" onClick={onClose}>
      <div className="composer" onClick={(e) => e.stopPropagation()}>
        <div className="composer-header">
          <h3>New Message</h3>
          <button className="composer-close" onClick={onClose}>✕</button>
        </div>
        <label>
          To
          <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="recipient@eoffice.com" />
        </label>
        <label>
          Subject
          <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Subject" />
        </label>
        <label>
          Body
          <textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="Write your message..." />
        </label>
        <div className="composer-actions">
          <button className="composer-btn" onClick={onClose}>Discard</button>
          <button className="composer-btn primary" onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
}
