---
filed: 2026-05-12
tester: Tester agent (Sonnet)
commit_reviewed: 7393d60 (Coder), ded5e21 (gap-fill)
task: Phase 6 T7 — FreeListCompare with R10 inclusion-frequency bars
reviewer_upstream: PASS (docs/status/2026-05-12-phase6-T7-reviewer-verdict.md)
---

# Tester Verdict — Phase 6 T7

## TESTER VERDICT: PASS

---

## Gap analysis

### Coder's 36 existing tests (freelist-compare.test.tsx) — adequate coverage

| Area | Covered by Coder | Notes |
|---|---|---|
| AC #2 VizSwitcher tab enabled | Yes (3 tests) | aria-disabled absent, click fires, aria-selected |
| AC #4 terms + R10 bars render | Yes (5 tests) | items, order, bars, freq labels, R10 caption (toContain) |
| AC #5 hover cross-column | Yes (2 tests) | mouseover propagates; mouseout clears |
| AC #6 focus parity (same-column) | Yes (2 tests) | focusin adds class; focusout removes |
| AC #7 aria-label content | Yes (2 tests) | contains "Sutrop salience score", "collection runs"; exact format |
| AC #8 Case B no salience data | Yes (3 tests) | caption present, header present, R10 suppressed |
| AC #8 Case C no terms produced | Yes (3 tests) | caption present, no list items, forbidden-vocab clean |
| AC #9 shared-term star glyph | Yes (4 tests) | present, aria-label, absent when single model, absent when no overlap |
| AC #10 Case A no models | Yes (2 tests) | instruction text, no columns |
| AC #11 WCAG AA structure | Yes (4 tests) | h2.sr-only, root aria-label, h3 headers, ol list |
| Sort order (plan §2.4 tie-breaks) | Yes (1 test) | CSI desc → mean_position asc → item alpha |
| Column structure | Yes (2 tests) | count per selectedModels, term count line |
| Forbidden vocabulary (rendered) | Yes (2 tests) | rendered DOM + Case A text |
| VizSwitcher + permalink gap-fill | Yes (Coder's viz-switcher.test.tsx + permalink.test.ts) | freelist tab active, #freelist valid |

### Gaps identified and filled

Seven real gaps:

**GAP 1 — CDA SME §5.1 verbatim exact match** (regression guard)
The Coder used `.toContain()` on two halves of the §5.1 binding string. This
would not catch a reword like "that model's" vs "this model's". Gap-fill adds
`.toBe()` using `String.fromCharCode(39)` to construct a U+0027 apostrophe
(avoiding editor smart-quote substitution). Regex fallback accepts both
U+0027 and U+2019 as a belt-and-suspenders guard. 2 tests.

**GAP 2 — CDA SME §5.5 "no methodology narration" guard**
No test existed to assert the component does not contain `<details>`,
`<summary>`, info-icon buttons, or "we chose" / "we use" / "bootstrap" /
"smoothing" prose. This is the guard against future agents adding an
in-component methodology tooltip (explicitly forbidden by CDA SME §5.5
and plan §5). 7 tests.

**GAP 3 — UI/UX F-T7-A1 h2 is first child (not just present)**
The Coder confirmed the h2 exists and has the correct text, but did not
assert it is `firstElementChild` of the root div. F-T7-A1 binds this
explicitly. Also added: h2 precedes every h3 in DOM order (no h1→h3 skip
regression). 2 tests.

**GAP 4 — Static-source forbidden vocabulary scan (T0 gap-fill pattern)**
Following the `t0-gap-fill.test.ts` precedent, added source-file reads of
`FreeListCompare.tsx`, `FreeListColumn.tsx`, and `freelist-compare.css`
asserting no model-applied multi-word forbidden constructions. Single-word
entries ("worldview", "missing", etc.) are excluded from the source scan
because both component files contain compliance-documenting headers that
self-reference those words in a quoted context — false-positives, not
violations. The rendered-DOM tests in the Coder's file cover those words
at the output layer. 21 tests (7 phrases × 3 files).

**GAP 5 — F-T7-C1 CSS opacity source-level regression**
No test guarded against reverting the bar fill from opacity 0.8 back to
0.6. Added: CSS source contains "opacity: 0.8" and no non-comment line
carries "opacity" + "0.6". 2 tests.

**GAP 6 — Schema drift safety net**
No test verified that a `sutrop_csi` entry with unexpected extra properties
renders gracefully. Added render-without-crash + term-still-rendered checks.
1 test.

**GAP 7 — Cross-column highlight via focusin**
The Coder's cross-column test used `mouseover`. AC #6 requires focus parity.
Added: `focusin` on term in column A propagates `--hovered` to the same term
in column B; `focusout` clears both. 2 tests.

### Gaps not found (already covered or not applicable)

- CDA SME §5.2 aria-label regex: the Coder's exact `toBe` test for "alpha"
  with the full verbatim template is sufficient; all items use the same
  template. No gap.
- Case A verbatim string: `.toContain("Select one or more models...")` with
  the full sentence — adequate. No gap.
- Heading hierarchy at full-page level (App → DataExplorer → FreeListCompare):
  out of scope for a component-level test; the F-T7-A1 first-child assertion
  is the correct component-level anchor.

---

## Tests written

| File | Function | What it covers |
|---|---|---|
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `R10 caption text is exactly the CDA SME §5.1 binding string` | CDA SME §5.1 verbatim regression: exact string via String.fromCharCode(39) |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `R10 caption matches verbatim regardless of entity encoding` | §5.1 regex guard accepting both U+0027 and U+2019 apostrophes |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `renders no <details> element` | §5.5 no expandable methodology section |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `renders no <summary> element` | §5.5 no expandable methodology section |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `renders no info-icon button` | §5.5 no info-icon tooltip |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `rendered text contains no 'we chose' methodology prose` | §5.5 no on-page methodology narration |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `rendered text contains no 'we use' methodology prose` | §5.5 no on-page methodology narration |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `rendered text contains no 'bootstrap' methodology prose` | §5.5 no on-page methodology narration |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `rendered text contains no 'smoothing' methodology prose` | §5.5 no on-page methodology narration |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `sr-only h2 is the first child of the .freelist-compare root div` | F-T7-A1 first-child assertion |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `h2 precedes h3 in DOM order (no h1→h3 skip regression)` | F-T7-A1 heading hierarchy order |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `FreeListCompare.tsx does not contain forbidden phrase: "model believes"` | static-source scan (×7 phrases) |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `FreeListColumn.tsx does not contain forbidden phrase: "model believes"` | static-source scan (×7 phrases) |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `freelist-compare.css does not contain forbidden phrase: "model believes"` | static-source scan (×7 phrases) |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `freelist-compare.css contains 'opacity: 0.8' (not 0.6) for freq-fill` | F-T7-C1 contrast pass regression |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `freelist-compare.css does NOT contain 'opacity: 0.6' as live property` | F-T7-C1 contrast regression guard |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `renders without crashing when sutrop_csi entries have unexpected extra properties` | schema drift safety net |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `focusin on a term in column A highlights the same term in column B` | cross-column focus propagation (AC #6) |
| `/opt/lsb-agent/apps/dashboard/src/__tests__/t7-gap-fill.test.tsx` | `focusout on a term in column A clears the highlight in both columns` | cross-column focus clear (AC #6) |

(21 source-scan tests omitted from the table above for brevity; each covers one forbidden phrase × one source file.)

---

## Test run output

```
Test Files  30 passed (30)
      Tests  889 passed (889)
   Start at  15:43:02
   Duration  32.03s

npm run lint: clean (no ESLint errors or warnings)
npm run build: success — 81.19 KB JS (gzip), 4.32 KB CSS (gzip)
```

Before gap-fill: 852 tests (29 files)
After gap-fill: 889 tests (30 files)
New tests added: 37

---

## Coverage gaps remaining

None. All acceptance criteria from the plan §3 are covered. All five CDA SME
§5 binding notes have at least one dedicated test. Both UI/UX findings
(F-T7-A1, F-T7-C1) have regression tests. The "no methodology narration" guard
(§5.5) is now a live DOM test rather than just a Reviewer spot-check.

The one deliberate scope limit: the heading-hierarchy test is at the
FreeListCompare component level, not at the full App → DataExplorer →
FreeListCompare integration level. A full-page heading-order test would require
mocking the data-fetch layer and is T14 territory (heading hierarchy sweep).
The F-T7-A1 first-child assertion is the component-level anchor the
UI/UX verdict requires.

---

## Gap-fill commit

`ded5e21` — test(dashboard): T7 gap-fill — verbatim caption, §5.5 no-narration,
F-T7-A1 first-child, static-source scan, schema drift, focus cross-column, F-T7-C1 opacity

---

*End of Tester verdict for Phase 6 T7. Reviewer verdict was at commit `7393d60`; gap-fill at `ded5e21`.*

— Tester agent (Sonnet), 2026-05-12
