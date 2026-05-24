# Reviewer Verdict: Phase 9a T6+T7 — TermMDSPlot + Dendrogram

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent (Sonnet)
**Tasks reviewed:** T6 (TermMDSPlot / TermMDSTable) and T7 (Dendrogram / DendrogramTable)
**Gate verdicts on file:**
- CDA SME: PASS-WITH-NOTES — `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`
- UI/UX: PASS-WITH-NOTES — `docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md`

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        PASS
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check findings

### Check 1 — No LLM imports in cdb_analyze/
PASS. The two matches found by grep in `packages/cdb_analyze/cdb_analyze/__init__.py` are comment/documentation strings only. No actual `import` or `from` statements for any LLM client library appear in `packages/cdb_analyze/`. The PR touches only `apps/dashboard/`.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` is not touched in this PR. Confirmed with `git diff`.

### Check 3 — No secrets
PASS. Scanned all changed files for API keys, webhook URL patterns, and credential strings. No matches found.

### Check 4 — Forbidden vocabulary
PASS. All occurrences of `worldview`, `believes`, `thinks`, `within-model consensus`, `within-model eigenratio`, `within-model CCM`, and `publishable` in the new files appear only in comment block headers that enumerate the forbidden vocabulary (e.g., "Forbidden vocabulary: no 'worldview'…"). Zero user-facing string violations. The description texts, SR summaries, tooltip copy, legend text, and component captions are clean.

Specific strings verified clean:
- TermMDSPlot description: "Where [domain] terms cluster in model output space…" — uses structural/output language, not cognition attribution.
- Dendrogram description: "How [domain] terms cluster hierarchically…" — structural framing per M7 binding.
- SR summaries in `screen_reader_summaries.ts`: all templates use "outputs pattern as", "categorical structure", or "how models organize" framing.
- No model is described as believing, thinking, seeing, or understanding anything.

M4a note in tooltip (`TermMDSPlot.tsx` line 130): `"Uncertainty reflects agreement across models, not within-model sampling variance."` — the comment labels this "CDA SME M4a binding verbatim" which is slightly inaccurate (the CDA SME exact phrase was "Term position confidence reflects…"), but the semantic content satisfies M4a's requirement. M4a's primary binding is on the methods page (a separate deliverable beyond this PR). The tooltip carries the required meaning. Not a FAIL.

M5a compliance: Dendrogram uses "bootstrap support (%)" throughout — in `DendrogramTable.tsx` column header (line 76), legend text (line 282 of `Dendrogram.tsx`), and tooltip copy (line 524). "AU p-value" does not appear anywhere. PASS.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `packages/cdb_core/schemas.py` is not modified in this PR.

### Check 6 — New dependencies sign-off
PASS. `apps/dashboard/package.json` and `pyproject.toml` are unchanged. No new npm or Python dependencies introduced.

### Check 7 — Prompt versioning
N/A. No prompt templates touched.

### Check 8 — Uncertainty in visualizations
PASS.

**T6 (TermMDSPlot):** When uncertainty data is present, confidence ellipses are shown on hover/focus by default with a "Show uncertainty" toggle to display all ellipses simultaneously. The tooltip always shows CI parameters (semi-major, semi-minor, rotation, bootstrap N) alongside the M4a explanatory note. The accessible table (TermMDSTable) displays "—" for missing CI columns. When uncertainty data is null for a given term (data not yet computed), the point renders without a special visual treatment. This differs from the MDSPlot's R1-b dashed-circle pattern but was reviewed and approved by the UI/UX agent's PASS-WITH-NOTES verdict, which is the prerequisite gate for this pattern. The UI/UX agent's explicit decisions cover the `uncertainty` null case via the toggle design. I accept this as satisfying R10 under the approved design.

**T7 (Dendrogram):** Bootstrap support uncertainty is expressed via dashed branches (opacity 0.6, `strokeDasharray="5 3"`) for BP < 70%, with numeric percentage annotations left of the node and full BP explanation in the tooltip. The legend explains dashed branches. The DENDROGRAM_SUPPORT_THRESHOLD constant (0.70) is correctly imported from `apps/dashboard/src/config/analysis.ts` rather than hardcoded. The accessible table includes a "Bootstrap support (%)" column with "—" for missing values.

### Check 9 — Prerequisite verdicts
PASS. Both required gate verdicts are present and on file:
- CDA SME PASS-WITH-NOTES: `docs/status/2026-05-24-phase9a-cda-sme-verdict.md` — all M-notes (M1–M8) were available before Coder implementation.
- UI/UX PASS-WITH-NOTES: `docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md` — key design decisions were binding on implementation.

All PASS-WITH-NOTES items from both gate verdicts verified addressed in the implementation:

CDA SME notes relevant to this PR:
- M4a: Tooltip carries between-model variance annotation. ADDRESSED.
- M5a: "bootstrap support (%)" labeling, dashed < 70% branches. ADDRESSED.

UI/UX notes verified implemented:
- Tab "Term Map" at index 1, fragment `#term-mds`. ADDRESSED.
- Tab "Cluster Tree" at index 2, fragment `#cluster-tree`. ADDRESSED.
- Cluster colors use `--color-cluster-1..8`, NOT model colors. ADDRESSED.
- Ellipses hover/focus-only default, "Show uncertainty" toggle. ADDRESSED.
- Label placement: greedy 8-compass, 12px, hidden at <768px. ADDRESSED.
- Cluster region labels: 24px, 20% opacity, show/hide toggle. ADDRESSED.
- POINT_RADIUS = 4. ADDRESSED.
- Dendrogram: left-to-right, SVG 800px wide, height = n_terms * 20 + margins. ADDRESSED.
- BP < 70%: dashed + numeric annotation. ADDRESSED.
- VizSwitcher: 8 tabs total, horizontal scroll at <1024px. ADDRESSED.
- ScreenReaderSummary + ReadAsTableToggle on both components. ADDRESSED.
- DESIGN_SYSTEM.md updated to v0.5.2 with cluster tokens and component inventory. ADDRESSED.

---

## Additional findings (non-blocking)

1. **CSS token consistency (rule 15):** All CSS custom properties referenced in `term-mds-plot.css` and `dendrogram.css` are defined in `tokens.css`. All `var(--color-cluster-N)` tokens referenced in `Dendrogram.tsx` inline styles exist in tokens.css. The hardcoded hex values in `TermMDSPlot.tsx`'s `CLUSTER_COLORS` array match the cluster token definitions in `tokens.css` exactly — this is the correct approach for SVG fill attributes where CSS custom properties are not reliably resolvable.

2. **M4a note wording:** The comment at `TermMDSPlot.tsx` line 127 says "CDA SME M4a binding verbatim" but the UNCERTAINTY_NOTE text ("Uncertainty reflects…") is not the exact CDA SME phrase ("Term position confidence reflects…"). The semantic meaning is correct. Consider correcting the comment to remove "verbatim" in a follow-up.

3. **Dendrogram `selectedModels` prop:** `Dendrogram.tsx` declares `selectedModels?: string[]` in its props interface but the prop is not used in the component body (the dendrogram renders all terms, not a model-filtered subset). This unused prop is harmless and may be forward-compatible scaffolding.

---

*End of verdict. Coder may merge. All nine checks pass.*
