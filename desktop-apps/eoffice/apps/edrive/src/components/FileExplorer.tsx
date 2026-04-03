import type { DriveFile } from '../hooks/useDrive';

const FILE_ICONS: Record<DriveFile['type'], string> = {
  folder: '📂', document: '📄', image: '🖼️', spreadsheet: '📊', archive: '📦', other: '📎',
};

interface FileExplorerProps {
  children: DriveFile[];
  currentPath: { id: string | null; name: string }[];
  selectedFileId: string | null;
  onSelect: (id: string) => void;
  onOpen: (file: DriveFile) => void;
  onNavigateBreadcrumb: (index: number) => void;
}

export default function FileExplorer({ children, currentPath, selectedFileId, onSelect, onOpen, onNavigateBreadcrumb }: FileExplorerProps) {
  return (
    <div className="edrive-main">
      <div className="breadcrumb">
        {currentPath.map((p, i) => (
          <span key={i}>
            {i > 0 && <span className="breadcrumb-sep">/</span>}
            <span
              className={`breadcrumb-item ${i === currentPath.length - 1 ? 'current' : ''}`}
              onClick={() => i < currentPath.length - 1 && onNavigateBreadcrumb(i)}
            >
              {p.name}
            </span>
          </span>
        ))}
      </div>
      <div className="file-grid">
        {children.length === 0 ? (
          <div className="file-empty">
            <div className="file-empty-icon">📂</div>
            <div>This folder is empty</div>
          </div>
        ) : (
          children.map((file) => (
            <div
              key={file.id}
              className={`file-card ${file.id === selectedFileId ? 'selected' : ''}`}
              onClick={() => onSelect(file.id)}
              onDoubleClick={() => file.type === 'folder' && onOpen(file)}
            >
              <div className="file-card-icon">{FILE_ICONS[file.type]}</div>
              <div className="file-card-name">{file.name}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
