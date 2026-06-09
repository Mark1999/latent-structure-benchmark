# Phase 9a T2 — render published generated_lede — UI/UX verdict (2026-06-09)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS / cite PASS / WCAG PASS-WITH-NOTES (one
required contrast fix). DESIGN_SYSTEM.md update REQUIRED (§21, v0.17.0).

## Required before merge (binding)
1. **WCAG contrast fix (bonus bug found):** `apps/dashboard/src/styles/app.css` `.chart-lede` color
   `var(--color-text-secondary)` (#7f8c8d, ~3.40:1 at 13px — FAILS AA) → `var(--color-text-caption)`
   (#6c757d, ~4.60:1 — PASS). `--color-text-caption` already exists; no new token. Pre-existing defect
   T2 brings into scope by promoting the lede to a primary finding surface.
2. **Render spec:** `<p className="chart-lede" aria-live="polite">{domain.generated_lede}</p>` — single
   continuous paragraph (do NOT split the 2-sentence lede / no different styling on the R1-b sentence;
   it is a first-class finding, not a footnote). No branching on `selectedModelIds`, no inline Smith's S
   computation. DROP the "Consensus baseline (all tested models):" prefix (the published lede
   self-identifies). KEEP `aria-live="polite"` (lede changes on domain switch).
3. **DESIGN_SYSTEM.md (same commit):** bump to **v0.17.0** + changelog; add **§21 ".chart-lede binding
   token spec"** (binds `.chart-lede` color to `--color-text-caption`, the single-`<p>` verbatim render
   spec, aria-live, no inline lede logic, the "--" note); fix the stale §12.9 SR-template boundary note
   ("`generated_lede` ... used only in ArticleHeader.tsx" → "rendered in ContentArea.tsx as the Focus-3
   chart lede strip (Phase 9a T2)").

## Decisions
- F3 (2-sentence treatment): single continuous `<p>`, no typographic split.
- F4 ("Consensus baseline" label): DROP, no replacement.
- F5 (aria-live): KEEP.
- F6: no new tokens.
- F7 ("--" clause separator in the published lede): renders verbatim (approved published copy; it is a
  double-hyphen, not a Unicode em dash, so the no-em-dash rule is not violated). A follow-up to
  `lede_v1.py` to swap "--" for a comma/parenthetical is OUT of T2 scope, non-blocking.

## Scope note
T2 touches ONLY the Focus-3 lede (ContentArea.tsx:199-220) + app.css `.chart-lede` color +
DESIGN_SYSTEM. The Focus-1 / Focus-2 lede strips (ContentArea.tsx:114, 119) are OUT of scope.
