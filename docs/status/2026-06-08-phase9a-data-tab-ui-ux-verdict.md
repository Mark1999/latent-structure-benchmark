# Phase 9a — Data download tab — UI/UX verdict (2026-06-08)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS / cite PASS / WCAG PASS-WITH-NOTES.
DESIGN_SYSTEM.md update REQUIRED. **NOTE: numbering conflict with the failures UI/UX verdict which took
§19/v0.15.0 — the Data tab takes §20, v0.16.0** (renumber the UI/UX agent's "§19" to §20).

## Resolved visual questions (binding)
1. **Bare `<section>` blocks, no card chrome.** Mirror MethodologyPage. `.data-page*` rules appended to
   `app.css`; container `--max-prose-width` centered. `<main aria-label="Data download">`, `<h2>` per
   section (use `--font-size-xl` + `--color-text-primary`).
2. **Size warning = `role="note"` callout** (NOT bare inline), rendered BEFORE the tarball anchor:
   `.data-page__note` bg `--color-surface-note` (NEW semantic alias = same hex as --color-surface,
   #f8f9fa; add to tokens.css with the comment — do NOT let the Coder use --color-surface directly or a
   hex), border-left 4px `--color-warning`, --border-radius-sm, --space-3/--space-4 padding,
   --font-size-sm, **text `--color-text-primary`** (NOT secondary — secondary fails 4.5:1 on the tint),
   --line-height-body.
3. **Code blocks** (SHA256 + citation): `<pre><code className="data-page__code-block">` — bg
   `--color-surface`, --color-border, --border-radius-sm, --font-mono, --font-size-sm,
   --color-text-primary, overflow-x auto, white-space pre. Copy-button DEFERRED (confirmed).
4. **Section render order (binding, NOT the plan's A-H label order):** B (HF Get-the-data) → D (Cite) →
   A (header) → C (tarball+warning) → E (GitHub) → F (what's-in-bundle) → G (licenses) → H (provenance
   pointer). B+D first for the 30-sec-journalist + researcher tests.
5. **External-link contract (binding, every external `<a>`):** `target="_blank"` +
   `rel="noopener noreferrer"` + nested `<span className="sr-only">(opens <dest> in new tab)` +
   self-describing visible text. B2 anchor sr-only = "(starts 1.55 GB download in new tab)". Precedent
   ProvenanceFooter:96-101.

## DESIGN_SYSTEM.md §20 (v0.16.0) — Coder pastes
Add §20 "Data Page visual specification" + the `--color-surface-note` token (§1.2) capturing the above
(bare sections, role=note size warning + token, code-block token, section order B/D/A/C/E/F/G/H,
external-link a11y). Add DataPage.tsx to the §11 component inventory. (The full clause text is in the
UI/UX agent transcript; the bindings above are authoritative.)

## Required before merge
1. `--color-surface-note: #f8f9fa;` added to tokens.css (semantic alias, with the comment); the
   `.data-page__note` rule uses the alias, not --color-surface directly, not a hex.
2. Section render order B/D/A/C/E/F/G/H.
3. `.data-page__note` `role="note"` size warning, full token set, text `--color-text-primary`.
4. `.data-page__code-block` on SHA256 + citation `<pre>`.
5. Every external `<a>` satisfies the 4-part contract; B2 sr-only conveys size.
6. `<h2>` headings use --font-size-xl + --color-text-primary.
7. Vitest tests 9 + 10 (loop external anchors for target+rel; sr-only "opens") binding.
