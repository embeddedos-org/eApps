import type { Slide } from '../hooks/useSway';

interface SlideListProps {
  slides: Slide[];
  currentSlideId: string;
  onSelect: (id: string) => void;
  onAdd: () => void;
}

export default function SlideList({ slides, currentSlideId, onSelect, onAdd }: SlideListProps) {
  return (
    <div className="slide-list">
      <div className="slide-list-header">
        <span>Slides</span>
        <button className="slide-list-add" onClick={onAdd} title="Add slide">+</button>
      </div>
      <div className="slide-list-items">
        {slides.map((slide, i) => (
          <div
            key={slide.id}
            className={`slide-item ${slide.id === currentSlideId ? 'active' : ''}`}
            onClick={() => onSelect(slide.id)}
          >
            <div className="slide-item-number">{i + 1}</div>
            <div className="slide-item-info">
              <div className="slide-item-title">{slide.question}</div>
            </div>
            <span className={`slide-type-badge ${slide.type}`}>{slide.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
