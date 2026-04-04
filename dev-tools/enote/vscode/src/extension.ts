import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-enote.activate', () => {
        vscode.window.showInformationMessage('Code Notes & Snippets — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
