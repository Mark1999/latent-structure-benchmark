# T11 — OCI low-concentration threshold single-source-of-truth — Architect plan (2026-06-08)

**Task:** T11 from `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md`.
**Gate path:** Architect → **CDA SME (low-touch confirm)** → Coder → Reviewer → Tester. **No UI/UX.**

## 1. Map (verified, with 2 corrections to the original audit framing)
Canonical Python SoT: `cdb_publish/lede.py:40` `OCI_LOW_CONCENTRATION_THRESHOLD = 3.0` (per
DESIGN_SYSTEM §3.3.5 item 7). `derived.py` + `schemas/manifest.py` correctly import it;
manifest.py publishes it to `manifest.json:66`; `types.ts:111` types the field.
- **Duplicate #1 (Python):** `scripts/rebaseline_corpus.py:82` re-hardcodes `= 3.0` (no import).
- **Duplicate #2 (TS):** `apps/dashboard/src/config/analysis.ts:10` `= 3.0`.
- **Correction A:** `Focus1SelfConsistencyOverview getTier` uses the SEPARATE 50/10 banding
  (`OCI_CONCENTRATED/MODERATE_THRESHOLD`, DESIGN_SYSTEM §13.4), NOT the R1-b 3.0 — not a consumer.
- **Correction B (real finding):** the TS `OCI_LOW_CONCENTRATION_THRESHOLD` export is NEVER
  imported anywhere in apps/dashboard/src (dead export), AND the published manifest field is dead.
  The dashboard consumes the backend-computed `r1_state` literal (from `derived.r1_state_for`),
  not a client-side re-derivation. So there are NO consumers to refactor — this is pure drift
  prevention. Value is stable (all copies = 3.0); not a value-correction task.

## 2. Python ruling (T11a)
`scripts/rebaseline_corpus.py`: delete the line-82 `OCI_LOW_CONCENTRATION_THRESHOLD = 3.0`; add
`from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD` (near line 59 — `scripts/publish.py`
already imports from cdb_publish, so it's available). Call sites (219–220, T-4 guard) unchanged.
Leave the Romney boundary consts (83–84) — not T11. → lede.py becomes the sole Python `3.0` literal.

## 3. TS ruling (T11b) — Option (b): keep analysis.ts, add a drift guard
Rationale: value stable; NO consumers to refactor (option a would invent scope); DESIGN_SYSTEM
§3.3.5 item 7 binds `analysis.ts` as the dashboard's named SoT (option a would demote it +
require a UI/UX DESIGN_SYSTEM amendment); a vitest-imports-published-JSON precedent already exists
(the T5 `DomainResultPublished.shape.test.ts`). Add `apps/dashboard/src/__tests__/OCI_threshold.drift.test.ts`
importing `manifest.json` + the `analysis.ts` constant + the `Manifest` type, asserting:
(1) `manifest as Manifest` typechecks; (2) `manifest.oci_low_concentration_threshold ===
OCI_LOW_CONCENTRATION_THRESHOLD`; (3) defensive `=== 3.0`. This makes the dead manifest field
load-bearing as the verification surface binding the Python SoT ↔ dashboard SoT. NO change to
analysis.ts / manifest.json / types.ts. (Option (a) — dashboard reads the manifest field at
runtime — is the right answer ONLY once a component needs to DISPLAY the threshold, e.g. the
methodology-page injection §3.3.5 mentions but which isn't implemented; backlog, not T11.)

## 4. Gates
- **CDA SME — low-touch confirm** (4 points): 3.0 stays the canonical R1-a/R1-b boundary (no value
  change); de-dup doesn't alter R1 classification semantics (`derived.r1_state_for` untouched, T-4
  predicate unchanged); no lede/published-copy change; lede.py stays the documented Python SoT.
  A PASS on these four — not a four-axis re-derivation.
- **UI/UX — NO-OP.** No visual change, no DESIGN_SYSTEM amendment, test-file-only under
  `apps/dashboard/src/__tests__/`. (Precedent: T5 shape guard shipped with no UI/UX gate.)

## 5. Scope — TWO commits (different packages, §8)
**T11a** `refactor(scripts): import OCI_LOW_CONCENTRATION_THRESHOLD from cdb_publish.lede (T11a)` —
single-file edit to rebaseline_corpus.py. AC: only one `3.0` literal for this threshold remains
(`lede.py:40`); `pytest tests/cdb_publish/` green; `rebaseline_corpus.py --smoke` succeeds, T-4
guard fires identically; ruff/mypy clean.
**T11b** `test(dashboard): add OCI threshold drift guard binding manifest to analysis.ts (T11b)` —
new vitest only; analysis.ts/manifest.json/types.ts UNCHANGED. AC: new test present; npm
build+test+lint green; Tester proves the guard via revert-and-confirm-fail (mutate analysis.ts to
3.1 → test fails → revert).

## 6. Test plan
T11a: existing `tests/cdb_publish/` (boundary + manifest-publication tests) + the smoke run prove
behavior-preservation; no new Python tests. T11b: the new vitest enforces analysis.ts===manifest;
Tester revert-and-confirm-fail proves it fires; the `Manifest` typecheck proves the field can't
vanish silently. No new fixtures (uses the static published manifest.json, rule 9).

## 7. Reviewer emphasis
`grep -rn 'OCI_LOW_CONCENTRATION_THRESHOLD.*=.*3\.0'` → exactly one hit (lede.py:40). T-4 guard
behavior intact. T11b follows the shape-test pattern; analysis.ts:10 value unchanged. No
schemas.py, no DESIGN_SYSTEM, no forbidden vocab/spend-gate. Two commits, one task each.
