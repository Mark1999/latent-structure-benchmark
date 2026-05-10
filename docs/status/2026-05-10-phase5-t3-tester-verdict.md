# Phase 5 T3 — Tester Verdict

**Task:** T3 — lede injection + display-derived fields + dual JSON write + manifest field  
**Commit under test:** `aef3262` (Reviewer PASS at `07c82bc`)  
**Verdict:** PASS-WITH-NOTES  
**Date:** 2026-05-10  
**Tester:** Tester agent (claude-sonnet-4-6)

---

## Test run results

### Targeted suite (`tests/cdb_publish/`)

```
39 passed in 0.82s   (before gap-fills)
43 passed in 0.82s   (after gap-fills committed at ced8feb)
```

Count breakdown (43 total):
- 8 T1 tests (`test_build.py`)
- 10 T3 integration tests (`test_build_domain_json.py`, 8 Coder + 2 gap-fills)
- 11 T3 derived tests (`test_derived.py`, 9 Coder + 2 gap-fills)
- 14 T2 lede tests (`test_lede.py`)

### Full suite

```
1258 passed, 26313 warnings in 13.66s   (after gap-fills)
```

No regressions. The pre-existing 1254 tests all continue to pass.

### ruff

```
All checks passed!
```

### mypy

```
Success: no issues found in 60 source files
```

---

## Binding behavior verification

### `test_derived.py` (9 Coder tests + 2 gap-fills)

| # | Test | Behavior covered | Result |
|---|---|---|---|
| 1 | `test_r1_state_typical_concentration` | `r1_state_for` with oci=10.0, deterministic=False → "typical_concentration" | PASS |
| 2 | `test_r1_state_low_concentration` | `r1_state_for` with oci=2.0, deterministic=False → "low_concentration" | PASS |
| 3 | `test_r1_state_deterministic_overrides_oci` | `r1_state_for` with deterministic=True, any oci → "deterministic" (priority check) | PASS |
| 4 | `test_r1_state_boundary_at_threshold` | `r1_state_for` at oci exactly == OCI_LOW_CONCENTRATION_THRESHOLD → "typical_concentration" (strict less-than) | PASS |
| 5 | `test_top_freelist_terms_basic_ranking` | CSI descending sort | PASS |
| 6 | `test_top_freelist_terms_k_parameter` | k=3 and k=1 both respected | PASS |
| 7 | `test_top_freelist_terms_stable_tiebreak` | Lexicographic ascending tie-break on equal CSI | PASS |
| 8 | `test_top_freelist_terms_empty_input` | Empty dict → [] | PASS |
| 9 | `test_top_terms_metric_constant` | `TOP_TERMS_METRIC == "sutrop_csi"` and `DEFAULT_TOP_K == 5` (Q4 binding) | PASS |
| G1 | `test_top_freelist_terms_k_zero_returns_empty` | k=0 → [] for non-empty input (gap-fill) | PASS |
| G2 | `test_top_freelist_terms_k_exceeds_input_length` | k=100 on 2-item input → all 2 items returned (gap-fill) | PASS |

### `test_build_domain_json.py` (8 Coder tests + 2 gap-fills)

| # | Test | Behavior covered | Result |
|---|---|---|---|
| 1 | `test_published_json_has_nonempty_lede` | Lede injection: generated_lede non-empty after build() | PASS |
| 2 | `test_display_r1_states_keyed_by_all_mds_models` | r1_states keyed by every model in mds_coordinates, all valid state values | PASS |
| 3 | `test_display_top_terms_keyed_by_sutrop_csi_models` | top_terms keyed by models with sutrop_csi, non-empty lists | PASS |
| 4 | `test_display_top_terms_metric_is_sutrop_csi` | display.top_terms_metric == "sutrop_csi" (Q4 binding) | PASS |
| 5 | `test_versioned_and_unversioned_files_byte_identical` | {slug}.json and {slug}.v{version}.json exist and byte-identical | PASS |
| 6 | `test_manifest_carries_oci_threshold` | manifest.oci_low_concentration_threshold == OCI_LOW_CONCENTRATION_THRESHOLD (3.0); checked against constant AND serialized disk value | PASS |
| 7 | `test_source_files_byte_identical_after_build` | SHA256 of data/results/family/0.2.json and holidays/0.2.json unchanged before/after build() (AC6 append-only invariant) | PASS |
| 8 | `test_real_corpus_smoke` | Real corpus: family (11 models in r1_states), holidays (9 models), non-empty ledes, manifest threshold, top_terms_metric | PASS |
| G3 | `test_display_r1_states_fallback_for_missing_within_model_result` | Model in mds_coordinates absent from within_model_results → "typical_concentration" fallback (gap-fill) | PASS |
| G4 | `test_display_top_terms_absent_when_no_sutrop_csi` | No sutrop_csi data → top_terms == {} without error (gap-fill) | PASS |

---

## No-real-API-calls check

Grep of `tests/cdb_publish/` for `httpx`, `requests`, `aiohttp`, `urllib.request`, `anthropic`, `openai`, `google.generativeai`: all hits are fixture string literals (provider name in model dicts) or the `test_no_llm_imports_in_lede_py` test that checks those strings are *not* imported. Zero live API calls. Rule 10 satisfied.

---

## Build artifact hygiene

- `.gitignore` line 49: `apps/dashboard/public/data/` correctly suppresses dashboard output.
- `git status --short` after the full test run: only `?? HARDWARE.md` (Mark's file). No JSON build artifacts tracked.

---

## Manifest `oci_low_concentration_threshold` source check

`packages/cdb_publish/cdb_publish/schemas/manifest.py` imports `OCI_LOW_CONCENTRATION_THRESHOLD` from `cdb_publish.lede` and uses it as the Pydantic field default. `build.py` constructs `Manifest()` without passing `oci_low_concentration_threshold` explicitly — it relies on the schema default. The docstring comment in `build.py` ("Write manifest.json with oci_low_concentration_threshold = 3.0") is informational and correct as of the constant's current value. The constant is not hardcoded in executable code.

---

## Coverage gaps found and resolved

Four gaps were identified and filled in commit `ced8feb`:

**Gap 1 — `top_freelist_terms(k=0)`**  
Not tested by the Coder. Added `test_top_freelist_terms_k_zero_returns_empty` to `test_derived.py`.

**Gap 2 — `top_freelist_terms(k > len(input))`**  
Not tested by the Coder. Added `test_top_freelist_terms_k_exceeds_input_length` to `test_derived.py`.

**Gap 3 — `_compute_display` fallback for model absent from `within_model_results`**  
The fallback to `"typical_concentration"` is documented in `build.py` but had no machine-verifiable test. Added `test_display_r1_states_fallback_for_missing_within_model_result` to `test_build_domain_json.py`. The test confirms the fallback fires correctly.

**Gap 4 — `_compute_display` with no `sutrop_csi` data**  
`_minimal_domain_result(include_sutrop_csi=False)` existed in the fixture helper but was never called in any test. Added `test_display_top_terms_absent_when_no_sutrop_csi` to `test_build_domain_json.py`. The test confirms `display.top_terms == {}` and no error is raised.

## Residual coverage notes (not gaps, no action needed)

- `r1_state_for` with oci=0.0 and `deterministic_output=False`: not explicitly tested, but the `low_concentration` path is fully covered by `test_r1_state_low_concentration` (oci=2.0). The oci=0.0 case with `deterministic=True` is tested in Test 3 for a different purpose.
- Multi-version dual-write with T3 derived fields: the `test_build_selects_latest_version` test in `test_build.py` confirms version selection behavior. The T3 integration tests operate on single-version inputs; the derived field computation is version-agnostic (it is called once, on the selected version, regardless of how many version files exist), so no additional multi-version T3 test is warranted.

---

## Files written or modified

- `/opt/lsb-agent/tests/cdb_publish/test_derived.py` — 2 gap-fill tests appended
- `/opt/lsb-agent/tests/cdb_publish/test_build_domain_json.py` — 2 gap-fill tests appended
- `/opt/lsb-agent/docs/status/2026-05-10-phase5-t3-tester-verdict.md` — this file

Gap-fill commit: `ced8feb` (`test(publish): gap-fill edge cases for Phase 5 T3 derived/build tests`)
