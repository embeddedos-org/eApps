import { useEffect, useRef } from 'react';
import type { Message } from '../hooks/useConnect';

interface MessageThreadProps {
  messages: Message[];
  channelName: string;
}

export default function MessageThread({ messages, channelName }: MessageThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  if (messages.length === 0) {
    return (
      <div className="message-thread">
        <div className="message-empty">
          <div className="message-empty-icon">💬</div>
          <div>No messages in #{channelName} yet</div>
          <div style={{ fontSize: 12 }}>Start the conversation!</div>
        </div>
      </div>
    );
  }

  return (
    <div className="message-thread">
      {messages.map((msg) => (
        <div key={msg.id} className="message-item">
          <div className="message-avatar">{msg.author[0]}</div>
          <div className="message-body">
            <div className="message-header">
              <span className="message-author">{msg.author}</span>
              <span className="message-time">{msg.timestamp}</span>
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
