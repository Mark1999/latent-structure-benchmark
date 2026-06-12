---
name: runbook-step2-fix-verdict
description: RUNBOOK-STEP2-FIX docs-only plan PASS-WITH-NOTES 2026-06-12 — Step 2 single_pass correction
metadata:
  type: project
---

# RUNBOOK-STEP2-FIX plan verdict (2026-06-12)

**Plan:** docs-only single-file correction to `docs/proposed/2026-06-08-new-model-incorporation-runbook.md` so Step 2 canonical incorporation command uses `single_pass` (not `cross_model_consensus`), updates `--skip-collected` semantic to `(model_id, domain_slug)` 2-tuple per COLLECTOR-BUGS BUG 1, and adds one-line Step 3 forward-reference to `similarity_collection_mode` per-domain guard from FOOD-FIX-A.

**Verdict:** PASS-WITH-NOTES.

**Why this lands cleanly:**
- Step 2 mode correction directly addresses Protocol-validity axis (the runbook prescribed a mode that produces empty `parsed_items` and cannot enter the consensus basis; PROMOTE-FOOD-V02 + FOOD-FIX-A + Phase 9b food guard-trip memos all confirm `single_pass` is the slate-incorporation mode and `cross_model_consensus` is a supplement that requires existing single_pass records for the new model to be meaningful).
- `--skip-collected` semantic update matches COLLECTOR-BUGS BUG 1 fix (commit `0c1d9b0`, key now `(model_id, domain_slug)` per `scripts/collect.py:149,151,680,683,697`) — Reviewer-grade accuracy.
- Step 3 one-liner correctly characterizes `similarity_collection_mode` per-domain (food = `single_pass`, family/holidays = None) as documented at `scripts/rebaseline_corpus.py:83-99`.
- Glossary cross-reference target (`docs/GLOSSARY.md` line 13 "Collection mode") already names the 2026-06-11 contamination incident; no glossary edits required.
- CLI surface check anchor correct: `--mode single_pass --model <id>` (singular) per `scripts/collect.py` usage docstring lines 7-12.
- No UI/UX routing (no frontend artifact); no schema change; no test surface; single-file diff.

## Binding N-notes (Coder must apply before commit)

**N1 (BINDING, vocabulary axis).** The new "Which collection mode" subsection must keep prose at the level of record-shape (one session sorts its own items vs. one session sorts a shared deck). It must not introduce attribution-class framing to either mode name (no language about what the model considers, regards, perceives, or understands; no language about the model's view of the deck or its mental model of any item). Acceptable phrasing: "single_pass produces records where the model sorts items it generated in the same session"; "cross_model_consensus produces records where the model sorts a shared item deck derived from every contributing model's free-lists." CLAUDE.md §7 / ARCHITECTURE.md §1.5.4 apply to runbook prose even when audience is operator-internal.

**N2 (BINDING, claims axis).** The "Which collection mode" subsection must not characterize `cross_model_consensus` records as "lower-quality" or "noisier." They are a different record shape (placeholder free-list + populated pile-sort on shared deck), not a degraded `single_pass`. The accurate framing is: cross_model_consensus records intentionally carry an empty `parsed_items` because the items are externally supplied; this is by-design, not a defect. The reason they cannot enter the consensus free-list basis is the empty `parsed_items`, not a quality judgment. SME pre-clears the byte-string "produces records with placeholder free-lists that cannot enter the consensus basis" used in the plan as accurate and non-attributing — preserve that exact framing.

**N3 (BINDING, protocol axis).** The Step 2 canonical example bullet text "match the slate's current N for that domain" is correct in spirit but must cite the operational rule by its name: the saturation analysis is referenced in `ARCHITECTURE.md` §4.2.7 (two-level pipeline). Plan AC2's existing pointer "(ARCHITECTURE §4.2.7)" already in the current runbook line 95 — preserve it on the rewrite; do not strip the cross-reference. The "CDA SME question if unsure" carry-over is licit.

**N4 (BINDING, protocol axis).** The new subsection must not imply that `cross_model_consensus` is *only* relevant after slate widening. It is the second-stage Register-2 protocol step in the standard pipeline and is run on the established slate as a regular analytical surface. The accurate scoping is: "cross_model_consensus cannot be used as the first or only collection mode for a new model entering a domain" — narrower than "cross_model_consensus is only a supplement, never primary." Re-word any draft language that implies the latter.

**N5 (BINDING, claims axis).** The Step 3 one-line addendum on `similarity_collection_mode` must not recapitulate the FOOD-FIX-A methodology argument; one factual sentence + file-line pointer per the plan AC5 wording is correct. Specifically the sentence must not say or imply "without this guard, contamination is automatic" — the guard is a defense-in-depth measure; the upstream defense is collecting in the correct mode (which is what Step 2 is being corrected to do). Suggested phrasing: "Note that `rebaseline_corpus.py` carries a per-domain `similarity_collection_mode` setting (set to `single_pass` for food after FOOD-FIX-A); this is a defense-in-depth filter, not a substitute for Step 2 mode-correctness." Coder may match diction to local prose, but the defense-in-depth framing is binding.

**N6 (BINDING, vocabulary axis, em-dash hard rule).** The verdict-author and Coder both run an em-dash grep (U+2014) over the diff hunks before commit; zero matches required. The plan AC7 already names this. Pre-existing em-dashes elsewhere in the runbook are OUT OF SCOPE for this commit; the AC9 single-file constraint does not require fixing them in this task. Coder should not silently fix them as a side-pass.

**N7 (ADVISORY, claims axis).** The "cautionary incident" link in the new subsection should point to the campaign status doc as specified, AND the subsection's incident sentence should not name the SME as having "diagnosed the runbook bug" or similar. The runbook bug is a separable defect surfaced by the campaign incident; the SME adjudicated the data artifact (eigenratio drop), and the runbook defect was the upstream root cause. Keep the framing factual: "the 2026-06-11 food campaign incident traced its proximate pipeline defect to records collected under this mode" or similar. The Architect plan §1 wording "followed it verbatim, collected only `cross_model_consensus` records" is licit and the SME pre-clears it for the runbook prose if reused.

## Axis scorecard

```
Axis 1 — Protocol validity:      PASS  (single_pass = correct slate-incorporation mode; cross_model_consensus shape correctly characterized)
Axis 2 — Analytical validity:    N/A   (docs-only; no method change)
Axis 3 — Claims validity:        PASS-WITH-NOTES  (N2/N5/N7 constrain non-attributing framing of mode difference + Step 3 defense-in-depth)
Axis 4 — Audience translation:   PASS-WITH-NOTES  (N1 vocabulary; N3 cross-reference preservation; N6 em-dash grep)

Register compliance:             N/A   (no register-1/2 claim re-framed in this diff)
Vocabulary compliance:           PASS-WITH-NOTES  (N1, N6 binding; SME will spot-check the diff on re-review if requested)
```

## Routing call

Re-route to SME only if any of the following arise during implementation:
- Coder discovers the `--skip-collected` semantic is NOT keyed on `(model_id, domain_slug)` at the actual current commit (re-verify against `scripts/collect.py:680-697`; if discrepancy, STOP and surface).
- Coder discovers `similarity_collection_mode` per-domain dict has changed since `rebaseline_corpus.py:83-99` was last read in this verdict file.
- Drafting language for the "Which collection mode" subsection requires more than 200 words or touches the methodology page surface.
- Glossary "Collection mode" entry needs an edit after all.

Otherwise: PASS-WITH-NOTES is terminal; hand to Coder; no re-route required.

## Forbidden carve-outs (none)

No carve-outs requested or granted. CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden vocabulary fully apply to all added runbook prose.
