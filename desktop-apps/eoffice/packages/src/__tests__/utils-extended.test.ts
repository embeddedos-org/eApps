import { describe, it, expect } from 'vitest';
import { sanitizeString, validateId } from '../utils';

describe('sanitizeString', () => {
  it('strips HTML tags from input', () => {
    expect(sanitizeString('<b>bold</b> text')).toBe('bold text');
  });

  it('trims leading and trailing whitespace', () => {
    expect(sanitizeString('  hello  ')).toBe('hello');
  });

  it('limits output to default maxLength of 10000', () => {
    const long = 'a'.repeat(20000);
    expect(sanitizeString(long)).toHaveLength(10000);
  });

  it('handles empty string', () => {
    expect(sanitizeString('')).toBe('');
  });

  it('respects custom maxLength parameter', () => {
    expect(sanitizeString('abcdefghij', 5)).toBe('abcde');
  });
});

describe('validateId', () => {
  it('returns true for a valid UUID v4', () => {
    expect(validateId('550e8400-e29b-41d4-a716-446655440000')).toBe(true);
  });

  it('returns false for an invalid UUID', () => {
    expect(validateId('not-a-uuid')).toBe(false);
  });

  it('returns false for empty string', () => {
    expect(validateId('')).toBe(false);
  });
});
