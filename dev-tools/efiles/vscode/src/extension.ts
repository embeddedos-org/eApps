import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-efiles.activate', () => {
        vscode.window.showInformationMessage('Advanced File Explorer — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
