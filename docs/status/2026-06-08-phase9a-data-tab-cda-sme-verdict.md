# Phase 9a — Data download tab — CDA SME verdict (light) (2026-06-08)

**Verdict: PASS-WITH-NOTES.** Claims validity PASS / audience PASS-WITH-NOTES. Vocabulary PASS.
Light re-use confirmation (all copy verbatim from M11-launch-vetted artifacts).

## Findings
- Header subhead, bundle-stats sentence, licenses, citation, what's-in-the-bundle: all verbatim from
  `data/open_bundle/README.md` + `huggingface_dataset_card.md` + ARCHITECTURE §6.6, all clean. The
  Coder writes no new framing prose, so no new §7 surface (Reviewer spot-grep at PR is the backstop).

## Required before merge (binding)
1. **Header subhead — lift the FULL three-sentence framing block, not a single sentence.** Source:
   `data/open_bundle/README.md` lines 19-26 (the paragraph beginning "The mismatch is the finding"
   through the corpus-lens definition through "Every domain in v1 is model-to-model. There are no human
   baselines."). If a shorter subhead is forced, the minimum legal subset is the corpus-lens sentence
   PLUS "Every domain in v1 is model-to-model." The bare "There are no human baselines." MUST NOT appear
   without the "model-to-model" anchor co-located in the same visual block (else it reads as pitfall-#4
   absence framing). Reviewer enforces via spot-grep + visual read.
