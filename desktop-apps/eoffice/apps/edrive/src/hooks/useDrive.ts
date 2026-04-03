import { useState, useCallback } from 'react';

export interface DriveFile {
  id: string;
  name: string;
  type: 'folder' | 'document' | 'image' | 'spreadsheet' | 'archive' | 'other';
  size: number;
  modified: string;
  parentId: string | null;
}

let nextId = 1;
const uid = () => `f${nextId++}`;

const SEED: DriveFile[] = [
  { id: uid(), name: 'Documents', type: 'folder', size: 0, modified: '2025-03-15', parentId: null },
  { id: uid(), name: 'Photos', type: 'folder', size: 0, modified: '2025-03-10', parentId: null },
  { id: uid(), name: 'report-q1.pdf', type: 'document', size: 245000, modified: '2025-03-20', parentId: 'f1' },
  { id: uid(), name: 'budget.xlsx', type: 'spreadsheet', size: 128000, modified: '2025-03-18', parentId: 'f1' },
  { id: uid(), name: 'vacation.jpg', type: 'image', size: 3200000, modified: '2025-02-14', parentId: 'f2' },
  { id: uid(), name: 'notes.txt', type: 'document', size: 4200, modified: '2025-03-22', parentId: null },
  { id: uid(), name: 'backup.zip', type: 'archive', size: 52000000, modified: '2025-01-05', parentId: null },
];

function formatSize(bytes: number): string {
  if (bytes === 0) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

export function useDrive() {
  const [files, setFiles] = useState<DriveFile[]>(SEED);
  const [currentPath, setCurrentPath] = useState<{ id: string | null; name: string }[]>([{ id: null, name: 'My Drive' }]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  const currentFolderId = currentPath[currentPath.length - 1].id;
  const children = files.filter((f) => f.parentId === currentFolderId);
  const selectedFile = files.find((f) => f.id === selectedFileId) ?? null;
  const totalSize = files.reduce((s, f) => s + f.size, 0);

  const navigateTo = useCallback((folderId: string | null, folderName: string) => {
    setCurrentPath((prev) => [...prev, { id: folderId, name: folderName }]);
    setSelectedFileId(null);
  }, []);

  const navigateToBreadcrumb = useCallback((index: number) => {
    setCurrentPath((prev) => prev.slice(0, index + 1));
    setSelectedFileId(null);
  }, []);

  const addFile = useCallback((name: string, type: DriveFile['type'], size = 0) => {
    const id = uid();
    setFiles((prev) => [...prev, { id, name, type, size, modified: new Date().toISOString().slice(0, 10), parentId: currentFolderId }]);
  }, [currentFolderId]);

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
    setSelectedFileId((prev) => (prev === id ? null : prev));
  }, []);

  return {
    files, children, currentPath, currentFolderId, selectedFile, selectedFileId, totalSize,
    setSelectedFileId, navigateTo, navigateToBreadcrumb, addFile, removeFile, formatSize,
  };
}
