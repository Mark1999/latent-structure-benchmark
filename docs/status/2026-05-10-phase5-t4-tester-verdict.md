# Phase 5 T4 — Tester Verdict

**Task:** Phase 5 T4 — Dashboard foundation scaffold (SPA shell, Header/ArticleHeader-stub/Footer, manifest fetch, embed mode detection)
**Commits validated:** `1b7064f` (Coder), `8322079` (UI/UX corrections), `bfc8e3e` (Reviewer PASS)
**Tester verdict:** PASS-WITH-NOTES
**Date:** 2026-05-10

---

## Verdict

PASS-WITH-NOTES

All 51 Coder tests pass. 33 new component render tests added (84 total). One structural note documented below.

---

## Test run output

### vitest (51 original tests)

```
 Test Files  5 passed (5)
      Tests  51 passed (51)
   Duration  1.23s
```

### vitest (84 tests after gap-fill)

```
 Test Files  6 passed (6)
      Tests  84 passed (84)
   Duration  1.35s
```

### ESLint

Clean (zero warnings, zero errors).

### Build

```
dist/index.html                   0.60 kB │ gzip:  0.37 kB
dist/assets/index-DecqivkI.css    7.73 kB │ gzip:  1.98 kB
dist/assets/index-Y5eTSLBT.js   200.39 kB │ gzip: 62.69 kB
✓ built in 1.61s
```

JS bundle: **62.69 kB gzipped** — passes <100 KB gzipped limit.

### Preview smoke

`curl http://localhost:4173/` returned valid HTML with correct `<title>Cognitive Structure Lab — Latent Structure Benchmark</title>` and correct asset references.

### Python suite

```
1258 passed, 26313 warnings in 14.30s
```

No regressions.

---

## Binding behavior spot-checks (all pass)

### framing.test.ts (16 tests)
- TAGLINE byte-equals canonical US English: confirmed (`"categorize"`, not `"categorise"`)
- TAGLINE begins with `"LSB measures"`: confirmed
- TAGLINE contains `"reproducible"`, `"comparable across models"`, `"trackable across time"`: confirmed
- Forbidden vocabulary (7 patterns): none found in TAGLINE or TAGLINE_LONG
- TAGLINE_LONG contains `"corpus lens"`: confirmed
- CORPUS_LENS_TERM === `"corpus lens"`: confirmed
- SITE_NAME === `"Cognitive Structure Lab"`: confirmed
- SITE_URL contains `"cogstructurelab.com"`: confirmed
- GITHUB_URL contains `"github.com"`: confirmed

### analysis-config.test.ts (3 tests)
- `OCI_LOW_CONCENTRATION_THRESHOLD === 3.0`: confirmed

### api-client.test.ts (10 tests)
- `fetchManifest()` fetches `/data/manifest.json` with `credentials: "omit"`: confirmed
- `fetchDomain("family")` fetches `/data/family.json`: confirmed
- `fetchDomain("family", "0.2")` fetches `/data/family.v0.2.json`: confirmed
- All fetch calls use `vi.stubGlobal("fetch", mockFetch)` — zero real network calls: confirmed
- Error handling: HTTP 404 and 500 both throw with message including status code: confirmed
- Error message includes slug name and version string: confirmed

### embed-detection.test.ts (10 tests)
- `?embed=true` → `isEmbedMode()` returns `true`: confirmed
- `?embed=false`, `?embed=`, empty string, other params → returns `false`: confirmed
- `?embed=TRUE` (case-sensitive) → returns `false`: confirmed
- `?embed=1` → returns `false`: confirmed
- Malformed `???` query string: no throw: confirmed
- `window.location.search` stub integration: confirmed

### app-state.test.ts (12 tests)
- Initial state is `"loading"`: confirmed
- `fetchManifest()` resolves → state transitions to `"loaded"`: confirmed
- `fetchManifest()` rejects → state transitions to `"error"`: confirmed
- All `fetchManifest` calls use `vi.mock("../api/client")` — no real fetch: confirmed
- `Header` and `Footer` export as functions (importable without error): confirmed
- `manifest.oci_low_concentration_threshold` matches `OCI_LOW_CONCENTRATION_THRESHOLD`: confirmed
- Error message canonical string contains `"Could not load data"` and `"Refresh the page"`: confirmed
- Loading message canonical string is `"Loading..."`: confirmed

---

## UI/UX corrections verified in build output

- `--color-model-11: #9a7d0a` present in `dist/assets/*.css`: **confirmed**
  (CSS property regex: `--color-model-11:\s*([^;/\s]+)` → `#9a7d0a`)
- Animation duration `revealFade` uses `.28s` (280ms, Vite-minified) in build output: **confirmed**
  (Source: `280ms` per DESIGN_SYSTEM.md v0.4.1; Vite minifies to `.28s`; no `300ms` in output)

---

## Real fetch in tests — grep result

Zero hits for bare `fetch(...)` not wrapped in `vi.fn()` or `vi.stubGlobal()` across all 6 test files. CLAUDE.md §6 R9 satisfied.

---

## Gap-fill tests written

**File:** `apps/dashboard/src/__tests__/components.test.ts` (33 tests, new)

| Test group | What it covers |
|---|---|
| Header.tsx — NAV_LINKS constant (5 tests) | 4 nav links present, correct hrefs (`/`, `/methodology`, `/data`, `/about`) and labels; SITE_NAME constant used |
| Footer.tsx — framing constant usage (9 tests) | DATA_LICENSE, CODE_LICENSE, GITHUB_URL, CONTACT_EMAIL all imported from framing.ts; /data, GITHUB_URL, #cite, /methodology, mailto: links present; `role="contentinfo"` |
| ArticleHeader.tsx — structure and framing constants (7 tests) | TAGLINE used in subtitle; SITE_NAME in byline; eyebrow with `article-header__eyebrow`; h1 with `article-header__title`; subtitle with `article-header__subtitle`; Methodology and Cite hrefs; loading conditional |
| App.tsx — ARIA attributes (4 tests) | `role="status"` + `aria-live="polite"` in loading state source; `role="alert"` + `aria-live="assertive"` in error state source |
| App.tsx — render order (4 tests) | Header before ArticleHeader; ArticleHeader before content placeholder; Footer after content; page-wrapper class present |
| tokens.css — color-model-11 (2 tests) | `--color-model-11: #9a7d0a` confirmed; CSS property assignment is `#9a7d0a` (not the old `#b7950b`) |

---

## Remaining coverage note (not a FAIL — structural constraint)

**ARIA attribute tests are source-text assertions, not DOM-render assertions.**

The `vite.config.ts` sets `test.environment: "node"`. The four ARIA tests
(`role="status"`, `aria-live="polite"`, `role="alert"`, `aria-live="assertive"`) are
implemented as source-text searches on `App.tsx` rather than as rendered-DOM assertions.
This is correct behavior: the attributes are present in the source (confirmed), and the
source-text test is a valid regression guard. A true DOM-render assertion would require
adding `jsdom` as a test dependency and configuring a separate test environment for
component tests.

**Recommendation for T5+:** when the data explorer is wired in (T6), add a jsdom-based
render suite as a parallel test environment. The `vite.config.ts` `test.environment`
can be overridden per-file with a `// @vitest-environment jsdom` comment. This is a
future enhancement, not a gap in T4's coverage.

**`prefers-reduced-motion` CSS override:** not unit-testable in vitest. The `@media
(prefers-reduced-motion: reduce)` override in `app.css` is verified by reading the
source and build output. Visual confirmation is a manual/Playwright concern for T6+.

---

## Checklist

- [x] 51 original tests pass (vitest)
- [x] 33 gap-fill tests written and passing (84 total)
- [x] `npm run lint` clean
- [x] `npm run build` clean, bundle <100 KB gzipped
- [x] Preview smoke: HTML loads correctly
- [x] Python suite: 1258 passed, no regressions
- [x] Zero real fetch/API calls in any test file
- [x] UI/UX corrections confirmed in build output (#9a7d0a, 280ms)
- [x] No forbidden vocabulary in any test file
- [x] Verdict file saved to `docs/status/2026-05-10-phase5-t4-tester-verdict.md`
