/** Scopes a client-only localStorage key (e.g. an unsaved draft) to a tenant,
 *  so switching tenants never bleeds one tenant's draft into another's. */
export function tenantStorageKey(tenant: string, baseKey: string): string {
  return `${baseKey}_${tenant}`;
}
