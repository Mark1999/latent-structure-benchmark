# Reviewer Verdict: Phase 9a T10 — CentralityChart (second pass)

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent (second pass)
**Working tree at review:** working tree (staged + untracked; not yet committed)
**Task:** T10 — Dashboard: Cultural centrality display
**Prior verdict:** FAIL (first pass, same date) — three procedural items

---

## REVIEWER VERDICT: PASS

---

## Check Results

| Check | Result |
|---|---|
| Check 1 — No LLM imports in cdb_analyze | PASS |
| Check 2 — Append-only JSONL | PASS |
| Check 3 — No secrets | PASS |
| Check 4 — Forbidden vocabulary | PASS |
| Check 5 — Schema + DATA_DICTIONARY | N/A |
| Check 6 — New deps sign-off | PASS |
| Check 7 — Prompt versioning | N/A |
| Check 8 — Uncertainty in viz | PASS |
| Check 9 — Prerequisite verdicts | PASS |

---

## Resolution of First-Pass FAIL Items

### FAIL Item 1 — UI/UX verdict missing: RESOLVED

`/opt/lsb-agent/docs/status/2026-05-24-phase9a-T10-ui-ux-verdict.md` now exists.
Verdict: PASS-WITH-NOTES. Criteria 1 (OWID design fidelity): PASS. Criteria 2
(30-second journalist): PASS-WITH-NOTES. Criteria 3 (researcher reproduce-and-cite):
PASS. Criteria 4 (WCAG AA): PASS-WITH-NOTES.

### FAIL Item 2 — DESIGN_SYSTEM.md not updated: RESOLVED

`DESIGN_SYSTEM.md` is now at v0.5.0 (bumped from v0.4.10). The diff confirms:
- v0.5.0 changelog entry added at top, documenting the three new tokens and the
  gate verdicts.
- `CentralityChart.tsx`, `CentralityTable.tsx`, and `centrality-chart.css` added
  to §11 Component Inventory ("Phase 9a" section).
- Three tooltip-dark tokens (`--color-tooltip-dark-bg`, `--color-tooltip-dark-text`,
  `--color-tooltip-dark-divider`) added to §1.2 Color Palette with full rationale
  and WCAG contrast annotation.
- Footer updated to read "End of DESIGN_SYSTEM.md v0.5.0".
- Version header updated to v0.5.0.
- Test files (t6, t8, t11, t12) updated to match v0.5.0 assertions.

### FAIL Item 3 — Hardcoded rgba(255,255,255,0.15) in centrality-chart.css: RESOLVED

`/opt/lsb-agent/apps/dashboard/src/styles/centrality-chart.css` line 142 now reads
`border-top: 1px solid var(--color-tooltip-dark-divider)`.
No hardcoded rgba values remain in the file.
The token is defined in `tokens.css` and documented in `DESIGN_SYSTEM.md` §1.2.

---

## Check Details

### Check 1 — No LLM imports in cdb_analyze: PASS

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|
google.generativeai" packages/cdb_analyze/` returns only the guard docstring comment
in `packages/cdb_analyze/cdb_analyze/__init__.py` — not an import statement.
T10 introduces no Python file changes. No actual LLM client imports found.

### Check 2 — Append-only JSONL: PASS

`data/raw/informants.jsonl` is not in the working tree changes. `git diff HEAD --
data/raw/informants.jsonl` returns zero lines.

### Check 3 — No secrets: PASS

All changed and new files scanned:
- `DESIGN_SYSTEM.md` — no credentials, no webhook URLs, no API keys.
- `apps/dashboard/src/styles/tokens.css` — CSS custom properties only.
- `apps/dashboard/src/styles/centrality-chart.css` — CSS rules using only `var(--...)`.
- `apps/dashboard/src/components/CentralityChart.tsx` — no credentials.
- `apps/dashboard/src/components/CentralityTable.tsx` — no credentials.
- `apps/dashboard/src/copy/screen_reader_summaries.ts` — string templates only.
- `apps/dashboard/src/__tests__/t10-centrality-chart.test.tsx` — fixture data only.
- Modified test files (t6, t8, t11, t12) — version string assertions only.
- Modified component files (VizSwitcher, DataExplorer, DownloadBar, permalink) — tab
  type widening only.

### Check 4 — Forbidden vocabulary: PASS

All user-facing strings and documentation text in changed files scanned for the
CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden vocabulary tables.

`CentralityChart.tsx`:
- `CENTRALITY_TOOLTIP_EXPLANATION` (line 100-101): verbatim CDA SME M8 approved text.
  Contains "categorical structure", "dominant pattern", "differently" — all approved.
  Does not contain: "worldview", "believes", "thinks", "competence", "accuracy",
  "correctness", "cultural bias", "within-model consensus".
- Caption text (line 291-292): "Higher scores indicate closer alignment with the
  group's dominant categorical pattern." — approved phrasing.
- Aria-label (line 270-271): "Ranked bar chart of cultural centrality scores" — clean.
- "(negative centrality)" SVG label: describes the measurement state, not a quality
  judgment. Clean.

`CentralityTable.tsx`:
- `CENTRALITY_TABLE_CAPTION` template: "Cultural centrality scores... Higher scores
  indicate closer alignment with the group's dominant categorical pattern." — approved.
- Column headers use "Centrality score", "Notes" — clean.

`centralityScreenReaderSummary` (screen_reader_summaries.ts):
- Sentence 1: "higher scores indicate closer alignment with the group's dominant
  categorical pattern" — approved.
- Sentence 2: model names + numeric scores only.
- Sentence 3: "Bootstrap confidence intervals" — neutral technical description.

`DESIGN_SYSTEM.md` v0.5.0 changelog and §11 additions:
- Descriptive copy only. No model-behavior framing. Clean.

Comments in CentralityChart.tsx and CentralityTable.tsx list "worldview", "believes"
as items in a forbidden-vocabulary enumeration (the guard docstring). These are
metadata about the prohibition, not user-facing text. Per CLAUDE.md §7 interpretation
guidance, the rule is "about how LSB talks about its subjects" — docstring vocabulary
guards are exempt.

AC7 test in `t10-centrality-chart.test.tsx` enumerates forbidden strings in a FORBIDDEN
array — same exemption applies; these are test assertions, not generated text.

### Check 5 — Schema + DATA_DICTIONARY: N/A

No changes to `cdb_core/schemas.py`. T10 accesses `cultural_centrality_scores` via
cast-through-unknown pattern — the field exists in the published JSON output; no new
Pydantic schema field is introduced in this PR.

### Check 6 — New deps sign-off: PASS

`apps/dashboard/package.json` is not in the changed files. `git diff HEAD --
apps/dashboard/package.json` returns zero lines. No new npm or Python dependencies
introduced.

### Check 7 — Prompt versioning: N/A

No changes to `packages/cdb_collect/prompts/`. T10 is a frontend-only change.

### Check 8 — Uncertainty in viz: PASS

`CentralityChart.tsx` implements R10 compliance explicitly (lines 22-25 in file header):

When CI data is present (`hasCiData = true`):
- Error bars rendered per bar: horizontal CI line + left and right 6px caps, model
  color, 1.5px stroke, round linecap (lines 417-449 in CentralityChart.tsx).
- Score label includes `[lo–hi]` CI range notation (line 361-363).
- Tooltip shows "95% CI: lo–hi" (lines 524-531).

When CI data is absent (`hasCiData = false`):
- `ScreenReaderSummary` Sentence 3: "(Bootstrap CIs not yet computed — bars show
  point estimates only.)" — explicit acknowledgment of absent uncertainty.
- Tooltip: "Bootstrap CIs pending" — explicit acknowledgment.

This is not a bare point estimate. The component is aware of the absence of CI data
and communicates it to all users (sighted, screen-reader). ARCHITECTURE.md §4.5 /
CLAUDE.md §6 rule 11 satisfied.

### Check 9 — Prerequisite verdicts: PASS

**CDA SME:** `/opt/lsb-agent/docs/status/2026-05-24-phase9a-cda-sme-verdict.md`
Verdict: PASS-WITH-NOTES. T10-relevant binding note M8 applied correctly:
- Tooltip uses verbatim M8 text (confirmed above in Check 4).
- Axis label "Cultural centrality score" — matches M8 point 4 acceptable form.
- Caption includes domain consensus type per M8 point 5 (`consensusPhrase` rendering
  at CentralityChart.tsx line 290-292).
- Error bars implemented per M8 binding note (and graceful-absent when CI absent).

CDA SME notes M1–M7 are not T10-scoped (they apply to T1–T9 analysis tasks not
in this PR). M8 is fully addressed.

**UI/UX:** `/opt/lsb-agent/docs/status/2026-05-24-phase9a-T10-ui-ux-verdict.md`
Verdict: PASS-WITH-NOTES. Notes N1 and N2 both addressed:

- N1 (30-second journalist — title, axis label, interpretive affordance):
  Axis label "Cultural centrality score" rendered at SVG bottom (CentralityChart.tsx
  line 482). Caption renders "Higher scores indicate closer alignment with the group's
  dominant categorical pattern." Aria-label provides chart title context. N1 addressed.

- N2 (WCAG AA on dark tooltip):
  `--color-tooltip-dark-text` = `var(--color-background)` = #ffffff on
  `--color-tooltip-dark-bg` = `var(--color-text-primary)` = #2c3e50.
  Contrast ratio: ~11.1:1, exceeds WCAG AAA. N2 addressed by design.

DESIGN_SYSTEM.md §11 "DESIGN_SYSTEM.md update required" checklist from UI/UX verdict:
- "Add CentralityChart to component inventory" — done (§11 Phase 9a section).
- "Add `--color-tooltip-dark-divider` token" — done (§1.2 plus two companion tokens).
- "Document dark tooltip exception with rationale" — done (§1.2 block comment, §11 entry).

All prerequisite verdicts present and all PASS-WITH-NOTES notes resolved.

---

## Failures

None.

---

*End of Reviewer verdict (second pass). Coder may merge.*
