import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-ebot.activate', () => {
        vscode.window.showInformationMessage('AI Coding Assistant — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
