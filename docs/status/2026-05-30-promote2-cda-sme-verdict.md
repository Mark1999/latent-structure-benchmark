# CDA SME Verdict — PROMOTE-2 (corrected re-blessing for family+holidays promotion, 2026-05-30)

**Date:** 2026-05-30
**Scope:** Corrected verdict for the atomic FAMILY + HOLIDAYS promotion of the 2026-05-29 staged re-baseline (NumPy 2.4.4 / SciPy 1.17.1) to live. **Food deferred** — its staged file adds 12 populated structural keys (term-MDS, centroid_piles) and is not drift-only; food gets its own CDA SME review as a separate task.

**Supersedes:** `docs/status/2026-05-30-promote-cda-sme-verdict.md` on the CI-stability claim only. The prior verdict's Ask 1 rationale paragraph contained a factual error: it asserted "The published 95% CI rounds identically ([0.64, 0.94] under both toolchains: 0.6406→0.6438 and 0.9433→0.9425 both round to 0.64 and 0.94)." That is **WRONG**. The actual upper bound moves 0.9433→0.9498, which renders 0.94→**0.95**. Holidays also has two rendered CI movements (0.76→0.77 lower, 0.96→0.97 upper) that the prior verdict did not address because Ask 1 was scoped to family only. This verdict corrects both.

The PROMOTE-1 verdict's Ask 2 prose, Notes A1, A2, A4–A8, and the footer contract remain in force; this verdict re-blesses them under the corrected (broader) scope and offers a refined wording option for the methodology paragraph in §3 below.

**Companion docs:** `docs/status/2026-05-29-rebaseline-cda-sme-verdict.md` (N1–N3, T-1..T-6 origin), `docs/status/2026-05-29-rebaseline-completion.md` (guard-clear evidence), `out/rebaseline/numeric-deltas-family.md`, `out/rebaseline/numeric-deltas-holidays.md`, `out/rebaseline/baseline_manifest.json`, `ARCHITECTURE.md` §1.5 + §1.5.4, CLAUDE.md §7.

**Routing:** This verdict gates the atomic family+holidays promotion commit. UI/UX already PASS on layout (`2026-05-30-promote-ui-ux-verdict.md`); Architect already signed off on `provenance.json` (`2026-05-30-provenance-json-architect-signoff.md`). Reviewer gates the test/file diff against this verdict's authorized list.

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

The PASS-WITH-NOTES axes carry forward N1–N3 from the 2026-05-29 verdict and the binding promotion notes A1–A8 from PROMOTE-1, **plus** the explicit CI-shift acknowledgments below. No new methodological objection. The substance remains a rounding-level reproducibility shift produced by pinning a previously-unpinned analytical toolchain — the same event the 2026-05-29 verdict pre-authorized for promotion conditional on the threshold guard clearing on all three domains (the guard cleared, per `out/rebaseline/baseline_manifest.json`).

---

## §1 — All four rendered-digit changes are acceptable. APPROVED for publication.

**Ruling:** Publishing the four rendered-digit movements below as a single atomic family+holidays promotion is **APPROVED** as rounding-level reproducibility drift. None of them crosses a classification or lede-class boundary; all four are last-shown-digit moves driven by 3rd-decimal underlying shifts under the pinned toolchain.

### The complete change list (verified against staged files)

I have independently verified the four changes against `out/rebaseline/family/0.3.json` L26641–L26645 and `out/rebaseline/holidays/0.3.json` L29482–L29486:

**family/0.3** (live → staged):
| Field | Underlying live | Underlying staged | Δ | Renders (2-decimal) | Visible? |
|---|---|---|---|---|---|
| `consensus_score` (Smith's S) | 0.803321 | 0.805244 | +0.001923 | **0.80 → 0.81** | **YES** |
| `consensus_ci[0]` | 0.640555 | 0.644920 | +0.004365 | 0.64 → 0.64 | no |
| `consensus_ci[1]` | 0.943343 | 0.949769 | +0.006426 | **0.94 → 0.95** | **YES** |
| `romney_eigenratio` | 18.997 | 19.143 | +0.147 | — (not in lede) | n/a |
| `consensus_type` | STRONG_CONSENSUS | STRONG_CONSENSUS | — | unchanged | no |

**holidays/0.3** (live → staged):
| Field | Underlying live | Underlying staged | Δ | Renders (2-decimal) | Visible? |
|---|---|---|---|---|---|
| `consensus_score` (Smith's S) | 0.878139 | 0.880363 | +0.002224 | 0.88 → 0.88 | no |
| `consensus_ci[0]` | 0.763975 | 0.770445 | +0.006470 | **0.76 → 0.77** | **YES** |
| `consensus_ci[1]` | 0.964445 | 0.965641 | +0.001196 | **0.96 → 0.97** | **YES** |
| `romney_eigenratio` | 36.253 | 39.283 | +3.030 | — (not in lede) | n/a |
| `consensus_type` | STRONG_CONSENSUS | STRONG_CONSENSUS | — | unchanged | no |

**Total visible rendered-digit changes: FOUR.** The PROMOTE-1 verdict blessed ONE (family S 0.80→0.81). The other three (family CI-hi 0.94→0.95, holidays CI-lo 0.76→0.77, holidays CI-hi 0.96→0.97) are now explicitly blessed in this verdict.

### Rationale, axis by axis (corrected)

- **Analytical validity (PASS).** All four underlying deltas are at the 3rd decimal (0.001–0.007 absolute), one order of magnitude smaller than the displayed CI width (e.g., family CI width is 0.31 absolute; the largest underlying delta is 0.0064, two orders of magnitude inside the published uncertainty surface). On a single more decimal of display precision, none of these would have crossed a rendering boundary. These are textbook rounding-edge cases driven by underlying values landing within 0.005 of a rounding break under the unpinned toolchain and crossing it under the pinned toolchain. The 2-decimal display rounding is the *only* reason any of these shifts are publicly visible. Holidays' rendered point estimate stays at 0.88 because 0.8781 and 0.8804 both round to 0.88 — the CI bounds happened to be the values that crossed.

- **Claims validity (PASS-WITH-NOTES — note B1 below).** No classification, lede-class, interpretive claim, or model ordering changes on either domain. Both stay STRONG_CONSENSUS. Family's `strong_consensus_with_low_oci` lede pattern (n=15, 1 R1-b model) is unchanged. Holidays' `strong_consensus_with_low_oci` pattern (n=14, 2 R1-b models per the live file) is unchanged. Romney eigenratios move (family +0.147, holidays +3.030) but stay well above both thresholds (5.0 LSB, 3.0 classic) and do not appear in the rendered lede — they drive the consensus-type classification, which is invariant here. The four visible movements are last-shown-digit flips on numerics the audience explicitly came to read, which makes them **more** consequential to surface honestly in the methodology paragraph (see §3), not less.

- **Audience translation (PASS-WITH-NOTES — note B2 below).** A returning reader who screenshotted the previous family lede ("Smith's S = 0.80 [0.64, 0.94]") and now sees "Smith's S = 0.81 [0.64, 0.95]" sees **two** digits move, not one. A returning reader who screenshotted holidays' previous CI display sees both CI bounds move. The PROMOTE-1 methodology paragraph singled out "family's Smith's S moving from 0.80 to 0.81" as "the smallest visible effect on this site" — under the corrected change list, that phrasing understates the visible surface. §3 of this verdict offers a refined paragraph option (binding if Mark hasn't already shipped the PROMOTE-1 verbatim copy; advisory if he has and would prefer a one-paragraph follow-up note instead).

**Note B1 (binding — claims validity).** The promotion commit body MUST reference this verdict file (`docs/status/2026-05-30-promote2-cda-sme-verdict.md`), the PROMOTE-1 verdict (`2026-05-30-promote-cda-sme-verdict.md`), and the 2026-05-29 rebaseline verdict (`2026-05-29-rebaseline-cda-sme-verdict.md`) by path. The audit trail across all three CDA SME approvals must be greppable from `git log`, with this verdict's name making clear it supersedes the prior CI-stability claim.

**Note B2 (binding — audience translation).** The data promotion + test updates and the methodology-page paragraph + footer + manifest link MUST ship in the same release. Same rule as PROMOTE-1 note A2; reaffirmed under the broader change list. The four visible movements without the provenance paragraph would land a number-movement surface on the dashboard with no explanation, which is exactly the audience-translation hole N1–N3 were authored to close.

**Note B3 (binding — food deferral disclosure).** The methodology-page paragraph must NOT claim that *all* published domains were recomputed under the pinned toolchain, because food was not promoted. Acceptable framings: "the published family and holidays corpora were recomputed…" or "the published corpora marked with the pinned-toolchain footer were recomputed…" or any other wording that does not assert the unpinned-food domain participated. See §3 for the binding refined paragraph copy, which handles this explicitly.

**Note B4 (binding — provenance.json scope).** The `provenance.json` artifact shipped with this promotion MUST list only the two promoted domains (family, holidays) in its `domains` block, not all three. Shipping a manifest that includes food under the 2026-05-29 pinned-toolchain regen while food's actual published corpus is the unpinned older file would be a manifest/data integrity violation. The Architect's `2026-05-30-provenance-json-architect-signoff.md` should be checked for this; if it pre-dated the food deferral decision, Reviewer must catch the discrepancy. The single-artifact `provenance.json` either describes what is actually live (correct), or it doesn't ship until food is also promoted.

**Note B5 (binding — footer scope).** The "Calculated with NumPy 2.4.4 and SciPy 1.17.1" footer (PROMOTE-1 A6) MUST NOT appear on the food domain's dashboard page until food is itself promoted under the pin. Two acceptable implementations: (a) the footer is global to the site and the methodology paragraph clearly scopes which domains it applies to (less ideal — invites misreading on food's domain page), or (b) the footer is conditional per-domain, sourced from `provenance.json`'s `domains` block, and renders only on pages whose domain is listed in the manifest (preferred). Coder + UI/UX choose between (a) and (b); the binding requirement is no false provenance claim on the food page. This is the same defect class as the 2026-05-30 revert (`bc0c9b9`) — a provenance claim outpacing the data it claims to describe.

---

## §2 — Authorized test updates in `tests/cdb_publish/test_lede.py`

**Ruling:** The following diff is **APPROVED** and is the complete authorized test-file change set for this promotion. Reviewer should reject any larger or different test diff.

### Authorized edits — family lede assertion (Test 1, L195–L205)

Current state (verified by Read):
```python
194:    # n=15 models on the map (was 11; updated to current corpus — T4 will update again)
195:    assert "15 frontier models" in lede, (
...
198:    # Smith's S = 0.8033... → "0.80" (was 0.71; updated to current corpus)
199:    assert "Smith's S = 0.80" in lede, (
200:        f"Expected 'Smith's S = 0.80' in lede; got: {lede!r}"
201:    )
202:    # CI [0.6406..., 0.9433...] → "[0.64, 0.94]" (was [0.50, 0.91]; updated)
203:    assert "[0.64, 0.94]" in lede, (
204:        f"Expected '[0.64, 0.94]' in lede; got: {lede!r}"
205:    )
```

Approved post-promotion state:
```python
194:    # n=15 models on the map (was 11; updated to current corpus)
195:    assert "15 frontier models" in lede, (
...
198:    # Smith's S = 0.8052... → "0.81" (was 0.80 pre-rebaseline; updated under
199:    # pinned NumPy 2.4.4 / SciPy 1.17.1, 2026-05-30)
200:    assert "Smith's S = 0.81" in lede, (
201:        f"Expected 'Smith's S = 0.81' in lede; got: {lede!r}"
202:    )
203:    # CI [0.6449..., 0.9498...] → "[0.64, 0.95]" (was [0.64, 0.94] pre-rebaseline;
204:    # updated under pinned NumPy 2.4.4 / SciPy 1.17.1, 2026-05-30)
205:    assert "[0.64, 0.95]" in lede, (
206:        f"Expected '[0.64, 0.95]' in lede; got: {lede!r}"
207:    )
```

This subsumes PROMOTE-1 Note A3 (the trailing-comment update for self-documentation), and is now binding — not advisory — because under the corrected change list the comment becomes the primary place a future reader will look to understand why the CI assertion moved.

### No holidays lede assertion change is required

I verified Test 2 (`test_holidays_real_corpus_strong_consensus_with_low_oci`, L221–L250) and the rest of `test_lede.py` (grep on `0\.88|0\.96|0\.76|0\.77|0\.97|Smith`). **No holidays test asserts on Smith's S or CI rendered numerics.** Test 2 reads from `data/results/holidays/0.2.json` (the older n=9 file, not the live n=14 `0.3.json`) and only asserts on the R1-b count phrase and the n=9 model count. The holidays CI movements (0.76→0.77, 0.96→0.97) ship through the lede generator at runtime but are not pinned by any test assertion, so no test edit is needed for holidays under this promotion.

**Stale-test note (advisory, not blocking — carry forward, do not bundle here).** Test 2 asserting against the older `0.2.json` while the live dashboard renders `0.3.json` is a known disjoint. It is not introduced by this promotion (pre-existing condition) and is out of scope for this verdict. If the Coder is tempted to "just update Test 2 to read 0.3.json while we're here," the answer is no — that is bundling per CLAUDE.md §8. File it as a follow-up.

### Anything else

No other test edits are authorized under this verdict. Reviewer rejects any other lede test changes shipped in the same commit unless explicitly required by the `0.81` / `[0.64, 0.95]` updates (e.g., snapshot files, if any exist — none surfaced in my grep, but if Coder finds one, treat it as in-scope for the byte-identical lede update only).

---

## §3 — Methodology-page paragraph: refined copy under the corrected change list

The PROMOTE-1 verdict's approved paragraph singled out "family's Smith's S moving from 0.80 to 0.81" as "the smallest visible effect on this site." Under the corrected change list (four visible rendered-digit movements, not one), that line is **inaccurate as scoped** and **insufficient as audience translation**. It needs revision.

I am providing two options. Mark picks one; either earns PASS. Both are byte-binding once chosen. Both fully satisfy N1, N2, N3, B3 (food-deferral disclosure), and §1.5 / §7 vocabulary.

### Option 1 (RECOMMENDED — full refined paragraph, byte-binding)

> **Data provenance.** The published family and holidays corpora were recomputed on 2026-05-30 under a pinned analytical toolchain (NumPy 2.4.4, SciPy 1.17.1, Python 3.12) so that any researcher with the open data bundle can reproduce the published numerics on their own machine. The prior figures were valid under the toolchain that produced them; what changed is that LSB now pins the NumPy and SciPy versions used for all bootstrap and MDS computations, where previously those versions were whatever the host environment happened to have installed. Values shifted at the third or fourth decimal in bootstrap- and MDS-derived quantities; at two-decimal display rounding, the visible effects on this site are family's Smith's S moving from 0.80 to 0.81 and its 95% confidence interval upper bound from 0.94 to 0.95, and holidays' 95% confidence interval moving from [0.76, 0.96] to [0.77, 0.97]. Deterministic quantities such as Smith's S values before display rounding, OCI, and the Romney eigenratios that drive the consensus-type classification are unaffected at any boundary, and no consensus classification, model ordering, or relative geometry on the MDS maps has changed on either domain. The pinned versions and the exact git commit are recorded in [`provenance.json`](/data/provenance.json), which is regenerated on every published bundle. The food domain remains on its prior toolchain pending a separate methodological review and is not covered by the footer above; it will be re-baselined and re-marked once that review completes.

### Option 2 (MINIMAL DIFF from PROMOTE-1 — replace ONE sentence, keep the rest)

Take the PROMOTE-1 paragraph as-is, and replace the single sentence:

> "Values shifted at the third or fourth decimal in bootstrap- and MDS-derived quantities (the smallest visible effect on this site is family's Smith's S moving from 0.80 to 0.81 at two-decimal rendering); deterministic quantities such as Smith's S point estimates before display rounding, OCI, and Romney eigenratios that drive the consensus-type classification are unaffected at any boundary, and no consensus classification, model ordering, or relative geometry on the MDS maps has changed."

with:

> "Values shifted at the third or fourth decimal in bootstrap- and MDS-derived quantities; at two-decimal display rounding, the visible effects on this site are family's Smith's S moving from 0.80 to 0.81 and its 95% confidence interval upper bound from 0.94 to 0.95, and holidays' 95% confidence interval moving from [0.76, 0.96] to [0.77, 0.97]. Deterministic quantities such as Smith's S values before display rounding, OCI, and the Romney eigenratios that drive the consensus-type classification are unaffected at any boundary, and no consensus classification, model ordering, or relative geometry on the MDS maps has changed on either domain."

AND append, as the final sentence of the paragraph (after the `provenance.json` link sentence):

> "The food domain remains on its prior toolchain pending a separate methodological review and is not covered by the footer above; it will be re-baselined and re-marked once that review completes."

AND change the opening clause "The published corpus was recomputed on 2026-05-30…" to "The published family and holidays corpora were recomputed on 2026-05-30…" to satisfy B3.

**Vocabulary audit (both options).** Zero §1.5.4 / CLAUDE.md §7 forbidden phrases. Zero "worldview," "believes," "thinks." Zero "wrong," "right," "corrected," "fixed," "bug," "error" framing per N3. The defect remains named as *unpinning*, not as an error in the numerics or the methodology. PASS.

**N1 satisfaction (both options).** Date "2026-05-30" + toolchain "NumPy 2.4.4, SciPy 1.17.1, Python 3.12" verbatim. PASS.

**N2 satisfaction (both options).** Inline link to `provenance.json` retained in-paragraph (not footnoted). PASS.

**N3 satisfaction (both options).** All four visible movements disclosed explicitly. Returning reader who notices any of the four can land on a single paragraph that names the change they saw. PASS.

**B3 satisfaction (both options).** Opening clause scoped to "the published family and holidays corpora"; closing sentence explicitly scopes food out. No reader can read the paragraph and conclude food was re-baselined. PASS.

**Note B6 (binding — placement, layout, link target).** PROMOTE-1 Notes A4, A5 apply unchanged. Paragraph placed as the first paragraph of the "Data provenance" section on the methodology page (create the section if it does not yet exist); UI/UX gates heading level + typographic treatment; `provenance.json` link target resolves to whatever public path Mark/UI/UX chose for the canonical artifact.

---

## §4 — Food deferral is methodologically fine. CONFIRMED.

**Ruling:** Promoting 2 of 3 domains (family + holidays) under the pin while food stays on the older unpinned numbers is methodologically clean, **conditional on Notes B3, B4, and B5 above being satisfied** (no false provenance claim on food's dashboard surface, no false claim in the methodology paragraph, no food entry in `provenance.json`'s `domains` block).

**Rationale.** The pinning event is a provenance/reproducibility upgrade, not a methodology change. There is no analytical reason all three domains must transition at the same instant — each domain's published numbers were independently valid under their respective toolchains, and pinning each one is a separate audit event. Food being held back for an independent SME review on its 12 new populated structural keys (term-MDS, centroid_piles per the resume runbook) is exactly the right posture: food is *not* a drift-only change like family/holidays, so it cannot be blessed under the rounding-level rationale that authorizes this promotion. Bundling it would either (a) drag this promotion to wait on the food review, delaying audience-translation surfaces that are already overdue per the 2026-05-30 revert, or (b) pre-bless food's structural changes under a verdict scoped to rounding-level drift, which would be a methodological category error.

**The audit-trail story is coherent.** A reader inspecting the live site post-promotion sees: family + holidays footers say "Calculated with NumPy 2.4.4 / SciPy 1.17.1," `provenance.json` lists family + holidays with the pinned versions and the 2026-05-29 regen timestamp, the methodology paragraph names food as pending separate review. Food's dashboard page either has no footer (preferred per B5b) or a globally-displayed footer whose scope is explicit in the methodology paragraph (acceptable per B5a). When food's separate review completes and food is promoted, the methodology paragraph and `provenance.json` are updated in lockstep; no historical audit-trail breakage.

**The mixed-state risk is low and bounded.** The single risk is a reader assuming the pinned-toolchain claim covers food. The methodology paragraph's closing sentence (Option 1 last sentence; Option 2 appended sentence) closes that gap explicitly. The B5b conditional-footer implementation closes it mechanically. Both belt-and-suspenders together leave essentially no room for the food-confusion failure mode.

---

## §5 — Register & vocabulary compliance

**Register compliance — PASS.** Promotion does not move any analytical method across the R1/R2/R3 boundary on either domain. The corpus was already regenerated; this is the publication step. Family's STRONG_CONSENSUS at R2 (between-model categorical structure) is unchanged. Holidays' STRONG_CONSENSUS at R2 is unchanged. No register reclassification.

**Vocabulary compliance — PASS.** Both refined paragraph options audited against §1.5.4 + CLAUDE.md §7. Zero forbidden phrases. Zero "worldview," "believes," "thinks." Zero "wrong/right/corrected/fixed/bug/error" framing per N3. Zero "publishable" or "closer to human = better" claims. The defect remains named as *unpinning*; the change remains named as a *pin*; the values are *recomputed*, not *fixed*.

---

## Required before promotion ships (consolidated, supersedes PROMOTE-1's list)

1. **Note B1 (binding)** — promotion commit body references this verdict, the PROMOTE-1 verdict, and the 2026-05-29 rebaseline verdict by path.
2. **Note B2 (binding)** — data promotion (`data/results/family/0.3.json`, `data/results/holidays/0.3.json`, plus the matching `apps/dashboard/public/data/**` copies) + test updates (§2 above) + methodology-page paragraph (§3 above, Option 1 or Option 2) + footer (PROMOTE-1 A6) + `provenance.json` artifact ship in the SAME commit (atomic release per the resume runbook).
3. **Note B3 (binding)** — methodology paragraph explicitly scopes the pinned-toolchain claim to family + holidays only; explicitly mentions food deferral.
4. **Note B4 (binding)** — `provenance.json` lists only family + holidays in its `domains` block (no food entry).
5. **Note B5 (binding)** — footer string does NOT make a pinned-toolchain claim on food's dashboard page (preferred: conditional per-domain footer sourced from `provenance.json`; acceptable: global footer plus explicit methodology-paragraph scoping).
6. **Note B6 (binding)** — methodology paragraph placed as the lede of a "Data provenance" section; in-paragraph link to `provenance.json`; layout per UI/UX PASS.
7. **PROMOTE-1 Note A6 (binding, carried forward)** — footer is a one-click link to `provenance.json`, not bare text.
8. **PROMOTE-1 Note A8 (binding, carried forward)** — footer string sourced from the manifest, not hard-coded.
9. **§2 above (binding)** — `tests/cdb_publish/test_lede.py` Test 1 updated to `Smith's S = 0.81` and `[0.64, 0.95]` with the trailing-comment refresh; no other test edits.

## Advisory (not blocking)

10. Mark picks between §3 Option 1 (full refined paragraph) and §3 Option 2 (minimal diff from PROMOTE-1). Option 1 reads more cleanly as a single coherent paragraph; Option 2 minimizes diff against any PROMOTE-1 copy already in flight. Reviewer confirms byte-identity against whichever option is selected.
11. The stale-test condition on Test 2 (reads `holidays/0.2.json` while live renders `0.3.json`) is preserved out-of-scope. Carry as a follow-up; do not bundle into this promotion.

---

*PASS-WITH-NOTES. The atomic family+holidays promotion may proceed under the binding conditions above. This verdict corrects the CI-stability error in `2026-05-30-promote-cda-sme-verdict.md` Ask 1 rationale; the prior verdict's Ask 2 prose framework and Notes A1, A2, A4–A8 are carried forward as-applied. Food remains explicitly deferred to its own separate CDA SME review. Reviewer confirms byte-identity of the chosen §3 paragraph against this verdict file and rejects any test edits beyond the §2 authorized list.*
