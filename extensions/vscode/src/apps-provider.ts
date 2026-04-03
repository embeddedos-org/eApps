import * as vscode from 'vscode';

interface AppItem {
  id: string;
  name: string;
  icon: string;
  description: string;
  ready: boolean;
}

const APPS: AppItem[] = [
  { id: 'edocs', name: 'eDocs', icon: '📝', description: 'Word processing', ready: true },
  { id: 'enotes', name: 'eNotes', icon: '📒', description: 'Digital notebooks', ready: true },
  { id: 'esheets', name: 'eSheets', icon: '📊', description: 'Spreadsheets', ready: false },
  { id: 'eslides', name: 'eSlides', icon: '📽️', description: 'Presentations', ready: false },
  { id: 'email', name: 'eMail', icon: '📧', description: 'Email & Calendar', ready: false },
  { id: 'edb', name: 'eDB', icon: '🗄️', description: 'Database', ready: false },
  { id: 'edrive', name: 'eDrive', icon: '☁️', description: 'Cloud storage', ready: false },
  { id: 'econnect', name: 'eConnect', icon: '👥', description: 'Collaboration', ready: false },
  { id: 'eforms', name: 'eForms', icon: '📋', description: 'Forms & surveys', ready: false },
  { id: 'esway', name: 'eSway', icon: '🎭', description: 'Presentations', ready: false },
  { id: 'eplanner', name: 'ePlanner', icon: '✅', description: 'Task management', ready: false },
];

export class EOfficeAppsProvider implements vscode.TreeDataProvider<AppItem> {
  getTreeItem(element: AppItem): vscode.TreeItem {
    const item = new vscode.TreeItem(`${element.icon} ${element.name}`);
    item.description = element.description;
    item.tooltip = `${element.name} — ${element.description}${element.ready ? '' : ' (Coming Soon)'}`;
    item.command = element.ready ? {
      command: `eoffice.open${element.name.charAt(1).toUpperCase() + element.name.slice(2)}`,
      title: `Open ${element.name}`,
      arguments: []
    } : undefined;
    item.contextValue = element.ready ? 'readyApp' : 'comingSoonApp';
    return item;
  }

  getChildren(): AppItem[] {
    return APPS;
  }
}
