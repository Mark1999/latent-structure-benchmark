# Architect Plan — Definitive Spend-Cap Removal

**Target file:** `/opt/lsb-agent/docs/status/2026-05-08-spend-cap-removal-architect-plan.md`
**Author:** LSB Architect agent (Opus 4.7)
**Date:** 2026-05-08
**Originating directive:** Mark, 2026-05-08 — verbatim quoted in §0
**Working tree at plan time:** clean at `981a7f1`
**Gate routing:** No CDA SME gate (no methodology change). No UI/UX gate (no frontend). Architect → Coder → Reviewer → Tester only.
**Commit one-liner:** `docs(arch): spend-cap removal architect plan (2026-05-08)`

---

## §0. Preamble and override

Mark's directive, verbatim (2026-05-08):

> "Before we start this run, we have to backtrack and remove all references to spending caps out of this project. It is causing us way more trouble than it's worth, completely inaccurate. We have not even approached close to this number."

**Override of prior plans.** The Phase 4b architect plan at `docs/status/2026-05-07-phase4b-architect-plan.md` §9 ("Cost transparency") and §8 T4 acceptance criteria around `CDB_MAX_SPEND_USD` are **null and void from this point forward**. The 2026-05-07 plan file is **not edited** — append-only audit-trail discipline keeps it as historical record. This 2026-05-08 plan is the operative authority for everything cost-related downstream.

**Why we are doing this again.** A prior removal landed 2026-05-01 across three commits (`d491ad9` → schema → `edb9de6`) and was reviewer-approved. It regressed in seven days because the Architect plan for Phase 4b §9 reintroduced the framing as "operational guard," and the Coder dutifully wired enforcement back into `scripts/run_phase4b_variance.py`. The mechanism that allowed the regression — soft framing in `ARCHITECTURE.md` §6.2 plus a $300 placeholder in `.env.example` plus a habit of writing cost paragraphs in plans — must be closed off mechanically, not just doctrinally.

Yesterday's actual API spend for the entire Phase 4b T2 + T3 ride-along day was $0.004. The Phase 4b plan estimated $120–$300 for the variance arm. Estimates are off by 2–3 orders of magnitude. Real cost safety lives in provider billing dashboards Mark monitors directly. Software-side cost gates produce friction (script aborts, agent hesitation, hook denials, dispatch friction) without producing safety value.

---

## §1. Architectural decisions (binding)

### §1.1 Decision A — `ARCHITECTURE.md` §6.2 disposition

**Architect rec:** **Replace, do not merely soften.** The §6.2 section header `### 6.2 Cost tracking` is renamed to `### 6.2 Cost posture` and its body is replaced with a **principle statement** (text in §3 below). The header is preserved (not deleted) because §6.2 is referenced by section number from `docs/SHAKEDOWN_PROTOCOL.md` and `docs/PROMPT_EVOLUTION_LOG.md` and historical `docs/status/` files; renumbering downstream sections risks audit-trail breakage. The Anthropic prompt-caching paragraph that currently sits inside §6.2 (lines 1391 in `ARCHITECTURE.md`) is **preserved verbatim** — prompt caching is a real cost-control mechanism for orchestrator calls and is binding on agent invocation, not a "spend cap." The relocated paragraph stays under the renamed §6.2 heading.

The "Cost tracking" stub written in 2026-05-01 (commit `d491ad9`) said the right thing structurally but used "tracking" framing that invited the regression. The new principle statement rules out future regressions definitively.

### §1.2 Decision B — Regression-prevention mechanism

**Architect rec:** **CI grep check (primary)** + **Reviewer rule R13 (secondary)**. Both, not either-or.

CI grep is the strong, mechanical, can't-be-forgotten layer. It runs in `.github/workflows/ci.yml` (or equivalent), greps the tree for the forbidden tokens (`CDB_MAX_SPEND_USD`, `MAX_SPEND_USD`, `DEFAULT_MAX_SPEND`, `spend_cap`, `cost_cap`, `cost-cap-usd`, `--max-spend`), and fails the build on any match outside the allowlist (the allowlist is the historical `docs/status/` directory and `docs/INCIDENTS/` — see §1.3). The Reviewer rule R13 is the doctrinal layer that makes the rule visible to humans reading `SECURITY_AND_HARDENING.md` §9 and gives the Reviewer agent something to cite when rejecting a PR.

Why both: the prior removal had Reviewer awareness ("scope creep ruling," "exit-3 dead code") but no mechanical enforcement. CI grep is the missing piece. Reviewer rule alone is what we had; it is what failed.

### §1.3 Decision C — Historical document allowlist

The CI grep check excludes the following paths because they are append-only audit-trail records of decisions made when the cap mechanism was current:

- `docs/status/**` (all files, including future `docs/status/` files — those are also audit trail and remain immutable post-commit)
- `docs/INCIDENTS/**`
- `docs/3rdpartyreviews/**`
- `docs/proposals/**`
- `docs/PROMPT_EVOLUTION_LOG.md`

Active code, binding docs, tests, and `.env.example` are all in scope for the grep.

### §1.4 Decision D — Memory note rewrite

`/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` is rewritten from a "$10 ceiling for asking permission" framing to a **positive trust-the-provider-dashboard framing**. The new note tells future agents: "LSB does not have software-side cost gates. Don't write cost-estimate paragraphs in plans. Don't ask for cost authorization. Provider billing dashboards are the only authoritative cost-safety mechanism."

The current `feedback_test_budget.md` is dated 2026-05-04 and the system already flagged it as 3 days old / point-in-time. Rewriting it brings the standing memory into alignment with the new posture.

### §1.5 Decision E — `.env.example` disposition

The `CDB_MAX_SPEND_USD=300` line and its preceding comment block (`# Spend cap (ARCHITECTURE.md §6.2)`) are **deleted** from `.env.example`. The file remains tracked. No replacement variable. Existing `.env` files on Mark's machines may still carry `CDB_MAX_SPEND_USD` — that is harmless (no code reads it after this plan lands) and Mark can clean it at his convenience.

---

## §2. Blast radius — file-by-file (post-grep, 2026-05-08)

**Active code (must change):**

| Path | What's in scope | What's preserved |
|---|---|---|
| `scripts/run_phase4b_variance.py` | Module docstring §17, §41, §45, §56 (spend-cap mentions); `DEFAULT_MAX_SPEND_USD` constant L153; `total_spend_usd` field on `CampaignStats` L218 + `add_spend` method L224–226; cost-estimate accumulation in `run_cell` L530–545 (`estimate_cell_cost_usd`, `cell_cost`, `add_spend`, log line `cell_cost_usd=` / `total_spend_usd=`); spend-cap branch in `provider_worker` L663–675; env read L981; stdout print L1038, L1070; log header L1149; `provider_worker` `max_spend_usd` parameter L640 and call site L1171; final summary L1188, L1200, L1203–1207; helper `estimate_cell_cost_usd` L241+ and any callers of it; `"SPEND_CAP"` return value L501; exit-3 path | All non-cost telemetry: `n_pass`, `n_failed`, `n_skipped`, `cells_attempted`, `cells_remaining`. Idempotence, retry logic, rate limits, signal handling, dry-run, compute-rates-only mode, log structure, registry validation. Exit codes 0/1/2 (exit 3 — "spend cap crossed" — is removed). |
| `scripts/rerun_phi4_phase4b_t2.py` | Docstring L21–23 (`CDB_MAX_SPEND_USD=5` block) | Everything else; this script does not read the env var, only documents it. Verified by grep — no functional cap logic in this file. |
| `scripts/rerun_t3_unexplained_phase4b.py` | Docstring L12 (`CDB_MAX_SPEND_USD guard` mention), L32–33 (`CDB_MAX_SPEND_USD=5` invocation example) | Everything else; this script does not read the env var either. |
| `scripts/run_decline_backfill.py` | Module-level docstring "A8 — call-count" stale label (Note N1 from 2026-05-01 Task 3 verdict, never addressed); Section 3b print header "(cost-guard + methodology filter)" L681 (Note N2). Backward-compat shim parameters `cost_per_call=None, spend_cap=None` at L468–491 and L1328–1370 are **kept** — they are documented as ignored backward-compat shims and removing them would break test helpers and external callers. The shim is benign and grepable; the regression risk is in the *active* enforcement code, which was already removed in 2026-05-01. | Call-count gate (`--max-batch-calls`, `DEFAULT_MAX_BATCH_CALLS`, `STOP` / `SURFACE-TO-SME` / `GO` dispositions, `escalation_ratio`, exit codes). The A8 SME Amendment 1 checkpoint stays preserved. |
| `tests/unit/test_run_phase4b_variance.py` | `test_provider_worker_exits_when_spend_cap_reached` L899–945; the test's L10 docstring entry; the `# Test 8` comment block L891–897 | All other tests in the file. Re-number subsequent test sections in comments only if it improves readability. |
| `tests/test_run_decline_backfill.py` | The four `spend_cap=N.NN` keyword-arg call sites that exist purely to exercise the backward-compat shim parameter (L1191, L1206, L1307, L1322, L1546, L1561). The Coder may either (a) delete the `spend_cap=` keyword args while keeping the test functions intact, since `spend_cap` is now a no-op, or (b) keep them — the shim parameter still accepts the kwarg. Architect rec: **option (a), delete the kwargs**, because they reinforce the framing we're trying to remove. The conversion-shim helper at L242–260 (`max_batch_calls = max(1, int(spend_cap / cost_per_call))`) remains useful — keep the helper but rename the parameter from `spend_cap` to `legacy_dollar_threshold` and update the docstring to flag it as a unit-conversion artifact for tests written under the old contract. | Functional decline-backfill behavior tests (call-count gate, STOP, SURFACE-TO-SME). |
| `.env.example` | L21–22 (`# Spend cap (ARCHITECTURE.md §6.2)` + `CDB_MAX_SPEND_USD=300`) — delete both lines | All other env entries. |

**Binding docs (must change):**

| Path | What's in scope |
|---|---|
| `ARCHITECTURE.md` | §6.2 header rename + body replacement (see §3 text). v0.7.3 changelog entry added at top. The §3 repo-layout tree at L364 still mentions `cost_report.py` — delete that line (the file was deleted in 2026-05-01 Task 3 commit `edb9de6`; the tree never got updated). The §7 SUPERSEDED rows at L1490 and L1512 get a second SUPERSEDED date appended (`SUPERSEDED 2026-05-01, reaffirmed 2026-05-08`) referencing this plan; the original text stays. Repo-layout reference numbering at L1586, L1595, L1599, L1617 is in v0.4 historical version-history — leave untouched (audit trail). |
| `CLAUDE.md` | §6 "Binding rules" — add **rule 14**: *"LSB does not enforce software-side spend gates. Cost safety is provided by the provider billing dashboards Mark monitors directly. Authors of scripts, plans, completion reports, status documents, and any other operational text MUST NOT include cost estimates, cost caps, cost-authorization gates, or `CDB_MAX_SPEND_USD`-style env vars. The CI grep check rejects any PR that introduces them; the Reviewer rule R13 is the doctrinal counterpart."* Also: scan §9 "Common pitfalls" and add a new pitfall #14: *"Reintroducing a spend-cap mechanism. The cap framework was removed twice (2026-05-01, 2026-05-08). It produces friction without safety value. CI grep check + Reviewer R13 enforce removal mechanically."* |
| `SECURITY_AND_HARDENING.md` | §1.1 threat-model table row "API key compromise" — replace "per-provider account caps as the Tier 2 spend defense" with "per-provider account caps configured directly on each provider's billing dashboard"; row "DDoS / abusive traffic" — replace "the spend-cap defense covers any operational consequence" with "operational cost is bounded by per-provider account caps configured at the provider, not in code". §9 Reviewer rules table — add **R13: "No software-side spend gates."** with rule text matching `CLAUDE.md` rule 14. v0.1.2 changelog entry. |
| `PHASE_0_TASKS.md` | L55 `.gitignore` checklist line — strip the trailing "`data/cost_reports/*.txt` is **NOT** ignored" clause (the directory was deleted 2026-05-01 Task 3); L56 — strip `CDB_MAX_SPEND_USD=300` from the `.env.example` placeholder list. |
| `docs/SHAKEDOWN_PROTOCOL.md` | L7 companion-doc reference to "§6.2 (spend cap)" → "§6.2 (cost posture)". L87 precondition #4 ("Spend cap env override active. Export `CDB_MAX_SPEND_USD=25`...") — replace with: *"Per the 2026-05-08 spend-cap-removal plan, no env-var spend cap applies. Real-time billing-dashboard awareness is the only operational cost safety."* L138 (`export CDB_MAX_SPEND_USD=25`) — delete the export line. L235 (sanity check "All cells collected without exceeding the `CDB_MAX_SPEND_USD=25` cap") — replace with "All cells collected within the operator's awareness of provider billing-dashboard state". |
| `docs/BOOTSTRAP_DESIGN.md` | L93 "monthly spend cap" — replace with "available compute budget" (this is forward-looking Phase 2 design language; no behavioral hook to a code mechanism). |

**Memory (out-of-tree):**

| Path | What's in scope |
|---|---|
| `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` | Full rewrite (see §1.4 + replacement text in §3). New title: "No software-side spend gates." Type: `feedback`. |

**Files NOT modified (audit-trail / historical):**

- `docs/status/2026-05-01-spend-cap-removal-task1-reviewer-verdict.md`
- `docs/status/2026-05-01-spend-cap-removal-task2-reviewer-verdict.md`
- `docs/status/2026-05-01-spend-cap-removal-task3-reviewer-verdict.md`
- `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md`
- `docs/status/2026-04-23-phase4a1-*` (all)
- `docs/status/2026-05-05-phase4a-recovery-*` (all)
- `docs/status/2026-05-06-phase4a-completion-redo.md`
- `docs/status/2026-05-07-phase4b-architect-plan.md` (current plan; superseded but immutable per preamble override)
- `docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md`
- `docs/status/2026-05-07-phase4b-t3-*`
- `docs/status/2026-05-08-phase4b-t4-*`
- `docs/status/2026-05-07-phase4b-t3-tail-failures-memo.md`
- `docs/INCIDENTS/2026-04-19-test-data-loss.md`
- `docs/PROMPT_EVOLUTION_LOG.md` L49, L65 (historical references in changelog/footnotes)
- `docs/3rdpartyreviews/gemini project_review.md`
- `docs/proposals/2026-04-20-sme-open-questions.md`

---

## §3. Verbatim replacement texts

### §3.1 New `ARCHITECTURE.md` §6.2 body

```
### 6.2 Cost posture

**Principle (binding, 2026-05-08).** LSB does not enforce software-side spend gates. Cost safety is provided by the provider billing dashboards Mark monitors directly (Anthropic, OpenAI, Google AI Studio, xAI, OpenRouter, Hugging Face). Authors of scripts, plans, completion reports, and status documents do not include cost estimates, cost caps, cost-authorization gates, or `CDB_MAX_SPEND_USD`-style env vars. Per-provider hard caps are configured at the provider, not in code.

**Why this is binding, not advisory.** The cap mechanism was removed once on 2026-05-01 (commits d491ad9 → edb9de6) and regressed within seven days. The regression went through the standard Architect → Coder → Reviewer → Tester pipeline because the framing in this section was soft enough to accommodate it. The 2026-05-08 removal closes this with two enforcement layers: a CI grep check that rejects any PR introducing the forbidden tokens (`CDB_MAX_SPEND_USD`, `MAX_SPEND_USD`, `spend_cap`, `cost_cap`, `--max-spend`), and Reviewer rule R13 in `SECURITY_AND_HARDENING.md` §9.

**Anthropic prompt caching for orchestrator calls (binding, added v0.6, retained 2026-05-08).** All static documents passed into agent API calls — `ARCHITECTURE.md`, `CLAUDE.md`, `SECURITY_AND_HARDENING.md`, `HOSTING_AND_DEV_OPS.md`, `PHASE_0_TASKS.md`, `docs/DATA_DICTIONARY.md`, the §1.5.4 language guardrails table, and any other long-lived context the orchestrator passes into Claude — must use Anthropic prompt caching. These documents are large, change rarely, and are passed into nearly every agent task. Without caching, every task pays the full input-token cost on every invocation. With caching, the per-task orchestrator cost drops by approximately 80%. Implementation: pass `cache_control={"type": "ephemeral"}` on the relevant content blocks per the Anthropic API docs. The Reviewer agent must reject any orchestrator call that passes one of the listed static documents without prompt caching enabled — this is a binding cost-control rule on agent-call construction (not a spend gate on collection runs), and it is the only cost-control mechanism that lives in code. Per-document caching keys should be derived from the file's git SHA so that an updated document invalidates its own cache without forcing a full rebuild.
```

### §3.2 New `CLAUDE.md` §6 rule 14

```
14. **No software-side spend gates.** LSB does not enforce cost caps, cost authorization, or `CDB_MAX_SPEND_USD`-style env vars in code. Cost safety is provided by the provider billing dashboards Mark monitors directly. Authors of scripts, plans, completion reports, status documents, and any other operational text MUST NOT include cost estimates, cost caps, or cost-authorization gates. The CI grep check (`.github/workflows/ci.yml` step `no-spend-gate-check`) rejects any PR introducing the forbidden tokens; Reviewer rule R13 (`SECURITY_AND_HARDENING.md` §9) is the doctrinal counterpart. The single exception is the Anthropic prompt-caching binding rule on orchestrator calls (`ARCHITECTURE.md` §6.2), which is a per-call construction rule, not a spend gate on collection runs.
```

### §3.3 New `CLAUDE.md` §9 pitfall 14

```
14. **Reintroducing a spend-cap mechanism.** The `CDB_MAX_SPEND_USD` framework was removed twice (2026-05-01 across three commits; 2026-05-08 definitively). It produces friction (script aborts, agent hesitation, hook denials, dispatch friction) without producing safety value — actual API spend has been 2–3 orders of magnitude below the estimates the framework was sized against. CI grep check + Reviewer R13 enforce removal mechanically. If you find yourself wanting to add "just one more guard" in a script or "just a small estimate paragraph" in a plan: don't. Mark monitors provider billing dashboards directly; that is the cost safety.
```

### §3.4 New `SECURITY_AND_HARDENING.md` §9 row R13

```
| **R13** | **No software-side spend gates.** No `CDB_MAX_SPEND_USD` env var, no `MAX_SPEND_USD` constants, no `spend_cap` parameters in active code, no cost-estimate paragraphs in architect plans / completion reports / status docs going forward. CI grep check is the mechanical enforcement; the Reviewer agent backs it up by rejecting any PR that introduces cost-cap framing in active code or in new (post-2026-05-08) plans and reports. The single exception is the Anthropic prompt-caching binding rule on orchestrator agent calls, which is a per-call construction rule, not a spend gate. | `ARCHITECTURE.md` §6.2, `CLAUDE.md` §6 rule 14 |
```

### §3.5 New CI grep check (workflow step)

The Coder will add a step to `.github/workflows/ci.yml` (or, if no such workflow exists, create the file with this single check). The step name is `no-spend-gate-check`. It runs after checkout and before any other test step. Pseudocode:

```yaml
- name: no-spend-gate-check
  run: |
    set -e
    FORBIDDEN='CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend'
    HITS=$(git grep -nE "$FORBIDDEN" -- \
      ':(exclude)docs/status/' \
      ':(exclude)docs/INCIDENTS/' \
      ':(exclude)docs/3rdpartyreviews/' \
      ':(exclude)docs/proposals/' \
      ':(exclude)docs/PROMPT_EVOLUTION_LOG.md' \
      ':(exclude).github/workflows/ci.yml' \
      || true)
    if [ -n "$HITS" ]; then
      echo "::error::Forbidden spend-gate token(s) detected:"
      echo "$HITS"
      echo ""
      echo "See ARCHITECTURE.md §6.2, CLAUDE.md rule 14, SECURITY_AND_HARDENING.md R13."
      exit 1
    fi
    echo "no-spend-gate-check: PASS"
```

The exclusion of `.github/workflows/ci.yml` itself is necessary because the check's pattern strings appear literally in the workflow file. If the project already has CI configured locally (Mark's preference per `CLAUDE.md` §8 is direct-to-master with no CI re-run), the Coder still creates the file — it serves as a documented mechanical guard that runs whenever CI does run, including for any future branch+PR work.

### §3.6 Memory note rewrite

Path: `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md`

The current note is titled "Standing $10 test budget" and its core text says "Don't ask for cost-estimate authorization on LSB probes/tests under $10." It will be replaced wholesale. New file content:

```
---
name: No software-side spend gates
description: LSB does not enforce cost caps in code. Trust provider billing dashboards. Don't write cost estimates in plans.
type: feedback
originSessionId: <Coder fills with the session id at the time of the rewrite>
---
LSB does not have software-side spend gates. The `CDB_MAX_SPEND_USD` mechanism was removed twice (2026-05-01, 2026-05-08) because (a) it produces friction without safety value and (b) cost estimates have been 2–3 orders of magnitude off from actual spend. Yesterday's full-day collection cost $0.004; the active plan estimated $120–$300.

**How to apply:**
- For LSB API probes / collection runs / validation tests: just run them. Don't estimate cost. Don't ask for cost authorization. Don't write a cost paragraph in the plan. Mark monitors provider billing dashboards directly — that is the cost safety.
- This applies project-wide, not just to "small" probes. There is no $10 ceiling, no $50 session cap, no $300 monthly cap in code.
- The only cost-control mechanism that lives in code is Anthropic prompt caching on orchestrator agent calls (`ARCHITECTURE.md` §6.2). That is a per-call construction rule, not a spend gate on collection runs. It stays binding.
- This rule is LSB-scoped. For other projects without a stated posture, default back to surfacing costs.
- This does NOT relax other authorization needs (modifying production data, writing to the canonical corpus, irreversible operations) — only the cost-estimate friction.

**Enforcement:**
- CI grep check (`no-spend-gate-check`) blocks PRs that introduce `CDB_MAX_SPEND_USD`, `MAX_SPEND_USD`, `spend_cap`, `cost_cap`, `cost-cap-usd`, `--max-spend`, or `DEFAULT_MAX_SPEND` outside of historical `docs/status/`, `docs/INCIDENTS/`, `docs/3rdpartyreviews/`, `docs/proposals/`, and `docs/PROMPT_EVOLUTION_LOG.md`.
- Reviewer rule R13 (`SECURITY_AND_HARDENING.md` §9) is the doctrinal counterpart.

**Origin:** 2026-05-08 architect plan at `docs/status/2026-05-08-spend-cap-removal-architect-plan.md`. Mark's directive: "We have to backtrack and remove all references to spending caps out of this project. It is causing us way more trouble than it's worth, completely inaccurate."
```

---

## §4. Task decomposition (Coder-sized, one commit each)

**Five tasks, executed in this order. SC-T1 is first because it unblocks the Phase 4b T4 launch.**

| # | Task ID | Title | Files touched | Acceptance criteria |
|---|---|---|---|---|
| 1 | **SC-T1** | Strip cap mechanism from `run_phase4b_variance.py` (unblocks Phase 4b T4 launch) | `scripts/run_phase4b_variance.py`; `tests/unit/test_run_phase4b_variance.py` | (a) All §2 in-scope items removed from the script. (b) `test_provider_worker_exits_when_spend_cap_reached` deleted; the `# Test 8` comment block deleted; the L10 docstring item deleted. (c) `provider_worker` signature loses `max_spend_usd` parameter; main caller stops passing it; the env-read line deleted; the `DEFAULT_MAX_SPEND_USD` constant deleted; `CampaignStats.total_spend_usd` and `add_spend` deleted; `estimate_cell_cost_usd` helper and all call sites deleted; the `"SPEND_CAP"` outcome string and exit-3 path deleted; spend-related stdout prints and log lines deleted. (d) Module docstring §17, §41, §45, §56 lines rewritten to drop spend-cap framing. (e) `uv run pytest && uv run ruff check . && uv run mypy packages/` all green. (f) `git grep -nE 'CDB_MAX_SPEND_USD\|MAX_SPEND_USD\|DEFAULT_MAX_SPEND\|spend_cap\|cost_cap\|cost-cap-usd' -- scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py` returns zero hits. (g) The script's `--dry-run` mode still produces a sensible plan summary without cost framing. |
| 2 | **SC-T2** | Strip cap framing from secondary scripts and `.env.example` | `scripts/rerun_phi4_phase4b_t2.py` (docstring only); `scripts/rerun_t3_unexplained_phase4b.py` (docstring only); `scripts/run_decline_backfill.py` (Notes N1 + N2 only — module docstring L27 + Section 3b print header L681; do NOT touch the backward-compat shim parameters); `tests/test_run_decline_backfill.py` (Architect rec option (a): delete the six `spend_cap=N.NN` kwargs at L1191/1206/1307/1322/1546/1561 and rename the `spend_cap` parameter on the helper at L242 to `legacy_dollar_threshold` with updated docstring); `.env.example` (delete L21–22) | (a) `uv run pytest && uv run ruff check . && uv run mypy packages/` green. (b) Decline-backfill behavioral tests still pass (call-count gate intact). (c) `.env.example` no longer contains any cost reference. (d) `git grep -nE 'CDB_MAX_SPEND_USD' -- scripts/ tests/ .env.example` returns zero hits. (e) The `cost_per_call=None, spend_cap=None` backward-compat shim parameters in `run_decline_backfill.py` are still present (renaming them is out of scope and would break external callers); only the stale labels are fixed. |
| 3 | **SC-T3** | Update binding docs: ARCHITECTURE.md §6.2, CLAUDE.md §6/§9, SECURITY_AND_HARDENING.md §1.1/§9, PHASE_0_TASKS.md, SHAKEDOWN_PROTOCOL.md, BOOTSTRAP_DESIGN.md | The six binding/operational docs listed in §2 | (a) `ARCHITECTURE.md` §6.2 body matches §3.1 verbatim. v0.7.3 changelog entry added at top of file referencing this plan. The §3 repo-layout `cost_report.py` line at L364 is deleted. The §7 SUPERSEDED rows at L1490 and L1512 get the `, reaffirmed 2026-05-08` annotation appended. (b) `CLAUDE.md` §6 has new rule 14 matching §3.2; §9 has new pitfall 14 matching §3.3. (c) `SECURITY_AND_HARDENING.md` §1.1 threat-model rows updated per §2; §9 has new row R13 matching §3.4; v0.1.2 changelog entry. (d) `PHASE_0_TASKS.md` L55 stripped of cost_reports clause; L56 `.env.example` placeholder list no longer mentions `CDB_MAX_SPEND_USD=300`. (e) `SHAKEDOWN_PROTOCOL.md` L7, L87, L138, L235 updated per §2. (f) `BOOTSTRAP_DESIGN.md` L93 "monthly spend cap" → "available compute budget". (g) `git grep -nE 'CDB_MAX_SPEND_USD\|spend cap\|spend-cap\|three-tier defense\|cost cap'` across `ARCHITECTURE.md CLAUDE.md SECURITY_AND_HARDENING.md PHASE_0_TASKS.md docs/SHAKEDOWN_PROTOCOL.md docs/BOOTSTRAP_DESIGN.md` returns only the §6.2 "spend gate" / "spend cap" mentions inside the new principle text and the §7 SUPERSEDED rows in `ARCHITECTURE.md`. (h) `uv run pytest && uv run ruff check . && uv run mypy packages/` green. |
| 4 | **SC-T4** | Add CI grep check for regression prevention | `.github/workflows/ci.yml` (or create if absent) | (a) `no-spend-gate-check` step matches §3.5 pseudocode (workflow-syntax adjustments allowed). (b) The step runs first or near-first in the workflow. (c) The step's exclusion list matches §1.3 verbatim. (d) Coder runs the equivalent grep locally (`git grep -nE '<pattern>' -- ':(exclude)<paths>'`) and reports zero hits in the commit body. (e) The step's failure message references `ARCHITECTURE.md §6.2`, `CLAUDE.md` rule 14, and `SECURITY_AND_HARDENING.md` R13. (f) If `.github/workflows/ci.yml` does not exist before this commit, the Coder creates it with **only** the checkout step + the `no-spend-gate-check` step (no other CI work bundled). |
| 5 | **SC-T5** | Memory rewrite | `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` (out-of-tree; not a git commit; updated as a separate operation per `feedback_dispatch_hygiene.md`) | (a) File contents match §3.6 verbatim, with the Coder filling in the originSessionId field. (b) The file's prior content is overwritten in full; no append. (c) Because this is an out-of-tree file, no git commit. The Coder reports completion in the dispatch summary so the orchestrator's per-step `git status --short` hygiene check does not flag stray changes. |

**Note on commit hygiene per `CLAUDE.md` §8 + `feedback_dispatch_hygiene.md`:** Each of SC-T1 through SC-T4 is exactly one commit. Memory updates (SC-T5) are out-of-tree and do not touch the git index — but if the Coder agent's session causes any other memory-file side effects, those go in a separate `chore(memory):` commit before the next SC-T task starts.

---

## §5. Dependency graph

```
                          (start)
                             │
                             ▼
                          SC-T1  ◀── unblocks Phase 4b T4 launch
                             │
                             ▼
                          SC-T2
                             │
                             ▼
                          SC-T3
                             │
                             ▼
                          SC-T4  ◀── regression prevention now live
                             │
                             ▼
                          SC-T5  (out-of-tree; can also run in parallel after SC-T4)
                             │
                             ▼
                          (Phase 4b T4 launch dispatched by orchestrator)
```

**Why SC-T1 first.** Mark's directive opens with "Before we start this run." The "this run" is Phase 4b T4. The T4 launch is currently gated on the cap mechanism — script aborts on hook-denied authorization. SC-T1 alone is sufficient to unblock the launch. SC-T2 through SC-T5 can land in series afterward without delaying the run; they close the regression door but do not block the immediate operational need.

**Why SC-T4 (CI grep) lands before SC-T5 (memory).** The CI grep is the mechanical regression guard. Memory is doctrinal. We want the mechanical guard live before any subsequent task touches a script — even SC-T5 — to catch any inadvertent reintroduction at the earliest possible point.

**Why not bundle.** Each task touches a distinct concern (active script / secondary scripts + env / binding docs / CI / memory). Bundling violates `CLAUDE.md` §8 "one commit per task" and makes per-task Reviewer verdicts ambiguous. Bundling also makes per-task rollback harder if any one task surfaces an unexpected issue.

---

## §6. Reviewer enforcement per task

The Reviewer agent runs the standard nine-check scorecard on each task plus the task-specific items below. **Verdict files saved to `docs/status/2026-05-08-spend-cap-removal-{task-id}-reviewer-verdict.md`**.

**SC-T1 specific Reviewer items:**
- A. Confirm `provider_worker` no longer has `max_spend_usd` parameter and main caller no longer passes it.
- B. Confirm `CampaignStats` no longer has `total_spend_usd` / `add_spend`; confirm `n_pass`/`n_failed`/`n_skipped` still present.
- C. Confirm exit code 3 is removed from the docstring exit-codes block; only 0/1/2 remain.
- D. Confirm `--dry-run` output produces a sensible plan summary with no cost lines.
- E. Confirm test count drop matches deleted-test count exactly (one test deleted; if the file had N tests, post-commit should be N−1).
- F. `git grep -nE 'CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend|estimate_cell_cost_usd|total_spend_usd|add_spend' -- scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py` returns zero hits.
- G. `uv run pytest tests/unit/test_run_phase4b_variance.py` passes; `uv run mypy scripts/run_phase4b_variance.py` clean.

**SC-T2 specific Reviewer items:**
- A. The two rerun scripts' docstrings no longer reference `CDB_MAX_SPEND_USD` (these scripts had only docstring mentions; no functional changes expected).
- B. `run_decline_backfill.py` Notes N1 and N2 fixed: module docstring L27 says "call-count" not "cost"; Section 3b print header says "(call-count gate + methodology filter)" not "(cost-guard + methodology filter)".
- C. `run_decline_backfill.py` backward-compat shim parameters at L468–491 and L1328–1370 are **unchanged** (the Coder did not delete them). The A8 SME Amendment 1 checkpoint is fully preserved.
- D. `.env.example` no longer contains `CDB_MAX_SPEND_USD` or any cost reference.
- E. `tests/test_run_decline_backfill.py` either kept the `spend_cap=` kwargs (option (b)) or deleted them and renamed the helper parameter (option (a)) — Architect rec was option (a). Reviewer accepts either, but if option (a) was chosen, all six call sites must use the new parameter name.
- F. `git grep -nE 'CDB_MAX_SPEND_USD' -- scripts/ tests/ .env.example` returns zero hits.
- G. Decline-backfill tests all pass; the existing call-count gate scenarios (STOP, SURFACE-TO-SME, GO) still execute.

**SC-T3 specific Reviewer items:**
- A. `ARCHITECTURE.md` §6.2 body is **byte-identical** to §3.1 verbatim text in this plan, modulo Markdown rendering. The Reviewer reads §3.1 and the post-commit §6.2 side-by-side.
- B. `ARCHITECTURE.md` v0.7.3 changelog entry is at the **top** of the changelog block, references this plan path, and uses the date 2026-05-08.
- C. `ARCHITECTURE.md` §3 repo-layout L364 (`cost_report.py` line) is deleted.
- D. `ARCHITECTURE.md` §7 rows 2 and 24 still contain the original "SUPERSEDED 2026-05-01" text (audit trail) and have `, reaffirmed 2026-05-08` appended only.
- E. `CLAUDE.md` §6 rule 14 is byte-identical to §3.2 verbatim text.
- F. `CLAUDE.md` §9 has a new pitfall 14 matching §3.3.
- G. `SECURITY_AND_HARDENING.md` §9 row R13 is byte-identical to §3.4 verbatim text.
- H. `SECURITY_AND_HARDENING.md` §1.1 threat-model rows reworded per §2.
- I. `SECURITY_AND_HARDENING.md` v0.1.2 changelog entry added.
- J. `PHASE_0_TASKS.md` L55 and L56 cleaned.
- K. `docs/SHAKEDOWN_PROTOCOL.md` four locations cleaned.
- L. `docs/BOOTSTRAP_DESIGN.md` L93 cleaned.
- M. The forbidden-vocabulary §1.5.4 list is unchanged (this is a cost-cap removal, not a vocabulary update).
- N. No file under `docs/status/`, `docs/INCIDENTS/`, `docs/3rdpartyreviews/`, `docs/proposals/`, or `docs/PROMPT_EVOLUTION_LOG.md` is touched.
- O. `git grep` regression check across the six docs returns only allowed hits (the `Cost posture` section header + the principle text + the SUPERSEDED rows).

**SC-T4 specific Reviewer items:**
- A. `.github/workflows/ci.yml` exists post-commit. If it existed before this commit, the diff is additive (single new step inserted near the top); if not, it is a new file with only the checkout step + the `no-spend-gate-check` step.
- B. The step's pattern matches `CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend` — verbatim from §1.3 / §3.5.
- C. The exclusion list matches §1.3 verbatim.
- D. The error message references `ARCHITECTURE.md §6.2`, `CLAUDE.md` rule 14, and `SECURITY_AND_HARDENING.md` R13.
- E. Reviewer runs the same grep locally and reports zero hits — proving the check would PASS on the post-commit tree.
- F. The Reviewer artificially adds a single test pattern (e.g., grep for the literal `CDB_MAX_SPEND_USD` in a throwaway file path that the script does not commit) and confirms the grep would catch it. This is a smoke test; the throwaway file is not committed.
- G. CI workflow YAML is syntactically valid (`yamllint` pass, or the equivalent in the repo's tooling).

**SC-T5 specific Reviewer items:**
- A. The memory file content matches §3.6 verbatim, modulo the originSessionId field.
- B. The file's prior content is fully overwritten (the Coder's session-end git status confirms no in-tree memory file changes; the out-of-tree memory file is overwritten directly).
- C. No git commit — Reviewer confirms this is correctly out-of-tree.

---

## §7. Tester scope

| Task | Tests removed | Tests added | Tester actions |
|---|---|---|---|
| **SC-T1** | `test_provider_worker_exits_when_spend_cap_reached` | None | Confirm test count delta is exactly −1. Run `uv run pytest tests/unit/test_run_phase4b_variance.py -v` and inspect that no remaining test name references spend / cap / cost. Confirm `--dry-run` mode still works end-to-end. |
| **SC-T2** | None (test functions retained; only kwarg call sites changed) | None | Confirm all decline-backfill tests still pass (`uv run pytest tests/test_run_decline_backfill.py`). Confirm the helper-parameter rename (if Architect rec option (a) chosen) compiles and the renamed parameter is used consistently across all call sites. |
| **SC-T3** | None | None | Run `uv run pytest && uv run ruff check . && uv run mypy packages/`. Confirm no test references the renamed `ARCHITECTURE.md §6.2` section by old name in a way that breaks. (Tests do not generally reference doc section numbers, but the Tester confirms.) |
| **SC-T4** | None | The CI grep check itself acts as a "test" against future regressions; it is its own coverage | Tester runs the workflow step locally (or simulates with a shell script) on (a) the current tree → expect PASS, (b) a tree with `CDB_MAX_SPEND_USD` introduced into `scripts/foo.py` → expect FAIL with the documented error message. The Tester does not commit the FAIL-case tree. |
| **SC-T5** | None | None | Tester confirms (a) the memory file content matches §3.6 verbatim modulo originSessionId, (b) the file's mtime is post-commit-of-SC-T4, (c) no in-tree side effects from the rewrite. |

**Tester verdict files saved to `docs/status/2026-05-08-spend-cap-removal-{task-id}-tester-verdict.md`** following the standard PASS / PASS-WITH-NOTES / FAIL format.

---

## §8. Reading list per task (Coder)

Every task: read this plan in full plus `CLAUDE.md` (especially §6 binding rules and §8 commit hygiene) before starting.

| Task | Additional required reading |
|---|---|
| **SC-T1** | `scripts/run_phase4b_variance.py` (full file); `tests/unit/test_run_phase4b_variance.py` (full file); `docs/status/2026-05-07-phase4b-architect-plan.md` §8 T4 row (for context on what T4 does, so the Coder doesn't break unrelated functionality) |
| **SC-T2** | `scripts/rerun_phi4_phase4b_t2.py` (full file); `scripts/rerun_t3_unexplained_phase4b.py` (full file); `scripts/run_decline_backfill.py` (full file — large; the Coder needs to find Notes N1 and N2 specifically and confirm the shim parameters are intact); `tests/test_run_decline_backfill.py` L240–260 helper, L1191/1206/1307/1322/1546/1561 call sites; `.env.example` (full); `docs/status/2026-05-01-spend-cap-removal-task3-reviewer-verdict.md` Notes N1 and N2 (for context on what was deferred) |
| **SC-T3** | `ARCHITECTURE.md` §6.2 (current); §3 repo-layout block at L362–369; §7 rows 2 and 24; v0.7.x changelog block; `CLAUDE.md` §6 (full) and §9 (full); `SECURITY_AND_HARDENING.md` §1.1 (full table) and §9 (full table); `PHASE_0_TASKS.md` L50–60; `docs/SHAKEDOWN_PROTOCOL.md` L7, L80–95, L130–145, L230–240; `docs/BOOTSTRAP_DESIGN.md` L88–96 |
| **SC-T4** | `CLAUDE.md` §8 (commit hygiene); `.github/workflows/ci.yml` (if it exists); GitHub Actions workflow syntax docs (if the Coder is unsure) |
| **SC-T5** | `/home/lsb/.claude/projects/-opt-lsb-agent/memory/feedback_test_budget.md` (current); `feedback_dispatch_hygiene.md` (memory note about between-dispatch hygiene); the originSessionId convention used in other memory notes in the same directory |

---

## §9. Phase 4b T4 disposition (explicit)

**Phase 4b T4 launch is gated on SC-T1 landing.** Once SC-T1 is committed and Reviewer + Tester have issued PASS verdicts, the orchestrator may dispatch the T4 launch — the T4 script will then run without any cost authorization gate. SC-T2 through SC-T5 land in series after SC-T1 but **do not gate** the T4 launch; they close the regression door but do not block the immediate operational need that motivated this plan.

If the orchestrator wants to be conservative and wait for SC-T4 (CI grep) to land before dispatching T4, that is acceptable but not required by Mark's directive. Architect rec: **launch T4 after SC-T1**, in parallel with SC-T2/T3/T4/T5 progressing through the pipeline. The T4 run itself takes 2–4 days of campaign wall-clock per the (now-superseded) Phase 4b plan estimate; SC-T2 through SC-T5 will land well within that window.

---

## §10. Out of scope (explicit)

- **The Phase 4b T4 run itself** — orchestrator dispatches; Architect does not.
- **The Phase 4b architect plan §9 cost transparency** — the plan stays committed as-is (audit trail). Its cost framing is null and void from the moment this plan is committed; this is captured in §0 of this plan.
- **Methodology-page or dashboard-facing copy** — operational change only; no public-facing surface area.
- **CDA SME gate** — no methodology change.
- **UI/UX gate** — no frontend work.
- **Renaming or removing the `cost_per_call=None, spend_cap=None` backward-compat shim parameters in `run_decline_backfill.py`** — out of scope; deleting them would break external test helpers and offers no regression-prevention value because they are no-ops. The CI grep correctly catches *new* introductions; the existing shim parameters are grandfathered. (The CI grep pattern includes `spend_cap`, which would flag these — but the function-signature lines containing them are inside `scripts/run_decline_backfill.py`, which is not in the exclusion list. **Architect resolution:** the Coder for SC-T4 adjusts the regex to exclude the precise `scripts/run_decline_backfill.py` shim lines via a path-line allowlist comment (e.g., a `# noqa: spend-gate-check` style marker), OR the SC-T2 Coder takes Architect rec option (a) and renames `spend_cap` → `legacy_dollar_threshold` in the shim parameter, eliminating the conflict entirely. **Architect rec: option (a) — rename in SC-T2**, so SC-T4's CI grep is clean without any allowlist gymnastics. The Reviewer for SC-T4 verifies that the post-SC-T2 tree produces zero grep hits.)
- **Future cost-related work** — none planned. If Mark later decides the project needs cost telemetry (e.g., per-run token counts for academic publication), that is a separate plan with its own Architect cycle.

---

## §11. Gate verdict file paths (forward references)

Once tasks land, verdict files will be saved at:

- Coder commit messages reference task ID `SC-T{1..5}` and this plan path.
- `docs/status/2026-05-08-spend-cap-removal-sc-t1-reviewer-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t1-tester-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t2-reviewer-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t2-tester-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t3-reviewer-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t3-tester-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t4-reviewer-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t4-tester-verdict.md`
- `docs/status/2026-05-08-spend-cap-removal-sc-t5-reviewer-verdict.md` (memory rewrite — Reviewer confirms out-of-tree only)
- `docs/status/2026-05-08-spend-cap-removal-sc-t5-tester-verdict.md`

---

## §12. Sign-off

This plan is authored by the Architect agent (Opus 4.7) on 2026-05-08 in response to Mark's verbatim directive in §0. No CDA SME gate is required (no methodology change). No UI/UX gate is required (no frontend work). The plan is binding on the Coder, Reviewer, and Tester for tasks SC-T1 through SC-T5.

**Architect:** _LSB Architect agent (Opus 4.7), 2026-05-08_

---

# End of plan.
