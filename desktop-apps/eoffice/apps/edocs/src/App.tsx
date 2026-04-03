import { useState, useCallback, useRef } from 'react';
import TopBar from './components/TopBar';
import Toolbar from './components/Toolbar';
import Editor from './components/Editor';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useEBot } from './hooks/useEBot';

interface FormatState {
  bold: boolean;
  italic: boolean;
  underline: boolean;
  heading: boolean;
  list: boolean;
}

export default function App() {
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('Untitled Document');
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const [ebotSidebarOpen, setEbotSidebarOpen] = useState(false);
  const [ebotResponse, setEbotResponse] = useState('');
  const [autoSaveStatus, setAutoSaveStatus] = useState<'saved' | 'saving' | 'unsaved'>('saved');
  const [cursorPosition, setCursorPosition] = useState({ line: 1, col: 1 });
  const [formatState, setFormatState] = useState<FormatState>({
    bold: false,
    italic: false,
    underline: false,
    heading: false,
    list: false,
  });

  const autoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const editorRef = useRef<HTMLDivElement>(null);

  const { connected: ebotConnected, loading: isLoading, summarize, rewrite, grammarCheck, translate } = useEBot();

  const computeStats = useCallback((text: string) => {
    const trimmed = text.trim();
    const words = trimmed === '' ? 0 : trimmed.split(/\s+/).length;
    setWordCount(words);
    setCharCount(text.length);
  }, []);

  const handleContentChange = useCallback(
    (newContent: string) => {
      setContent(newContent);
      computeStats(newContent);
      setAutoSaveStatus('unsaved');

      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      autoSaveTimer.current = setTimeout(() => {
        setAutoSaveStatus('saving');
        setTimeout(() => setAutoSaveStatus('saved'), 600);
      }, 1500);
    },
    [computeStats]
  );

  const handleFormat = useCallback((command: string) => {
    document.execCommand(command, false);
    editorRef.current?.focus();

    setFormatState((prev) => {
      const key = command === 'insertUnorderedList' ? 'list' : command;
      if (key in prev) {
        return { ...prev, [key]: !prev[key as keyof FormatState] };
      }
      return prev;
    });
  }, []);

  const handleUndo = useCallback(() => {
    document.execCommand('undo', false);
    editorRef.current?.focus();
  }, []);

  const handleRedo = useCallback(() => {
    document.execCommand('redo', false);
    editorRef.current?.focus();
  }, []);

  const handleHeading = useCallback(() => {
    const selection = window.getSelection();
    if (selection && selection.rangeCount > 0) {
      document.execCommand('formatBlock', false, formatState.heading ? 'p' : 'h2');
      setFormatState((prev) => ({ ...prev, heading: !prev.heading }));
    }
    editorRef.current?.focus();
  }, [formatState.heading]);

  const handleEBotAction = useCallback(
    async (action: string) => {
      if (!ebotConnected) return;

      setEbotResponse('');

      const plainText = editorRef.current?.innerText || content;

      if (!plainText.trim()) {
        setEbotResponse('⚠️ Document is empty. Add some content first.');
        return;
      }

      try {
        let response = '';

        switch (action) {
          case 'summarize':
            response = await summarize(plainText);
            response = `📋 **Summary**\n\n${response}`;
            break;

          case 'rewrite-formal':
            response = await rewrite(plainText, 'formal');
            response = `✍️ **Formal Rewrite**\n\n${response}`;
            break;

          case 'rewrite-casual':
            response = await rewrite(plainText, 'casual');
            response = `✍️ **Casual Rewrite**\n\n${response}`;
            break;

          case 'rewrite-concise':
            response = await rewrite(plainText, 'concise');
            response = `✍️ **Concise Rewrite**\n\n${response}`;
            break;

          case 'grammar':
            response = await grammarCheck(plainText);
            response = `✅ **Grammar Check**\n\n${response}`;
            break;

          case 'translate':
            response = await translate(plainText, 'Spanish');
            response = `🌐 **Translation (Spanish)**\n\n${response}`;
            break;

          default:
            response = `eBot processed your "${action}" request.`;
        }

        setEbotResponse(response);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setEbotResponse(`❌ **eBot Error**\n\n${msg}\n\nPlease check that the eBot server is running at http://localhost:3001.`);
      }
    },
    [ebotConnected, content, summarize, rewrite, grammarCheck, translate]
  );

  const handleCursorChange = useCallback((line: number, col: number) => {
    setCursorPosition({ line, col });
  }, []);

  return (
    <div className="edocs-app">
      <TopBar
        title={title}
        onTitleChange={setTitle}
        ebotSidebarOpen={ebotSidebarOpen}
        onToggleEBot={() => setEbotSidebarOpen((prev) => !prev)}
        connected={ebotConnected}
      />
      <Toolbar
        formatState={formatState}
        onFormat={handleFormat}
        onHeading={handleHeading}
        onUndo={handleUndo}
        onRedo={handleRedo}
      />
      <div className="edocs-body">
        <Editor
          ref={editorRef}
          content={content}
          onChange={handleContentChange}
          onCursorChange={handleCursorChange}
        />
        <EBotSidebar
          open={ebotSidebarOpen}
          connected={ebotConnected}
          response={ebotResponse}
          isLoading={isLoading}
          onAction={handleEBotAction}
          onClose={() => setEbotSidebarOpen(false)}
        />
      </div>
      <StatusBar
        wordCount={wordCount}
        charCount={charCount}
        connected={ebotConnected}
        cursorPosition={cursorPosition}
        autoSaveStatus={autoSaveStatus}
      />
    </div>
  );
}
