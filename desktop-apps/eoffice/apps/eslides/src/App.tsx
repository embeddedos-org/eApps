import { useState, useCallback } from 'react';
import TopBar from './components/TopBar';
import Toolbar from './components/Toolbar';
import SlideList from './components/SlideList';
import SlideCanvas from './components/SlideCanvas';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { usePresentation } from './hooks/usePresentation';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [title, setTitle] = useState('Untitled Presentation');
  const [ebotOpen, setEbotOpen] = useState(false);
  const [ebotResponse, setEbotResponse] = useState('');
  const [theme, setTheme] = useState('Default');

  const pres = usePresentation();
  const { connected, loading, suggestContent, generateTalkingPoints } = useEBot();

  const handlePresent = useCallback(() => {
    alert(`Presenting "${title}" — ${pres.slides.length} slides (presentation mode coming soon)`);
  }, [title, pres.slides.length]);

  const handleDeleteElement = useCallback(() => {
    if (pres.selectedElementId) pres.removeElement(pres.selectedElementId);
  }, [pres]);

  const handleEBotAction = useCallback(
    async (action: string, input?: string) => {
      if (!connected) return;
      setEbotResponse('');
      try {
        let response = '';
        switch (action) {
          case 'generate-slides': {
            const [topic, count] = (input || '').split('|||');
            response = await suggestContent(topic, parseInt(count) || 5);
            response = `✨ **Generated Slides**\n\n${response}`;
            break;
          }
          case 'talking-points': {
            const content = pres.currentSlide.elements
              .map((el) => el.content)
              .join('\n');
            if (!content.trim()) {
              response = '⚠️ Add content to the current slide first.';
            } else {
              response = await generateTalkingPoints(content);
              response = `🎤 **Talking Points**\n\n${response}`;
            }
            break;
          }
          case 'improve-slide': {
            const slideContent = pres.currentSlide.elements
              .map((el) => el.content)
              .join('\n');
            if (!slideContent.trim()) {
              response = '⚠️ Add content to the current slide first.';
            } else {
              response = `💡 **Improvement Suggestions**\n\nConsider:\n- Adding a visual element\n- Making bullet points more concise\n- Adding a relevant statistic`;
            }
            break;
          }
          default:
            response = `eBot processed "${action}".`;
        }
        setEbotResponse(response);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setEbotResponse(`❌ **eBot Error**\n\n${msg}`);
      }
    },
    [connected, suggestContent, generateTalkingPoints, pres.currentSlide],
  );

  return (
    <div className="eslides-app">
      <TopBar
        title={title}
        onTitleChange={setTitle}
        ebotSidebarOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={connected}
        onPresent={handlePresent}
      />
      <Toolbar
        onInsertText={() => pres.addElement('text', 'Click to edit')}
        onInsertShape={() => pres.addElement('shape', '')}
        onDeleteElement={handleDeleteElement}
        hasSelection={!!pres.selectedElementId}
        theme={theme}
        onThemeChange={setTheme}
      />
      <div className="eslides-body">
        <SlideList
          slides={pres.slides}
          currentIndex={pres.currentIndex}
          onSelect={pres.setCurrentIndex}
          onAdd={pres.addSlide}
          onDuplicate={pres.duplicateSlide}
          onRemove={pres.removeSlide}
        />
        <SlideCanvas
          slide={pres.currentSlide}
          selectedElementId={pres.selectedElementId}
          onSelectElement={pres.setSelectedElementId}
          onUpdateElement={pres.updateElement}
          onAddElement={pres.addElement}
        />
        <EBotSidebar
          open={ebotOpen}
          connected={connected}
          response={ebotResponse}
          isLoading={loading}
          onAction={handleEBotAction}
          onClose={() => setEbotOpen(false)}
        />
      </div>
      <StatusBar
        slideCount={pres.slides.length}
        currentSlide={pres.currentIndex + 1}
        connected={connected}
      />
    </div>
  );
}
