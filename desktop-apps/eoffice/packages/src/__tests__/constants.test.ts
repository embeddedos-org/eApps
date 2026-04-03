import { describe, it, expect } from 'vitest';
import {
  EBOT_DEFAULT_HOST,
  EBOT_DEFAULT_PORT,
  EBOT_ENDPOINTS,
  APP_REGISTRY,
  VERSION,
} from '../constants';

describe('constants', () => {
  describe('EBOT_DEFAULT_HOST', () => {
    it('is 192.168.1.100', () => {
      expect(EBOT_DEFAULT_HOST).toBe('192.168.1.100');
    });
  });

  describe('EBOT_DEFAULT_PORT', () => {
    it('is 8420', () => {
      expect(EBOT_DEFAULT_PORT).toBe(8420);
    });
  });

  describe('EBOT_ENDPOINTS', () => {
    it('has exactly 5 endpoints', () => {
      expect(Object.keys(EBOT_ENDPOINTS)).toHaveLength(5);
    });

    it('has a chat endpoint', () => {
      expect(EBOT_ENDPOINTS.chat).toBe('/api/ebot/chat');
    });

    it('has a complete endpoint', () => {
      expect(EBOT_ENDPOINTS.complete).toBe('/api/ebot/complete');
    });

    it('has a summarize endpoint', () => {
      expect(EBOT_ENDPOINTS.summarize).toBe('/api/ebot/summarize');
    });

    it('has a taskExtract endpoint', () => {
      expect(EBOT_ENDPOINTS.taskExtract).toBe('/api/ebot/task-extract');
    });

    it('has a search endpoint', () => {
      expect(EBOT_ENDPOINTS.search).toBe('/api/ebot/search');
    });
  });

  describe('APP_REGISTRY', () => {
    it('has exactly 11 apps', () => {
      expect(APP_REGISTRY).toHaveLength(11);
    });

    it('each app has all required fields', () => {
      const requiredFields = [
        'id',
        'name',
        'icon',
        'description',
        'category',
        'version',
        'path',
      ];

      for (const app of APP_REGISTRY) {
        for (const field of requiredFields) {
          expect(app).toHaveProperty(field);
          expect((app as unknown as Record<string, unknown>)[field]).toBeDefined();
        }
      }
    });

    it('all app ids are unique', () => {
      const ids = APP_REGISTRY.map((a) => a.id);
      expect(new Set(ids).size).toBe(ids.length);
    });

    it('all app paths start with /apps/', () => {
      for (const app of APP_REGISTRY) {
        expect(app.path).toMatch(/^\/apps\//);
      }
    });

    it('categories are valid', () => {
      const validCategories = [
        'documents',
        'communication',
        'storage',
        'collaboration',
      ];
      for (const app of APP_REGISTRY) {
        expect(validCategories).toContain(app.category);
      }
    });

    it('contains expected apps', () => {
      const ids = APP_REGISTRY.map((a) => a.id);
      expect(ids).toContain('edocs');
      expect(ids).toContain('enotes');
      expect(ids).toContain('esheets');
      expect(ids).toContain('eslides');
      expect(ids).toContain('email');
      expect(ids).toContain('edb');
      expect(ids).toContain('edrive');
      expect(ids).toContain('econnect');
      expect(ids).toContain('eforms');
      expect(ids).toContain('esway');
      expect(ids).toContain('eplanner');
    });
  });

  describe('VERSION', () => {
    it('is defined', () => {
      expect(VERSION).toBeDefined();
    });

    it('is a string', () => {
      expect(typeof VERSION).toBe('string');
    });

    it('follows semver format', () => {
      expect(VERSION).toMatch(/^\d+\.\d+\.\d+$/);
    });
  });
});
