# T4 — `detect --dry-run` poison-pill side-effects — Architect plan (2026-06-08)

**Task:** T4 from `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md`.
**Gate path:** Architect → Coder → Reviewer → Tester. **No CDA SME, no UI/UX** (see §7).

**OUTCOME — T4 DONE (`dd1b8ea`).** Architect (this plan) → Coder → Reviewer **PASS** →
Tester **PASS**. 16 regression tests added (real detectors, no mocking — the existing
dry-run tests mocked the detectors, which is why the bug shipped); full social suite
171/171 green; ruff + mypy clean. Tester ran the **revert-and-confirm-fail cycle**
(runbook §3): removing the `monthly_roundup` guard made test-4 (detector + CLI level)
FAIL, restoring made them PASS — proving the tests catch the regression. Reviewer
confirmed the critical `monthly_roundup` guard is `if not dry_run:` (NOT gated on
`triggers`) and that all guards wrap only persistence, leaving the trigger SET unchanged.
Verdict detail in §"Gate verdicts" at the foot of this doc.

## 1. Bug
`python -m cdb_social.cli detect --dry-run` is contractually side-effect-free
(cli.py `cmd_detect` docstring step 7). In practice four detectors invoked BEFORE
the dry-run branch (cli.py:486) each persist their baseline state file at trigger
time, so a dry-run silently consumes baselines and the next REAL run mistakes those
events for already-seen state.

## 2. Scope ruling — COMPLETE fix (audit under-scoped it)
The audit named only `detect_new_model`/`detect_new_domain`. Architect ruling: T4
covers ALL FOUR active state-mutating detectors + a `detect_drift` verification note.
A partial fix leaves two live poison pills:
| Detector | State file | Write site | Guard |
|---|---|---|---|
| `detect_new_model` | `seen_models.json` | triggers.py:381 | `if triggers and not dry_run:` |
| `detect_new_domain` | `seen_domains.json` | triggers.py:454 | `if triggers and not dry_run:` |
| `detect_divergence` | `divergence_highs.json` | triggers.py:749 | `if triggers and not dry_run:` |
| `detect_monthly_roundup` | `monthly_roundup.json` | triggers.py:813 | **`if not dry_run:`** (NOT gated on triggers — preserves the unconditional-on-fire write semantic; most insidious case: a dry-run on/after the 1st would mark the month fired and suppress the real run) |

`detect_drift` (cli:419, `enable=False`) early-returns at triggers.py:512–513 BEFORE
any state-file access — verified. No `dry_run` plumbing; add a one-line verification
comment at the call site so a future audit doesn't re-raise.

## 3. Mechanism — design (a): `dry_run: bool = False` keyword-only param
Chosen over snapshot/restore because (i) `monthly_roundup`'s write is unconditional
when it fires, which a one-line `if not dry_run:` handles cleanly while snapshot/restore
would have to bracket the call regardless of return; (ii) locality — each detector
docstrings its own state contract; (iii) house style — `cmd_detect` (cli:393) and
`publisher.publish` (publisher.py:180) already carry `dry_run`; (iv) test ergonomics —
the regression test can call the detector directly with `dry_run=True`.

## 4. Signatures (triggers.py) — all add keyword-only `dry_run: bool = False`
```python
def detect_new_model(manifest, state_dir, *, dry_run=False) -> list[SocialTrigger]
def detect_new_domain(manifest, state_dir, *, dry_run=False) -> list[SocialTrigger]
def detect_divergence(domain_results, state_dir, *, new_models_this_run=None, dry_run=False) -> list[SocialTrigger]
def detect_monthly_roundup(state_dir, *, now, dry_run=False) -> list[SocialTrigger]
```
Each docstring gains: "When dry_run=True, the state file is NOT written; the returned
trigger list is unchanged." `cmd_detect` forwards `dry_run=dry_run` at cli:408/414/433/441.

## 5. Acceptance criteria
1. Four detectors accept keyword-only `dry_run`.
2. `dry_run=True` → none of seen_models / seen_domains / divergence_highs /
   monthly_roundup is created or rewritten (monthly_roundup even when it would fire).
3. `dry_run=True` returns a trigger list IDENTICAL (dedupe_keys, evidence, order) to
   `dry_run=False` on the same inputs — persistence guard, not a logic change.
4. `cmd_detect` forwards the flag to all four sites; drift call carries the verify comment.
5. Existing `TestDetectCmdDryRun` (mocks detectors) still passes.
6. New `TestDetectCmdDryRunNoStatePersist` (REAL detectors) passes.
7. `pytest tests/unit/test_social_cli_detect.py tests/unit/test_social_triggers.py`,
   `ruff check .`, `mypy packages/` all green.
8. CI `cdb-social-boundary` green (no drafter instantiation added).
9. One commit: `fix(social): plug detect --dry-run state-write poison pill (T4)`,
   referencing this plan + Reviewer/Tester verdict files.

## 6. Test plan (Tester)
New class `TestDetectCmdDryRunNoStatePersist` in `tests/unit/test_social_cli_detect.py`
— **must NOT mock the detectors** (mocking is exactly why the bug shipped):
1. dry-run leaves `seen_models.json` byte-identical (new model in manifest).
2. dry-run leaves `seen_domains.json` byte-identical (new domain).
3. dry-run leaves `divergence_highs.json` byte-identical (pre-seed low high, gap exceeds).
4. **dry-run leaves `monthly_roundup.json` byte-identical EVEN WHEN firing** — highest
   priority; patch `cdb_social.cli.datetime` to a firing date vs pre-seeded
   `last_fired_month`.
5. dry-run-then-real-run round-trip: after a dry-run, the real run still emails all four
   trigger types (mock `send_digest`) — end-to-end proof the baseline wasn't consumed.
Plus direct detector tests in `tests/unit/test_social_triggers.py` (items 6–7): one per
detector asserting `dry_run=True` returns the same list AND leaves its state file
byte-identical. Mock `send_digest` (no SMTP, rule 9); never mock the detectors; use
`tmp_path`; reuse existing `_setup_*` fixture helpers.

## 7. Gates — no CDA SME, no UI/UX
Side-effect guard only: no change to detection logic, evidence, dedupe keys, thresholds,
or trigger SET; no methodology copy/lede/claim/measure; no §1.5.x framing surface; no
`apps/dashboard/` change. Boundary: no LLM/drafter added → pitfall #17 / B-1 intact,
`cdb-social-boundary` stays green. No schema/DATA_DICTIONARY surface (R7 not triggered).

## Gate verdicts

### Reviewer (commit `dd1b8ea`) — PASS
Scorecard: Checks 1/2/3/4/9 PASS; 5/6/7/8 N/A. All nine plan criteria verified:
keyword-only `dry_run` on all four detectors; all four `_atomic_write_json` sites
guarded; **`detect_monthly_roundup` guard is `if not dry_run:` (NOT `if triggers and
not dry_run:`)** — preserves the unconditional-on-fire write semantic; guards wrap only
persistence so the returned trigger SET is identical under both `dry_run` values
(core correctness property CONFIRMED); `cmd_detect` forwards the flag to all four sites +
`detect_drift` verification comment present; new CLI tests do NOT mock the detectors and
DO mock `send_digest` (rule 9); tests 4 + 5 present; scope = exactly 4 files (no schema /
DATA_DICTIONARY / deps / `out/rebaseline/`); B-1 / pitfall-#17 boundary intact
(`cdb-social-boundary` green); no forbidden vocabulary; Conventional Commits referencing
plan + T4. Live gate: 116/116 pass, ruff clean, mypy clean.

### Tester (commit `dd1b8ea`) — PASS
No additions — the 16 shipped tests are correct + complete. Full social suite
(`test_social_cli_detect` + `test_social_triggers` + `test_social_admin_console`):
**171 passed**. **Revert-and-confirm-fail cycle (runbook §3):** removed the
`if not dry_run:` guard from `detect_monthly_roundup` → both
`TestDetectMonthlyRoundupDryRun::test_dry_run_state_file_byte_identical_when_firing`
and the CLI-level `test_dry_run_monthly_roundup_byte_identical_when_firing` FAILED
(state file mutated `2026-04` → `2026-05`); restored via `git checkout` → both PASS.
Coverage-gap verdict COMPLETE: per-detector trigger-list-identical assertions (dedupe_key
lists compared, not just lengths) + state-file-byte-identical assertions present for all
four; `detect_divergence` exercises a genuine firing path (seeded high 0.3, gap 0.6,
delta 0.3 ≫ MIN_DIVERGENCE_DELTA 0.02), not a no-op; CLI round-trip (test 5) proves
baselines not consumed. No detectors mocked; `send_digest` mocked; `tmp_path` throughout.
