import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-etools.activate', () => {
        vscode.window.showInformationMessage('Dev Utility Toolkit — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
