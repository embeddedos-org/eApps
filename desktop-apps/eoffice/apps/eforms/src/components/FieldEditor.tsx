import type { FormField, FieldType } from '../hooks/useFormBuilder';

interface FieldEditorProps {
  field: FormField;
  onUpdate: (id: string, updates: Partial<FormField>) => void;
}

const FIELD_TYPES: FieldType[] = ['text', 'email', 'number', 'textarea', 'select', 'radio', 'checkbox', 'date'];

export default function FieldEditor({ field, onUpdate }: FieldEditorProps) {
  const hasOptions = field.type === 'select' || field.type === 'radio';

  return (
    <div className="field-editor">
      <div className="field-editor-title">Field Properties</div>

      <label>
        Type
        <select
          value={field.type}
          onChange={(e) => onUpdate(field.id, { type: e.target.value as FieldType })}
        >
          {FIELD_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </label>

      <label>
        Label
        <input
          value={field.label}
          onChange={(e) => onUpdate(field.id, { label: e.target.value })}
        />
      </label>

      <label>
        Placeholder
        <input
          value={field.placeholder}
          onChange={(e) => onUpdate(field.id, { placeholder: e.target.value })}
        />
      </label>

      <label className="field-editor-check">
        <input
          type="checkbox"
          checked={field.required}
          onChange={(e) => onUpdate(field.id, { required: e.target.checked })}
        />
        Required
      </label>

      {hasOptions && (
        <label>
          Options (one per line)
          <textarea
            value={field.options.join('\n')}
            onChange={(e) =>
              onUpdate(field.id, {
                options: e.target.value.split('\n').filter(Boolean),
              })
            }
          />
        </label>
      )}
    </div>
  );
}
