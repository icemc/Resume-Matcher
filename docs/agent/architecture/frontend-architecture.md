# Frontend Architecture

> Next.js 15 + React 19 | TypeScript | Tailwind | Swiss International Style

## Directory Structure

```
apps/frontend/
├── app/
│   ├── [locale]/             # Tenant-scoped routes — locale = tenant (en, es, zh, ja, pt, fr)
│   │   ├── layout.tsx        # Validates the locale param, generateStaticParams()
│   │   └── (default)/        # Main app routes (route group — no URL contribution)
│   │       ├── page.tsx      # Landing (/[locale])
│   │       ├── dashboard/    # /[locale]/dashboard
│   │       ├── builder/      # /[locale]/builder
│   │       ├── tailor/       # /[locale]/tailor
│   │       ├── tracker/      # /[locale]/tracker
│   │       ├── settings/     # /[locale]/settings
│   │       ├── resume-wizard/# /[locale]/resume-wizard
│   │       └── resumes/[id]/ # /[locale]/resumes/[id]
│   └── print/                # Print routes for PDF — locale-free by design
├── proxy.ts                  # Redirects locale-less paths to /${defaultLocale}${pathname}
├── components/
│   ├── ui/                  # Button, Input, Dialog, etc.
│   ├── builder/             # ResumeBuilder, forms/
│   ├── tenant/               # tenant-nav-bar.tsx — shared tenant switcher chrome
│   ├── tracker/              # Kanban board
│   ├── preview/              # PaginatedPreview, usePagination
│   └── resume/               # Templates (single, two-column)
├── lib/
│   ├── api/                  # client.ts, resume.ts, tracker.ts, config.ts
│   ├── context/               # status-cache.tsx, language-context.tsx (UI language only), tenant-context.tsx (useTenant())
│   ├── utils/                 # tenant-paths.ts, tenant-storage-key.ts, ...
│   └── constants/             # page-dimensions.ts
└── messages/                 # i18n translations
```

> Each supported language is its own **tenant** — see [i18n.md](../features/i18n.md) and [language-tenant-dashboards.md](../../plans/language-tenant-dashboards.md) for the full architecture.

## Pages

### Dashboard (`/[locale]/dashboard`)
- Master resume card + tailored resume tiles, scoped to the active tenant (`useTenant()`)
- States: `loading | pending | processing | ready | failed`
- Auto-refreshes on window focus
- Master resume id is derived live from `fetchResumeList(tenant, true)`'s `is_master` flag — **not** cached in localStorage (the old `master_resume_id` key is retired)

### Builder (`/builder`)
- Left: Editor Panel (forms + formatting controls)
- Right: WYSIWYG PaginatedPreview
- Tabs: Resume | Cover Letter | Outreach
- Auto-saves to localStorage

### Tailor (`/tailor`)
- Job description textarea
- Calls: `POST /jobs/upload` → `POST /resumes/improve`
- Redirects to `/resumes/[new_id]`

### Settings (`/settings`)
- Provider selection (6 providers)
- API key input
- System status (cached, 30-min refresh)

### Print Routes (`/print/resumes/[id]`, `/print/cover-letter/[id]`)
- Headless Chrome renders these for PDF
- Query params: template, pageSize, margins, spacing

## UI Components

**Button variants:** default (blue), destructive (red), success (green), warning (orange), outline, secondary

**Styling:** `rounded-none`, hard shadows, `font-mono` for labels

## Context Providers

### StatusCacheProvider
```typescript
const { status, refreshStatus, incrementResumes, decrementResumes } = useStatusCache();
```
- Caches system status, 30-min auto-refresh
- Optimistic counter updates on user actions

### LanguageProvider
```typescript
const { uiLanguage, setUiLanguage } = useLanguage();
```
- **UI language only** — one global setting shared across every tenant, localStorage-backed.
- Content language is no longer a separate setting here — it *is* the tenant (see `useTenant()` below).

### `useTenant()`
```typescript
const tenant = useTenant(); // from lib/context/tenant-context.tsx
```
- Derives the active tenant from the `[locale]` route param (`useParams()`), falling back to the default locale for an invalid/missing segment.
- No provider needed — purely derived.

## API Client (`lib/api/`)

```typescript
import { fetchResume, API_BASE } from '@/lib/api';

// client.ts exports
API_URL, API_BASE, apiFetch, apiPost, apiPatch, apiDelete, withTenant

// resume.ts — fetchResume/fetchResumeList/uploadJobDescriptions take language (tenant) as a required param
uploadJobDescriptions, improveResume, fetchResume, fetchResumeList, fetchConfiguredLanguages
updateResume, downloadResumePdf, deleteResume

// config.ts
fetchLlmConfig, updateLlmConfig, testLlmConnection, fetchSystemStatus
```

## localStorage Keys

| Key | Scope | Purpose |
|-----|-------|---------|
| `resume_matcher_ui_language` | Global | UI language |
| `${baseKey}_${tenant}` (via `tenantStorageKey()`) | Per-tenant | Auto-saved builder/wizard drafts + template settings |

`master_resume_id` is **retired** — always derived live from the tenant-scoped resume list, never cached.

## Pagination System

`usePagination` hook calculates page breaks:
- Respects `.resume-item` boundaries
- Prevents orphaned headers
- 150ms debounce for performance

## Critical CSS Rule

For PDF generation, `globals.css` must whitelist print classes:
```css
@media print {
  body * { visibility: hidden !important; }
  .resume-print, .resume-print * { visibility: visible !important; }
  .cover-letter-print, .cover-letter-print * { visibility: visible !important; }
}
```
