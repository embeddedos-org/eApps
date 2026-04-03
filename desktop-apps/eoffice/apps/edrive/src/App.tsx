import { useState } from 'react';
import TopBar from './components/TopBar';
import FileExplorer from './components/FileExplorer';
import FilePreview from './components/FilePreview';
import UploadZone from './components/UploadZone';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useDrive } from './hooks/useDrive';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [ebotOpen, setEbotOpen] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const drive = useDrive();
  const ebot = useEBot();

  const handleUpload = (name: string, size: number) => {
    const ext = name.split('.').pop()?.toLowerCase() ?? '';
    const typeMap: Record<string, 'document' | 'image' | 'spreadsheet' | 'archive' | 'other'> = {
      pdf: 'document', doc: 'document', txt: 'document', md: 'document',
      png: 'image', jpg: 'image', gif: 'image',
      xlsx: 'spreadsheet', csv: 'spreadsheet',
      zip: 'archive', tar: 'archive',
    };
    drive.addFile(name, typeMap[ext] || 'other', size);
    setShowUpload(false);
  };

  return (
    <div className="edrive-app">
      <TopBar
        onUpload={() => setShowUpload((p) => !p)}
        onNewFolder={() => drive.addFile('New Folder', 'folder')}
        ebotOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={ebot.connected}
      />
      <div className="edrive-body">
        <FileExplorer
          children={drive.children}
          currentPath={drive.currentPath}
          selectedFileId={drive.selectedFileId}
          onSelect={drive.setSelectedFileId}
          onOpen={(f) => drive.navigateTo(f.id, f.name)}
          onNavigateBreadcrumb={drive.navigateToBreadcrumb}
        />
        {drive.selectedFile && (
          <FilePreview file={drive.selectedFile} formatSize={drive.formatSize} />
        )}
        <EBotSidebar
          open={ebotOpen}
          connected={ebot.connected}
          loading={ebot.loading}
          onClose={() => setEbotOpen(false)}
          onSearchFiles={ebot.searchFiles}
          onSummarizeFile={ebot.summarizeFile}
        />
      </div>
      {showUpload && <UploadZone onUpload={handleUpload} />}
      <StatusBar
        fileCount={drive.files.length}
        totalSize={drive.formatSize(drive.totalSize)}
        connected={ebot.connected}
      />
    </div>
  );
}
