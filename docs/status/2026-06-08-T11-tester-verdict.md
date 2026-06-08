# T11 — OCI low-concentration threshold de-dup — Tester verdict (2026-06-08)

**Task:** T11 OCI single-source-of-truth — commits `59dfa0d` (T11a) + `cac3ea2` (T11b)
**Tester:** Tester agent (claude-sonnet-4-6)
**Verdict: PASS**
**Plan reference:** `docs/status/2026-06-08-T11-architect-plan.md`

---

## 1. T11a — Python behavior-preservation

### 1.1 Single grep-hit verification

```
grep -rn 'OCI_LOW_CONCENTRATION_THRESHOLD.*=.*3\.0' packages/ scripts/
```

Result: exactly **one hit**:

```
packages/cdb_publish/cdb_publish/lede.py:40:OCI_LOW_CONCENTRATION_THRESHOLD: float = 3.0
```

No hit in `scripts/rebaseline_corpus.py` — the local `= 3.0` literal has been removed and replaced with `from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD` at line 61.

### 1.2 Import-resolves sanity check

```
uv run python -c "from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD as t; print(t)"
```

Output: `3.0` — import resolves correctly.

### 1.3 pytest tests/cdb_publish/ baseline

```
uv run pytest tests/cdb_publish/ -q
```

Result: **91 passed** in 241s. No failures, no warnings affecting behavior. Behavior-preservation confirmed: T-4 guard call sites (lines 220–221 of rebaseline_corpus.py) are unchanged; they now consume the imported constant rather than the deleted local literal.

### 1.4 Smoke run

```
uv run python scripts/rebaseline_corpus.py --smoke
```

Output (relevant lines):
```
INFO rebaseline_corpus.py starting — bootstrap_B=5 domain=family
INFO [family] Already complete in manifest — skipping
INFO   family: guard=pass bootstrap_B=500 model_count=15 sha256=fb4d988eec11...
INFO Manifest: /opt/lsb-agent/out/rebaseline/baseline_manifest.json
INFO Staging root: /opt/lsb-agent/out/rebaseline
```

Guard fires identically (`guard=pass`). T-4 predicate semantics unchanged. Smoke exits 0.

---

## 2. T11b — Dashboard drift guard

### 2.1 Build + test + lint baseline

```
cd apps/dashboard && npm run build && npm run test && npm run lint
```

Results:
- **build:** `tsc -b && vite build` — 64 modules transformed, built in 3.20s. Exit 0.
- **test:** `vitest run` — **86 passed** (7 test files). Exit 0.
- **lint:** `eslint .` — clean. Exit 0.

Both new assertions in `OCI_threshold.drift.test.ts` pass:
```
✓ OCI_LOW_CONCENTRATION_THRESHOLD drift guard (T11b) > manifest.oci_low_concentration_threshold matches analysis.ts constant
✓ OCI_LOW_CONCENTRATION_THRESHOLD drift guard (T11b) > OCI_LOW_CONCENTRATION_THRESHOLD is exactly 3.0 (defensive sentinel)
```

### 2.2 Revert-and-confirm-fail (plan §5 T11b AC5 — load-bearing proof)

**Mutation applied:** `apps/dashboard/src/config/analysis.ts` line 10 changed from `= 3.0` to `= 3.1`.

**Test run result:** 2 failures, 84 passed (1 file failed):

```
× OCI_LOW_CONCENTRATION_THRESHOLD drift guard (T11b) > manifest.oci_low_concentration_threshold matches analysis.ts constant
  → expected 3 to be 3.1 // Object.is equality

  AssertionError: expected 3 to be 3.1 // Object.is equality
    - Expected: 3.1
    + Received:  3
    at src/__tests__/OCI_threshold.drift.test.ts:39:58

× OCI_LOW_CONCENTRATION_THRESHOLD drift guard (T11b) > OCI_LOW_CONCENTRATION_THRESHOLD is exactly 3.0 (defensive sentinel)
  → expected 3.1 to be 3 // Object.is equality

  AssertionError: expected 3.1 to be 3 // Object.is equality
    - Expected: 3
    + Received:  3.1
    at src/__tests__/OCI_threshold.drift.test.ts:52:45
```

Both assertions fire as designed. The `manifest.oci_low_concentration_threshold === OCI_LOW_CONCENTRATION_THRESHOLD` assertion (test 1) catches the analysis.ts ↔ manifest.json drift. The defensive sentinel (test 2) catches the raw value change. This confirms the guard is not inert — it would catch a real drift event.

**Restore:** `git checkout -- apps/dashboard/src/config/analysis.ts`

**Post-restore test run:** `vitest run` — **86 passed** (7 test files). Exit 0. Green confirmed.

---

## 3. Working tree at HEAD

After all scratch edits restored:

```
git status --short
?? WritingSample/
?? docs/status/2026-06-08-T11-architect-plan.md
?? docs/status/2026-06-08-T11-cda-sme-verdict.md
?? out/rebaseline/
```

Tree is clean at HEAD `cac3ea2`. No tracked files modified. Untracked personal/staging dirs untouched per task constraints.

---

## 4. Summary table

| Check | Result |
|---|---|
| Single `3.0` literal hit (`lede.py:40`) | PASS — exactly 1 hit |
| `rebaseline_corpus.py` imports from `cdb_publish.lede` | PASS — line 61 |
| Import resolves to `3.0` at runtime | PASS |
| `pytest tests/cdb_publish/` | PASS — 91 passed |
| `rebaseline_corpus.py --smoke` | PASS — guard=pass, exit 0 |
| `npm run build` | PASS — exit 0 |
| `npm run test` (baseline) | PASS — 86 passed |
| `npm run lint` | PASS — clean |
| Revert-and-confirm-fail (analysis.ts → 3.1) | PASS — 2 failures as designed |
| Post-restore green | PASS — 86 passed |
| Tree at HEAD after all mutations restored | PASS — clean |

**Overall: PASS — T11 pipeline complete.**
