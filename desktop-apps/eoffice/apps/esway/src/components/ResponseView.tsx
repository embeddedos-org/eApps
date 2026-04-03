import type { Slide } from '../hooks/useSway';

const BAR_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

interface ResponseViewProps {
  slide: Slide | null;
}

export default function ResponseView({ slide }: ResponseViewProps) {
  if (!slide || slide.options.every((o) => o.votes === 0)) return null;

  const maxVotes = Math.max(...slide.options.map((o) => o.votes), 1);
  const totalVotes = slide.options.reduce((s, o) => s + o.votes, 0);

  return (
    <div className="response-view">
      <div className="response-view-title">Responses ({totalVotes} total)</div>
      {slide.options.map((opt, i) => (
        <div key={i} className="response-bar-row">
          <div className="response-bar-label">{opt.text}</div>
          <div className="response-bar-track">
            <div
              className="response-bar-fill"
              style={{
                width: `${(opt.votes / maxVotes) * 100}%`,
                background: BAR_COLORS[i % BAR_COLORS.length],
              }}
            />
          </div>
          <div className="response-bar-count">{opt.votes}</div>
        </div>
      ))}
    </div>
  );
}
