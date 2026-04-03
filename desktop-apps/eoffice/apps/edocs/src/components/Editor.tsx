import React, { forwardRef, useCallback, useEffect, useRef } from 'react';

interface EditorProps {
  content: string;
  onChange: (content: string) => void;
  onCursorChange: (line: number, col: number) => void;
}

const Editor = forwardRef<HTMLDivElement, EditorProps>(
  ({ onChange, onCursorChange }, ref) => {
    const internalRef = useRef<HTMLDivElement>(null);
    const editorEl = (ref as React.RefObject<HTMLDivElement>) || internalRef;

    const handleInput = useCallback(() => {
      const el = editorEl.current;
      if (el) {
        onChange(el.innerText);
      }
    }, [editorEl, onChange]);

    const updateCursorPosition = useCallback(() => {
      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0) return;

      const range = selection.getRangeAt(0);
      const el = editorEl.current;
      if (!el) return;

      const preCaretRange = range.cloneRange();
      preCaretRange.selectNodeContents(el);
      preCaretRange.setEnd(range.endContainer, range.endOffset);

      const textBeforeCaret = preCaretRange.toString();
      const lines = textBeforeCaret.split('\n');
      const line = lines.length;
      const col = (lines[lines.length - 1]?.length ?? 0) + 1;

      onCursorChange(line, col);
    }, [editorEl, onCursorChange]);

    useEffect(() => {
      const el = editorEl.current;
      if (!el) return;

      const handleKeyUp = () => updateCursorPosition();
      const handleMouseUp = () => updateCursorPosition();

      el.addEventListener('keyup', handleKeyUp);
      el.addEventListener('mouseup', handleMouseUp);

      return () => {
        el.removeEventListener('keyup', handleKeyUp);
        el.removeEventListener('mouseup', handleMouseUp);
      };
    }, [editorEl, updateCursorPosition]);

    return (
      <main className="editor-container">
        <div className="editor-paper">
          <div
            ref={editorEl}
            className="editor-content"
            contentEditable
            suppressContentEditableWarning
            role="textbox"
            aria-multiline="true"
            aria-label="Document editor"
            data-placeholder="Start typing your document..."
            onInput={handleInput}
            onKeyUp={updateCursorPosition}
            onMouseUp={updateCursorPosition}
            spellCheck
          />
        </div>
      </main>
    );
  }
);

Editor.displayName = 'Editor';

export default Editor;
