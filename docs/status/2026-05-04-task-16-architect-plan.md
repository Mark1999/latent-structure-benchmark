# Task #16 — Adaptive max_tokens Across All Adapters: Architect Plan

**Date:** 2026-05-04
**Planner:** Architect agent
**Task ID:** #16 (Adaptive max_tokens across all adapters)
**Status:** Draft pending CDA SME review
**Supersedes (in part):** `docs/status/2026-04-22-phase4a-adapter-fix-verdict.md` — that verdict's chosen value `max_tokens=4096` for OpenRouter is replaced by `max_tokens=16384`. The reasoning from that verdict (the phi-4 16K-context constraint) is preserved as a note: phi-4 is no longer in the active slate, so the small-context constraint that drove the 4096 cap no longer binds.
**Carries forward:** the original commit-discipline rule from the 2026-04-22 verdict (one task → one commit; do not bundle).
**Trigger:** Stages 1.5, 1.5b, and 1.6 probes (commits `d06e64c`, `11a36c0`, `19d67f1`) confirmed that the 29 Phase 4a failures are predominantly a `max_output_tokens=4096` configuration artifact, not corpus-lens or refusal events. Stage 1.6 end-to-end on gemini-2.5-pro at `max_output_tokens=16384, thinking_budget=1024` produced 10/10 valid informants on family + holidays. Stage 1.5b confirmed the same root cause for glm-5.1 (×6) and llama-4-maverick (×4) on OpenRouter.

---

## 1. Disposition table

| Concern | Action | Rationale |
|---|---|---|
| `GeminiAdapter._do_call` `max_output_tokens=4096` | **Change to `16384`** | Stage 1.6 proved the value end-to-end; no slate Gemini variant has a context constraint that bites at this cap. |
| `GeminiAdapter._do_call` `thinking_budget=8192` | **Change to `1024`** | Stage 1.6 used `1024`; reducing the reasoning budget reclaims headroom for visible output. The 8192 figure was not based on probe data. |
| `OpenRouterAdapter._do_call` `max_tokens=4096` | **Change to `16384`** | Stage 1.5b proved this unblocks glm-5.1 (needs 16384+) and llama-4-maverick (needs ~8000+). 16384 covers both. The original 2026-04-22 4096 cap was set to protect phi-4's 16K total context; phi-4 is no longer in the active slate. |
| Per-step adaptive caps | **Reject — single global cap** | Stage 1.6 showed one cap suffices end-to-end. Per-step adaptive sizing is an unnecessary complication; revisit only if a future probe shows it's needed. |
| `AdapterResult` thoughts field | **Add `thoughts_token_count: int = 0`** | Captures provider-side reasoning-token usage so QA and downstream analysis can detect "model spent everything on thinking, nothing on output" without re-parsing raw responses. Default `0` (not `None`) to avoid `int | None` arithmetic gymnastics on the consumer side; matches the existing `input_tokens: int` convention. |
| Step-record schemas (`FreelistRecord`, `PileSortRecord`, `InterviewRecord`) | **Add `thoughts_token_count: int = 0`** | Methodology-significant — captures a per-step diagnostic in the canonical record. Optional with default `0` so old records load unchanged. |
| `failures.jsonl` envelope | **Add `thoughts_token_count` to `append_failure` (top-level when failing-step value is known) and to `partial_session.{freelist,pile_sort}` sub-objects** | Required by Reviewer rule R7 corollary — the failure envelope must carry the same forensic detail as `InformantRecord` for every per-step token count it tracks. |
| `docs/DATA_DICTIONARY.md` | **Co-update §1.2, §1.3, §1.4 (step records), §9.2/§9.3 (failures envelope)** | Binding per CLAUDE.md §6 R7; same PR. |
| Phi-4 forward path | **Out of scope.** Document in plan only: phi-4 has a 1 ValueError + 5 HTTPStatusError pattern that is not a max_tokens issue. |
| Corpus recovery (re-collect 19 fixable failures against new caps) | **Out of scope.** Separate follow-on task with its own gate chain, blocked on this task's merge. |
| gpt-5.4-mini ×3 and mistral-small ×1 unexplained failures | **Out of scope.** Stage 1.5b showed the cap fix does not recover them. Separate investigation task. |
| Prompt template version bump | **No.** Prompt templates are unchanged. Per CLAUDE.md §6 R8, only the prompt files in `packages/cdb_collect/prompts/v{N}/` are versioned; adapter parameters (`max_tokens`, `temperature`) live outside the prompt template and do not trigger a version bump. Surfacing for SME confirmation as Q3 below. |
| Backward compatibility with old Phase 4a records (no `thoughts_token_count` field) | **Default `0`.** Pydantic v2 with the field declared as `int = 0` accepts JSONL lines that lack the field — it materialises as `0` on read. No migration required. |

---

## 2. Tasks

### Task 16.A — Update `AdapterResult` and both adapters

**Owner:** Coder
**Estimated cost:** $0 (adapter code change; tests use fixtures, no API calls)

**Files to modify:**

1. `/opt/lsb-agent/packages/cdb_collect/cdb_collect/adapters/base.py`
   - Add field `thoughts_token_count: int = 0` to `AdapterResult` dataclass (between `output_tokens` and `provider_request_id` for readability; the dataclass is `frozen=True` so all defaulted fields must come after non-defaulted ones — the existing `thinking_text: str = ""` is already at the end, so place `thoughts_token_count` immediately before `thinking_text`).
2. `/opt/lsb-agent/packages/cdb_collect/cdb_collect/adapters/google.py`
   - In `_do_call`:
     - Change `max_output_tokens=4096` to `max_output_tokens=16384`.
     - Change `thinking_budget=8192` to `thinking_budget=1024`.
     - Update the comment block above to cite this plan and the Stage 1.6 probe (`scripts/probe_gemini_fullcycle_2026_05_04.py`, commit `19d67f1`) instead of the 2026-04-22 verdict.
   - Capture `thoughts_token_count`: read `usage.thoughts_token_count` from the `usage_metadata` object (google-genai exposes this as a sibling of `prompt_token_count` and `candidates_token_count`). Default to `0` if the attribute is absent or `None`.
   - Pass the captured value to `AdapterResult(thoughts_token_count=...)`.
3. `/opt/lsb-agent/packages/cdb_collect/cdb_collect/adapters/openrouter.py`
   - In `_do_call`:
     - Change `"max_tokens": 4096` to `"max_tokens": 16384`.
     - Replace the existing comment block (lines 104–108) with one that cites this plan, the Stage 1.5b probe (commit `11a36c0`), and notes that the original 4096 figure was driven by phi-4's 16K total context and that phi-4 is no longer in the active slate.
   - Capture `thoughts_token_count`: read `usage.completion_tokens_details.reasoning_tokens` from OpenRouter's response (per OpenRouter docs, the `usage` object includes a `completion_tokens_details` sub-object with `reasoning_tokens` for thinking models). Default to `0` if the path is absent. **Add `"include_reasoning": True`** to the request payload — per OpenRouter docs, this is required to surface reasoning tokens. (This was already implicitly present via the `reasoning_content` extraction logic, but make it explicit.)
   - Pass the captured value to `AdapterResult(thoughts_token_count=...)`.

**Files NOT to modify:**

- `packages/cdb_collect/cdb_collect/adapters/anthropic.py` — Anthropic adapter is not in the failure scope. Stage 1.5/1.5b/1.6 did not probe it. If it has a `max_tokens` cap, leave it alone. (If the Coder finds it does and wants to align — pause and surface to Architect. Out of scope for this task.)
- `packages/cdb_collect/cdb_collect/adapters/huggingface.py` — same reasoning.
- Any prompt template under `packages/cdb_collect/prompts/v{N}/` — no template changes; this is purely an adapter parameter change.
- `packages/cdb_collect/cdb_collect/runner.py` — runner does not need to know about `thoughts_token_count` to pass it through; `AdapterResult` flows opaquely.

**Acceptance criteria:**

1. `AdapterResult.thoughts_token_count` field exists with default `0` and type `int`.
2. `GeminiAdapter._do_call` sends `max_output_tokens=16384, thinking_budget=1024` on every call (no per-step branching).
3. `GeminiAdapter._do_call` populates `AdapterResult.thoughts_token_count` from the response's `usage_metadata.thoughts_token_count`, defaulting to `0` when absent.
4. `OpenRouterAdapter._do_call` sends `max_tokens=16384` and `include_reasoning=True` on every call.
5. `OpenRouterAdapter._do_call` populates `AdapterResult.thoughts_token_count` from `usage.completion_tokens_details.reasoning_tokens`, defaulting to `0` when absent.
6. Comment blocks in both adapters reference this plan path and the relevant probe commit hashes.
7. `ruff`, `mypy`, and the no-LLM-imports static check pass.

**Test coverage requirements:**

- `tests/adapters/test_google.py` (or equivalent location in the repo's test layout): add a fixture-based test asserting `_do_call` constructs `GenerateContentConfig` with `max_output_tokens=16384` and `thinking_budget=1024`. Use `unittest.mock` to intercept `genai.Client.models.generate_content`; do not call the real API.
- `tests/adapters/test_openrouter.py`: add a fixture-based test asserting the request payload contains `"max_tokens": 16384` and `"include_reasoning": True`. Use `httpx.MockTransport` or equivalent.
- For both adapters: add a fixture covering the case where the provider returns a non-zero `thoughts_token_count` and a case where the field is absent (returns `0`).
- For both adapters: existing tests must continue to pass without modification (the cap and field are the only changes; transport behaviour, retries, `temperature` handling are untouched).

**Reading list for the Coder:**

1. `/opt/lsb-agent/CLAUDE.md` — full read; §6 binding rules and §9 pitfalls especially.
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (framing — applies to comment text in adapters), §3.2 (schemas), §4.1.2 (adapter contract).
3. `/opt/lsb-agent/SECURITY_AND_HARDENING.md` §9 Reviewer rules table.
4. `/opt/lsb-agent/docs/status/2026-04-22-phase4a-adapter-fix-verdict.md` — the verdict this task partially supersedes.
5. `/opt/lsb-agent/scripts/probe_gemini_fullcycle_2026_05_04.py` — exact cap values and the `_BumpedGeminiAdapter` reference subclass.
6. `/opt/lsb-agent/scripts/probe_openrouter_cap_bump_2026_05_04.py` — Stage 1.5b OpenRouter probe.
7. OpenRouter docs on reasoning tokens: https://openrouter.ai/docs/use-cases/usage-accounting and https://openrouter.ai/docs/guides/best-practices/reasoning-tokens — reference for the `include_reasoning` flag and `completion_tokens_details.reasoning_tokens` path.

**Gate verdicts required:**

- CDA SME PASS or PASS-WITH-NOTES (gates Task 16.A entirely — not just the schema task).
- Reviewer PASS on the Coder commit.
- Tester PASS on the Coder commit.
- No UI/UX gate (no frontend impact).

**Commit message template:** `fix(collect): bump adapter caps to 16384 and capture thoughts_token_count`. Body cites task #16, this plan, the CDA SME verdict file, and the Stage 1.5/1.5b/1.6 probe commits.

---

### Task 16.B — Schema + DATA_DICTIONARY co-update

**Owner:** Coder
**Estimated cost:** $0
**Architect explicit sign-off:** GRANTED for the additive schema change described below, **conditional on CDA SME PASS for the overall plan**. CLAUDE.md §6 R7 requires Architect sign-off for any change to `cdb_core/schemas.py`.

**Files to modify:**

1. `/opt/lsb-agent/packages/cdb_core/cdb_core/schemas.py`
   - Add `thoughts_token_count: int = 0` to `FreelistRecord` (after `output_tokens`).
   - Add `thoughts_token_count: int = 0` to `PileSortRecord` (after `output_tokens`).
   - Add `thoughts_token_count: int = 0` to `InterviewRecord` (after `output_tokens`).
   - Do **not** modify `DeclineInterview` — that schema's token fields are about the follow-up call only, and the decline-interview adapter path is the same as the primary path; if reasoning tokens become needed there, address in a separate follow-on. Surfacing as Q5.
2. `/opt/lsb-agent/docs/DATA_DICTIONARY.md`
   - Bump version to `v0.1.11`.
   - Add changelog entry citing task #16, this plan, and the CDA SME verdict path.
   - In §1.2 (FreelistRecord), §1.3 (PileSortRecord), §1.4 (InterviewRecord) tables: add a row for `thoughts_token_count` with type `int`, required `No (default 0)`, semantics: "Provider-reported reasoning/thoughts token count. Captured separately from `output_tokens` because reasoning tokens are billed and consumed against the same `max_tokens` budget but do not produce visible output. Detecting `output_tokens == 0 AND thoughts_token_count > 0` is the diagnostic signature of cap-exhausted reasoning failures (see task #16). For providers that do not surface reasoning tokens (Anthropic, HuggingFace at this commit), the value is `0`."
3. `/opt/lsb-agent/packages/cdb_collect/cdb_collect/jsonl.py`
   - In `append_failure`: add a new keyword-only parameter `thoughts_token_count: int | None = None`. When non-None, write it as a top-level entry field after `stop_reason` (matching the existing field-order convention).
   - In docstring: document the new parameter.
4. `/opt/lsb-agent/docs/DATA_DICTIONARY.md` §9.2 and §9.3
   - §9.2 top-level fields table: add `thoughts_token_count` row, type `int | None`, semantics: "Provider-reported thoughts/reasoning token count for the failing step (or final retry). Absent when the request never completed. `0` for providers that do not surface this."
   - §9.3 partial_session shape: add `thoughts_token_count: int` row to both the `freelist` and `pile_sort` sub-object tables (interview sub-object can be left unchanged unless the runner is already populating it; surfacing for the Coder as a Q during implementation).
5. **Runner / persistence wiring** — `/opt/lsb-agent/packages/cdb_collect/cdb_collect/runner.py` (or equivalent):
   - When constructing `FreelistRecord`, `PileSortRecord`, `InterviewRecord`: pass `thoughts_token_count=adapter_result.thoughts_token_count`.
   - When constructing `partial_session` dicts and calling `append_failure`: include the value at every site that already includes `output_tokens`.

**Files NOT to modify:**

- `cdb_core/schemas.py` `DeclineInterview` class — out of scope; surfacing as Q5 below.
- `cdb_core/schemas.py` `InformantRecord` top-level — the new field lives on the per-step records, not on the envelope.
- `scripts/build_db.py` — the SQLite layer is downstream. **Update DDL to add a `thoughts_token_count INTEGER NOT NULL DEFAULT 0` column to the `freelist`, `pile_sort`, and `interview` tables (or whichever tables hold the per-step records).** This is on the critical path because the data dictionary describes the SQLite shape and the field must propagate. If `build_db.py` is not currently structured to easily add a column, the Coder pauses and surfaces to Architect.
- `scripts/qa_check.py` — a follow-on task may want a QA check that flags `output_tokens == 0 AND thoughts_token_count > 0` as a cap-exhausted-reasoning warning, but that is a separate task with separate semantics; out of scope here.

**Acceptance criteria:**

1. The three step-record pydantic classes have `thoughts_token_count: int = 0`.
2. Runner / persistence wiring populates the new field from `AdapterResult.thoughts_token_count` for all three steps.
3. `append_failure` accepts `thoughts_token_count` and writes it.
4. `DATA_DICTIONARY.md` is updated with version bump, changelog entry, and field rows in §1.2, §1.3, §1.4, §9.2, §9.3.
5. `scripts/build_db.py` DDL includes the new column with default `0` for the three step tables.
6. Round-trip test: an old InformantRecord JSONL line (without the new field) loads cleanly and serialises with `thoughts_token_count: 0`.
7. Round-trip test: a new InformantRecord with `thoughts_token_count=42` round-trips through `model_dump_json` → `model_validate_json` → SQLite insert/select with the value preserved.
8. `ruff`, `mypy`, `pytest` pass.
9. No-LLM-imports static check passes (no `cdb_analyze` change is being made; this is a sanity confirmation).
10. Reviewer R7 (schema + dictionary in same commit) is satisfied.

**Test coverage requirements:**

- `tests/cdb_core/test_schemas.py` (or equivalent): add a test that loads a fixture JSONL line lacking `thoughts_token_count` and asserts the loaded record has the field set to `0`.
- Same test file: add a test that constructs an `InformantRecord` with non-zero `thoughts_token_count` on each of its three step records and asserts the value survives `model_dump_json` round-trip.
- `tests/scripts/test_build_db.py` (or equivalent): add a test that builds a SQLite DB from a fixture JSONL containing both old (no field) and new (with field) records and asserts the column is populated correctly for both.
- `tests/cdb_collect/test_jsonl.py` (or equivalent): add a test for `append_failure` with `thoughts_token_count` set, asserting the field appears in the written line in the documented position.

**Reading list for the Coder:**

1. CLAUDE.md §6 R7 (binding: schema change requires DATA_DICTIONARY co-update in same PR).
2. ARCHITECTURE.md §3.2 (schema source of truth).
3. `/opt/lsb-agent/docs/DATA_DICTIONARY.md` §0–§1.4, §9, §10 — read end-to-end so the changelog entry conforms to the established style.
4. `/opt/lsb-agent/packages/cdb_core/cdb_core/schemas.py` — full read.
5. `/opt/lsb-agent/scripts/build_db.py` — full read; understand the existing per-step table layout before adding the column.

**Gate verdicts required:**

- CDA SME PASS or PASS-WITH-NOTES on this plan (covers both 16.A and 16.B).
- Reviewer PASS on the Coder commit.
- Tester PASS on the Coder commit.

**Commit message template:** `feat(core): add thoughts_token_count to step records and failures envelope`. Body cites task #16, this plan, the CDA SME verdict file path, and the data dictionary version bump.

---

## 3. Sequencing and dependencies

**Dependency graph:**

```
Architect plan (this doc)
          │
          ▼
   CDA SME review  ─── FAIL ──→ Architect rework
          │
        PASS / PASS-WITH-NOTES
          │
          ▼
   Task 16.A (adapters + AdapterResult)
          │
          ▼
   Task 16.B (schemas + dictionary + runner wiring + build_db)
          │
          ▼
   Reviewer + Tester
          │
          ▼
   [follow-on, separate plan] Corpus recovery for the 19 fixable Phase 4a failures
```

**Why 16.A before 16.B:** 16.B's runner wiring reads `adapter_result.thoughts_token_count`, which only exists after 16.A. They could in principle be one commit, but per CLAUDE.md §8 "one commit per task; do not bundle" — and these are two distinct concerns (adapter behaviour change vs. schema/persistence extension). Two commits, sequenced.

**Could 16.B come first?** No. Adding the schema field with no runner wiring would commit a no-op. Adding runner wiring referring to a non-existent `AdapterResult` field would not type-check.

**Could 16.A and 16.B be a single commit?** Per §8, no — they are independently reviewable concerns. Coder must split.

---

## 4. Risks

**R1 — Backward compatibility with existing Phase 4a JSONL records.**
*Risk:* Old `informants.jsonl` lines lack `thoughts_token_count`. If the field were declared as `int` (no default), pydantic would reject those lines on read, breaking analysis and the build script.
*Mitigation:* Field is declared `int = 0`. Pydantic v2 with the project's existing `extra='ignore'`-equivalent posture loads old records cleanly with `thoughts_token_count=0`. This matches the existing `cost_usd` removal pattern (DATA_DICTIONARY v0.1.10) where old fields are silently dropped on read; we use the same mechanism in the additive direction.
*Test:* Acceptance criterion 16.B.6 covers this with a fixture JSONL line.

**R2 — `include_reasoning` flag changes OpenRouter billing or response shape unexpectedly.**
*Risk:* Adding `"include_reasoning": True` to the request payload could in theory change response structure for models that don't support reasoning, or affect billing pages. Per OpenRouter docs reasoning tokens are billed as output tokens regardless, so billing impact is bounded by the same `max_tokens` cap.
*Mitigation:* The flag is well-documented and is already implicitly assumed by the existing `reasoning_content` extraction logic (which only works if reasoning is being surfaced). Making it explicit is a no-op for models that don't support it. Coder should add a fixture-based regression test for a non-reasoning OpenRouter model to confirm response parsing still works.

**R3 — Higher cap → higher per-call cost on producers that previously truncated.**
*Risk:* Models that were previously hitting the 4096 cap will now produce more output, raising per-call cost. For glm-5.1 and llama-4-maverick this is the desired effect (recovering failures), but cost goes up.
*Mitigation:* Bounded — `max_tokens` is a ceiling, not a floor. Models that don't need 16384 will not produce 16384. The pile-sort step's typical envelope is ~2000 visible tokens; the cap matters only when reasoning is large. Existing `$300/mo` budget gate (ARCHITECTURE.md §6.2) and `weekly-cost-alert.yml` workflow continue to enforce the spend ceiling.
*Verification:* The corpus-recovery follow-on task will measure actual cost impact and report.

**R4 — Phi-4 cap regression.**
*Risk:* Per the original 2026-04-22 verdict, phi-4 has a 16K total context window. Setting `max_tokens=16384` would leave no room for the prompt, triggering HTTP 400.
*Mitigation:* Phi-4 is not in the active slate (per task description: "phi-4 1 ValueError + 5 HTTPStatusError — out of scope, separate adapter issues"). If phi-4 is reintroduced later, the right answer is per-model adaptive caps — that becomes a separate task. Document the constraint as a comment in `openrouter.py`.

**R5 — Gemini `thinking_budget=1024` reduces reasoning quality.**
*Risk:* Stage 1.6 used `thinking_budget=1024`, down from the production `8192`. A smaller reasoning budget could in principle reduce response quality on reasoning-heavy steps (pile-sort).
*Mitigation:* Stage 1.6 produced 10/10 valid informants on family + holidays at this budget — the empirical evidence is that 1024 is sufficient for the pile-sort task. If Phase 4b introduces a domain that empirically requires more reasoning, revisit. **Surfacing for CDA SME as Q6.**

**R6 — `thoughts_token_count` semantics differ subtly across providers.**
*Risk:* Gemini's `thoughts_token_count` and OpenRouter's `completion_tokens_details.reasoning_tokens` may not be exactly comparable across providers (e.g., one could include caching effects, the other not).
*Mitigation:* The data dictionary entry must explicitly say "as reported by the provider" without claiming cross-provider numerical comparability. Downstream analysis (e.g., a "cap-exhausted-reasoning" QA check) operates on the within-provider invariant `output_tokens == 0 AND thoughts_token_count > 0`, which is provider-internal and not subject to cross-provider drift.

**R7 — Test fixtures may not represent both providers' new shape.**
*Risk:* Existing fixtures were captured under the old caps. They lack the `thoughts_token_count` data path.
*Mitigation:* Coder adds new fixtures synthesised from the Stage 1.5b/1.6 probe outputs (`/opt/lsb-agent/data/probes/2026-05-04-*`). These are real provider responses at the new caps, suitable for fixture extraction.

---

## 5. What Mark must sign off on

**Nothing.** This is a routine improvement plan, not a methodology amendment. Mark's interventions are reserved for:
- Reviewer rejection overrides (per CLAUDE.md §4 — "Only Mark can override a Reviewer rejection").
- Architectural decisions implied by ambiguous specs (§8 stop conditions).
- New origin / provider / collection_method enum values (§7 stability promises).

None of those triggers fire here. **The next gate is CDA SME review.**

---

## 6. Open questions for CDA SME ruling

The CDA SME's review must address these explicitly. Each is flagged in-line above as well; collected here for the verdict file.

**Q1 — Single global cap vs. per-step adaptive caps.**
*Architect recommendation:* Single global cap (`max_output_tokens=16384` for Gemini, `max_tokens=16384` for OpenRouter). Stage 1.6 proved the simpler approach works end-to-end. Per-step adaptive sizing would be premature optimisation given current evidence. SME ruling requested.

**Q2 — Default value for `thoughts_token_count` on providers that don't expose it (Anthropic, HuggingFace).**
*Architect recommendation:* `0`. Matches the existing `output_tokens: int` convention; avoids `int | None` arithmetic in downstream consumers; preserves the diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` cleanly (since `0 > 0` is False, the diagnostic doesn't false-positive on non-reasoning providers). SME ruling requested.

**Q3 — Does this change require a prompt-template version bump per CLAUDE.md §6 R8?**
*Architect recommendation:* No. Prompt templates under `packages/cdb_collect/prompts/v{N}/` are unchanged. The CLAUDE.md §6 R8 rule applies to the prompt **content** (the words sent to the model), not to adapter parameters (`max_tokens`, `temperature`, `top_p`). SME ruling requested for confirmation.

**Q4 — Backward compatibility: how should the schema handle old Phase 4a records lacking `thoughts_token_count`?**
*Architect recommendation:* Pydantic field declared as `int = 0` (default), no migration. Old records load with the field set to `0`. Aligns with the v0.1.10 `cost_usd` removal precedent. SME ruling requested for confirmation.

**Q5 — Should `DeclineInterview` schema also gain `thoughts_token_count`?**
*Architect recommendation:* Out of scope for this task. The decline-interview path uses the same adapters, but the per-record context is different (it's a follow-up reasoning trace, not a primary step). Adding the field there is a separate, smaller task that can be filed after this one merges. SME ruling requested — if SME prefers symmetry, it's a small addition to Task 16.B.

**Q6 — Is `thinking_budget=1024` (down from 8192) a valid Gemini default?**
*Architect recommendation:* Yes, per Stage 1.6 empirical evidence (10/10 success on family + holidays). The original 8192 was not based on probe data. The 1024 figure preserves enough budget for pile-sort reasoning (the most reasoning-intensive step) while reclaiming headroom for visible output. SME ruling requested — methodology-significant because reasoning budget could affect pile-sort quality on harder domains.

---

## 7. Reading list summary (consolidated for CDA SME)

The CDA SME must read these before issuing a verdict:

1. `/opt/lsb-agent/CLAUDE.md` (full).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5, §3.2, §4.1.2, §4.1.3 (CDA step temperature conventions).
3. `/opt/lsb-agent/docs/DATA_DICTIONARY.md` §1.2–§1.4, §9, §10.
4. `/opt/lsb-agent/docs/SME_REVIEW.md` — check whether any prior SME ruling speaks to reasoning-budget defaults or to per-step parameter variation.
5. `/opt/lsb-agent/docs/BOOTSTRAP_DESIGN.md` — confirm `thoughts_token_count` capture has no implications for the Register 1 / Register 2 bootstrap design (Architect read: it does not; the field is metadata, not analysis input).
6. `/opt/lsb-agent/docs/status/2026-04-22-phase4a-adapter-fix-verdict.md` — the partially-superseded prior verdict.
7. `/opt/lsb-agent/scripts/probe_gemini_fullcycle_2026_05_04.py` — Stage 1.6 reference.
8. `/opt/lsb-agent/scripts/probe_openrouter_cap_bump_2026_05_04.py` — Stage 1.5b reference.

---

## 8. Sign-off

**CDA SME PASS is required before the Coder can start Task 16.A or Task 16.B.** Per CLAUDE.md §6 R13 and ARCHITECTURE.md §5.1, plans that touch schema methodology fields cannot be handed to the Coder without an SME verdict on file at `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (or equivalent dated path).

The Architect will route this plan to `#lsb-cda-sme` per CLAUDE.md §5. On PASS, Tasks 16.A and 16.B are released to the Coder in the order specified in §3. On FAIL, the Architect reworks against the SME's notes and re-routes.

No UI/UX gate (no frontend impact). No Mark sign-off required (routine improvement plan). Reviewer + Tester gates apply per-commit per the standard pipeline.

---

*End of plan.*
