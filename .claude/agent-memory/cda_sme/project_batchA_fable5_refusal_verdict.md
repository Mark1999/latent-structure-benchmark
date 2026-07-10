---
name: project-batchA-fable5-refusal-verdict
description: batch A claude-fable-5 refusal disposition PASS-WITH-NOTES 2026-07-10; 22/23 refusal on free-list, exclude from Register 2 basis for family+holidays+food, decline-interview probes capped at one per domain, bound disclosure string with 5 load-bearing nouns
metadata:
  type: project
---

# batch A claude-fable-5 refusal disposition 2026-07-10 — PASS-WITH-NOTES

Campaign: new-model-refresh-2026h2-a-20260710 (batch A). claude-fable-5 free-list
elicitations return stop_reason=refusal with empty content in 22/23 attempts
(10/10 family, 10/10 holidays, 2/3 food). Identical prompts on claude-opus-4-8 and
claude-sonnet-5 same-hour: zero refusals. Refusal is deployment-configuration
property, not corpus.

**Why:** informant-level per-model refusal at collection time is a new disposition
class the SME has not previously adjudicated for a v1-active campaign. gpt-5.5
forced-temperature and reasoning-QA-recalibration precedents from the same campaign
apply "disclose don't exclude" but this case is different: there is nothing to
disclose because the model declines the elicitation itself in 2 of 3 domains.
Failures-are-findings ([[project_failures_are_findings]]) governs. Refusal is the
finding, not a defect.

**How to apply:** four operative rulings.

## Bound rulings

**R1 (representation).** Option (i) + (ii) layered. Exclude claude-fable-5 from
family and holidays Register 2 similarity/consensus basis (no free-list material
exists). Record refusal counts on failures trail + status doc. Run decline-interview
probes per R3 on top. Option (iii) — dropping Fable entirely — is REJECTED as
violating failures-are-findings.

**R2 (food domain minimum-n reasoning).** Preserve the 1 passing food free-list in
`informants.jsonl` verbatim (raw-first, commitment 1). EXCLUDE from food Register 2
basis. LSB has no formal minimum-n per informant per domain; the operative
principle is parity of measurement. n=1 vs. other-model n≈10 makes between-model
similarity structurally asymmetric. Register 1 OCI is undefined at n < 2 runs (the
run × item agreement matrix has no off-diagonal mass). This is the SME-recorded
minimum-n principle for future analogous cases: exclusion for measurement parity,
not for a hard n floor.

**R3 (decline-interview probes).** Approved. Use bound `decline_v1` template at
`packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt`. One probe per
(claude-fable-5, domain) = 3 sessions total, NOT the standard per-session trigger's
22 sessions. Campaign-specific reduction: within-domain classifier behavior is
homogeneous across 10 attempted runs; 3 probes suffice. Standard per-session
trigger preserved for future campaigns. Outcomes:
- Success → append to `decline_interviews.jsonl` per standard runner, surface on
  failures panel.
- Refusal (empty content, stop_reason=refusal) → persist verbatim; empty
  response_verbatim is signal per CLAUDE.md pitfall #10. Second-order finding.
- No further Fable collection in batch A after these 3 probes.

**R4 (bound disclosure string).** For batch A status doc + any Fable-related
dashboard copy in batch A context:

> The provider's deployment-side output filter returned empty content
> (stop_reason=refusal) for 22 of 23 free-list elicitation attempts on
> claude-fable-5 in batch A. Under identical prompts collected the same hour,
> claude-opus-4-8 and claude-sonnet-5 completed the same elicitations with zero
> refusals. The pattern is a property of claude-fable-5's deployment configuration,
> not of its training corpus, and does not license any claim about
> claude-fable-5's categorical structure for family or holidays.

Load-bearing nouns (non-negotiable): "provider deployment-side output filter",
"empty content", "stop_reason=refusal", "elicitation attempts", "deployment
configuration".

Extended forbidden in Fable-related batch A text (on top of §7 defaults):
- "the model refused" (agentic)
- "Fable declined" (agentic)
- "safety" as standalone noun (editorializing)
- "conservatively-tuned classifier" (repeats provider claim as fact)

Precedent: collector-bugs C1 language-register rule
([[project_collector_bugs_verdict]]) that classification language targets the
LSB-side detection event, not model behavior. This ruling extends that precedent
to elicitation-time provider-side output-filter events.

## Axes summary

- Axis 1 (Protocol validity): PASS-WITH-NOTES — decline-interview probe capped at
  one per domain rather than one per refused session, defensible for this campaign
  given homogeneous within-domain classifier behavior; standard trigger preserved
  for future.
- Axis 2 (Analytical validity): PASS — exclusion from Register 2 basis required
  (no data for family/holidays; measurement parity for food).
- Axis 3 (Claims validity): PASS — refusal pattern is first-class finding, no
  categorical-structure claim for Fable in family/holidays/food from batch A.
- Axis 4 (Audience translation): PASS-WITH-NOTES — R4 disclosure string bound.
- Register compliance: PASS.
- Vocabulary compliance: PASS-WITH-NOTES — extends §7 grep with R4 forbidden list.

## Routing call

PASS-WITH-NOTES. Hand back to orchestrator. No Architect plan required (SME is
resolving a campaign-execution question, not a schema/protocol change). No UI/UX
gate unless a Fable-related failures-panel component is later authored. Coder
executes R3 probes when Mark greenlights; Reviewer verifies R4 disclosure copy on
any Fable-related status/dashboard commit.

Verdict file: `docs/status/2026-07-10-batchA-fable5-refusal-cda-sme-verdict.md`.
