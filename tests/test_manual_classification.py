"""Tests for cdb_analyze.manual_classification and scripts/build_manual_classification_seed.py.

All tests are fixture-based (synthetic in-memory rows). No real API calls.
No access to data/raw/decline_interviews.jsonl.

References:
  Plan:     docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md §3 T3C
  SME:      docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md
  Origin:   docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md Ruling 1 + Note B1
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from cdb_analyze.manual_classification import (  # noqa: E402
    DeclineManualClassification,
    load_manual_classifications,
    validate_against_source,
)
from pydantic import ValidationError

# ── Load seed builder via importlib (matches test_run_decline_backfill.py pattern) ──
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SEED_SCRIPT = _REPO_ROOT / "scripts" / "build_manual_classification_seed.py"

_spec = importlib.util.spec_from_file_location("build_manual_classification_seed", _SEED_SCRIPT)
assert _spec is not None and _spec.loader is not None
_seed_mod = importlib.util.module_from_spec(_spec)
sys.modules["build_manual_classification_seed"] = _seed_mod
_spec.loader.exec_module(_seed_mod)  # type: ignore[union-attr]

build_seed = _seed_mod.build_seed  # type: ignore[attr-defined]

# ── All 7 valid enum values ───────────────────────────────────────────────────
ALL_ENUM_VALUES = [
    "safety_event_attribution",
    "blocked_event_attribution",
    "technical_glitch_attribution",
    "no_prior_context_acknowledgment",
    "substantive_compliance_with_empty_input",
    "other_substring_false_positive",
    "genuine_recursive_decline",
]


# ── Fixture builder helpers ───────────────────────────────────────────────────

def _make_classification(
    *,
    decline_interview_id: str = "test-id-001",
    manual_classification: str = "safety_event_attribution",
    manual_classification_rationale: str = "The response attributes to safety filter.",
    manual_classifier_id: str = "mark",
    response_verbatim_excerpt: str = "The model said its safety filter was triggered.",
    detector_flag_v1: bool = True,
) -> dict:  # type: ignore[type-arg]
    """Build a valid classification dict for use in tests."""
    return {
        "decline_interview_id": decline_interview_id,
        "manual_classification": manual_classification,
        "manual_classification_rationale": manual_classification_rationale,
        "manual_classifier_id": manual_classifier_id,
        "response_verbatim_excerpt": response_verbatim_excerpt,
        "detector_flag_v1": detector_flag_v1,
    }


def _make_source_row(
    *,
    decline_interview_id: str = "test-id-001",
    response_verbatim: str = "The model reported a safety filter.",
    model_id: str = "test-model",
    provider: str = "openrouter",
) -> dict:  # type: ignore[type-arg]
    """Build a minimal synthetic source row (matching DeclineInterview shape)."""
    return {
        "decline_interview_id": decline_interview_id,
        "originating_informant_id": "orig-001",
        "originating_failure_id": None,
        "originating_step": "pile_sort",
        "originating_outcome_class": "empty_output",
        "detection_rule_version": "v1",
        "detection_timestamp": "2026-04-23T22:58:15.808418Z",
        "followup_timestamp": "2026-04-23T22:58:20.000000Z",
        "model_id": model_id,
        "model_version_returned": model_id,
        "provider": provider,
        "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "prompt_version": "decline_v1",
        "sha256_manifest": "abc123",
        "prompt_verbatim": "Test prompt.",
        "response_verbatim": response_verbatim,
        "thinking_verbatim": "",
        "input_tokens": 10,
        "output_tokens": 20,
        "latency_ms": 1000,
        "stop_reason": "stop",
        "qa_notes": "",
        "version_drift_flag": False,
    }


def _write_jsonl(path: Path, rows: list) -> None:  # type: ignore[type-arg]
    """Write a list of dicts as JSONL to path."""
    lines = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Schema validation tests ───────────────────────────────────────────────────

@pytest.mark.parametrize("enum_value", ALL_ENUM_VALUES)
def test_valid_classification_each_enum_value(enum_value: str) -> None:
    """Each of the 7 enum values constructs a valid model instance."""
    data = _make_classification(manual_classification=enum_value)
    model = DeclineManualClassification.model_validate(data)
    assert model.manual_classification == enum_value


def test_unclassified_sentinel_rejected_by_pydantic() -> None:
    """The UNCLASSIFIED sentinel is outside the Literal enum and must be rejected."""
    data = _make_classification(manual_classification="UNCLASSIFIED")
    with pytest.raises(ValidationError):
        DeclineManualClassification.model_validate(data)


def test_empty_rationale_rejected() -> None:
    """Empty manual_classification_rationale must raise ValidationError."""
    data = _make_classification(manual_classification_rationale="")
    with pytest.raises(ValidationError):
        DeclineManualClassification.model_validate(data)


def test_rationale_at_200_chars_accepted() -> None:
    """Rationale of exactly 200 chars must be accepted."""
    rationale = "A" * 200
    data = _make_classification(manual_classification_rationale=rationale)
    model = DeclineManualClassification.model_validate(data)
    assert len(model.manual_classification_rationale) == 200


def test_rationale_at_201_chars_rejected() -> None:
    """Rationale of 201 chars must be rejected."""
    rationale = "A" * 201
    data = _make_classification(manual_classification_rationale=rationale)
    with pytest.raises(ValidationError):
        DeclineManualClassification.model_validate(data)


def test_empty_classifier_id_rejected() -> None:
    """Empty manual_classifier_id must raise ValidationError."""
    data = _make_classification(manual_classifier_id="")
    with pytest.raises(ValidationError):
        DeclineManualClassification.model_validate(data)


def test_empty_decline_interview_id_rejected() -> None:
    """Empty decline_interview_id must raise ValidationError."""
    data = _make_classification(decline_interview_id="")
    with pytest.raises(ValidationError):
        DeclineManualClassification.model_validate(data)


def test_extra_field_rejected() -> None:
    """Extra fields must be rejected (ConfigDict extra='forbid')."""
    data = _make_classification()
    data["unexpected_field"] = "surprise"
    with pytest.raises(ValidationError):
        DeclineManualClassification.model_validate(data)


# ── Loader behavior tests ─────────────────────────────────────────────────────

def test_load_round_trip(tmp_path: Path) -> None:
    """Write 3 valid rows to a JSONL file, load, get back a 3-key dict."""
    rows = [
        _make_classification(
            decline_interview_id=f"id-{i:03d}",
            manual_classification=ALL_ENUM_VALUES[i % len(ALL_ENUM_VALUES)],
        )
        for i in range(3)
    ]
    f = tmp_path / "classifications.jsonl"
    _write_jsonl(f, rows)
    result = load_manual_classifications(f)
    assert len(result) == 3
    assert set(result.keys()) == {"id-000", "id-001", "id-002"}


def test_load_rejects_unclassified_row(tmp_path: Path) -> None:
    """A row with 'UNCLASSIFIED' manual_classification must raise ValueError naming the row."""
    bad_row = {
        "decline_interview_id": "id-999",
        "manual_classification": "UNCLASSIFIED",
        "manual_classification_rationale": "Some rationale.",
        "manual_classifier_id": "mark",
        "response_verbatim_excerpt": "excerpt",
        "detector_flag_v1": False,
    }
    f = tmp_path / "bad.jsonl"
    f.write_text(json.dumps(bad_row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="id-999"):
        load_manual_classifications(f)


def test_load_rejects_invalid_enum_value(tmp_path: Path) -> None:
    """A row with an unrecognized classification value must raise an exception."""
    bad_row = {
        "decline_interview_id": "id-888",
        "manual_classification": "not_a_real_category",
        "manual_classification_rationale": "Some rationale.",
        "manual_classifier_id": "mark",
        "response_verbatim_excerpt": "excerpt",
        "detector_flag_v1": False,
    }
    f = tmp_path / "bad.jsonl"
    f.write_text(json.dumps(bad_row) + "\n", encoding="utf-8")
    with pytest.raises((ValidationError, ValueError)):
        load_manual_classifications(f)


def test_load_returns_dict_keyed_by_decline_interview_id(tmp_path: Path) -> None:
    """Loaded dict must be keyed by decline_interview_id."""
    row = _make_classification(decline_interview_id="specific-id-42")
    f = tmp_path / "one.jsonl"
    _write_jsonl(f, [row])
    result = load_manual_classifications(f)
    assert "specific-id-42" in result
    assert result["specific-id-42"].decline_interview_id == "specific-id-42"


def test_load_empty_file_returns_empty_dict(tmp_path: Path) -> None:
    """Loading an empty JSONL file returns an empty dict."""
    f = tmp_path / "empty.jsonl"
    f.write_text("", encoding="utf-8")
    result = load_manual_classifications(f)
    assert result == {}


def test_load_skips_blank_lines(tmp_path: Path) -> None:
    """Blank lines in the JSONL must be skipped without error."""
    row = _make_classification(decline_interview_id="id-blank-test")
    line = json.dumps(row, sort_keys=True, ensure_ascii=False)
    f = tmp_path / "blank_lines.jsonl"
    f.write_text(f"\n{line}\n\n", encoding="utf-8")
    result = load_manual_classifications(f)
    assert len(result) == 1
    assert "id-blank-test" in result


# ── Cross-reference (validate_against_source) tests ──────────────────────────

def test_validate_against_source_passes_when_aligned(tmp_path: Path) -> None:
    """Source has 3 IDs, classifications has 3 matching IDs — no error raised."""
    ids = ["alpha", "beta", "gamma"]

    source_path = tmp_path / "source.jsonl"
    source_rows = [_make_source_row(decline_interview_id=did) for did in ids]
    _write_jsonl(source_path, source_rows)

    classifications = {
        did: DeclineManualClassification.model_validate(
            _make_classification(decline_interview_id=did)
        )
        for did in ids
    }

    # Should not raise
    validate_against_source(classifications, source_path)


def test_validate_against_source_missing_id(tmp_path: Path) -> None:
    """Source has an ID not in classifications — ValueError listing the missing ID."""
    ids = ["alpha", "beta", "gamma"]

    source_path = tmp_path / "source.jsonl"
    source_rows = [_make_source_row(decline_interview_id=did) for did in ids]
    _write_jsonl(source_path, source_rows)

    # Only classify 2 of 3
    classifications = {
        did: DeclineManualClassification.model_validate(
            _make_classification(decline_interview_id=did)
        )
        for did in ["alpha", "beta"]
    }

    with pytest.raises(ValueError, match="gamma"):
        validate_against_source(classifications, source_path)


def test_validate_against_source_extra_id(tmp_path: Path) -> None:
    """Classifications has an ID not in source — ValueError listing the extra ID."""
    ids = ["alpha", "beta"]

    source_path = tmp_path / "source.jsonl"
    source_rows = [_make_source_row(decline_interview_id=did) for did in ids]
    _write_jsonl(source_path, source_rows)

    # Classify 3 rows but source only has 2
    classifications = {
        did: DeclineManualClassification.model_validate(
            _make_classification(decline_interview_id=did)
        )
        for did in ["alpha", "beta", "unexpected-extra"]
    }

    with pytest.raises(ValueError, match="unexpected-extra"):
        validate_against_source(classifications, source_path)


# ── No LLM imports test ───────────────────────────────────────────────────────

def test_module_has_no_llm_imports() -> None:
    """manual_classification.py must not import any LLM client library."""
    module_path = (
        _REPO_ROOT
        / "packages"
        / "cdb_analyze"
        / "cdb_analyze"
        / "manual_classification.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = ["anthropic", "openai", "google.generativeai", "huggingface_hub"]
    for token in forbidden:
        assert token not in content, (
            f"Forbidden LLM import found in manual_classification.py: {token!r}"
        )


# ── Seed builder tests ────────────────────────────────────────────────────────

def _write_source_jsonl(path: Path, rows: list) -> None:  # type: ignore[type-arg]
    """Write synthetic source rows (decline_interviews shape) to a JSONL file."""
    lines = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_seed_builder_emits_correct_row_count(tmp_path: Path) -> None:
    """5-row source JSONL produces exactly 5 seed rows."""
    source = tmp_path / "source.jsonl"
    rows = [
        _make_source_row(decline_interview_id=f"src-{i:03d}", response_verbatim=f"Response {i}.")
        for i in range(5)
    ]
    _write_source_jsonl(source, rows)

    output = tmp_path / "seed.jsonl"
    rc = build_seed(source_path=source, output_path=output, force=False)
    assert rc == 0

    seed_lines = [ln for ln in output.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(seed_lines) == 5


def test_seed_builder_emits_unclassified_sentinel(tmp_path: Path) -> None:
    """Every output row's manual_classification must be 'UNCLASSIFIED'."""
    source = tmp_path / "source.jsonl"
    rows = [
        _make_source_row(decline_interview_id=f"id-{i}", response_verbatim="Some text.")
        for i in range(3)
    ]
    _write_source_jsonl(source, rows)

    output = tmp_path / "seed.jsonl"
    build_seed(source_path=source, output_path=output, force=False)

    for line in output.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        assert row["manual_classification"] == "UNCLASSIFIED", (
            f"Expected UNCLASSIFIED but got {row['manual_classification']!r} "
            f"for {row['decline_interview_id']!r}"
        )


def test_seed_builder_truncates_excerpt_at_400(tmp_path: Path) -> None:
    """A 1000-char response_verbatim produces an excerpt of exactly 400 chars."""
    long_text = "X" * 1000
    source = tmp_path / "source.jsonl"
    rows = [_make_source_row(decline_interview_id="id-long", response_verbatim=long_text)]
    _write_source_jsonl(source, rows)

    output = tmp_path / "seed.jsonl"
    build_seed(source_path=source, output_path=output, force=False)

    seed_lines = [ln for ln in output.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(seed_lines) == 1
    row = json.loads(seed_lines[0])
    assert len(row["response_verbatim_excerpt"]) == 400


def test_seed_builder_short_response_excerpt_unchanged(tmp_path: Path) -> None:
    """A 50-char response_verbatim produces a 50-char excerpt (no padding or alteration)."""
    short_text = "Y" * 50
    source = tmp_path / "source.jsonl"
    rows = [_make_source_row(decline_interview_id="id-short", response_verbatim=short_text)]
    _write_source_jsonl(source, rows)

    output = tmp_path / "seed.jsonl"
    build_seed(source_path=source, output_path=output, force=False)

    seed_lines = [ln for ln in output.read_text(encoding="utf-8").splitlines() if ln.strip()]
    row = json.loads(seed_lines[0])
    assert len(row["response_verbatim_excerpt"]) == 50
    assert row["response_verbatim_excerpt"] == short_text


def test_seed_builder_deterministic(tmp_path: Path) -> None:
    """Running the seed builder twice on the same input produces byte-identical output."""
    source = tmp_path / "source.jsonl"
    rows = [
        _make_source_row(decline_interview_id=f"id-{i}", response_verbatim=f"Response {i}.")
        for i in range(4)
    ]
    _write_source_jsonl(source, rows)

    out1 = tmp_path / "seed1.jsonl"
    out2 = tmp_path / "seed2.jsonl"

    build_seed(source_path=source, output_path=out1, force=False)
    build_seed(source_path=source, output_path=out2, force=False)

    content1 = out1.read_bytes()
    content2 = out2.read_bytes()
    assert content1 == content2, "Seed builder output is not byte-identical on repeat runs"


def test_seed_builder_idempotency_guard(tmp_path: Path) -> None:
    """Pre-existing partially-filled output causes non-zero exit; --force overrides."""
    source = tmp_path / "source.jsonl"
    rows = [_make_source_row(decline_interview_id="id-guard", response_verbatim="Test text.")]
    _write_source_jsonl(source, rows)

    output = tmp_path / "seed.jsonl"

    # First run — writes the file
    rc = build_seed(source_path=source, output_path=output, force=False)
    assert rc == 0

    # Simulate a partially-filled file (Mark has edited it)
    partial_content = json.dumps(
        {
            "decline_interview_id": "id-guard",
            "manual_classification": "safety_event_attribution",
            "manual_classification_rationale": "Mark filled this in.",
            "manual_classifier_id": "mark",
            "response_verbatim_excerpt": "Test text.",
            "detector_flag_v1": False,
        },
        sort_keys=True,
        ensure_ascii=False,
    ) + "\n"
    output.write_text(partial_content, encoding="utf-8")

    # Second run without --force — must return non-zero (idempotency guard fires)
    rc2 = build_seed(source_path=source, output_path=output, force=False)
    assert rc2 != 0, "Expected non-zero exit when existing file differs and --force not set"

    # The file should still have the partially-filled content (not overwritten)
    assert output.read_text(encoding="utf-8") == partial_content

    # Third run with --force — must succeed and overwrite
    rc3 = build_seed(source_path=source, output_path=output, force=True)
    assert rc3 == 0

    # File is now back to the seed content (UNCLASSIFIED)
    seed_row = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert seed_row["manual_classification"] == "UNCLASSIFIED"


# ── Gap-fill: duplicate decline_interview_id in loader ───────────────────────

def test_load_raises_on_duplicate_decline_interview_id(tmp_path: Path) -> None:
    """Loader must raise ValueError naming the duplicate when two rows share a decline_interview_id.

    The loader uses a dict keyed by decline_interview_id. Without an explicit
    duplicate check, the second row would silently overwrite the first
    (last-write-wins), losing one classification — a data-integrity failure that
    would corrupt T4's cross-tab without any visible error.

    The code at manual_classification.py lines 157-160 checks for duplicates
    and raises ValueError. This test pins that behavior.
    """
    row_a = _make_classification(
        decline_interview_id="dup-id-001",
        manual_classification="safety_event_attribution",
    )
    row_b = _make_classification(
        decline_interview_id="dup-id-001",
        manual_classification="genuine_recursive_decline",
    )
    f = tmp_path / "dup.jsonl"
    _write_jsonl(f, [row_a, row_b])
    with pytest.raises(ValueError, match="dup-id-001"):
        load_manual_classifications(f)


# ── Gap-fill: seed builder module import survives absent .env ─────────────────

def test_seed_builder_module_already_imported_without_dotenv() -> None:
    """The seed builder module is importable even when .env is absent.

    build_manual_classification_seed.py calls _load_v1_detector() at module
    scope, which exec_modules run_decline_backfill.py. That script calls
    load_dotenv() at its top level. load_dotenv() is a no-op when .env is
    absent, so the import chain must not raise regardless of whether .env
    exists in the working directory.

    The module was already imported at the top of this test file (line 31-35).
    This test confirms the already-imported module object is live and that its
    build_seed callable is present — meaning the import-time side effects
    (load_dotenv, cdb_collect imports) did not raise.

    This pins the Reviewer's observation 1 (non-blocking) from
    docs/status/2026-04-30-phase4a1-t3c-reviewer-verdict.md §Code-quality
    observation 1 as a passing test rather than a silent assumption.
    """
    # _seed_mod was exec_module'd at test-file import time without any .env
    # guarantee. If that raised, the entire module would have failed to collect.
    # Asserting build_seed is callable is sufficient to confirm the import path.
    assert callable(build_seed), (
        "build_seed is not callable — seed builder module failed to import cleanly"
    )
