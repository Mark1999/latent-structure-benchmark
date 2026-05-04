# OPS-T7 — Reviewer verdict

**Verdict:** PASS-WITH-NOTES
**Reviewer:** LSB Reviewer agent
**Date:** 2026-05-04
**Commit reviewed:** `3570af2`
**Plan reviewed:** `docs/status/2026-05-06-OPS-T7-architect-plan.md`
**CDA SME verdict:** `docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md` (PASS-WITH-NOTES, 10 binding edits verified)

---

## Scorecard

| Check | Result | Notes |
|---|---|---|
| Check 1 — No LLM imports in cdb_analyze/ | PASS | grep clean. The two lines in `packages/cdb_analyze/cdb_analyze/__init__.py` are comment-only (the no-LLM-imports warning text itself). |
| Check 2 — Append-only JSONL | PASS | Neither `data/raw/informants.jsonl` nor `data/raw/decline_interviews.jsonl` appears in the commit's file list. |
| Check 3 — No secrets | PASS | No API keys, Slack webhook URLs, or credential-shaped strings found in any added line. |
| Check 4 — Forbidden vocabulary | PASS | All occurrences of `believes`, `thinks`, `worldview`, etc. in the diff are inside `_FORBIDDEN_PATTERNS` regex string literals used by the tests — not in user-facing copy, docstrings, or comments describing model behavior. ARCHITECTURE.md §1.5.4 additions (`within-model *`, `publishable`) also clean. |
| Check 5 — Schema + DATA_DICTIONARY | N/A | `cdb_core/schemas.py` not touched. No `DATA_DICTIONARY.md` update required. |
| Check 6 — New deps sign-off | N/A | `pyproject.toml` and `uv.lock` not touched. |
| Check 7 — Prompt versioning | N/A | No `packages/cdb_collect/prompts/` directory touched. |
| Check 8 — Uncertainty in viz | N/A | No new visualization components. This is a text-rendering ops tool addition. |
| Check 9 — Prerequisite verdicts | PASS | CDA SME PASS-WITH-NOTES present at `docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md`. UI/UX gating waived for internal ops dashboard per memory `feedback_visual_inspection.md`. |

### Plan-specific checks

| Check | Result | Notes |
|---|---|---|
| R1 — No LLM imports in diff files | PASS | `qa_interpreter.py`, `app.py`, `detail.py` all clean. |
| R2 — Append-only JSONL | PASS | Confirmed above. |
| R3 — No secrets in diff | PASS | Confirmed above. |
| R4 — Forbidden vocabulary on diff | PASS | Confirmed above. |
| R5 — No schema edits | PASS | `cdb_core/schemas.py` not in commit. |
| R6 — No new dependencies | PASS | `pyproject.toml` not in commit. |
| R7 — No DATA_DICTIONARY update needed | PASS | No schema change. |
| R8 — Commit message | PASS-WITH-NOTES | Conventional Commits scope `feat(ops):` correct. References `OPS-T7`, both verdict file paths, option (iii). **Subject line is 86 characters — exceeds the 72-character limit in CLAUDE.md §8.** Not a blocking failure for this direct-to-master commit (the commit already landed), but should be corrected in future commits. |
| R9 — One commit | PASS | Single commit `3570af2`. |
| R10 — Read-only invariant | PASS | `qa_interpreter.py`: no `open(`, `write`, `dump` calls found. |
| R11 — qa_interpreter.py imports only stdlib/cdb_core | PASS | Only `re` and `dataclasses` imported. No `cdb_collect`, `cdb_analyze`, `cdb_publish`, `cdb_social`, or LLM client imports. |

### SME 10 binding edits

| Edit | Result | Evidence |
|---|---|---|
| 1. Q1 option (iii) bare-integer disambiguation | PASS | Only-segment bare int → `freelist_too_low`; trailing bare int after other shorthands → `token_inconsistency_or_campaign_tag`. Both branches present in `qa_interpreter.py:190–215`. |
| 2. `freelist_too_low` impact: "operator should exclude" | PASS | `qa_interpreter.py` line: *"Operator should exclude or flag this run when computing grouped salience; the analysis pipeline does not currently filter on `qa_passed` automatically."* |
| 3. `uniqueness_too_low` impact: >=2-runs precondition + "independent elicitation across runs" | PASS | Text: *"Aggregate concern, computed across the >=2 runs for this (model, domain) group — not on this single record. The group's salience structure may reflect rote output rather than independent elicitation across runs."* |
| 4. `token_inconsistency` impact: chars/4 heuristic is the loose part | PASS | Trailing-bare-int impact: *"heuristic-only flag, run remains usable … The two cases cannot be distinguished from the qa_notes string alone."* |
| 5. Q2 = (a): banner above QA badge | PASS | `app.py` line 244: `st.subheader(f"Detail — ...")` followed by banner block at lines 246–257, then QA badge at lines 258+. |
| 6. Q3 banner verbatim | PASS-WITH-NOTES | Text in `app.py`: *"This run has {N} classified decline event(s). See Decline summary and Decline events sections below."* Substantive words match the SME binding exactly. **Deviation:** SME verdict uses `**Decline summary**` and `**Decline events**` (bold), but the implementation and the user's own review instructions both omit the bold markers. The user's review instructions explicitly note "no bold around section names." Treated as pre-authorized deviation — non-blocking. |
| 7. Q4 caption rewordings for both branches | PASS | own_freelist: *"Items sorted: this informant's own Step 1 freelist ({N} items)."* External: *"Items sorted: items from `{item_source}` ({N} items). Not derived from this informant's own freelist — see `PileSortRecord.item_source` for source semantics."* Both present. |
| 8. Q5 = (a): `sum(len(pile) for pile in parsed_piles)` | PASS | `detail.py`: exactly `return sum(len(pile) for pile in record.pile_sort.parsed_piles)`. |
| 9. QI-T5/T6/T12 expected counts per option (iii) | PASS | QI-T5: `len(result) == 2` (`[latency_exceeded, token_inconsistency_or_campaign_tag]`). QI-T6: `len(result) == 3` (`[freelist_too_low, latency_exceeded, token_inconsistency_or_campaign_tag]`). QI-T12: `len(result) == 1` (`[freelist_too_low]`). All correct. |
| 10. Forbidden-vocab clearance | PASS | AST-T5 parametrized test covers all §7 and §1.5.4 patterns across `app.py`, `lib/qa_interpreter.py`, `lib/detail.py`. QI-T14 covers the interpretation table. Direct scan of diff confirms clean. |

### A1 — QA-notes interpreter spot-checks

- **A1.1** `QaInterpretation` dataclass with `code`, `why`, `impact`, `raw_segment` fields: PASS (`qa_interpreter.py:45–57`).
- **A1.2** Table covers all required codes: PASS. `latency_exceeded`, `label_count_mismatch`, `uniqueness_too_low`, `matrix_non_binary`, `matrix_asymmetric`, `empty_request_id`, `freelist_too_low` (bare-int only-segment), `token_inconsistency_or_campaign_tag` (bare-int trailing), `unknown` all present.
- **A1.3** Splits on `"; "`, classifies each segment, bare-int disambiguation per option (iii): PASS.
- **A1.4** Empty `qa_notes` returns `[]`: PASS (tested QI-T1).
- **A1.5** `st.warning` with `**Why:**`, `**Impact on analysis:**`, raw segment on failing branch only: PASS (`app.py:273–279`).
- **A1.6** Forbidden-vocab scan passes: PASS.

### A2 — Decline banner spot-checks

- **A2.1** `_declines` lookup hoisted above QA badge: PASS (`app.py:229–241`).
- **A2.2** Banner renders directly under `st.subheader(f"Detail — ...")` and above QA badge when `len(_declines) > 0`: PASS (`app.py:244–257`).
- **A2.3** When `len(_declines) == 0`, no banner: PASS (bare `if len(_declines) > 0:` block, no else clause).
- **A2.4** Neutral framing, SME-approved wording: PASS.
- **A2.5** Downstream `### Decline summary` and `### Decline events` reuse same `_declines` value with no double-fetch: PASS (`app.py:357–387`).

### A3 — Pile-sort source caption spot-checks

- **A3.1** `pile_sort_item_count(record) -> int` in `lib/detail.py`, returns `sum(len(pile) for pile in record.pile_sort.parsed_piles)`: PASS.
- **A3.2** Both caption branches present in `app.py` under `### Pile-sort`, before the existing verbatim-provenance caption: PASS (`app.py:319–337`).
- **A3.3** Caption suppressed when `_piles` is empty: PASS (`if _piles:` guard at `app.py:321`).

---

## Blocking issues

None.

## Non-blocking notes

1. **Commit subject line 86 chars (limit 72, CLAUDE.md §8).** The subject `feat(ops): add QA-notes interpreter, decline banner, pile-sort source caption (OPS-T7)` is 86 characters. Direct-to-master commit already landed; note for future commits. No rework required.
2. **Decline banner bold markers.** The SME verdict text uses `**Decline summary**` and `**Decline events**` (rendered bold in Streamlit). The implementation omits the bold markers. The user's own review instructions explicitly authorize this deviation ("no bold around section names"). Non-blocking.

---

## Closing summary

Commit `3570af2` passes all nine binding checks and all ten CDA SME binding edits. The implementation is correct, read-only, has no forbidden vocabulary in user-facing text, imports nothing from LLM clients or the cdb_* analysis/collection layers, and the QI-T5/T6/T12 test expectations correctly reflect option (iii) disambiguation. Two non-blocking notes recorded: a commit subject line that slightly exceeds the 72-character limit, and a minor deviation on bold markers in the decline banner that is pre-authorized by the user's review instructions.

