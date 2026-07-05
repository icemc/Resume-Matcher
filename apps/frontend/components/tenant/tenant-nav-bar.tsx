'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Dropdown, type DropdownOption } from '@/components/ui/dropdown';
import { useTenant } from '@/lib/context/tenant-context';
import { useTranslations } from '@/lib/i18n';
import { fetchConfiguredLanguages } from '@/lib/api/resume';
import { locales, localeNames, localeFlags, type Locale } from '@/i18n/config';
import { tenantPath } from '@/lib/utils/tenant-paths';

/** Shared top-bar chrome: switches between tenants (languages). Each tenant
 *  keeps its own resumes/tracker/etc.; landing on an unconfigured tenant's
 *  dashboard shows its own empty/upload-prompt state. */
export function TenantNavBar() {
  const { t } = useTranslations();
  const tenant = useTenant();
  const router = useRouter();
  const [configuredLanguages, setConfiguredLanguages] = useState<Set<string>>(new Set());

  useEffect(() => {
    let cancelled = false;
    fetchConfiguredLanguages()
      .then((languages) => {
        if (!cancelled) setConfiguredLanguages(new Set(languages));
      })
      .catch(() => {
        if (!cancelled) setConfiguredLanguages(new Set());
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const options: DropdownOption[] = locales.map((locale) => ({
    id: locale,
    label: `${localeFlags[locale]} ${localeNames[locale]}`,
    description: configuredLanguages.has(locale)
      ? t('tenantSwitcher.configured')
      : t('tenantSwitcher.setUp'),
  }));

  return (
    <div className="border-b border-black bg-white">
      <div className="mx-auto flex max-w-7xl justify-end px-4 py-2">
        <div className="w-64">
          <Dropdown
            options={options}
            value={tenant}
            onChange={(locale) => router.push(tenantPath(locale as Locale, '/dashboard'))}
          />
        </div>
      </div>
    </div>
  );
}
