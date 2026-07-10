# UI/UX Verdict: Ops Console Panels 1-3 Templates (T2, T5, T8, T9)

**Date:** 2026-07-10
**Reviewer:** UI/UX agent (persisted by orchestrator; agent session had no write access)
**Scope:** Six new templates under packages/cdb_social/cdb_social/admin_console/templates/ (new_campaign.html, dry_run_plan.html, live_board.html, lane_tail.html, qa.html, dispatch_template.html) plus base.html nav additions.
**Gate scope:** Reduced per the 2026-06-08 internal-ops precedent and Architect plan section 6. Public DESIGN_SYSTEM.md and OWID fidelity not binding. WCAG AA accessibility floor and readable copy only. R10 not applicable. CDA SME copy rules where section 1.5 language could appear.
**Authority:** docs/status/2026-07-10-ops-console-panels123-architect-plan.md section 6.

---

UI/UX VERDICT: PASS-WITH-NOTES

Scorecard (adapted to reduced scope; criteria 1-3 not binding for internal ops):

1. OWID design fidelity:        N/A (internal ops, not public visualization)
2. 30-second journalist:        N/A (internal ops)
3. Researcher cite path:        N/A (internal ops)
4. WCAG AA accessibility floor: PASS-WITH-NOTES

Subchecks:
- Labeled form controls (new_campaign.html):   PASS
- Table headers with scope= (all tables):      PASS
- aria-live on dynamic status affordance:      PASS (dispatch_template.html copy-status span)
- Keyboard operability of copy affordance:     PASS (proper button element + aria-label)
- Focus/contrast sanity (existing stylesheet): PASS-WITH-NOTES (note 2)
- Section 1.5 vocabulary scan:                 PASS (no forbidden terms in template copy)
- Readable copy, boundary labeling:            PASS-WITH-NOTES (required fix 1)
- Tier 1 notice copy:                          PASS

DESIGN_SYSTEM.md update: not required (internal ops).

---

Required before merge:

1. qa.html line 73: the error tooltip pattern (`title="{{ row.error }}"` with display text "error (see title)") is not keyboard accessible (WCAG 2.1.1) and "see title" is HTML jargon (1.3.1). Replace with an accessible inline disclosure: `<details class="bug-note"><summary>error</summary><span>{{ row.error }}</span></details>`.

Notes (not blocking):

2. `.field-note` (color #777 on #fafafa) is roughly 4.3:1 contrast, below the 4.5:1 AA threshold for normal-size text. Pre-existing class across the console; the divergence boundary definition is duplicated in body-weight text so the key information is not lost. Address in a future CSS pass.
3. live_board.html uses `.validation-error` (red-bordered box) for the informational "all cells already complete" state; red signals error to a scanning eye. Low severity; cosmetic.
4. base.html nav lacks aria-label on the nav landmark and aria-current on the active link. Pre-existing across all console pages; not introduced here.

Positive findings: all form controls labeled with for-id pairs or wrapping labels; aria-describedby wired on new_domain and runs_per_cell; captions and th scope attributes on every table; role="alert" on the Tier 1 gate notice; keyboard-accessible copy button with aria-live="polite" feedback and readable clipboard fallback; no section 1.5 forbidden vocabulary anywhere in the six templates; every CSS class referenced is defined in the existing admin.css with no undefined custom properties.

---

## Fix application (orchestrator, 2026-07-10)

Required fix 1 applied: qa.html:73 replaced with the recommended details/summary disclosure pattern; "see title" text removed. Console test suite re-run: 184 passed. Notes 2-4 recorded as future CSS-pass follow-ups, per the verdict's non-blocking designation.
