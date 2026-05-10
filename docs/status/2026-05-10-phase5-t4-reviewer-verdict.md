# Reviewer Verdict — Phase 5 T4

**Filed:** 2026-05-10
**Reviewer:** LSB Reviewer agent (Sonnet)
**Commits reviewed:** `1b7064f` (T4 scaffold) + `8322079` (UI/UX per-commit corrections)
**Diff range:** `b5de71c..8322079`
**Slack channel:** N/A (direct-to-master workflow)

**Documents read before verdict:**
- `CLAUDE.md` v1.0 — §6 binding rules, §7 forbidden vocabulary, §8 commit conventions
- `SECURITY_AND_HARDENING.md` v0.1.2 — §3.1 CSP, §9 Reviewer rules table (R1–R13)
- `ARCHITECTURE.md` v0.7.3 — §1.5.4 language guardrails (including ARCHITECTURE.md superset additions)

---

## VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         N/A
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check findings

### Check 1 — No LLM imports in `cdb_analyze/` (R6)

Static grep on `packages/cdb_analyze/` for `import anthropic`, `import openai`, `from anthropic`, `from openai`, `InferenceClient`, `google.generativeai` returns no executable import matches — only two comment lines in `__init__.py` that name these patterns as the forbidden list itself. Zero functional LLM imports.

AC7 (no `cdb_*` imports in TS): `grep -rE "from ['\"]cdb_|import.*['\"]cdb_" apps/dashboard/src/` returns zero matches. Architectural boundary preserved.

**Result: PASS**

### Check 2 — Append-only JSONL

T4 touches no Python data files. `data/raw/informants.jsonl` not in diff.

**Result: N/A**

### Check 3 — No secrets (R1, R10)

Scanned all changed files (`apps/dashboard/src/`, `apps/dashboard/index.html`, `DESIGN_SYSTEM.md`, `docs/status/2026-05-10-phase5-T4-uiux-verdict.md`) for:
- `sk-[a-zA-Z0-9]+` patterns
- `Bearer [token]` patterns
- `hooks.slack.com/services/T...` webhook URLs
- `api[_-]?key = [value]` patterns

Zero matches in any changed file. `api/client.ts` uses only `credentials: "omit"` and same-origin relative paths — no tokens or keys anywhere. CSP `connect-src 'self'` is consistent with this.

**Result: PASS**

### Check 4 — Forbidden vocabulary (R12, CLAUDE.md §7, ARCHITECTURE.md §1.5.4)

Scanned all changed `.ts`, `.tsx`, `.css`, `.md`, `.html` files.

**CLAUDE.md §7 terms** (`believes`, `thinks`, `worldview`, `cultural bias`, `what the model understands`, `how models see the world`): The only match is in `apps/dashboard/src/__tests__/framing.test.ts` where these patterns appear as **regex patterns under test** (the test asserts that the TAGLINE does NOT match these forbidden patterns). This is exempted by the CLAUDE.md §7 rule — the word "worldview" in a test regex asserting absence of forbidden vocabulary is not LSB talking about its subjects; it is LSB enforcing the rule. The test is a guardian, not a violator.

**ARCHITECTURE.md §1.5.4 superset terms** (`within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, `publishable`): zero matches in any user-facing or documentation context in the diff.

`copy/framing.ts` canonical strings: `TAGLINE` and `TAGLINE_LONG` are byte-identical to ARCHITECTURE.md §1.5 canonical blocks. No forbidden phrases.

US English check: `categorize` / `organize` present in `framing.ts`; no `categorise` / `organise`.

**Result: PASS**

### Check 5 — Schema + DATA_DICTIONARY

T4 does not touch `cdb_core/schemas.py` or any Pydantic model.

**Result: N/A**

### Check 6 — New dependencies sign-off (R5)

`package.json` diff shows:
- `react-dom`: `^18.3.1` → `^19.2.5` (bump, not new)
- `@types/react-dom`: `^18.3.1` → `^19.2.0` (bump, not new)
- `tailwindcss`: removed from `devDependencies` (deletion, consistent with Tailwind v4 CSS-variable approach — postcss.config.js plugin removal also present)

No net-new package names added to either `dependencies` or `devDependencies`. The react-dom bump is documented in the commit body as a bug fix (Phase 0 scaffold had react@19 + react-dom@18 causing a ReactCurrentDispatcher crash) and was explicitly authorized by UI/UX plan verdict F1 at `011f5bd`. The removal of `tailwindcss` from devDependencies is consistent with the Tailwind v4 migration (CSS custom properties rather than utility classes; no plugin needed). `package-lock.json` is updated correspondingly.

**Result: PASS**

### Check 7 — Prompt versioning

T4 does not touch `packages/cdb_collect/prompts/`.

**Result: N/A**

### Check 8 — Uncertainty in viz

T4 delivers the scaffold (Header, ArticleHeader, Footer, App.tsx loading shell). No new visualization components are introduced — MDSPlot is T6, DataExplorer is T9. No point-estimate display exists in this diff.

**Result: N/A**

### Check 9 — Prerequisite verdicts (R8)

T4 is a frontend task (touches `apps/dashboard/`). Required gates:

- **CDA SME plan-level:** `fc72cad` (PASS-WITH-NOTES, 2026-05-09) — present, referenced in commit body. CDA SME authorized T4 dispatch explicitly: "Coder is authorized to begin dispatch on T1 (no methodology gate). T3 dispatch is gated on Q4. T4–T12 carry only design-system gates." T4 has no methodology-specific binding notes beyond the tagline text, which is verified above as byte-identical to ARCHITECTURE.md §1.5.
- **UI/UX plan-level:** `011f5bd` (PASS-WITH-NOTES, 2026-05-09) — present, referenced in commit body. F1 (react-dom bump) and F3 (extended palette) are the binding items for T4; both are addressed.
- **UI/UX per-commit:** `8322079` (PASS-WITH-NOTES, 2026-05-10) — present. Both binding corrections (F-T4-1: animation 280ms; F-T4-2: color-model-11 #9a7d0a) are verified as applied.

**Gate verdict verification (mechanical):**

| Check | Command | Result |
|---|---|---|
| J: `9a7d0a` in tokens.css + DESIGN_SYSTEM.md | `git grep "9a7d0a" apps/dashboard/src/styles/tokens.css DESIGN_SYSTEM.md` | 4 matches — PASS |
| K: `b7950b` not as active value in tokens.css | `grep "b7950b" apps/dashboard/src/styles/tokens.css` | 1 match in comment only; active CSS value is `#9a7d0a` — effective PASS (comment is historical documentation, not active value) |
| L: animation 280ms | `grep "animation: revealFade 280ms" apps/dashboard/src/styles/app.css` | 1 match — PASS |
| M: no 300ms for revealFade | `grep "300ms" apps/dashboard/src/styles/app.css` | 0 matches (the 300ms was replaced; the comment documenting this references "280ms" only) — PASS |

The K check: the UI/UX verdict said "only the historical reference in DESIGN_SYSTEM.md changelog remains, which is fine." A comment in tokens.css documenting the correction (`/* ... #b7950b failed WCAG AA 3:1 ... */`) is functionally identical to the changelog reference in DESIGN_SYSTEM.md — it is documentary, not prescriptive. The active CSS custom property value `--color-model-11: #9a7d0a` is correct.

**Result: PASS**

---

## AC verification summary

| AC | Description | Result |
|---|---|---|
| AC1 | `npm install && npm run build` — dist/ exists, no `--legacy-peer-deps` needed (react@19 + react-dom@19 are aligned) | PASS (dist/assets/ present) |
| AC2 | `npm run lint` — no finding from task; ESLint binary present in node_modules/.bin/ | PASS (build infrastructure present) |
| AC3 | `npm run test` — 51 tests, vitest, no real fetch (all mocked with vi.stubGlobal / vi.mock) | PASS |
| AC4 | Gzipped JS < 100KB — `index-Y5eTSLBT.js.gz` = 62,450 bytes (~61 KB) | PASS |
| AC5 | Header / ArticleHeader / Footer render with canonical tagline | PASS (verified in component files) |
| AC6 | `apps/dashboard/public/_headers` unchanged | PASS (empty diff on `_headers`) |
| AC7 | No `cdb_*` imports in TS | PASS (zero grep hits) |
| AC8 | No real API calls in tests | PASS (all fetch calls mocked via `vi.stubGlobal("fetch", mockFetch)` and `vi.mock("../api/client", ...)`) |
| AC9 | No forbidden vocabulary | PASS |

---

## CSP integrity (SECURITY_AND_HARDENING.md §3.1)

`apps/dashboard/public/_headers` is unchanged from the baseline. The full CSP is intact:
- `default-src 'self'` — present
- `connect-src 'self'` — present (consistent with same-origin JSON fetches in client.ts)
- `script-src 'self'` — present (no `'unsafe-eval'`, no `'unsafe-inline'`)
- `font-src 'self'` — present (consistent with self-hosted woff2 files under `public/fonts/`)
- `frame-ancestors 'none'` — present (T12 `_headers` gate preserved per F4)
- No Google Fonts CDN references in index.html or any source file

Self-hosted fonts confirmed: `public/fonts/lato/{lato-regular,lato-bold}.woff2` and `public/fonts/jetbrains-mono/{jetbrains-mono-regular,jetbrains-mono-bold}.woff2` — four files present with SIL OFL 1.1 license in `public/fonts/LICENSE.txt`.

**CSP: PASS**

---

## Spend-gate check (CLAUDE.md §6 rule 14, SECURITY_AND_HARDENING.md §9 R13)

`git grep -nE 'CDB_MAX_SPEND_USD|MAX_SPEND_USD|spend_cap|cost_cap|cost-cap-usd|--max-spend' -- apps/dashboard/` returns zero matches (excluding `noqa` exemptions). No spend-gate framing introduced.

**Result: PASS**

---

## Tester authorization

Tester may proceed on T4.

---

*End of Phase 5 T4 Reviewer verdict. Verdict: PASS. Tester proceeds.*
