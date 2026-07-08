'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { locales, defaultLocale, localeNames, type Locale } from '@/i18n/config';

const UI_STORAGE_KEY = 'resume_matcher_ui_language';

interface LanguageContextValue {
  uiLanguage: Locale;
  setUiLanguage: (lang: Locale) => void;
  languageNames: typeof localeNames;
  supportedLanguages: readonly Locale[];
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [uiLanguage, setUiLanguageState] = useState<Locale>(defaultLocale);

  // UI language is a client-only setting shared across tenants (unlike content
  // language, which is now the tenant itself — see useTenant()).
  useEffect(() => {
    const cachedUiLang = localStorage.getItem(UI_STORAGE_KEY);
    if (cachedUiLang && locales.includes(cachedUiLang as Locale)) {
      setUiLanguageState(cachedUiLang as Locale);
    }
  }, []);

  const setUiLanguage = useCallback((lang: Locale) => {
    if (!locales.includes(lang)) {
      console.error(`Unsupported UI language: ${lang}`);
      return;
    }
    setUiLanguageState(lang);
    localStorage.setItem(UI_STORAGE_KEY, lang);
  }, []);

  return (
    <LanguageContext.Provider
      value={{
        uiLanguage,
        setUiLanguage,
        languageNames: localeNames,
        supportedLanguages: locales,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
