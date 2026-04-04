import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-essh.activate', () => {
        vscode.window.showInformationMessage('SSH Manager — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
