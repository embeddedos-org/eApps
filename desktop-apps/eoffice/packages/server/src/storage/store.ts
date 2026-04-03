import fs from 'fs';
import path from 'path';

export interface DataStore<T> {
  get(key: string): T | undefined;
  set(key: string, value: T): void;
  delete(key: string): boolean;
  list(): T[];
  has(key: string): boolean;
}

export class MemoryStore<T> implements DataStore<T> {
  private data = new Map<string, T>();

  get(key: string): T | undefined {
    return this.data.get(key);
  }
  set(key: string, value: T): void {
    this.data.set(key, value);
  }
  delete(key: string): boolean {
    return this.data.delete(key);
  }
  list(): T[] {
    return Array.from(this.data.values());
  }
  has(key: string): boolean {
    return this.data.has(key);
  }
}

export class FileStore<T> implements DataStore<T> {
  constructor(private directory: string) {
    if (!fs.existsSync(directory)) {
      fs.mkdirSync(directory, { recursive: true });
    }
  }

  private filePath(key: string): string {
    return path.join(this.directory, `${key}.json`);
  }

  get(key: string): T | undefined {
    const fp = this.filePath(key);
    if (!fs.existsSync(fp)) return undefined;
    return JSON.parse(fs.readFileSync(fp, 'utf-8'));
  }

  set(key: string, value: T): void {
    fs.writeFileSync(this.filePath(key), JSON.stringify(value, null, 2));
  }

  delete(key: string): boolean {
    const fp = this.filePath(key);
    if (!fs.existsSync(fp)) return false;
    fs.unlinkSync(fp);
    return true;
  }

  list(): T[] {
    if (!fs.existsSync(this.directory)) return [];
    return fs
      .readdirSync(this.directory)
      .filter((f) => f.endsWith('.json'))
      .map((f) => JSON.parse(fs.readFileSync(path.join(this.directory, f), 'utf-8')));
  }

  has(key: string): boolean {
    return fs.existsSync(this.filePath(key));
  }
}
