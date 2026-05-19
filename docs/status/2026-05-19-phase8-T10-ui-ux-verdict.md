# Phase 8 T10 — UI/UX Verdict (plan review)

**Date:** 2026-05-19
**Task:** T10 — methodology page placeholder
**Verdict:** **PASS-WITH-NOTES**

## Scorecard (reduced scope per `feedback_ui_polish_scope.md`)

| Criterion | Status |
|---|---|
| OWID design fidelity | PASS |
| 30-second journalist test | PASS (N/A — placeholder) |
| Researcher cite path | PASS-WITH-NOTES (anchor durability) |
| WCAG AA accessibility | PASS-WITH-NOTES (skip-link + `aria-current`) |

**`DESIGN_SYSTEM.md` update required:** No.

## Findings

### Per-criterion

1. **OWID design fidelity.** Plan reuses `<Header>` + `<Footer>`; `<h1>` + short prose layout consistent with DESIGN_SYSTEM.md §2 long-form publication model. No invented visual decisions. PASS.
2. **30-second journalist test.** N/A — placeholder has no finding to quote. "In preparation" honest about state. PASS on reduced scope.
3. **Researcher cite path.** Single cite-path element is the GitHub link to `ARCHITECTURE.md §1.5`. **Heading-anchor approach is fragile** — GitHub auto-generates slugs from heading text; heading edits silently break the anchor (this has happened in changelog at least twice). Ruling: link to file root, no `#` suffix.
4. **WCAG AA.** Token colors already AA-compliant; `<h1>` unique on route; focus order natural. No regression. Pre-existing skip-link absence noted as follow-up but not a T10 blocker.

### Per-decision rulings

1. **GitHub anchor strategy:** use file root, no `#` anchor. See Required-before-merge item 1.
2. **T10.3 footnote refresh blocking T10.1/T10.2:** does not block. Footnote text is SME-gated copy; ship T10.1+T10.2 first, route T10.3 separately.
3. **"In preparation" vs alternatives:** confirmed correct. No date commitment, screen-reader friendly, no deprecated idiom.
4. **Header/Footer reuse:** confirmed correct. Chrome-less placeholder would break nav context.

## Required before merge

1. **`copy/methodology_page.ts` `archLinkHref`** must point to the file root of the canonical repo:
   ```
   https://github.com/Mark1999/latent-structure-benchmark/blob/master/ARCHITECTURE.md
   ```
   (Note: the UI/UX agent's reasoning used `cogstructurelab/lsb` as a placeholder org — the actual repo path is `Mark1999/latent-structure-benchmark`, as confirmed by `git remote -v` and the public-flip runbook. **Coder uses the actual path.**) No `#` heading anchor.

2. **`aria-current="page"`** on the `/methodology` nav link when rendering on that route. Pattern: add `isActive` prop to `NAV_LINKS` mapping in `Header.tsx`, or derive inline from `window.location.pathname`. No new token.

3. **Unit test assertions:**
   - `<h1>` present
   - Link `href` equals the file-root GitHub URL with no `#` suffix
   - Body contains no forbidden vocabulary: `worldview`, `believes`, `thinks`, `coming in Phase 6`

## Follow-ups (non-blocking)

- **Skip-to-content link site-wide.** No `.sr-only` skip-link exists on any page today. Not introduced by T10; pre-existing accessibility gap. Schedule a separate site-wide a11y task.

---

*Verdict authored by UI/UX agent; transcribed and corrected for the actual repo path by the orchestrator.*
