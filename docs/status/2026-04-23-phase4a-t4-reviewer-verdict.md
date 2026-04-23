# Phase 4a T4 — Reviewer Verdict

**Date:** 2026-04-23
**Commit reviewed:** `b2b74e4 feat(scripts): Phase 4a T4 full 12-model × 2-domain × N=5 run`
**Architect verdict:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` §4 T4 + Amendment A
**Slate verdict:** `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md`
**Superseding directive:** 2026-04-23 failures-as-findings directive + `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` (resolves the report's open "NO GO for T5" disposition).
**Preceding gates:** Reviewer only per Architect §6 gate table.

---

## Verdict: **PASS-WITH-NOTES**

Three non-blocking forward notes. All R-rule checks PASS. Runner + report are operationally accurate records of what happened.

---

## Scope

Exactly 2 files:
- `scripts/run_phase4a_t4.sh`
- `docs/status/2026-04-22-phase4a-t4-run-report.md`

No code changes to `cdb_collect/`, no schema changes, no test changes.

## Runner script correctness

- `set -u` (NOT `-e`) at line 8; comment explains rationale. Correct — runner must continue past cell failures per Architect brief.
- Per-stream output via `--output data/raw/informants-t4-<name>.jsonl` avoids concurrent-append races. ✓
- 5 streams present; all 5 PIDs waited at line 80. ✓
- Cell counts match slate exactly: anthropic 4, openai 4, google 2, xai 2, openrouter 12. **Total: 24 cells.** ✓
- All 12 canonical model IDs match Architect verdict §1 (no aliases). ✓
- Each invocation: `--mode single_pass --runs 5`. Amendment A satisfied.
- No `--pile-sorts` flag (Amendment A.1 omitted it). ✓
- No `--campaign-id` (Phase 4a canonical, not shakedown). ✓

## Run report accuracy

- Report correctly identifies 4 failure classes: gemini/glm systematic, grok-4 QA_FAIL, gpt-5.4-mini truncation, **qwen3.6-plus 10/10 FAIL** (explicitly documented at lines 118–126).
- Report header: 101 total records (97 T4 + 4 T3 canary). Matches current `scripts/inspect.py --count` output.
- Commit message and report are consistent: "4 failure classes" tally matches.
- **Correction to my earlier characterization:** I had flagged Qwen 10/10 FAIL as unreported. It IS reported. I was wrong.

## R-rule findings

| # | Check | Result |
|---|---|---|
| 2 | Append-only JSONL | PASS — runner writes to per-stream files; external `cat ... >>` merge is append-compatible; no existing lines modified |
| 4 | Forbidden vocabulary | PASS — no §1.5.4 terms in either file |
| 5 | Schema + DATA_DICTIONARY | N/A |
| 6 | New deps | N/A |
| 7 | Prompt versioning | N/A |
| 8 | Uncertainty in viz | N/A |
| 9 | No LLM imports in cdb_analyze | N/A |
| 10 | No real API calls in tests | N/A |
| 3 | No secrets | PASS — `max_tokens` is a technical parameter, not a credential; `uv run python scripts/collect.py` picks up creds from `.env` at runtime |
| Prerequisite gates | PASS — Architect verdict + Amendment A present; slate SME verdict present; no CDA SME or UI/UX gate required for T4 |

## Commit message

`feat(scripts): Phase 4a T4 full 12-model × 2-domain × N=5 run` — 49 chars, references Architect verdict and Amendment A. Conforming.

---

## Forward notes (non-blocking)

### Note 1 — Runner script has no embedded merge step

The script's header comment describes post-stream merge into `data/raw/informants.jsonl`, but the script body has no `cat data/raw/informants-t4-*.jsonl >> data/raw/informants.jsonl` step. The merge was performed externally/manually. For audit completeness this is fine (run report documents the merge), but a future runner revision could add the merge step in-script for self-containedness. **Low priority; T7 hygiene opportunity.**

### Note 2 — Qwen reporting correction

Earlier in this session I characterized the T4 report as understating failure scope by missing Qwen 10/10 FAIL. The Reviewer confirmed Qwen is documented at report lines 118–126. My earlier characterization was wrong. **No action — the report is accurate as written.**

### Note 3 — "NO GO for T5" framing superseded

The T4 report ends with a "NO GO for T5 analysis — 4 failure classes must be resolved" disposition. The 2026-04-23 failures-as-findings directive **supersedes** this — failures are findings, the 4 classes ARE the data, T5 proceeds once Stream A (audit + #23 + #24) closes and Stream B SME PASS lands. The report's framing is a historical record of what the Coder recommended at the time, before Mark's directive. **No retroactive change to this commit required.**

---

*End of verdict. Task #12 complete. The T4 operational record is preserved as-is; the directive-driven disposition is captured in `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` and `docs/status/2026-04-23-phase4a-open-items.md` §3.*
