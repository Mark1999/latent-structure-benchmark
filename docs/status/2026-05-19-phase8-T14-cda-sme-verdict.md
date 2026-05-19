# CDA SME Verdict — Phase 8 T14 (`ARCHITECTURE.md` §6.6 doc-fix)

**Date:** 2026-05-19
**Reviewer:** CDA SME (external)
**Scope:** Architect's proposed replacement wording for `ARCHITECTURE.md` §6.6
licensing surface (Edits 1–5), aligning §6.6 with the 2026-05-07 §1.5.5
amendment and the SME-approved HF card + bundle README.
**Precedent:** T7.1 verdict (final paragraph) flagged this carry-forward.

---

## CDA SME VERDICT: PASS

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity     | PASS |
| Axis 2 — Analytical validity   | PASS |
| Axis 3 — Claims validity       | PASS |
| Axis 4 — Audience translation  | PASS |
| Register compliance            | N/A (licensing surface) |
| Vocabulary compliance          | PASS |

---

## Four-axis scorecard

**Axis 1 — Protocol validity.** The replacement text correctly describes the
v1 distribution posture established by §1.5.5: human grounding is removed
from v1, `data/grounding/family/` is retained for audit-trail completeness
only, no v1 surface (bundle / dashboard / HF card / Zenodo) injects it as a
baseline. Edit 3's enumeration of the four non-consumption surfaces matches
§1.5.5 (L182–190) and the `data/grounding/README.md` historical banner verbatim
in posture. No protocol concern.

**Axis 2 — Analytical validity.** Artifact references are correct.
`data/grounding/family/romney_1996/` is the right subpath for the CC-BY
conditional in Edit 3. `data/open_bundle/huggingface_dataset_card.md` is the
right card location for Edit 4. License files block at L1573–L1578 is
correctly preserved unchanged. Edit 5's "HF dataset IS the bundle artifact"
matches the SME-approved card YAML (`license: cc0-1.0`, L2) and supersedes
the stale "retaining the CC-BY-4.0 designation" language at the old L1606.

**Axis 3 — Claims validity.** Forbidden-vocab scan across all five edits
clean: no `worldview`, `believes`, `thinks`, `within-model consensus`,
`closer to human`, `publishable`. §1.5.5 pitfalls correctly avoided — no
"no human baseline available yet" framing, no "interim state pending"
language. Edit 3 frames the directory's status as a permanent v1 posture
(retained for reproducibility / audit), not a deferred-arrival state.
"Methodological forebears" mirrors the SME-approved bundle README L33 and
HF card L33 phrasing exactly. Romney as ancestry credit, not as bundled
data — the correct doctrinal posture.

**Axis 4 — Audience translation.** A researcher reading §6.6 cold gets the
full posture without needing §1.5.5 context, while still being pointed to
§1.5.5 and the originating amendment plan. Edit 3 is the longest of the
five but the verbosity is load-bearing: the four-surface enumeration
(bundle / dashboard / HF / Zenodo) and the CC-BY conditional clause are
both information that §6.6 readers will not get elsewhere in the licensing
section. Edit 4 cleanly removes the contradiction with the HF card.
Edit 5 closes the §6.7 mirror-licensing inconsistency.

---

## Per-decision rulings

**1. Romney paragraph posture ("historical reference data").** PASS.
"Historical reference data" is the right framing — matches
`data/grounding/README.md` L1 verbatim ("Historical reference data only.")
and is doctrinally accurate (the data is preserved, not archived-and-
removed; "reference" carries the methodological-citation connotation that
"archival" loses). Reject "archival reference" (implies write-once / cold
storage, which doesn't match the live `data/grounding/family/` directory)
and reject "audit-trail reference" (narrower than the actual posture; the
directory also serves reproducibility of any future researcher who wants
to re-run the historical baseline analysis externally).

**2. Verbosity of Edit 3.** PASS as drafted. The four-surface enumeration
and the CC-BY-redistribution conditional are both load-bearing — they tell
the §6.6 reader things they will not learn from a cross-link to §1.5.5
(which is framing, not distribution-surface accounting). Cross-link is
already present ("Per the 2026-05-07 §1.5.5 amendment"); further compression
would lose the licensing-section operational content.

**3. Forbidden-vocabulary scan.** PASS. All five edits clean against the
§7 / §1.5.4 table and against the §1.5.5-amendment pitfalls (§1.5
forbidden-text scan + §1.5.5 "no human baseline available yet" /
"interim state" patterns).

**4. `DESIGN_SYSTEM.md §6.1 item 2` cross-link.** PASS — verified.
`DESIGN_SYSTEM.md` L489 begins §6.1 ("Page Structure"); L496–500 is item 2
("What is Cultural Domain Analysis?"), which explicitly names
"Romney, D'Andrade, Weller, Borgatti: named and cited" at L498. The anchor
exists and is the correct target.

**5. CC-BY-4.0 conditional clause posture.** PASS as drafted. "Applies to
anyone who chooses to redistribute the historical reference files" is the
doctrinally correct phrasing. LSB itself does not redistribute Romney 1996
data in any v1 artifact (Edit 3's final sentence), so a clause naming "LSB
if LSB ever resumes distribution" would be hypothetical-future framing that
muddies the present-tense v1 posture. The current phrasing addresses the
real legal surface — third-party redistributors of the directory — without
pre-committing LSB to any v2 / resumption decision.

---

## Required before merge

None. PASS as drafted. Coder may apply Edits 1–5 verbatim.

---

## Notes for the Coder (non-binding)

- Edit 2 changelog entry references `docs/status/2026-05-19-phase8-T7.1-cda-sme-verdict.md`
  and `docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md`.
  Verify both paths resolve before commit (the T7.1 path is confirmed extant;
  the 2026-05-07 amendment plan path should be confirmed by `ls`).
- After the Coder applies Edits 1–5, no fresh CDA SME pass is required on
  the regenerated §6.6 markdown — this verdict covers the wording verbatim
  as proposed. If the Coder deviates from the proposed text in any
  non-trivial way (anything beyond whitespace / line-wrapping), route back
  for a second pass.
- T14 carry-forward from T7.1 is hereby satisfied at the verdict level;
  the carry-forward closes once the commit lands.

---

*End of T14 doc-fix verdict.*
