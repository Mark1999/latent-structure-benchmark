# Ops Console v1: Campaign Runner Spec and Operating Matrix

**Document:** `docs/proposed/2026-07-10-ops-console-campaign-runner-spec.md`
**Status:** PROPOSED. Requested by Mark (2026-07-10) after the batch A campaign made the
token-burn pattern concrete. Extends Option 3 of
`docs/proposed/2026-07-09-admin-console-access-proposal.md`; needs an Architect plan
before any code.
**Prime directive:** CLAUDE.md §8, programmatic before generative. Day-to-day lab
operation is scripts behind buttons. LLM dispatches are click-triggered, scoped, and
tiered; none are resident and none run on cron (the Phase 7 B-1 boundary generalizes:
the console may RUN scripts autonomously, but every LLM call is an explicit click).

---

## 1. Evidence base: batch A, 2026-07-10

One campaign day, run through the CLI agent, decomposes as follows. Everything in the
first list was executed as ad hoc shell/Python by the orchestrating agent and produced
deterministic results; it is all scriptable.

**Was mechanical (no model needed):**
- Registry scan and update; slate verification against the catalog
- Campaign planning: per-cell shortfall computation (target minus passed records)
- Lane generation and parallel launch; per-model log files
- Log monitoring with failure-signature alerts (404/400/credit/parse patterns)
- Stop/resume of individual lanes; idempotent re-planning after interruptions
- Pass/fail matrices per model x domain; QA failure histograms per check
- Parser replays over stored records (pile-sort re-parse)
- Anomaly statistics: chars-per-token medians, refusal-rate counts, latency tallies
- Preflight checks (reasoning-class representation; N11-style density detector)
- API liveness pings; model_version_returned reroute scan
- Rebaseline invocation, guard evaluation, numeric-deltas rendering (already scripted)

**Needed judgment (LLM or Mark):**
- Four CDA SME rulings (forced-default sampling; reasoning-QA calibration;
  dense-tokenizer addendum; refused-informant disposition)
- One Architect plan (recalibration decomposition, N5 disposition)
- Code implementation and review (Coder, Reviewer, Tester)
- Interpretation of anomalies AFTER detectors surfaced them (what does a 100 percent
  refusal rate mean for informant status)
- Mark: billing, promotion authorization, slate composition

The ratio matters: tens of mechanical operations per judgment call. The console's job
is to make the first list buttons and the second list rare, explicit dispatches.

## 2. Operating matrix (standing policy)

| Activity | Mode | Mechanism |
|---|---|---|
| Model discovery, registry updates | Programmatic | `discover_models.py` behind a button; diff view before write |
| Campaign planning (cells, runs, shortfalls) | Programmatic | computed from informants.jsonl, never estimated |
| Collection launch / resume / stop | Programmatic | generated lane scripts; per-lane controls |
| Live monitoring, failure signatures | Programmatic | log tailing + pattern table; alert row in UI |
| QA tallies, failure breakdowns | Programmatic | `qa_check.py` per record; histogram per check per model |
| Anomaly detectors (density, refusal rate, latency) | Programmatic | thresholds from SME rulings; warn-only rows |
| Preflight checks before rebaseline | Programmatic | `preflight_reasoning_class_representation.py` et al. |
| Rebaseline to staging + guard status | Programmatic | `rebaseline_corpus.py`; guards halt as designed |
| Publish build, deploy verify | Programmatic | `publish.py`; curl checks |
| New-domain prompt drafting/refinement | AI on dispatch | Tier 1 path; CDA SME gate; versioned prompt dirs |
| Gate rulings (SME, UI/UX, Reviewer) | AI on dispatch | click-dispatched with computed facts attached |
| Anomaly disposition when a detector fires | AI on dispatch | SME dispatch template pre-filled with the numbers |
| Social drafts | AI on dispatch | existing sole sanctioned site (admin console) |
| Code changes | AI pipeline | Architect to Tester, unchanged |
| Promotion to live, slate composition, billing | Mark only | console displays, never decides |

## 3. Campaign runner v1 (console scope)

Extends the existing `cdb_social` admin console Flask app (same package, same loopback
posture; remote access per the 2026-07-09 proposal's pending tailscale decision).

**Panel 1, New campaign.** Domain selector (existing domains from manifest; free-text
for a new domain routes to the prompt-drafting dispatch instead of a run). Model
multi-select from `registry.json` with collected-record counts shown. Runs per cell
(default 5, shows the per-domain precedent). Generates campaign id, shows the dry-run
plan (the same output as `collect.py --dry-run` per cell), and a Launch button.

**Panel 2, Live board.** Model x domain matrix of passed/failed/in-flight computed
from informants.jsonl plus lane process state. Per-lane tail view. Alert rows on
failure signatures (the batch A pattern table: auth, billing, 404, parse-after-retries,
refusal streak). Per-lane Stop. Resume button recomputes shortfalls and relaunches
only what is missing.

**Panel 3, QA.** Per-model failing-check histogram. A recompute-under-current-rules
view (the corpus-build re-QA semantics) showing persisted vs recomputed divergence.
Detector warnings (density roster candidates, refusal rates) with a copy-ready SME
dispatch template pre-filled with the computed numbers.

**Panel 4, Rebaseline (read-mostly).** Buttons: run preflight, run rebaseline to
staging. Displays: guard status, THRESHOLD-CROSSING files, numeric-deltas tables
rendered. Explicit non-goal: NO promote button in v1. Promotion stays on the gated
CLI path (Reviewer, SME provenance, UI/UX footer), per the runbook.

**Panel 5, Dispatch.** The only LLM-invoking surface. Buttons per dispatch type
(SME ruling, Architect plan, prompt draft, social draft), each showing the model tier
it will use and the prepared prompt (facts pre-filled programmatically) before Mark
clicks Send. Every dispatch and its verdict lands in docs/status/ per existing
conventions.

## 4. Model-tier policy for dispatches

Qualitative tiers; exact ids resolved from the registry at dispatch time. No
premium-tier (Fable-class) model is used for any operational dispatch.

| Dispatch | Tier | Rationale |
|---|---|---|
| CDA SME rulings, Architect plans | Opus-class | judgment that gates published claims |
| Reviewer, Tester, Coder | Sonnet-class | current pipeline assignment, unchanged |
| Prompt refinement, social drafts | Sonnet-class, Haiku-class acceptable for mechanical rewording | drafting against fixed templates and validators |
| Day-to-day CLI orchestration (until the console absorbs it) | Opus-class or Sonnet-class session | switch the interactive session model; reserve premium tier for rare hardest-problem sessions |

Cross-provider drafter alternatives (via the existing OpenRouter adapter) are noted as
an option if drafter volume ever grows; not part of v1.

## 5. Boundaries

- Rule 15: the console renders analysis outputs; it never computes or modifies
  statistical measures.
- B-1 generalized: no autonomous LLM invocation anywhere in the console; scripts may
  run on click or on lane-completion chaining, LLM dispatches only on click.
- Append-only: all record views are read-only; no mutation surfaces exist.
- Internal-ops gating per the 2026-06-08 ui-polish-scope precedent: accessibility
  floor and readability; OWID fidelity not required; public DESIGN_SYSTEM.md not
  binding on internal panels.
- No cost estimates or spend gates anywhere in the console (CLAUDE.md rule 14);
  provider billing dashboards remain the cost surface.

## 6. Next steps

1. Mark approves or amends this scope.
2. Architect plan decomposing panels 1-3 (the campaign runner core) as the first
   build; panels 4-5 second.
3. Existing admin console access decision (SSH tunnel vs tailscale serve) resolves
   independently and applies to this console unchanged.
