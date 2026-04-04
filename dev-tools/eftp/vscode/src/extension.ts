import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('eos-eftp.activate', () => {
        vscode.window.showInformationMessage('FTP/SFTP Transfer — EoS Dev Tool');
    });
    context.subscriptions.push(cmd);
}

export function deactivate() {}
