export type AppCategory = 'documents' | 'communication' | 'storage' | 'collaboration';

export interface EOfficeApp {
  id: string;
  name: string;
  icon: string;
  description: string;
  category: AppCategory;
  version: string;
  path: string;
}

export interface EBotRequest {
  endpoint: string;
  prompt: string;
  context?: Record<string, unknown>;
  app_id: string;
}

export interface EBotResponse {
  text: string;
  tool_call?: string;
  tokens?: number;
  error?: string;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  created_at: Date;
  updated_at: Date;
  app_id: string;
  tags: string[];
}

export type BlockType = 'paragraph' | 'heading' | 'list' | 'code' | 'image';

export interface TextStyle {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  fontSize?: number;
  color?: string;
}

export interface DocumentBlock {
  id: string;
  type: BlockType;
  content: string;
  style?: TextStyle;
}

export interface NoteEntry {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created_at: Date;
  updated_at: Date;
  pinned: boolean;
}

export interface SpreadsheetCell {
  row: number;
  col: number;
  value: string;
  formula?: string;
  type: 'text' | 'number' | 'formula';
}

export interface SlideData {
  id: string;
  title: string;
  content: string;
  layout: 'title' | 'content' | 'two-column' | 'blank';
  notes?: string;
}

export interface UserPrefs {
  theme: 'light' | 'dark';
  fontSize: number;
  autoSave: boolean;
  ebotEnabled: boolean;
  ebotHost: string;
  ebotPort: number;
}

export type CellFormatAlign = 'left' | 'center' | 'right';
export type CellNumberFormat = 'general' | 'number' | 'currency' | 'percent' | 'date';

export interface CellFormat {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  color?: string;
  backgroundColor?: string;
  align?: CellFormatAlign;
  numberFormat?: CellNumberFormat;
}

export interface Cell {
  value: string;
  formula?: string;
  computedValue?: string | number;
  format?: CellFormat;
}

export interface Sheet {
  id: string;
  name: string;
  cells: Record<string, Cell>;
  columnWidths?: Record<number, number>;
  rowHeights?: Record<number, number>;
}

export interface Spreadsheet {
  id: string;
  title: string;
  sheets: Sheet[];
  activeSheetId: string;
  created_at: Date;
  updated_at: Date;
}

// Phase 2 types
export type SlideElementType = 'text' | 'image' | 'shape' | 'chart';
export type SlideTransition = 'none' | 'fade' | 'slide' | 'zoom';

export interface SlideElement {
  id: string;
  type: SlideElementType;
  content: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation?: number;
  style?: Record<string, string>;
}

export interface Slide {
  id: string;
  elements: SlideElement[];
  background?: string;
  notes?: string;
  transition?: SlideTransition;
}

export interface Presentation {
  id: string;
  title: string;
  slides: Slide[];
  theme: string;
  created_at: Date;
  updated_at: Date;
}

export interface PresentationTheme {
  id: string;
  name: string;
  colors: { primary: string; secondary: string; background: string; text: string };
  fonts: { heading: string; body: string };
}

// Phase 2 Auth types
export interface User {
  id: string;
  username: string;
  email: string;
  passwordHash: string;
  role: 'admin' | 'editor' | 'viewer';
  created_at: Date;
}

export interface AuthToken {
  token: string;
  refreshToken: string;
  expiresAt: Date;
}

// Phase 3 types
export type TaskStatus = 'todo' | 'in-progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface PlannerTask {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: string;
  dueDate?: Date;
  tags: string[];
  linkedDocs: string[];
  created_at: Date;
  updated_at: Date;
}

export interface Board {
  id: string;
  name: string;
  columns: string[];
  tasks: PlannerTask[];
  created_at: Date;
  updated_at: Date;
}

export type FormFieldType = 'text' | 'number' | 'select' | 'checkbox' | 'radio' | 'date' | 'textarea';

export interface FormField {
  id: string;
  type: FormFieldType;
  label: string;
  required: boolean;
  options?: string[];
  placeholder?: string;
}

export interface Form {
  id: string;
  title: string;
  description: string;
  fields: FormField[];
  created_at: Date;
  updated_at: Date;
}

export interface FormSubmission {
  id: string;
  formId: string;
  data: Record<string, unknown>;
  submitted_at: Date;
}

export interface Version {
  id: string;
  resourceType: string;
  resourceId: string;
  snapshot: string;
  description: string;
  author?: string;
  created_at: Date;
}

// Phase 4 types
export interface EmailMessage {
  id: string;
  from: string;
  to: string[];
  subject: string;
  body: string;
  read: boolean;
  starred: boolean;
  folder: string;
  created_at: Date;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  description?: string;
  location?: string;
  attendees: string[];
}

export interface DBTable {
  id: string;
  name: string;
  columns: Array<{ name: string; type: string }>;
  rows: Array<Record<string, unknown>>;
  created_at: Date;
}

export interface DriveFile {
  id: string;
  name: string;
  type: string;
  size: number;
  parentId?: string;
  path: string;
  content?: string;
  created_at: Date;
  updated_at: Date;
}

export interface Channel {
  id: string;
  name: string;
  description: string;
  members: string[];
  created_at: Date;
}

export interface ChannelMessage {
  id: string;
  channelId: string;
  author: string;
  content: string;
  created_at: Date;
}

export interface InteractiveSlide {
  id: string;
  type: 'quiz' | 'poll' | 'qa';
  question: string;
  options?: string[];
  responses: Array<{ participantId: string; answer: string; timestamp: Date }>;
}

export interface SwayPresentation {
  id: string;
  title: string;
  slides: InteractiveSlide[];
  created_at: Date;
  updated_at: Date;
}
