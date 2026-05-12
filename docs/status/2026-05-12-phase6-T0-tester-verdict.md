# Phase 6 T0 Tester Verdict

**Task:** T0 — Operator Inspection Mode (`?inspect=...`)
**Date:** 2026-05-12
**Verdict:** PASS
**Agent:** Tester (Sonnet)
**Commit reviewed:** `39d8a05` (Coder) + `b5f45d9` (this gap-fill)

---

## Audit checklist

### F-T0-A1 — InspectSection id generation

- [COVERED by Coder] Individual id slug derivation: `inspect.test.tsx` — "renders h2 with id derived from title (F-T0-A1)" and "strips special chars from id"
- [GAP-FILLED] **Set-level uniqueness**: no test in `inspect.test.tsx` asserted that all 17 domain-mode and 2 manifest-mode section titles produce _distinct_ HTML ids. `t0-gap-fill.test.ts` adds 7 tests covering: set uniqueness (domain and manifest modes separately), HTML id character validity, source-sync checks that InspectRoot.tsx uses exactly the §2.4 heading strings, and the parentheses-stripping regression for "MDS uncertainty (bootstrap ellipses)".

### F-T0-B1 — `--color-surface` token

- [COVERED by Coder] `inspect.test.tsx` lines 269-276: asserts `inspect.css` contains `--color-surface` and does not contain `--color-bg-surface`. No gap.

### F-T0-B2 — `--font-mono` token

- [COVERED by Coder] `inspect.test.tsx` lines 264-285: asserts both `InspectTable.tsx` source and `inspect.css` contain `--font-mono` and do not contain `--font-family-mono`. No gap.

### F-T0-C1 — loading/error strings use `--color-text-caption`

- [COVERED by Coder] `inspect.test.tsx` lines 287-291: asserts `InspectRoot.tsx` source contains `--color-text-caption` and does not contain `--color-text-muted`. No gap.

### AC5 — reader mode unchanged

- [GAP-FILLED] No test in `inspect.test.tsx` or `app-state.test.ts` verified that the full-page reader branch (no `?inspect=`, no `?embed=`) still contains `ArticleHeader`, `DataExplorer`, and `MethodologySummary` after T0 introduced the `inspectSlug !== null` early-return. `t0-gap-fill.test.ts` adds 5 tests: presence of all three components in source, correct ordering of the `inspectSlug` check before `page-wrapper` return, and correct ordering of `inspectSlug` check before the `embed-root` block.

### AC6 — `?embed=true` mode unchanged

- [COVERED partially by pre-T0 tests] `embed-detection.test.ts` verifies `isEmbedMode()` in isolation. However, no test verified that the T0 early-return ordering (`inspectSlug !== null` checked before `embedMode`) does not intercept `?embed=true` requests.
- [GAP-FILLED] `t0-gap-fill.test.ts` adds 4 tests: `embed-root` block still present; `isEmbedMode` still called; `InspectRoot` not rendered inside embed branch; `inspectSlug` null guard falls through to `embedMode` check.

### AC7 — unknown field surfaces in "Other top-level fields"

- [COVERED by Coder] `inspect.test.tsx` lines 627-651: renders `MOCK_DOMAIN` fixture containing `foo_bar: [1,2,3]` and asserts "Other top-level fields" heading and "foo_bar" key appear. No gap.

### AC10 — `<meta robots noindex>` lifecycle

- [COVERED by Coder] `inspect.test.tsx` lines 516-558: mount test asserts meta tag injected; unmount test asserts meta tag removed. No gap.

### AC11 — no forbidden vocabulary

- [COVERED partially by Coder] `inspect.test.tsx` lines 301-315 check `"worldview"`, `"believes"`, and `"How models see"` in InspectRoot.tsx source. Only 3 of the 10 CLAUDE.md §7 forbidden constructions were checked; `InspectSection.tsx`, `InspectTable.tsx`, and `inspect.css` were not checked at all.
- [GAP-FILLED] `t0-gap-fill.test.ts` adds 31 tests scanning all four inspect surface files against the full §7 forbidden phrase table (10 patterns: `believes`, `Model X believes`, `How models see the world`, `How models see`, `What the model understands`, `Cultural bias`, `worldview`, `model thinks`, `model believes`, `model understands`). Case-insensitive matching.

### Schema-drift safety net

- [COVERED by Coder — via AC7] The "Other top-level fields" mechanism is tested. No additional gap.

---

## Tests added

New file: `/opt/lsb-agent/apps/dashboard/src/__tests__/t0-gap-fill.test.ts`

```
t0-gap-fill.test.ts — F-T0-A1 — all domain-mode section titles produce distinct slugified ids
t0-gap-fill.test.ts — F-T0-A1 — all manifest-mode section titles produce distinct slugified ids
t0-gap-fill.test.ts — F-T0-A1 — domain-mode ids are valid HTML ids
t0-gap-fill.test.ts — F-T0-A1 — manifest-mode ids are valid HTML ids
t0-gap-fill.test.ts — F-T0-A1 — InspectRoot.tsx uses exactly the §2.4 domain section headings (source sync check)
t0-gap-fill.test.ts — F-T0-A1 — InspectRoot.tsx uses exactly the §2.4 manifest section headings (source sync check)
t0-gap-fill.test.ts — F-T0-A1 — InspectSection.tsx titleToId strips parentheses (MDS uncertainty title test)
t0-gap-fill.test.ts — AC5 — App.tsx full-page branch still renders ArticleHeader
t0-gap-fill.test.ts — AC5 — App.tsx full-page branch still renders DataExplorer
t0-gap-fill.test.ts — AC5 — App.tsx full-page branch still renders MethodologySummary
t0-gap-fill.test.ts — AC5 — App.tsx inspectSlug check appears BEFORE the full-page return
t0-gap-fill.test.ts — AC5 — App.tsx inspectSlug check appears BEFORE embedMode early-return
t0-gap-fill.test.ts — AC6 — App.tsx embed-root block is still present after T0 changes
t0-gap-fill.test.ts — AC6 — App.tsx embedMode is still checked (isEmbedMode call is present)
t0-gap-fill.test.ts — AC6 — App.tsx embed-root branch does NOT contain InspectRoot rendering
t0-gap-fill.test.ts — AC6 — App.tsx inspectSlug null guard prevents inspect mode when slug is null
t0-gap-fill.test.ts — AC11 — InspectRoot.tsx: 10 forbidden phrases × 1 file = 10 tests
t0-gap-fill.test.ts — AC11 — InspectSection.tsx: 10 forbidden phrases × 1 file = 10 tests
t0-gap-fill.test.ts — AC11 — InspectTable.tsx: 10 forbidden phrases × 1 file = 10 tests
t0-gap-fill.test.ts — AC11 — inspect.css: combined forbidden vocabulary scan
```

---

## Test run output

```
Test Files  28 passed (28)
     Tests  812 passed (812)
  Start at  14:45:44
  Duration  30.78s
```

47 tests added (765 → 812 total). No failures. No production code modified.

---

## Coverage gaps remaining

None. All T0 acceptance criteria are now covered:

| Criterion | Coverage status |
|---|---|
| F-T0-A1 (id generation + uniqueness) | Coder individual slug + Tester set-level uniqueness |
| F-T0-B1 (--color-surface token) | Coder — full coverage |
| F-T0-B2 (--font-mono token) | Coder — full coverage |
| F-T0-C1 (--color-text-caption for loading/error) | Coder — full coverage |
| AC5 (reader mode unchanged) | Tester gap-fill |
| AC6 (embed mode ordering after inspect guard) | Tester gap-fill |
| AC7 (unknown field in Other top-level fields) | Coder — full coverage |
| AC8 (accessibility: caption, th scope, h1→h2) | Coder DOM tests + source assertions |
| AC10 (meta robots noindex lifecycle) | Coder — full coverage |
| AC11 (forbidden vocabulary, comprehensive) | Coder partial + Tester gap-fill |
| AC12 (no new dependencies) | Coder source assertions |
| AC13 (no raw-data paths) | Coder source assertions |
| Schema-drift safety net | Covered via AC7 |

---

*Gap-fill commit: `b5f45d9`*
*Reviewer PASS upstream: `docs/status/2026-05-12-phase6-T0-reviewer-verdict.md`*
