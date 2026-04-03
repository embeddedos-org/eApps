import {
  App,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  requestUrl,
  TFile,
  addIcon,
} from 'obsidian';

interface EOfficeSettings {
  backendUrl: string;
  syncInterval: number;
  autoSync: boolean;
}

const DEFAULT_SETTINGS: EOfficeSettings = {
  backendUrl: 'http://localhost:3001',
  syncInterval: 5,
  autoSync: false,
};

const SYNC_ICON = `<svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="8"><path d="M30 50a20 20 0 0 1 40 0"/><path d="M70 50a20 20 0 0 1-40 0"/><polyline points="28,38 28,52 42,52"/><polyline points="72,62 72,48 58,48"/></svg>`;

export default class EOfficePlugin extends Plugin {
  settings: EOfficeSettings = DEFAULT_SETTINGS;
  syncIntervalId: number | null = null;
  statusBarItem: HTMLElement | null = null;
  isSyncing = false;

  async onload() {
    await this.loadSettings();

    addIcon('eoffice-sync', SYNC_ICON);

    // Ribbon icon for sync
    this.addRibbonIcon('eoffice-sync', 'Sync with eNotes', async () => {
      await this.syncVaultToENotes();
    });

    // Status bar
    this.statusBarItem = this.addStatusBarItem();
    this.updateStatusBar('idle');

    // Commands
    this.addCommand({
      id: 'ebot-summarize-note',
      name: 'eBot: Summarize current note',
      editorCallback: async (editor) => {
        const content = editor.getValue();
        if (!content.trim()) {
          new Notice('Note is empty.');
          return;
        }

        new Notice('eBot is summarizing...');
        const summary = await this.ebotRequest(
          `Summarize the following note concisely:\n\n${content}`
        );

        if (summary) {
          const cursor = editor.getCursor();
          editor.replaceRange(
            `\n\n---\n## eBot Summary\n${summary}\n`,
            { line: editor.lastLine() + 1, ch: 0 }
          );
          editor.setCursor(cursor);
          new Notice('Summary appended to note.');
        }
      },
    });

    this.addCommand({
      id: 'ebot-generate-outline',
      name: 'eBot: Generate outline from note',
      editorCallback: async (editor) => {
        const content = editor.getValue();
        if (!content.trim()) {
          new Notice('Note is empty.');
          return;
        }

        new Notice('eBot is generating outline...');
        const outline = await this.ebotRequest(
          `Generate a structured outline with headings and bullet points from the following text:\n\n${content}`
        );

        if (outline) {
          const cursor = editor.getCursor();
          editor.replaceRange(
            `\n\n---\n## eBot Outline\n${outline}\n`,
            { line: editor.lastLine() + 1, ch: 0 }
          );
          editor.setCursor(cursor);
          new Notice('Outline appended to note.');
        }
      },
    });

    this.addCommand({
      id: 'sync-vault-to-enotes',
      name: 'Sync vault to eNotes',
      callback: async () => {
        await this.syncVaultToENotes();
      },
    });

    this.addCommand({
      id: 'import-from-enotes',
      name: 'Import from eNotes',
      callback: async () => {
        await this.importFromENotes();
      },
    });

    // Settings tab
    this.addSettingTab(new EOfficeSettingTab(this.app, this));

    // Auto-sync
    if (this.settings.autoSync) {
      this.startAutoSync();
    }
  }

  onunload() {
    this.stopAutoSync();
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  updateStatusBar(status: 'idle' | 'syncing' | 'success' | 'error') {
    if (!this.statusBarItem) return;
    const labels: Record<string, string> = {
      idle: '📎 eOffice: Ready',
      syncing: '🔄 eOffice: Syncing...',
      success: '✅ eOffice: Synced',
      error: '❌ eOffice: Error',
    };
    this.statusBarItem.setText(labels[status]);
  }

  startAutoSync() {
    this.stopAutoSync();
    const intervalMs = this.settings.syncInterval * 60 * 1000;
    this.syncIntervalId = window.setInterval(async () => {
      await this.syncVaultToENotes();
    }, intervalMs);
  }

  stopAutoSync() {
    if (this.syncIntervalId !== null) {
      window.clearInterval(this.syncIntervalId);
      this.syncIntervalId = null;
    }
  }

  async ebotRequest(message: string): Promise<string | null> {
    try {
      const resp = await requestUrl({
        url: `${this.settings.backendUrl}/api/ebot/chat`,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = resp.json;
      return data.text || data.response || null;
    } catch {
      new Notice('eBot is offline. Start the eOffice server.');
      return null;
    }
  }

  async syncVaultToENotes() {
    if (this.isSyncing) return;
    this.isSyncing = true;
    this.updateStatusBar('syncing');

    try {
      const files = this.app.vault.getMarkdownFiles();
      let synced = 0;

      for (const file of files) {
        const content = await this.app.vault.read(file);
        const stat = await this.app.vault.adapter.stat(file.path);
        const modifiedMs = stat?.mtime || 0;

        try {
          await requestUrl({
            url: `${this.settings.backendUrl}/api/enotes/sync`,
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              path: file.path,
              title: file.basename,
              content,
              modifiedAt: modifiedMs,
              source: 'obsidian',
            }),
          });
          synced++;
        } catch {
          // Server may be offline; continue with other files
        }
      }

      this.updateStatusBar('success');
      new Notice(`Synced ${synced}/${files.length} notes to eNotes.`);

      setTimeout(() => this.updateStatusBar('idle'), 3000);
    } catch {
      this.updateStatusBar('error');
      new Notice('Sync failed. Is the eOffice server running?');
    } finally {
      this.isSyncing = false;
    }
  }

  async importFromENotes() {
    this.updateStatusBar('syncing');

    try {
      const resp = await requestUrl({
        url: `${this.settings.backendUrl}/api/enotes`,
        method: 'GET',
      });
      const notes: Array<{ id: string; title: string; content: string }> = resp.json;

      if (!Array.isArray(notes) || notes.length === 0) {
        new Notice('No notes found in eNotes.');
        this.updateStatusBar('idle');
        return;
      }

      let imported = 0;
      const folder = 'eNotes Import';
      if (!(await this.app.vault.adapter.exists(folder))) {
        await this.app.vault.createFolder(folder);
      }

      for (const note of notes) {
        const safeName = note.title.replace(/[\\/:*?"<>|]/g, '_');
        const filePath = `${folder}/${safeName}.md`;

        const existing = this.app.vault.getAbstractFileByPath(filePath);
        if (existing && existing instanceof TFile) {
          await this.app.vault.modify(existing, note.content);
        } else {
          await this.app.vault.create(filePath, note.content);
        }
        imported++;
      }

      this.updateStatusBar('success');
      new Notice(`Imported ${imported} notes from eNotes.`);
      setTimeout(() => this.updateStatusBar('idle'), 3000);
    } catch {
      this.updateStatusBar('error');
      new Notice('Import failed. Is the eOffice server running?');
    }
  }
}

class EOfficeSettingTab extends PluginSettingTab {
  plugin: EOfficePlugin;

  constructor(app: App, plugin: EOfficePlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    containerEl.createEl('h2', { text: 'eOffice Sync Settings' });

    new Setting(containerEl)
      .setName('Backend URL')
      .setDesc('The eOffice server URL (default: http://localhost:3001)')
      .addText((text) =>
        text
          .setPlaceholder('http://localhost:3001')
          .setValue(this.plugin.settings.backendUrl)
          .onChange(async (value) => {
            this.plugin.settings.backendUrl = value || DEFAULT_SETTINGS.backendUrl;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName('Sync interval (minutes)')
      .setDesc('How often to auto-sync when enabled (minimum 1 minute)')
      .addSlider((slider) =>
        slider
          .setLimits(1, 60, 1)
          .setValue(this.plugin.settings.syncInterval)
          .setDynamicTooltip()
          .onChange(async (value) => {
            this.plugin.settings.syncInterval = value;
            await this.plugin.saveSettings();
            if (this.plugin.settings.autoSync) {
              this.plugin.startAutoSync();
            }
          })
      );

    new Setting(containerEl)
      .setName('Auto-sync')
      .setDesc('Automatically sync vault to eNotes at the configured interval')
      .addToggle((toggle) =>
        toggle.setValue(this.plugin.settings.autoSync).onChange(async (value) => {
          this.plugin.settings.autoSync = value;
          await this.plugin.saveSettings();
          if (value) {
            this.plugin.startAutoSync();
            new Notice('Auto-sync enabled.');
          } else {
            this.plugin.stopAutoSync();
            new Notice('Auto-sync disabled.');
          }
        })
      );

    containerEl.createEl('h3', { text: 'Manual Actions' });

    new Setting(containerEl)
      .setName('Sync now')
      .setDesc('Push all vault notes to eNotes')
      .addButton((btn) =>
        btn
          .setButtonText('Sync to eNotes')
          .setCta()
          .onClick(async () => {
            await this.plugin.syncVaultToENotes();
          })
      );

    new Setting(containerEl)
      .setName('Import notes')
      .setDesc('Pull all notes from eNotes into your vault')
      .addButton((btn) =>
        btn.setButtonText('Import from eNotes').onClick(async () => {
          await this.plugin.importFromENotes();
        })
      );
  }
}
