# Phase 5 T10 Tester Verdict

**Task:** T10 — SourceAttribution + DownloadBar + CSV export + permalink codec
**Commits in scope:** `2feccd8` (Coder), `d02bcb5` (UI/UX corrections), `135b258` (Reviewer PASS)
**Tester verdict:** PASS-WITH-NOTES
**Date:** 2026-05-10

---

## Verdict

PASS-WITH-NOTES

The T10 implementation is correct and the original 476-test suite passes cleanly. Three coverage gaps were identified and filled with 7 gap-fill tests (suite now 483). All gap-fill tests pass. The notes below document what was missing and what was added.

---

## Test run results

| Suite | Before gap-fill | After gap-fill |
|---|---|---|
| vitest (dashboard) | 476 passed, 17 files | 483 passed, 17 files |
| pytest (Python) | 1258 passed | 1258 passed (unchanged) |
| `npm run lint` | clean | clean |
| `npm run build` | clean, 70.40 KB gzip | clean, 70.40 KB gzip |

Build bundle: 70.40 KB gzipped (limit: 380 KB).

---

## Tests written (gap-fill)

All 7 tests added in a single `test(dashboard):` commit.

### `apps/dashboard/src/__tests__/source-attribution.test.tsx` — 5 new tests

**describe: "SourceAttribution — v0.4.3 WCAG AA fix (--color-text-caption token)"**

- `wrapper element uses --color-text-caption for its color style` — asserts `container.querySelector('.source-attribution').style.color === 'var(--color-text-caption)'`. Directly verifies the v0.4.3 UI/UX correction is present in the rendered DOM. Previously untested: existing tests only checked `textContent`, not inline styles.

- `small-n note element uses --color-text-caption for its color style` — asserts the `.source-attribution__small-n-note` element's `style.color` is `var(--color-text-caption)`, not `--color-text-secondary` (which would be a WCAG AA failure at 12px italic).

**describe: "SourceAttribution — (N of M models shown) subspan"**

- `renders '(N of M models shown)' when selectedModels.length < totalModelCount` — 5-model fixture, 2 selected; asserts "2 of 5 models shown" appears.

- `does NOT render '(N of M models shown)' when all models are selected` — 3-model fixture, all 3 selected; asserts "models shown" is absent.

- `renders correct counts in '(N of M models shown)'` — 11-model fixture, 6 selected; asserts "6 of 11 models shown".

### `apps/dashboard/src/__tests__/permalink.test.ts` — 2 new tests

**describe: "encodePermalink — slash encoding in model_id (gap-fill)"**

- `encodes '/' in a model_id as '%2F' in the URL string` — asserts `encodePermalink` with `deepseek/deepseek-v3.2` produces a string containing `%2f`. Makes the URLSearchParams encoding contract explicit.

- `round-trips a model_id with multiple '/' chars without corruption` — asserts `meta-llama/llama-4-maverick` and `openai/gpt-5.4` survive encode → decode verbatim.

---

## Coverage gaps found and closed

### Gap 1 (critical): v0.4.3 `--color-text-caption` token not verified

The blocking T10 Reviewer/UI/UX concern was WCAG AA contrast — the `--color-text-muted` token was replaced with `--color-text-caption` (#6c757d, ~4.60:1). The original test suite verified only `textContent`; no test confirmed the inline `style.color` on the rendered elements used the new token. A future refactor that reverts to `--color-text-muted` would pass all 476 original tests undetected. Gap closed by 2 new style-assertion tests.

### Gap 2: `(N of M models shown)` subspan untested

`SourceAttribution.tsx` lines 84–93 have a branch: when `selectedModels.length !== domainResult.models.length`, a `(n of M models shown)` subspan renders. This is distinct from the `+N more` overflow (which is about the inline list truncation). The original tests exercised the `+N more` path only. Gap closed by 3 new tests.

### Gap 3: Permalink `/` encoding not explicitly asserted

The round-trip tests used model ids with `/` chars (e.g., `deepseek/deepseek-v3.2`) but only asserted the round-trip result, not the encoded form. The URL-safety contract (that `/` chars become `%2F`) was implicit. Gap closed by 2 new tests that assert both the encoding form and the round-trip.

---

## Real API call check

Re-grep of `apps/dashboard/src/__tests__/` confirms: all `fetch` references in tests are mocked via `vi.stubGlobal("fetch", mockFetch)` in `api-client.test.ts`. No test issues a real network request. CLAUDE.md rule 10 / pitfall 9 satisfied.

---

## Forbidden vocabulary check

No forbidden vocabulary (`believes`, `worldview`, `thinks` applied to models) appears in any committed test text or component copy.

---

## Notes for next agent

None. All identified gaps are closed. The suite is 483 tests and clean.
