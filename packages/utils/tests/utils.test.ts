import { describe, expect, it } from 'vitest';
import {
  formatDuration,
  formatNumber,
  formatRelativeTime,
  pageRange,
  toQueryString,
} from '../src/index';

describe('formatDuration', () => {
  it('formats seconds', () => {
    expect(formatDuration(45)).toBe('45s');
  });
  it('formats minutes and seconds', () => {
    expect(formatDuration(200)).toBe('3m 20s');
  });
  it('formats hours and minutes', () => {
    expect(formatDuration(7500)).toBe('2h 05m');
  });
  it('handles null/undefined', () => {
    expect(formatDuration(null)).toBe('—');
    expect(formatDuration(undefined)).toBe('—');
  });
  it('clamps negatives to zero', () => {
    expect(formatDuration(-10)).toBe('0s');
  });
});

describe('formatRelativeTime', () => {
  const now = new Date('2026-07-02T12:00:00Z');
  it('formats minutes ago', () => {
    expect(formatRelativeTime('2026-07-02T11:55:00Z', now)).toBe('hace 5 min');
  });
  it('formats hours ago', () => {
    expect(formatRelativeTime('2026-07-02T09:00:00Z', now)).toBe('hace 3 h');
  });
  it('formats days ago', () => {
    expect(formatRelativeTime('2026-06-29T12:00:00Z', now)).toBe('hace 3 d');
  });
  it('handles invalid input', () => {
    expect(formatRelativeTime('no-fecha', now)).toBe('—');
    expect(formatRelativeTime(null, now)).toBe('—');
  });
});

describe('formatNumber', () => {
  it('adds thousands separator', () => {
    expect(formatNumber(12345)).toBe('12,345');
  });
  it('handles null', () => {
    expect(formatNumber(null)).toBe('—');
  });
});

describe('pageRange', () => {
  it('returns all pages when few', () => {
    expect(pageRange(2, 3)).toEqual([1, 2, 3]);
  });
  it('adds gaps around current page', () => {
    expect(pageRange(10, 20)).toEqual([1, '…', 9, 10, 11, '…', 20]);
  });
  it('handles zero pages', () => {
    expect(pageRange(1, 0)).toEqual([]);
  });
});

describe('toQueryString', () => {
  it('omits empty values', () => {
    expect(toQueryString({ a: '1', b: undefined, c: '' })).toBe('?a=1');
  });
  it('returns empty string when nothing set', () => {
    expect(toQueryString({})).toBe('');
  });
  it('encodes values', () => {
    expect(toQueryString({ etl: 'etl cobranza' })).toBe('?etl=etl+cobranza');
  });
});
