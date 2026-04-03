import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EBotOffice } from '../ebot-office';
import { EBotClient } from '../ebot-client';
import type { EBotResponse } from '../ebot-client';

function createMockClient() {
  return {
    chat: vi.fn(),
    complete: vi.fn(),
    summarize: vi.fn(),
    taskExtract: vi.fn(),
    search: vi.fn(),
    getModels: vi.fn(),
    getTools: vi.fn(),
    getStatus: vi.fn(),
    resetSession: vi.fn(),
    isConnected: vi.fn(),
    getStats: vi.fn(),
  } as unknown as EBotClient;
}

function successResponse(text: string): EBotResponse {
  return { success: true, text, tokens_used: 10 };
}

function errorResponse(message: string): EBotResponse {
  return { success: false, text: '', error: message };
}

describe('EBotOffice', () => {
  let mockClient: ReturnType<typeof createMockClient>;
  let office: EBotOffice;

  beforeEach(() => {
    mockClient = createMockClient();
    office = new EBotOffice(mockClient);
  });

  describe('summarizeText', () => {
    it('calls client.summarize with the text', async () => {
      (mockClient.summarize as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('This is a summary.'),
      );

      const result = await office.summarizeText('Long text to summarize');
      expect(mockClient.summarize).toHaveBeenCalledWith('Long text to summarize');
      expect(result).toBe('This is a summary.');
    });

    it('throws on error response', async () => {
      (mockClient.summarize as ReturnType<typeof vi.fn>).mockResolvedValue(
        errorResponse('Service unavailable'),
      );

      await expect(office.summarizeText('text')).rejects.toThrow('Service unavailable');
    });
  });

  describe('rewriteText', () => {
    it('includes tone in the prompt', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('Rewritten text in casual tone'),
      );

      const result = await office.rewriteText('Some text', 'casual');
      expect(result).toBe('Rewritten text in casual tone');

      const callArgs = (mockClient.complete as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(callArgs).toContain('casual');
    });

    it('defaults to formal tone', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('Formal text'),
      );

      await office.rewriteText('Some text');

      const callArgs = (mockClient.complete as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(callArgs).toContain('formal');
    });
  });

  describe('grammarCheck', () => {
    it('returns suggestions from parsed JSON response', async () => {
      const jsonResponse = JSON.stringify({
        suggestions: ['Use comma before "and"', 'Capitalize "monday"'],
        corrected: 'Fixed text here.',
      });
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse(jsonResponse),
      );

      const result = await office.grammarCheck('text with errors');
      expect(result.suggestions).toHaveLength(2);
      expect(result.corrected).toBe('Fixed text here.');
    });

    it('returns fallback on malformed JSON', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('not valid json at all'),
      );

      const result = await office.grammarCheck('some text');
      expect(result.suggestions).toEqual([]);
      expect(result.corrected).toBe('some text');
    });
  });

  describe('autoTagNote', () => {
    it('returns array of tags from parsed JSON', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('["meeting", "project", "planning"]'),
      );

      const result = await office.autoTagNote('Notes from project planning meeting');
      expect(result).toEqual(['meeting', 'project', 'planning']);
    });

    it('returns empty array on failure', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        errorResponse('Service down'),
      );

      await expect(office.autoTagNote('content')).rejects.toThrow();
    });

    it('returns empty array on malformed response', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('not json'),
      );

      const result = await office.autoTagNote('content');
      expect(result).toEqual([]);
    });
  });

  describe('extractTasks', () => {
    it('returns task array from parsed JSON', async () => {
      const tasks = [
        { task: 'Complete report', priority: 'high', due: '2025-01-20' },
        { task: 'Review code', priority: 'medium' },
      ];
      (mockClient.taskExtract as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse(JSON.stringify(tasks)),
      );

      const result = await office.extractTasks('Please complete the report by Jan 20 and review the code');
      expect(result).toHaveLength(2);
      expect(result[0].task).toBe('Complete report');
      expect(result[0].priority).toBe('high');
      expect(result[1].task).toBe('Review code');
    });

    it('returns empty array on malformed response', async () => {
      (mockClient.taskExtract as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('no tasks found'),
      );

      const result = await office.extractTasks('Nothing here');
      expect(result).toEqual([]);
    });
  });

  describe('semanticSearch', () => {
    it('calls client.search with the query', async () => {
      const results = [
        { title: 'Doc 1', snippet: 'Matching content', app: 'edocs', score: 0.95 },
      ];
      (mockClient.search as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse(JSON.stringify(results)),
      );

      const result = await office.semanticSearch('project roadmap');
      expect(mockClient.search).toHaveBeenCalledWith('project roadmap');
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('Doc 1');
      expect(result[0].score).toBe(0.95);
    });

    it('returns empty array on malformed response', async () => {
      (mockClient.search as ReturnType<typeof vi.fn>).mockResolvedValue(
        successResponse('no results'),
      );

      const result = await office.semanticSearch('query');
      expect(result).toEqual([]);
    });
  });

  describe('error handling', () => {
    it('summarizeText throws on error response', async () => {
      (mockClient.summarize as ReturnType<typeof vi.fn>).mockResolvedValue(
        errorResponse('timeout'),
      );

      await expect(office.summarizeText('text')).rejects.toThrow('timeout');
    });

    it('rewriteText throws on error response', async () => {
      (mockClient.complete as ReturnType<typeof vi.fn>).mockResolvedValue(
        errorResponse('model unavailable'),
      );

      await expect(office.rewriteText('text', 'formal')).rejects.toThrow('model unavailable');
    });

    it('extractTasks throws on error response', async () => {
      (mockClient.taskExtract as ReturnType<typeof vi.fn>).mockResolvedValue(
        errorResponse('rate limited'),
      );

      await expect(office.extractTasks('text')).rejects.toThrow('rate limited');
    });

    it('semanticSearch throws on error response', async () => {
      (mockClient.search as ReturnType<typeof vi.fn>).mockResolvedValue(
        errorResponse('index offline'),
      );

      await expect(office.semanticSearch('query')).rejects.toThrow('index offline');
    });
  });
});
