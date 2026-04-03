import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { Note } from '../App';

interface NoteEditorProps {
  note: Note;
  onUpdate: (id: string, updates: Partial<Omit<Note, 'id' | 'createdAt'>>) => void;
}

export default function NoteEditor({ note, onUpdate }: NoteEditorProps) {
  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content);
  const [tagInput, setTagInput] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setTitle(note.title);
    setContent(note.content);
    setTagInput('');
  }, [note.id, note.title, note.content]);

  const autoResize = useCallback(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = `${Math.max(ta.scrollHeight, 300)}px`;
    }
  }, []);

  useEffect(() => {
    autoResize();
  }, [content, autoResize]);

  const debouncedUpdate = useCallback(
    (field: 'title' | 'content', value: string) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onUpdate(note.id, { [field]: value });
      }, 400);
    },
    [note.id, onUpdate],
  );

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setTitle(val);
    debouncedUpdate('title', val);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);
    debouncedUpdate('content', val);
  };

  const addTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !note.tags.includes(tag)) {
      onUpdate(note.id, { tags: [...note.tags, tag] });
    }
    setTagInput('');
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag();
    }
  };

  const removeTag = (tag: string) => {
    onUpdate(note.id, { tags: note.tags.filter((t) => t !== tag) });
  };

  const lastModified = new Date(note.updatedAt).toLocaleString();

  return (
    <div className="note-editor">
      <input
        type="text"
        className="note-title-input"
        placeholder="Note title…"
        value={title}
        onChange={handleTitleChange}
        autoFocus
      />

      <div className="tag-bar">
        {note.tags.map((tag) => (
          <span key={tag} className="tag-pill">
            {tag}
            <button className="tag-remove" onClick={() => removeTag(tag)}>
              ×
            </button>
          </span>
        ))}
        <input
          type="text"
          className="tag-input"
          placeholder="Add tag…"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
          onKeyDown={handleTagKeyDown}
          onBlur={addTag}
        />
      </div>

      <textarea
        ref={textareaRef}
        className="note-content-input"
        placeholder="Start writing…"
        value={content}
        onChange={handleContentChange}
      />

      <div className="editor-footer">
        <span className="last-modified">Last modified: {lastModified}</span>
        <span className="char-count">{content.length} chars</span>
      </div>
    </div>
  );
}
