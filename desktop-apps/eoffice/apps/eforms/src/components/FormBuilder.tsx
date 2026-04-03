import type { FormField, FieldType } from '../hooks/useFormBuilder';

interface FormBuilderProps {
  fields: FormField[];
  selectedFieldId: string | null;
  onSelectField: (id: string) => void;
  onAddField: (type?: FieldType) => void;
  onRemoveField: (id: string) => void;
}

export default function FormBuilder({
  fields,
  selectedFieldId,
  onSelectField,
  onAddField,
  onRemoveField,
}: FormBuilderProps) {
  return (
    <div className="form-content">
      <div className="form-container">
        {fields.map((field) => (
          <div
            key={field.id}
            className={`form-field-card ${field.id === selectedFieldId ? 'selected' : ''}`}
            onClick={() => onSelectField(field.id)}
          >
            <span className="form-field-drag">⠿</span>
            <div className="form-field-info">
              <div className="form-field-type">{field.type}</div>
              <div className="form-field-label">{field.label}</div>
            </div>
            {field.required && <span className="form-field-required">Required</span>}
            <button
              className="form-field-remove"
              onClick={(e) => { e.stopPropagation(); onRemoveField(field.id); }}
            >
              ✕
            </button>
          </div>
        ))}
        <button className="form-add-btn" onClick={() => onAddField()}>
          ＋ Add Field
        </button>
      </div>
    </div>
  );
}
