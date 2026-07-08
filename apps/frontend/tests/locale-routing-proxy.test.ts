import { describe, expect, it } from 'vitest';
import { pathnameHasLocale } from '@/proxy';

describe('pathnameHasLocale', () => {
  it('recognizes an exact locale-root path', () => {
    expect(pathnameHasLocale('/en')).toBe(true);
    expect(pathnameHasLocale('/fr')).toBe(true);
  });

  it('recognizes a locale-prefixed path', () => {
    expect(pathnameHasLocale('/en/dashboard')).toBe(true);
    expect(pathnameHasLocale('/fr/tracker')).toBe(true);
  });

  it('rejects a locale-less path', () => {
    expect(pathnameHasLocale('/dashboard')).toBe(false);
    expect(pathnameHasLocale('/')).toBe(false);
  });

  it('does not match a locale as a substring of another segment', () => {
    expect(pathnameHasLocale('/energy')).toBe(false);
    expect(pathnameHasLocale('/frank')).toBe(false);
  });

  it('rejects an unsupported locale-looking prefix', () => {
    expect(pathnameHasLocale('/xx/dashboard')).toBe(false);
  });
});
