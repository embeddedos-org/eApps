import type { EOfficeApp, PresentationTheme } from './types';

export const EBOT_DEFAULT_HOST = '192.168.1.100';

export const EBOT_DEFAULT_PORT = 8420;

export const EBOT_ENDPOINTS = {
  chat: '/api/ebot/chat',
  complete: '/api/ebot/complete',
  summarize: '/api/ebot/summarize',
  taskExtract: '/api/ebot/task-extract',
  search: '/api/ebot/search',
} as const;

export const APP_REGISTRY: EOfficeApp[] = [
  {
    id: 'edocs',
    name: 'eDocs',
    icon: '📝',
    description: 'Word processing',
    category: 'documents',
    version: '0.1.0',
    path: '/apps/edocs',
  },
  {
    id: 'enotes',
    name: 'eNotes',
    icon: '📒',
    description: 'Digital notebooks',
    category: 'documents',
    version: '0.1.0',
    path: '/apps/enotes',
  },
  {
    id: 'esheets',
    name: 'eSheets',
    icon: '📊',
    description: 'Spreadsheets',
    category: 'documents',
    version: '0.1.0',
    path: '/apps/esheets',
  },
  {
    id: 'eslides',
    name: 'eSlides',
    icon: '📽️',
    description: 'Presentations',
    category: 'documents',
    version: '0.1.0',
    path: '/apps/eslides',
  },
  {
    id: 'email',
    name: 'eMail',
    icon: '📧',
    description: 'Email & Calendar',
    category: 'communication',
    version: '0.1.0',
    path: '/apps/email',
  },
  {
    id: 'edb',
    name: 'eDB',
    icon: '🗄️',
    description: 'Database',
    category: 'storage',
    version: '0.1.0',
    path: '/apps/edb',
  },
  {
    id: 'edrive',
    name: 'eDrive',
    icon: '☁️',
    description: 'Cloud storage',
    category: 'storage',
    version: '0.1.0',
    path: '/apps/edrive',
  },
  {
    id: 'econnect',
    name: 'eConnect',
    icon: '👥',
    description: 'Collaboration & chat',
    category: 'collaboration',
    version: '0.1.0',
    path: '/apps/econnect',
  },
  {
    id: 'eforms',
    name: 'eForms',
    icon: '📋',
    description: 'Forms & surveys',
    category: 'collaboration',
    version: '0.1.0',
    path: '/apps/eforms',
  },
  {
    id: 'esway',
    name: 'eSway',
    icon: '🎭',
    description: 'Interactive presentations',
    category: 'documents',
    version: '0.1.0',
    path: '/apps/esway',
  },
  {
    id: 'eplanner',
    name: 'ePlanner',
    icon: '✅',
    description: 'Task management',
    category: 'collaboration',
    version: '0.1.0',
    path: '/apps/eplanner',
  },
];

export const VERSION = '0.1.0';

export const PRESENTATION_THEMES: PresentationTheme[] = [
  { id: 'default', name: 'Default', colors: { primary: '#1a73e8', secondary: '#34a853', background: '#ffffff', text: '#202124' }, fonts: { heading: 'Segoe UI', body: 'Segoe UI' } },
  { id: 'dark', name: 'Dark', colors: { primary: '#8ab4f8', secondary: '#81c995', background: '#1e1e1e', text: '#e0e0e0' }, fonts: { heading: 'Segoe UI', body: 'Segoe UI' } },
  { id: 'nature', name: 'Nature', colors: { primary: '#2e7d32', secondary: '#558b2f', background: '#f1f8e9', text: '#1b5e20' }, fonts: { heading: 'Georgia', body: 'Arial' } },
  { id: 'corporate', name: 'Corporate', colors: { primary: '#1565c0', secondary: '#0277bd', background: '#f5f5f5', text: '#212121' }, fonts: { heading: 'Calibri', body: 'Calibri' } },
  { id: 'creative', name: 'Creative', colors: { primary: '#e91e63', secondary: '#9c27b0', background: '#fce4ec', text: '#880e4f' }, fonts: { heading: 'Poppins', body: 'Roboto' } },
];
