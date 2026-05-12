---
name: phase6-T9-failures-publish-verdict
description: Phase 6 T9 failures-as-findings publish-layer CDA SME verdict — PASS-WITH-NOTES; verbatim publication approved; framing_note field binding addition; originating_outcome_class enum surfaces verbatim; provider-quote concern routed Phase 8
metadata:
  type: project
---

2026-05-12 — Phase 6 T9 (failures-as-findings publish-layer) verdict: PASS-WITH-NOTES.

**Key dispositions:**

- **Verbatim-with-defensive-sanitization publication APPROVED.** Architect's §2.1 posture (publish all records verbatim, gated by §3.3 wrapper + publish-layer redaction of API keys / webhook URLs / local paths) is correct.
- **`originating_outcome_class` 7-enum verbatim PASS.** `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other` — all §1.5.4-compliant; surface verbatim; no rewrite map; no `cdb_core` change; no T14 doc-sweep flag on the enum. `refusal_string_match` is the only value with framing weight but reads correctly as a detection-rule name, not a model-intent claim.
- **Manifest key `"failures"` PASS.** The 2026-04-23 directive positively reclaims "failures."
- **Decline-interview v1 prompt PASS.** "In your own words, please describe what happened in that exchange" is anthropological-elicitation register, not introspection.

**Why:** Verbatim publication IS the §1.5 stance for the LSB-authored *prose* layer (T9 emits no paraphrase), but verbatim bytes cannot frame themselves — the framing has to come from somewhere. T10's UI is one path; a top-level `framing_note` field in the JSON is the open-data-bundle path.

**How to apply:** Five binding notes for Coder:
1. **§5.1 — emit top-level `framing_note` field with verbatim text** (Coder may not paraphrase; T10's plan must consume it). Anti-attribution sentence: detection-rule semantics on `originating_outcome_class`, no model-intent attribution.
2. **§5.2 — `DATA_DICTIONARY.md` anti-attribution sentence + duplicate in `cdb_publish/failures.py` module docstring.**
3. **§5.3 — sanitize.py docstring §1.5 scan** (technical-description register only).
4. **§5.4 — narrow generic sk- regex** to `\bsk-[a-zA-Z0-9_-]{50,}` (word-boundary, Anthropic-shape minimum) to reduce false-positives on benign refusal-text mentions.
5. **§5.5 — `DATA_DICTIONARY.md` provider-quote advisory** ("attribute quotes to the model output, not to model intent").

**Provider-quote concern (binding question D):** routed to Mark for acknowledgment, non-blocking for Coder dispatch. Phase 8 legal review path stays open; §5.1+§5.5 mitigate methodological half at JSON layer.

Related: [[phase6-T7-R10-empirical-frequency-verdict]] [[phase6-T5-similarity-heatmap-verdict]] [[failures-are-findings]]
