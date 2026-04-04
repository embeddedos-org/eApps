import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-erunner.activate', () => {
        vscode.window.showInformationMessage('Task/Script Runner — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
