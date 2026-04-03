import { useState } from 'react';
import type { TableDef } from '../hooks/useDatabase';

interface QueryEditorProps {
  tables: TableDef[];
}

export default function QueryEditor({ tables }: QueryEditorProps) {
  const [query, setQuery] = useState('SELECT * FROM users;');
  const [results, setResults] = useState('');
  const [isError, setIsError] = useState(false);

  const runQuery = () => {
    const q = query.trim().toUpperCase();
    setIsError(false);

    if (q.startsWith('SELECT')) {
      const match = query.match(/FROM\s+(\w+)/i);
      const tableName = match?.[1];
      const table = tables.find((t) => t.name === tableName);
      if (!table) {
        setIsError(true);
        setResults(`Error: Table "${tableName || '?'}" not found.`);
        return;
      }
      const header = table.columns.map((c) => c.name.padEnd(15)).join(' | ');
      const sep = table.columns.map(() => '—'.repeat(15)).join('-+-');
      const rows = table.rows.map((r) =>
        table.columns.map((c) => (r[c.name] || '').padEnd(15)).join(' | ')
      ).join('\n');
      setResults(`${header}\n${sep}\n${rows}\n\n${table.rows.length} row(s) returned.`);
    } else {
      setIsError(true);
      setResults('Only SELECT queries are supported in the demo query editor.');
    }
  };

  return (
    <div className="query-editor">
      <div className="query-editor-header">
        <span>📝 Query Editor</span>
        <button onClick={runQuery}>▶ Run</button>
      </div>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter SQL query..."
        spellCheck={false}
      />
      {results && (
        <div className={`query-results ${isError ? 'error' : ''}`}>{results}</div>
      )}
    </div>
  );
}
