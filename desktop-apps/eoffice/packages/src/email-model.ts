import type { EmailMessage, CalendarEvent } from './types';
import { generateId } from './utils';

export class MailboxModel {
  public messages: EmailMessage[];
  public events: CalendarEvent[];

  constructor(messages: EmailMessage[] = [], events: CalendarEvent[] = []) {
    this.messages = messages;
    this.events = events;
  }

  addMessage(from: string, to: string[], subject: string, body: string): EmailMessage {
    const msg: EmailMessage = {
      id: generateId(), from, to, subject, body,
      read: false, starred: false, folder: 'inbox', created_at: new Date(),
    };
    this.messages.push(msg);
    return msg;
  }

  deleteMessage(id: string): boolean {
    const index = this.messages.findIndex((m) => m.id === id);
    if (index === -1) return false;
    this.messages.splice(index, 1);
    return true;
  }

  markRead(id: string): boolean {
    const msg = this.messages.find((m) => m.id === id);
    if (!msg) return false;
    msg.read = true;
    return true;
  }

  toggleStar(id: string): boolean {
    const msg = this.messages.find((m) => m.id === id);
    if (!msg) return false;
    msg.starred = !msg.starred;
    return true;
  }

  moveToFolder(id: string, folder: string): boolean {
    const msg = this.messages.find((m) => m.id === id);
    if (!msg) return false;
    msg.folder = folder;
    return true;
  }

  getByFolder(folder: string): EmailMessage[] {
    return this.messages.filter((m) => m.folder === folder);
  }

  addEvent(title: string, start: Date, end: Date, description?: string, location?: string, attendees: string[] = []): CalendarEvent {
    const event: CalendarEvent = { id: generateId(), title, start, end, description, location, attendees };
    this.events.push(event);
    return event;
  }

  removeEvent(id: string): boolean {
    const index = this.events.findIndex((e) => e.id === id);
    if (index === -1) return false;
    this.events.splice(index, 1);
    return true;
  }

  getEventsInRange(start: Date, end: Date): CalendarEvent[] {
    return this.events.filter((e) => e.start >= start && e.end <= end);
  }

  toJSON(): object {
    return { messages: this.messages, events: this.events };
  }

  static fromJSON(json: { messages: EmailMessage[]; events: CalendarEvent[] }): MailboxModel {
    return new MailboxModel(
      json.messages.map((m) => ({ ...m, created_at: new Date(m.created_at) })),
      json.events.map((e) => ({ ...e, start: new Date(e.start), end: new Date(e.end) })),
    );
  }
}
