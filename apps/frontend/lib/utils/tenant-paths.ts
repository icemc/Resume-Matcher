import type { Locale } from '@/i18n/config';

/** Prefixes an internal app path with the active tenant's locale segment. */
export function tenantPath(locale: Locale, path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `/${locale}${normalized}`;
}
