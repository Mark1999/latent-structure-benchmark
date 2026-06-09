# Phase 9a Data download tab — Tester verdict (2026-06-08)

**Task:** Tester gate for commit `98cf213` — Data download tab (`DataPage.tsx` + 12-case suite).
**Verdict file:** `docs/status/2026-06-08-phase9a-data-tab-tester-verdict.md`

---

## TESTER VERDICT: PASS

---

## 1. Baseline

`apps/dashboard/` — `npm run build && npm run test && npm run lint` all green before any scratch edits.

- Build: vite 6.4.2, 68 modules, no errors
- Tests: 9 test files, 108 tests, all pass
- Lint: eslint 0 warnings / 0 errors

---

## 2. Revert-and-confirm-fail #1 — external-link contract guard

Mutation: removed `rel="noopener noreferrer"` from the HuggingFace anchor in `DataPage.tsx`.

Result: **2 tests FAILED** (both correctly naming the gap):
- `DataPage > HuggingFace link has exact href, target=_blank, rel=noopener noreferrer` (case 2 — individual link test)
- `DataPage > every external <a> has target=_blank and rel=noopener noreferrer` (case 9 — loop test)

Restore via `git checkout --`: back to 108/108 green. Both halves confirmed.

---

## 3. Revert-and-confirm-fail #2 — SHA256 verbatim-copy guard

Mutation: changed final character of SHA256 hash in `DataPage.tsx` from `3` to `4`.

Result: **1 test FAILED** (exactly the right one):
- `DataPage > SHA256 string appears verbatim inside a <code> element` (case 6)

Restore via `git checkout --`: back to 108/108 green. Verbatim assertion is real, not vacuous.

---

## 4. Coverage verdict

All 12 plan cases from `docs/status/2026-06-08-phase9a-data-tab-architect-plan.md §6` are covered and verified real by the revert tests above.

Coverage map:
1. `<main aria-label="Data download">` landmark — case 1
2. HF exact href + target + rel — case 2 (revert #1 caught this)
3. DOI exact href + target + rel — case 3
4. B2 exact href + target + rel — case 4
5. "1.55 GB" warning before tarball anchor in DOM order — case 5
6. SHA256 verbatim in `<code>` — case 6 (revert #2 caught this)
7. GitHub exact href + target + rel — case 7
8. Citation first line in `<pre><code>` — case 8
9. Loop all external anchors for target+rel — case 9 (revert #1 also caught this)
10. Loop all external anchors for sr-only "opens" / download text — case 10
11. No forbidden vocabulary (ARCHITECTURE.md §1.5.4 / CLAUDE.md §7) — case 11
12. All four licenses present, CC-BY-4.0 appears at least twice — case 12

Gap found and filled: the 12 plan cases do not include a DOM section-order guard, but the UI/UX verdict §20 makes the B → D → A → C render order binding. No test existed to catch a future reorder. Added case 13 (see below).

---

## 5. Test added

**Case 13 — section render order (UI/UX verdict §20, binding):**

Added to `apps/dashboard/src/__tests__/DataPage.test.tsx` at the end of the describe block. Uses `compareDocumentPosition` with `DOCUMENT_POSITION_FOLLOWING` (same idiom as case 5) to assert:
- Section B (`#data-hf-heading`) precedes section D (`#data-cite-heading`)
- Section D precedes section A (`#data-header-heading`)
- Section A precedes section C (`#data-tarball-heading`)

Test passes green. Total suite: 9 test files, 109 tests, all pass. Lint clean.

---

## 6. Section-order spot check (DOM)

Confirmed by reading `DataPage.tsx` JSX order and by the new case 13 test:

```
B (HF, #data-hf-heading)        line 32
D (Cite, #data-cite-heading)    line 51
A (header/Data, #data-header-heading)  line 84
C (tarball, #data-tarball-heading)     line 97
E (GitHub)
F (bundle contents)
G (licenses)
H (provenance pointer)
```

Matches the UI/UX verdict §20 binding order exactly. The journalist and researcher CTAs (B and D) come before the framing paragraph (A) and the download itself (C), which is the intended reading-flow.

---

## 7. Commit

`test(dashboard): add section-order guard to DataPage suite (Phase 9a data tab)`

Commit hash: see below.

---

## 8. Tree state at close

Staged and committed: `apps/dashboard/src/__tests__/DataPage.test.tsx` only.

Untouched: `DataPage.tsx` at HEAD `98cf213`, `docs/proposed/2026-06-08-methodology-page-scaffold.md` (Mark's uncommitted scaffold edit), `WritingSample/`, `out/rebaseline/`, all other untracked files.

`git status --short` after commit shows only Mark's pre-existing untracked/modified files.

No real API calls in any test. All fixtures; DataPage is fully static.
