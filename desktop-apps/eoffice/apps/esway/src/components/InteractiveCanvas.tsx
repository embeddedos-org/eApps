import type { Slide } from '../hooks/useSway';

interface InteractiveCanvasProps {
  slide: Slide | null;
  onVote: (slideId: string, optionIdx: number) => void;
}

export default function InteractiveCanvas({ slide, onVote }: InteractiveCanvasProps) {
  if (!slide) {
    return (
      <div className="canvas">
        <div className="canvas-empty">
          <div className="canvas-empty-icon">🎯</div>
          <div>Select a slide or create a new one</div>
        </div>
      </div>
    );
  }

  const labels = ['A', 'B', 'C', 'D', 'E', 'F'];

  return (
    <div className="canvas">
      <div className="canvas-card">
        <span className={`canvas-type ${slide.type}`}>{slide.type}</span>
        <div className="canvas-question">{slide.question}</div>
        <div className="canvas-options">
          {slide.options.map((opt, i) => (
            <div
              key={i}
              className="canvas-option"
              onClick={() => onVote(slide.id, i)}
            >
              <span className="canvas-option-label">{labels[i]}</span>
              {opt.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
