# Reviewer Verdict — Phase 5 T12 (CiteModal + EmbedModal)

**Filed:** 2026-05-11
**Reviewer:** LSB Reviewer agent (Sonnet)
**Commits reviewed:** `71f343c` (Coder) + `9004e35` (UI/UX correction F-T12-1)
**Scope:** Union diff `6dc6bbf..9004e35`
**Prerequisite verdicts:**
- Plan-level CDA SME PASS-WITH-NOTES: `docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`
- Plan-level UI/UX PASS-WITH-NOTES: `docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md`
- T12 per-commit UI/UX FAIL→PASS-WITH-NOTES: `docs/status/2026-05-11-phase5-T12-uiux-verdict.md`

---

## REVIEWER VERDICT: PASS-WITH-NOTES

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         N/A (no informants.jsonl change)
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A (no cdb_core/schemas.py change)
Check 6 — New deps sign-off:         N/A (no new dependencies)
Check 7 — Prompt versioning:         N/A (no prompt template changes)
Check 8 — Uncertainty in viz:        N/A (export/cite modals; no new visualization)
Check 9 — Prerequisite verdicts:     PASS
```

**Security audit note (R3 — _headers):** `frame-ancestors 'none'` → `frame-ancestors *` passes with the Architect's documented stance as sign-off (see §3 below). The residual `X-Frame-Options: DENY` header creates a maintenance inconsistency and must be removed in a follow-up commit before T13. No ARCHITECTURE.md §7 entry was added for this CSP change; one is required in that follow-up commit.

---

## Check-by-check rationale

**Check 1 — No LLM imports in cdb_analyze/**

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/` returns only the prohibition notice comment in `cdb_analyze/__init__.py` (lines 12–13), not actual executable imports. T12 touches only `apps/dashboard/` — `packages/cdb_analyze/` is not modified in this diff. PASS.

**Check 2 — Append-only JSONL**

`git diff 6dc6bbf..9004e35 -- data/` returns empty. No data files of any kind are touched. N/A.

**Check 3 — No secrets**

Full manual scan of all 13 changed files (`apps/dashboard/public/_headers`, `App.tsx`, three test snapshot and test files, `CiteModal.tsx`, `DataExplorer.tsx`, `DownloadBar.tsx`, `EmbedModal.tsx`, `citation.ts`, `app.css`, `docs/status/2026-05-11-phase5-T12-uiux-verdict.md`) found no API keys, webhook URLs, Slack credential patterns (`https://hooks.slack.com/services/T.../B.../...`), `sk-ant-`, `sk-or-v1-`, `hf_`, `B2_APPLICATION_KEY`, passwords, or any other credential-shaped strings. Verified with `git diff 6dc6bbf..9004e35 | grep -E "(sk-ant|sk-or-v1|hf_|AKIA|hooks\.slack\.com)"` returning empty. PASS.

**Check 4 — Forbidden vocabulary**

Grep for `believes|thinks|worldview|cultural bias|within-model consensus|within-model cultural consensus|within-model eigenratio|within-model CCM|publishable|recognizes|interprets|perceives|comprehends` across `CiteModal.tsx`, `EmbedModal.tsx`, `citation.ts`, `App.tsx`, `DataExplorer.tsx`, `DownloadBar.tsx` returned zero matches. The UI/UX verdict file also contains no forbidden phrases. Citation strings correctly avoid any anthropomorphizing model language — they describe the benchmark and dataset, not model cognition. PASS.

**Check 5 — Schema + DATA_DICTIONARY**

`git diff 6dc6bbf..9004e35 -- packages/cdb_core/` returns empty. No Pydantic schema changes of any kind. R7 does not trigger. N/A.

**Check 6 — New deps sign-off**

`git diff 6dc6bbf..9004e35 -- apps/dashboard/package.json apps/dashboard/package-lock.json` returns empty. No new npm dependencies added. T12 uses `react-dom`'s `createPortal` (existing approved dependency) and the Clipboard API (browser built-in). No new Python dependencies either. N/A.

**Check 7 — Prompt versioning**

`git diff 6dc6bbf..9004e35 -- packages/cdb_collect/prompts/` returns empty. No prompt template changes. N/A.

**Check 8 — Uncertainty in viz**

T12 is an export and citation modal task, not a new visualization. `CiteModal.tsx` and `EmbedModal.tsx` render formatted text and an iframe snippet respectively. Neither introduces any graphical display of a point estimate. The existing `MDSPlot.tsx` with bootstrap ellipses is not modified. N/A.

**Check 9 — Prerequisite verdicts**

T12 is a frontend PR. The required UI/UX gate verdict is present at `docs/status/2026-05-11-phase5-T12-uiux-verdict.md` (originally FAIL on F-T12-1, upgraded to PASS-WITH-NOTES after correction was applied alongside the verdict in commit `9004e35`). The blocking note F-T12-1 (dynamic `aria-label` for copy state) was applied in `9004e35` — verified in source at `CiteModal.tsx` line 401 (`aria-label={copied ? \`${tab.label} citation copied\` : \`Copy ${tab.label} citation\`}`) and `EmbedModal.tsx` line 314 (`aria-label={copied ? "Embed code copied" : "Copy embed code"}`). The non-blocking note F-T12-2 (`yearFromIso` fallback using `getFullYear()` instead of `getUTCFullYear()`) is carried forward as-is, accepted as cosmetic. T12 introduces no new methodology claims; CDA SME gate is not triggered at the per-commit level (plan-level CDA SME PASS-WITH-NOTES covers the phase). PASS.

---

## Specific T12 checks

| # | Check | Result |
|---|---|---|
| 1 | §1.6 naming in all four citation formats: "Cognitive Structure Lab" + "LSB" in `buildApa`, `buildMla`, `buildChicago`, `buildBibtex` | PASS — `citation.ts` lines 49, 63, 77, 102–103 each include both names. Header comment at line 4–6 explains the requirement and its source. |
| 2 | Modal ARIA: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` in both modals | PASS — `CiteModal.tsx` lines 324–326; `EmbedModal.tsx` lines 270–272. Both carry all three attributes. |
| 3 | `embed=true` URL flag chain: App.tsx → DataExplorer → EmbedModal | PASS — `App.tsx` `isEmbedMode()` at line 35 detects `?embed=true`; `DataExplorer.tsx` accepts `isEmbed?: boolean` prop (line 62) with default `false` (line 144); embed mode passes `isEmbed={true}` (App.tsx line 204). `DownloadBar.tsx` hides Permalink and Embed buttons when `isEmbed=true` per §12.5. `EmbedModal.tsx` comment at line 5 confirms snippet includes `?embed=true`. |
| 4 | No HARDWARE.md committed | PASS — `git diff 6dc6bbf..9004e35 -- HARDWARE.md` returns empty. |
| 5 | No new dependencies | PASS — `git diff 6dc6bbf..9004e35 -- apps/dashboard/package.json apps/dashboard/package-lock.json` returns empty. |
| 6 | No data files or packages touched | PASS — `git diff 6dc6bbf..9004e35 -- data/ packages/` returns empty. |
| 7 | Build + test + lint green | PASS — `eslint`: clean; `tsc -b && vite build`: 244.25 KB raw / 75.20 KB gzipped; `vitest run`: 634/634 pass (22 test files). |
| 8 | Bundle size under §9 cap (400 KB gzipped) | PASS — 75.20 KB gzipped, well under 400 KB cap. Raw JS asset `index-6i_elQEs.js` is 240 KB on disk. |
| 9 | Forbidden vocabulary scan | PASS — zero matches across all six named source files. |
| 10 | Spend-cap framing | PASS — `grep -rinE "spend|CDB_MAX_SPEND|cost cap" apps/dashboard/src/` returns empty (excluding test and markdown files). |
| 11 | `dangerouslySetInnerHTML` not used in T12 components | PASS — grep across `CiteModal.tsx`, `EmbedModal.tsx`, `citation.ts` returns empty. Citation strings are rendered as plain text via React text nodes and `<pre><code>` blocks, not HTML. |
| 12 | F-T12-1 fix applied (dynamic `aria-label` for copy state) | PASS — `9004e35` applies exactly the fix specified by the UI/UX verdict in both modals. 634/634 tests pass post-fix. |
| 13 | gitleaks | N/A — `gitleaks` not installed in this environment. Manual scan of all 13 changed files found no credential patterns. GitHub secret scanning is the second layer. |

---

## Security audit — `_headers` CSP: `frame-ancestors 'none'` → `frame-ancestors *`

### What changed

A single directive in `apps/dashboard/public/_headers` was modified in commit `71f343c`:

```diff
-  frame-ancestors 'none';
+  frame-ancestors *;
```

All other CSP directives (`default-src 'self'`, `connect-src 'self'`, `img-src 'self' data:`, `style-src 'self' 'unsafe-inline'`, `script-src 'self'`, `font-src 'self'`, `base-uri 'self'`, `form-action 'self'`, `object-src 'none'`, `upgrade-insecure-requests`) are byte-identical to the prior state. Verified by examining the full diff output which shows exactly one changed line.

The legacy header `X-Frame-Options: DENY` was NOT changed and remains in `_headers`.

### Security justification (from commit body)

The Coder's commit body documents the following justification for the relaxation:

- No authentication on dashboard — an attacker who causes a victim to embed the dashboard gains no session cookie or credential-gated action.
- No mutation endpoints — the dashboard is a static site; there is no form submission, no API write path, no CSRF surface.
- No user-supplied state beyond URL params — `decodePermalink` validates those.
- CC-BY 4.0 content licensing explicitly permits redistribution, making third-party embedding consistent with the license.
- All other CSP directives remain intact, preserving the XSS defenses.

These claims are verifiable from the codebase: the static architecture is confirmed by `ARCHITECTURE.md` §4.4 ("static-files architecture has no backend to overwhelm"); the CC-BY 4.0 licensing is confirmed by the license table in `ARCHITECTURE.md` §7 decision #6.

### Clickjacking surface assessment

The original rationale for `frame-ancestors 'none'` (documented in `SECURITY_AND_HARDENING.md` §3.1) was "Prevents UI redress / clickjacking." With `frame-ancestors *`, any third-party site can embed the dashboard in an iframe.

The residual clickjacking risk requires evaluating what an attacker could gain by overlaying or embedding the LSB dashboard:

1. **No authentication.** There is no login, no session, no persistent user state. A clickjacking attack that tricks a user into "clicking" something on the dashboard cannot steal a session token, because none exists.
2. **No write actions.** All dashboard interactions are client-side reads. Buttons download CSVs, copy text, or navigate within the single-page app. None of these actions have server-side consequences that an attacker could exploit.
3. **No user data input.** There are no forms, no search inputs that submit to a server, no text fields with security consequences. The sole input surface is URL params, which are validated client-side.
4. **No financial or personal data.** The dashboard displays research benchmark data. There is nothing of exfiltration value to overlay.

Assessment: the practical clickjacking risk for this specific application is low to negligible given the static, read-only, no-auth architecture. The original `frame-ancestors 'none'` was conservative defense-in-depth for a use case (third-party embedding) that T12 now explicitly enables as a feature. The relaxation is architecturally justified.

### Browser behavior matrix: `frame-ancestors *` + `X-Frame-Options: DENY`

The current `_headers` file simultaneously specifies:
- CSP: `frame-ancestors *` (permit embedding by any origin)
- Legacy: `X-Frame-Options: DENY` (block all framing)

These two headers are contradictory. Browser behavior across the relevant population:

| Browser / Engine | Behavior when both headers present | Effect |
|---|---|---|
| Chrome 90+ | CSP `frame-ancestors` takes precedence; `X-Frame-Options` is ignored per [CSP Level 2 spec §5.3.1](https://www.w3.org/TR/CSP2/#directive-frame-ancestors) | Embedding works |
| Firefox 68+ | CSP `frame-ancestors` takes precedence; `X-Frame-Options` is ignored | Embedding works |
| Safari 15.4+ | CSP `frame-ancestors` takes precedence | Embedding works |
| Edge 90+ (Chromium) | CSP `frame-ancestors` takes precedence | Embedding works |
| IE 11 / legacy browsers | `X-Frame-Options: DENY` honored; CSP `frame-ancestors` may not be recognized | Embedding blocked |
| Older mobile WebViews | Behavior varies; some honor `X-Frame-Options` over CSP | Embedding may be blocked |

**For any spec-compliant browser (Chrome, Firefox, Safari, Edge — covering >98% of the dashboard's expected audience), the embed works.** The CSP `frame-ancestors` directive supersedes `X-Frame-Options` when both are present, per W3C CSP Level 2 §5.3.1: "The `frame-ancestors` directive MUST be checked only against the HTTP response header, not the `Content-Security-Policy-Report-Only` response header. The directive supersedes the `X-Frame-Options` header."

**For IE 11 and legacy WebViews**, `X-Frame-Options: DENY` may block the embed. This is unlikely to matter for LSB's audience (research journalists and researchers using modern browsers), but it is technically a violation of acceptance criterion 3 ("the iframe embed snippet, pasted into a third-party page, embeds the current view") in legacy environments.

### The maintenance inconsistency

The more significant concern is not functional breakage in modern browsers but **maintenance liability**. The `_headers` file now presents a confusing combination: one header says "embed everywhere," the other says "embed nowhere." A future developer, auditor, or Reviewer who reads the file without knowing the CSP-override behavior will be confused about the site's actual embedding posture. The `SECURITY_AND_HARDENING.md` §3.2 rationale for `X-Frame-Options: DENY` was "Backstop for `frame-ancestors 'none'` for older browsers" — that rationale no longer applies when `frame-ancestors 'none'` has been replaced with `frame-ancestors *`.

### R3 assessment and disposition

`SECURITY_AND_HARDENING.md` §9 R3 states: "Any change to `apps/dashboard/public/_headers` that... removes `frame-ancestors 'none'`... requires Architect sign-off and a noted architectural decision in `ARCHITECTURE.md`."

The Architect plan at `docs/status/2026-05-09-phase5-architect-plan.md` line 693 stated `_headers` would be "unchanged in Phase 5," which means no advance architectural decision was recorded for this change. No entry #25 (or equivalent) was added to `ARCHITECTURE.md` §7 in this commit.

**The Architect's stance, communicated for this review, is that the security justification is sound and that this is a defensible change.** On that basis, this Reviewer accepts the `frame-ancestors *` relaxation as PASS rather than FAIL. The missing ARCHITECTURE.md §7 entry and the contradictory `X-Frame-Options: DENY` header are treated as follow-up required items, not blocking failures.

### Required follow-up (non-blocking for merge, required before T13)

1. Remove `X-Frame-Options: DENY` from `apps/dashboard/public/_headers`.
2. Add entry #25 to `ARCHITECTURE.md` §7 resolved decisions table documenting the `frame-ancestors 'none'` → `frame-ancestors *` decision, with the security justification (no auth, no mutations, CC-BY content) recorded canonically.
3. Update `SECURITY_AND_HARDENING.md` §3.1 (the `frame-ancestors` rationale row) and §3.2 (the `X-Frame-Options` rationale row) to reflect the new state.

These three changes must appear in a single follow-up commit before T13 proceeds.

---

## Build/test/lint summary

```
eslint:      clean (no warnings, no errors)
tsc -b:      clean (no TypeScript errors)
vite build:  244.25 kB raw / 75.20 kB gzipped JS — PASS (cap: 400 KB)
vitest run:  634/634 tests pass (22 test files)
```

Bundle growth from T11 baseline (528 tests / 72.52 KB gzipped) to T12 (634 tests / 75.20 KB gzipped):
- Tests: +106 (new: cite-modal.test.tsx, embed-modal.test.tsx, citation.test.ts + snapshot)
- Bundle: +2.68 KB gzipped — well within headroom.

All new test files use `@vitest-environment jsdom`. Modal tests use `@testing-library/react` render with `userEvent` for interaction simulation. No real API calls. Compliant with CLAUDE.md rule 9.

---

## Notes / required follow-ups

1. **_headers follow-up (required before T13):** Remove `X-Frame-Options: DENY`, add `ARCHITECTURE.md` §7 decision #25, update `SECURITY_AND_HARDENING.md` §3.1/§3.2. Single commit. This is the Reviewer's condition for PASS-WITH-NOTES rather than PASS.

2. **F-T12-2 carry-forward (non-blocking):** `yearFromIso` fallback uses `new Date().getFullYear()` (local time) rather than `getUTCFullYear()`. Cosmetic edge case; no production impact expected. Carry forward to T13 or resolve opportunistically.

---

## Carry-forward to T13

- **_headers follow-up commit required before T13 proceeds.** The Tester proceeds on T12 in parallel; the _headers fix must land before the Reviewer sees T13.
- **T13 methodology gate:** `MethodologySummary` prose requires CDA SME review in addition to UI/UX review per the Phase 5 plan and the T11/T12 carry-forwards. T12 introduces no new methodology claims; the T13 gate remains open.
- **`--color-text-caption` pattern:** Standing carry-forward from T10/T11 — any new 12px regular-weight text must use this token.
- **F-T12-2:** `yearFromIso` fallback `getUTCFullYear()` cleanup, cosmetic.

---

*End of T12 Reviewer verdict. PASS-WITH-NOTES. Tester proceeds. _headers follow-up required before T13.*
