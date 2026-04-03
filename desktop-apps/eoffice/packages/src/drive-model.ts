import type { DriveFile } from './types';
import { generateId } from './utils';

export class DriveModel {
  public files: DriveFile[];

  constructor(files: DriveFile[] = []) {
    this.files = files;
  }

  addFile(name: string, type: string, content?: string, parentId?: string): DriveFile {
    const now = new Date();
    const path = parentId ? `${this.getFile(parentId)?.path ?? ''}/${name}` : `/${name}`;
    const file: DriveFile = {
      id: generateId(), name, type, size: content?.length ?? 0,
      parentId, path, content, created_at: now, updated_at: now,
    };
    this.files.push(file);
    return file;
  }

  removeFile(id: string): boolean {
    const index = this.files.findIndex((f) => f.id === id);
    if (index === -1) return false;
    this.files.splice(index, 1);
    return true;
  }

  moveFile(id: string, newParentId: string): boolean {
    const file = this.files.find((f) => f.id === id);
    if (!file) return false;
    const parent = this.files.find((f) => f.id === newParentId);
    file.parentId = newParentId;
    file.path = parent ? `${parent.path}/${file.name}` : `/${file.name}`;
    file.updated_at = new Date();
    return true;
  }

  renameFile(id: string, newName: string): boolean {
    const file = this.files.find((f) => f.id === id);
    if (!file) return false;
    const dir = file.path.substring(0, file.path.lastIndexOf('/'));
    file.name = newName;
    file.path = `${dir}/${newName}`;
    file.updated_at = new Date();
    return true;
  }

  getChildren(parentId?: string): DriveFile[] {
    return this.files.filter((f) => f.parentId === parentId);
  }

  getFile(id: string): DriveFile | undefined {
    return this.files.find((f) => f.id === id);
  }

  search(query: string): DriveFile[] {
    const lower = query.toLowerCase();
    return this.files.filter((f) => f.name.toLowerCase().includes(lower));
  }

  getTotalSize(): number {
    return this.files.reduce((sum, f) => sum + f.size, 0);
  }

  toJSON(): object {
    return { files: this.files };
  }

  static fromJSON(json: { files: DriveFile[] }): DriveModel {
    return new DriveModel(
      json.files.map((f) => ({ ...f, created_at: new Date(f.created_at), updated_at: new Date(f.updated_at) })),
    );
  }
}
