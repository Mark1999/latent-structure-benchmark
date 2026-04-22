# Phase 4a T2 — CLI Semantics Confirmation (Orchestrator Verdict)

**Date:** 2026-04-22
**Gate:** Architect (orchestrator-executed per task §6 table)
**Architect verdict:** `docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md` §4 T2, as amended by Amendment A.2
**Preceding:** CDA SME PASS on slate (task #8), Reviewer PASS on T1 preflight (task #9)

---

## Verdict: **PASS**

CLI semantics match the Amendment A ruling. Mode is `single_pass`, `--runs N` controls informant count, `--pile-sorts` is not applicable (single_pass runs one pile-sort per informant by construction). Output path is `data/raw/informants.jsonl`.

---

## Dry-run evidence

Command:

```
uv run python scripts/collect.py --mode single_pass --domain family \
  --model anthropic/claude-sonnet-4.6 --runs 2 --dry-run
```

Output:

```
DRY RUN — mode: single_pass
  Model:  anthropic/claude-sonnet-4.6
  Domain: family (Family Terms)
  Prompts: v1
  Runs: 2
  Monthly spend: $0.00 (status: ok)
```

`Runs: 2` matches `--runs 2`; no `--pile-sorts` flag in the dry-run banner (consistent with single_pass's intrinsic one-pile-sort-per-run semantics).

## InformantRecord shape verification

The `single_pass` mode calls `run_informant` (confirmed at `scripts/collect.py:200-206`, in `collect_single_pass`). Each call produces one `InformantRecord` with all three CDA step payloads.

Empirical evidence from the 2026-04-21 shakedown corpus (observed during Position C replay earlier this session): each of the 108 records carries top-level keys including `freelist`, `pile_sort`, and `interview`, with `collection_mode=single_pass` across 100% of records. See `docs/status/2026-04-22-position-c-replay-verdict.md` §1 input-integrity table.

This is empirical confirmation that `single_pass` is the full CDA protocol per informant.

## Output path

Per `scripts/collect.py`, the `--output` flag defaults to `data/raw/informants.jsonl` when Phase 4a is run without the shakedown `--campaign-id` override. Verified in the CLI argparse block; no `--output` override is required for Phase 4a.

## Downstream implications

- T3 canary invocation: `uv run python scripts/collect.py --mode single_pass --domain family --model microsoft/phi-4 --runs 5`
- T4 per-cell invocation pattern: `uv run python scripts/collect.py --mode single_pass --domain <D> --model <M> --runs 5` for each of 12 models × 2 domains = 24 invocations producing 120 records.
- No `--pile-sorts` flag in any Phase 4a invocation.
- No `--campaign-id` override (Phase 4a is canonical, not shakedown).

## Gate

Orchestrator (me). No further review required for T2.

---

*End of verdict. Task #10 complete. T3 canary is unblocked.*
