# CDA SME Verdict: PROMOTE-FOOD-V02 (2026-06-11)

**Task:** PROMOTE-FOOD-V02 — food domain v0.2 promotion with WEAK_CONSENSUS override  
**SME gate:** Round 3 adjudication (food eigenratio CI straddling analysis)  
**Verdict:** PASS-WITH-NOTES

---

## Source

The binding SME adjudication is recorded verbatim in:

`.claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md` (round 3)

This verdict file is the commit-trail reference. The agent-memory file is the canonical ruling.

---

## Binding notes applied by Coder (P1-P8)

| Note | Status | Implementation |
|---|---|---|
| P1: eigenratio CI as constants, not computed | APPLIED | `apps/dashboard/src/copy/consensus_disclosure.ts` inline strings |
| P2: em-dash grep coverage | APPLIED | All new copy files checked; T1h + T2 em-dash suite |
| P3: schema shape (override + reason fields) | APPLIED | `cdb_core/schemas.py` + DATA_DICTIONARY.md v0.1.27 |
| P4: single-commit discipline | APPLIED | One commit per §8 schema-change exception |
| P5: maverick scoping (excluded from similarity basis, present in models list) | APPLIED | `data/results/food/0.2.json`; heatmap exclusion in ContentArea.tsx |
| P6: F3-R3-E placement in MethodologyPage | APPLIED | `apps/dashboard/src/components/MethodologyPage.tsx` id="food-v02-footnote" |
| P7: social drafter carve-out (no social pipeline changes) | APPLIED | No social pipeline touched |
| P8: domain-scoped pattern key in lede.py | APPLIED | `lede.py` `_select_pattern()` checks `domain_slug == "food"` and `analysis_version == "0.2"` |

---

## Five binding strings (F3-R3 series)

| String | Binding | Location |
|---|---|---|
| F3-R3-A (lede) | Verbatim in `lede_v1.py` pattern key; test T1f byte-identical | `packages/cdb_publish/cdb_publish/templates/lede_v1.py` |
| F3-R3-B (override reason) | Verbatim in `data/results/food/0.2.json`; test T1c byte-identical | `data/results/food/0.2.json` `consensus_type_override_reason` |
| F3-R3-C (CI disclosure) | Verbatim in `consensus_disclosure.ts`; test T2a + T2d | `apps/dashboard/src/copy/consensus_disclosure.ts` |
| F3-R3-D (small-n line) | Verbatim in `consensus_disclosure.ts`; test T2b + T2e | `apps/dashboard/src/copy/consensus_disclosure.ts` |
| F3-R3-E (methodology footnote) | Verbatim in MethodologyPage.tsx; test T2f | `apps/dashboard/src/components/MethodologyPage.tsx` |

Any edit to any of the five strings requires a fresh CDA SME pass.
