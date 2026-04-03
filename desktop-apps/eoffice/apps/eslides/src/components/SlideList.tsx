import type { Slide } from '../hooks/usePresentation';

interface SlideListProps {
  slides: Slide[];
  currentIndex: number;
  onSelect: (index: number) => void;
  onAdd: () => void;
  onDuplicate: (index: number) => void;
  onRemove: (index: number) => void;
}

export default function SlideList({
  slides,
  currentIndex,
  onSelect,
  onAdd,
  onDuplicate,
  onRemove,
}: SlideListProps) {
  return (
    <div className="slide-panel">
      <div className="slide-panel-header">
        <span>Slides</span>
        <div className="slide-panel-actions">
          <button className="slide-panel-btn" onClick={onAdd} title="Add Slide">+</button>
          <button
            className="slide-panel-btn"
            onClick={() => onDuplicate(currentIndex)}
            title="Duplicate"
          >
            ⧉
          </button>
          <button
            className="slide-panel-btn"
            onClick={() => onRemove(currentIndex)}
            title="Delete"
            disabled={slides.length <= 1}
          >
            🗑
          </button>
        </div>
      </div>
      <div className="slide-list">
        {slides.map((slide, i) => (
          <div
            key={slide.id}
            className={`slide-thumb ${i === currentIndex ? 'active' : ''}`}
            onClick={() => onSelect(i)}
          >
            <div className="slide-thumb-content">
              {slide.elements.length > 0
                ? slide.elements.map((el) => (
                    <span key={el.id} style={{ fontSize: 7 }}>
                      {el.type === 'text' ? el.content.slice(0, 20) : '■'}
                    </span>
                  ))
                : 'Empty slide'}
            </div>
            <span className="slide-thumb-number">{i + 1}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
