import type { FormEvent } from 'react';
import type { FormField } from '../hooks/useFormBuilder';

interface FormPreviewProps {
  title: string;
  fields: FormField[];
}

export default function FormPreview({ title, fields }: FormPreviewProps) {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    alert('Form submitted! (preview mode)');
  };

  return (
    <div className="form-preview-container">
      <form className="form-preview" onSubmit={handleSubmit}>
        <div className="form-preview-title">{title || 'Untitled Form'}</div>
        <div className="form-preview-desc">Fill out the form below.</div>

        {fields.map((field) => (
          <div key={field.id} className="form-preview-field">
            <div className="form-preview-label">
              <span>{field.label}</span>
              {field.required && <span className="required">*</span>}
            </div>

            {field.type === 'textarea' ? (
              <textarea
                className="form-preview-input form-preview-textarea"
                placeholder={field.placeholder}
                required={field.required}
              />
            ) : field.type === 'select' ? (
              <select className="form-preview-input" required={field.required}>
                <option value="">{field.placeholder || 'Select...'}</option>
                {field.options.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : field.type === 'radio' ? (
              <div className="form-preview-radio">
                {field.options.map((opt) => (
                  <label key={opt} className="form-preview-option">
                    <input type="radio" name={field.id} value={opt} required={field.required} />
                    {opt}
                  </label>
                ))}
              </div>
            ) : field.type === 'checkbox' ? (
              <label className="form-preview-option">
                <input type="checkbox" required={field.required} />
                {field.placeholder || field.label}
              </label>
            ) : (
              <input
                className="form-preview-input"
                type={field.type}
                placeholder={field.placeholder}
                required={field.required}
              />
            )}
          </div>
        ))}

        <button type="submit" className="form-preview-submit">Submit</button>
      </form>
    </div>
  );
}
