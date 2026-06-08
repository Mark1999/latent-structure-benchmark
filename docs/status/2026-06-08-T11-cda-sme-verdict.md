# T11 — OCI low-concentration threshold single-source-of-truth de-duplication — CDA SME verdict (2026-06-08)

**Scope:** Low-touch methodological confirm. T11 consolidates three `3.0`
literals of the OCI R1-a / R1-b boundary. T11a points
`scripts/rebaseline_corpus.py:82` at the canonical
`cdb_publish.lede.OCI_LOW_CONCENTRATION_THRESHOLD`; T11b adds a vitest drift
guard binding `apps/dashboard/src/config/analysis.ts:10` to the published
manifest field. Value remains `3.0` everywhere. No classification logic,
lede template, or published-copy change.

**Posture:** The Architect explicitly framed this as a four-point ratify,
not a four-axis re-derivation. Treating it as such; no four-axis scorecard
below. Verdict applies to the framing only — the implementation must still
pass Reviewer + Tester.

## Verdict on the four Architect §4 points

**Point 1 — `3.0` remains the canonical R1-a / R1-b boundary; no value
change anywhere → PASS.**
Confirmed by inspection at `cdb_publish/lede.py:40`,
`scripts/rebaseline_corpus.py:82`, and `apps/dashboard/src/config/analysis.ts:10`
— all three currently equal `3.0`. The Architect plan §2 deletes the
rebaseline literal in favor of an import (no arithmetic on the value);
§3 leaves `analysis.ts` and `manifest.json` untouched. The value `3.0` is
preserved in DESIGN_SYSTEM.md §3.3.5 (R1-a vs R1-b table row),
ARCHITECTURE.md / `docs/SME_REVIEW.md` open question 1, and BOOTSTRAP_DESIGN
§ on R1 thresholds. The provisional-pending-Phase-4b annotation in §3.3.5
remains the canonical doctrinal posture — T11 does not relitigate it; it
merely makes the literal harder to drift.

**Point 2 — De-duplication does not alter R1 classification semantics →
PASS.**
The sole classification site is `cdb_publish/derived.py:34 r1_state_for`,
which already imports `OCI_LOW_CONCENTRATION_THRESHOLD` from
`cdb_publish.lede` (line 20) and uses strict less-than at line 54
(`if within.oci < OCI_LOW_CONCENTRATION_THRESHOLD`). T11 does not touch
this file. The T-4 rebaseline threshold-crossing guard at
`scripts/rebaseline_corpus.py:219–220` uses
`prior_oci >= OCI_LOW_CONCENTRATION_THRESHOLD` /
`new_oci >= OCI_LOW_CONCENTRATION_THRESHOLD`; after T11a it reads the same
value from the imported constant rather than a local literal of the same
value, so the predicate's truth set is bit-identical. Reviewer §7 emphasis
("T-4 guard behavior intact") aligns with this.

A note on the R1-a / R1-b boundary semantics: `derived.r1_state_for` is
strict `<` (oci exactly == 3.0 → "typical_concentration"); the T-4 guard is
`>=` (oci exactly == 3.0 → "non-low" side). These two predicates use
opposite inequalities and have always done so — this is correct (the
classifier defines membership in R1-b, the rebaseline guard defines
membership in the non-R1-b side for crossing detection). T11 preserves
both. Not a methodological concern; flagged here only so the Tester is not
surprised if the boundary-test at oci == 3.0 partitions one direction and
the rebaseline guard the other.

**Point 3 — No lede or published-copy change → PASS.**
`cdb_publish/templates/lede_v1.py` patterns are unchanged. The lede
generator at `cdb_publish/lede.py:71` uses the constant identically before
and after T11. The published manifest field
`oci_low_concentration_threshold` at `cdb_publish/schemas/manifest.py:50`
is unchanged in both type and serialized value. The dashboard does not
render the threshold value in any user-visible copy (DESIGN_SYSTEM §3.3.5
item 4 explicitly forbids hard-coding the value in copy; the methodology-
page injection mentioned in the Architect plan §3 is not implemented and
remains out of T11 scope). No risk of audience-facing surface drift.

**Point 4 — `cdb_publish.lede.OCI_LOW_CONCENTRATION_THRESHOLD` remains the
documented Python source of truth; `analysis.ts` remains the dashboard's
named SoT per DESIGN_SYSTEM §3.3.5 item 7; the two bound by the manifest
publication + the new drift guard → PASS.**
DESIGN_SYSTEM §3.3.5 already documents `analysis.ts` as the dashboard's
config home (the v0.3 changelog entry on line 40 cites it explicitly:
"OCI low-concentration threshold config constant location specified at
`apps/dashboard/src/config/analysis.ts`"). `lede.py:37–40`'s docstring
documents itself as the Python SoT and names `analysis.ts` as the parallel
dashboard SoT. After T11a, the Python side has exactly one `3.0` literal
for this threshold (lede.py:40); after T11b, the dashboard side is bound
to the Python side via the published manifest field and the new vitest
guard. The two-named-SoT-with-binding-test posture is preserved, not
demoted.

## Concurrence note: Option (b) (keep analysis.ts + drift guard) over Option (a) (dashboard reads manifest at runtime)

**Concur with Option (b), with one methodological observation that does
not change the recommendation.**

Engineering rationale for (b) is sound: the TS constant has no current
consumers (Architect §1 Correction B), the manifest field is currently
dead, the dashboard renders the backend-computed `r1_state` literal rather
than re-deriving R1-state client-side, and DESIGN_SYSTEM §3.3.5 already
binds `analysis.ts` as the named SoT. Option (a) would invent scope and
require a DESIGN_SYSTEM amendment routed through UI/UX.

**The one methodological observation (advisory, not blocking):**
DESIGN_SYSTEM §3.3.5 item 4 says the threshold is provisional and "the
dashboard should read it from a config constant so tuning after Phase 4b
doesn't require a UI code change." If a future methodology-page disclosure
ever surfaces the literal `3.0` to the reader (the Architect plan §3 notes
the §3.3.5 mention of this as backlog), the value needs to flow from the
Python SoT to the rendered text without a dashboard code edit. At that
point, Option (a) (manifest runtime read) becomes the right answer —
exactly as the Architect notes. T11 is not that moment; the dead manifest
field becomes load-bearing under T11b's drift guard, and a future
methodology-page T-task will be the one that promotes manifest-runtime-read
to the rendering path. No methodological reason for the threshold to flow
to the client at runtime *today*.

This observation is a backlog signal, not a T11 blocker.

## Vocabulary scan

Clean. No forbidden vocabulary in the Architect plan. No new generated
text in the implementation. The constant name and the docstrings use
"concentration" / "OCI" / "Register 1" / "R1-a / R1-b" terminology
consistent with ARCHITECTURE.md §4.2.0 and DESIGN_SYSTEM §3.3.5.

## Register compliance

OCI remains an R1 (within-model) concentration statistic. T11 does not
move it to R2 or relabel it. `derived.r1_state_for` continues to classify
into R1-a / R1-b / R1-c per §3.3.5. No register drift.

## Summary

```
CDA SME VERDICT: PASS

Point 1 — 3.0 remains canonical boundary, no value change:   PASS
Point 2 — R1 classification semantics unchanged:             PASS
Point 3 — No lede or published-copy change:                  PASS
Point 4 — Documented two-named-SoT posture preserved:        PASS

Option (b) vs (a):   concur with (b); (a) is a future methodology-page-
                     disclosure-time decision, not a T11 decision.
```

Proceed to Coder. No required-before-merge items from CDA SME.
