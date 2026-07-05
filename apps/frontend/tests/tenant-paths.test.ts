import { describe, expect, it } from 'vitest';
import { tenantPath } from '@/lib/utils/tenant-paths';

describe('tenantPath', () => {
  it('prefixes a path with the tenant locale', () => {
    expect(tenantPath('en', '/dashboard')).toBe('/en/dashboard');
    expect(tenantPath('fr', '/tracker')).toBe('/fr/tracker');
  });

  it('adds a leading slash to a bare path', () => {
    expect(tenantPath('en', 'dashboard')).toBe('/en/dashboard');
  });

  it('preserves query strings', () => {
    expect(tenantPath('en', '/builder?id=abc')).toBe('/en/builder?id=abc');
  });
});
