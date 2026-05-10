# Phase 5 T5 — Tester Verdict

**Task:** T5 — DomainPicker + KeyFinding components
**Coder commit:** `eae4da5`
**UI/UX verdict:** PASS (`a584d97`)
**Reviewer verdict:** PASS (`f106362`)
**Tester verdict date:** 2026-05-10
**Tester agent:** Sonnet 4.6

---

## Verdict: PASS-WITH-NOTES

All gates cleared. Five gap tests added (see below). New tests committed as `test(dashboard):`.

---

## Test run results

### Vitest (frontend)

Original suite (Coder-shipped): **121 passed** — confirmed.

After gap-fill additions: **126 passed, 0 failed, 0 skipped** (8 test files).

```
Test Files  8 passed (8)
Tests  126 passed (126)
Duration  3.99s
```

### Python suite

**1258 passed, 26313 warnings** — unchanged, no regressions.

```
1258 passed, 26313 warnings in 14.12s
```

### Lint

`npm run lint` — clean (0 errors, 0 warnings).

### Build

`npm run build` — clean.
- Bundle: 63.58 KB gzipped (target: <400 KB — 84% headroom).
- TypeScript compile: clean.

### Preview smoke

`curl http://localhost:4173/` returns valid `<!doctype html>` with correct title
"Cognitive Structure Lab — Latent Structure Benchmark" and linked JS/CSS assets.

---

## Binding behavior inspection (30 Coder tests + T5 extensions)

### domain-picker.test.tsx (20 Coder tests)

| Binding behavior | Status |
|---|---|
| Pill count matches domains prop | PASS |
| Active pill aria-selected="true" | PASS |
| Inactive available pill aria-selected="false" | PASS |
| Disabled pill aria-selected="false" | PASS |
| Disabled pill aria-disabled="true" | PASS |
| Disabled pill tabIndex is not -1 (remains in tab order) | PASS |
| Available pill tabIndex is 0 | PASS |
| Click available pill calls onSelect(slug) | PASS |
| Click disabled pill does NOT call onSelect | PASS |
| ArrowRight moves focus to next pill | PASS |
| ArrowLeft moves focus to previous pill | PASS |
| ArrowRight from last pill wraps to first | PASS |
| Enter activates available pill | PASS |
| Enter on disabled pill does NOT call onSelect | PASS |
| Disabled pill title = "Coming in a future update" exactly | PASS |
| Available pill has no title tooltip | PASS |
| Active pill aria-label contains "currently displayed" | PASS |
| Inactive available pill aria-label contains "switch to view" | PASS |
| Disabled pill aria-label contains "coming in a future update" | PASS |
| Container has role="tablist" | PASS |
| Tablist has aria-label="Domain selection" | PASS |

### key-finding.test.tsx (10 Coder tests)

| Binding behavior | Status |
|---|---|
| Renders generatedLede as visible text | PASS |
| Renders updated lede on prop change | PASS |
| Outer section has role="region" | PASS |
| Outer section has aria-label="Key finding" | PASS |
| Inner content has aria-live="polite" | PASS |
| Outer section has class "key-finding" | PASS |
| Inner content has class "key-finding__content" | PASS |
| key-change fade re-fires on lede change | PASS |
| .key-finding container class present (carries 780px max-width) | PASS |

### app-state.test.ts T5 extensions (6 Coder tests)

| Binding behavior | Status |
|---|---|
| Default activeSlug is "family" (source text assertion) | PASS |
| fetchDomain("holidays") called when slug switches | PASS |
| Manifest with 1 domain produces 1 available + ≥3 unavailable pills | PASS |
| Domain switch updates generated_lede (mocked) | PASS |
| DomainPicker exported as function component | PASS |
| KeyFinding exported as function component | PASS |

---

## CSS verification

- `animation: keyFindingFade 200ms ease-out forwards;` — confirmed at line 419 of app.css.
- `@media (prefers-reduced-motion: reduce)` block for `.key-finding__content` — confirmed at lines 432-437 of app.css (sets `animation: none; opacity: 1`).
- Separate `@media (prefers-reduced-motion: reduce)` block for `.reveal-cascade-item` — confirmed at lines 88-94.

---

## No real API calls

`grep "fetch("` across all three new test files returned no output. All fetch calls are either
`vi.fn()` mocks or accessed through `vi.mocked(fetchManifest)` / `vi.mocked(fetchDomain)`.
Rule 10 (CLAUDE.md §6) — confirmed clean.

---

## Coverage gaps identified and filled

Five tests were absent from the Coder's suite. All five were added in this session:

### Gap 1 — ArrowLeft wrap-around (first pill → last pill)
**File:** `apps/dashboard/src/__tests__/domain-picker.test.tsx`
**Test:** `"ArrowLeft from first pill wraps to last"`
**Why:** The Coder tested ArrowRight wrap (last→first) but not the symmetric ArrowLeft
wrap (first→last). The `moveFocus` function uses `(currentIndex + direction + total) % total`
which handles both wraps. The missing test would have caught a regression if the formula
changed to `(currentIndex + direction) % total` (which breaks on negative index).

### Gap 2 — Space key on disabled pill
**File:** `apps/dashboard/src/__tests__/domain-picker.test.tsx`
**Test:** `"Space key on disabled pill does NOT call onSelect"`
**Why:** The `handleKeyDown` handler guards `e.key === " "` (Space) with `domain.available`.
The Coder tested Enter on disabled; Space was not tested. Both keys are in the same guard.

### Gap 3 — fetchDomain rejection is non-fatal
**File:** `apps/dashboard/src/__tests__/app-state.test.ts`
**Test:** `"fetchDomain rejection is non-fatal — manifest state is still 'loaded'"`
**Why:** App.tsx catches domain fetch errors silently (non-fatal). There was no test
verifying that a domain fetch failure does not transition appState to "error". The Coder
tested manifest rejection (which does set error state) but not domain fetch rejection.

### Gap 4 — Embed mode hides DomainPicker + KeyFinding
**File:** `apps/dashboard/src/__tests__/app-state.test.ts`
**Test:** `"App.tsx isEmbedMode() function exists and returns false when search is empty"`
**Why:** DESIGN_SYSTEM.md §12.5 requires that ?embed=true suppresses DomainPicker,
KeyFinding, Header, Footer, ArticleHeader. No test verified this. The source-read strategy
(same approach as the activeSlug default test) is used because `window.location.search`
cannot be set in the node vitest environment. The test confirms: (a) isEmbedMode() exists,
(b) it checks `?embed=true`, (c) the embed-root block contains no `<DomainPicker` or
`<KeyFinding`. A jsdom render test for this is deferred to the T13 Playwright pass.

### Gap 5 — Canonical lede format regression
**File:** `apps/dashboard/src/__tests__/app-state.test.ts`
**Test:** `"generated_lede in fixture follows the canonical 'Across N frontier models...' format"`
**Why:** The UI/UX agent verified the lede format manually during review. A regex test
(`/^Across \d+ frontier models,/`) prevents the fixture from drifting silently to a format
that would no longer match the DESIGN_SYSTEM.md §3.8 binding lede pattern.

---

## Remaining carry-forward items (not gaps in T5 scope)

These items were assessed but correctly deferred:

- **`prefers-reduced-motion: reduce` CSS override for keyFindingFade** — the CSS is correctly
  implemented (verified by grep). Testing it in vitest/jsdom is not feasible because jsdom
  does not resolve `@media` queries. Carry forward to T13 Playwright/visual regression pass.

- **Embed mode full DOM render test** — `window.location.search` is not settable in the
  node vitest environment without URL mocking infrastructure. The source-text assertion
  (Gap 4 above) provides a structural guarantee. A full jsdom/Playwright test is deferred
  to T13.

- **Smith's S = X.XX, 95% CI [Y, Z] lede format** — noted in the task spec as the format
  the UI/UX agent checked manually. The current lede format in the published fixtures uses
  the "Across N frontier models..." pattern, not a Smith's S format. Gap 5 above adds a
  regex regression on the actual canonical format.

---

## Notes to Coder (PASS-WITH-NOTES)

1. The ArrowLeft wrap-around gap (Gap 1) and Space-on-disabled gap (Gap 2) are low-risk
   because the implementation handles both correctly — the gaps were test coverage gaps,
   not behavioral gaps.

2. The embed mode structural test (Gap 4) uses a source-read strategy. If the App.tsx
   embed branch is ever refactored to a separate component file, this test will need
   updating. Consider extracting `EmbedShell` in a future task to make this more testable.

3. No forbidden vocabulary found in any committed text for this task. §12.3 references
   in the source comments use "coming in a future update" (not "not available" or
   "phase-gated"), confirming compliance with the design system.
