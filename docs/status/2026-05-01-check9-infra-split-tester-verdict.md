# Tester Verdict — Check 9 infrastructure split (task #F2-T11)

**Commit verified:** `36d180e` (fix(scripts): split check 9 (infra) out of per-record QA battery)
**Follow-up commit:** `a8d816b` (test(scripts): follow-up coverage for check-9 infra split)
**Date:** 2026-05-01
**Verdict:** PASS (with follow-up tests added)

---

## Verification checklist

### 1. Four new tests from the Coder commit — all present and fixture-only

| Test | File | Present | Real API call? |
|---|---|---|---|
| `test_infrastructure_check_returns_check_9_when_log_missing` | `tests/unit/test_qa_check.py:497` | YES | No — monkeypatch on `_BACKUP_LOG_PATH` |
| `test_run_record_checks_does_not_invoke_check_9` | `tests/unit/test_qa_check.py:509` | YES | No — monkeypatch on `_BACKUP_LOG_PATH` |
| `test_post_infrastructure_alert_posts_expected_fields` | `tests/unit/test_qa_check.py:524` | YES | No — `patch("scripts.qa_check.requests.post")` |
| `test_run_informant_no_backup_log_does_not_fail_qa` | `tests/unit/test_runner.py:274` | YES | No — monkeypatch + mock adapter |

All four tests use only monkeypatch, MagicMock, or `unittest.mock.patch`. No real network calls, no real API keys, no real webhook URLs.

### 2. Pre-existing check_9 unit tests — unmodified and still pass

The four direct `check_9_backup_freshness(log_path=...)` tests that the plan required to survive intact:

| Test | Current line | Status |
|---|---|---|
| `test_check9_log_missing_returns_failure` | 444 | PASS |
| `test_check9_log_49h_old_returns_failure` | 453 | PASS |
| `test_check9_log_1h_old_passes` | 469 | PASS |
| `test_check9_log_exactly_48h_returns_failure` | 481 | PASS |

(Plan referenced original line numbers 442/458/473/485 — these shifted slightly due to the new tests being appended above in the same commit, but the test bodies are byte-for-byte unmodified as confirmed by `git show`.)

### 3. Seven previously-failing tests — now green

All pass without modification to the test code. The runner and qa_check production edits in `36d180e` made them green, exactly as the plan specified.

| Test | Status |
|---|---|
| `test_qa_check.py::test_passing_record_no_failures` | PASS |
| `test_qa_passed_honest.py::TestT07HonestQaPassed::test_passing_record_has_qa_passed_true` | PASS |
| `test_qa_passed_honest.py::TestT07HonestQaPassed::test_passing_record_with_campaign_id` | PASS |
| `test_qa_passed_honest.py::TestT09LabelCountMismatch::test_matched_count_record_passes_check_8` | PASS |
| `test_runner.py::test_run_informant_default_temperature_and_empty_qa_notes` | PASS |
| `test_runner.py::test_run_informant_campaign_id_written_to_qa_notes` | PASS |
| `test_runner.py::test_run_informant_temperature_and_campaign_id_together` | PASS |

### 4. Full test suite

```
===================== 751 passed, 26313 warnings in 13.14s =====================
```

(Before the follow-up commit; 753 after.)

---

## Coverage gap assessment

Three gaps were specified in the Tester brief. Assessment:

### Gap 2 — "QA Infrastructure Failure" header (ALREADY COVERED)

`test_post_infrastructure_alert_posts_expected_fields` (line 541) explicitly asserts:

```python
assert "QA Infrastructure Failure" in payload_text
```

This test was written by the Coder. No follow-up needed.

### Gap 1 — run_qa_checks shim concatenates checks 1–8 + 9 (REAL GAP — test added)

The existing `test_passing_record_no_failures` and `test_failing_record_has_failures` both call `run_qa_checks` but neither verifies that check 9 failures are included in the return value. The shim implementation is `run_record_checks(record, all_records) + run_infrastructure_checks()` — if someone swapped this to just `run_record_checks(...)`, neither existing test would catch it.

Follow-up test added: `test_run_qa_checks_shim_concatenates_check_9_failures`

Strategy: monkeypatch `_BACKUP_LOG_PATH` to a nonexistent path, call `run_qa_checks(_record())`, assert exactly one failure with `check_num == 9` is present.

### Gap 3 — check_record does not route check 9 through post_to_slack (REAL GAP — test added)

`check_record` (the per-record CLI helper at `qa_check.py:456`) was not imported or tested anywhere in `test_qa_check.py`. The task brief specifically required a test verifying it does NOT call `post_to_slack` for infrastructure conditions (SME mandatory note 2: `post_infrastructure_alert` vs `post_to_slack` separation).

Follow-up test added: `test_check_record_does_not_route_check_9_through_post_to_slack`

Strategy: monkeypatch `_BACKUP_LOG_PATH` to nonexistent, call `check_record(_record())` under `patch("scripts.qa_check.requests.post")`, assert return is `True` and `mock_post` was not called.

---

## Follow-up commit

**SHA:** `a8d816b`
**Contents:** 2 new tests + `check_record` added to import list in `test_qa_check.py`
**Production code changed:** None (test-only commit)
**Test counts after follow-up commit:** 753 passed
**ruff:** clean
**mypy packages/:** clean

---

## Test counts summary

| Category | Count |
|---|---|
| Total passing after commit `36d180e` | 751 |
| New tests added by `36d180e` | 4 |
| Follow-up tests added in `a8d816b` | 2 |
| Total passing after `a8d816b` | 753 |

---

## Final verdict

**PASS.** The Coder's four new tests are well-formed, fixture-only, and cover the specified scenarios. Two coverage gaps (shim concatenation verification; `check_record` isolation from `post_to_slack`) were identified and addressed in a single follow-up test commit (`a8d816b`). The full suite is green at 753 tests. No production code was modified.
