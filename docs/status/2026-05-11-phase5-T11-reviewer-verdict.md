# Reviewer Verdict — Phase 5 T11 (PNG export: canvas + tEXt metadata + watermark)

**Filed:** 2026-05-11
**Reviewer:** LSB Reviewer agent (Sonnet)
**Commits reviewed:** `727d9a9` (Coder), `fc83f01` (UI/UX corrections)
**Scope:** Union diff `294950c..fc83f01`
**Prerequisite verdicts:**
- Plan-level CDA SME PASS-WITH-NOTES: `docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`
- Plan-level UI/UX PASS-WITH-NOTES: `docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md`
- T11 per-commit UI/UX FAIL→PASS-WITH-NOTES: `docs/status/2026-05-11-phase5-T11-uiux-verdict.md`

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         N/A (no informants.jsonl change)
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A (no cdb_core/schemas.py change)
Check 6 — New deps sign-off:         N/A (no new dependencies)
Check 7 — Prompt versioning:         N/A (no prompt template changes)
Check 8 — Uncertainty in viz:        N/A (PNG export pipeline; no new visualization)
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check rationale

**Check 1 — No LLM imports in cdb_analyze/**
`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/` returns only the prohibition notice comment in `cdb_analyze/__init__.py`, not actual imports. T11 does not touch `packages/cdb_analyze/`. The dashboard-side `openai` matches in grep output are all model ID string literals in data fixtures and `modelShortName.ts` — not LLM client imports. PASS.

**Check 2 — Append-only JSONL**
`git diff 294950c..fc83f01 -- data/raw/informants.jsonl` returns empty. No data files touched. N/A.

**Check 3 — No secrets**
Full scan of all changed files (`png-export.ts`, `png-metadata.ts`, `DownloadBar.tsx`, `app.css`, three test files, `docs/status/2026-05-11-phase5-T11-uiux-verdict.md`) found no API keys, webhook URLs, passwords, or credential-shaped strings. `apps/dashboard/public/_headers` is unchanged — confirmed by `git diff 294950c..fc83f01 -- apps/dashboard/public/_headers` returning empty. PASS.

**Check 4 — Forbidden vocabulary**
Grep for `believes|thinks|worldview|cultural bias|within-model consensus|within-model cultural consensus|within-model eigenratio|within-model CCM|publishable|recognizes|interprets|perceives|comprehends` across all six new/modified source files returned zero matches. The verdict text in `docs/status/2026-05-11-phase5-T11-uiux-verdict.md` also contains no forbidden phrases. PASS.

**Check 5 — Schema + DATA_DICTIONARY**
`git diff 294950c..fc83f01 -- packages/cdb_core/cdb_core/schemas.py` returns empty. No Pydantic schema changes. R7 does not trigger. N/A.

**Check 6 — New deps sign-off**
`git diff 294950c..fc83f01 -- apps/dashboard/package.json apps/dashboard/package-lock.json` returns empty. No new npm or Python dependencies introduced. The PNG implementation is pure DOM/stdlib with no third-party PNG library (no UPNG.js, pngjs, or equivalent). N/A.

**Check 7 — Prompt versioning**
`git diff 294950c..fc83f01 -- packages/cdb_collect/prompts/` returns empty. No prompt template changes. N/A.

**Check 8 — Uncertainty in viz**
T11 is an export pipeline, not a new visualization. `png-export.ts` rasterizes the existing MDSPlot SVG (which already carries bootstrap ellipses per the §4.2.6 binding). No new visualization is introduced that could display a point estimate without uncertainty. N/A.

**Check 9 — Prerequisite verdicts**
T11 is a frontend PR. The required UI/UX gate verdict is present at `docs/status/2026-05-11-phase5-T11-uiux-verdict.md` (FAIL→PASS-WITH-NOTES). Both blocking notes (F-T11-1: focus-visible extension; F-T11-2: caption token) were applied in `fc83f01` alongside the verdict — verified in source. T11 does not introduce any methodology claims; CDA SME gate is not triggered at the per-commit level (plan-level CDA SME PASS-WITH-NOTES covers the phase). PASS.

---

## Specific T11 checks

| # | Check | Result |
|---|---|---|
| 1 | F5 binding: `canvas.width` and `canvas.height` set explicitly for both size variants | PASS — lines 129–130 of `png-export.ts`; CANVAS_DIMS lookup table at line 32 (`social: {1600, 900}`, `highres: {2000, 2000}`). Four hits on `canvas\.(width|height)\s*=` confirmed. |
| 2 | Watermark position as % of canvas: `0.02`, `0.012`, `0.03` constants present | PASS — `marginRight = canvasWidth * 0.02` (line 147), `marginBottom = canvasHeight * 0.02` (line 148), `fontSize = canvasWidth * 0.012` (line 152), `ctx.globalAlpha = 0.03` (line 157). |
| 3 | PNG tEXt 8 fields in `buildPngMetadata` | PASS — `Title`, `Author`, `Source`, `Software`, `Domain`, `Models`, `Analysis-Version`, `Generated-At` all present at `DownloadBar.tsx` lines 94–102. |
| 4 | CSP unchanged (`_headers` not modified) | PASS — `git diff 294950c..fc83f01 -- apps/dashboard/public/_headers` returned empty. |
| 5 | No HARDWARE.md committed | PASS — `git diff 294950c..fc83f01 -- HARDWARE.md` returned empty. |
| 6 | No new dependencies | PASS — `git diff 294950c..fc83f01 -- apps/dashboard/package.json apps/dashboard/package-lock.json` returned empty. |
| 7 | No data files touched | PASS — `git diff 294950c..fc83f01 -- data/` returned empty. |
| 8 | No third-party PNG library; CRC-32 implemented from scratch | PASS — `png-metadata.ts` contains a self-contained CCITT-32 CRC-32 implementation (0xEDB88320 polynomial) at lines 28–57. No UPNG.js, pngjs, or equivalent import present. |
| 9 | No LLM imports in `apps/dashboard/src/` | PASS — all `openai` matches in the dashboard are model ID string literals in data fixtures and the model-name registry; no LLM client library is imported. |
| 10 | Build + test + lint green | PASS — `eslint`: clean; `tsc -b && vite build`: 72.52 KB gzipped (under 400 KB §9 cap); `vitest run`: 528/528 pass (19 test files). |
| 11 | Bundle size cap ≤400 KB gzipped | PASS — 72.52 KB gzipped. |
| 12 | Watermark editorial restraint | PASS — text is `"cogstructurelab.com"`, monospace font, `ctx.globalAlpha = 0.03`. No marketing copy, no logo, no decorative elements. |
| 13 | Forbidden vocabulary scan across three new/modified source files | PASS — zero matches for `believes`, `thinks`, `worldview`, `recognizes`, `interprets`, `perceives`, `comprehends`. |
| 14 | gitleaks | N/A — `gitleaks` not installed in this environment. Visual scan of all changed files found no key-shaped strings, webhook URL patterns, or credential patterns. GitHub secret scanning is the second layer. |

---

## Build/test/lint output summary

```
eslint:          clean (no warnings, no errors)
tsc -b --noEmit: clean (no type errors)
vite build:      231.37 kB raw / 72.52 kB gzipped JS — PASS (cap: 400 KB)
vitest run:      528/528 tests pass (19 test files)
```

Test breakdown for T11-new test files:
- `png-export.test.ts`: 20 tests — canvas mock (jsdom-only, no real canvas), F5 dimension bindings, watermark font-size scaling, error paths, type contract
- `png-metadata.test.ts`: 16 tests — PNG signature preservation, chunk ordering (tEXt before IDAT, after IHDR, IEND last), CRC verification, round-trip kv recovery (single, multiple, full 8-field LSB set), empty kv passthrough, invalid input rejection
- `download-bar.test.tsx`: 19 tests (including 8 new T11 tests) — PNG button presence, ARIA labels, click dispatch to mocked `renderToPng` + `injectTextMetadata`, download anchor verification

All three test files use jsdom environment (`// @vitest-environment jsdom`). Canvas APIs are fully mocked via `vi.spyOn(document, "createElement")` interception; `renderToPng` and `injectTextMetadata` are mocked in `download-bar.test.tsx` via `vi.mock(...)`. No real API calls. Compliant with CLAUDE.md rule 9.

---

## Failures

None.

---

## Required before merge

None. Coder may merge.

---

## Carry-forward to T12–T13

- **CSP relaxation for embed iframe (T12):** `apps/dashboard/public/_headers` currently has `frame-ancestors 'none'`. T12's embed modal requires a `frame-ancestors` relaxation. Per the UI/UX verdict carry-forward, this must pass through the Reviewer and `SECURITY_AND_HARDENING.md` §3.1 review before T12 commits. The Reviewer must see a documented architectural decision in `ARCHITECTURE.md` §7 for any CSP weakening.
- **`--color-text-caption` pattern established:** Both `SourceAttribution.tsx` (T10) and `DownloadBar.tsx` `linkStyle` (T11) use `--color-text-caption` for 12px readable text. Any future 12px regular-weight text must use this token. Carry-forward to T12–T13 as a standing reminder.
- **T13 gate:** `MethodologySummary` prose requires CDA SME review in addition to UI/UX review. T11 introduces no methodology claims; the T13 gate remains as documented.

---

*T11 is PASS. Tester proceeds.*
