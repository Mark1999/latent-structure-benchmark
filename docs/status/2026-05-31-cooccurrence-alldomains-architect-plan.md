# Architect Plan — cooccurrence files for all domains (term map blank on holidays/food)

**Bug:** TermMap fetches `/data/{domain}-cooccurrence.json` per domain; only family's exists → holidays + food term maps render BLANK (verified: family 100 dots, holidays 0, food 0). Predates food promotion. No `build_cooccurrence.py`; publish.py never emitted these; family's was a 2026-05-25 one-off.

**Ruling:** publish-format/plumbing, NOT new methodology (cooccurrence+MDS approved at Phase 9a). CDA SME advisory only.

## Tasks
- **T1** — add `{domain}-cooccurrence.json` emission to `scripts/publish.py` for ALL published domains, sourced from the same pile-sort data the analysis already uses (reuse `cdb_analyze/cooccurrence.py`, do not hand-roll). Match the exact shape of the existing `family-cooccurrence.json` (`{items[], models{model_id: ModelPileData}, domain, n_models}`) — read `apps/dashboard/src/lib/cooccurrence.ts` + TermMap's CooccurrenceData/ModelPileData interfaces. Gate: Reviewer + Tester (+ SME advisory).
- **T2** — run publish.py, commit the 3 files, browser-verify all 3 term maps render (family unchanged 100 dots; holidays + food now non-zero). Gate: Reviewer + UI/UX browser check.

## Bundling
Food promotion commit `6d96ebd` (unpushed at HEAD) published food's term_mds data but its map is blank without the cooccurrence file. **Ship together** — land T1+T2 on top of 6d96ebd, verify all 3 render, push the whole set. Do NOT push 6d96ebd alone (would put a blank promoted food map live).

## Decisions (Mark)
1. SME advisory check that generated cooccurrence pooling matches the approved definition the backend term_mds was computed from (cheap consistency insurance) — yes/no.
2. Family: accept semantic-equivalence (same items+piles, reordering OK) vs require byte-identity (infeasible). Rec: semantic-equivalence; STOP if substantively different.
3. Generic emission over all published domains (not hardcode 3). Rec: yes.

Architect recommends: SME advisory YES, semantic-equivalence YES, generic YES.
