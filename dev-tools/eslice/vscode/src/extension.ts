import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-eslice.activate', () => {
        vscode.window.showInformationMessage('Image Asset Slicer — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
