import * as vscode from 'vscode';

export class CsvEditorProvider implements vscode.CustomTextEditorProvider {
  static register(context: vscode.ExtensionContext): vscode.Disposable {
    return vscode.window.registerCustomEditorProvider(
      'eoffice.csvEditor',
      new CsvEditorProvider(context),
      { supportsMultipleEditorsPerDocument: false }
    );
  }

  constructor(private readonly context: vscode.ExtensionContext) {}

  async resolveCustomTextEditor(
    document: vscode.TextDocument,
    webviewPanel: vscode.WebviewPanel,
    _token: vscode.CancellationToken
  ): Promise<void> {
    webviewPanel.webview.options = { enableScripts: true };

    const updateWebview = () => {
      webviewPanel.webview.html = this.getHtmlForCsv(document.getText());
    };

    const changeDocumentSubscription = vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.uri.toString() === document.uri.toString()) {
        updateWebview();
      }
    });

    webviewPanel.onDidDispose(() => {
      changeDocumentSubscription.dispose();
    });

    webviewPanel.webview.onDidReceiveMessage(message => {
      if (message.type === 'edit') {
        const edit = new vscode.WorkspaceEdit();
        edit.replace(
          document.uri,
          new vscode.Range(0, 0, document.lineCount, 0),
          message.csv
        );
        vscode.workspace.applyEdit(edit);
      }
    });

    updateWebview();
  }

  private getHtmlForCsv(csvText: string): string {
    const rows = csvText.split('\n').filter(r => r.trim()).map(r => r.split(',').map(c => c.trim()));
    const headers = rows[0] || [];
    const data = rows.slice(1);

    const headerHtml = headers.map((h, i) => `<th contenteditable="true" data-col="${i}">${this.escapeHtml(h)}</th>`).join('');
    const bodyHtml = data.map((row, ri) =>
      `<tr>${row.map((cell, ci) => `<td contenteditable="true" data-row="${ri}" data-col="${ci}">${this.escapeHtml(cell)}</td>`).join('')}</tr>`
    ).join('');

    return `<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: var(--vscode-font-family); background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); margin: 0; padding: 16px; }
  .toolbar { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; }
  .toolbar button { padding: 4px 12px; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
  .toolbar button:hover { background: var(--vscode-button-hoverBackground); }
  .toolbar span { font-size: 12px; color: var(--vscode-descriptionForeground); }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { background: var(--vscode-editor-selectionBackground); font-weight: 600; text-align: left; }
  th, td { padding: 6px 10px; border: 1px solid var(--vscode-input-border); min-width: 80px; }
  td:focus, th:focus { outline: 2px solid var(--vscode-focusBorder); background: var(--vscode-editor-selectionBackground); }
  tr:nth-child(even) { background: var(--vscode-list-hoverBackground); }
  .info { font-size: 12px; color: var(--vscode-descriptionForeground); margin-top: 8px; }
</style>
</head>
<body>
<div class="toolbar">
  <strong>📊 eSheets CSV Editor</strong>
  <button onclick="addRow()">+ Row</button>
  <button onclick="addCol()">+ Column</button>
  <button onclick="save()">💾 Save</button>
  <span>${data.length} rows × ${headers.length} cols</span>
</div>
<table id="table">
  <thead><tr>${headerHtml}</tr></thead>
  <tbody>${bodyHtml}</tbody>
</table>
<div class="info">Edit cells directly. Click Save to write changes back to the file.</div>
<script>
  const vscode = acquireVsCodeApi();

  function save() {
    const table = document.getElementById('table');
    const rows = Array.from(table.rows);
    const csv = rows.map(row => Array.from(row.cells).map(c => c.textContent).join(',')).join('\\n');
    vscode.postMessage({ type: 'edit', csv });
  }

  function addRow() {
    const tbody = document.querySelector('tbody');
    const colCount = document.querySelector('thead tr').cells.length;
    const tr = document.createElement('tr');
    for (let i = 0; i < colCount; i++) {
      const td = document.createElement('td');
      td.contentEditable = 'true';
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }

  function addCol() {
    const table = document.getElementById('table');
    Array.from(table.rows).forEach((row, i) => {
      const cell = i === 0 ? document.createElement('th') : document.createElement('td');
      cell.contentEditable = 'true';
      cell.textContent = i === 0 ? 'New' : '';
      row.appendChild(cell);
    });
  }

  document.getElementById('table').addEventListener('input', () => {
    clearTimeout(window._saveTimer);
    window._saveTimer = setTimeout(save, 1000);
  });
</script>
</body>
</html>`;
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}
