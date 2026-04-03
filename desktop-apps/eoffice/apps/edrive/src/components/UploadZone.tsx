import { useState } from 'react';

interface UploadZoneProps {
  onUpload: (name: string, size: number) => void;
}

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const [dragover, setDragover] = useState(false);

  const simulateUpload = () => {
    const names = ['document.pdf', 'photo.png', 'data.csv', 'notes.md', 'archive.zip'];
    const name = names[Math.floor(Math.random() * names.length)];
    const size = Math.floor(Math.random() * 5000000) + 10000;
    onUpload(name, size);
  };

  return (
    <div
      className={`upload-zone ${dragover ? 'dragover' : ''}`}
      onClick={simulateUpload}
      onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
      onDragLeave={() => setDragover(false)}
      onDrop={(e) => { e.preventDefault(); setDragover(false); simulateUpload(); }}
    >
      <div className="upload-zone-icon">📤</div>
      <div>Click or drag files here to upload (simulated)</div>
    </div>
  );
}
