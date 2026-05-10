# UI/UX Per-Commit Verdict — Phase 5 T6

**Filed:** 2026-05-10
**Reviewer:** UI/UX agent (Sonnet)
**Commit reviewed:** `f3b7b43` (T6 MDSPlot with R1-state rendering)
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** v0.4.1 (unchanged — no new visual decisions)
**Visual reference:** `docs/status/2026-05-10-phase5-T6-screenshots/{t6-mdsplot-fold-1,t6-mdsplot-fullpage}.png`

---

## VERDICT: PASS-WITH-NOTES

| Question | Result |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS-WITH-NOTES (F-T6-1 — non-blocking) |
| 3. Researcher reproduce-and-cite | PASS |
| 4. WCAG AA accessibility | PASS |

**DESIGN_SYSTEM.md update:** not required.

T6 is the most visually load-bearing component in Phase 5. Every binding implementation requirement in §3.3 + §3.3.5 was verified line-by-line against the source. All 21 binding checks PASS. The single PASS-WITH-NOTES finding is a data-pipeline issue (lede string content), not a component defect — the component faithfully renders the published lede verbatim.

T6 proceeds to Reviewer + Tester with no MDSPlot rework. F-T6-1 is carry-forward to the lede template generator in `cdb_publish/templates/lede_v1.py`.

---

## F-T6-1 — Lede em-dash vs. ASCII double-hyphen (data pipeline carry-forward)

**Issue:** The lede in `apps/dashboard/public/data/family.json` `generated_lede` field reads `"... sits relative to that consensus -- and which models diverge from it."` The `--` should be an em-dash (`—`).

**Root cause:** The lede template in `packages/cdb_publish/cdb_publish/templates/lede_v1.py` uses ASCII double-hyphen rather than U+2014 em-dash. The `generate_lede()` function passes the template through verbatim.

**Component behavior is correct:** `MDSPlot.tsx` and `KeyFinding.tsx` render the lede string verbatim from the JSON. This is the intended behavior; the components do not editorialize the lede content.

**Fix location:** `packages/cdb_publish/cdb_publish/templates/lede_v1.py`. Replace `--` with `—` (U+2014) in the affected pattern strings. The DESIGN_SYSTEM.md §3.3.5 item 6 binding for the all-deterministic case already uses U+2014 em-dash; the other patterns should match this discipline.

**Severity:** Non-blocking for T6. The lede remains comprehensible and quotable. Mark may schedule a `cdb_publish/templates/lede_v2.py` (per CLAUDE.md §6 R7 versioning discipline) at his discretion.

---

## Criterion 1 — OWID design fidelity (PASS)

**Verified line-by-line against DESIGN_SYSTEM.md §3.3 and §3.3.5:**

| Spec | Source | Status |
|---|---|---|
| §3.3 item 1 — grid at `--color-border` opacity 0.5 | `MDSPlot.tsx:503–533` | ✓ |
| §3.3 item 2 — axis labels with "— relative" qualifier | `MDSPlot.tsx:686, 699` | ✓ |
| §3.3 item 3 — ellipse 8% fill / 25% stroke (model color) | `MDSPlot.tsx:547–548` | ✓ |
| §3.3 item 4 — 10px diameter / white 2px stroke (R1-a) | `MDSPlot.tsx:96, 648–649` | ✓ |
| §3.3 item 5 — labels 12px Lato | `MDSPlot.tsx:665–666` | ✓ |
| §3.3.5 binding invariant 1 — no ellipse for R1-b/c | `MDSPlot.tsx:539` (single guard) | ✓ |
| §3.3.5 imp. req. 1 — R1-c is hollow triangle (△) | `MDSPlot.tsx:573, 585` | ✓ |
| §3.3.5 imp. req. 2 — R1-c stroke 3px (NOT 2px) | `MDSPlot.tsx:589` | ✓ |
| §3.3.5 imp. req. 3 — R1-b stroke 100% / fill 60% | `MDSPlot.tsx:620–621` | ✓ |
| §3.3.5 imp. req. 4 — legend 14px marker samples | `MDSPlot.tsx:303–332` | ✓ |
| §3.3.5 imp. req. 7 — no `3.0` numeric literal | grep — zero hits | ✓ |

The visual diff between `lsb-prototype-explorer.png` (prototype reference) and `t6-mdsplot-fullpage.png` (T6 rendered output) shows fidelity at or above the prototype level. The current implementation includes:
- All 11 family models with confidence ellipses (all R1-a per family.json)
- Distinct cluster structure visible (GPT-5.4 mini isolated; main cluster at right)
- Clean axis labeling with "— relative" footnote qualifier
- Three-state legend below the plot with rendered 14px samples
- Editorial spacing rhythm preserved

---

## Criterion 2 — 30-second journalist test (PASS-WITH-NOTES per F-T6-1)

**Lede comprehensibility:** The KeyFinding strip presents "Across 11 frontier models, family vocabulary is organized around a single shared categorical structure (Smith's S = 0.71, 95% CI [0.50, 0.91]). The map below shows where each model sits relative to that consensus -- and which models diverge from it." Quotable, declarative, self-contained. The `--` typographic issue (F-T6-1) does not impair the 30-second comprehension.

**MDSPlot legibility:** Cluster structure is clear at a glance. R1-b and R1-c are visually distinguishable by shape alone (filled vs. dashed circle vs. hollow triangle), preserving grayscale interpretability per §7.

---

## Criterion 3 — Researcher reproduce-and-cite (PASS)

**Tooltip content varies correctly by R1 state:**
- R1-a (`MDSPlot.tsx:261–284`): model short name, model_id (mono), OCI value with state badge, top-5 free-list terms.
- R1-b (`MDSPlot.tsx:242–258`): verbatim §3.3.5 R1-b row binding copy with computed OCI substituted; threshold display included.
- R1-c (`MDSPlot.tsx:226–239`): verbatim §3.3.5 imp. req. 5 binding copy.

**Schema identifiers absent from tooltip:** grep for `OCI sentinel`, `ConsensusType.DETERMINISTIC`, `r1_state` literals returns zero hits in user-facing strings. The TypeScript type names in code annotations are fine.

**Cite path intact:** Article header byline strip carries CC BY 4.0, Methodology, and Cite links per T4 + T5 verdicts. `MDSPlot` does not regress the cite path.

---

## Criterion 4 — WCAG AA accessibility (PASS)

**SVG `role="img"` and aria-label:**
- Line 487: `role="img"`.
- Line 434 computes the binding-format `aria-label`:

```
"MDS cognitive map of {n} frontier language models on the {domain} domain. {first sentence of generated_lede}."
```

For family: `"MDS cognitive map of 11 frontier language models on the family domain. Across 11 frontier models, family vocabulary is organized around a single shared categorical structure (Smith's S = 0.71, 95% CI [0.50, 0.91])."`

Screen reader users get the key finding without requiring a table toggle (which is Phase 6 per §12.6).

**3:1 contrast on R1-c stroke at 3px:** All 11 palette slots verified per DESIGN_SYSTEM.md §12.4. Slot 11 corrected to `#9a7d0a` (~3.96:1) per v0.4.1. Other slots: 3.1:1 to 7.2:1 — all exceed 3:1.

**Grayscale interpretability (§7):** Shape encoding distinguishes the three R1 states independently of color. Filled circle / dashed-stroke circle / hollow triangle. PASS.

**Color + shape together (§7):** Confirmed. No color-only encoding anywhere.

**Interactive element ARIA:** Point groups carry `aria-label` with R1-state context (e.g., `{shortName} — deterministic output`). Mouse handlers on `<g>` elements. Legend uses `role="list"` + `role="listitem"`. Grid and labels use `aria-hidden="true"`.

---

## Carry-forward bindings verified

| Binding | Source | Status |
|---|---|---|
| T4 §12.6 — SVG aria-label format | `MDSPlot.tsx:430–434` | ✓ |
| T4 §12.4 — sorted model_id → palette slot | `App.tsx:116–124` | ✓ |
| T4 v0.4.1 — slot 11 = #9a7d0a | `App.tsx:76` | ✓ |
| T5 F-T5-1 — no `:nth-child(6)+` in cascade | `App.tsx:250–285` (KF=1, MDS=2) | ✓ |

---

## Non-blocking observations for carry-forward

**F-T6-1 → cdb_publish data pipeline:** Em-dash typographic correction in `lede_v1.py` template strings. Per CLAUDE.md §6 R7, this should ship as `lede_v2.py`. Architect to schedule.

**F-T6-2 → T9:** When `DataExplorer.tsx` takes ownership of `modelColors` (§12.4 ownership note in `App.tsx:25`), the Coder must reproduce the sorted-model_id algorithm verbatim, not re-derive.

**F-T6-3 → Phase 6:** Zoom and pan interactions deferred per §3.2 v0.4.1 update ("D3 or React+SVG" with D3 migration target for Phase 6). T6 correctly omits these.

---

## Required before Reviewer passes T6

None for T6 component itself. F-T6-1 is data-pipeline carry-forward, not blocking. Reviewer + Tester proceed.

---

*End of T6 per-commit UI/UX verdict. Posted to `#lsb-ui-ux`. The most visually heavy task in Phase 5 lands clean.*
