import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-etimer.activate', () => {
        vscode.window.showInformationMessage('Focus Timer — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
