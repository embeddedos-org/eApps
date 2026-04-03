import type { DocumentBlock, BlockType, TextStyle } from './types';
import { generateId } from './utils';

export class DocumentModel {
  public blocks: DocumentBlock[];

  constructor(blocks: DocumentBlock[] = []) {
    this.blocks = blocks;
  }

  addBlock(
    type: BlockType,
    content: string,
    style?: TextStyle,
  ): DocumentBlock {
    const block: DocumentBlock = {
      id: generateId(),
      type,
      content,
      style,
    };
    this.blocks.push(block);
    return block;
  }

  removeBlock(id: string): boolean {
    const index = this.blocks.findIndex((b) => b.id === id);
    if (index === -1) return false;
    this.blocks.splice(index, 1);
    return true;
  }

  updateBlock(
    id: string,
    updates: Partial<Omit<DocumentBlock, 'id'>>,
  ): boolean {
    const block = this.blocks.find((b) => b.id === id);
    if (!block) return false;
    if (updates.type !== undefined) block.type = updates.type;
    if (updates.content !== undefined) block.content = updates.content;
    if (updates.style !== undefined) block.style = updates.style;
    return true;
  }

  getPlainText(): string {
    return this.blocks.map((b) => b.content).join('\n');
  }

  getWordCount(): number {
    const text = this.getPlainText().trim();
    if (text.length === 0) return 0;
    return text.split(/\s+/).length;
  }

  getCharCount(): number {
    return this.getPlainText().length;
  }

  toJSON(): object {
    return {
      blocks: this.blocks.map((block) => ({
        id: block.id,
        type: block.type,
        content: block.content,
        style: block.style,
      })),
    };
  }

  static fromJSON(json: { blocks: DocumentBlock[] }): DocumentModel {
    return new DocumentModel(
      json.blocks.map((b) => ({
        id: b.id,
        type: b.type,
        content: b.content,
        style: b.style,
      })),
    );
  }
}
