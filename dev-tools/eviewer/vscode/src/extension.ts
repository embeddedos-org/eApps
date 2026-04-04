import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-eviewer.activate', () => {
        vscode.window.showInformationMessage('Binary/Hex Viewer — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
