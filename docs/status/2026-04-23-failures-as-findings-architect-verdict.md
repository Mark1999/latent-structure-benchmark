# Failures-as-Findings Directive — Architect Verdict

**Date:** 2026-04-23
**Architect:** spawned from Claude Code session on Linode `lsb-agent-02`
**Trigger:** Mark's binding directive (verbatim below) issued 2026-04-23 in the wake of T4's partial outcome (101/120 records; 4 models with zero-or-degraded output).
**Preceding context:** `docs/status/2026-04-22-phase4a-t4-run-report.md`, `docs/status/2026-04-23-phase4a-open-items.md` §3.
**Memory anchor:** `memory/project_failures_are_findings.md`.

---

## Directive (verbatim)

> Treat partial data as a real finding. We should always record failed runs as a real finding. If the LLM connected but refused to respond, we save that session verbatim including all thinking or reasoning traces. If the failure was technical, again, it should be saved as well. If the LLM responds in an unexpected manner or for some reason refuses to do the task, then interview the LLM informant as follow up questions. Note for the future: we need a way for the dashboard to call out failed runs and allow the website viewer to review the reasons why and the raw logs.

---

## Disposition — three-stream decomposition

| Stream | Scope | Blocks T5? |
|---|---|---|
| **A** — Verbatim-capture audit + gap-close + schema expansion | Phase 4a | YES |
| **B** — Follow-up decline-interview protocol (design + impl + backfill) | Phase 4a-adjacent | **Design blocks T5; implementation does not** |
| **C** — Dashboard failure-display surface | Phase 6+ | No |

---

## Stream A — Verbatim-capture audit (Phase 4a blocker)

The T4 numbers show at least 19 missing cells. Before T5 analysis, close the gap between "we have 101 records + N failures.jsonl entries" and "every session the API handled is captured verbatim somewhere." An unaudited `run_informant` path is a silent-data-loss risk that invalidates the "failures are findings" commitment.

### Audit checklist

1. `scripts/collect.py::collect_single_pass` — the `try/except Exception` at lines 200–220. Confirm every exception class routes to `append_failure`. Confirm `append_failure`'s `context` dict includes enough to reconstruct the cell identity — it currently does; audit whether it includes the partial session bytes when they exist.
2. `cdb_collect/runner.py::run_informant` — three inline awaits (`run_free_list`, `run_pile_sort`, `run_pile_interview`). **If step 2 raises, step 1's verbatim prompt+response is lost because it was inside a local variable that never reaches `_assemble_record`. This is the most likely gap** and the most likely cause of GLM-5.1's and gemini-2.5-pro's missing verbatim.
3. Each adapter's `complete` path — HTTP 200 with empty body (GLM, gemini pile-sort case) vs HTTP 4xx/5xx vs timeout vs stream-cut. Audit what each returns and whether the caller has access to the raw response bytes.
4. Parser layer — `parse.py`, `pile_sort_parser.py`, `free_list_parser.py`, `pile_interview_parser.py`. A parse exception must preserve `response_verbatim` end-to-end.
5. QA layer — `check_record` inside `collect_single_pass` runs *after* `append_record`, so it cannot suppress a record. Add to the audit report for completeness.
6. The two-pass / cross-model / baseline variants have a single outer `try/except` that is coarser than single-pass. Audit partial-success retention on these paths.

### Deliverable

`docs/status/2026-04-23-verbatim-capture-audit.md` — a matrix of {session-outcome class} × {where verbatim lands} × {gap | OK}, plus specific file:line references for any gap.

### Schema ruling

The directive names "thinking or reasoning traces" as required capture. `FreelistRecord`/`PileSortRecord`/`InterviewRecord` already have `thinking_verbatim: str = ""`. But `failures.jsonl` currently carries only `error_type`, `error_message`, `context` — no `response_verbatim`, no `thinking_verbatim`, no `prompt_verbatim`. **This is the schema gap.**

- **No change to `InformantRecord`.** Refused-HTTP-200 already lands as a normal record with `qa_passed=False` and `response_verbatim` populated. The GLM case *already works* under the current schema.
- **Expand `failures.jsonl` entry shape.** Add: `partial_session` — an object with whatever step records completed, shaped as `{freelist?, pile_sort?, interview?}` with the same fields as the corresponding step record types. Add top-level `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason` for the step that actually failed. Stays in `failures.jsonl` (not a new type). Requires matching `DATA_DICTIONARY.md` update (Reviewer R7 same-PR).
- **Reject** promoting refused-HTTP-200 cases from `informants.jsonl` to `failures.jsonl`. The current split (records that hit `_assemble_record` go to informants.jsonl; exceptions go to failures.jsonl) is the right invariant — flipping on "content is bad" would couple QA semantics to the JSONL routing and break append-only audit.

### Acceptance

Every failure mode observed in T4 is traceable from the two JSONL files back to the exact session bytes the provider returned, with `prompt_verbatim` + `response_verbatim` + `thinking_verbatim` (where the adapter surfaces it) present for each. A re-run of T4 with a synthetic refusal and a synthetic mid-session exception produces entries where a future analyst can reconstruct what happened from the file alone.

---

## Stream B — Follow-up decline-interview protocol

**CDA SME is the gate on methodology.** All 6 design questions go to them. My non-binding preference rulings, to tighten the SME brief:

1. **Prompt design** — SME territory. My hunch: neutral "You produced no pile-sort (or: a pile-sort that did not parse). Can you say what happened?" Avoid "why did you refuse" (presupposes agency). §1.5-compliant.
2. **Sync vs async** — Orchestrator with SME consultation. **Ruling: asynchronous Phase 4a.1 remediation pass.** Synchronous couples into `run_informant`, forcing a schema change on the primary step path and inflating every run's latency. Async decouples; model-version drift is auditable via `model_version_returned`.
3. **Refusal detection** — Joint SME+Architect. **Must be deterministic.** Two triggers: (a) session landed in `failures.jsonl` with any error class; (b) session landed in `informants.jsonl` with `qa_passed=False` AND pile-sort `response_verbatim` matches a refusal-string allowlist OR has 0 items. A classifier is out of scope — rule 12 (no LLM imports in `cdb_analyze`) drifts toward that. Deterministic Python rule only.
4. **Data model** — SME territory. My strong preference: **new sibling type `DeclineInterview`** persisted to `data/raw/decline_interviews.jsonl`, keyed by the `informant_id` of the session being followed up on (or a synthetic ID for sessions that failed before `informant_id` was assigned). Rationale: a 4th step on `InformantRecord` would force the append-only record to be mutated, or force every record everywhere to carry an empty 4th step. Sibling type keeps `InformantRecord` v0.7 stable.
5. **Analysis integration** — SME territory. My read: **reported but not analyzed in v1.** Register 2 consumes pile-sort matrices, not free-text refusal explanations. Decline-interview becomes dashboard copy (Stream C) and methodology-page content. Register 3 discourse analysis is Phase 7+.
6. **Backfill** — Architect territory. **NO.** T5 proceeds on 101 records + failures.jsonl + 19 missing cells. Decline-interview applies to a Phase 4a.1 remediation (after Stream A closes and Stream B design lands) and to Phase 4b onward. Backfilling now blocks T5 on a protocol that hasn't been SME-reviewed.

### Deliverable

`docs/DECLINE_INTERVIEW_PROTOCOL.md` — a design note the SME can PASS/PASS-WITH-NOTES/FAIL. **Not handed to Coder** without SME PASS or PASS-WITH-NOTES.

### Gate

CDA SME (mandatory — new CDA protocol step, four-axis review) → Architect re-review for schema sign-off on `DeclineInterview` → Coder → Reviewer.

---

## Stream C — Dashboard failure-display (Phase 6+)

Scope paragraph for `ARCHITECTURE.md` §5.3 Phase 6:

> **Phase 6 failure-display surface.** The dashboard exposes a per-model, per-domain failure-rate callout alongside the standard model-comparison views. A reader can click through from any model's card to a session-level log viewer that presents the verbatim prompt, verbatim response, and thinking trace (where the provider surfaces it) for each run that failed, refused, or produced a non-parsing output. Copy follows ARCHITECTURE.md §1.5 — "declined," "did not parse," "returned empty response"; not "broken," "defective," or "failed model." Raw logs are readable as text (not only JSON); accessibility per DESIGN_SYSTEM.md WCAG AA. Decline-interview transcripts (captured per the Phase 4a.1 protocol) render alongside the originating session. The CDA SME reviews all copy; the UI/UX agent gates the visualization and interaction. Source-of-truth for the data surface is `data/raw/informants.jsonl` (qa_passed=False rows) + `data/raw/failures.jsonl` + `data/raw/decline_interviews.jsonl`, shaped for the dashboard by `cdb_publish`.

Task **#22 is docs-only** — landing this paragraph in `ARCHITECTURE.md` §5.3 now ensures it won't be forgotten. Implementation is not Phase 4a work.

---

## Task decomposition & gate map

Existing task IDs reconciled with Architect's graph:

| # | Task | Type | Gates | Depends on |
|---|---|---|---|---|
| #18 | Architect decomposition (this verdict) | Docs (verdict) | Self | — |
| #19 | Verbatim-capture audit report | Docs (audit report, no code) | Reviewer | #18 |
| **#23** *(new)* | Close verbatim-capture gaps surfaced by audit | Code | Architect sign-off per fix → Coder → Reviewer | #19 |
| **#24** *(new)* | Expand `failures.jsonl` schema + `DATA_DICTIONARY.md` | Schema + docs | Architect sign-off (in principle, granted here; formal on exact field list after #19) → Coder → Reviewer (R7 same-PR) | #19 |
| **#25** *(new)* | Write `docs/DECLINE_INTERVIEW_PROTOCOL.md` design note | Docs (design) | Self (orchestrator composes from this verdict's Stream B) | #18 |
| #20 | CDA SME review of decline-interview protocol | Gate | CDA SME four-axis; mandatory | #25 |
| **#26** *(new)* | `DeclineInterview` schema + runner + detector | Code | Architect schema sign-off → Coder → Reviewer; CDA SME PASS on #20 prerequisite | #20 |
| #21 | Phase 4a.1 remediation pass (decline-interviews over existing corpus) | Ops | Architect go/no-go | #26, #19, #23, #24 |
| #22 | `ARCHITECTURE.md` §5.3 Phase 6 paragraph | Docs | Architect (me) → Reviewer | — |

**Sequencing call:**

- **T5 (task #13) waits for:** #19, #23, #24, #25, #20 PASS (not #26 impl, not #21 backfill, not #22 docs).
- **T5 does NOT wait for:** #26 (impl), #21 (backfill), #22 (docs paragraph — independent).
- **Reviewer on T4 commit `b2b74e4`** is independent of all of this and can run any time.

**Dependency graph:**

```
#18 (this verdict, done) 
  ├──► #19 (audit) ──┬──► #23 (gap fixes) ──┐
  │                   └──► #24 (schema)    ──┤──► T5 unblocked on data side
  │                                           │
  ├──► #25 (design note) ──► #20 (SME PASS) ─┴──► T5 unblocked on narrative side
  │                            └────► #26 (impl) ──► #21 (backfill, post-T5)
  │
  └──► #22 (Phase 6 paragraph, independent)
```

---

## Scope fencing — explicitly out of Phase 4a

- Dashboard implementation of failure-display (all of `apps/dashboard/` failure-surfacing work) — Phase 6+.
- Decline-interview backfill to T3 shakedown records — out. Only Phase 4a canonical + Phase 4b onward.
- Any LLM-based classifier for refusal detection — hard out. Deterministic rules only.
- Cross-linking decline-interview transcripts into Register 1/2 analysis — Phase 7+.

---

## Reading list for each Coder task

- **#19:** `ARCHITECTURE.md` §1 commitment 7, §4.1.6; `CLAUDE.md` §6 rules 10/12, §9 pitfalls #9/#10; `packages/cdb_collect/` all of `runner.py`, `jsonl.py`, each adapter, each parser, `scripts/collect.py`.
- **#23:** #19 + specific files the audit surfaces.
- **#24:** `DATA_DICTIONARY.md`; `ARCHITECTURE.md` §3.2; `CLAUDE.md` §6 rule 7 (R7 same-PR).
- **#25:** `ARCHITECTURE.md` §1.5 (binding on prompt wording), §4.1 (CDA steps); `docs/SME_REVIEW.md`; `docs/SHAKEDOWN_PROTOCOL.md` §1/§3 (protocol-versioning precedent).
- **#26:** #25 outputs + `cdb_core/schemas.py` + `cdb_collect/runner.py` + `DATA_DICTIONARY.md`.
- **#22:** `ARCHITECTURE.md` §5.3 + `DESIGN_SYSTEM.md` §4.1.

---

## Routing for next action

1. Spawn Coder on **#19** immediately (docs-only audit, no gates required).
2. In parallel: compose **#25** design note from this verdict's Stream B and route to **CDA SME** (#20).
3. Do not proceed to #23/#24 until #19 lands.
4. Do not proceed to #26 until CDA SME PASS on #20.
5. Reviewer on `b2b74e4` (T4 commit) can run any time — independent of this thread.

---

*End of verdict. Directive captured. T5 has concrete unblocking criteria. Architect gate on this thread: closed pending #19 and #20 outcomes.*
