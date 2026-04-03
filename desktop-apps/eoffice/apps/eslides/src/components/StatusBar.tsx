interface StatusBarProps {
  slideCount: number;
  currentSlide: number;
  connected: boolean;
}

export default function StatusBar({ slideCount, currentSlide, connected }: StatusBarProps) {
  return (
    <div className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">Slide {currentSlide} of {slideCount}</span>
      </div>
      <div className="statusbar-right">
        <span className={`statusbar-connection ${connected ? 'connected' : 'disconnected'}`}>
          <span className="statusbar-dot" />
          <span>eBot</span>
        </span>
      </div>
    </div>
  );
}
