'use client';

import { useParams } from 'next/navigation';
import { locales, defaultLocale, type Locale } from '@/i18n/config';

/** The active tenant (content language), derived from the `[locale]` route segment. */
export function useTenant(): Locale {
  const params = useParams<{ locale: string }>();
  const candidate = params?.locale;
  return locales.includes(candidate as Locale) ? (candidate as Locale) : defaultLocale;
}
