# Phase 9a T1 — failures restore (top-level tab) — UI/UX verdict (2026-06-08)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS-WITH-NOTES / cite PASS / WCAG PASS-WITH-NOTES.
DESIGN_SYSTEM.md update REQUIRED (new **§19**, v0.15.0). Absorbs CDA SME M1-M4. Coder may proceed.

## Binding decisions (apply all)
- **N1 / nav tab label:** `"Collection records"` (CDA SME M1 Option A). Export
  `FAILURES_TAB_LABEL = "Collection records"` from `copy/failures_findings.ts`.
- **Nav order:** `[Explore] [Methodology] [Collection records] [Data]`. Extend `NavTab` to add
  `'collection-records'`; update `NavBar.tsx` activeTab/onTabChange; `aria-current` on the new tab.
- **Domain selector:** OWN state, defaults to `'family'` (NOT inherited from Explore). Label `"Domain"`
  (M3 ok). `<select id="failures-domain-select">` + `<label htmlFor="failures-domain-select">` (distinct
  id from the Sidebar's). Same 3 domain options.
- **Page heading:** `<h1>` (top-level for the tab region), text verbatim T10/M2
  `"Collection records and follow-up interviews"`.
- **Content order (binding):** `<h1>` → framing_note `<p>` (verbatim) → counts caption `<p>` (T10 §4
  template; OMIT when n_records=0) → records `<ol>` or empty-state `<p>`. No chart-lede / Smith's-S /
  SelectionBar / VizTabs (M4).
- **Badges (N3):** "Collection failure" → border+text `var(--color-error)` (10.23:1, PASS), bg
  `--color-background`, pill (xs/medium, --space-2, --border-radius-sm). "Follow-up interview" → border
  `--color-border`, text `--color-text-secondary`, same pill. **NO new tokens; no hex literals.**
- **`<details>`/`<summary>` (N4):** native, no role override; summary collapsed = badge + model_id
  `<code>` + date + (failure: error_type + "error_message: N chars") / (decline:
  "originating_outcome_class: <code>{enum}</code>") — NO verbatim bytes (T10 S1). Focus ring:
  `.failures-findings__summary:focus-visible { outline: 2px solid var(--color-info); outline-offset: 2px; }`.
- **`<pre>` (N5):** `.failures-findings__pre` font-mono / --font-size-xs / pre-wrap / break-word /
  overflow-y auto / **max-height 320px** / --color-surface bg / --color-border / --space-3 padding.
- **Empty state (food):** verbatim T10 §S2 caption (export `EMPTY_CAPTION`), no error/greyout/skeleton.
- **M4 chrome-isolation grep test (N7):** rendered tab text (excluding `<pre>` bytes) must not contain
  consensus / Smith's S / agree / believe / think / worldview / categoriz(without -pipeline). AC13.

## DESIGN_SYSTEM.md §19 (v0.15.0) — Coder pastes the clause
Add §19 "Collection records tab" capturing all the above (tab label/order/type, domain selector,
heading level, content order, badge tokens, details/summary + focus ring, `<pre>` container, empty
state, the new files, "no new tokens"). Full clause text is in this verdict's source (the UI/UX agent
transcript); the binding decisions above are the authoritative summary. **NOTE numbering conflict:** the
Data-tab UI/UX verdict also proposed §19/v0.15.0 — whichever task lands first takes §19/v0.15.0; the
second takes §20/v0.16.0. Failures should take §19 (this verdict).

## Carry-forward (T9/T10, unchanged)
framing_note verbatim byte-identity (AC5); outcome_class enum verbatim in `<code>`, no expansion (AC7);
block labels (Follow-up prompt LSB sent / Model output to the follow-up prompt / Reasoning trace /
Provenance); first-class loading/fetch-failed states; all CSS via tokens (pitfall #15).

## Out of scope
methodology-page link wiring (T14 carry-forward); cross-tab domain sync (Architect decision); mobile
(renders single-column naturally).
