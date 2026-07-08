# Frontend Workflow

> User flows and state management for Resume Matcher.

## Core User Flow

```
Dashboard → Upload Master Resume → Tailor for Job → View/Edit → Download PDF
```

Every page lives under `/[locale]/...` — the locale segment is the active **tenant** (see [i18n.md](../features/i18n.md)). Switching tenants via `components/tenant/tenant-nav-bar.tsx` navigates to that tenant's own dashboard; each tenant has its own master resume, tailored resumes, and tracker board.

## Pages

### 1. Dashboard (`/[locale]/dashboard`)
- **No master (for this tenant):** "Initialize Master Resume" card — this is also the onboarding screen for an unconfigured tenant
- **Has master:** "Master Resume" card + tailored tiles
- **Create:** "+" card opens `/[locale]/tailor`
- Auto-refreshes on window focus
- Master resume id is derived live from the tenant-scoped resume list each load — not cached

### 2. Resume Viewer (`/[locale]/resumes/[id]`)
- Read-only display at 250mm width
- Actions: Back, Edit, Download PDF, Delete
- Delete shows confirmation + success dialogs
- `isMasterResume` comes from the fetched resume's own `is_master` field

### 3. Tailor (`/[locale]/tailor`)
- Job description textarea (min 50 chars)
- Process: Upload JD (tagged with the tenant) → Improve → Redirect to viewer
- Redirects to the dashboard if the active tenant has no master resume yet

### 4. Builder (`/[locale]/builder`)
- **Left panel:** Editor (forms + formatting)
- **Right panel:** WYSIWYG preview
- **Tabs:** Resume | Cover Letter | Outreach
- Data priority: URL param → Context → localStorage (tenant-scoped key) → defaults

### 5. Tracker (`/[locale]/tracker`)
- 7-column Kanban board, scoped to the active tenant
- Manual add, bulk move/delete, drag-and-drop reorder

### 6. Settings (`/[locale]/settings`)
- System status (cached)
- LLM configuration (6 providers)
- UI language selector (global, not tenant-scoped)
- Last fetched indicator + manual refresh

## Pagination Rules

- Sections CAN span pages
- Individual items stay together
- Pages ≥50% full before break
- Headers never orphaned

## State Management

### localStorage
| Key | Scope | Purpose |
|-----|-------|---------|
| `resume_matcher_ui_language` | Global | UI language |
| `resume_builder_draft_${tenant}` | Per-tenant | Auto-saved form (via `tenantStorageKey()`) |
| `resume_builder_settings_${tenant}` | Per-tenant | Template prefs |
| `resume_wizard_draft_${tenant}` | Per-tenant | Wizard draft |

`master_resume_id` is retired — always derived live from the tenant-scoped resume list.

### StatusCache Context
- Initial fetch on app start
- 30-min auto-refresh
- Optimistic counter updates

## Delete Flow

1. Click Delete → Confirmation dialog
2. API: `DELETE /resumes/{id}`
3. If it was the master, `setHasMasterResume(false)` (StatusCache) — no localStorage to clear
4. Success dialog → Redirect to dashboard

## Section Management

| Action | Result |
|--------|--------|
| Rename | Click pencil icon |
| Reorder | Up/down arrows |
| Hide | Eye icon (hidden sections still editable) |
| Delete | Hides default, removes custom |
| Add | "Add Section" button |

## API Client

```typescript
import { fetchResume, API_BASE } from '@/lib/api';

// Resume operations — fetchResume/fetchResumeList/uploadJobDescriptions take
// language (the tenant) as a required first param
fetchResume, fetchResumeList, fetchConfiguredLanguages, updateResume, deleteResume
uploadJobDescriptions, improveResume, downloadResumePdf

// Config operations  
fetchLlmConfig, updateLlmConfig, testLlmConnection
```
