import { useState, useCallback } from 'react';

export interface Channel { id: string; name: string; members: number; }
export interface Message { id: string; channelId: string; author: string; content: string; timestamp: string; }

let nextId = 1;
const uid = () => `${nextId++}`;

const SEED_CHANNELS: Channel[] = [
  { id: uid(), name: 'general', members: 12 },
  { id: uid(), name: 'engineering', members: 8 },
  { id: uid(), name: 'design', members: 5 },
  { id: uid(), name: 'random', members: 15 },
];

const SEED_MESSAGES: Message[] = [
  { id: uid(), channelId: '1', author: 'Alice', content: 'Welcome to the general channel! 🎉', timestamp: '9:00 AM' },
  { id: uid(), channelId: '1', author: 'Bob', content: 'Hey everyone! Excited to be here.', timestamp: '9:05 AM' },
  { id: uid(), channelId: '1', author: 'Carol', content: 'Don\'t forget the standup at 10 AM.', timestamp: '9:15 AM' },
  { id: uid(), channelId: '2', author: 'Dave', content: 'PR #42 is ready for review.', timestamp: '10:30 AM' },
  { id: uid(), channelId: '2', author: 'Alice', content: 'I\'ll take a look after lunch.', timestamp: '10:45 AM' },
  { id: uid(), channelId: '3', author: 'Eve', content: 'New mockups are in Figma — feedback welcome!', timestamp: '11:00 AM' },
];

export function useConnect() {
  const [channels, setChannels] = useState<Channel[]>(SEED_CHANNELS);
  const [messages, setMessages] = useState<Message[]>(SEED_MESSAGES);
  const [selectedChannelId, setSelectedChannelId] = useState<string>(SEED_CHANNELS[0].id);

  const selectedChannel = channels.find((c) => c.id === selectedChannelId) ?? null;
  const channelMessages = messages.filter((m) => m.channelId === selectedChannelId);

  const addChannel = useCallback((name: string) => {
    const id = uid();
    setChannels((prev) => [...prev, { id, name, members: 1 }]);
    setSelectedChannelId(id);
  }, []);

  const sendMessage = useCallback((content: string) => {
    const id = uid();
    const now = new Date();
    const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setMessages((prev) => [...prev, { id, channelId: selectedChannelId, author: 'You', content, timestamp }]);
  }, [selectedChannelId]);

  return {
    channels, messages, selectedChannelId, selectedChannel, channelMessages,
    setSelectedChannelId, addChannel, sendMessage,
  };
}
