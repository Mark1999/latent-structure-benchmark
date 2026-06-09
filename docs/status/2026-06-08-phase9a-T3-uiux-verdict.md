# Phase 9a T3 — heatmap CI-crosses-null dashed border — UI/UX verdict (2026-06-09)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS / cite PASS / WCAG PASS (conditional on the
contrast-fallback rule below). DESIGN_SYSTEM.md §12.8 update REQUIRED (same commit).

## The binding contrast ruling (the load-bearing decision)
The dark `--color-text-primary` (#2c3e50) dashed stroke FAILS WCAG 1.4.11 (3:1 non-text) on the two
darkest cell backgrounds: seq-3 (#2e6da4) = 1.75:1, seq-4 (#1a3a5c) = 1.22:1 (stroke lighter than bg,
nearly invisible). seq-0/1/2 PASS (8.43 / 5.82 / 3.31:1). **Binding fallback — switch the dashed stroke
color on the EXISTING `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60` boundary (no new constant, no new token):**
```ts
const dashStroke = ciCrossesNull
  ? (sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
      ? 'var(--color-background)')   // white on seq-3/seq-4: 5.47 / 11.67:1 PASS
      : 'var(--color-text-primary)') // dark on seq-0/1/2: 8.43 / 5.82 / 3.31:1 PASS
  : 'var(--color-border)';           // non-crossing solid
```
Reference the tokens by `var(--...)` name (pitfall #15); no hardcoded hex. seq-2 (3.31:1, marginal)
PASSes; the numeric cell value + labels give redundancy.

## Other rulings
- **R10 pairing PASS:** numeric `<text>` + dashed `<rect>` + CI aria-label jointly cover all 4 cell
  classes (off-diagonal-with-CI / crossing / null-CI / diagonal).
- **`ciCrossesNull` strict inequalities** `ci_lo < 0.5 && 0.5 < ci_hi` — closed-boundary cases
  ([0.5,0.501], [0.499,0.5]) return false (test case 6 binding).
- **Caption** on ContentArea `chart-wrap__desc` only (NOT in the component — grep for an existing
  CI-crossing sentence first to avoid duplication). Per CDA SME the binding caption is the full
  two-sentence form: "Each cell shows how similarly two models organize this domain (1.00 = identical
  organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the
  no-shared-structure value of 0.50." Integrate the dashed-cell sentence + the "0.50 = no shared
  structure" meaning into the similarity description.
- **CVD PASS:** dashed is a stroke-STYLE discriminator (not color-only) + the aria text. Do NOT change
  CELL_SIZE or the dasharray without re-flagging.
- **No new tokens.**

## DESIGN_SYSTEM.md §12.8 patch (Coder applies, same commit)
Update the §12.8 heading to add "dashed-stroke contrast ruling added T3, 2026-06-09"; replace the
"CI-crosses-null treatment (deferred)" subsection with the RESTORED treatment: the dashed-border spec
(crossing → dashStroke / 1.5px / "3,2"; non-crossing → --color-border / 0.5px; diagonal never dashed),
the contrast table + the `dashStroke` binding rule (no new token), the caption text, and the 4 aria
templates. (tokens.css NOT modified.)

## Required before merge
1. Apply the `dashStroke` expression verbatim (token refs, not hex).
2. No caption duplication (grep ContentArea first).
3. `ciCrossesNull` strict `<` both sides (test case 6).
4. The R10 binding guard test (every off-diagonal aria-label has one of the 3 CI phrases) must run, not skipped.
5. The §12.8 patch committed in the same commit as the component change.
