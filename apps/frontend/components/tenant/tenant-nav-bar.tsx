'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChevronDown from 'lucide-react/dist/esm/icons/chevron-down';
import { useTenant } from '@/lib/context/tenant-context';
import { useTranslations } from '@/lib/i18n';
import { fetchConfiguredLanguages } from '@/lib/api/resume';
import { locales, localeNames, localeFlags, type Locale } from '@/i18n/config';
import { tenantPath } from '@/lib/utils/tenant-paths';

/** Shared top-bar chrome: switches between tenants (languages). Each tenant
 *  keeps its own resumes/tracker/etc.; landing on an unconfigured tenant's
 *  dashboard shows its own empty/upload-prompt state. A compact badge +
 *  dropdown, not the larger form-field-style shared Dropdown (which is sized
 *  for Settings-page pickers, not persistent top-bar chrome). */
export function TenantNavBar() {
  const { t } = useTranslations();
  const tenant = useTenant();
  const router = useRouter();
  const [configuredLanguages, setConfiguredLanguages] = useState<Set<string>>(new Set());
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    if (!isOpen) return;
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleSelect = (locale: Locale) => {
    setIsOpen(false);
    router.push(tenantPath(locale, '/dashboard'));
  };

  return (
    <div className="border-b border-black bg-white">
      <div className="mx-auto flex max-w-7xl justify-end px-4 py-2">
        <div className="relative" ref={containerRef}>
          <button
            type="button"
            onClick={() => setIsOpen((open) => !open)}
            aria-haspopup="menu"
            aria-expanded={isOpen}
            aria-label={t('tenantSwitcher.label')}
            className="flex items-center gap-1.5 rounded-none border border-black bg-white px-2.5 py-1.5 font-mono text-xs font-bold shadow-sw-xs transition-all duration-150 ease-out hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none"
          >
            <span>
              {localeFlags[tenant]} {localeNames[tenant]}
            </span>
            <ChevronDown
              className={`h-3 w-3 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {isOpen && (
            <div
              role="menu"
              aria-label={t('tenantSwitcher.label')}
              className="absolute right-0 top-full z-50 mt-1 w-44 rounded-none border border-black bg-white shadow-sw-default"
            >
              {locales.map((locale, index) => {
                const isActive = locale === tenant;
                return (
                  <button
                    key={locale}
                    type="button"
                    role="menuitemradio"
                    aria-checked={isActive}
                    onClick={() => handleSelect(locale)}
                    className={`flex w-full items-center justify-between gap-2 border border-black px-2.5 py-1.5 text-left font-mono text-xs transition-colors duration-150 ${
                      isActive
                        ? 'bg-green-700 text-white'
                        : 'bg-white text-black hover:bg-paper-tint'
                    } ${index > 0 ? '-mt-px' : ''}`}
                  >
                    <span>
                      {localeFlags[locale]} {localeNames[locale]}
                    </span>
                    <span className="text-[10px] uppercase opacity-80">
                      {configuredLanguages.has(locale)
                        ? t('tenantSwitcher.configured')
                        : t('tenantSwitcher.setUp')}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
