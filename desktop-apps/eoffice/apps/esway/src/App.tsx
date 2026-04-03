import { useState } from 'react';
import TopBar from './components/TopBar';
import SlideList from './components/SlideList';
import InteractiveCanvas from './components/InteractiveCanvas';
import ResponseView from './components/ResponseView';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useSway } from './hooks/useSway';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [ebotOpen, setEbotOpen] = useState(false);
  const sway = useSway();
  const ebot = useEBot();

  const handleAddSlide = () => {
    sway.addSlide('poll', 'New question?', ['Option A', 'Option B', 'Option C']);
  };

  const handlePresent = () => {
    alert('Presenting! (Full-screen presentation mode coming soon)');
  };

  return (
    <div className="esway-app">
      <TopBar
        onPresent={handlePresent}
        ebotOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={ebot.connected}
      />
      <div className="esway-body">
        <SlideList
          slides={sway.slides}
          currentSlideId={sway.currentSlideId}
          onSelect={sway.setCurrentSlideId}
          onAdd={handleAddSlide}
        />
        <div className="esway-main">
          <InteractiveCanvas
            slide={sway.currentSlide}
            onVote={sway.submitResponse}
          />
          <ResponseView slide={sway.currentSlide} />
        </div>
        <EBotSidebar
          open={ebotOpen}
          connected={ebot.connected}
          loading={ebot.loading}
          onClose={() => setEbotOpen(false)}
          onGenerateQuiz={ebot.generateQuiz}
          onSuggestPoll={ebot.suggestPoll}
        />
      </div>
      <StatusBar
        slideCount={sway.slides.length}
        totalResponses={sway.totalResponses}
        connected={ebot.connected}
      />
    </div>
  );
}
