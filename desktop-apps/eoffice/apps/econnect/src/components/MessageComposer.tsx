import { useState } from 'react';

interface MessageComposerProps {
  onSend: (content: string) => void;
  channelName: string;
}

export default function MessageComposer({ onSend, channelName }: MessageComposerProps) {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (!text.trim()) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <div className="message-composer">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={`Message #${channelName}...`}
        onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
      />
      <button onClick={handleSend} disabled={!text.trim()}>Send</button>
    </div>
  );
}
