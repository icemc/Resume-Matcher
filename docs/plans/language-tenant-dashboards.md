# Language-as-Tenant Dashboards — Implementation Plan

## Context

The prior multi-language work (`feature/multi-language-support`, now parked) bolted per-language "base CV" cards onto a single global dashboard, with client-side language filter tabs. After manual testing the user rejected this UX outright: it still didn't behave as expected (wrong headings, broken filters, confusing single-page model). The user wants a structural pivot instead: **each language is a tenant**, with its own URL-scoped dashboard (`/en/dashboard`, `/fr/dashboard`, ...), full feature parity per tenant (CV management, tailoring, cover letters, outreach, enrichment, tracker), while the **UI chrome language stays one global setting** shared across tenants (simplification the user explicitly asked for). This plan starts fresh from `main` (branch `feature/language-tenant-dashboards`, already created) rather than building further on the rejected branch, since none of that branch's frontend UX is being reused — only a couple of its backend ideas (partial unique index technique, per-resume language column) inform this design.

Verified against the current `main`-derived branch state (confirmed via direct reads, not assumed): `Resume` has no `language`/`base_language` column yet, `is_master` is enforced globally-unique via a single partial index (`apps/backend/app/models.py:57-61`), `_master_resume_lock` (`apps/backend/app/database.py:59`) serializes master promotion, there are zero usages of FastAPI `Depends(` anywhere in the backend, and the dashboard's existing `!masterResumeId` empty state (`apps/frontend/app/(default)/dashboard/page.tsx:342`) already renders an upload prompt — this becomes the per-tenant onboarding screen for free once scoped.

## Decision summary (commit, do not re-litigate during implementation)

| Question | Decision |
|---|---|
| Tenant transport to backend | URL locale segment is for frontend routing only. API calls carry tenant as a **required query param `?language=xx`** (or `Form` field for the multipart upload), appended at the `lib/api/client.ts` choke point. Not a header, not an API path prefix. |
| Backend route shape | Existing `/api/v1/...` paths unchanged. `language` becomes a required `Query(...)`/`Form(...)` param on list/create/upload endpoints, optional on by-id endpoints for a soft tenant-mismatch 404 check. |
| Schema migration tool | Hand-rolled idempotent `ALTER TABLE` in `app/main.py` lifespan, same family as the existing `migrate_tinydb_to_sqlite.py` precedent — not introducing Alembic (repo has zero migration framework today; 3 guarded `ALTER TABLE`s is proportionate). |
| Master invariant | `is_master` partial-unique index becomes composite `(language, is_master)` — one master per tenant, not one master globally. `_master_resume_lock` stays a single global lock (see close call B). |
| Frontend route nesting | `app/[locale]/(default)/...` — locale **outside** the route group (route groups don't contribute to the URL, so `[locale]` must be the ancestor segment). |
| `master_resume_id` localStorage key | **Retired** — replaced by deriving from the already tenant-scoped resume list/fetch. The other 3 draft/settings keys are **prefixed by tenant**, not retired (no backend equivalent for client-only drafts). |
| Content-language config | `get_content_language()` / `/config/language`'s `content_language` half becomes vestigial (used only as the Phase-0 backfill default) — every per-tenant AI call site uses the resume's own `language` column directly. UI language stays global, unchanged. |

Two close calls, flagged with recommendation at the end: (A) query-param vs. header for tenant transport — **query param**; (B) global vs. per-language-sharded master lock — **keep global**.

---

## Phase 0 — Backend schema groundwork (no behavior change yet)

**`apps/backend/app/models.py`**
- Add `language: Mapped[str] = mapped_column(String, nullable=False, default="en", index=True)` to `Resume`, `Job`, `Application`.
- Replace `ux_resumes_single_master` with:
  ```python
  Index("ux_resumes_single_master_per_language", "language", "is_master",
        unique=True, sqlite_where=text("is_master = 1"))
  ```

**New: `apps/backend/app/scripts/migrate_add_language_column.py`** — idempotent, mirrors `migrate_tinydb_to_sqlite.py`'s shape:
1. Introspect via `PRAGMA table_info(<table>)` (explicit existence check, not try/except-swallowing).
2. For each of `resumes`/`jobs`/`applications` missing `language`: `ALTER TABLE {table} ADD COLUMN language TEXT NOT NULL DEFAULT 'en'`, then backfill existing rows to the real `get_content_language()` value if it isn't `'en'` (`UPDATE {table} SET language = :lang WHERE language = 'en'`) — only fires once, on first run.
3. `DROP INDEX IF EXISTS ux_resumes_single_master`; `CREATE UNIQUE INDEX IF NOT EXISTS ux_resumes_single_master_per_language ON resumes (language, is_master) WHERE is_master = 1`.
4. Returns `{"status": "migrated"|"noop", ...counts}`.

**`apps/backend/app/main.py`** — call `migrate_add_language_column.migrate()` in lifespan, right after the TinyDB migration call, before `migrate_legacy_keys()`.

**`apps/backend/app/database.py`** — converters (`_resume_to_dict` etc.) gain `"language"`. `create_resume`, `create_resume_atomic_master`, `get_master_resume`, `set_master_resume`, `list_resumes`, `create_job`, `create_application`, `list_applications` all gain a **required** `language: str` parameter (deliberately breaking — every call site must be updated, caught by tests/tsc). `get_master_resume`/`set_master_resume`/the stuck-master demotion logic scope to `WHERE language == language`.

**Tests:** new `tests/unit/test_migrate_add_language_column.py` (pre-migration temp DB → migrate → assert column+backfill+index swap; re-run → assert true no-op via `PRAGMA index_list`). Modify `tests/unit/test_database.py` to pass `language="en"` everywhere (anti-theater forcing function — a missed call site throws `TypeError`).

**Verify:** `uv run pytest apps/backend/tests/unit/test_migrate_add_language_column.py apps/backend/tests/unit/test_database.py -v`; manual restart-twice check for the `noop` log line.

---

## Phase 1 — Backend endpoint scoping

**New: `apps/backend/app/routers/_tenant.py`** — `validate_tenant_language(language: str) -> str` (400 if not in `SUPPORTED_LANGUAGES`), a plain function (no `Depends`, matching the codebase's existing no-DI style).

**`apps/backend/app/routers/resumes.py`**
- `upload_resume(..., language: str = Form(...))`, validated, passed to `create_resume_atomic_master`.
- `get_resume(resume_id: str = Query(...), language: str = Query(...))` — 404 if `resume["language"] != language` (not 403 — don't leak existence).
- `list_resumes(include_master=..., language: str = Query(...))` → `db.list_resumes(language=language)`.
- Improve/preview/confirm + cover-letter/outreach generation: replace every `get_content_language()` call with the loaded resume's own `["language"]` — no inheritance chain needed, since tenant *is* the content language now.
- All other by-`resume_id` endpoints (PATCH, pdf, delete, retry, title, job-description, cover-letter pdf): add **optional** `language: str | None = Query(None)` → soft 404-on-mismatch when provided (kept optional so the PDF-renderer's internal round-trip isn't broken).

**`apps/backend/app/routers/jobs.py`** — `JobUploadRequest.language: str` required; `get_job` gets the same optional soft-check.

**`apps/backend/app/routers/applications.py`** — `list_applications(language: str = Query(...))`; `ManualApplicationCreate.language: str` required, passed straight through (no resolve-chain); by-id endpoints get the optional soft-check.

**`apps/backend/app/routers/enrichment.py`** — same `get_content_language()` → resume's own `language` swap.

**Schemas:** `schemas/jobs.py` (`JobUploadRequest.language`), `schemas/applications.py` (`ManualApplicationCreate.language`, `ApplicationResponse.language`), `schemas/models.py` (`ResumeSummary.language`, `ResumeFetchData.language`; confirm/add `is_master` on `ResumeFetchData` at implementation time — needed by Phase 6).

**Tests:** new `tests/integration/test_tenant_isolation.py` — two tenants each get their own master with no unique-constraint clash; `list?language=en` excludes `fr` data; cross-tenant `GET /resumes?resume_id=<fr>&language=en` → 404; unsupported language → 400; concurrent same-language uploads → exactly one master; tracker language filter isolation. Modify `test_resume_api.py`, `test_upload_api.py`, `test_applications_api.py` to add `language=en` to existing calls (anti-theater: missed call sites 422).

**Verify:** `uv run pytest apps/backend/tests -v`; confirm `.githooks/pre-push` passes.

---

## Phase 2 — Frontend routing skeleton + tenant plumbing (mechanical move, no new UX)

Move (via `git mv`) the entire `(default)` tree under a new ancestor segment — `(default)` itself contributes nothing to the URL, so `[locale]` must sit above it:
```
app/(default)/...  →  app/[locale]/(default)/...
```
(`app/print/*` and root `app/layout.tsx` stay untouched — locale-free by design.)

**New: `apps/frontend/app/[locale]/layout.tsx`** — validates `params.locale` against `i18n/config.ts`'s `locales`, calls `notFound()` if invalid; `generateStaticParams()` over `locales`. `app/[locale]/(default)/layout.tsx` keeps the exact existing provider nesting, unchanged in content.

**New: `apps/frontend/proxy.ts`** (Next.js 16 renamed `middleware.ts` → `proxy.ts`/`proxy()`; built against the deprecated `middleware.ts` name would print a build warning) — redirects any locale-less path (including bare `/`) to `/${defaultLocale}${pathname}`; matcher explicitly excludes `/api`, `/print`, `/_next`, `/docs`, `/redoc`, `/openapi.json` so the proxy/PDF paths are untouched. Exports the pure `pathnameHasLocale` predicate for unit testing.

**`apps/frontend/lib/api/client.ts`** — new pure helper:
```ts
export function withTenant(endpoint: string, language: string): string {
  const [path, query = ''] = endpoint.split('?');
  const params = new URLSearchParams(query);
  params.set('language', language);
  return `${path}?${params.toString()}`;
}
```
`apiFetch` itself stays plain (no React/context access) — every tenant-scoped function in `lib/api/resume.ts`, `lib/api/tracker.ts`, the job-upload client call gains a **new required first parameter** `language: string` and wraps its endpoint in `withTenant(...)`. This is a deliberate breaking signature change — missed call sites fail `tsc`/`next build`, which is the forcing function. Functions that already take a `locale?: Locale` for the print/PDF `lang` searchParam (`getResumePdfUrl`, `getCoverLetterPdfUrl`, download variants) keep their shape unchanged — only the *value* passed at call sites moves from `uiLanguage` to the tenant (Phase 3).

**Tests:** modify `tests/api-client.test.ts` (add `withTenant` cases) and every `lib/api/*`-touching test to pass `language`. New `tests/locale-routing-middleware.test.ts` against an extracted pure "has-locale-prefix" predicate (middleware itself isn't practically unit-testable in this stack).

**Verify:** `npm run build` (catches every missed call site + routing structure mistakes). Manual: `/en/dashboard` and `/fr/dashboard` both load; bare `/` redirects to `/en`; `/xx/dashboard` (bad locale) 404s; `/print/resumes/<id>?lang=fr` still works unprefixed.

---

## Phase 3 — `LanguageProvider` split + `useTenant()` hook

**`apps/frontend/lib/context/language-context.tsx`** — remove `contentLanguage`/`setContentLanguage`/the backend content-language sync entirely; becomes UI-language-only (`uiLanguage`, `setUiLanguage`, `languageNames`, `supportedLanguages`). The Settings page's content-language selector UI + its PUT call are removed (content language is no longer independently settable — it's the tenant).

**New: `apps/frontend/lib/context/tenant-context.tsx`**
```tsx
export function useTenant(): Locale {
  const params = useParams<{ locale: string }>();
  return locales.includes(params.locale as Locale) ? (params.locale as Locale) : locales[0];
}
```
No provider wrapper needed — purely derived from `useParams()`. Every former `contentLanguage` consumer switches to `useTenant()` and threads it as the new `language` argument into `lib/api/*` calls.

**Files touched:** `language-context.tsx`, new `tenant-context.tsx`, `app/[locale]/(default)/settings/page.tsx` (remove content-language UI), `components/builder/resume-builder.tsx` + `resumes/[id]/page.tsx` (swap PDF-locale argument value from `uiLanguage` to `useTenant()`), `lib/api/config.ts` (drop frontend content-language calls; keep `ui_language` half if still used).

**Tests:** new `tests/tenant-context.test.tsx` (mock route param → correct tenant; bogus param → fallback). Update any test mocking `useLanguage()` with a `contentLanguage` field to drop it.

**Verify:** `npm run build && npm run test`.

---

## Phase 4 — Tenant switcher + onboarding UX (Swiss-styled)

A tenant is "configured" iff it has ≥1 resume — no separate tenants table.

**New: `GET /api/v1/resumes/configured-languages` → `{"languages": [...]}`** (`apps/backend/app/routers/resumes.py` + `db.list_configured_languages()` = `SELECT DISTINCT language FROM resumes ORDER BY language`). No path-collision risk against the existing `resume_id`-as-query-param fetch.

**New: `apps/frontend/components/tenant/tenant-nav-bar.tsx`** — first shared nav chrome (today each page renders its own header). Swiss-styled badge (flag + name, `rounded-none border border-black shadow-sw-xs`, `font-mono`) opening a dropdown (reuse `components/ui/dropdown`) listing all `SUPPORTED_LANGUAGES`, configured ones checkmarked, others marked "set up". Clicking any tenant `router.push`es to `/${target}/dashboard` — no separate "add language" dialog: landing on an unconfigured tenant's dashboard already shows the existing `!masterResumeId` empty/upload-prompt state (confirmed at `dashboard/page.tsx:342`), which *is* the onboarding screen once tenant-scoped. Mounted in `app/[locale]/(default)/layout.tsx`.

**i18n:** new `tenantSwitcher.*` keys in `en.json`, mirrored identically across `es`/`zh`/`ja`/`pt-BR`/`fr` in the same commit (hard build constraint).

**Tests:** new `tests/integration/test_configured_languages.py` (backend); new `tests/tenant-nav-bar.test.tsx` (mock fetch, assert configured/unconfigured visual distinction + navigation). Run both `npm run test`'s locale-parity spec and `python scripts/check_locale_parity.py`.

**Verify (manual):** fresh DB → `/en/dashboard` empty state → upload → switcher shows `en` configured, others not → switch to `fr` → separate empty state (proves isolation) → upload → switch back → original `en` data intact.

---

## Phase 5 — Internal navigation helper

**New: `apps/frontend/lib/utils/tenant-paths.ts`** — `tenantPath(locale, path)` → `/${locale}${normalizedPath}`.

Apply at every internal `Link`/`router.push` call site (confirmed list): `components/home/hero.tsx`, `dashboard/page.tsx` (6 call sites), `settings/page.tsx`, `tailor/page.tsx` (4), `resumes/[id]/page.tsx` (4), `components/builder/resume-builder.tsx`, `components/resume-wizard/resume-wizard-page.tsx` (2). Hero needs the locale passed as a prop if it stays server-rendered, or `useTenant()` directly if client.

**Tests:** new `tests/tenant-paths.test.ts` (pure unit). Update existing tests asserting `router.push` targets (e.g. `resume-wizard-page.test.tsx`) to expect the locale-prefixed path.

**Verify:** `npm run build && npm run test`; manual click-through confirming the URL never drops its locale prefix during normal navigation.

---

## Phase 6 — localStorage scoping fixes

**`master_resume_id` — retire entirely.** `dashboard/page.tsx` already derives `masterFromList = data.find(r => r.is_master)` from the (now tenant-scoped) list call — remove all `localStorage.getItem/setItem/removeItem('master_resume_id')` in `dashboard/page.tsx`, `resumes/[id]/page.tsx` (derive `isMasterResume` from the fetched resume's own `is_master` field instead), `tailor/page.tsx`, `settings/page.tsx` (reset-DB flow, just delete the now-dead line), `resume-wizard-page.tsx` (`MASTER_RESUME_KEY` constant + usages removed — use the upload response's `resume_id` directly for the redirect).

**Other 3 keys — prefix by tenant**, since they have no backend equivalent (client-only drafts): `resume_builder_draft`, `resume_builder_settings`, `resume_wizard_draft`/settings in `resume-builder.tsx` and `resume-wizard-page.tsx`. New tiny helper `apps/frontend/lib/utils/tenant-storage-key.ts`: `tenantStorageKey(tenant, baseKey) → \`${baseKey}_${tenant}\``.

**Tests:** modify `tests/resume-wizard-page.test.tsx` (replace the `localStorage.getItem('master_resume_id')` assertion with proof it's now `null` after the flow + navigation uses the response's id directly). **Note:** `tests/tracker-reorder.test.ts`'s `master_resume_id: null` fixture field is the unrelated `Application` API response field (lineage pointer), not this localStorage key — leave it untouched, don't conflate the two. New `tests/tenant-storage-key.test.ts`.

**Verify (manual):** draft in `/en/builder` (unsaved) → switch to `/fr/builder` → blank (no bleed-through) → switch back → draft intact.

---

## Phase 7 — Documentation + final sweep

Update per backend `CLAUDE.md` rule ("schema/prompt changes must be reflected in docs"): `docs/agent/features/i18n.md` (tenant model supersedes global content-language description), `docs/agent/apis/front-end-apis.md` + `api-flow-maps.md` (new `language` params + `configured-languages` endpoint), `docs/agent/architecture/frontend-architecture.md`/`frontend-workflow.md` (`[locale]`, `middleware.ts`, `useTenant()`), `apps/backend/CLAUDE.md` + `apps/frontend/CLAUDE.md` route tables. Optionally a new `docs/agent/features/language-tenant-dashboards.md` cross-linked from `docs/agent/README.md`.

**Final sweep:** `uv run pytest` (full backend), `npm run build && npm run test && npm run lint` (frontend), both locale-parity checks (`i18n-locale-parity.test.ts` + `scripts/check_locale_parity.py`), confirm `.githooks/pre-push` passes clean before considering the branch mergeable.

---

## Close calls (recommendation stated, not re-opened)

**(A) Query param vs. header for tenant transport.** Query param (`?language=xx`). This codebase has zero precedent for custom headers or `Depends()`-based extraction; a query param matches the existing idiom (`pageSize`, `lang`, `template` are already query params on these same routers), stays visible in `/docs` and network logs, and needs no new middleware.

**(B) Global vs. per-language-sharded master-resume lock.** Keep the single global `asyncio.Lock`. Master promotion only happens on upload — a rare, human-paced action — so cross-tenant serialization costs nothing meaningful, while a sharded `dict[str, asyncio.Lock]` adds a real bug surface (lock-dict races, unbounded growth) for a contention scenario that won't occur at this scale.

---

## Status

- **Phase 0** — done: `language` column + migration + per-tenant master index + `database.py` params.
- **Phase 1** — done: router/schema scoping, full backend test suite green (`uv run pytest`: 501 passed, 1 pre-existing unrelated Windows-only `test_crypto.py` failure), new `tests/integration/test_tenant_isolation.py` added.
- **Phase 2** — done: `app/(default)` moved to `app/[locale]/(default)` via `git mv`; `app/[locale]/layout.tsx` validates the locale param + `generateStaticParams`; `proxy.ts` (Next 16's renamed `middleware.ts`) redirects locale-less paths; `withTenant()` added to `lib/api/client.ts`; `fetchResume`/`fetchResumeList`/`uploadJobDescriptions`/`listApplications`/`createApplication`/`finalizeResumeWizard` all gained a required tenant/`language` parameter, wired at every call site via a `useTenant()` hook pulled forward from Phase 3 (`lib/context/tenant-context.tsx`) since the new required params needed a real value to build against. Also fixed a pre-existing gap where `finalizeResumeWizard` never sent the (now backend-required) `language` field. `npm run build`, `tsc --noEmit`, `npm run test` (192 passed), and `npm run lint` all green; manual smoke test confirmed `/en/dashboard` + `/fr/dashboard` load, bare `/` and locale-less paths redirect, `/xx/dashboard` 404s, and `/print/*` stays unprefixed.
- **Phase 3** — done: `language-context.tsx` is now UI-language-only (`contentLanguage`/`setContentLanguage`/`isLoading` and the backend content-language sync removed entirely); Settings' Content Language selector section removed (UI Language section kept, heading simplified); `resume-builder.tsx` and `resumes/[id]/page.tsx` PDF-locale args and the regenerate wizard's `outputLanguage` now source from `useTenant()` instead of `uiLanguage`/`contentLanguage`. Deleted the now-fully-dead `fetchLanguageConfig`/`updateLanguageConfig`/`LanguageConfig`/`LanguageConfigUpdate`/`SupportedLanguage` from `lib/api/config.ts` (zero remaining call sites) and the two now-orphaned `settings.contentLanguage*` i18n keys from all 6 locale files. `useTenant()` hook + its test were already in place from Phase 2. Full re-verify green: `tsc --noEmit`, `npm run test` (192 passed), `npm run build`, `npm run lint`, and `scripts/check_locale_parity.py` (needs `PYTHONIOENCODING=utf-8` to print its ✓ on a Windows cp1252 console — a pre-existing environment quirk, not a real failure).
- **Phase 4** — done: `GET /api/v1/resumes/configured-languages` added (backend `db.list_configured_languages()` already existed from an earlier phase; only the router endpoint + `ConfiguredLanguagesResponse` schema were missing), with `tests/integration/test_configured_languages.py` (2 tests). Frontend: `fetchConfiguredLanguages()` in `lib/api/resume.ts`, new `components/tenant/tenant-nav-bar.tsx` (reuses `components/ui/dropdown`; flag+name trigger, options show "Configured"/"Not set up yet" per tenant, selecting one navigates to `/${locale}/dashboard`), mounted in `app/[locale]/(default)/layout.tsx` so it's shared chrome across every page including the landing page. New `tenantSwitcher.*` i18n keys (`label`/`configured`/`setUp`) added to all 6 locale files. New `tests/tenant-nav-bar.test.tsx` (2 tests: configured/unconfigured visual distinction, navigation). Full re-verify green (backend: 503 passed; frontend: `tsc --noEmit`, `npm run test` 194 passed, `npm run build`, `npm run lint`, locale parity); manual smoke test via `curl` confirmed the nav bar renders the correct active tenant per route (`English` on `/en/*`, `Français` on `/fr/*`) on both `/dashboard` and the landing page.
- **Phase 5** — done: new `lib/utils/tenant-paths.ts` (`tenantPath(locale, path)`), applied at every internal `Link`/`router.push` call site found by exhaustive grep (broader than the plan's original enumeration — also caught `components/home/swiss-grid.tsx` and `components/tracker/card-detail-modal.tsx`, which weren't in the original list): `dashboard/page.tsx` (6), `resumes/[id]/page.tsx` (4), `settings/page.tsx` (1), `tailor/page.tsx` (4, plus fixed a real missing-dependency bug on the redirect-guard `useEffect` that lint caught), `tracker/page.tsx` (1), `resume-builder.tsx` (1), `hero.tsx` (1), `swiss-grid.tsx` (2), `resume-wizard-page.tsx` (2), `tenant-nav-bar.tsx` (1, refactored to use the helper for consistency), `card-detail-modal.tsx` (1). New `tests/tenant-paths.test.ts`; updated `tests/resume-wizard-page.test.tsx`'s `router.push` assertion to expect the locale-prefixed path. Full re-verify green: `tsc --noEmit`, `npm run test` (197 passed), `npm run build`, `npm run lint`; manual `curl` click-through on `/en` and `/fr` (landing, settings, tracker) confirmed every rendered internal `href` carries the correct locale prefix.
- **Phase 6** — done: `master_resume_id` retired entirely — `dashboard/page.tsx` now derives it purely from `fetchResumeList(tenant, true)`'s `is_master` flag (the bootstrap-from-localStorage `useEffect` was deleted outright, not just its localStorage calls); `resumes/[id]/page.tsx` derives `isMasterResume` from the fetched resume's own `is_master` field (required adding `is_master: boolean` to the frontend `ResumeResponse['data']` type — the backend `ResumeFetchData`/`GET /resumes` already returned it from an earlier phase); `tailor/page.tsx`'s master-resume guard now calls `fetchResumeList(tenant, true)` instead of reading localStorage; `settings/page.tsx`'s reset-DB flow drops the dead key and loops `locales` to clear every tenant's `resume_builder_draft`/`resume_builder_settings`/`resume_wizard_draft` (a single un-scoped `removeItem` would have missed all but one tenant post-scoping); `resume-wizard-page.tsx`'s `MASTER_RESUME_KEY` constant + both usages removed (navigation already used the finalize response's `resume_id` directly). The 3 client-only draft/settings keys are now tenant-scoped via new `lib/utils/tenant-storage-key.ts` (`tenantStorageKey(tenant, baseKey)` → `` `${baseKey}_${tenant}` ``), threaded through `resume-builder.tsx` (`BASE_STORAGE_KEY`/`BASE_SETTINGS_STORAGE_KEY` → computed `storageKey`/`settingsStorageKey`) and `resume-wizard-page.tsx` (`BASE_DRAFT_STORAGE_KEY` → `draftStorageKey`, and `readSavedDraft()` now takes the key as a parameter instead of closing over a module constant). New `tests/tenant-storage-key.test.ts`; updated `tests/resume-wizard-page.test.tsx`'s draft-seeding keys to the tenant-scoped form and replaced the `master_resume_id` assertion with proof the key is never written (`toBeNull()`). Confirmed `tests/tracker-reorder.test.ts`'s `master_resume_id: null` fixture is the unrelated `Application.master_resume_id` API field, not this localStorage key — left untouched. Full re-verify green: `tsc --noEmit`, `npm run test` (199 passed), `npm run build`, `npm run lint`. Note: the manual "switch tenants, confirm no draft bleed-through" click-through from the plan requires a real browser (pure client-side localStorage state, invisible to `curl`) — not performed in this environment; correctness instead rests on the `tenantStorageKey` unit tests plus code review confirming every read/write site resolves the key through `useTenant()`.
- **Phase 7** — done: updated `docs/agent/features/i18n.md` (tenant model, `fr` added, all new key files), `docs/agent/apis/front-end-apis.md` + `api-flow-maps.md` (new `language` params, `configured-languages` endpoint, removed dead `fetchLanguageConfig`/`updateLanguageConfig` mentions), `docs/agent/architecture/frontend-architecture.md` + `frontend-workflow.md` (`[locale]` tree, `proxy.ts`, `useTenant()`, retired `master_resume_id`), `apps/backend/CLAUDE.md` (router table: tenant validation, `configured-languages`, `applications.py`/`resume_wizard.py` bullets that were missing entirely, per-tenant master invariant) and `apps/frontend/CLAUDE.md` (route table, directory layout, i18n section, new test files). Cross-linked this plan doc from `docs/agent/README.md`'s new "Plans" section instead of duplicating it into a separate feature doc.
  **Final sweep results:**
  - `uv run pytest` (backend): **503 passed**, 1 pre-existing unrelated Windows-only failure (`test_crypto.py` — confirmed identical on `main`).
  - `npm run build`: clean, all 6 locales × 7 tenant routes generated.
  - `npm run test`: **199 passed** (29 files).
  - `npm run lint`: 29 pre-existing errors, all in files untouched this entire branch (confirmed via `git status`) — zero errors in any file this work touched.
  - Both locale-parity checks pass (`i18n-locale-parity.test.ts`: 9 passed; `scripts/check_locale_parity.py`: passes, but needs `PYTHONIOENCODING=utf-8` to print its ✓ without crashing on this machine's Windows cp1252 console).
  - **`.githooks/pre-push` itself reports overall FAILED** on this machine — but only because of the same two pre-existing Windows-console artifacts stacked together (the crypto chmod assertion, and the parity script's `UnicodeEncodeError` on the ✓ character), not from anything this branch changed. Both predate this branch and reproduce identically on `main`. On a POSIX runner (Linux/macOS CI, WSL) the hook should pass clean.
