import type { NoteEntry } from './types';
import { generateId } from './utils';

export class NoteBook {
  public notes: NoteEntry[];

  constructor(notes: NoteEntry[] = []) {
    this.notes = notes;
  }

  addNote(
    title: string,
    content: string,
    tags: string[] = [],
    pinned: boolean = false,
  ): NoteEntry {
    const now = new Date();
    const note: NoteEntry = {
      id: generateId(),
      title,
      content,
      tags,
      created_at: now,
      updated_at: now,
      pinned,
    };
    this.notes.push(note);
    return note;
  }

  removeNote(id: string): boolean {
    const index = this.notes.findIndex((n) => n.id === id);
    if (index === -1) return false;
    this.notes.splice(index, 1);
    return true;
  }

  updateNote(
    id: string,
    updates: Partial<Omit<NoteEntry, 'id' | 'created_at'>>,
  ): boolean {
    const note = this.notes.find((n) => n.id === id);
    if (!note) return false;
    if (updates.title !== undefined) note.title = updates.title;
    if (updates.content !== undefined) note.content = updates.content;
    if (updates.tags !== undefined) note.tags = updates.tags;
    if (updates.pinned !== undefined) note.pinned = updates.pinned;
    note.updated_at = updates.updated_at ?? new Date();
    return true;
  }

  findByTag(tag: string): NoteEntry[] {
    return this.notes.filter((n) =>
      n.tags.some((t) => t.toLowerCase() === tag.toLowerCase()),
    );
  }

  search(query: string): NoteEntry[] {
    const lower = query.toLowerCase();
    return this.notes.filter(
      (n) =>
        n.title.toLowerCase().includes(lower) ||
        n.content.toLowerCase().includes(lower),
    );
  }

  sortByDate(ascending: boolean = false): NoteEntry[] {
    return [...this.notes].sort((a, b) => {
      const diff = b.updated_at.getTime() - a.updated_at.getTime();
      return ascending ? -diff : diff;
    });
  }

  toJSON(): object {
    return {
      notes: this.notes.map((note) => ({
        id: note.id,
        title: note.title,
        content: note.content,
        tags: note.tags,
        created_at: note.created_at.toISOString(),
        updated_at: note.updated_at.toISOString(),
        pinned: note.pinned,
      })),
    };
  }

  static fromJSON(json: {
    notes: Array<{
      id: string;
      title: string;
      content: string;
      tags: string[];
      created_at: string;
      updated_at: string;
      pinned: boolean;
    }>;
  }): NoteBook {
    return new NoteBook(
      json.notes.map((n) => ({
        id: n.id,
        title: n.title,
        content: n.content,
        tags: n.tags,
        created_at: new Date(n.created_at),
        updated_at: new Date(n.updated_at),
        pinned: n.pinned,
      })),
    );
  }
}
