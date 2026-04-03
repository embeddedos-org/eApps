import * as vscode from 'vscode';

export class RecentFilesProvider implements vscode.TreeDataProvider<string> {
  private context: vscode.ExtensionContext;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
  }

  getTreeItem(element: string): vscode.TreeItem {
    const item = new vscode.TreeItem(element);
    item.command = {
      command: 'vscode.open',
      title: 'Open File',
      arguments: [vscode.Uri.file(element)]
    };
    return item;
  }

  getChildren(): string[] {
    return this.context.globalState.get<string[]>('recentFiles', []);
  }
}
