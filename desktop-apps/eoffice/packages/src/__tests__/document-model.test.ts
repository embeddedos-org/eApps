import { describe, it, expect } from 'vitest';
import { DocumentModel } from '../document-model';

describe('DocumentModel', () => {
  it('constructor creates empty document with no blocks', () => {
    const doc = new DocumentModel();
    expect(doc.blocks).toEqual([]);
  });

  it('constructor accepts initial blocks', () => {
    const blocks = [
      { id: '1', type: 'paragraph' as const, content: 'Hello' },
    ];
    const doc = new DocumentModel(blocks);
    expect(doc.blocks).toHaveLength(1);
    expect(doc.blocks[0].content).toBe('Hello');
  });

  describe('addBlock', () => {
    it('adds a block with a generated id', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'Test content');
      expect(block.id).toBeDefined();
      expect(typeof block.id).toBe('string');
      expect(block.id.length).toBe(36);
      expect(block.type).toBe('paragraph');
      expect(block.content).toBe('Test content');
      expect(doc.blocks).toHaveLength(1);
    });

    it('adds multiple blocks in order', () => {
      const doc = new DocumentModel();
      doc.addBlock('heading', 'Title');
      doc.addBlock('paragraph', 'Body');
      doc.addBlock('code', 'console.log("hi")');
      expect(doc.blocks).toHaveLength(3);
      expect(doc.blocks[0].content).toBe('Title');
      expect(doc.blocks[1].content).toBe('Body');
      expect(doc.blocks[2].content).toBe('console.log("hi")');
    });

    it('adds a block with style', () => {
      const doc = new DocumentModel();
      const style = { bold: true, fontSize: 16, color: '#ff0000' };
      const block = doc.addBlock('heading', 'Styled heading', style);
      expect(block.style).toEqual(style);
    });

    it('adds a block without style (undefined)', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'No style');
      expect(block.style).toBeUndefined();
    });
  });

  describe('removeBlock', () => {
    it('removes the correct block by id', () => {
      const doc = new DocumentModel();
      const b1 = doc.addBlock('paragraph', 'First');
      const b2 = doc.addBlock('paragraph', 'Second');
      const b3 = doc.addBlock('paragraph', 'Third');

      const result = doc.removeBlock(b2.id);
      expect(result).toBe(true);
      expect(doc.blocks).toHaveLength(2);
      expect(doc.blocks[0].id).toBe(b1.id);
      expect(doc.blocks[1].id).toBe(b3.id);
    });

    it('returns false when block id does not exist', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'Content');
      const result = doc.removeBlock('nonexistent-id');
      expect(result).toBe(false);
      expect(doc.blocks).toHaveLength(1);
    });

    it('returns false for empty document', () => {
      const doc = new DocumentModel();
      expect(doc.removeBlock('any-id')).toBe(false);
    });
  });

  describe('updateBlock', () => {
    it('modifies block content', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'Original');
      const result = doc.updateBlock(block.id, { content: 'Updated' });
      expect(result).toBe(true);
      expect(doc.blocks[0].content).toBe('Updated');
    });

    it('modifies block type', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'Text');
      doc.updateBlock(block.id, { type: 'heading' });
      expect(doc.blocks[0].type).toBe('heading');
    });

    it('modifies block style', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'Text');
      doc.updateBlock(block.id, { style: { bold: true, italic: true } });
      expect(doc.blocks[0].style).toEqual({ bold: true, italic: true });
    });

    it('returns false when block id does not exist', () => {
      const doc = new DocumentModel();
      const result = doc.updateBlock('nonexistent', { content: 'x' });
      expect(result).toBe(false);
    });

    it('does not modify unspecified fields', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('heading', 'Title', { bold: true });
      doc.updateBlock(block.id, { content: 'New Title' });
      expect(doc.blocks[0].type).toBe('heading');
      expect(doc.blocks[0].style).toEqual({ bold: true });
    });
  });

  describe('getPlainText', () => {
    it('returns concatenated text of all blocks joined by newlines', () => {
      const doc = new DocumentModel();
      doc.addBlock('heading', 'Title');
      doc.addBlock('paragraph', 'Body text here');
      doc.addBlock('code', 'const x = 1;');
      expect(doc.getPlainText()).toBe('Title\nBody text here\nconst x = 1;');
    });

    it('returns empty string for empty document', () => {
      const doc = new DocumentModel();
      expect(doc.getPlainText()).toBe('');
    });

    it('returns single block content without trailing newline', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'Only block');
      expect(doc.getPlainText()).toBe('Only block');
    });
  });

  describe('getWordCount', () => {
    it('counts words correctly', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'Hello world');
      expect(doc.getWordCount()).toBe(2);
    });

    it('handles multiple spaces between words', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'Hello    world   test');
      expect(doc.getWordCount()).toBe(3);
    });

    it('handles newlines between blocks', () => {
      const doc = new DocumentModel();
      doc.addBlock('heading', 'Title');
      doc.addBlock('paragraph', 'Body text');
      expect(doc.getWordCount()).toBe(3);
    });

    it('returns 0 for empty document', () => {
      const doc = new DocumentModel();
      expect(doc.getWordCount()).toBe(0);
    });

    it('returns 0 for document with empty blocks', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', '');
      expect(doc.getWordCount()).toBe(0);
    });

    it('handles tabs and mixed whitespace', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'one\ttwo\n\nthree');
      expect(doc.getWordCount()).toBe(3);
    });
  });

  describe('getCharCount', () => {
    it('counts characters including spaces', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'Hello');
      expect(doc.getCharCount()).toBe(5);
    });

    it('includes newline characters between blocks', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', 'Hi');
      doc.addBlock('paragraph', 'Lo');
      // "Hi\nLo" = 5 chars
      expect(doc.getCharCount()).toBe(5);
    });

    it('returns 0 for empty document', () => {
      const doc = new DocumentModel();
      expect(doc.getCharCount()).toBe(0);
    });
  });

  describe('toJSON / fromJSON roundtrip', () => {
    it('preserves data through serialization', () => {
      const doc = new DocumentModel();
      doc.addBlock('heading', 'Title', { bold: true, fontSize: 24 });
      doc.addBlock('paragraph', 'Body paragraph');
      doc.addBlock('code', 'const x = 42;');

      const json = doc.toJSON() as { blocks: Array<{ id: string; type: string; content: string; style?: object }> };
      const restored = DocumentModel.fromJSON(json as any);

      expect(restored.blocks).toHaveLength(3);
      expect(restored.blocks[0].type).toBe('heading');
      expect(restored.blocks[0].content).toBe('Title');
      expect(restored.blocks[0].style).toEqual({ bold: true, fontSize: 24 });
      expect(restored.blocks[1].content).toBe('Body paragraph');
      expect(restored.blocks[2].type).toBe('code');
      expect(restored.blocks[2].content).toBe('const x = 42;');
    });

    it('preserves block ids through roundtrip', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'Content');
      const json = doc.toJSON() as any;
      const restored = DocumentModel.fromJSON(json);
      expect(restored.blocks[0].id).toBe(block.id);
    });

    it('handles empty document roundtrip', () => {
      const doc = new DocumentModel();
      const json = doc.toJSON() as any;
      const restored = DocumentModel.fromJSON(json);
      expect(restored.blocks).toEqual([]);
    });
  });

  describe('edge cases', () => {
    it('handles adding and immediately removing a block', () => {
      const doc = new DocumentModel();
      const block = doc.addBlock('paragraph', 'Temp');
      doc.removeBlock(block.id);
      expect(doc.blocks).toHaveLength(0);
      expect(doc.getPlainText()).toBe('');
      expect(doc.getWordCount()).toBe(0);
    });

    it('handles blocks with empty content', () => {
      const doc = new DocumentModel();
      doc.addBlock('paragraph', '');
      doc.addBlock('paragraph', '');
      expect(doc.getPlainText()).toBe('\n');
      expect(doc.getCharCount()).toBe(1);
    });
  });
});
