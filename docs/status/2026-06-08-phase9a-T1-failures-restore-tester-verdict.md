# Phase 9a T1 — Tester verdict (2026-06-09)

**Task:** Phase 9a T1 — Restore failures-as-findings Collection records tab.
**Commit under test:** `7e08cf2` (feat(dashboard): restore failures-as-findings as Collection records tab)
**Test file:** `apps/dashboard/src/__tests__/FailuresFindings.test.tsx`
**Tester commit:** see below (one `test(dashboard):` commit referencing 9a-T1)

---

## TESTER VERDICT: PASS

(Two test improvements applied before issuing verdict — see §3 coverage.)

---

## 1. Baseline

`npm run build && npm run test && npm run lint` from `apps/dashboard/` at HEAD `7e08cf2`.

- Build: green (67 modules, no TypeScript errors)
- Tests: 97 passed (97) across 8 test files
- Lint: clean (ESLint, no warnings)

---

## 2. Revert-and-confirm-fail results

### Revert-and-confirm-fail #1 — M4 chrome-isolation guard

Injected the string "consensus view" into the `<h1>` heading text inside
`FailuresFindings.tsx` (the visible LSB chrome, not a `<pre>` block).

- Tests with injection: **1 FAILED** — test 9 "M4/N7: LSB chrome does not contain
  forbidden substrings (no Explore chrome leak)": `expected ... not to contain 'consensus'`.
  Exactly the right test case fired. No other tests were affected.
- Restored via `git checkout -- apps/dashboard/src/components/FailuresFindings.tsx`.
- Tests after restore: **97 passed (97)**. GREEN confirmed.

### Revert-and-confirm-fail #2 — S1 no-verbatim-bytes-in-summary guard

Injected `{' '}{record.response_verbatim.slice(0, 40)}` into the `<summary>` of
`DeclineInterviewRow` (inside `FailuresFindings.tsx`).

- Tests with injection: **1 FAILED** — test 4 "summary rows do not expose
  response_verbatim text before expansion (T10 S1)": `expected 'Follow-up interview...'
  not to contain 'In that exchange, you asked me to sort a'`. Exactly the right test
  case fired. No other tests were affected.
- Restored via `git checkout -- apps/dashboard/src/components/FailuresFindings.tsx`.
- Tests after restore: **97 passed (97)**. GREEN confirmed.

---

## 3. Coverage check against plan §8

All 10 cases from the Architect plan §8 audited:

| Case | Description | Status |
|---|---|---|
| 1 | Heading present (SECTION_HEADING verbatim) | COVERED — test 1, `getByRole('heading', {level:1})` + `toHaveTextContent(SECTION_HEADING)` |
| 2 | framing_note byte-identity | COVERED — test 2, `getByText(familyJson.framing_note)` exact match |
| 3 | `<details>` count === n_records | COVERED — test 3, `querySelectorAll('details').length === 36` |
| 4 | S1 summary no verbatim bytes | COVERED — test 4, iterates all summaries × all decline records' first-40-chars |
| 5 | originating_outcome_class in `<code>` | COVERED — test 5, `querySelectorAll('summary code')` with value check |
| 6 | Click-to-expand exposes response_verbatim in `<pre>` | COVERED — test 6, fireEvent.click + checks `<pre>` text |
| 7 | Provenance exposes sha256_manifest | COVERED — test 7, click to expand, `getByText(sha256_manifest)` |
| 8 | Empty state: verbatim EMPTY_CAPTION + zero `<details>` (food) | COVERED — see below (fix applied) |
| 9 | M4 chrome grep (forbidden vocab excluded from LSB chrome) | COVERED — test 9, `extractChromeText` helper + 7 forbidden patterns |
| 10 | Domain switch re-fetches (AC4) | COVERED — test 10, fetchSpy call count + URL matching |

### Fixes applied (2 items)

**Fix 1 — Test 8 placeholder replaced (WEAK → COVERED).**
The original suite had a `expect(true).toBe(true)` placeholder labelled "plan §8 case 8" with
actual coverage deferred to a separate "8b" test. The placeholder inflated the test count
without testing anything. Replaced with a single direct test: `mockFetchWith(foodJson)` queued
for the initial family fetch; component receives `n_records=0`; `waitFor(EMPTY_CAPTION)` +
`querySelectorAll('details').length === 0`. This is a tighter, cleaner path than the
original 8b (which performed a domain switch mid-test after already being in the empty state).
Test count: 97 → 96.

**Fix 2 — Test 9 dead `if` block replaced with explicit assertion.**
The original test 9 called `prEls_haveResponseBytes(preEls)` inside an `if` block whose
body contained only a comment. This meant the test could pass vacuously if `<pre>` elements
happened to be empty (exclusion logic never exercised). Changed to
`expect(prEls_haveResponseBytes(preEls)).toBe(true)`, which asserts the exclusion logic is
doing real work: at least one `<pre>` in the DOM contains response_verbatim bytes from the
fixture. This guarantees the chrome-isolation check is not vacuously passing.

---

## 4. Empty-state spot check

`food.json` fixture: `n_records=0`, `records: []` (zero entries).

Test 8 (post-fix): renders component with `foodJson` as mock response. Assertions:
- `screen.getByText(EMPTY_CAPTION)` finds the `<p class="failures-findings__empty">` element
  containing the T10 S2 verbatim caption text.
- `container.querySelectorAll('details').length === 0`.

Both pass. The empty state is first-class (no error icon, no skeleton, no greyout). CONFIRMED.

Note: `food.json.framing_note` is the standard pipeline framing note (same as family), not the
EMPTY_CAPTION constant. The component correctly renders `data.framing_note` as the intro `<p>`
AND `EMPTY_CAPTION` as the empty-state `<p class="failures-findings__empty">`. The test
asserts the EMPTY_CAPTION string appears, which it does.

---

## 5. Commit

One `test(dashboard):` commit with the two fixes above.
Commit hash: see git log after this file is committed.

---

## 6. Working tree state after all operations

```
M  apps/dashboard/src/__tests__/FailuresFindings.test.tsx  (tester commit)
M  docs/proposed/2026-06-08-methodology-page-scaffold.md   (Mark's uncommitted edit, untouched)
?? WritingSample/
?? docs/status/2026-06-08-phase9a-T1-failures-restore-architect-plan.md
?? docs/status/2026-06-08-phase9a-T1-failures-restore-cda-sme-verdict.md
?? docs/status/2026-06-08-phase9a-T1-failures-restore-uiux-verdict.md
?? docs/status/2026-06-08-phase9a-data-tab-architect-plan.md
?? docs/status/2026-06-08-phase9a-data-tab-cda-sme-verdict.md
?? docs/status/2026-06-08-phase9a-data-tab-ui-ux-verdict.md
?? out/rebaseline/
```

All scratch edits to `FailuresFindings.tsx` were restored via `git checkout --` before
this commit. `FailuresFindings.tsx` is at HEAD `7e08cf2` exactly.

No commits to `out/rebaseline/`, `WritingSample/`, or the methodology scaffold.
