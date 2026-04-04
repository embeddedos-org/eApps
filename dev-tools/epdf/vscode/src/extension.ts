import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-epdf.activate', () => {
        vscode.window.showInformationMessage('PDF/Doc Viewer — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
