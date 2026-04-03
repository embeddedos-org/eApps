import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  generateId,
  formatDate,
  truncateText,
  escapeJson,
  debounce,
} from '../utils';

describe('generateId', () => {
  it('returns a string of length 36 (UUID format)', () => {
    const id = generateId();
    expect(typeof id).toBe('string');
    expect(id.length).toBe(36);
  });

  it('contains hyphens at UUID positions', () => {
    const id = generateId();
    expect(id[8]).toBe('-');
    expect(id[13]).toBe('-');
    expect(id[18]).toBe('-');
    expect(id[23]).toBe('-');
  });

  it('has "4" as the version digit', () => {
    const id = generateId();
    expect(id[14]).toBe('4');
  });

  it('matches UUID v4 regex pattern', () => {
    const id = generateId();
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
    expect(id).toMatch(uuidRegex);
  });

  it('returns unique values on successive calls', () => {
    const ids = new Set<string>();
    for (let i = 0; i < 100; i++) {
      ids.add(generateId());
    }
    expect(ids.size).toBe(100);
  });
});

describe('formatDate', () => {
  it('returns a readable date string in YYYY-MM-DD HH:MM format', () => {
    const date = new Date(2025, 0, 15, 9, 5);
    const formatted = formatDate(date);
    expect(formatted).toBe('2025-01-15 09:05');
  });

  it('zero-pads single-digit month and day', () => {
    const date = new Date(2025, 2, 3, 14, 30);
    const formatted = formatDate(date);
    expect(formatted).toBe('2025-03-03 14:30');
  });

  it('handles midnight correctly', () => {
    const date = new Date(2025, 11, 31, 0, 0);
    const formatted = formatDate(date);
    expect(formatted).toBe('2025-12-31 00:00');
  });

  it('handles end-of-day time', () => {
    const date = new Date(2025, 5, 10, 23, 59);
    const formatted = formatDate(date);
    expect(formatted).toBe('2025-06-10 23:59');
  });
});

describe('truncateText', () => {
  it('returns short text unchanged when under maxLen', () => {
    expect(truncateText('Hello', 10)).toBe('Hello');
  });

  it('returns text unchanged when exactly at maxLen', () => {
    expect(truncateText('Hello', 5)).toBe('Hello');
  });

  it('truncates long text with ellipsis', () => {
    const result = truncateText('Hello World, this is a long text', 15);
    expect(result).toBe('Hello World,...');
    expect(result.length).toBe(15);
  });

  it('ends with "..." when truncated', () => {
    const result = truncateText('A very long string that should be truncated', 20);
    expect(result.endsWith('...')).toBe(true);
    expect(result.length).toBe(20);
  });

  it('handles empty string', () => {
    expect(truncateText('', 10)).toBe('');
  });
});

describe('escapeJson', () => {
  it('escapes double quotes', () => {
    expect(escapeJson('He said "hello"')).toBe('He said \\"hello\\"');
  });

  it('escapes backslashes', () => {
    expect(escapeJson('path\\to\\file')).toBe('path\\\\to\\\\file');
  });

  it('escapes newlines', () => {
    expect(escapeJson('line1\nline2')).toBe('line1\\nline2');
  });

  it('escapes carriage returns', () => {
    expect(escapeJson('line1\rline2')).toBe('line1\\rline2');
  });

  it('escapes tabs', () => {
    expect(escapeJson('col1\tcol2')).toBe('col1\\tcol2');
  });

  it('handles string with multiple escape characters', () => {
    expect(escapeJson('"hi"\n\\there')).toBe('\\"hi\\"\\n\\\\there');
  });

  it('returns empty string unchanged', () => {
    expect(escapeJson('')).toBe('');
  });

  it('returns plain string unchanged', () => {
    expect(escapeJson('hello world')).toBe('hello world');
  });
});

describe('debounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('delays function execution', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledOnce();
  });

  it('cancels previous calls when called again within delay', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    vi.advanceTimersByTime(50);
    debounced();
    vi.advanceTimersByTime(50);
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(50);
    expect(fn).toHaveBeenCalledOnce();
  });

  it('passes arguments to the debounced function', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced('arg1', 'arg2');
    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledWith('arg1', 'arg2');
  });

  it('uses the latest arguments when debounced', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced('first');
    debounced('second');
    debounced('third');
    vi.advanceTimersByTime(100);

    expect(fn).toHaveBeenCalledOnce();
    expect(fn).toHaveBeenCalledWith('third');
  });

  it('allows multiple separated calls', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledTimes(1);

    debounced();
    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledTimes(2);
  });
});
