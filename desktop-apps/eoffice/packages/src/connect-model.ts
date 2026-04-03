import type { Channel, ChannelMessage } from './types';
import { generateId } from './utils';

export class ConnectModel {
  public channels: Channel[];
  public messages: ChannelMessage[];

  constructor(channels: Channel[] = [], messages: ChannelMessage[] = []) {
    this.channels = channels;
    this.messages = messages;
  }

  addChannel(name: string, description: string): Channel {
    const channel: Channel = { id: generateId(), name, description, members: [], created_at: new Date() };
    this.channels.push(channel);
    return channel;
  }

  removeChannel(id: string): boolean {
    const index = this.channels.findIndex((c) => c.id === id);
    if (index === -1) return false;
    this.channels.splice(index, 1);
    this.messages = this.messages.filter((m) => m.channelId !== id);
    return true;
  }

  addMember(channelId: string, member: string): boolean {
    const channel = this.channels.find((c) => c.id === channelId);
    if (!channel) return false;
    if (channel.members.includes(member)) return false;
    channel.members.push(member);
    return true;
  }

  removeMember(channelId: string, member: string): boolean {
    const channel = this.channels.find((c) => c.id === channelId);
    if (!channel) return false;
    const index = channel.members.indexOf(member);
    if (index === -1) return false;
    channel.members.splice(index, 1);
    return true;
  }

  sendMessage(channelId: string, author: string, content: string): ChannelMessage | undefined {
    if (!this.channels.find((c) => c.id === channelId)) return undefined;
    const msg: ChannelMessage = { id: generateId(), channelId, author, content, created_at: new Date() };
    this.messages.push(msg);
    return msg;
  }

  getMessages(channelId: string): ChannelMessage[] {
    return this.messages.filter((m) => m.channelId === channelId);
  }

  deleteMessage(id: string): boolean {
    const index = this.messages.findIndex((m) => m.id === id);
    if (index === -1) return false;
    this.messages.splice(index, 1);
    return true;
  }

  toJSON(): object {
    return { channels: this.channels, messages: this.messages };
  }

  static fromJSON(json: { channels: Channel[]; messages: ChannelMessage[] }): ConnectModel {
    return new ConnectModel(
      json.channels.map((c) => ({ ...c, created_at: new Date(c.created_at) })),
      json.messages.map((m) => ({ ...m, created_at: new Date(m.created_at) })),
    );
  }
}
