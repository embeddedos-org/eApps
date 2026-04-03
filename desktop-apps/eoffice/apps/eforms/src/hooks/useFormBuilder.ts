import { useState, useCallback } from 'react';

export type FieldType = 'text' | 'email' | 'number' | 'textarea' | 'select' | 'radio' | 'checkbox' | 'date';

export interface FormField {
  id: string;
  type: FieldType;
  label: string;
  placeholder: string;
  required: boolean;
  options: string[];
}

let nextId = 1;
const uid = () => `field-${nextId++}`;

const SAMPLE_FIELDS: FormField[] = [
  { id: uid(), type: 'text', label: 'Full Name', placeholder: 'Enter your name', required: true, options: [] },
  { id: uid(), type: 'email', label: 'Email Address', placeholder: 'you@example.com', required: true, options: [] },
  { id: uid(), type: 'select', label: 'Department', placeholder: 'Select department', required: false, options: ['Engineering', 'Design', 'Marketing', 'Sales'] },
];

export function useFormBuilder() {
  const [fields, setFields] = useState<FormField[]>(SAMPLE_FIELDS);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState(false);

  const selectedField = fields.find((f) => f.id === selectedFieldId) || null;

  const addField = useCallback((type: FieldType = 'text') => {
    const field: FormField = {
      id: uid(),
      type,
      label: `New ${type} field`,
      placeholder: '',
      required: false,
      options: type === 'select' || type === 'radio' ? ['Option 1', 'Option 2'] : [],
    };
    setFields((prev) => [...prev, field]);
    setSelectedFieldId(field.id);
    return field;
  }, []);

  const updateField = useCallback((id: string, updates: Partial<FormField>) => {
    setFields((prev) => prev.map((f) => (f.id === id ? { ...f, ...updates } : f)));
  }, []);

  const removeField = useCallback((id: string) => {
    setFields((prev) => prev.filter((f) => f.id !== id));
    setSelectedFieldId((prev) => (prev === id ? null : prev));
  }, []);

  const reorderFields = useCallback((fromIndex: number, toIndex: number) => {
    setFields((prev) => {
      const newFields = [...prev];
      const [moved] = newFields.splice(fromIndex, 1);
      newFields.splice(toIndex, 0, moved);
      return newFields;
    });
  }, []);

  return {
    fields,
    selectedField,
    selectedFieldId,
    setSelectedFieldId,
    previewMode,
    setPreviewMode,
    addField,
    updateField,
    removeField,
    reorderFields,
  };
}
