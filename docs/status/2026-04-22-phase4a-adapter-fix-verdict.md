# OpenRouter Adapter max_tokens Fix — Architect Verdict

**Date:** 2026-04-22
**Trigger:** Phase 4a T3 canary (task #11) — all 5 phi-4 runs failed with HTTP 400 from OpenRouter due to `max_tokens=16384` leaving no room for the prompt in phi-4's 16384-token total context window.
**Preceding context:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` (Phase 4a plan + Amendment A).

---

## Verdict: **APPROVE**

- **Constant change `16384 → 4096` in `packages/cdb_collect/cdb_collect/adapters/openrouter.py`:** APPROVED. 16384 was wrong by construction — it made the adapter unusable for any model whose total context equals the old hardcode. 4096 is the right Phase 4a choice: well above worst-case CDA step output (~2000 tokens for pile-sort matrix), well below every slate model's context, simple to reason about.
- **Output-length risk:** none for Phase 4a. Shakedown priors (freelist ~250 tokens, pile-sort ~2000, interview ~500) all fit with >2× headroom. The one forward watchpoint: at temperature 0.7 with a large item set, pile-sort output grows with item count. If Phase 4b introduces a domain with >40 items, revisit. Not a Phase 4a blocker.
- **Adaptive vs. fixed:** fixed 4096 for Phase 4a. Adaptive (`min(registry.context_length - prompt_len - safety_margin, cap)`) is the right long-term answer but it's a bigger change requiring registry lookup, prompt tokenization, and safety-margin tuning. File a follow-up task for Phase 4b prep: **"adaptive max_tokens in openrouter adapter."**
- **Phi-4 as canary:** KEEP. The bug it surfaced is a real adapter defect that would have bitten us later on any ≤32K-context model. Swapping to sidestep would be "ship now, debug later" technical debt. Fix the adapter, rerun phi-4 T3.
- **Commit structure:** two separate commits. (a) `fix(collect): cap openrouter max_tokens at 4096 to fit small-context models` — adapter change + comment block only, body references this verdict. (b) Second commit is the T3 canary report artifact after rerun succeeds. Do not bundle; Reviewer rejects bundled commits per §8.
- **Historical context for the 16384:** `git log -p packages/cdb_collect/cdb_collect/adapters/openrouter.py` shows the hardcode was introduced in commit `6452e22d` with rationale "max_tokens consistent at 16384" — i.e., set for cross-adapter consistency, not based on any specific model's context window. No deep rationale to preserve. The new 5-line comment replaces the silent hardcode with documented intent.

---

## Slate context lengths (reference)

| model | context_length |
|---|---|
| anthropic/claude-opus-4.6 | 1,000,000 |
| anthropic/claude-sonnet-4.6 | 1,000,000 |
| openai/gpt-5.4 | 1,050,000 |
| openai/gpt-5.4-mini | 400,000 |
| google/gemini-2.5-pro | 1,048,576 |
| x-ai/grok-4 | 256,000 |
| meta-llama/llama-4-maverick | 1,048,576 |
| mistralai/mistral-large-2512 | 262,144 |
| mistralai/mistral-small-2603 | 262,144 |
| deepseek/deepseek-v3.2 | 163,840 |
| qwen/qwen3.6-plus | 1,000,000 |
| z-ai/glm-5.1 | 202,752 |
| microsoft/phi-4 | **16,384** |

All 12 actual slate models have ≥163K context. 4096 `max_tokens` is non-limiting for them.

---

## Gates

- **No CDA SME gate** — adapter behavior change; no analysis-measure, gate-threshold, ConsensusType, §1.5-framing, or methodology impact.
- **No UI/UX gate** — no visual / dashboard impact.
- **Reviewer gate** applies to both commits.

---

## Follow-up task (Phase 4b prep)

Add to backlog: **"Adaptive max_tokens in openrouter adapter."** Scope: replace the fixed `max_tokens=4096` with a per-call computation based on the model's `registry.context_length` minus tokenized prompt length minus a safety margin, capped at a reasonable maximum. This is the right long-term fix; deferred as it's not Phase 4a critical path.

---

*End of verdict. Coder is authorized to commit the adapter fix and rerun T3 canary.*
