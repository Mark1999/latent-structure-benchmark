# Phase 4a — Open Items (snapshot for the next session)

**Date:** 2026-04-23
**Purpose:** A durable record of what's open after T4 completed partially. A new Claude Code session (or Mark re-opening this one) should read this first to pick up the thread without re-deriving state from the commit log.

---

## 1. Where we are

T1–T3 are closed. T4 ran but produced **101/120 records** across 3 failure classes. T5/T6/T7 are blocked on a disposition decision for the three failing models.

| Gate | Status | Reference |
|---|---|---|
| Architect plan + Amendment A | ✓ | `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` |
| CDA SME slate review | ✓ PASS-WITH-NOTES (5 forward notes A–E) | `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md` |
| T1 adapter preflight | ✓ 5/5 PASS, $0.010 total | `docs/status/2026-04-22-phase4a-t1-reviewer-verdict.md` |
| T2 CLI confirmation | ✓ `single_pass` semantics confirmed | `docs/status/2026-04-22-phase4a-t2-orchestrator-verdict.md` |
| T3 phi-4 canary | ✓ 4/5 clean (1 phi-4 pile-sort parse exhaustion) | `docs/status/2026-04-22-phase4a-t3-canary-report.md` |
| Adapter fix (max_tokens 16384→4096 across 5 sites) | ✓ | `docs/status/2026-04-22-phase4a-adapter-fix-verdict.md` |
| **T4 full 12-model collection** | **PARTIAL — 101/120; 3 failure classes** | `docs/status/2026-04-22-phase4a-t4-run-report.md` (commit `b2b74e4`) |
| T4 Reviewer | **not yet run** | — |
| T5 analysis | **blocked on failure-class disposition** | — |
| T6 QA sweep | blocked on T5 | — |
| T7 hygiene + completion report | blocked on T6 | — |

Master tip: `b2b74e4`. Many commits ahead of `origin/master` — nothing pushed this session.

---

## 2. T4 outcome (summary — full detail in `2026-04-22-phase4a-t4-run-report.md`)

- Records produced: **101** of expected 120 (some cells partial or zero)
- QA tally: **74 PASS / 27 FAIL** (re-run of `scripts/qa_check.py` on the corpus)
- Total spend: **$4.95** (vs $300 monthly cap)
- Wall clock: ~2h 48min across 5 parallel streams
- Runner: `scripts/run_phase4a_t4.sh` (committed)
- Streams: anthropic, openai, google, xai, openrouter — each wrote to its own file under `data/raw/informants-t4-*.jsonl` then merged into `data/raw/informants.jsonl`. Merge appended to the pre-existing 4 phi-4 canary records from T3.

### Three failure classes to resolve

| Model | Records | QA result | Suspected cause |
|---|---|---|---|
| `google/gemini-2.5-pro` | **0/10** (rc=1 on every call) | — | systematic adapter-level or CDA-prompt-format mismatch; T1 preflight passed with a trivial "reply ok" probe, so this is CDA-prompt-specific |
| `z-ai/glm-5.1` | 10 records written but **all `qa_passed=False`** and **0 useful pile sorts** | all FAIL | output format drift — records parse as records but the pile-sort content doesn't decode into valid piles |
| `x-ai/grok-4` | 10 records, **8 `qa_passed=False`** | 80% FAIL | likely the content-refusal heuristic that fired on the T1 probe also firing on CDA prompts (T1 forward note warned about this) |

---

## 3. Decisions that must be made before T5 analysis

This is Architect + CDA SME territory, not a Coder decision. Sample composition affects v1 claims.

### Decision 1 — Disposition of the three failing models

Options (per model, may differ):

- **Drop from the slate.** Phase 4a ships as a 9-, 10-, or 11-model slate depending on which are dropped. Changes coverage counts (e.g., US-closed-weight 5→3 if both Gemini and Grok drop; CN-closed-weight 2→1 if GLM drops).
- **Re-run with prompt adjustments.** Targeted intervention (e.g., reword probe to avoid Grok's jailbreak heuristic; inspect raw Gemini output to identify the parse-break pattern).
- **Re-run with fallback parser.** If the output is recoverable but the parser is brittle (e.g., GLM's format differs by a trivial whitespace/keyword change).
- **Accept partial data as a finding.** "Some models decline or can't complete CDA elicitation in canonical form" is itself a Register 2 observation worth reporting. Appropriate for Grok if the refusal is a safety policy; less appropriate for Gemini if it's a parser mismatch.

### Decision 2 — Updated slate composition vs claims

The CDA SME slate verdict's axis-1 PASS was predicated on the 12-model coverage. Dropping models changes claims validity:

- If 3 drop (Gemini, GLM, Grok) → 9-model slate; 3 origins (US 4, EU 2, CN 1); coverage narrows sharply on CN closed-weight and on the xai/google adapters.
- The SME will likely require a re-verdict on any composition change that drops more than one axis-category representative.

### Decision 3 — Whether to re-run T4 partially

If Decision 1 picks "re-run with adjustments," that's a new task (call it T4.1) that needs Architect scoping + potentially SME re-approval on prompt changes.

---

## 4. Pending gate actions

- **T4 commit `b2b74e4` needs Reviewer.** The Coder finished and committed the runner script + run report. Reviewer has not yet issued a verdict on this commit. Normal R-rule check applies; nothing methodologically significant beyond the disposition question above.
- **Architect ruling** on the three failing models (above Decision 1).
- **CDA SME re-verdict** on any slate change resulting from Decision 1 (sample-composition impact).

---

## 5. CDA SME forward notes (from slate verdict) — still applicable downstream

These were accepted at T0 and don't block T4, but they DO bind T5 and beyond:

- **Note A [T5-binding]:** `DomainResult.romney_small_n_warning=True` must be populated; CCM-derived copy must render the small-n caveat.
- **Note B [T6-binding]:** Stored-vs-rerun `qa_passed` divergence will reproduce on the Phase 4a corpus per the Position C replay finding; T6 must reconcile.
- **Note C [public-copy-binding]:** "Coherent corpus-lens structure" language may only migrate into public copy under the full "12 models / 3 origins / n=12 caveat / Register 2 between-model" hedged framing.
- **Note D [public-copy-binding]:** No ceiling claims (proximity to human baseline) until Phase 4c lands.
- **Note E [methodology-page-binding]:** US-weighted composition must be named as a sample limitation, with zero-EU-open-weight gap explicit.

If the slate shrinks below 12 via Decision 1, Notes C and E need revisiting.

---

## 6. Other carried-forward items

- **Task #16 — adaptive `max_tokens` in openrouter adapter** (deferred from T3 fix). Long-term fix; replaces the fixed `4096` cap with `min(registry.context_length - prompt_len - safety_margin, cap)`. Phase 4b prep.
- **Phi-4 3-retry pile-sort exhaustion** (1 record lost during T3). Not a stop condition, just a model-output-quality behavior. Reappears at T4? Check the openrouter stream log.
- **Shakedown-vs-canonical `qa_passed` semantics** — Position C replay finding. `DATA_DICTIONARY.md` addendum pending at T7. Brief: `qa_passed` stored in each record is a collection-time snapshot (pool of same-`model×domain` records then existing); re-running `scripts/qa_check.py` on the full corpus produces different results because Check 2 (freelist uniqueness) is pool-aggregation.
- **Deferred `run_qa_checks` → `cdb_collect.qa` refactor.** Check_9 was placed in `scripts/qa_check.py` adjacent to checks 1–8 pending this migration. When the migration lands, check_9 should be promoted from per-record to once-per-run (Reviewer note on T4/#4 commit).
- **Origin push of ~27 local commits.** `origin/master` is stale; session has not pushed.
- **`HOSTING_AND_DEV_OPS.md` full Hetzner-era rewrite** — deferred per handoff §5. 25 residual references to Hetzner/lsb-agent-01 outside the bounded sections.
- **SSH hardening on Linode** (`PermitRootLogin prohibit-password`) — still TBD, noted in `docs/status/2026-04-22-vps-handoff.md` §5.
- **Cloudflare DNS A-record cutover** `cogstructurelab.com` → `172.238.170.9` — TBD, only after web server live.

---

## 7. Task list state (as of this snapshot)

| # | Task | Status |
|---|---|---|
| 7 | Architect Phase 4a plan | completed |
| 8 | CDA SME slate review | completed |
| 9 | T1 adapter preflight | completed |
| 10 | T2 CLI semantics | completed |
| 11 | T3 phi-4 canary (thread) | completed |
| 12 | T4 full 12-model collection | **in_progress — run complete, Reviewer + disposition decision pending** |
| 13 | T5 analyze family + holidays | pending (blocked on 12) |
| 14 | T6 QA sweep | pending |
| 15 | T7 hygiene + completion report | pending |
| 16 | Adaptive `max_tokens` in openrouter (follow-up) | pending (deferred to Phase 4b prep) |
| 17 | Inspection CLI for raw records | in_progress (this commit) |

---

## 8. How a new session should pick up

1. Read this doc first.
2. Read `docs/status/2026-04-22-phase4a-t4-run-report.md` for T4 specifics.
3. Use the new `scripts/inspect.py` (in this commit) to look at the raw records yourself before spawning any agent. Specifically, inspect the 20 pile-sort transcripts for `google/gemini-2.5-pro`, `z-ai/glm-5.1`, and `x-ai/grok-4` to diagnose the three failure classes.
4. Once the failure modes are understood, decide on Decision 1 (disposition). If any slate-changing option is chosen, spawn CDA SME.
5. After disposition decides, spawn Reviewer on `b2b74e4`, then kick off the disposition actions (possibly T4.1 re-run, possibly proceed to T5 with reduced slate).

---

*End of open-items snapshot. Updated as open items are closed or as new ones emerge.*
