import { describe, expect, it } from 'vitest';
import { tenantStorageKey } from '@/lib/utils/tenant-storage-key';

describe('tenantStorageKey', () => {
  it('suffixes the base key with the tenant', () => {
    expect(tenantStorageKey('en', 'resume_builder_draft')).toBe('resume_builder_draft_en');
    expect(tenantStorageKey('fr', 'resume_builder_draft')).toBe('resume_builder_draft_fr');
  });

  it('produces distinct keys per tenant for the same base key', () => {
    const en = tenantStorageKey('en', 'resume_wizard_draft');
    const fr = tenantStorageKey('fr', 'resume_wizard_draft');
    expect(en).not.toBe(fr);
  });
});
