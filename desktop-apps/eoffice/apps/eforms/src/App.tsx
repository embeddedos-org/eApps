import { useState, useCallback } from 'react';
import TopBar from './components/TopBar';
import FormBuilder from './components/FormBuilder';
import FieldEditor from './components/FieldEditor';
import FormPreview from './components/FormPreview';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useFormBuilder } from './hooks/useFormBuilder';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [title, setTitle] = useState('Untitled Form');
  const [ebotOpen, setEbotOpen] = useState(false);
  const [ebotResponse, setEbotResponse] = useState('');

  const form = useFormBuilder();
  const { connected, loading, suggestFields, improveQuestion } = useEBot();

  const handleEBotAction = useCallback(
    async (action: string, input?: string) => {
      if (!connected) return;
      setEbotResponse('');
      try {
        let response = '';
        switch (action) {
          case 'suggest-fields': {
            if (input) {
              response = await suggestFields(input);
              response = `✨ **Suggested Fields**\n\n${response}`;
            }
            break;
          }
          case 'improve-questions': {
            const labels = form.fields.map((f) => f.label).join('\n');
            if (!labels.trim()) {
              response = '⚠️ Add some fields first.';
            } else {
              response = await improveQuestion(labels);
              response = `💡 **Improved Questions**\n\n${response}`;
            }
            break;
          }
          case 'validate': {
            const issues: string[] = [];
            if (form.fields.length === 0) issues.push('• Form has no fields');
            if (!form.fields.some((f) => f.required)) issues.push('• No required fields set');
            if (!form.fields.some((f) => f.type === 'email')) issues.push('• Consider adding an email field');
            response = issues.length > 0
              ? `⚠️ **Validation Issues**\n\n${issues.join('\n')}`
              : '✅ **Form looks good!** No issues found.';
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
    [connected, suggestFields, improveQuestion, form.fields],
  );

  return (
    <div className="eforms-app">
      <TopBar
        title={title}
        onTitleChange={setTitle}
        previewMode={form.previewMode}
        onTogglePreview={() => form.setPreviewMode((p) => !p)}
        ebotSidebarOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={connected}
      />
      <div className="eforms-body">
        {form.previewMode ? (
          <FormPreview title={title} fields={form.fields} />
        ) : (
          <>
            <FormBuilder
              fields={form.fields}
              selectedFieldId={form.selectedFieldId}
              onSelectField={form.setSelectedFieldId}
              onAddField={form.addField}
              onRemoveField={form.removeField}
            />
            {form.selectedField && (
              <FieldEditor field={form.selectedField} onUpdate={form.updateField} />
            )}
          </>
        )}
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
        fieldCount={form.fields.length}
        connected={connected}
        previewMode={form.previewMode}
      />
    </div>
  );
}
