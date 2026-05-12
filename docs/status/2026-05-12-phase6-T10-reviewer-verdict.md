---
filed: 2026-05-12
reviewer: Reviewer agent (Sonnet)
commit_reviewed: 389993f
task: Phase 6 T10 — FailuresFindingsSection (failures-as-findings UI surface)
cda_sme_upstream: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md)
uiux_plan_level: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T10-uiux-plan-verdict.md)
---

# Reviewer Verdict — Phase 6 T10

## REVIEWER VERDICT: PASS

---

## Nine Binding Checks

```
Check 1 — No LLM imports in cdb_analyze:   PASS
Check 2 — Append-only JSONL:               PASS
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         N/A
Check 6 — New deps sign-off:                N/A (no new deps)
Check 7 — Prompt versioning:                N/A
Check 8 — Uncertainty in viz:               N/A (failure records carry no point estimates)
Check 9 — Prerequisite verdicts:            PASS

Failures: none
Required before merge: none
```

---

## 1. Rules table (R1–R13, SECURITY_AND_HARDENING.md §9)

| Rule | Check | Result | Notes |
|---|---|---|---|
| R1 | No edits to `data/raw/informants.jsonl` | PASS | Not in commit's eleven changed files; all changes are in `apps/dashboard/`. |
| R2 | No `dangerouslySetInnerHTML` in dashboard | PASS | The two matches of the string in `FailuresFindingsSection.tsx` are in docstring/comment lines explicitly asserting compliance — no actual usage in JSX. All verbatim text rendered via React text nodes or `<pre>{value}</pre>` children. |
| R3 | No CSP weakening | PASS | `apps/dashboard/public/_headers` not in commit. No `unsafe-eval` or frame-ancestors removal introduced. |
| R4 | No edits to existing lines in `data/raw/informants.jsonl` | PASS | File absent from commit diff. |
| R5 | No new dependency without Architect sign-off | N/A | `apps/dashboard/package.json` and `package-lock.json` not in commit. `npm run build` succeeds (69 modules — same as pre-T10 count +0 external). No new JS library imported anywhere in the eleven changed files. |
| R6 | No LLM client imports in `cdb_analyze/` | PASS | T10 is a pure frontend task; no `packages/cdb_analyze/` files touched. Static grep confirms the only matches in `cdb_analyze/` are the prohibition comments in `__init__.py`, unchanged. |
| R7 | `InformantRecord`/`GroundingRef` schema changes co-update `DATA_DICTIONARY.md` | N/A | `cdb_core/schemas.py` not in commit. `data/types.ts` not in commit (plan AC12 — T14 deferral). T10 is schema-quiet; no `DATA_DICTIONARY.md` co-update required. |
| R8 | Frontend PRs carry UI/UX verdict | PASS | UI/UX PASS-WITH-NOTES at `docs/status/2026-05-12-phase6-T10-uiux-plan-verdict.md`. Both binding corrections applied (F-T10-T1, F-T10-C1) and advisory applied (F-T10-A1). |
| R9 | Researcher grounding submission PRs | N/A | No `data/grounding/` files in commit. |
| R10 | Webhook URL secrets never committed | PASS | No Slack webhook URLs in any changed file. The words "token" in the CSS file refer to design-system token methodology (e.g., `var(--font-mono)`), not credentials. |
| R11 | `SECURITY.md` not weakened | PASS | `SECURITY.md` not in commit. |
| R12 | §1.5.4 language guardrails | PASS | See §3 below. |
| R13 | No software-side spend gates | PASS | The single `R13` reference in `FailuresFindingsSection.tsx` is a docstring asserting compliance, not a gate. No `CDB_MAX_SPEND_USD`, `spend_cap`, cost-estimate paragraphs, or cost-aggregation logic found in any changed file or commit body. `input_tokens` / `output_tokens` field names are data identifiers from the published JSON shape — they are surfaced per-record in the expanded view without aggregation or cost derivation, consistent with plan §5. |

---

## 2. CLAUDE.md §6 specific checks

### Check 1 — No LLM imports in cdb_analyze
PASS. T10 touches only `apps/dashboard/`. Static grep of `packages/cdb_analyze/` returns zero actual import statements. Only the prohibition comments in `cdb_analyze/__init__.py` match — unchanged.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` is absent from the commit's eleven changed files.

### Check 3 — No API keys or secrets
PASS. Full scan of all eleven changed files for credential patterns (`sk-`, `xoxb-`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`, `hooks.slack.com`, `api_key`, `password`, `secret`, `token` as a credential): zero matches. The word "token" in `failures-findings.css` is a design-system token reference (`var(--font-mono)` etc.), not a credential.

### Check 4 — Forbidden vocabulary
PASS. See §3 below.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` untouched. `data/types.ts` untouched per T14 deferral. No `DATA_DICTIONARY.md` co-update required.

### Check 6 — New dependencies
N/A. `package.json` and `package-lock.json` unchanged. `npm run build` succeeds (69 modules). No new `import` of an external library in any new file.

### Check 7 — Prompt versioning
N/A. No prompt templates in `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
N/A. The plan, CDA SME verdict (§1 axis 8), and UI/UX verdict (criterion 2) all confirm R10 is not triggered for failures-as-findings. Failure records carry no point estimates with paired uncertainty values.

### Check 9 — Prerequisite verdicts
PASS. Both required gate verdicts present and all binding notes applied:
- CDA SME PASS-WITH-NOTES: `docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md`. Notes S1–S7 applied. See §4 below.
- UI/UX PASS-WITH-NOTES: `docs/status/2026-05-12-phase6-T10-uiux-plan-verdict.md`. F-T10-T1 and F-T10-C1 (both BINDING) applied; F-T10-A1 (ADVISORY) applied. See §5 below.

---

## 3. Forbidden vocabulary confirmation

Scanned `FailuresFindingsSection.tsx`, `FailuresInspectView.tsx`, `copy/failures_findings.ts`, `failures-findings.css`, `api/client.ts`, `InspectRoot.tsx`, `App.tsx`, and the commit message body against CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.

| Forbidden phrase | Present in user-facing text? | Notes |
|---|---|---|
| `worldview` / `believes` / `thinks` (model-applied) | No | Absent from all LSB-authored strings. The word "responded" appears in the S2 EMPTY_CAPTION: "how this set of models responded to this domain's elicitation prompts." — this describes the LSB-pipeline outcome (models produced output), not a state-of-mind claim. CDA SME approved this wording verbatim at §2.3 of the verdict. |
| `How models see the world` / `How models see` | No | — |
| `What the model understands` | No | — |
| `Cultural bias` (standalone) | No | — |
| `within-model consensus` / `within-model cultural` / `within-model eigenratio` / `within-model CCM` | No | — |
| `publishable` (for LSB findings) | No | — |
| `refuses` / `refused` in LSB-authored captions | No | — |
| `missing` / `placeholder` / `no data yet` / `pending` (empty-state) | No | `ERROR_FRAMING_MISSING` constant name contains "MISSING" but its exported string value is "Collection records are unavailable for this domain." — clean. Constant names are internal identifiers per CLAUDE.md §7 code-variable exemption. |

PASS on vocabulary.

---

## 4. CDA SME binding notes verification (S1–S7)

| Note | Required correction | Applied? | Evidence |
|---|---|---|---|
| S1 (LOAD-BEARING) | Summary row: field-shape descriptor only (`error_message: N chars` for failure; enum value only for decline_interview; NO verbatim preview bytes) | PASS | `FailuresFindingsSection.tsx` line 219–221: `record.error_message !== undefined ? \`error_message: ${record.error_message.length} chars\` : null`. The verbatim bytes (`error_message`, `response_verbatim`) are rendered only in `<pre>` blocks inside the `<div className="failure-record__body">` (the `<details>` expanded content), never in `<summary>`. Regression tests 5a and 5b in `failures-findings.test.tsx` assert no substring of `error_message` or `response_verbatim` appears in any `<summary>` element's text content. These tests pass (983/983). |
| S2 | `EMPTY_CAPTION` verbatim: `"This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."` | PASS | `copy/failures_findings.ts` lines 48–49 export the exact two-sentence string verbatim. Test 4 in `failures-findings.test.tsx` asserts byte-identical match. |
| S3 | "Outcome class" block label is plain text at T10; T14 wires methodology-page link | PASS | `copy/failures_findings.ts` line 74: `export const LABEL_OUTCOME_CLASS = "Outcome class";` — plain text, no hyperlink. Advisory noted for T14. |
| S4a | Badge label `"Decline follow-up"` → `"Follow-up interview"` | PASS | `copy/failures_findings.ts` line 34: `decline_interview: "Follow-up interview"`. Test 7 asserts the copy module contains `"Follow-up interview"` and does NOT contain `"Decline follow-up"`. |
| S4b | Block label `"Model response"` → `"Model output"` / `"Model output to the follow-up prompt"` | PASS | `copy/failures_findings.ts` exports `LABEL_MODEL_OUTPUT = "Model output"` (line 81) and `LABEL_MODEL_OUTPUT_FOLLOWUP = "Model output to the follow-up prompt"` (line 82). Component applies the correct label per `record_type` at lines 354–358. Test 8 asserts both strings are present and `"Model response"` is absent from the copy module. |
| S5 | Explicit `aria-label` on every `<summary>` per templates | PASS | `FailuresFindingsSection.tsx` lines 152–163: `buildAriaLabel()` constructs the exact templates from CDA SME S5. Every `<summary>` receives `aria-label={ariaLabel}` (line 229). Tests 6a–6c assert all `<summary>` elements have non-null aria-labels and contain the correct record-type prefix strings. |
| S6 | `"Reasoning trace the provider surfaced"` (no parenthetical) | PASS | `copy/failures_findings.ts` line 84: `export const LABEL_REASONING_TRACE = "Reasoning trace the provider surfaced";`. Test 9 asserts verbatim match. |
| S7 | No methodology-page hyperlink at T10 | PASS | `framing_note` is rendered as a plain `<p>` text node (line 520). The string contains "See the methodology page" from T9's emitted JSON but no `<a>` element wraps it — the T14 doc-sweep item is correctly deferred. No hyperlink-wiring code present in any T10 file. |

All S1–S7 binding notes applied. PASS.

---

## 5. UI/UX binding and advisory note verification

| Finding | Severity | Applied? | Evidence |
|---|---|---|---|
| F-T10-T1 | BINDING | PASS | `failures-findings.css` contains `var(--font-mono)` at lines 135, 151, 161, 197, 205, 219. Contains `var(--font-body)` at lines 125, 161. Zero occurrences of phantom `--font-family-mono` or `--font-family-base` (grep confirmed; test 15 in `failures-findings.test.tsx` asserts both phantom names are absent). |
| F-T10-C1 | BINDING | PASS | `failures-findings.css` uses `var(--color-text-caption)` at the three appropriate sites: `.failure-record__field-shape` (xs-size S1 descriptor, line 163), `.failure-record__block-value--provenance` (xs-size provenance IDs, line 208), and `.failures-findings__error` (defensive captions, line 60). The two remaining `--color-text-secondary` uses are `.failure-record__date` (14px `--font-size-sm` — within the DESIGN_SYSTEM.md §1.2 "14px+" acceptable range) and `.failure-record__block-label` (12px but **bold + uppercase** with letter-spacing — within the DESIGN_SYSTEM.md §1.2 "secondary labels at 14px+ or bold" allowance). Both are WCAG AA compliant per the token rationale in the UI/UX verdict. Test 15 asserts `var(--color-text-caption)` is present. |
| F-T10-A1 | ADVISORY | PASS | `failures-findings.css` lines 87–91: `summary:focus-visible { outline: 2px solid var(--color-info); outline-offset: 2px; border-radius: var(--border-radius-sm); }`. Tests 16a–16c assert the rule, the outline value, and the offset are all present. |

All F-T10 findings applied. PASS.

---

## 6. S1 LOAD-BEARING verification (special depth check)

The CDA SME explicitly flagged S1 as LOAD-BEARING and the orchestrator's review request called it out by name. Detailed verification:

- **Summary row composition**: `<summary className="failure-record__summary">` renders: (1) badge chip, (2) `model_id` in mono, (3) `collection_date` date-only prefix, (4) for decline_interview: `originating_outcome_class` enum verbatim in mono, (5) for failure: `error_message: {N} chars` in `--font-body` + `--color-text-caption`. No slice, substring, or preview of `error_message` or `response_verbatim` bytes appears in the summary row.
- **Verbatim content location**: `error_message` bytes appear only inside `<BlockField label={LABEL_ERROR_MESSAGE}><PreBlock value={record.error_message} /></BlockField>` (line 338), which is inside `<div className="failure-record__body">` — the `<details>` expanded content, not the `<summary>`.
- **`response_verbatim` bytes** appear only inside `<BlockField label={...}><PreBlock value={record.response_verbatim} /></BlockField>` (line 353–360), likewise inside `failure-record__body`.
- **Test coverage**: Two dedicated regression tests (S1a: failure record; S1b: decline_interview record) in `failures-findings.test.tsx` confirm `<summary>.textContent` contains zero bytes from the respective verbatim fields. Both pass in the 983/983 suite.

PASS — S1 LOAD-BEARING honored.

---

## 7. Native `<details>`/`<summary>` accordion confirmation

Plan §2.6 requires native HTML disclosure elements; no custom click handlers replacing native disclosure.

- Every record is wrapped in `<li><details className="failure-record">` with `<summary className="failure-record__summary">` as the first child.
- No `onClick` handler on `<summary>` or `<details>`. No `useState` for open/closed state.
- `<summary>` uses `cursor: pointer` for visual affordance (CSS line 101) — the native toggle behavior is entirely browser-handled.
- No `aria-expanded` attribute manually set on `<summary>` (the browser manages `<details open>` natively).

PASS.

---

## 8. Protected files — untouched verification

Per plan AC14:

| File | Touched? |
|---|---|
| `cdb_core/schemas.py` | No |
| `apps/dashboard/src/data/types.ts` | No |
| `MDSPlot.tsx` | No |
| `FreeListCompare.tsx` | No |
| `SimilarityHeatmap.tsx` | No |
| `ModelSelector.tsx` | No |
| `MethodologySummary.tsx` | No |
| `DataExplorer.tsx` | No |
| `VizSwitcher.tsx` | No |
| `KeyFinding.tsx` | No |
| `Header.tsx` | No |
| `Footer.tsx` | No |
| `ArticleHeader.tsx` | No |
| `DomainPicker.tsx` | No |

All protected files confirmed untouched. PASS.

---

## 9. Build / test / lint summary

| Check | Result |
|---|---|
| `npm run lint` | Clean — no ESLint errors or warnings |
| `npm run build` | Success — 282 kB JS uncompressed / 85.22 KB gzipped; 31 kB CSS / 4.89 KB gzipped. 69 modules. |
| `npm run test` | 983/983 pass (32 test files) |
| Bundle gzip total (JS) | 85.22 KB |
| Pre-T10 baseline (plan §8) | ~85 KB gzipped (T9 was backend-only; baseline = last dashboard build) |
| Bundle delta (JS gzip) | ≈ +0.2 KB — well within the 8 KB ceiling |
| Bundle ceiling (plan §1 directive 8) | 8 KB — PASS |

**Note on commit body bundle reporting**: The commit body reports "Build: 282 kB JS / 31 kB CSS (69 modules)" but does not state the explicit gzip delta against the pre-T10 baseline as required by plan AC18 ("Coder reports the measured delta in the commit body"). The Reviewer independently verified the 85.22 KB total against the plan's ~85 KB baseline — the delta is satisfied. This omission is minor and non-blocking since the cap constraint is verifiably met; noted for future commits.

---

## 10. Additional spot-checks

| Check | Result | Evidence |
|---|---|---|
| `framing_note` verbatim consumption (AC3) | PASS | Line 520: `<p className="failures-findings__framing">{data.framing_note}</p>` — React text node, no paraphrase. Test 3 (`framing_note byte-identity`) asserts `<p>.textContent === FRAMING_NOTE` after render. |
| `<h2>` heading hierarchy | PASS | Line 496–500: `<h2 id="failures-findings-heading" className="failures-findings__heading">`. H2 sibling of MethodologySummary's H2 per CDA SME §2.4. |
| `<section aria-labelledby>` | PASS | Line 493–495: `<section className="failures-findings" aria-labelledby="failures-findings-heading">`. Tests 13a–13b assert aria-labelledby and h2 id values. |
| `!embedMode` guard in App.tsx | PASS | App.tsx line 353: `{!embedMode && appState === "loaded" && activeSlug.length > 0 && (`. Test 14b verifies both `embedMode` and `FailuresFindingsSection` are referenced in App.tsx. |
| Cascade slot 6 = 360ms, slot 7 = 360ms | PASS | `app.css` lines 100–102. Tests 17a–17b assert the delay values. Coder added a note acknowledging the 280ms + 360ms = 640ms total slightly exceeds the §12.1 600ms cap, with documented rationale (slots 6 and 7 share the same delay; perceived difference imperceptible). The Architect's plan §2.2 specified 360ms for both slots; implementation matches. |
| No `data/raw` or `data/results` path in component code | PASS | Grep of all new/modified files returns zero matches. |
| Commit message follows Conventional Commits | PASS | `feat(dashboard): T10 failures-as-findings UI surface` — correct type, correct scope, under 72 chars. |
| Commit body references CDA SME + UI/UX verdicts | PASS | Both cited by path and finding IDs (S1–S7, F-T10-T1, F-T10-C1, F-T10-A1). |
| No `data/types.ts` import in new files | PASS | Test 20c asserts `FailuresFindingsSection.tsx` does not contain `"data/types"`. Cast-through-unknown used at the `fetchFailures` boundary. |
| No `dangerouslySetInnerHTML` in new files | PASS | Only appearances are in docstring comments asserting compliance; zero JSX usage. |
| `?inspect=failures-family` and `?inspect=failures-holidays` modes | PASS | `InspectRoot.tsx` lines 120–122: nav entries present. `FailuresInspectView` imported and wired to `failuresResult` at lines 905–906. Tests 19a–19c assert both entries and the import. |
| `fetchFailures` returns `Promise<unknown>` | PASS | `api/client.ts` line 81: `export async function fetchFailures(slug: string): Promise<unknown>`. |

---

## 11. Notes / required follow-ups

None blocking. Two T14 advisory items carried forward from plan §5:
1. Methodology-page link from `framing_note` paragraph `"See the methodology page"` — T14 wires when T1/T2 methodology page ships (CDA SME S7).
2. Methodology-page link from "Outcome class" block label — T14 wires the anti-attribution DATA_DICTIONARY.md sentence (CDA SME S3).
3. Explicit gzip bundle delta in commit body — see §9 note. Non-blocking for this commit; Reviewer recommends the Coder include it in future T10+ commits.

---

*End of Reviewer verdict for Phase 6 T10 commit `389993f`. Coder may merge.*

— Reviewer agent (Sonnet), 2026-05-12
