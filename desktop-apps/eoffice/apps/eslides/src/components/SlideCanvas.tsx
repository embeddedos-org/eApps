import React from 'react';
import type { Slide, SlideElement } from '../hooks/usePresentation';

interface SlideCanvasProps {
  slide: Slide;
  selectedElementId: string | null;
  onSelectElement: (id: string | null) => void;
  onUpdateElement: (id: string, updates: Partial<SlideElement>) => void;
  onAddElement: (type: 'text' | 'shape', content: string) => void;
}

export default function SlideCanvas({
  slide,
  selectedElementId,
  onSelectElement,
  onUpdateElement,
  onAddElement,
}: SlideCanvasProps) {
  const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onSelectElement(null);
    }
  };

  const handleDoubleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onAddElement('text', 'Click to edit');
    }
  };

  return (
    <div className="canvas-area">
      <div
        className="slide-canvas"
        onClick={handleCanvasClick}
        onDoubleClick={handleDoubleClick}
      >
        {slide.elements.length === 0 ? (
          <div className="canvas-placeholder">
            <div className="canvas-placeholder-icon">📽️</div>
            <div className="canvas-placeholder-text">Double-click to add text</div>
          </div>
        ) : (
          slide.elements.map((el) => (
            <div
              key={el.id}
              className={`slide-element ${el.id === selectedElementId ? 'selected' : ''}`}
              style={{
                left: `${el.x}%`,
                top: `${el.y}%`,
                width: `${el.width}%`,
                height: `${el.height}%`,
                background: el.type === 'shape' ? (el.color || '#ea580c') : 'transparent',
                borderRadius: el.type === 'shape' ? '4px' : undefined,
              }}
              onClick={(e) => {
                e.stopPropagation();
                onSelectElement(el.id);
              }}
            >
              {el.type === 'text' ? (
                <div
                  className="slide-element-text"
                  contentEditable
                  suppressContentEditableWarning
                  onBlur={(e) =>
                    onUpdateElement(el.id, { content: e.currentTarget.textContent || '' })
                  }
                  style={{ fontSize: '14px' }}
                >
                  {el.content}
                </div>
              ) : (
                <div className="slide-element-shape">{el.content || '■'}</div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
