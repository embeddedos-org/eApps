import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  EBotClient,
  EBOT_DEFAULT_HOST,
  EBOT_DEFAULT_PORT,
  EBOT_API_VERSION,
} from '../ebot-client';

const mockFetch = vi.fn();

describe('EBotClient', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch);
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function mockOkResponse(body: unknown) {
    return mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(body),
      text: () => Promise.resolve(JSON.stringify(body)),
    });
  }

  function mockErrorResponse(status: number, statusText: string) {
    return mockFetch.mockResolvedValueOnce({
      ok: false,
      status,
      statusText,
      text: () => Promise.resolve(statusText),
    });
  }

  function mockNetworkError() {
    return mockFetch.mockRejectedValueOnce(new Error('Network error'));
  }

  describe('constructor', () => {
    it('uses default host and port', () => {
      const client = new EBotClient();
      expect(EBOT_DEFAULT_HOST).toBe('192.168.1.100');
      expect(EBOT_DEFAULT_PORT).toBe(8420);

      const expectedBase = `http://${EBOT_DEFAULT_HOST}:${EBOT_DEFAULT_PORT}/${EBOT_API_VERSION}`;

      mockOkResponse({ success: true, text: 'response' });
      client.chat('test');
      expect(mockFetch).toHaveBeenCalledWith(
        `${expectedBase}/chat`,
        expect.any(Object),
      );
    });

    it('accepts custom host and port', () => {
      const client = new EBotClient('10.0.0.1', 9999);

      mockOkResponse({ success: true, text: 'response' });
      client.chat('test');
      expect(mockFetch).toHaveBeenCalledWith(
        `http://10.0.0.1:9999/${EBOT_API_VERSION}/chat`,
        expect.any(Object),
      );
    });
  });

  describe('chat', () => {
    it('sends POST to /chat with correct body', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'Hello!', tokens_used: 10 });

      await client.chat('Hello', { user: 'test' });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/chat'),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'Hello', context: { user: 'test' } }),
        },
      );
    });

    it('returns parsed response', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'Reply', tokens_used: 5 });

      const result = await client.chat('Hi');
      expect(result.success).toBe(true);
      expect(result.text).toBe('Reply');
      expect(result.tokens_used).toBe(5);
    });

    it('handles connection errors gracefully', async () => {
      const client = new EBotClient();
      mockNetworkError();

      const result = await client.chat('test');
      expect(result.success).toBe(false);
      expect(result.text).toBe('');
      expect(result.error).toContain('Network error');
    });

    it('handles HTTP error responses', async () => {
      const client = new EBotClient();
      mockErrorResponse(500, 'Internal Server Error');

      const result = await client.chat('test');
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  describe('complete', () => {
    it('sends POST to /complete with prompt', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'completed text' });

      await client.complete('Write a poem');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/complete'),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: 'Write a poem' }),
        },
      );
    });

    it('returns completed text', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'Roses are red...' });

      const result = await client.complete('Write a poem');
      expect(result.text).toBe('Roses are red...');
    });
  });

  describe('summarize', () => {
    it('sends POST to /summarize with text', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'Summary here' });

      await client.summarize('Long text to summarize');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/summarize'),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: 'Long text to summarize' }),
        },
      );
    });
  });

  describe('getModels', () => {
    it('sends GET to /models', async () => {
      const client = new EBotClient();
      const models = [{ name: 'gpt-4', tier: 'premium', params: '175B' }];
      mockOkResponse({ models });

      const result = await client.getModels();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/models'),
        {
          method: 'GET',
          headers: { Accept: 'application/json' },
        },
      );
      expect(result.models).toEqual(models);
    });

    it('returns empty models on error', async () => {
      const client = new EBotClient();
      mockNetworkError();

      const result = await client.getModels();
      expect(result.models).toEqual([]);
    });
  });

  describe('getStatus', () => {
    it('sends GET to /status', async () => {
      const client = new EBotClient();
      mockOkResponse({ total_requests: 42, total_tokens: 1000 });

      const result = await client.getStatus();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/status'),
        expect.any(Object),
      );
      expect(result.total_requests).toBe(42);
      expect(result.total_tokens).toBe(1000);
    });

    it('returns zeroed status on error', async () => {
      const client = new EBotClient();
      mockNetworkError();

      const result = await client.getStatus();
      expect(result.total_requests).toBe(0);
      expect(result.total_tokens).toBe(0);
    });
  });

  describe('resetSession', () => {
    it('sends POST to /reset', async () => {
      const client = new EBotClient();
      mockOkResponse({});

      await client.resetSession();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/reset'),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        },
      );
    });
  });

  describe('isConnected', () => {
    it('returns false initially', () => {
      const client = new EBotClient();
      expect(client.isConnected()).toBe(false);
    });

    it('returns true after a successful request', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'response' });

      await client.chat('test');
      expect(client.isConnected()).toBe(true);
    });

    it('returns false after a failed request', async () => {
      const client = new EBotClient();
      mockNetworkError();

      await client.chat('test');
      expect(client.isConnected()).toBe(false);
    });

    it('transitions from connected to disconnected on error', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'ok' });
      await client.chat('test');
      expect(client.isConnected()).toBe(true);

      mockNetworkError();
      await client.chat('test');
      expect(client.isConnected()).toBe(false);
    });
  });

  describe('getStats', () => {
    it('returns initial stats with zero requests', () => {
      const client = new EBotClient();
      const stats = client.getStats();
      expect(stats.requests).toBe(0);
      expect(stats.connected).toBe(false);
    });

    it('increments request count after successful calls', async () => {
      const client = new EBotClient();
      mockOkResponse({ success: true, text: 'r1' });
      mockOkResponse({ success: true, text: 'r2' });
      mockOkResponse({ success: true, text: 'r3' });

      await client.chat('one');
      await client.chat('two');
      await client.chat('three');

      const stats = client.getStats();
      expect(stats.requests).toBe(3);
      expect(stats.connected).toBe(true);
    });

    it('does not increment on failed requests', async () => {
      const client = new EBotClient();
      mockNetworkError();

      await client.chat('fail');

      const stats = client.getStats();
      expect(stats.requests).toBe(0);
    });
  });
});
