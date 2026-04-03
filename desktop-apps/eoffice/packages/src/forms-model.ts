import type { Form, FormField, FormSubmission } from './types';
import { generateId } from './utils';

export class FormsModel {
  public forms: Form[];
  public submissions: Map<string, FormSubmission[]>;

  constructor(forms: Form[] = [], submissions: Map<string, FormSubmission[]> = new Map()) {
    this.forms = forms;
    this.submissions = submissions;
  }

  addForm(title: string, description: string): Form {
    const now = new Date();
    const form: Form = { id: generateId(), title, description, fields: [], created_at: now, updated_at: now };
    this.forms.push(form);
    this.submissions.set(form.id, []);
    return form;
  }

  removeForm(id: string): boolean {
    const index = this.forms.findIndex((f) => f.id === id);
    if (index === -1) return false;
    this.forms.splice(index, 1);
    this.submissions.delete(id);
    return true;
  }

  addField(formId: string, field: Omit<FormField, 'id'>): FormField | undefined {
    const form = this.forms.find((f) => f.id === formId);
    if (!form) return undefined;
    const newField: FormField = { id: generateId(), ...field };
    form.fields.push(newField);
    form.updated_at = new Date();
    return newField;
  }

  removeField(formId: string, fieldId: string): boolean {
    const form = this.forms.find((f) => f.id === formId);
    if (!form) return false;
    const index = form.fields.findIndex((f) => f.id === fieldId);
    if (index === -1) return false;
    form.fields.splice(index, 1);
    form.updated_at = new Date();
    return true;
  }

  updateField(formId: string, fieldId: string, updates: Partial<Omit<FormField, 'id'>>): boolean {
    const form = this.forms.find((f) => f.id === formId);
    if (!form) return false;
    const field = form.fields.find((f) => f.id === fieldId);
    if (!field) return false;
    Object.assign(field, updates);
    form.updated_at = new Date();
    return true;
  }

  submitForm(formId: string, data: Record<string, unknown>): FormSubmission | undefined {
    if (!this.forms.find((f) => f.id === formId)) return undefined;
    const submission: FormSubmission = { id: generateId(), formId, data, submitted_at: new Date() };
    const list = this.submissions.get(formId) ?? [];
    list.push(submission);
    this.submissions.set(formId, list);
    return submission;
  }

  getSubmissions(formId: string): FormSubmission[] {
    return this.submissions.get(formId) ?? [];
  }

  toJSON(): object {
    const subs: Record<string, FormSubmission[]> = {};
    this.submissions.forEach((v, k) => { subs[k] = v; });
    return { forms: this.forms, submissions: subs };
  }

  static fromJSON(json: { forms: Form[]; submissions: Record<string, FormSubmission[]> }): FormsModel {
    const map = new Map<string, FormSubmission[]>();
    for (const [k, v] of Object.entries(json.submissions)) {
      map.set(k, v.map((s) => ({ ...s, submitted_at: new Date(s.submitted_at) })));
    }
    return new FormsModel(
      json.forms.map((f) => ({ ...f, created_at: new Date(f.created_at), updated_at: new Date(f.updated_at) })),
      map,
    );
  }
}
