import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NoteBook } from '../note-model';

describe('NoteBook', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('constructor creates empty notebook', () => {
    const nb = new NoteBook();
    expect(nb.notes).toEqual([]);
  });

  it('constructor accepts initial notes', () => {
    const now = new Date();
    const notes = [
      {
        id: '1',
        title: 'Existing',
        content: 'Content',
        tags: [],
        created_at: now,
        updated_at: now,
        pinned: false,
      },
    ];
    const nb = new NoteBook(notes);
    expect(nb.notes).toHaveLength(1);
    expect(nb.notes[0].title).toBe('Existing');
  });

  describe('addNote', () => {
    it('creates note with id and timestamp', () => {
      const now = new Date('2025-01-15T10:00:00Z');
      vi.setSystemTime(now);

      const nb = new NoteBook();
      const note = nb.addNote('My Note', 'Content here');

      expect(note.id).toBeDefined();
      expect(note.id.length).toBe(36);
      expect(note.title).toBe('My Note');
      expect(note.content).toBe('Content here');
      expect(note.tags).toEqual([]);
      expect(note.pinned).toBe(false);
      expect(note.created_at).toEqual(now);
      expect(note.updated_at).toEqual(now);
      expect(nb.notes).toHaveLength(1);
    });

    it('creates note with tags', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Tagged', 'Content', ['work', 'urgent']);
      expect(note.tags).toEqual(['work', 'urgent']);
    });

    it('creates pinned note', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Pinned', 'Important', [], true);
      expect(note.pinned).toBe(true);
    });
  });

  describe('removeNote', () => {
    it('removes correct note by id', () => {
      const nb = new NoteBook();
      const n1 = nb.addNote('First', 'Content 1');
      const n2 = nb.addNote('Second', 'Content 2');
      const n3 = nb.addNote('Third', 'Content 3');

      const result = nb.removeNote(n2.id);
      expect(result).toBe(true);
      expect(nb.notes).toHaveLength(2);
      expect(nb.notes[0].id).toBe(n1.id);
      expect(nb.notes[1].id).toBe(n3.id);
    });

    it('returns false when note id does not exist', () => {
      const nb = new NoteBook();
      nb.addNote('Note', 'Content');
      expect(nb.removeNote('nonexistent')).toBe(false);
      expect(nb.notes).toHaveLength(1);
    });

    it('returns false for empty notebook', () => {
      const nb = new NoteBook();
      expect(nb.removeNote('any')).toBe(false);
    });
  });

  describe('updateNote', () => {
    it('modifies note title', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Original', 'Content');
      const result = nb.updateNote(note.id, { title: 'Updated Title' });
      expect(result).toBe(true);
      expect(nb.notes[0].title).toBe('Updated Title');
    });

    it('modifies note content', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Title', 'Old content');
      nb.updateNote(note.id, { content: 'New content' });
      expect(nb.notes[0].content).toBe('New content');
    });

    it('modifies note tags', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Title', 'Content', ['old']);
      nb.updateNote(note.id, { tags: ['new', 'updated'] });
      expect(nb.notes[0].tags).toEqual(['new', 'updated']);
    });

    it('modifies pinned state', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Title', 'Content');
      nb.updateNote(note.id, { pinned: true });
      expect(nb.notes[0].pinned).toBe(true);
    });

    it('updates updated_at timestamp', () => {
      const t1 = new Date('2025-01-01T00:00:00Z');
      vi.setSystemTime(t1);
      const nb = new NoteBook();
      const note = nb.addNote('Title', 'Content');

      const t2 = new Date('2025-06-15T12:00:00Z');
      vi.setSystemTime(t2);
      nb.updateNote(note.id, { content: 'Changed' });

      expect(nb.notes[0].updated_at).toEqual(t2);
      expect(nb.notes[0].created_at).toEqual(t1);
    });

    it('returns false when note id does not exist', () => {
      const nb = new NoteBook();
      expect(nb.updateNote('nonexistent', { title: 'x' })).toBe(false);
    });
  });

  describe('findByTag', () => {
    it('returns matching notes', () => {
      const nb = new NoteBook();
      nb.addNote('Work note', 'Content', ['work', 'important']);
      nb.addNote('Personal note', 'Content', ['personal']);
      nb.addNote('Another work', 'Content', ['work']);

      const results = nb.findByTag('work');
      expect(results).toHaveLength(2);
      expect(results[0].title).toBe('Work note');
      expect(results[1].title).toBe('Another work');
    });

    it('is case-insensitive', () => {
      const nb = new NoteBook();
      nb.addNote('Note', 'Content', ['JavaScript']);
      const results = nb.findByTag('javascript');
      expect(results).toHaveLength(1);
    });

    it('returns empty array when no match', () => {
      const nb = new NoteBook();
      nb.addNote('Note', 'Content', ['work']);
      expect(nb.findByTag('nonexistent')).toEqual([]);
    });

    it('returns empty array for empty notebook', () => {
      const nb = new NoteBook();
      expect(nb.findByTag('anything')).toEqual([]);
    });
  });

  describe('search', () => {
    it('finds notes by title', () => {
      const nb = new NoteBook();
      nb.addNote('Meeting Notes', 'Discussed project');
      nb.addNote('Shopping List', 'Buy groceries');

      const results = nb.search('meeting');
      expect(results).toHaveLength(1);
      expect(results[0].title).toBe('Meeting Notes');
    });

    it('finds notes by content', () => {
      const nb = new NoteBook();
      nb.addNote('Note 1', 'Contains keyword banana');
      nb.addNote('Note 2', 'No match');

      const results = nb.search('banana');
      expect(results).toHaveLength(1);
      expect(results[0].title).toBe('Note 1');
    });

    it('is case-insensitive', () => {
      const nb = new NoteBook();
      nb.addNote('UPPERCASE', 'lowercase content');

      expect(nb.search('uppercase')).toHaveLength(1);
      expect(nb.search('LOWERCASE')).toHaveLength(1);
    });

    it('returns empty array when no match', () => {
      const nb = new NoteBook();
      nb.addNote('Note', 'Content');
      expect(nb.search('zzzzz')).toEqual([]);
    });

    it('matches partial strings', () => {
      const nb = new NoteBook();
      nb.addNote('Documentation', 'Guide for developers');
      expect(nb.search('doc')).toHaveLength(1);
      expect(nb.search('develop')).toHaveLength(1);
    });
  });

  describe('sortByDate', () => {
    it('sorts descending by default (newest first)', () => {
      const nb = new NoteBook();

      vi.setSystemTime(new Date('2025-01-01'));
      nb.addNote('Old', 'Content');

      vi.setSystemTime(new Date('2025-06-01'));
      nb.addNote('Middle', 'Content');

      vi.setSystemTime(new Date('2025-12-01'));
      nb.addNote('New', 'Content');

      const sorted = nb.sortByDate();
      expect(sorted[0].title).toBe('New');
      expect(sorted[1].title).toBe('Middle');
      expect(sorted[2].title).toBe('Old');
    });

    it('sorts ascending when ascending=true', () => {
      const nb = new NoteBook();

      vi.setSystemTime(new Date('2025-01-01'));
      nb.addNote('Old', 'Content');

      vi.setSystemTime(new Date('2025-06-01'));
      nb.addNote('Middle', 'Content');

      vi.setSystemTime(new Date('2025-12-01'));
      nb.addNote('New', 'Content');

      const sorted = nb.sortByDate(true);
      expect(sorted[0].title).toBe('Old');
      expect(sorted[1].title).toBe('Middle');
      expect(sorted[2].title).toBe('New');
    });

    it('does not mutate the original notes array', () => {
      const nb = new NoteBook();

      vi.setSystemTime(new Date('2025-01-01'));
      nb.addNote('Old', 'Content');

      vi.setSystemTime(new Date('2025-12-01'));
      nb.addNote('New', 'Content');

      const sorted = nb.sortByDate();
      expect(sorted).not.toBe(nb.notes);
      expect(nb.notes[0].title).toBe('Old');
    });
  });

  describe('toJSON / fromJSON roundtrip', () => {
    it('preserves data through serialization', () => {
      const t = new Date('2025-03-15T10:30:00Z');
      vi.setSystemTime(t);

      const nb = new NoteBook();
      nb.addNote('Important', 'Some content', ['work', 'urgent'], true);
      nb.addNote('Casual', 'Other content', ['personal']);

      const json = nb.toJSON() as any;
      const restored = NoteBook.fromJSON(json);

      expect(restored.notes).toHaveLength(2);
      expect(restored.notes[0].title).toBe('Important');
      expect(restored.notes[0].content).toBe('Some content');
      expect(restored.notes[0].tags).toEqual(['work', 'urgent']);
      expect(restored.notes[0].pinned).toBe(true);
      expect(restored.notes[0].created_at).toEqual(t);
      expect(restored.notes[0].updated_at).toEqual(t);
      expect(restored.notes[1].title).toBe('Casual');
      expect(restored.notes[1].pinned).toBe(false);
    });

    it('preserves note ids through roundtrip', () => {
      const nb = new NoteBook();
      const note = nb.addNote('Test', 'Content');
      const json = nb.toJSON() as any;
      const restored = NoteBook.fromJSON(json);
      expect(restored.notes[0].id).toBe(note.id);
    });

    it('handles empty notebook roundtrip', () => {
      const nb = new NoteBook();
      const json = nb.toJSON() as any;
      const restored = NoteBook.fromJSON(json);
      expect(restored.notes).toEqual([]);
    });

    it('serializes dates as ISO strings', () => {
      const nb = new NoteBook();
      nb.addNote('Test', 'Content');
      const json = nb.toJSON() as any;
      expect(typeof json.notes[0].created_at).toBe('string');
      expect(typeof json.notes[0].updated_at).toBe('string');
    });
  });
});
