# Frontend API Client

> API client layer for Resume Matcher frontend.

## Base Client (`lib/api/client.ts`)

```typescript
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const API_BASE = `${API_URL}/api/v1`;

export async function apiFetch(endpoint: string, options?: RequestInit);
export async function apiPost<T>(endpoint: string, body: T);
export async function apiPatch<T>(endpoint: string, body: T);
export async function apiPut<T>(endpoint: string, body: T);
export async function apiDelete(endpoint: string);
export function getUploadUrl(): string;
export function withTenant(endpoint: string, language: string): string; // appends ?language=xx (or merges with an existing query string)
```

Every language is its own tenant (see [i18n.md](../features/i18n.md)). List/create/upload endpoints require the tenant explicitly: `withTenant()` appends it as a query param for GET endpoints; POST bodies/multipart forms include `language` directly as a field.

## Resume Operations (`lib/api/resume.ts`)

```typescript
// Job descriptions (language = tenant; goes in the JSON body, not the query string)
uploadJobDescriptions(language: string, descriptions: string[], resumeId: string) → job_id

// Resume improvement (no language param — the backend resolves output_language
// from the loaded resume's own language column)
improveResume(resumeId: string, jobId: string) → ImprovedResult

// CRUD (language = tenant; fetchResume/fetchResumeList wrap their endpoint in withTenant())
fetchResume(language: string, resumeId: string) → ResumeResponse['data']   // 404 on cross-tenant mismatch
fetchResumeList(language: string, includeMaster?: boolean) → ResumeListItem[]
fetchConfiguredLanguages() → string[]   // NOT tenant-scoped — lists tenants with ≥1 resume, for the tenant switcher
updateResume(resumeId: string, data: ResumeData) → ResumeResponse['data']
deleteResume(resumeId: string) → void

// PDF (locale param is the tenant, threaded via useTenant() at call sites)
downloadResumePdf(resumeId: string, settings?: TemplateSettings, locale?: Locale) → Blob
downloadCoverLetterPdf(resumeId: string, pageSize?: string, locale?: Locale) → Blob

// Content updates
updateCoverLetter(resumeId: string, content: string) → void
updateOutreachMessage(resumeId: string, content: string) → void
```

## Resume Wizard (`lib/api/resume-wizard.ts`)

```typescript
postResumeWizardTurn(payload: ResumeWizardTurnRequest) → ResumeWizardTurnResponse
finalizeResumeWizard(state: ResumeWizardState, language: string) → ResumeWizardFinalizeResponse
createInitialResumeWizardState() → ResumeWizardState
```

Backend endpoints:

- `POST /api/v1/resume-wizard/turn` — one adaptive turn. `action` is `start | answer | skip | back | review`. `answer`/`skip` run one AI call that updates `resume_data`, returns the next `current_question`, `inferred_skills`, and an `is_complete` flag; `back`/`review`/`start` are deterministic (no LLM). The full `ResumeWizardState` round-trips in the request and response.
- `POST /api/v1/resume-wizard/finalize` — creates the master resume **for the given tenant** (`language`, required) from the draft (`processing_status: "ready"`), or `409` if that tenant already has a master.

The wizard is an AI-led, one-question-at-a-time flow that builds a general master resume; it does not require a job description and does not replace the upload parser. Question and content text are produced in the tenant's language (see [i18n.md](../features/i18n.md)); static UI chrome uses the `resumeWizard.*` i18n keys.

## Application Tracker (`lib/api/tracker.ts`)

```typescript
// Kanban board (7 status columns: saved | applied | no_response |
// response | interview | accepted | rejected). language = tenant, scopes the whole board.
listApplications(language: string) → ApplicationListResponse        // { columns: Record<status, Application[]> }
createApplication(payload: ManualApplicationCreate) → Application   // manual add from a pasted JD; payload.language required
getApplicationDetail(id: string) → ApplicationDetail               // embedded JD + applied resume (resume null if deleted)
updateApplication(id: string, payload: ApplicationUpdate) → Application   // status/position/notes/company/role/applied_at

// Bulk
bulkUpdateStatus(applicationIds: string[], status: ApplicationStatus) → ApplicationActionResponse
deleteApplication(id: string) → void
bulkDeleteApplications(applicationIds: string[]) → ApplicationActionResponse
```

## Config Operations (`lib/api/config.ts`)

```typescript
fetchLlmConfig() → LLMConfig
updateLlmConfig(config: LLMConfigUpdate) → LLMConfig
testLlmConnection() → LLMHealthCheck
fetchSystemStatus() → SystemStatus

// Per-provider API keys (encrypted server-side; switching the active
// provider no longer wipes another provider's key — responses always masked)
fetchApiKeyStatus() → ApiKeyStatusResponse           // { providers: [{ provider, configured, masked_key }] }
updateApiKeys(keys: ApiKeysUpdateRequest) → ApiKeysUpdateResponse
deleteApiKey(provider: ApiKeyProvider) → void
clearAllApiKeys() → void

// Feature flags
fetchFeatureConfig() → FeatureConfig
updateFeatureConfig(config: FeatureConfigUpdate) → FeatureConfig
```

> `fetchLanguageConfig`/`updateLanguageConfig` (`GET`/`PUT /config/language`) were removed from the frontend client — content language is no longer independently settable, it's the tenant (see [i18n.md](../features/i18n.md)). The backend endpoint itself is untouched (vestigial).

> `updateLlmApiKey` (`PUT /config/llm-api-key`) no longer persists a key — keys are managed per-provider via the encrypted `/config/api-keys` endpoints above.

## Provider Info

```typescript
export const PROVIDER_INFO = {
  openai: { name: 'OpenAI', defaultModel: 'gpt-5-nano-2025-08-07', requiresKey: true },
  anthropic: { name: 'Anthropic', defaultModel: 'claude-haiku-4-5-20251001', requiresKey: true },
  openrouter: { name: 'OpenRouter', defaultModel: 'deepseek/deepseek-chat', requiresKey: true },
  gemini: { name: 'Google Gemini', defaultModel: 'gemini-3-flash-preview', requiresKey: true },
  deepseek: { name: 'DeepSeek', defaultModel: 'deepseek-chat', requiresKey: true },
  ollama: { name: 'Ollama (Local)', defaultModel: 'gemma3:4b', requiresKey: false },
};
```

## Usage

```typescript
import { fetchResume, API_BASE, PROVIDER_INFO } from '@/lib/api';
```
