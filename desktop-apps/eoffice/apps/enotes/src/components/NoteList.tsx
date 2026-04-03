import React, { useState } from 'react';
import type { Note } from '../App';

interface NoteListProps {
  notes: Note[];
  selectedNoteId: string | null;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSelectNote: (id: string) => void;
  onCreateNote: () => void;
  onDeleteNote: (id: string) => void;
  onTogglePin: (id: string) => void;
}

function formatDate(ts: number): string {
  const d = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString();
}

function getPreview(content: string, maxLen = 80): string {
  const text = content.replace(/\n/g, ' ').trim();
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '…';
}

export default function NoteList({
  notes,
  selectedNoteId,
  searchQuery,
  onSearchChange,
  onSelectNote,
  onCreateNote,
  onDeleteNote,
  onTogglePin,
}: NoteListProps) {
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (deleteConfirmId === id) {
      onDeleteNote(id);
      setDeleteConfirmId(null);
    } else {
      setDeleteConfirmId(id);
      setTimeout(() => setDeleteConfirmId(null), 3000);
    }
  };

  const handlePin = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    onTogglePin(id);
  };

  return (
    <aside className="note-list-panel">
      <div className="note-list-header">
        <h1 className="app-title">📝 eNotes</h1>
        <button className="btn-new-note" onClick={onCreateNote} title="New Note">
          +
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search notes…"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="search-input"
        />
        {searchQuery && (
          <button className="search-clear" onClick={() => onSearchChange('')}>
            ×
          </button>
        )}
      </div>

      <div className="note-list-scroll">
        {notes.length === 0 ? (
          <div className="note-list-empty">
            {searchQuery ? 'No matching notes.' : 'No notes yet. Create one!'}
          </div>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className={`note-list-item ${selectedNoteId === note.id ? 'selected' : ''} ${note.pinned ? 'pinned' : ''}`}
              onClick={() => onSelectNote(note.id)}
            >
              <div className="note-item-header">
                <span className="note-item-title">
                  {note.pinned && <span className="pin-icon">📌 </span>}
                  {note.title || 'Untitled Note'}
                </span>
                <span className="note-item-date">{formatDate(note.updatedAt)}</span>
              </div>
              <div className="note-item-preview">
                {getPreview(note.content) || 'Empty note'}
              </div>
              {note.tags.length > 0 && (
                <div className="note-item-tags">
                  {note.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="tag-mini">
                      {tag}
                    </span>
                  ))}
                  {note.tags.length > 3 && (
                    <span className="tag-mini tag-more">+{note.tags.length - 3}</span>
                  )}
                </div>
              )}
              <div className="note-item-actions">
                <button
                  className="btn-icon"
                  onClick={(e) => handlePin(e, note.id)}
                  title={note.pinned ? 'Unpin' : 'Pin'}
                >
                  {note.pinned ? '📌' : '📍'}
                </button>
                <button
                  className={`btn-icon btn-delete ${deleteConfirmId === note.id ? 'confirm' : ''}`}
                  onClick={(e) => handleDelete(e, note.id)}
                  title={deleteConfirmId === note.id ? 'Click again to confirm' : 'Delete'}
                >
                  {deleteConfirmId === note.id ? '⚠️' : '🗑️'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
