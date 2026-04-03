import { useState, useCallback } from 'react';

export type Folder = 'inbox' | 'sent' | 'drafts';

export interface Email {
  id: string;
  from: string;
  to: string;
  subject: string;
  body: string;
  date: string;
  read: boolean;
  starred: boolean;
  folder: Folder;
}

let nextId = 1;
const uid = () => `msg-${nextId++}`;

const SAMPLE_EMAILS: Email[] = [
  { id: uid(), from: 'alice@eoffice.com', to: 'me@eoffice.com', subject: 'Q2 Planning Meeting', body: 'Hi team,\n\nLet\'s schedule our Q2 planning meeting for next Tuesday at 2 PM.\n\nPlease come prepared with your OKR proposals.\n\nBest,\nAlice', date: '2026-04-03', read: false, starred: false, folder: 'inbox' },
  { id: uid(), from: 'bob@eoffice.com', to: 'me@eoffice.com', subject: 'Code Review: PR #142', body: 'Hey,\n\nI\'ve reviewed your PR. A few comments:\n\n1. Consider adding error handling in the auth module\n2. The test coverage looks good\n3. Minor style issue on line 45\n\nOverall LGTM with minor changes.\n\n— Bob', date: '2026-04-02', read: true, starred: true, folder: 'inbox' },
  { id: uid(), from: 'carol@eoffice.com', to: 'me@eoffice.com', subject: 'Design Assets Ready', body: 'Hi,\n\nThe design assets for the new landing page are ready for development.\n\nYou can find them in the shared drive.\n\nThanks,\nCarol', date: '2026-04-01', read: true, starred: false, folder: 'inbox' },
  { id: uid(), from: 'me@eoffice.com', to: 'team@eoffice.com', subject: 'Sprint Recap', body: 'Team,\n\nGreat work this sprint! We completed 15 story points and shipped 3 features.\n\nSee you at the retro tomorrow.\n\nCheers', date: '2026-03-31', read: true, starred: false, folder: 'sent' },
];

export function useMailbox() {
  const [messages, setMessages] = useState<Email[]>(SAMPLE_EMAILS);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [currentFolder, setCurrentFolder] = useState<Folder>('inbox');

  const selectedEmail = messages.find((m) => m.id === selectedId) || null;
  const folderMessages = messages.filter((m) => m.folder === currentFolder);
  const unreadCount = messages.filter((m) => m.folder === 'inbox' && !m.read).length;

  const addMessage = useCallback((email: Omit<Email, 'id'>) => {
    const newEmail = { ...email, id: uid() };
    setMessages((prev) => [newEmail, ...prev]);
    return newEmail;
  }, []);

  const deleteMessage = useCallback((id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
    setSelectedId((prev) => (prev === id ? null : prev));
  }, []);

  const markRead = useCallback((id: string) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, read: true } : m)));
  }, []);

  const toggleStar = useCallback((id: string) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, starred: !m.starred } : m)));
  }, []);

  const selectEmail = useCallback((id: string) => {
    setSelectedId(id);
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, read: true } : m)));
  }, []);

  return {
    messages,
    folderMessages,
    selectedEmail,
    selectedId,
    currentFolder,
    unreadCount,
    setCurrentFolder,
    selectEmail,
    addMessage,
    deleteMessage,
    markRead,
    toggleStar,
  };
}
