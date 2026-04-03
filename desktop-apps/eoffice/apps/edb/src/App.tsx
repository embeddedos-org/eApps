import { useState } from 'react';
import TopBar from './components/TopBar';
import TableList from './components/TableList';
import TableView from './components/TableView';
import QueryEditor from './components/QueryEditor';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useDatabase } from './hooks/useDatabase';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [ebotOpen, setEbotOpen] = useState(false);
  const db = useDatabase();
  const ebot = useEBot();

  const handleNewTable = () => {
    const name = prompt('Table name:');
    if (name?.trim()) db.createTable(name.trim());
  };

  return (
    <div className="edb-app">
      <TopBar
        onNewTable={handleNewTable}
        ebotOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={ebot.connected}
      />
      <div className="edb-body">
        <TableList
          tables={db.tables}
          selectedTableId={db.selectedTableId}
          onSelect={db.setSelectedTableId}
          onCreate={handleNewTable}
          onDrop={db.dropTable}
        />
        <div className="edb-main">
          <TableView
            table={db.selectedTable}
            onInsertRow={db.insertRow}
            onUpdateRow={db.updateRow}
            onDeleteRow={db.deleteRow}
          />
          <QueryEditor tables={db.tables} />
        </div>
        <EBotSidebar
          open={ebotOpen}
          connected={ebot.connected}
          loading={ebot.loading}
          onClose={() => setEbotOpen(false)}
          onGenerateQuery={ebot.generateQuery}
          onExplainQuery={ebot.explainQuery}
        />
      </div>
      <StatusBar
        tableCount={db.tables.length}
        rowCount={db.totalRows}
        connected={ebot.connected}
      />
    </div>
  );
}
