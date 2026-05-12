---
filed: 2026-05-12
reviewer: UI/UX agent (Sonnet)
plan_reviewed: docs/status/2026-05-12-phase6-T0-architect-plan.md
cda_sme_upstream: not required (T0 is schema-quiet, no methodology surface)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.4 (no update required — inspect page is an ops surface with no §11 inventory entry)
verdict: PASS-WITH-NOTES
---

# UI/UX Plan-Level Verdict — Phase 6 T0 (Operator Inspection Mode)

**VERDICT: PASS-WITH-NOTES**

Review posture: light-touch per `feedback_ui_polish_scope.md`. Four criteria only: accessibility floor, R10 pairing, token consistency, WCAG AA contrast. No aesthetic critique, no OWID fidelity gating, no journalist/cite-path gating.

| Criterion | Result |
|---|---|
| 1. Accessibility floor | PASS-WITH-NOTES |
| 2. R10 pairing | PASS |
| 3. Token consistency | PASS-WITH-NOTES |
| 4. WCAG AA contrast | PASS-WITH-NOTES |

T0 is approved for Coder dispatch. Four binding implementation notes below must be applied during implementation; they do not require plan revision.

---

## 1. Accessibility floor — PASS-WITH-NOTES

**What the plan specifies correctly:**

- Every `<table>` is rendered by `InspectTable`, which requires a `caption: string` prop and renders `<caption>{caption}</caption>` as its first child (§2.3). WCAG 2.0 SC 1.3.1 caption requirement: satisfied at the plan level.
- Every `<th>` in `InspectTable` renders with `scope="col"` (§2.3 explicit). Satisfied.
- Single `<h1>`: `InspectRoot` renders exactly one `<h1>` ("LSB published-data inspection") in the sticky header (§2.3). No other component in the inspect surface renders a heading above `<h2>`. Satisfied.
- Heading order H1 → H2: `InspectSection` renders `<h2>` as the only heading element it produces, and every section passes through `InspectSection`. No `<h3>` or lower-level headings are used in the plan. Satisfied.
- `<meta name="robots" content="noindex">` lifecycle: `InspectRoot` injects via `useEffect` on mount and removes on unmount (§2.2, §10 risk 3). Correctly specified.

**Binding implementation note F-T0-A1:** `InspectSection` generates an `id` from its `title` prop to wire `<section aria-labelledby={id}>` to `<h2 id={id}>`. The plan does not specify how `id` is generated. The Coder must ensure:

1. The id is derived from the title as a valid HTML id (no spaces, lowercase, alphanumeric + hyphens; e.g. `title.toLowerCase().replace(/\s+/g, '-')`).
2. All section titles within a single inspect-mode page view are unique so no duplicate `id` attributes exist in the DOM.

---

## 2. R10 pairing — PASS

All point-estimate / CI pairs are explicitly specified adjacent in §2.4:

- **MDS coordinates + ellipse parameters:** §2.4 "MDS uncertainty (bootstrap ellipses)" table specified immediately after "MDS coordinates" table.
- **Similarity matrix + similarity_ci:** §2.4 specifies "Similarity confidence intervals" table "rendered immediately under the similarity matrix."
- **Consensus score + consensus_ci:** §2.4 places `consensus_score` and `consensus_ci` in a single "Consensus" 2-column scalar table.
- **OCI + oci_ci:** §2.4 specifies `oci` and `oci_ci` as adjacent columns in the within_model_results table.

No bare point estimates without adjacent CI rendering exist in the specified field coverage.

---

## 3. Token consistency — PASS-WITH-NOTES

**Binding implementation note F-T0-B1:** §2.2 references `--color-bg-surface` as an existing token. This token does not exist in `apps/dashboard/src/styles/tokens.css`. The correct token for card/panel backgrounds is `--color-surface` (#f8f9fa). The Coder must use `--color-surface`, not `--color-bg-surface`.

**Binding implementation note F-T0-B2:** §2.2 and §2.3 reference `--font-family-mono` as an existing token. This token does not exist in `tokens.css`. The correct token is `--font-mono` (defined at `tokens.css` line 55 as `'JetBrains Mono', monospace`).

---

## 4. WCAG AA contrast — PASS-WITH-NOTES

**Primary text combinations (PASS):** `--color-text-primary` (#2c3e50) against `--color-surface` (#f8f9fa) is ~10.8:1. Against `--color-background` (#ffffff) it is ~11.5:1. Both pass.

**Binding implementation note F-T0-C1:** The plan states loading/error strings render "matching the §12.2 pattern." The §12.2 pattern uses `--color-text-muted` (#bdc3c7, ~1.75:1 on white) and `--color-text-secondary` (#7f8c8d, ~3.40:1) — both fail WCAG AA for body text. This is a pre-existing design-system issue in §12.2 that was not corrected in Phase 5.

The inspect page is an operator surface where readable status text is functionally important. The Coder must NOT inherit the §12.2 pattern verbatim for inspect-page loading/error strings. Instead, use `--color-text-caption` (#6c757d, ~4.60:1 on white — WCAG AA pass) for both "Loading..." and "Could not load." strings in `InspectRoot.tsx`. This overrides §12.2 for the inspect surface only.

---

## Findings table

| ID | Severity | File | Issue | Required correction |
|---|---|---|---|---|
| F-T0-A1 | PASS-WITH-NOTES | `InspectSection.tsx` | `id` generation for `aria-labelledby` not specified | Coder derives id from title as `title.toLowerCase().replace(/\s+/g, '-')` (or equivalent slug); verifies uniqueness |
| F-T0-B1 | BINDING | `inspect.css` + components | `--color-bg-surface` does not exist in `tokens.css` | Use `--color-surface` (#f8f9fa) |
| F-T0-B2 | BINDING | `inspect.css` + `InspectTable.tsx` | `--font-family-mono` does not exist in `tokens.css` | Use `--font-mono` |
| F-T0-C1 | BINDING | `InspectRoot.tsx` | Loading/error strings inherit §12.2 pattern which uses tokens that fail WCAG AA | Use `--color-text-caption` (#6c757d, ~4.60:1) for both states |

Severity legend: BINDING = must apply before commit; PASS-WITH-NOTES = apply during implementation but does not block plan approval.

---

## DESIGN_SYSTEM.md update

**Not required.** The inspect page is an operator surface, not a public component. Three new components (`InspectRoot`, `InspectSection`, `InspectTable`) are ops-internal and do not warrant a §11 entry. No visual decisions are introduced that require a design-system update; all tokens used are existing. DESIGN_SYSTEM.md remains at v0.4.4.

---

## Escalation items for Mark

None. No plan-level decisions require Mark's eyes before Coder dispatch. The four notes above are implementation-level corrections that the Coder applies without further gate review.

---

*Posted to #lsb-ui-ux. Coder may proceed on receipt of this verdict.*
