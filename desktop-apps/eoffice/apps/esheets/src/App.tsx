import { useState, useCallback, useRef, type ChangeEvent } from 'react';
import TopBar from './components/TopBar';
import Toolbar from './components/Toolbar';
import FormulaBar from './components/FormulaBar';
import SpreadsheetGrid from './components/SpreadsheetGrid';
import SheetTabs from './components/SheetTabs';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useSpreadsheet } from './hooks/useSpreadsheet';
import { useEBot } from './hooks/useEBot';
import type { CellFormat } from '@eoffice/core';

export default function App() {
  const [title, setTitle] = useState('Untitled Spreadsheet');
  const [ebotSidebarOpen, setEbotSidebarOpen] = useState(false);
  const [ebotResponse, setEbotResponse] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const spreadsheet = useSpreadsheet();
  const { connected: ebotConnected, loading: ebotLoading, suggestFormula, explainFormula, analyzeData } = useEBot();

  const handleFormatChange = useCallback(
    (format: Partial<CellFormat>) => {
      if (!spreadsheet.activeCell) return;
      const currentFormat = spreadsheet.activeCellFormat;
      spreadsheet.setCellFormat(
        spreadsheet.activeCell.row,
        spreadsheet.activeCell.col,
        { ...currentFormat, ...format },
      );
    },
    [spreadsheet],
  );

  const handleFormulaSubmit = useCallback(() => {
    if (!spreadsheet.activeCell) return;
    spreadsheet.setCell(
      spreadsheet.activeCell.row,
      spreadsheet.activeCell.col,
      spreadsheet.editValue,
    );
  }, [spreadsheet]);

  const handleExportCSV = useCallback(() => {
    const csv = spreadsheet.exportCSV();
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'spreadsheet'}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [spreadsheet, title]);

  const handleImportCSV = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const csv = ev.target?.result as string;
        if (csv) {
          spreadsheet.importCSV(csv);
          setTitle(file.name.replace(/\.csv$/i, ''));
        }
      };
      reader.readAsText(file);
      e.target.value = '';
    },
    [spreadsheet],
  );

  const handleNewSheet = useCallback(() => {
    spreadsheet.newSpreadsheet();
    setTitle('Untitled Spreadsheet');
  }, [spreadsheet]);

  const handleAddSheet = useCallback(() => {
    const name = `Sheet ${spreadsheet.sheets.length + 1}`;
    spreadsheet.addSheet(name);
  }, [spreadsheet]);

  const handleEBotAction = useCallback(
    async (action: string, input?: string) => {
      if (!ebotConnected) return;
      setEbotResponse('');

      try {
        let response = '';

        switch (action) {
          case 'suggest-formula':
            if (input) {
              response = await suggestFormula(input);
              response = `💡 **Formula Suggestion**\n\n${response}`;
            }
            break;

          case 'explain-formula':
            if (input) {
              response = await explainFormula(input);
              response = `📖 **Formula Explanation**\n\n${response}`;
            }
            break;

          case 'analyze-data': {
            const csv = spreadsheet.exportCSV();
            if (!csv.trim()) {
              response = '⚠️ No data to analyze. Add some data to the spreadsheet first.';
            } else {
              response = await analyzeData(csv);
              response = `📊 **Data Analysis**\n\n${response}`;
            }
            break;
          }

          case 'summarize': {
            const csvData = spreadsheet.exportCSV();
            if (!csvData.trim()) {
              response = '⚠️ No data to summarize.';
            } else {
              response = await analyzeData(
                `Provide a brief summary of this spreadsheet data:\n\n${csvData}`,
              );
              response = `📋 **Data Summary**\n\n${response}`;
            }
            break;
          }

          default:
            response = `eBot processed "${action}".`;
        }

        setEbotResponse(response);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setEbotResponse(`❌ **eBot Error**\n\n${msg}`);
      }
    },
    [ebotConnected, suggestFormula, explainFormula, analyzeData, spreadsheet],
  );

  return (
    <div className="esheets-app">
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.tsv"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <TopBar
        title={title}
        onTitleChange={setTitle}
        ebotSidebarOpen={ebotSidebarOpen}
        onToggleEBot={() => setEbotSidebarOpen((prev) => !prev)}
        connected={ebotConnected}
        onNewSheet={handleNewSheet}
        onExportCSV={handleExportCSV}
        onImportCSV={handleImportCSV}
      />
      <Toolbar
        cellFormat={spreadsheet.activeCellFormat}
        onFormatChange={handleFormatChange}
      />
      <FormulaBar
        cellAddress={spreadsheet.cellAddress}
        formulaValue={spreadsheet.editValue}
        onFormulaChange={spreadsheet.setEditValue}
        onFormulaSubmit={handleFormulaSubmit}
      />
      <div className="esheets-body">
        <SpreadsheetGrid
          activeCell={spreadsheet.activeCell}
          editingCell={spreadsheet.editingCell}
          editValue={spreadsheet.editValue}
          revision={spreadsheet.revision}
          getCell={spreadsheet.getCell}
          getCellAddress={spreadsheet.getCellAddress}
          onSelectCell={spreadsheet.selectCell}
          onStartEditing={spreadsheet.startEditing}
          onEditValueChange={spreadsheet.setEditValue}
          onCommitEdit={spreadsheet.commitEdit}
          onCancelEdit={spreadsheet.cancelEdit}
        />
        <EBotSidebar
          open={ebotSidebarOpen}
          connected={ebotConnected}
          response={ebotResponse}
          isLoading={ebotLoading}
          onAction={handleEBotAction}
          onClose={() => setEbotSidebarOpen(false)}
        />
      </div>
      <SheetTabs
        sheets={spreadsheet.sheets}
        activeSheetId={spreadsheet.activeSheetId}
        onSwitchSheet={spreadsheet.switchSheet}
        onAddSheet={handleAddSheet}
        onRemoveSheet={spreadsheet.removeSheet}
        onRenameSheet={spreadsheet.renameSheet}
      />
      <StatusBar
        cellCount={spreadsheet.model.getCellCount()}
        sheetCount={spreadsheet.model.getSheetCount()}
        connected={ebotConnected}
        selectionStats={spreadsheet.selectionStats}
      />
    </div>
  );
}
