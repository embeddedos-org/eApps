import type { Version } from './types';
import { generateId } from './utils';

export class VersionHistory {
  public versions: Version[];

  constructor(versions: Version[] = []) {
    this.versions = versions;
  }

  saveVersion(resourceType: string, resourceId: string, snapshot: string, description: string, author?: string): Version {
    const version: Version = {
      id: generateId(), resourceType, resourceId, snapshot, description, author, created_at: new Date(),
    };
    this.versions.push(version);
    return version;
  }

  getVersions(resourceType: string, resourceId: string): Version[] {
    return this.versions.filter((v) => v.resourceType === resourceType && v.resourceId === resourceId);
  }

  getVersion(id: string): Version | undefined {
    return this.versions.find((v) => v.id === id);
  }

  restoreVersion(id: string): string | undefined {
    const version = this.versions.find((v) => v.id === id);
    return version?.snapshot;
  }

  toJSON(): object {
    return { versions: this.versions };
  }

  static fromJSON(json: { versions: Version[] }): VersionHistory {
    return new VersionHistory(
      json.versions.map((v) => ({ ...v, created_at: new Date(v.created_at) })),
    );
  }
}
