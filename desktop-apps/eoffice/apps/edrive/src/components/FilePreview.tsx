import type { DriveFile } from '../hooks/useDrive';

const FILE_ICONS: Record<DriveFile['type'], string> = {
  folder: '📂', document: '📄', image: '🖼️', spreadsheet: '📊', archive: '📦', other: '📎',
};

interface FilePreviewProps {
  file: DriveFile | null;
  formatSize: (bytes: number) => string;
}

export default function FilePreview({ file, formatSize }: FilePreviewProps) {
  if (!file) return null;

  return (
    <div className="file-preview">
      <div className="file-preview-icon">{FILE_ICONS[file.type]}</div>
      <div className="file-preview-name">{file.name}</div>
      <div className="file-preview-meta">
        <div className="file-preview-row">
          <span className="file-preview-label">Type</span>
          <span className="file-preview-value">{file.type}</span>
        </div>
        <div className="file-preview-row">
          <span className="file-preview-label">Size</span>
          <span className="file-preview-value">{formatSize(file.size)}</span>
        </div>
        <div className="file-preview-row">
          <span className="file-preview-label">Modified</span>
          <span className="file-preview-value">{file.modified}</span>
        </div>
      </div>
    </div>
  );
}
