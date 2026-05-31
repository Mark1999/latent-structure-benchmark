# CDA SME Verdict — Food Domain Re-baseline Promotion (2026-05-31)

**Date:** 2026-05-31
**Scope:** Promotion of the 2026-05-29 re-baselined food domain JSON (`out/rebaseline/food/0.2.json`, sha256 `3330f8fa…`, computed under pinned NumPy 2.4.4 / SciPy 1.17.1 / Python 3.12) to live (`data/results/food/0.2.json` + `apps/dashboard/public/data/food.json`), including matching `provenance.json` `domains` entry, footer auto-enablement on the food domain page, and methodology-paragraph scope amendment.

**Defers from:** `docs/status/2026-05-30-promote2-cda-sme-verdict.md` §4 (PROMOTE-2 explicitly deferred food because its staged file is not a pure drift-only change — it adds 12 populated structural keys [term-MDS, centroid_piles, cluster labels, ellipses, BP values] that did not exist in the published 0.2 and therefore could not be blessed under the rounding-level rationale).

**Companion docs:** `docs/status/2026-05-29-rebaseline-cda-sme-verdict.md` (T-1..T-6 threshold guards; T-3 food is the load-bearing one — eigenratio 6.586 above 5.0 boundary), `docs/status/2026-05-24-phase9a-cda-sme-verdict.md` (M4/M5 — the bootstrap functions producing the term-MDS uncertainty under review here), `docs/BOOTSTRAP_DESIGN.md` (Option 2 annotated uncertainty contract), `ARCHITECTURE.md` §4.5 (R10 uncertainty-display rule), `out/rebaseline/baseline_manifest.json`, `out/rebaseline/food/0.2.json`.

**Routing:** This verdict gates the food promotion commit. Reviewer gates the test/file diff against this verdict's authorized list and against the PROMOTE-2 contract for `provenance.json` + footer wiring (B4/B5 of PROMOTE-2 now invert their food carve-outs).

---

## Verdict: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| 1 — Protocol validity | PASS |
| 2 — Analytical validity | PASS |
| 3 — Claims validity | PASS-WITH-NOTES |
| 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

The PASS-WITH-NOTES axes carry forward N1–N3 (2026-05-29 rebaseline) and A/B series (PROMOTE-1/PROMOTE-2). No new methodological objection. Notes C1–C5 below operationalize the food-specific binding requirements: the methodology paragraph and `provenance.json` scope, the food domain-page footer auto-enablement, the small-n disclosure on the new term-level viz, the term-MDS stress trustworthiness posture, and the audit-trail closure of the food deferral.

---

## §1 — Question 1: Is publishing food's now-populated term-level data methodologically sound?

**Ruling: YES. APPROVED. No new method; this is "food gets the viz it should always have had."**

### Code-path identity vs family/holidays (verified)

The term-level fields populated in `out/rebaseline/food/0.2.json` are produced by the *identical* code path that family and holidays already use in their live published files:

| Field | Producing function | CDA SME approval lineage |
|---|---|---|
| `term_mds_coordinates`, `term_mds_items` | `pipeline.py` §2e (pooled cross-model MDS on item co-occurrence) | Phase 9a M1–M3 (`2026-05-24-phase9a-cda-sme-verdict.md`) |
| `term_mds_uncertainty` (per-term ellipses) | `bootstrap_term_mds_ellipses(per_model_matrices, …, n_bootstrap=200, random_state=42)` at `pipeline.py:686` | Phase 9a M4: model-resample bootstrap (Register 2 informants), B=200, reference-aligned via Procrustes |
| `term_cluster_assignments`, `term_cluster_labels`, `term_cluster_linkage` | UPGMA hierarchical clustering on 1-cooccurrence with modal pile-label assignment | Phase 9a M1 (UPGMA not Ward), M2 (1-cooccurrence not 1-similarity), modal pile-label per `phase9a` ruling |
| `term_cluster_bp_values` (branch-probability per internal node) | `bootstrap_branch_stability(per_model_matrices, reference_linkage, …, n_bootstrap=200, random_state=42)` at `pipeline.py:714` | Phase 9a M5: BP not AU, model-resample bootstrap |
| `centroid_piles` | per-model centroid-run pile assignment | Phase 9a M6: symmetric pile comparison rule |

I verified by grep that these are the same fields, in the same shape, present in `data/results/family/0.3.json` (L213739, L221941, L221962, L222964) and `data/results/holidays/0.3.json` (L231048, L238183, L238192, L238884) — i.e., already live and already CDA-SME-approved at Phase 9a sign-off. The food values arrive via the same `analyze.py` → `pipeline.py` invocation that produced them for family and holidays; the only difference is that food's prior published 0.2 was computed *before* Phase 9a's term-level extensions shipped (or with those fields empty) and therefore showed empty `term_mds_items: []`, `centroid_piles: {}`, `term_cluster_labels: []`, `term_mds_uncertainty: {}`, `term_cluster_bp_values: []` on the currently-published `apps/dashboard/public/data/food.json` (verified by grep — all five surface as empty containers in the live file).

**Conclusion: this is a re-baseline that simply fills in fields the food domain should have had populated all along. There is no new analytical method being introduced at promotion. The same R10-compliant uncertainty machinery (term-level ellipses, branch-probability bootstrap) that the dashboard already renders for family/holidays will now render for food.** Approving this promotion is *narrower* in methodological surface than approving Phase 9a was — Phase 9a approved the method; this verdict only approves applying the already-approved method to a domain that hadn't been re-analyzed since the method was added.

### Pinned-toolchain identity

Per `out/rebaseline/baseline_manifest.json` L11–18: food's regen ran under `numpy_version: "2.4.4"`, `scipy_version: "1.17.1"`, `python_version: "3.12.3"`, `git_sha: "fd6f490"`, `bootstrap_B: 500`, `guard: pass`. Identical toolchain to family + holidays. The pinning event from PROMOTE-1/PROMOTE-2 now extends to all three published domains under a single coherent provenance story.

---

## §2 — Question 2: R10 / §4.5 uncertainty surface on food's new term-MDS

**Ruling: PASS. Every term-level point published carries its uncertainty ellipse. R10 satisfied.**

Verified by direct file inspection:

- `term_mds_uncertainty` at `out/rebaseline/food/0.2.json` L51766–L54727 contains an ellipse object per term, each with the four `BootstrapEllipse` parameters Phase 9a M4 specifies: `center: [x, y]`, `semi_major: float`, `semi_minor: float`, `rotation_rad: float`, `n_bootstrap: 200`. Sample (line 51767–51776, item "biryani"): `{"center": [0.00819, 0.00950], "semi_major": 0.02160, "semi_minor": 0.01772, "rotation_rad": 1.9273, "n_bootstrap": 200}`. Same shape as family's and holidays' term ellipses.
- Total `n_bootstrap` field occurrences in the file: **304** = 296 term ellipses (matches `term_mds_items` length 296) + 8 model ellipses (matches food's 8 models). The 296-to-296 count is the load-bearing R10 check: every term on the term-MDS has its ellipse. No bare points.
- `term_cluster_bp_values` at L54728+ contains branch-probability values per internal node of the AHC linkage (verified non-empty, `1.0, 1.0, 1.0, 0.995, 0.995, 1.0, …` ranging high — solid branch stability on the well-defined clusters near the tips). This is the cluster-level uncertainty surface required for the dendrogram / cluster-label viz.
- Per-model bootstrap (`bootstrap_ellipses`, similarity CI etc.) is also populated for the cross-model MDS surface, same as family/holidays.

**The Register-1 underestimation caveat (`docs/BOOTSTRAP_DESIGN.md` §2) applies to OCI CIs only and does not apply at the term-MDS level — term-MDS bootstrap resamples *models* (Register 2 informants), not within-model runs.** This is the same posture I (CDA SME) approved at Phase 9a M4a: "Resulting CIs reflect between-model structural variance only. The methods page must state: 'Term position confidence reflects agreement across models, not within-model sampling variance.'" The food promotion inherits this M4a methods-page disclosure obligation. If the methods page already discloses M4a for family/holidays, it covers food automatically; if it does not yet, food's promotion does not introduce a new disclosure gap (it inherits an existing one) — see Note C4.

---

## §3 — Question 3: Food's small-n trustworthiness on term-level MDS / cluster solution

**Ruling: PASS-WITH-NOTES. Publishable as-is at n=8 because the per-term ellipse + BP-per-branch surfaces *are themselves* the small-n trustworthiness disclosure — every reader sees the wider-or-narrower ellipse and the per-cluster BP value and can reason about which positions to trust. No additional stress-level numerical disclosure is required. But — see Note C3 below — a methodology-page sentence explicitly naming food's n=8 in the context of the term-level viz is binding.**

### Why this is publishable

1. **The Romney consensus classification is not at risk.** Food's `romney_eigenratio: 6.586` (L6681) is comfortably above the 5.0 LSB strong-consensus boundary; even the recompute under the pinned toolchain held the classification (the 2026-05-29 verdict's T-3 guard was the most-load-bearing of the six because of this very proximity, and it cleared). `consensus_type: STRONG_CONSENSUS` (L6687) is methodologically defensible. The term-level viz is downstream of the consensus calculation, not a competing claim.

2. **Per-term ellipses are the trustworthiness disclosure for term positions.** Reviewing the sample ellipses I read (biryani: semi-major 0.0216 on a [-1, 1] unit-scale MDS; bouillabaisse: 0.0315; borscht: 0.0349), these are *narrow* ellipses — comparable to family's and holidays' at similar terms. The bootstrap is doing its job: terms whose position is uncertain *across models* render visibly wider ellipses; terms whose position is stable across models render visibly narrower ones. Readers see this directly without needing a stress disclaimer in copy.

3. **Per-cluster BP values are the trustworthiness disclosure for cluster solutions.** The sampled BP values I read (`1.0, 1.0, 1.0, 0.995, 0.995, 1.0, 0.995, 1.0, 0.94, 0.845, 0.83, …` at L54728+) range high near tips, lower near deeper splits. This is exactly the textbook BP pattern. Clusters readers should trust will render with BP near 1.0; deeper splits readers should be cautious about render with lower BP. This is the M5 contract.

4. **The small-n flag is already firing in-band.** `romney_small_n_warning: true` at L6686 (because food's n=8 < the 15-model threshold). Holidays *also* fires `romney_small_n_warning: true` at n=14 (verified at `data/results/holidays/0.3.json` L29492) under the same n<15 threshold. So food does not need a *new* small-n surface — it inherits the existing `romney_small_n_warning` surface that holidays already uses. The dashboard's existing small-n treatment (whatever copy renders alongside the consensus card when this flag is true) automatically covers food.

5. **The term-MDS / cluster machinery's own thresholds were already cleared.** `pipeline.py` line 678 gates term-MDS on `len(pooled_matrix.items) >= 3` (food has 296 — comfortably above). Phase 9a's `min_items=15, max_items=300` term-level cross-model frequency elbow (per the term truncation ruling in my memory `project_phase9a_term_truncation_ruling.md`) places food at 296 — at the upper end of the allowed range, *more* items than the floor demands. This is a domain with rich vocabulary, not a sparse one; the term-level viz is well-posed at this scale.

### Why a methodology-page sentence about food's n=8 is still binding (Note C3)

The above is methodologically correct, but the audience-translation surface needs an explicit handhold. The dashboard reader landing on the food page will see a term-MDS with 296 terms × 8 informants, and the n=8 is not obviously displayed alongside the term-MDS itself (it's adjacent to the consensus score, not on the term-MDS canvas). A returning reader who knows family/holidays have 14–15 models may notice food's tighter ellipses on certain terms and incorrectly attribute it to "stronger consensus on food" when it could also be a consequence of fewer informants in the model-resample bootstrap. Naming n=8 once in the methodology-page copy in the term-level viz section closes that gap. See Note C3 for the binding wording.

---

## §4 — Question 4: Provenance once food promotes

**Ruling: APPROVED. Footer auto-enables for food, `provenance.json` `domains` block adds the food entry, methodology-page scope expands. PROMOTE-2 B3/B4/B5 carve-outs invert in lockstep.**

### Concrete required changes (matches PROMOTE-2's contract, food entry added)

1. **`provenance.json` `domains` block.** Add the food entry with `numpy: "2.4.4"`, `scipy: "1.17.1"`, `regenerated_at: "2026-05-29T14:14:29.345588+00:00"`, `git_sha: "fd6f490"`, `analysis_version: "0.2"`, `sha256: "3330f8fa7702c0043c2c796267a545dc4bedc63aa8c9ed61652a240b932ed6b0"`. Reviewer cross-checks against `out/rebaseline/baseline_manifest.json` L11–18.

2. **Footer.** Per PROMOTE-2 Note B5(b) (preferred conditional per-domain footer sourced from `provenance.json`'s `domains` block), the food page's footer should now render "Calculated with NumPy 2.4.4 and SciPy 1.17.1" automatically as soon as the food entry appears in the manifest. No additional code change is required *if* B5(b) was implemented; if B5(a) (global footer + methodology scoping) was used instead, the methodology paragraph wording must change in lockstep (Note C1 below).

3. **Methodology-page paragraph.** The PROMOTE-2 §3 paragraph (whichever option Mark shipped) currently scopes the pinned-toolchain claim to "the published family and holidays corpora" and the final sentence explicitly defers food. Both sentences need lockstep amendment — see Note C1 for the exact required wording shift.

### Audit-trail story (post-promotion, three-domain)

A reader inspecting the live site post-promotion sees:
- All three domain pages (family, holidays, food) carry the footer "Calculated with NumPy 2.4.4 / SciPy 1.17.1."
- `provenance.json` lists all three domains under the pinned versions with the 2026-05-29 regen timestamp.
- Methodology paragraph names all three domains; the food-deferral sentence is removed (or rewritten to past tense to preserve the audit story — see Note C1 alternative).
- Commit history greppable: `2026-05-29-rebaseline-cda-sme-verdict.md` (corpus regen approval), `2026-05-30-promote-cda-sme-verdict.md` + `2026-05-30-promote2-cda-sme-verdict.md` (family + holidays promotion), `2026-05-31-food-promote-cda-sme-verdict.md` (this file — food promotion). Four CDA SME files; one chain of custody.

---

## Notes C1–C5 (binding for the promotion commit)

**Note C1 (binding — methodology paragraph scope amendment).** The methodology-page "Data provenance" paragraph (whichever Option 1 / Option 2 wording Mark shipped under PROMOTE-2 §3) must be amended to extend the pinned-toolchain claim to food. Two acceptable wording amendments — Mark picks one:

  **(C1.a — RECOMMENDED, drops the deferral sentence entirely.)** Change the opening clause "The published family and holidays corpora were recomputed…" to "The published family, holidays, and food corpora were recomputed…" *and* delete the final sentence ("The food domain remains on its prior toolchain pending a separate methodological review and is not covered by the footer above; it will be re-baselined and re-marked once that review completes."). This produces the cleanest reader-facing copy post-promotion.

  **(C1.b — preserves the audit story in past tense.)** Same opening-clause change as C1.a, but instead of deleting the final sentence, rewrite it to: "The food domain was re-baselined separately on 2026-05-31 under the same pinned toolchain; the food domain page now carries the same provenance footer as family and holidays." This is more verbose but leaves a forward-readable trace that food was on a different track for ~24 hours.

  Either option satisfies vocabulary compliance (no "wrong/right/corrected/fixed/bug/error" framing; no §1.5.4 / CLAUDE.md §7 forbidden phrases; the change is named as a re-baseline, not a fix). Reviewer confirms byte-identity against whichever option Mark selects.

**Note C2 (binding — `provenance.json` `domains` block lockstep).** The `provenance.json` artifact shipped with this promotion MUST add the food entry to its `domains` block with the values listed in §4 item 1 above. Reviewer verifies field-for-field against `out/rebaseline/baseline_manifest.json` L11–18 (food entry). PROMOTE-2 Note B4 inverts: food now appears in the manifest because the manifest claim is now true for food.

**Note C3 (binding — methodology-page n=8 disclosure for food's term-level viz).** The methodology-page section covering the term-MDS / cluster surface must name food's n=8 informant count explicitly, alongside the family (n=15) and holidays (n=14) counts that should also be named (or already are). A single sentence is sufficient. Acceptable wording: "The cross-model term map is computed from 15 model informants on family, 14 on holidays, and 8 on food; ellipse widths and branch-probability values are derived from model-resample bootstrap (B=200), so a sparser informant pool produces a different bootstrap envelope shape than a denser one even when the per-model agreement is similar." This wording reuses the Phase 9a M4 model-resample framing and closes the audience-translation hole described in §3.

**Note C4 (binding — Phase 9a M4a disclosure inherits to food).** The methods-page text governed by Phase 9a M4a ("Term position confidence reflects agreement across models, not within-model sampling variance") applies to food unchanged. If this text is already present for family/holidays it covers food automatically. If it is not present (i.e., M4a was carried as an outstanding obligation since Phase 9a sign-off), it must be added in this commit — promoting food's term-MDS without it would extend an existing M4a gap to a third domain. Reviewer greps the methodology page for the M4a sentence (or equivalent) and confirms presence before promotion lands. This is not a new ask of this promotion; it is a check that an outstanding ask from Phase 9a is satisfied at the moment food's term-MDS ships.

**Note C5 (binding — commit body audit chain).** The promotion commit body MUST reference (a) this verdict file (`docs/status/2026-05-31-food-promote-cda-sme-verdict.md`), (b) the PROMOTE-2 verdict (`2026-05-30-promote2-cda-sme-verdict.md`), and (c) the 2026-05-29 rebaseline verdict (`2026-05-29-rebaseline-cda-sme-verdict.md`) by path. This closes the four-CDA-SME-verdict chain for the full re-baseline → promotion → food-deferral → food-promotion lifecycle in a single greppable `git log`. The PROMOTE-1 verdict need not be re-referenced (PROMOTE-2 supersedes it on the CI-stability claim) but may be.

---

## §5 — What is *not* required (preempting scope creep)

- **No new tests.** Food's lede surfaces no rendered-digit change (consensus_score, consensus_ci, romney_eigenratio, consensus_type are all byte-identical live→staged per the verified facts in the task). No food-specific lede test exists that would need updating (verified by Grep against `tests/cdb_publish/test_lede.py` — only family + holidays have hardcoded numeric assertions, both already updated under PROMOTE-2 §2). The §2 of PROMOTE-2's authorized test-edit list is complete; this promotion adds nothing.
- **No re-bootstrap.** The 0.2 staged file was already computed at B=500 model-level + B=200 term-level under the pinned toolchain on 2026-05-29. Promotion is a copy operation, not a re-analysis.
- **No schema change.** The fields being populated for food were already in the `DomainResult` schema (verified by their presence-as-empty in the live `apps/dashboard/public/data/food.json`). No `cdb_core/schemas.py` change is required and no `DATA_DICTIONARY.md` update is required by this promotion specifically. (If the M4a disclosure of Note C4 is being added for the first time in this commit, the methods page is the only documentation surface — DATA_DICTIONARY is not affected.)
- **No new viz component.** The dashboard already renders term-MDS / dendrograms / cluster labels for family and holidays. Food's promotion lights up the same component for a third domain. No `apps/dashboard/src/views/` changes are introduced by this verdict (UI/UX may need a separate verdict if the food page route or domain-picker pill state needs adjustment, but that is outside CDA SME scope).
- **No `data/raw/` change.** Append-only invariant preserved. Reviewer's CI append-only check will not fire.

---

## §6 — Register & vocabulary compliance

**Register compliance — PASS.** Promotion does not move any analytical method across the R1/R2/R3 boundary. Food's consensus calculation is at R2 (between-model categorical structure analysis) and stays there. The newly-populated term-MDS / cluster surface is also at R2 (cross-model item co-occurrence + model-resample bootstrap per Phase 9a M4) — same register as the existing cross-model MDS map. No R1 within-model claim is added or modified by this promotion. The per-term ellipses *are not* OCI ellipses and do not carry the Register-1 underestimation caveat (which is correct — they're R2 ellipses).

**Vocabulary compliance — PASS.** All wording in Notes C1.a / C1.b / C3 / C4 audited against §1.5.4 + CLAUDE.md §7. Zero forbidden phrases. Zero "worldview," "believes," "thinks." Zero "wrong/right/corrected/fixed/bug/error" framing per N3 carry-forward. The change is named as a *re-baseline* and a *pin*, not as a *fix* or *correction*. The term "agreement across models" in the M4a inherited sentence (Note C4) is the Phase-9a-approved framing and is not a forbidden phrase. The R10 surface for the newly-published term-level viz inherits family/holidays' existing copy and does not introduce new wording that would need a fresh audit.

---

## Required before promotion ships (consolidated)

1. **Note C1 (binding)** — methodology paragraph scope amended (C1.a or C1.b); Reviewer confirms byte-identity against Mark's chosen option.
2. **Note C2 (binding)** — `provenance.json` `domains` block adds the food entry with the seven manifest fields listed in §4 item 1.
3. **Note C3 (binding)** — methodology-page text on term-MDS / cluster viz names food's n=8 alongside family's n=15 and holidays' n=14 (acceptable wording in C3 body).
4. **Note C4 (binding)** — Phase 9a M4a methods-page sentence ("Term position confidence reflects agreement across models, not within-model sampling variance") confirmed present on the methodology page; if absent, added in this commit alongside the food promotion.
5. **Note C5 (binding)** — promotion commit body references this verdict + PROMOTE-2 verdict + 2026-05-29 rebaseline verdict by path.
6. **Atomic release (carry-forward from PROMOTE-2 Note B2)** — data promotion (`data/results/food/0.2.json` + `apps/dashboard/public/data/food.json`) + `provenance.json` food entry + methodology paragraph amendment (C1) + methodology-page term-MDS n=8 disclosure (C3) ship in the SAME commit. No partial promotion.
7. **Footer rendering verification.** If PROMOTE-2 implemented B5(b) (conditional per-domain footer sourced from manifest), confirm the food page footer auto-renders post-promotion. If B5(a) (global footer) was used, confirm methodology paragraph C1 wording aligns and the global scope is now genuinely "all three domains."

## Advisory (not blocking)

8. The fact that food's `consensus_score`, `consensus_ci`, `romney_eigenratio`, and `consensus_type` are byte-identical live→staged (verified by the task description; food was the load-bearing T-3 guard from the 2026-05-29 verdict that *might* have crossed a threshold but did not) is the strongest single piece of evidence that the re-baseline preserved food's interpretive claims at every consequential decimal. The methodology paragraph need not mention food's byte-identity explicitly — silence on this point is the correct posture (calling it out would draw inappropriate audience attention to the fact that family + holidays *did* shift while food did not; the underlying mechanism is the same rounding-edge phenomenon and the asymmetry is uninteresting). Mark may choose to mention it in the commit body for the audit trail; this is advisory.

9. If Mark wants to add a single sentence to the methodology paragraph naming food's term-MDS as the surface where food gains a new visualization on this release ("Food's term-level cross-model map and cluster solution are published for the first time with this release, computed under the same pinned toolchain as family and holidays") — that is an acceptable optional addition that satisfies §1.5.4 + N3, but it is not required. The dashboard reader landing on food's page will see the populated term-MDS without it; copy disclosure is belt-and-suspenders, not load-bearing.

---

*PASS-WITH-NOTES. The food domain re-baseline promotion may proceed under the binding conditions above. This verdict closes the food-deferral carve-out from PROMOTE-2 §4 and completes the three-domain pinned-toolchain promotion. Reviewer confirms byte-identity of the §3-paragraph amendment (Note C1) against whichever option Mark selects, verifies the `provenance.json` `domains` block lockstep addition (Note C2), greps for the M4a methods-page sentence (Note C4), and confirms the commit body's three-verdict audit chain (Note C5).*
