# Phase 4a Kickoff — Architect Verdict

**Date:** 2026-04-22
**Architect:** spawned from Claude Code session on Linode `lsb-agent-02`
**Preceding gates (all PASS):**
- B2 backup layer Active (`docs/status/2026-04-22-b2-test-restore.md`)
- CDA SME on 2026-04-21 findings (`docs/status/2026-04-22-shakedown-findings-cda-sme-verdict.md`)
- CDA SME Position C decision (`docs/status/2026-04-22-reshakedown-question-cda-sme-verdict.md`)
- Position C replay PASS on Linode (`docs/status/2026-04-22-position-c-replay-verdict.md`)

**Amendments applied post-user directive (2026-04-22):**
- Scope: Option A (family + holidays, 120 records) — confirmed by Mark.
- Pre-run cost estimator task and all cost-projection stop conditions **removed** per Mark's standing directive. Prior cost projections were inaccurate by an order of magnitude against actual <$5/session observed. The `$300/month` `CDB_MAX_SPEND_USD` runtime cap (ARCHITECTURE.md §6.2 Tier 1) is the sole spend guardrail. See commit `303761c`.

---

## 1. 12-model slate (requires CDA SME PASS before T1)

The ARCHITECTURE.md §7 decision #3 three-axis filter is stale with respect to the current registry — the spec names `anthropic_api`/`openrouter`/`huggingface`; the registry and adapters include `openai_api`/`google_ai`/`xai_api`. The spec is out of date on the adapter set. The "12-model slate" count is still binding; the spec never enumerated the 12. **This verdict enumerates them.**

| # | model_id | origin | openness | collection_method | Notes |
|---|---|---|---|---|---|
| 1 | `anthropic/claude-opus-4.6` | us | closed | anthropic_api | Flagship US closed; SME §13 reference |
| 2 | `anthropic/claude-sonnet-4.6` | us | closed | anthropic_api | Shakedown-validated |
| 3 | `openai/gpt-5.4` | us | closed | openai_api | Current GPT flagship; SME §13 reference |
| 4 | `openai/gpt-5.4-mini` | us | closed | openai_api | Shakedown-validated |
| 5 | `google/gemini-2.5-pro` | us | closed | google_ai | Google flagship |
| 6 | `x-ai/grok-4` | us | closed | xai_api | **Untested adapter — T1 gates this** |
| 7 | `meta-llama/llama-4-maverick` | us | open | openrouter | US open-weight flagship |
| 8 | `mistralai/mistral-large-2512` | eu | closed | openrouter | EU closed-weight |
| 9 | `mistralai/mistral-small-2603` | eu | closed | openrouter | EU cost-efficient |
| 10 | `deepseek/deepseek-v3.2` | cn | open | openrouter | CN open-weight flagship |
| 11 | `qwen/qwen3.6-plus` | cn | open | openrouter | CN alternate family |
| 12 | `z-ai/glm-5.1` | cn | closed | openrouter | CN closed-weight |

**Coverage:** 3 origins (US 7, EU 2, CN 3), 2 openness states (closed 8, open 4), 5 collection_methods. Exceeds the SME diversity floor in `SHAKEDOWN_PROTOCOL.md` §4.

**Aliases** (`claude-opus-4-6`, `claude-sonnet-4-6`, `claude-opus-4-5`) are registry aliases pointing at the same adapter path and API endpoint as their canonical slash-form model_ids. They are **excluded** from the slate; T2 and T4 invocations use canonical `model_id` only.

**CDA SME gate required on this slate before T1 runs.** Sample composition affects v1 claims.

---

## 2. N semantics

- **Mode:** `--mode cross_model`. The shakedown's `single_pass` is insufficient for Phase 4a — the full CDA protocol (free-list + pile-sort + interview) is required to populate the fields that G1/G2/G3 gates depend on.
- **N=5 maps to** `--runs 5` (five full informant runs per `(model, domain)` cell).
- **Pile-sorts:** `--pile-sorts 1` (one pile-sort per informant per CDA canon; an informant is a subject, not a matrix generator).
- **Temperature:** default (0.7 / 0.3 / 0.3 per step per ARCHITECTURE.md §4.1.3). No override.
- **Domains:** `family` and `holidays` — Option A scope.

**Cell count:** 12 models × 2 domains × 5 runs = **120 InformantRecords, ~360 API calls.**

---

## 3. Spend envelope

**Single guardrail:** `CDB_MAX_SPEND_USD=300` monthly cap (ARCHITECTURE.md §6.2 Tier 1 runtime enforcement). Hard halt at 100% = $300. Warning emitted at 80% = $240. No pre-run projections produced; no session ceiling; no per-call soft ceiling. Observed spend per shakedown-class session has been well under $5; Phase 4a at similar scope is expected to remain well inside the cap.

---

## 4. Task decomposition

### T1 — Adapter preflight
**Scope:** `scripts/preflight.py` (new, read-only against the LLM APIs). For each of the 5 `collection_method` values in the slate (`anthropic_api`, `openai_api`, `google_ai`, `xai_api`, `openrouter`), make one minimum-cost call and verify: auth works, `model_version_returned` populated, response parses into the adapter shape, `cost_usd` populated. **Specifically exercises `xai_api`** (never canonically tested) with one Grok-4 ping. Writes result to `docs/status/2026-04-22-phase4a-preflight.md`.
**Acceptance:** 5/5 collection_methods PASS. If `xai_api` fails, Grok-4 is dropped and the slate is re-composed (loop back to Architect to preserve diversity criterion).
**Gates:** Reviewer.

### T2 — CLI semantics confirmation (via dry-run)
**Scope:** Coder runs `scripts/collect.py --mode cross_model --runs 2 --pile-sorts 1 --models anthropic/claude-sonnet-4.6 --domain family --dry-run` (or `CDB_MAX_SPEND_USD=1` minimal real invocation if dry-run does not exercise the plan) and confirms 2 InformantRecords per cell, 3 steps each, output path targets `data/raw/informants.jsonl`. If the CLI does not support this exact invocation, Coder pauses and routes to Architect.
**Acceptance:** One-paragraph note in the verdict file confirming CLI behavior matches §2 N semantics.
**Gates:** Architect (orchestrator).

### T3 — Canary to `data/raw/`
**Scope:** One cheap model (`microsoft/phi-4`) × `family` × N=5, `--mode cross_model`, writes append to `data/raw/informants.jsonl` (canonical, not `data/shakedown/`). Verifies the canonical write path end-to-end; confirms QA_Runner posts to `#lsb-alerts` on a real record; confirms append-only CI check passes; confirms `build_db.py` ingests.
**Acceptance:** 5 InformantRecords in `data/raw/informants.jsonl`, append-only check passes, all show `model_version_returned` populated and `qa_passed=True` (or documented reason if not), B2 nightly backup at 02:00 UTC includes them.
**Gates:** Reviewer.

**Do NOT proceed to T4 without T3 green.** A canary failure means the canonical write path has an uncaught bug.

### T4 — Full Phase 4a collection
**Scope:** 12 models × 2 domains × N=5, `--mode cross_model`, appends to `data/raw/informants.jsonl`. Model order: cheapest first (phi-4 is already T3; then qwen3.6-plus, llama-4-maverick, mistral-small, deepseek-v3.2, glm-5.1, gpt-5.4-mini, gemini-2.5-flash/pro, command/grok, mistral-large, gpt-5.4, sonnet-4.6, opus-4.6 last) so surprises surface on cheap calls before expensive ones. Inspect first model's output before fanning out, per `SHAKEDOWN_PROTOCOL.md` §5 precondition 5 applied in spirit.
**Acceptance:** 120 InformantRecords total (including T3's 5), all `model_version_returned` populated, QA pass rate soft-targeted at >80% (hard failures trigger stop condition 3 below), accumulated spend inside the $300 monthly cap.
**Gates:** Reviewer.

### T5 — Analysis pass
**Scope:** `scripts/analyze.py` for both domains, B=500 bootstraps, writes `data/results/family/0.1.json` and `data/results/holidays/0.1.json`. Does NOT run G1/G2/G3 gates (G1 needs Phase 4b sensitivity study; G3 needs two independent runs — Phase 4d).
**Acceptance:** Both DomainResults validate against schema; `consensus_type`, `romney_eigenratio`, `cultural_centrality_scores`, MDS coordinates populated with uncertainty.
**Gates:** Reviewer + **CDA SME** (first canonical DomainResult — binding four-axis review).

### T6 — QA re-run on corpus
**Scope:** `scripts/qa_check.py --file data/raw/informants.jsonl` sweep. Per the Position C replay verdict, stored-vs-rerun `qa_passed` may differ because Check 2 is pool-aggregation. Write output to `docs/status/2026-04-22-phase4a-qa-sweep.md` with the reconciliation.
**Acceptance:** Stored-vs-rerun deltas documented; no edits to existing JSONL lines (append-only CI rule applies); `qa_passed=False` records tagged with reason.
**Gates:** Reviewer.

### T7 — Post-run hygiene
**Scope:** Verify 02:00 UTC B2 backup captured the new records (or trigger a manual backup run); commit a `docs/DATA_DICTIONARY.md` addendum noting the stored-vs-rerun `qa_passed` semantics (Position C verdict note worth formalizing); write `docs/status/2026-04-22-phase4a-completion.md` summarizing commit SHAs, verdict paths, total actual spend (from `cost_report.py`), record count, QA pass rate.
**Acceptance:** Backup verified; dictionary addendum committed; completion report references all verdict files.
**Gates:** Reviewer.

---

## 5. Stop conditions during T4

1. **Total accumulated spend reaches 80% of `$300` cap ($240):** pause, surface to Mark, decide go/no-go on remainder. (Existing Tier 1 warning.)
2. **Any adapter returns ≥2 consecutive hard failures** (non-rate-limit, non-transient): drop that model from the remaining slate, document in the verdict file, continue with the rest.
3. **`qa_passed=False` rate exceeds 30% within any single model's 10 records** (2 domains × 5 runs): stop that model's runs, surface to Architect; do not continue to other models until diagnosed.
4. **`model_version_returned` missing or null on any record:** hard stop. The longitudinal view (§pitfall 1 in `CLAUDE.md`) depends on this field.
5. **Spend ceiling trips at $300:** hard halt per §6.2 Tier 1. No override.

No per-call estimate stop condition (removed per user directive).

---

## 6. Gate table

| Task | Reviewer | CDA SME | UI/UX | Architect |
|---|---|---|---|---|
| Slate composition (pre-T1) | — | **Required** | — | — |
| T1 preflight | ✓ | — | — | — |
| T2 CLI confirmation | — | — | — | Required |
| T3 canary | ✓ | — | — | — |
| T4 full run | ✓ | — | — | — |
| T5 analysis | ✓ | **Required** (first canonical DomainResult) | — | — |
| T6 QA sweep | ✓ | — | — | — |
| T7 hygiene | ✓ | — | — | — |

No UI/UX gate — Phase 4a produces no dashboard artifacts.

---

## 7. Reading list for the Coder (before T1)

- `CLAUDE.md` §6 rules 6–12, §8 stop conditions, §9 pitfalls 1, 2, 9, 10
- `ARCHITECTURE.md` §4.1 collection, §4.1.6 QA_Runner, §5.3 Phase 4a, §6.2 spend cap
- `docs/SHAKEDOWN_PROTOCOL.md` §4–§7 (shakedown framing, applied in spirit to Phase 4a)
- `docs/DATA_DICTIONARY.md` — `InformantRecord`, `qa_passed` semantics
- `docs/status/2026-04-22-position-c-replay-verdict.md` — stored-vs-rerun QA implications (T6 context)
- `data/models/registry.json` — exact canonical model_ids (no aliases in Phase 4a)
- `scripts/collect.py --help` — CLI flags before T2

---

## 8. Schema changes

**None.** Phase 4a writes to the existing `InformantRecord` shape. If T5 or T6 surfaces a need to formalize stored-vs-rerun `qa_passed` in the schema, that is a separate follow-up task with Architect sign-off + `DATA_DICTIONARY.md` co-update per Reviewer rule R7.

---

## 9. Sequencing

```
CDA SME PASS on slate (§1)
  → T1 adapter preflight
    → T2 CLI confirmation
      → T3 canary to data/raw/
        → T4 full 12-model × 2-domain run
          → T5 analysis (CDA SME gate)
            → T6 QA sweep
              → T7 hygiene + completion report
```

---

*End of verdict. Phase 4a is unblocked from the Architect gate. Next action: spawn CDA SME for slate review.*
