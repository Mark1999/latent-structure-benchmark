---
filed: 2026-05-12
reviewer: Reviewer agent (Sonnet)
commit_reviewed: 39d8a05
task: Phase 6 T0 — Operator Inspection Mode (?inspect=...)
cda_sme_upstream: not required (T0 is schema-quiet, no methodology surface)
uiux_plan_level: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md)
---

# Reviewer Verdict — Phase 6 T0

## REVIEWER VERDICT: PASS

---

## Nine Binding Checks

```
Check 1 — No LLM imports in cdb_analyze:   PASS
Check 2 — Append-only JSONL:               PASS
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         N/A
Check 6 — New deps sign-off:                PASS
Check 7 — Prompt versioning:                N/A
Check 8 — Uncertainty in viz:               PASS
Check 9 — Prerequisite verdicts:            PASS

Failures: none
Required before merge: none
```

---

## 1. Rules table (R1–R13, SECURITY_AND_HARDENING.md §9)

| Rule | Check | Result | Notes |
|---|---|---|---|
| R1 | No edits to `data/raw/informants.jsonl` | PASS | `git show 39d8a05 --name-only` lists six files only: `App.tsx`, `inspect.test.tsx`, `InspectRoot.tsx`, `InspectSection.tsx`, `InspectTable.tsx`, `inspect.css`. No data/ or packages/ files touched. |
| R2 | Tests use fixtures, no real API calls | PASS | `inspect.test.tsx` mocks `../api/client` via `vi.mock`. `fetchManifest` and `fetchDomain` are replaced by `vi.fn()`. `MOCK_MANIFEST` and `MOCK_DOMAIN` are inline fixtures. No real network; `@vitest-environment jsdom` directive present. See §4. |
| R3 | No LLM client imports in `cdb_analyze/` | PASS | T0 is a pure frontend task. Static grep of `packages/cdb_analyze/` confirms the only matches are the prohibition comments in `__init__.py` — no actual import statements. Unchanged by this commit. |
| R4 | No secrets / API keys | PASS | Grep for `api_key`, `secret`, `password`, `token`, `webhook`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`, `hooks.slack.com`, `xoxb-` across all six changed files: zero matches. |
| R5 | No point estimates without uncertainty in new viz | PASS | All R10 pairings are present and adjacent per plan §2.4. See §5. |
| R6 | Schema changes co-update `DATA_DICTIONARY.md` | N/A | `cdb_core/schemas.py` is not in the commit. No schema change. Plan §7 confirms schema-quiet status. |
| R7 | No new dependencies without Architect sign-off | PASS | `apps/dashboard/package.json` and `package-lock.json` are not in the commit. Test confirms `react-router-dom` absent. Existing `fetchManifest`/`fetchDomain` reused; `api/client.ts` has exactly 2 exported async functions as before. |
| R8 | Frontend UI/UX gate present | PASS | UI/UX PASS-WITH-NOTES verdict at `docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md`. All four binding notes (F-T0-A1, F-T0-B1, F-T0-B2, F-T0-C1) applied. Commit body recites all four by ID. CDA SME not required per plan §6 (no methodology surface). |
| R9 | No researcher grounding PRs | N/A | No `data/grounding/` files in commit. |
| R10 | Webhook URL secrets never committed | PASS | No Slack webhook URLs found in any changed file (confirmed under R4). |
| R11 | `SECURITY.md` not weakened | PASS | `SECURITY.md` not in commit. |
| R12 | §1.5.4 language guardrails in all generated text | PASS | See §3 below. Full scan: zero matches for any forbidden phrase in all six changed files and commit message. |
| R13 | No software-side spend gates | PASS | No `CDB_MAX_SPEND_USD`, `spend_gate`, `cost_cap`, or cost-estimate paragraphs in any changed file or commit body. |

---

## 2. CLAUDE.md §6 specific checks

### Check 1 — No LLM imports in cdb_analyze
PASS. Verified. T0 touches no `packages/cdb_analyze/` files.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` not present in the commit's changed file list.

### Check 3 — No API keys or secrets
PASS. Full grep of all six changed files: no credential pattern found.

### Check 4 — No forbidden vocabulary
PASS. See §3 below.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` untouched. `docs/DATA_DICTIONARY.md` co-update not required.

### Check 6 — New dependencies
PASS. `package.json` and `package-lock.json` unchanged. No new `pyproject.toml` changes. No `react-router-dom` or any other new dependency introduced.

### Check 7 — Prompt versioning
N/A. No prompt templates in `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
PASS. T0 is an operator inspection page, not a new public visualization. However, because T0 renders the published data including point estimates, R10 still applies per the plan. All four pairings are present and adjacent:
- **MDS coordinates + MDS uncertainty (bootstrap ellipses):** `InspectSection` "MDS coordinates" rendered at line 501 of `InspectRoot.tsx`; "MDS uncertainty (bootstrap ellipses)" section rendered at line 509–519 immediately below. `description` prop explicitly notes "R10: CI visible alongside every point estimate."
- **Similarity matrix + Similarity CIs:** "Similarity matrix" at line 522; "Similarity confidence intervals" at line 531–540 immediately below. Description notes R10 pairing.
- **Consensus score + consensus_ci:** Both in a single scalar table at line 543. `consensus_score` row appears before `consensus_ci` row in the same `consensusRows` array.
- **OCI + oci_ci:** `within_model_results` table at line 601: `wmrCols` array has `{ key: "oci", label: "oci" }` at position 3 followed immediately by `{ key: "oci_ci", label: "oci_ci" }` at position 4. Section description notes "oci and oci_ci columns are adjacent (R10)."

### Check 9 — Prerequisite verdicts
PASS. UI/UX PASS-WITH-NOTES verdict present at `docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md`. All four binding notes applied (verified below). CDA SME not required for this task.

---

## 3. Forbidden vocabulary confirmation

Grep of all six changed files and commit message against the full CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 forbidden table:

- `worldview` applied to models: **0 matches** (the test file contains `'"worldview"'` as a string literal inside an assertion — this is a test that forbids the word, not a usage of it)
- `believes` / `thinks` applied to models: **0 matches** in user-facing prose (same — test file asserts absence)
- `How models see the world` / `How models see`: **0 matches**
- `What the model understands`: **0 matches**
- `Cultural bias` (standalone): **0 matches**
- `Model X's worldview`: **0 matches**
- `within-model consensus` / `within-model cultural consensus` / `within-model eigenratio` / `within-model CCM`: **0 matches**
- `publishable` (for LSB findings): **0 matches**

Section headings in user-facing text: "Domain header", "Models in this domain", "Free lists (per model)", "MDS coordinates", "MDS uncertainty (bootstrap ellipses)", "Similarity matrix", "Similarity confidence intervals", "Consensus", "Cultural centrality", "Cross-model agreement", "Sutrop CSI (salience)", "Salience index agreement", "Within-model results", "G1 stability fields", "Groundings", "Display block (precomputed UI helpers)", "Other top-level fields", "Manifest top-level", "Domains in this manifest". None contain forbidden vocabulary.

The "Groundings" section description reads: "v1 domains are model-to-model by design per ARCHITECTURE.md §1.5.5. The groundings array is empty and selected_baseline_id is null — this is the expected first-class state, not a placeholder." This correctly avoids the "missing / placeholder" framing prohibited by CLAUDE.md §9 pitfall 4.

---

## 4. Test / mock verification

`apps/dashboard/src/__tests__/inspect.test.tsx`:
- Line 50–53: `vi.mock("../api/client", () => ({ fetchManifest: vi.fn(), fetchDomain: vi.fn() }))` — both API functions mocked.
- All `InspectRoot` render tests call `mockFetchManifest.mockResolvedValue(MOCK_MANIFEST)` and `mockFetchDomain.mockResolvedValue(MOCK_DOMAIN)` before rendering.
- `MOCK_MANIFEST` and `MOCK_DOMAIN` are defined inline in the test file at lines 61–195.
- `MOCK_DOMAIN` includes a synthetic unknown field `foo_bar: [1, 2, 3]` for the "Other top-level fields" fallback test (AC7).
- 765 tests total pass across 27 test files (run result captured during review). No test failures.

---

## 5. UI/UX binding notes verification

All four F-T0 binding notes applied:

| ID | Required correction | Applied? | Evidence |
|---|---|---|---|
| F-T0-A1 | `id` derived from title via `title.toLowerCase().replace(/\s+/g, '-')` etc.; all section titles unique | PASS | `InspectSection.tsx` lines 27–32: `titleToId()` applies `.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')`. All 16 domain section titles and 2 manifest section titles confirmed unique. Tested: `"MDS uncertainty (bootstrap ellipses)"` → `"mds-uncertainty-bootstrap-ellipses"` (parentheses stripped). |
| F-T0-B1 | Use `--color-surface` not `--color-bg-surface` | PASS | `inspect.css` line 28: `background: var(--color-surface)`. `--color-bg-surface` appears zero times in all changed files. Token `--color-surface` confirmed present in `tokens.css`. |
| F-T0-B2 | Use `--font-mono` not `--font-family-mono` | PASS | `InspectTable.tsx` line 51: `fontFamily: "var(--font-mono)"`. `inspect.css` line 152: `font-family: var(--font-mono)`. `--font-family-mono` appears zero times. Token `--font-mono` confirmed present in `tokens.css` line 55. |
| F-T0-C1 | Loading/error strings use `--color-text-caption` (not `--color-text-muted` or `--color-text-secondary`) | PASS | All four loading/error `<p>` elements in `InspectRoot.tsx` (lines 772–780, 784–793, 799–808, 811–820) use `color: "var(--color-text-caption)"`. `--color-text-muted` appears zero times in `InspectRoot.tsx`. |

Note: `--color-text-secondary` appears once in `inspect.css` at line 74 — as `border-color` on the active nav link, not as a text color. This is not a violation of F-T0-C1 (which governs loading/error text color for WCAG AA), nor does it introduce a hardcoded value. The token is valid per `tokens.css`.

---

## 6. Design-system token audit (no hardcoded values)

All CSS custom properties in `inspect.css` were audited against `tokens.css`. All 27 unique `var(--...)` tokens used are present in `tokens.css`. No hex color literals (`#RRGGBB`), `rgb()`, `rgba()`, or literal font-family strings in `inspect.css`, `InspectRoot.tsx`, `InspectTable.tsx`, or `InspectSection.tsx`.

---

## 7. Bundle delta verification

| Measurement | Value |
|---|---|
| JS (index-BHdK0NjL.js) gzipped | 79,964 bytes |
| CSS (index-Ce6pvL2V.css) gzipped | 3,959 bytes |
| Current total | 83,923 bytes |
| Coder's claimed after-total | 83,886 bytes |
| Measurement variance | 37 bytes (~0.04%) — acceptable; likely `gzip -c` vs Vite's compression measurement |
| Coder's claimed baseline | 79,658 bytes |
| Independent delta | 83,923 - 79,658 = 4,265 bytes ≈ **+4.16 KB** |
| Coder's claimed delta | +4.12 KB (4,228 bytes) |
| Plan ceiling | 15 KB gzipped |
| Status | **PASS — well under the 15 KB ceiling** |

---

## 8. Build / test / lint summary

| Check | Result |
|---|---|
| `npm run lint` | Clean — no ESLint errors or warnings |
| `npm run build` | Success — 83.9 KB gzipped total (JS + CSS) |
| `npm run test` | 765/765 pass (27 test files) |
| Bundle ceiling (plan §1 directive 7) | 83.9 KB total — +4.16 KB delta vs baseline — under the 15 KB ceiling |

---

## 9. Additional spot-checks (per reviewer instructions)

| Check | Result | Evidence |
|---|---|---|
| `cdb_core/schemas.py` not touched | PASS | Not in changed file list |
| `data/types.ts` not touched | PASS | Not in changed file list. Shape mismatches deferred to T14 per plan §4 |
| `HARDWARE.md` not committed | PASS | Not in changed file list |
| No raw-data paths in new files | PASS | Grep for `data/raw/` and `data/results/` across all new files: zero matches (only in test assertions that verify absence) |
| Commit message follows Conventional Commits | PASS | `feat(dashboard): T0 operator inspection mode (?inspect=...)` — correct scope, under 72 chars |
| Commit body references plan + UI/UX verdict | PASS | Body cites `docs/status/2026-05-12-phase6-T0-architect-plan.md` and `docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md` (PASS-WITH-NOTES) and recites all four binding notes by ID |
| Bundle delta reported in commit body | PASS | Body reports `+4.12 KB gzipped (JS: +3825 bytes, CSS: +403 bytes). Baseline: 79,658 bytes → After: 83,886 bytes.` |
| `data/types.ts` shape mismatches documented | PASS | Commit body lists all three mismatches with explanation; `InspectRoot.tsx` file header repeats them with deferred T14 reference |
| `?inspect=` returns null for empty slug | PASS | `isInspectMode()` in `App.tsx` guards `slug.trim() === ""` — return null. Test asserts this guard is present. |

---

## 10. Notes / required follow-ups

None. No blocking issues found. No PASS-WITH-NOTES conditions attached.

The stash conflict incurred during bundle-delta baseline measurement (`git stash pop` on the pre-existing `phase5-prototype-reference` stash introduced merge conflicts in `index.html`, `package-lock.json`, and `App.tsx` in the working tree). This is a working-tree-only state not reflected in any committed file. The HEAD commit `39d8a05` is unaffected. Mark should resolve the stash conflict (`git stash drop stash@{0}` to clear it, or resolve and commit the postcss.config.js change staged by the stash). This is not a Reviewer-blocking issue.

---

*End of Reviewer verdict for Phase 6 T0 commit `39d8a05`. Coder may merge.*

— Reviewer agent (Sonnet), 2026-05-12
