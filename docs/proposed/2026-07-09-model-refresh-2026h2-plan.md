# Model Refresh Plan, 2026 H2: New Flagships Into the Slate

**Document:** `docs/proposed/2026-07-09-model-refresh-2026h2-plan.md`
**Status:** PROPOSED. Operational plan for Mark. Executes the existing runbook
(`docs/proposed/2026-06-08-new-model-incorporation-runbook.md`); adds no new tooling.
**Origin:** Mark's request (2026-07-09). Landscape research sweep same date; model
ids below are web-sourced and MUST be re-verified with `discover_models.py --scan`
and a `--dry-run` before any collection (programmatic verification before trust).

---

## 1. Landscape since the slate was last touched (research sweep 2026-07-09)

| Provider | New since May 2026 | API id | Notes |
|---|---|---|---|
| Anthropic | Claude Fable 5 | `claude-fable-5` | Flagship, GA 06-09, redeployed 07-01 after a June suspension. 1M context. |
| Anthropic | Claude Opus 4.8 | `claude-opus-4-8` | Current recommended default. |
| Anthropic | Claude Sonnet 5 | `claude-sonnet-5` | GA 06-30. |
| OpenAI | GPT-5.5 | `openai/gpt-5.5` | GA on API since 04-24; stable. |
| OpenAI | GPT-5.6 Sol/Terra/Luna | ids unconfirmed | Public release literally 07-09 (today). Snapshot semantics unpublished. |
| xAI | Grok 4.3 | `x-ai/grok-4.3` | GA since April, default since 04-30. |
| xAI | Grok 4.5 | `x-ai/grok-4.5` | GA 07-08/09. Days old. |
| Google | Gemini 3.5 Flash | `google/gemini-3.5-flash` | Stable since 05-19. |
| Google | Gemini 3.5 Pro | not GA | Enterprise Vertex preview only; July target. |
| DeepSeek | DeepSeek V4 Pro / Flash | `deepseek/deepseek-v4-pro`, `-flash` | Since 04-24; open weights. |
| Mistral | Medium 3.5 | `mistralai/mistral-medium-3-5` | No new Large since 2512 (already in slate). |
| Zhipu | GLM-5.2 | `z-ai/glm-5.2` | GA 06-17; dated snapshot `z-ai/glm-5.2-20260616` listed. |
| Meta | Muse Spark | invite-only | Not collectable. No GA Llama 5. |

## 2. Urgent roster facts (verify before anything else)

1. **grok-4 upstream retired.** xAI retired `grok-4-0709` on 2026-05-15. The
   longitudinal series for roster model `x-ai/grok-4` likely ends at May 2026.
   Verify whether OpenRouter still has any serving provider; if not, record the
   series end in the data dictionary notes (fix-forward precedent, no backfill).
2. **DeepSeek alias retirement 2026-07-24.** `deepseek-chat` / `deepseek-reasoner`
   aliases already roll to V4-Flash and retire fully on 07-24. Audit our configs
   for alias usage now (grep collect configs and registry for the alias forms).
   Our roster id `deepseek/deepseek-v3.2` is a pinned form and remains available.
3. **Fable 5 reroute contamination risk.** Post-redeployment, a safety classifier
   reroutes a small share of requests to Opus 4.8. For an informant benchmark this
   means some `claude-fable-5` responses may actually be Opus 4.8 output.
   `model_version_returned` must be checked PER RESPONSE (we already record it;
   pitfall #1); mismatched rows get flagged in qa_notes, not deleted.
4. **OpenRouter slug punctuation differs from first-party ids** (e.g. OpenRouter
   `anthropic/claude-opus-4.8` with a dot vs Anthropic `claude-opus-4-8` with a
   hyphen). Keep the model_id alias vs model_version_returned distinction strict.
5. **xAI recommends `-latest` aliases in its own docs.** Do not use them; pin dated
   forms where they exist.

## 3. Proposed batches

Cross-model measures recompute over the whole slate every time a model is added
(runbook load-bearing fact), so batch additions to minimize re-baseline and
re-promotion cycles. Two batches:

**Batch A (now): stable, GA, verified.**
- `claude-fable-5` (Anthropic direct; watch reroute gotcha above)
- `claude-opus-4-8` (Anthropic direct)
- `claude-sonnet-5` (Anthropic direct)
- `openai/gpt-5.5`
- `x-ai/grok-4.3`
- `google/gemini-3.5-flash`
- `deepseek/deepseek-v4-pro`
- `z-ai/glm-5.2` (pin the dated snapshot form if the adapter path allows)

**Batch B (roughly 2 to 4 weeks out): let the ink dry.**
- GPT-5.6 (Sol and/or Terra) once ids and dated snapshots are published
- `google/gemini-3.5-pro` once GA
- `x-ai/grok-4.5` once it has uptime history
- optional mid-tier fills: `deepseek/deepseek-v4-flash`, `mistralai/mistral-medium-3-5`

All families are already in `FAMILY_CONFIG` (claude/gpt/gemini/grok/deepseek/
mistral/glm), so Step 0 of the runbook requires no code edit for either batch.

## 4. Execution per batch (runbook steps, summarized)

1. `discover_models.py --scan`, review buckets, `--update-registry`, commit registry.
2. `collect.py` per model per active domain (family, holidays, food), single_pass,
   `--skip-collected`, campaign id `new-model-refresh-2026h2-a-<yyyymmdd>`;
   `--dry-run` first. Match N to each domain's existing per-model runs count (check,
   don't assume; SME question if unclear).
3. `rebaseline_corpus.py` to staging; six threshold guards halt on any lede-class
   crossing. A guard trip escalates to Architect + CDA SME with the recompute rule
   applied to every numeric claim in the adjudication. Rule 15 applies throughout:
   run the frozen math, report results, no estimator changes under any gate.
4. `publish.py`, bump `analysis_version` (model set changes).
5. Gated promotion (Reviewer, CDA SME provenance copy, UI/UX footer), push, verify
   live per runbook Step 5.
6. Social trigger fires from the manifest change; drafts only from the admin
   console, per B-1.

Note: with roughly 8 new models over 3 domains, collection is provider-parallel and
runs in single-digit hours per the campaign-timing precedent, not days.

## 5. Open questions for Mark

1. Batch A slate: all eight, or trim? (Three Anthropic adds may be more than the
   slate needs; Fable 5 plus one of Opus 4.8 / Sonnet 5 would still cover the
   family's current spread.)
2. Does the grok-4 series end get a dashboard note when the drift view next ships,
   or just a data-dictionary note now?
3. Cadence remains unsettled (runbook open item). This plan is another on-demand
   invocation; if refreshes settle into a rhythm, decide cadence then, not now.
