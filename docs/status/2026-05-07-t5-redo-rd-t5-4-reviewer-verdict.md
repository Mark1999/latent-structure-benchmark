# Reviewer Verdict — T5 Redo RD-T5-4

**Date:** 2026-05-07
**Commit reviewed:** `3fc70be`
**Task:** Phase 4a T5 redo — RD-T5-4 (§8–§10 interpretation + completion-redo report)
**Reviewer:** LSB Reviewer agent
**Files changed:**
- `docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md` — §8–§10 filled in (+271 lines, -5 placeholder lines)
- `docs/status/2026-05-06-phase4a-completion-redo.md` — new file (+323 lines)
**SME plan verdict:** `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (commit `86ad713`) — PASS-WITH-NOTES; T12, T14, T15 binding on RD-T5-4
**SME content verdict required:** `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md` (gate chain step 3; pending)

---

## Prerequisite gate check

The SME plan verdict (PASS-WITH-NOTES, commit `86ad713`) is present on master. Notes binding on RD-T5-4 are T12 (§8.4 four-state S2 enumeration), T14 (no "publishable" framing), and T15 (Note G verbatim phrase + RD-3 trailing clause). T11 and T13 were confirmed at the RD-T5-3 Reviewer verdict. The SME content verdict (gate chain step 3) is not a prerequisite for this Reviewer pass; it follows the Tester gate and is the next step in the chain. No UI/UX gate applies (analytical-layer doc; per parent T4-redo SME Q4 precedent). Prerequisites satisfied; evaluation proceeds.

---

## Commit shape

`git show 3fc70be --stat` confirms exactly two files changed:

- `docs/status/2026-05-07-phase4a-t5-redo-analysis-report.md` (+271 / -5)
- `docs/status/2026-05-06-phase4a-completion-redo.md` (new; +323)

No source code, no data files, no JSONL files, no schema files, no dependency files, no prompt templates modified. No predecessor artifacts edited.

**Date discrepancy note (flagged, not a reject):** The T5 redo plan (commit `2a4c6c2`) names the canonical completion-redo file as `docs/status/2026-05-06-phase4a-completion-redo.md`. The commit landing date is 2026-05-07. The 2026-05-06 prefix aligns with the plan-specified filename, not the execution date. This is traceable and defensible: the plan-document anchor date is the conventional date for this project's status files, matching the same convention used for the plan itself. No reject; flagged as a notes-level observation for the SME's awareness.

---

## 15-Rule Scorecard (CLAUDE.md §6 + SECURITY_AND_HARDENING.md §9)

| Rule | Check | Verdict |
|---|---|---|
| R1 — Read ARCHITECTURE.md | No code changes; prose doc PR; §1.5 compliance verified below | PASS |
| R2 — Read SECURITY_AND_HARDENING.md | No dashboard, collection, or CI/CD changes | N/A |
| R3 — Read HOSTING_AND_DEV_OPS.md | No deployment work | N/A |
| R4 — Read PHASE_4C_CANDIDATE_SOURCES.md | No grounding work | N/A |
| R5 — Read PHASE_0_TASKS.md | No Phase 0 task | N/A |
| R6 — Read DATA_DICTIONARY.md | No schema changes; R7 check follows | N/A |
| R7 — No schema edit without DATA_DICTIONARY co-update | `git show 3fc70be --stat` shows no `schemas.py` changes | PASS |
| R8 — Prompt templates versioned | No prompt template changes | N/A |
| R9 — No API keys in repo | No credentials found in either file (scan run) | PASS |
| R10 — No real model calls in tests | No test files changed | N/A |
| R11 — No point estimates without uncertainty | All numerics in §8 reference §4–§7 CIs inline; no bare point estimates introduced in §8 | PASS |
| R12 — No LLM calls in cdb_analyze | No code changes; static scan confirms comment-only mention in `__init__.py` (listing forbidden imports, not importing them) | PASS |
| R13 — CDA SME gate present | SME plan verdict at `86ad713` (PASS-WITH-NOTES) confirmed present | PASS |
| R14 — Read DESIGN_SYSTEM.md | No frontend changes | N/A |
| R15 — Grounding submission PRs workflow | No grounding submission | N/A |

---

## Specific binding checks

### Check 1 — No LLM client imports in cdb_analyze/

```
grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/
```

Output: one hit in `packages/cdb_analyze/cdb_analyze/__init__.py` lines 12–13, which is a docstring comment **listing** forbidden imports as a guard notice (the module-level `NO LLM CALLS` banner). No actual import statement present. This commit makes no changes to `packages/cdb_analyze/`.

**PASS.**

### Check 2 — informants.jsonl append-only

`git show 3fc70be --stat` shows no changes to `data/raw/informants.jsonl`.

**PASS.**

### Check 3 — No API keys or secrets

Scanned both changed files for API key patterns, webhook URL patterns, token patterns, and password patterns. No matches found.

**PASS.**

### Check 4 — No forbidden vocabulary

Full scan of both files for CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden terms:

- `worldview` — zero hits
- `believes` — zero hits
- `thinks` (applied to models) — zero hits
- `How models see the world` — zero hits
- `cultural bias` (standalone) — zero hits
- `What the model understands` — zero hits
- `within-model consensus` / `within-model CCM` / `within-model eigenratio` — zero hits
- `publishable` — one hit in analysis report line 486, in the metalinguistic guard statement (`no "publishable" framing per T14`). This is the anti-claim declaration, not the forbidden framing. The word's mention in a rule-citation context is not a vocabulary violation.
- `publishable` in completion-redo report — zero hits
- `incorrect` applied to predecessor T5 — zero hits in analysis report (line 485 is the guard statement `no "incorrect" framing of the predecessor T5`). In completion-redo report line 279: "was incorrect. It was correct against its input population" — this is an explicit denial of the "incorrect" claim, not an assertion of it. This is correct usage.

**PASS.**

### Check 5 — Schema changes co-update DATA_DICTIONARY.md

No `cdb_core/schemas.py` changes in this commit.

**N/A — PASS.**

### Check 6 — No new dependencies without sign-off

No `pyproject.toml` or `package.json` changes.

**N/A — PASS.**

### Check 7 — Prompt templates versioned correctly

No changes to `packages/cdb_collect/prompts/`.

**N/A — PASS.**

### Check 8 — No point estimates without uncertainty in visualizations

No frontend changes. All numerics appearing in §8 either carry inline CIs (e.g., "Smith's S consensus score is 0.7107 (bootstrap CI [0.5049, 0.9092]; §4.1 and §5.1)") or reference back to §4–§5 where the CI was already reported and confirmed by the RD-T5-3 Reviewer. No bare point estimates introduced.

**N/A (non-frontend PR) — but confirms compliance under R11.**

### Check 9 — Prerequisite gate verdicts present

SME plan verdict (PASS-WITH-NOTES, `86ad713`) present and binding. RD-T5-3 Reviewer + Tester PASS verdicts present at `docs/status/2026-05-07-t5-redo-rd-t5-3-reviewer-verdict.md` and `docs/status/2026-05-07-t5-redo-rd-t5-3-tester-verdict.md`. Predecessor RD-T5-1 and RD-T5-2 gate chains confirmed in prior verdicts. SME content verdict (gate chain step 3) is the next step, not a prerequisite here.

**PASS.**

---

## Binding note compliance checks (T12, T14, T15)

### T12 — §8.4 enumerates all four S2 epistemic states

The T5 redo SME plan verdict T12 requires that §8.4 either (a) enumerate all four states from Task #16 S2 explicitly, or (b) cite S2 by file path.

The Coder used approach (a). Analysis report §8.4 (lines 610–617) enumerates:

1. The model produced no reasoning tokens (a non-reasoning model, or a reasoning model that bypassed reasoning for this call).
2. The provider does not surface reasoning-token usage in its API response (Anthropic, HuggingFace, and non-reasoning OpenRouter models at this commit).
3. A non-reasoning model on a reasoning-capable provider.
4. A legacy record from a pre-field era — Phase 4a pre-Task-#16 successful records, in which the `thoughts_token_count` field did not exist at collection time and is materialised as `0` on read by pydantic's default.

These match exactly the four states in T12 (`docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` lines 301–304). The pipeline-no-consume claim follows the enumeration as required. The S2 source is also cited by file path (`docs/status/2026-05-04-task-16-cda-sme-verdict.md`, Q2/S2) in the same paragraph.

**T12 SATISFIED.**

### T14 — No "publishable" framing

Grep for `publishable` across both files returns one hit: analysis report line 486, in the opening guard statement for §8: `no "publishable" framing per T14`. This is the anti-claim declaration itself — naming the rule that forbids the framing. No instance of claiming findings are "publishable" or "publication-ready" appears anywhere in either file.

The completion-redo report §9 (What this report does not claim) includes: "That any finding here is suitable for external academic publication. The methodology-page bar is credibility to a skeptical reader, per CLAUDE.md §1." This is the correct positive framing of the constraint — not claiming publishability, explicitly disclaiming it.

**T14 SATISFIED.**

### T15 — Note G verbatim phrase + RD-3 trailing clause

Two requirements:

1. **Verbatim phrase "produced no interpretable primary-step output"** — confirmed at:
   - Analysis report line 390 (§6.4): `*5 cells produced no interpretable primary-step output*`
   - Analysis report line 474 (§7.3): `*5 cells produced no interpretable primary-step output*`
   - Analysis report line 681 (§9 Note G row): `5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells was captured in Phase 4a.1, and the interpretation of those follow-ups is in the RD-3 reframing memo (...)`
   - Completion-redo report line 129 (§3.4): `5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells was captured in Phase 4a.1...`

2. **RD-3 trailing clause** — `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` appears as the trailing citation in the Note G row of §9, as required by T15.

The Note G §9 table row (line 681) uses the T15 alternative wording (`"the interpretation of those follow-ups is in the RD-3 reframing memo (path)"`) which is explicitly one of the acceptable alternatives listed in the SME plan verdict T15.

**T15 SATISFIED.**

---

## Q6 B6 public-copy guardrail checks

### Q6(a) — No CN-origin augmentation to Note E

Note E in §9 (analysis report line 680) explicitly states: "The original T5 SME augmented Note E with 'PLUS disproportionate CN-origin decline pattern.' That augmentation is REMOVED per the RD-3 reframing memo." The CN-origin phrase appears in the REMOVED/REPLACED context only — never as an active claim.

In the completion-redo report, lines 214 and 255 mention "CN-origin pattern" strictly in the context of stating the Note K hypothesis is REPLACED and the pattern was an instrument artifact. No CN-origin claim is asserted as active.

**Q6(a) SATISFIED.**

### Q6(b) — No "incorrect" framing of predecessor T5

The word "incorrect" appears in:
- Analysis report line 485: guard statement (`no "incorrect" framing of the predecessor T5`)
- Completion-redo report line 279: explicit denial (`"was incorrect. It was correct against its input population"`)

Neither is an assertion that the original T5 was incorrect. The completion-redo §8.5 "Population shift, not methodological correction" clause and §9 "What this report does not claim" both explicitly state the predecessor was correct against its input population.

**Q6(b) SATISFIED.**

### Q6(c) — No cross-provider/failure-mode/prompt-type generalization

Analysis report §8.5 "Scope discipline" (line 634) explicitly states: "Cross-provider, cross-failure-mode, or cross-prompt-type generalization requires new evidence that this corpus does not supply." This carries forward the parent T4-redo SME T6 scope discipline as required.

Scanned §8.1, §8.2, §8.3 for any sentence generalizing beyond the specific corpus conditions. No such sentence found. All observations are explicitly bounded: "this specific recovered corpus," "under v1 prompt conditions," "model-to-model distances only."

Completion-redo §9 (line 274): "That the observations generalize beyond the 11/9-model, two-domain, v1-prompt corpus conditions. Any cross-provider, cross-failure-mode, or cross-prompt-type generalization requires new evidence."

**Q6(c) SATISFIED.**

### Q6(d) — No internal-state claims

Grep for: `worldview|believes|thinks|could not see|was blind to|didn't know|the model recognized that|the model identified the failure as|the model's understanding|the model's interpretation`

Zero hits across both files.

Parent T4-redo SME T9 phrasing exclusions also scanned (`the model recognized`, `the model identified`, `the model's understanding`, `the model's interpretation`) — zero hits.

**Q6(d) SATISFIED.**

### Q6(e) — No "publishable" framing (T14)

Confirmed under T14 check above.

**Q6(e) SATISFIED.**

---

## §9 carry-forward table completeness check

The §9 binding-note compliance table in the analysis report contains:

| Required | Status | Verified |
|---|---|---|
| Note A — CARRIES FORWARD (active) | Present line 677 | Yes |
| Note C — CARRIES FORWARD (active) | Present line 678 | Yes |
| Note D — CARRIES FORWARD (active) | Present line 679 | Yes |
| Note E — CARRIES FORWARD (active) without CN-origin augmentation | Present line 680 with explicit REMOVED notation | Yes |
| Note G — CARRIES FORWARD (active) with T15 verbatim + RD-3 path | Present line 681 | Yes |
| Note K — REPLACED (audit preserved) referencing RD-3 memo | Present line 682 | Yes |

Five-category vocabulary (CARRIES FORWARD / REPLACED) from T10 applied correctly throughout.

**§9 table PASS.**

### R11 — No point estimates without uncertainty

All numeric references in §8 carry inline bootstrap CIs or explicitly reference the §4–§5 tables where CIs were reported. Spot-check: "Smith's S consensus score is 0.7107 (bootstrap CI [0.5049, 0.9092]; §4.1 and §5.1)" — CI present inline. "Romney CCM eigenratio of 12.10" — a threshold-comparator value, not a claim about a model's position; no CI required for eigenratio per ARCHITECTURE.md §4.2.6. No bare point estimates without associated uncertainty appear in §8.

**R11 PASS.**

### §10 forward-carry completeness check

Required items per dispatch brief:

| Required item | Present |
|---|---|
| T5 redo / Phase 4a closure complete | Yes — §10 opening paragraph |
| v2 prompt comparison study (Phase 5+) | Yes — §10 line 718 |
| phi-4 ×6 adapter task | Yes — §10 line 722 |
| gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation | Yes — §10 line 726 |
| Phase 4b G1 sensitivity study | Yes — §10 line 729 |
| Phase 4c human grounding | Yes — §10 line 733 |
| Methodology-page UI rendering (Phase 5/6, UI/UX-gated) | Yes — §10 line 737 |
| Phase 4b / next-domain expansion (informational) | Yes — §10 line 740 |

All eight required §10 items present.

**§10 PASS.**

### Completion-redo report structure check

Per dispatch brief requirements:

| Required element | Status |
|---|---|
| Updates corpus state (121 informants, 20 recovery rows, 11/9 models) | §3 and §3.1–§3.4 — confirmed |
| Updates headline numerics with bootstrap CIs | §3.2 and §3.3 — consensus_score + consensus_ci on both domains |
| References RD-3 for Note K disposition | §7.3 in Phase 4b readiness section; §3.4 |
| References analysis report for §1–§10 detail | §1 header, multiple §3 references |
| States Phase 4a closure status under post-recovery conditions | §10 "Phase 4a is COMPLETE" (conditional on SME content verdict) |
| "What this completion does not claim" section | §9 present (lines 266–293); six explicit non-claims |

The "What this completion does not claim" section mirrors the RD-3 §6 pattern as required, including non-generalization to other providers/failure-modes, non-incorrectness of predecessor, non-baseline-proximity, and non-publication-suitability.

**Completion-redo report structure PASS.**

### Commit message hygiene

Subject line: `docs(status): T5 redo RD-T5-4 §8-§10 + completion-redo report` (64 characters — under 72). Conventional Commits format: `docs(status):` scope. Body references plan commit (`2a4c6c2`), SME plan verdict commit (`86ad713`), prior RD chain commits (RD-T5-1 `fda4ed7`, RD-T5-2 `63b0f9a`, RD-T5-3 `5128e94`), RD-3 memo commit (`93a544f`), predecessor T5 (`d74ce57`). Binding notes applied (T12, T14, T15) and Q6(a-e) are called out. SME content verdict file path named. Co-author attributed.

**Commit hygiene PASS.**

---

## Standard 9-check scorecard

```
REVIEWER VERDICT: PASS

Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A (non-frontend; R11 confirmed)
Check 9 — Prerequisite verdicts:     PASS
```

---

## VERDICT: PASS

All nine binding checks pass. T12 (four S2 epistemic states), T14 (no publishable framing), and T15 (Note G verbatim phrase + RD-3 trailing clause) are all satisfied. B6 public-copy guardrails Q6(a)–(e) are all satisfied. §9 carry-forward table is complete with the correct five-category vocabulary. §10 forward-carry enumerates all required items. Completion-redo report structure is correct and includes the required "What this report does not claim" section.

**Coder may proceed to the Tester gate.** After Tester PASS, the SME content verdict (gate chain step 3) follows at `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`.

**Notes for the SME content review:**

1. The completion-redo filename uses the plan-specified 2026-05-06 prefix despite landing on 2026-05-07. This is a naming convention question, not a vocabulary or methodology question, but the SME may wish to note it.
2. §8.4 State 3 ("A non-reasoning model on a reasoning-capable provider") is a proper sub-case of State 1 in the T12 taxonomy, preserved exactly as specified in the SME plan verdict T12. The SME may wish to confirm that this four-state enumeration — which preserves a partially-overlapping category structure from T12 — is the intended disambiguation discipline for the data dictionary reference.
3. The §8.3 claim that the difference between 0.78 and 0.71 consensus scores is "not distinguishable from bootstrap noise" is framed as "the CI overlap means this difference is not distinguishable from bootstrap noise" — this is a descriptive CI-overlap observation, not a formal hypothesis test. The SME may wish to confirm this framing meets the claims-validity bar for methodology-page prose.

*End of Reviewer verdict. Predecessor reports preserved as audit at `docs/status/2026-04-23-phase4a-t5-analysis-report.md` and `docs/status/2026-04-23-phase4a-completion.md` — confirmed untouched by this commit.*
