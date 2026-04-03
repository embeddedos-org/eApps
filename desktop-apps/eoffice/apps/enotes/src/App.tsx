import { useState, useCallback, useEffect } from 'react';
import NoteList from './components/NoteList';
import NoteEditor from './components/NoteEditor';
import EBotPanel from './components/EBotPanel';

export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  pinned: boolean;
  createdAt: number;
  updatedAt: number;
}

const STORAGE_KEY = 'enotes-data';

function generateId(): string {
  return `note-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function loadNotes(): Note[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore parse errors
  }
  return [];
}

function saveNotes(notes: Note[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
}

export default function App() {
  const [notes, setNotes] = useState<Note[]>(loadNotes);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [ebotPanelOpen, setEbotPanelOpen] = useState(false);

  const selectedNote = notes.find((n) => n.id === selectedNoteId) ?? null;

  useEffect(() => {
    saveNotes(notes);
  }, [notes]);

  const createNote = useCallback(() => {
    const now = Date.now();
    const newNote: Note = {
      id: generateId(),
      title: '',
      content: '',
      tags: [],
      pinned: false,
      createdAt: now,
      updatedAt: now,
    };
    setNotes((prev) => [newNote, ...prev]);
    setSelectedNoteId(newNote.id);
  }, []);

  const updateNote = useCallback((id: string, updates: Partial<Omit<Note, 'id' | 'createdAt'>>) => {
    setNotes((prev) =>
      prev.map((n) =>
        n.id === id ? { ...n, ...updates, updatedAt: Date.now() } : n,
      ),
    );
  }, []);

  const deleteNote = useCallback((id: string) => {
    setNotes((prev) => prev.filter((n) => n.id !== id));
    setSelectedNoteId((prev) => (prev === id ? null : prev));
  }, []);

  const togglePin = useCallback((id: string) => {
    setNotes((prev) =>
      prev.map((n) =>
        n.id === id ? { ...n, pinned: !n.pinned, updatedAt: Date.now() } : n,
      ),
    );
  }, []);

  const filteredNotes = notes
    .filter((n) => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        n.title.toLowerCase().includes(q) ||
        n.content.toLowerCase().includes(q) ||
        n.tags.some((t) => t.toLowerCase().includes(q))
      );
    })
    .sort((a, b) => {
      if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
      return b.updatedAt - a.updatedAt;
    });

  return (
    <div className="enotes-app">
      <NoteList
        notes={filteredNotes}
        selectedNoteId={selectedNoteId}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSelectNote={setSelectedNoteId}
        onCreateNote={createNote}
        onDeleteNote={deleteNote}
        onTogglePin={togglePin}
      />
      <div className="editor-area">
        {selectedNote ? (
          <>
            <NoteEditor note={selectedNote} onUpdate={updateNote} />
            <EBotPanel
              note={selectedNote}
              isOpen={ebotPanelOpen}
              onToggle={() => setEbotPanelOpen((o) => !o)}
              onApplyTags={(tags) =>
                updateNote(selectedNote.id, {
                  tags: [...new Set([...selectedNote.tags, ...tags])],
                })
              }
            />
          </>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <h2>Welcome to eNotes</h2>
            <p>Select a note or create a new one to get started.</p>
            <button className="btn-primary" onClick={createNote}>
              + New Note
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
