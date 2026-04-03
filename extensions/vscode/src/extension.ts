import * as vscode from 'vscode';
import { EOfficeAppsProvider } from './apps-provider';
import { RecentFilesProvider } from './recent-provider';
import { CsvEditorProvider } from './csv-editor';

export function activate(context: vscode.ExtensionContext) {
  // eslint-disable-next-line no-console
  console.log('eOffice Suite extension activated');

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('eoffice.openDocs', () => openApp(context, 'edocs', 'eDocs')),
    vscode.commands.registerCommand('eoffice.openNotes', () => openApp(context, 'enotes', 'eNotes')),
    vscode.commands.registerCommand('eoffice.openSheets', () => openApp(context, 'esheets', 'eSheets')),
    vscode.commands.registerCommand('eoffice.openLauncher', () => openApp(context, 'launcher', 'eOffice Suite')),
    vscode.commands.registerCommand('eoffice.ebotChat', () => openEBotPanel(context)),
    vscode.commands.registerCommand('eoffice.summarizeSelection', () => ebotAction(context, 'summarize')),
    vscode.commands.registerCommand('eoffice.rewriteSelection', () => ebotAction(context, 'rewrite')),
  );

  // Register sidebar tree views
  const appsProvider = new EOfficeAppsProvider();
  vscode.window.registerTreeDataProvider('eoffice-apps', appsProvider);

  const recentProvider = new RecentFilesProvider(context);
  vscode.window.registerTreeDataProvider('eoffice-recent', recentProvider);

  // Register CSV custom editor
  context.subscriptions.push(
    CsvEditorProvider.register(context)
  );
}

export function deactivate() {}

function openApp(context: vscode.ExtensionContext, appId: string, title: string) {
  const panel = vscode.window.createWebviewPanel(
    `eoffice-${appId}`,
    title,
    vscode.ViewColumn.One,
    {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'webview')]
    }
  );

  const htmlPath = vscode.Uri.joinPath(context.extensionUri, 'webview', `${appId}.html`);
  vscode.workspace.fs.readFile(htmlPath).then(content => {
    const html = Buffer.from(content).toString('utf8');
    panel.webview.html = html;
  });
}

function openEBotPanel(_context: vscode.ExtensionContext) {
  const panel = vscode.window.createWebviewPanel(
    'eoffice-ebot',
    '🤖 eBot AI',
    vscode.ViewColumn.Beside,
    { enableScripts: true, retainContextWhenHidden: true }
  );

  panel.webview.html = getEBotChatHtml();

  panel.webview.onDidReceiveMessage(async (message) => {
    if (message.type === 'chat') {
      try {
        const config = vscode.workspace.getConfiguration('eoffice');
        const host = config.get<string>('ebotHost', 'localhost');
        const port = config.get<number>('ebotPort', 3001);
        const resp = await fetch(`http://${host}:${port}/api/ebot/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: message.text })
        });
        const data = await resp.json() as Record<string, string>;
        panel.webview.postMessage({ type: 'response', text: data.text || data.response || JSON.stringify(data) });
      } catch {
        panel.webview.postMessage({ type: 'response', text: 'eBot is offline. Start the server.' });
      }
    }
    if (message.type === 'insertToEditor') {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        editor.edit(editBuilder => {
          editBuilder.replace(editor.selection, message.text);
        });
      }
    }
  });
}

async function ebotAction(_context: vscode.ExtensionContext, action: string) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) { return; }

  const selection = editor.document.getText(editor.selection);
  if (!selection) {
    vscode.window.showWarningMessage('No text selected');
    return;
  }

  const config = vscode.workspace.getConfiguration('eoffice');
  const host = config.get<string>('ebotHost', 'localhost');
  const port = config.get<number>('ebotPort', 3001);

  const prompt = action === 'summarize'
    ? `Summarize the following text concisely:\n\n${selection}`
    : `Rewrite the following text to be clearer and more professional:\n\n${selection}`;

  try {
    const resp = await fetch(`http://${host}:${port}/api/ebot/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: prompt })
    });
    const data = await resp.json() as Record<string, string>;
    const result = data.text || data.response || '';

    const choice = await vscode.window.showInformationMessage(
      `eBot ${action}: ${result.substring(0, 100)}...`,
      'Replace Selection', 'Copy to Clipboard', 'Cancel'
    );

    if (choice === 'Replace Selection') {
      editor.edit(editBuilder => editBuilder.replace(editor.selection, result));
    } else if (choice === 'Copy to Clipboard') {
      await vscode.env.clipboard.writeText(result);
    }
  } catch {
    vscode.window.showErrorMessage('eBot is offline. Start the eOffice server (npm run dev:server)');
  }
}

function getEBotChatHtml(): string {
  return `<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: var(--vscode-font-family); background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); margin: 0; padding: 16px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
  h2 { margin: 0 0 12px; font-size: 16px; }
  .chat { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding: 8px 0; }
  .msg { padding: 8px 12px; border-radius: 8px; max-width: 85%; word-wrap: break-word; font-size: 13px; line-height: 1.5; }
  .msg.user { background: var(--vscode-button-background); color: var(--vscode-button-foreground); align-self: flex-end; }
  .msg.bot { background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); align-self: flex-start; }
  .input-row { display: flex; gap: 8px; margin-top: 8px; }
  input { flex: 1; padding: 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); border-radius: 4px; font-size: 13px; }
  button { padding: 8px 16px; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
  button:hover { background: var(--vscode-button-hoverBackground); }
  .actions { display: flex; gap: 4px; margin-top: 4px; }
  .actions button { padding: 4px 8px; font-size: 11px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }
</style>
</head>
<body>
<h2>🤖 eBot AI Assistant</h2>
<div class="chat" id="chat">
  <div class="msg bot">Hello! I'm eBot. Ask me anything or paste text to summarize, rewrite, or analyze.</div>
</div>
<div class="input-row">
  <input id="input" placeholder="Type a message..." />
  <button onclick="send()">Send</button>
</div>
<script>
  const vscode = acquireVsCodeApi();
  const chat = document.getElementById('chat');
  const input = document.getElementById('input');

  function send() {
    const text = input.value.trim();
    if (!text) return;
    addMsg(text, 'user');
    input.value = '';
    vscode.postMessage({ type: 'chat', text });
  }

  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

  function addMsg(text, type) {
    const div = document.createElement('div');
    div.className = 'msg ' + type;
    div.textContent = text;
    if (type === 'bot') {
      const actions = document.createElement('div');
      actions.className = 'actions';
      const insertBtn = document.createElement('button');
      insertBtn.textContent = '📋 Insert to Editor';
      insertBtn.onclick = () => vscode.postMessage({ type: 'insertToEditor', text });
      actions.appendChild(insertBtn);
      div.appendChild(actions);
    }
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  window.addEventListener('message', (e) => {
    if (e.data.type === 'response') addMsg(e.data.text, 'bot');
  });
</script>
</body>
</html>`;
}
