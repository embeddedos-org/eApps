import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-eserial.activate', () => {
        vscode.window.showInformationMessage('Serial Monitor — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
