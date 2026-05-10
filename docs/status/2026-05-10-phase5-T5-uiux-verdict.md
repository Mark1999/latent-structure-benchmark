# UI/UX Per-Commit Verdict — Phase 5 T5

**Filed:** 2026-05-10
**Reviewer:** UI/UX agent (Sonnet)
**Commit reviewed:** `eae4da5` (T5 DomainPicker + KeyFinding)
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** v0.4.1 (unchanged — all T5 visual decisions were already specified)

---

## VERDICT: PASS

| Question | Result |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS |
| 4. WCAG AA accessibility | PASS |

**DESIGN_SYSTEM.md update:** not required. All T5 visual decisions are covered by v0.4.1 — every binding specification has a clear source location. No new visual decisions surfaced.

T5 proceeds cleanly to Reviewer + Tester with no rework or carry-forward corrections.

---

## Criterion 1 — OWID design fidelity

**DomainPicker** (per §2.3):
- Pill layout uses `gap: var(--space-3)` (12px). Active pill uses blue background fill + `font-weight-bold` (two non-color active indicators). Disabled pills use `--color-text-muted` + `cursor: not-allowed`. `flex-wrap: wrap` for §8 mobile two-line wrap. All token references; no hardcoded values.

**KeyFinding** (per §3.8):
- `border-left: 4px solid var(--color-model-1)` ✓
- `max-width: var(--max-article-width)` (780px) ✓
- `padding: var(--space-6) var(--space-8)` (24px 32px) ✓
- Lato 20px, weight 500 ✓
- `background-color: var(--color-surface)` ✓

**200ms KeyFinding fade** (§3.8 binding):
- `animation: keyFindingFade 200ms ease-out forwards`
- `prefers-reduced-motion: reduce` override sets `animation: none; opacity: 1`
- Key-change remount strategy: old element disappears, new fades in; correct behavior for a never-stale lede

**Reveal cascade** (§12.1 carry-forward from T4):
- DomainPicker and KeyFinding wrapped in `reveal-cascade-item`
- 280ms duration + 320ms max delay = 600ms total cap preserved
- T4's animation-duration correction is intact

---

## Criterion 2 — 30-second journalist test

**Active domain clarity:** filled blue background + bold white text on active pill — unambiguous at a glance.

**Disabled pill reading:** muted text + not-allowed cursor + "Coming in a future update" tooltip — communicates "planned but not available" without exposing internal phase numbering.

**Family lede:** "Across 11 frontier models, family vocabulary is organized around a single shared categorical structure (Smith's S = 0.71, 95% CI [0.50, 0.91]). The map below shows where each model sits relative to that consensus..." — quotable, declarative, descriptive, not advocacy tone.

**Holidays lede:** Surfaces the OCI low-concentration finding for 2 of 9 models as a first-class observation. Per the §3.3.5 register framework. Well-handled.

---

## Criterion 3 — Researcher reproduce-and-cite

**Smith's S with CI in both ledes:** family `0.71, 95% CI [0.50, 0.91]`; holidays `0.78, 95% CI [0.47, 0.96]`. Uncertainty in the lede text itself; researcher gets the key statistic + CI without further interaction.

**Model-to-model framing:** Neither lede uses human comparison framing or references a baseline / "ground truth" / "closer to human." Correct per the 2026-05-07 amendment and §1.5.5.

**No forbidden vocabulary in rendered ledes:** Grep across `apps/dashboard/public/data/` for §1.5.4 + CLAUDE.md §7 phrases — zero hits. Lede uses permitted vocabulary: "organized around," "categorical structure," "output concentration," "runs did not converge."

---

## Criterion 4 — WCAG AA

**T4 carry-forward — disabled pills focusable** (§12.3): `tabIndex={0}` unconditional on all pills (DomainPicker.tsx:105). `aria-disabled="true"` on disabled pills (line 101). Test asserts `foodPill.tabIndex !== -1` (domain-picker.test.tsx:117–123). PASS.

**T4 carry-forward — tooltip text exact match** (§12.3): `title="Coming in a future update"` byte-exact on disabled pills (DomainPicker.tsx:106). Test asserts byte-exact at line 249. No "Phase 6," no "coming soon," no version-specific language. PASS.

**DomainPicker ARIA structure:** Container `role="tablist"` with `aria-label="Domain selection"`. Each pill `role="tab"`, `aria-selected`, `aria-label` with state text ("currently displayed" / "switch to view" / "coming in a future update"). Per §7.

**KeyFinding ARIA structure:** `<section role="region" aria-label="Key finding">` (KeyFinding.tsx:36–38). Inner `<p aria-live="polite">` (line 49). Screen readers announce new lede on domain switch without navigation.

**Keyboard navigation:** ArrowLeft/ArrowRight move focus with wrap-around. Enter/Space activate available pills; suppressed on disabled. Comprehensive coverage at domain-picker.test.tsx:162–241.

**Focus indicators:** `outline: 2px solid var(--color-info)` on `:focus-visible`. Never `outline: none` without replacement.

**Active pill contrast:** White on `--color-info` (#3360a9) — ~7.2:1, well above WCAG AA 4.5:1.

**Disabled pill text contrast:** `--color-text-muted` (#bdc3c7) on white — ~1.5:1. WCAG 1.4.3 explicitly exempts disabled components from contrast requirements; intended visual treatment for discoverable-but-inactive affordance.

**Slot 11 corrected value confirmed:** `tokens.css:92` is `#9a7d0a` (3.96:1 contrast). T4 correction intact.

---

## Specific binding verifications (all PASS)

| Binding | Location | Status |
|---|---|---|
| 200ms KeyFinding fade | `app.css:419` — `200ms ease-out` | ✓ |
| `prefers-reduced-motion` override on fade | `app.css:432–437` | ✓ |
| Disabled pills `tabIndex={0}` (not -1) | `DomainPicker.tsx:105` | ✓ |
| `aria-disabled="true"` on disabled pills | `DomainPicker.tsx:101` | ✓ |
| Tooltip text exact: "Coming in a future update" | `DomainPicker.tsx:106` | ✓ |
| §3.8: 4px `--color-model-1` border-left | `app.css:410` | ✓ |
| §3.8: max-width 780px | `app.css:403` → `tokens.css:149` | ✓ |
| §3.8: padding 24px 32px | `app.css:411` | ✓ |
| §3.8: Lato 20px weight 500 | `app.css:413–414` | ✓ |
| §2.3: `--space-3` gap | `app.css:333` | ✓ |
| §2.3: active pill non-color indicator | `app.css:365` (bold + fill) | ✓ |
| §12.1: cascade 600ms cap preserved | 280ms + 320ms = 600ms | ✓ |
| §12.3: no "Phase 6" in user-visible copy | grep across `src/` — zero hits | ✓ |
| `_headers` `frame-ancestors 'none'` unchanged | `public/_headers:9` intact | ✓ |
| Forbidden vocabulary in components | grep — zero hits | ✓ |
| Forbidden vocabulary in published ledes | grep `public/data/` — zero hits | ✓ |
| Smith's S + CI in both ledes | `family.json`, `holidays.json` | ✓ |

---

## Non-blocking observations for carry-forward

**F-T5-1 (carry-forward to T6):** The KeyFinding's `reveal-cascade-item` wrapper is `:nth-child(1)` within its parent (`.content-area`), getting 0ms delay — appropriate post-domain-fetch render. T6 will add the DataExplorer beneath; verify no child reaches `:nth-child(6)+` since the stagger spec only covers up to `:nth-child(5)` (320ms). Current T5 layout is within bounds.

**F-T5-2 (carry-forward to T13):** `#cite` anchor target unresolved (CiteModal is T11). Status unchanged from T4.

**F-T5-3 (carry-forward to T13):** `<title>` tag is static in T5; domain-specific title updates are a T13 integration concern. Per §12.5, embed mode requires a descriptive `<title>` — not blocking T5.

---

## Required before merge

None. All four criteria PASS. All carry-forward bindings from T4 verified. T5 proceeds to Reviewer + Tester.

---

*End of T5 per-commit UI/UX verdict. Posted to `#lsb-ui-ux`.*
