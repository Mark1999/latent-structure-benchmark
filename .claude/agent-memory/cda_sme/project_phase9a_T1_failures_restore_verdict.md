---
name: phase9a-T1-failures-restore-verdict
description: 2026-06-08 PASS-WITH-NOTES re-affirmation of T9/T10 framing under top-level-tab placement change. framing_note byte-identical in both family.json and food.json; M1-M4 binding (tab label, page heading, domain selector, no Explore-chrome leak).
metadata:
  type: project
---

Phase 9a T1 restored the failures-as-findings surface dropped by the 2026-05-25
rebuild, under Mark's 2026-06-08 directive moving the surface from a bottom-of-
article H2 sibling of MethodologySummary (T10) to a top-level NavBar tab + own
domain selector.

**Verdict:** PASS-WITH-NOTES. This was a re-affirmation only, not a re-litigation
of T9/T10. All seven T10 binding strings + S1-S7 carry-forward + the T9 §5.1
framing_note verbatim contract remain in force.

**framing_note byte-identity check (2026-06-08):** `family.json` and `food.json`
both carry the T9 §5.1 verbatim string. AC5 byte-identity vitest assertion is
correct.

**M1-M4 binding additions for the placement change:**
- M1: NavBar tab label is `"Collection records"` (preferred) or `"Failures"`
  (acceptable only with M2 expansion to full T10 SECTION_HEADING at page heading).
- M2: Page heading inside the Failures tab is the T10 SECTION_HEADING string
  `"Collection records and follow-up interviews"` byte-for-byte; HTML element
  level (`<h1>` vs `<h2>`) is UI/UX call.
- M3: Domain selector label uses existing picker label OR one of `"Domain"` /
  `"Show records for"` / `"Domain shown"`. Forbidden: `"Show failures from"`,
  `"Models that failed in"`, `"Refusals in"`, `"Where models declined"`.
- M4: Failures tab renders ONLY: page heading, framing_note paragraph, domain
  selector, counts caption, records list / empty-state. NO chart-lede / Smith's-S /
  consensus / category-map strings leak from Explore tab. Chrome regression-grep
  test for `consensus|Smith's S|agree|believe|think|worldview`.

**Why:** standalone NavBar tab arguably tightens §1.5.6 (failures are first-class
evidence parallel to Explore / Methodology / Data, not nested inside an article
view). Framing risk that "Failures" tab reads as "models failing" rather than
"LSB pipeline output distribution includes non-parseable responses" is real but
addressable via M1+M2 at the chrome layer; framing_note paragraph is the primary
defense.

**How to apply:** when reviewing the Coder's commit, verify (1) tab label
chosen per M1; (2) page heading matches M2 string byte-for-byte; (3) domain
selector label per M3; (4) chrome regression-grep test from M4 present and
passing. All T10 binding strings (badge labels "Collection failure"/"Follow-up
interview", block labels "Follow-up prompt LSB sent"/"Model output to the
follow-up prompt"/"Provenance IDs", empty-state caption S2 verbatim) unchanged.

**No new T14 doc-sweep flag.** Existing T9 §5.2 + T10 S3 + T10 S7 methodology-
page-link flags remain open and are unaffected by the placement change.

**No `cdb_core/schemas.py` change.** No Mark escalation required.

See [[phase6_T9_failures_publish_verdict]] and [[phase6_T10_failures_ui_verdict]]
for the originating binding strings + the seven binding constraints that carry
forward verbatim.
