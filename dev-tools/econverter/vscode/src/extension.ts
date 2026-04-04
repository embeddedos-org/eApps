import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-econverter.activate', () => {
        vscode.window.showInformationMessage('Data Format Converter — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
