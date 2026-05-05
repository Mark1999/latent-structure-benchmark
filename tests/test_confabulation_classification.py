"""Tests for cdb_analyze.confabulation_classification and
scripts/build_confabulation_classification_seed.py and
scripts/inspect_confabulation_candidates.py.

All tests are fixture-based (synthetic in-memory rows or temp-file JSONL).
No real API calls.  No access to data/raw/ or data/derived/ production
artifacts — every test that needs file data writes its own fixture files to
``tmp_path``.

References:
  Architect plan:   docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-2
  CDA SME verdict:  docs/status/2026-05-05-t4-redo-cda-sme-verdict.md (T1, T2)
  Schema module:    packages/cdb_analyze/cdb_analyze/confabulation_classification.py
  Seed builder:     scripts/build_confabulation_classification_seed.py
  CLI inspector:    scripts/inspect_confabulation_candidates.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from cdb_analyze.confabulation_classification import (
    ALL_CONFABULATION_LABELS,
    ConfabulationClassification,
    load_confabulation_classifications,
    validate_no_unclassified,
)
from pydantic import ValidationError

# ── Repo root ─────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Load seed builder via importlib ───────────────────────────────────────────
_SEED_SCRIPT = _REPO_ROOT / "scripts" / "build_confabulation_classification_seed.py"

_seed_spec = importlib.util.spec_from_file_location(
    "build_confabulation_classification_seed", _SEED_SCRIPT
)
assert _seed_spec is not None and _seed_spec.loader is not None
_seed_mod = importlib.util.module_from_spec(_seed_spec)
sys.modules["build_confabulation_classification_seed"] = _seed_mod
_seed_spec.loader.exec_module(_seed_mod)  # type: ignore[union-attr]

build_seed = _seed_mod.build_seed  # type: ignore[attr-defined]

# ── Load CLI inspector via importlib ──────────────────────────────────────────
_INSPECTOR_SCRIPT = _REPO_ROOT / "scripts" / "inspect_confabulation_candidates.py"

_insp_spec = importlib.util.spec_from_file_location(
    "inspect_confabulation_candidates", _INSPECTOR_SCRIPT
)
assert _insp_spec is not None and _insp_spec.loader is not None
_insp_mod = importlib.util.module_from_spec(_insp_spec)
sys.modules["inspect_confabulation_candidates"] = _insp_mod
_insp_spec.loader.exec_module(_insp_mod)  # type: ignore[union-attr]

# ── Five concrete label values (UNCLASSIFIED excluded) ────────────────────────
VALID_LABEL_VALUES: list[str] = [
    "safety_attribution_confabulation",
    "task_paradox_confabulation",
    "topic_sensitivity_confabulation",
    "mixed_attribution",
    "not_confabulation",
]


# ── Fixture builder helpers ───────────────────────────────────────────────────


def _make_classification(
    *,
    decline_interview_id: str = "test-id-001",
    confabulation_label: str = "safety_attribution_confabulation",
    confabulation_rationale: str = "narrative attributes failure to safety protocols",
    under_blind_spot: bool = True,
    classifier_id: str = "mark",
) -> dict:  # type: ignore[type-arg]
    """Build a valid ConfabulationClassification dict for use in tests."""
    return {
        "decline_interview_id": decline_interview_id,
        "confabulation_label": confabulation_label,
        "confabulation_rationale": confabulation_rationale,
        "under_blind_spot": under_blind_spot,
        "classifier_id": classifier_id,
    }


def _make_source_row(
    *,
    decline_interview_id: str = "source-id-001",
    safety_attribution_subtype: str = "k_frame",
    subtype_rationale: str = "Some rationale text.",
    subtype_classifier_id: str = "mark",
) -> dict:  # type: ignore[type-arg]
    """Build a row shaped like the May 1 superseded safety-attribution-subtype artifact."""
    return {
        "decline_interview_id": decline_interview_id,
        "safety_attribution_subtype": safety_attribution_subtype,
        "subtype_rationale": subtype_rationale,
        "subtype_classifier_id": subtype_classifier_id,
    }


def _make_decline_interview_row(
    *,
    decline_interview_id: str = "test-id-001",
    model_id: str = "google/gemini-2.5-pro",
    response_verbatim: str = "I could not complete that task due to safety protocols.",
) -> dict:  # type: ignore[type-arg]
    """Build a minimal decline_interviews.jsonl row for fixture use."""
    return {
        "decline_interview_id": decline_interview_id,
        "model_id": model_id,
        "response_verbatim": response_verbatim,
    }


def _write_jsonl(path: Path, rows: list) -> None:  # type: ignore[type-arg]
    """Write a list of dicts as JSONL to path."""
    lines = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Schema validation: each concrete label accepted ───────────────────────────


@pytest.mark.parametrize("label", VALID_LABEL_VALUES)
def test_valid_label_each_enum_value(label: str) -> None:
    """Each of the five concrete label values constructs a valid model instance."""
    data = _make_classification(confabulation_label=label)
    model = ConfabulationClassification.model_validate(data)
    assert model.confabulation_label == label


def test_unclassified_sentinel_rejected_by_pydantic() -> None:
    """The UNCLASSIFIED sentinel is outside the Literal enum and must be rejected."""
    data = _make_classification(confabulation_label="UNCLASSIFIED")
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


def test_unknown_label_value_rejected_by_pydantic() -> None:
    """An unrecognized label value must be rejected by Pydantic."""
    data = _make_classification(confabulation_label="not_a_real_label")
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


# ── T2 guard: safety_filter_confabulation is NOT a valid enum value ──────────


def test_safety_filter_confabulation_not_valid() -> None:
    """The pre-rename value safety_filter_confabulation must NOT be accepted.

    T2 (SME binding) renames this value to safety_attribution_confabulation.
    This test guards against accidental reversion.
    """
    data = _make_classification(confabulation_label="safety_filter_confabulation")
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


def test_safety_attribution_confabulation_is_valid() -> None:
    """The T2-renamed value safety_attribution_confabulation must be accepted."""
    data = _make_classification(confabulation_label="safety_attribution_confabulation")
    model = ConfabulationClassification.model_validate(data)
    assert model.confabulation_label == "safety_attribution_confabulation"


# ── Rationale length cap ──────────────────────────────────────────────────────


def test_rationale_at_200_chars_accepted() -> None:
    """Rationale of exactly 200 chars must be accepted."""
    rationale = "A" * 200
    data = _make_classification(confabulation_rationale=rationale)
    model = ConfabulationClassification.model_validate(data)
    assert len(model.confabulation_rationale) == 200


def test_rationale_at_201_chars_rejected() -> None:
    """Rationale of 201 chars must be rejected."""
    rationale = "A" * 201
    data = _make_classification(confabulation_rationale=rationale)
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


def test_empty_rationale_accepted_by_schema() -> None:
    """Empty confabulation_rationale is accepted by the schema (seed state).

    The schema does not enforce non-empty rationale — the seed has empty
    rationale by design.  The analysis consumer enforces non-empty via
    validate_no_unclassified (which gates on label, not rationale).
    """
    data = _make_classification(confabulation_rationale="")
    model = ConfabulationClassification.model_validate(data)
    assert model.confabulation_rationale == ""


# ── decline_interview_id non-empty enforced ───────────────────────────────────


def test_empty_decline_interview_id_rejected() -> None:
    """Empty decline_interview_id must raise ValidationError."""
    data = _make_classification(decline_interview_id="")
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


# ── classifier_id non-empty enforced ─────────────────────────────────────────


def test_empty_classifier_id_rejected() -> None:
    """Empty classifier_id must raise ValidationError."""
    data = _make_classification(classifier_id="")
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


# ── under_blind_spot bool field ───────────────────────────────────────────────


def test_under_blind_spot_true_accepted() -> None:
    """under_blind_spot=True is accepted."""
    data = _make_classification(under_blind_spot=True)
    model = ConfabulationClassification.model_validate(data)
    assert model.under_blind_spot is True


def test_under_blind_spot_false_accepted() -> None:
    """under_blind_spot=False is accepted."""
    data = _make_classification(under_blind_spot=False)
    model = ConfabulationClassification.model_validate(data)
    assert model.under_blind_spot is False


# ── extra fields rejected (extra="forbid") ────────────────────────────────────


def test_extra_field_rejected() -> None:
    """Extra fields must be rejected (ConfigDict extra='forbid')."""
    data = _make_classification()
    data["unexpected_field"] = "surprise"
    with pytest.raises(ValidationError):
        ConfabulationClassification.model_validate(data)


# ── load_confabulation_classifications round-trip ─────────────────────────────


def test_loader_round_trip_all_labels(tmp_path: Path) -> None:
    """Write a fixture JSONL with one row per concrete label; load and assert correct types."""
    fixture_rows = [
        _make_classification(
            decline_interview_id=f"id-{i:03d}",
            confabulation_label=label,
            confabulation_rationale=f"narrative text for {label}",
        )
        for i, label in enumerate(VALID_LABEL_VALUES)
    ]
    fixture_path = tmp_path / "classifications.jsonl"
    _write_jsonl(fixture_path, fixture_rows)

    records = load_confabulation_classifications(fixture_path)

    assert len(records) == len(VALID_LABEL_VALUES)
    for record in records:
        assert isinstance(record, ConfabulationClassification)
        assert record.confabulation_label in VALID_LABEL_VALUES
        assert record.under_blind_spot is True
        assert record.classifier_id == "mark"


def test_loader_round_trip_re_emit_semantic_equality(tmp_path: Path) -> None:
    """Load then re-emit rows; confirm semantic equality of all fields."""
    original = _make_classification(
        decline_interview_id="id-001",
        confabulation_label="task_paradox_confabulation",
        confabulation_rationale="role-playing instruction creates logical conflict",
        under_blind_spot=True,
        classifier_id="mark",
    )
    fixture_path = tmp_path / "single.jsonl"
    _write_jsonl(fixture_path, [original])

    records = load_confabulation_classifications(fixture_path)
    assert len(records) == 1
    record = records[0]

    re_emitted = record.model_dump()
    assert re_emitted["decline_interview_id"] == original["decline_interview_id"]
    assert re_emitted["confabulation_label"] == original["confabulation_label"]
    assert re_emitted["confabulation_rationale"] == original["confabulation_rationale"]
    assert re_emitted["under_blind_spot"] == original["under_blind_spot"]
    assert re_emitted["classifier_id"] == original["classifier_id"]


def test_loader_skips_blank_lines(tmp_path: Path) -> None:
    """Blank lines in the JSONL must be skipped without error."""
    row = _make_classification(decline_interview_id="id-001")
    line = json.dumps(row, sort_keys=True, ensure_ascii=False)
    fixture_path = tmp_path / "blanks.jsonl"
    fixture_path.write_text(f"\n{line}\n\n", encoding="utf-8")

    records = load_confabulation_classifications(fixture_path)
    assert len(records) == 1
    assert records[0].decline_interview_id == "id-001"


def test_loader_empty_file_returns_empty_list(tmp_path: Path) -> None:
    """Loading an empty JSONL file returns an empty list."""
    fixture_path = tmp_path / "empty.jsonl"
    fixture_path.write_text("", encoding="utf-8")

    records = load_confabulation_classifications(fixture_path)
    assert records == []


def test_loader_raises_on_missing_file(tmp_path: Path) -> None:
    """Loader raises FileNotFoundError when the artifact file does not exist."""
    nonexistent = tmp_path / "does_not_exist.jsonl"
    with pytest.raises(FileNotFoundError):
        load_confabulation_classifications(nonexistent)


# ── Loader sentinel rejection ─────────────────────────────────────────────────


def test_loader_rejects_unclassified_sentinel(tmp_path: Path) -> None:
    """Loader must raise ValueError naming the row when UNCLASSIFIED is present."""
    sentinel_row = {
        "decline_interview_id": "id-001",
        "confabulation_label": "UNCLASSIFIED",
        "confabulation_rationale": "",
        "under_blind_spot": True,
        "classifier_id": "mark",
    }
    fixture_path = tmp_path / "seed.jsonl"
    _write_jsonl(fixture_path, [sentinel_row])

    with pytest.raises(ValueError, match="UNCLASSIFIED"):
        load_confabulation_classifications(fixture_path)


def test_loader_rejects_unclassified_names_the_row(tmp_path: Path) -> None:
    """The UNCLASSIFIED ValueError message names the offending decline_interview_id."""
    sentinel_row = {
        "decline_interview_id": "id-special-99",
        "confabulation_label": "UNCLASSIFIED",
        "confabulation_rationale": "",
        "under_blind_spot": True,
        "classifier_id": "mark",
    }
    fixture_path = tmp_path / "seed.jsonl"
    _write_jsonl(fixture_path, [sentinel_row])

    with pytest.raises(ValueError, match="id-special-99"):
        load_confabulation_classifications(fixture_path)


def test_loader_rejects_duplicate_decline_interview_id(tmp_path: Path) -> None:
    """Loader must raise ValueError naming the duplicate when two rows share an id."""
    row_a = _make_classification(
        decline_interview_id="dup-id-001",
        confabulation_label="mixed_attribution",
    )
    row_b = _make_classification(
        decline_interview_id="dup-id-001",
        confabulation_label="not_confabulation",
    )
    fixture_path = tmp_path / "dup.jsonl"
    _write_jsonl(fixture_path, [row_a, row_b])

    with pytest.raises(ValueError, match="dup-id-001"):
        load_confabulation_classifications(fixture_path)


# ── validate_no_unclassified ──────────────────────────────────────────────────


def test_validate_no_unclassified_passes_when_all_classified() -> None:
    """validate_no_unclassified does not raise when all records have concrete labels."""
    records = [
        ConfabulationClassification.model_validate(
            _make_classification(
                decline_interview_id=f"id-{i:03d}",
                confabulation_label=label,
                confabulation_rationale="some rationale",
            )
        )
        for i, label in enumerate(VALID_LABEL_VALUES)
    ]
    # Should not raise
    validate_no_unclassified(records)


def test_validate_no_unclassified_raises_on_unclassified() -> None:
    """validate_no_unclassified raises ValueError if any record has UNCLASSIFIED.

    Note: ConfabulationClassification.confabulation_label is a strict Literal
    so Pydantic prevents the sentinel from entering a validated object.  We
    use object.__setattr__ to bypass this for the test (simulating a patched
    or hand-constructed object that managed to carry the sentinel).
    """
    record = ConfabulationClassification.model_validate(
        _make_classification(
            decline_interview_id="id-001",
            confabulation_label="safety_attribution_confabulation",
        )
    )
    # Bypass Pydantic to force-set the sentinel
    object.__setattr__(record, "confabulation_label", "UNCLASSIFIED")

    with pytest.raises(ValueError, match="UNCLASSIFIED"):
        validate_no_unclassified([record])


def test_validate_no_unclassified_empty_list_passes() -> None:
    """validate_no_unclassified passes on an empty list."""
    validate_no_unclassified([])


# ── Seed builder: run against fixture data ────────────────────────────────────


def _make_source_jsonl(tmp_path: Path, rows: list) -> Path:  # type: ignore[type-arg]
    """Write source rows (May 1 artifact shape) to a temp JSONL file."""
    p = tmp_path / "source.jsonl"
    _write_jsonl(p, rows)
    return p


def test_seed_builder_emits_correct_row_count(tmp_path: Path) -> None:
    """Seed builder emits one row per ID in the source artifact."""
    source_rows = [
        _make_source_row(decline_interview_id=f"src-id-{i:03d}")
        for i in range(3)
    ]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    rc = build_seed(source_path=source_path, output_path=output_path)
    assert rc == 0

    seed_lines = [
        ln
        for ln in output_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert len(seed_lines) == 3


def test_seed_builder_emits_unclassified_sentinel(tmp_path: Path) -> None:
    """Every output row's confabulation_label must be 'UNCLASSIFIED'."""
    source_rows = [
        _make_source_row(decline_interview_id=f"src-id-{i:03d}")
        for i in range(3)
    ]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    build_seed(source_path=source_path, output_path=output_path)

    for line in output_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        assert row["confabulation_label"] == "UNCLASSIFIED", (
            f"Expected UNCLASSIFIED but got "
            f"{row['confabulation_label']!r} for "
            f"{row['decline_interview_id']!r}"
        )


def test_seed_builder_emits_under_blind_spot_true(tmp_path: Path) -> None:
    """Every output row must have under_blind_spot=True."""
    source_rows = [_make_source_row(decline_interview_id="src-id-001")]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    build_seed(source_path=source_path, output_path=output_path)

    line = [
        ln
        for ln in output_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ][0]
    row = json.loads(line)
    assert row["under_blind_spot"] is True


def test_seed_builder_emits_empty_rationale(tmp_path: Path) -> None:
    """Every output row must have confabulation_rationale=''."""
    source_rows = [_make_source_row(decline_interview_id="src-id-001")]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    build_seed(source_path=source_path, output_path=output_path)

    line = [
        ln
        for ln in output_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ][0]
    row = json.loads(line)
    assert row["confabulation_rationale"] == ""


def test_seed_builder_emits_classifier_id_mark(tmp_path: Path) -> None:
    """Every output row must have classifier_id='mark'."""
    source_rows = [_make_source_row(decline_interview_id="src-id-001")]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    build_seed(source_path=source_path, output_path=output_path)

    line = [
        ln
        for ln in output_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ][0]
    row = json.loads(line)
    assert row["classifier_id"] == "mark"


def test_seed_builder_sorted_by_decline_interview_id(tmp_path: Path) -> None:
    """Seed builder sorts output rows by decline_interview_id for determinism."""
    source_rows = [
        _make_source_row(decline_interview_id="zzz-id"),
        _make_source_row(decline_interview_id="aaa-id"),
        _make_source_row(decline_interview_id="mmm-id"),
    ]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    build_seed(source_path=source_path, output_path=output_path)

    seed_lines = [
        ln
        for ln in output_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    emitted_ids = [json.loads(ln)["decline_interview_id"] for ln in seed_lines]
    assert emitted_ids == sorted(emitted_ids), (
        f"Seed rows are not sorted by decline_interview_id: {emitted_ids}"
    )


# ── Seed builder idempotence ──────────────────────────────────────────────────


def test_seed_builder_exits_1_if_output_exists(tmp_path: Path) -> None:
    """Seed builder exits 1 and does not overwrite if output file already exists."""
    source_rows = [_make_source_row(decline_interview_id="src-id-001")]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    # First run — writes the seed file
    rc = build_seed(source_path=source_path, output_path=output_path)
    assert rc == 0

    # Simulate Mark partially filling the file
    partial_content = json.dumps(
        {
            "classifier_id": "mark",
            "confabulation_label": "safety_attribution_confabulation",
            "confabulation_rationale": "narrative invoked safety protocols",
            "decline_interview_id": "src-id-001",
            "under_blind_spot": True,
        },
        sort_keys=True,
        ensure_ascii=False,
    ) + "\n"
    output_path.write_text(partial_content, encoding="utf-8")

    # Second run — must exit 1 and not clobber
    rc2 = build_seed(source_path=source_path, output_path=output_path)
    assert rc2 == 1, "Expected exit code 1 when output file already exists"
    assert output_path.read_text(encoding="utf-8") == partial_content, (
        "Output file was modified by the idempotence-guarded run (should not happen)"
    )


def test_seed_builder_idempotence_guard_message(
    tmp_path: Path, capsys: pytest.CaptureFixture  # type: ignore[type-arg]
) -> None:
    """The idempotence guard prints a descriptive message to stderr."""
    source_rows = [_make_source_row(decline_interview_id="src-id-001")]
    source_path = _make_source_jsonl(tmp_path, source_rows)
    output_path = tmp_path / "seed.jsonl"

    # First run creates the seed
    build_seed(source_path=source_path, output_path=output_path)

    # Second run triggers the guard
    capsys.readouterr()  # clear captured output from first run
    rc2 = build_seed(source_path=source_path, output_path=output_path)
    captured = capsys.readouterr()

    assert rc2 == 1
    assert "Seed already exists" in captured.err, (
        f"Expected 'Seed already exists' in stderr, got: {captured.err!r}"
    )
    assert "remove it manually" in captured.err, (
        f"Expected 'remove it manually' in stderr, got: {captured.err!r}"
    )


def test_seed_builder_source_not_found_exits_2(tmp_path: Path) -> None:
    """Seed builder exits 2 when the source file does not exist."""
    nonexistent_source = tmp_path / "does_not_exist.jsonl"
    output_path = tmp_path / "seed.jsonl"

    rc = build_seed(source_path=nonexistent_source, output_path=output_path)
    assert rc == 2, f"Expected exit code 2 for missing source, got {rc}"
    assert not output_path.exists(), "Output file must not be created when source is missing"


# ── CLI inspector tests ───────────────────────────────────────────────────────


def _make_inspector_fixtures(
    tmp_path: Path,
    *,
    seed_rows: list,  # type: ignore[type-arg]
    decline_rows: list | None = None,  # type: ignore[type-arg]
    may1_rows: list | None = None,  # type: ignore[type-arg]
) -> tuple[Path, Path, Path]:
    """Write fixture files for the CLI inspector tests.

    Returns (seed_path, decline_path, may1_path).
    """
    seed_path = tmp_path / "seed.jsonl"
    _write_jsonl(seed_path, seed_rows)

    decline_path = tmp_path / "decline_interviews.jsonl"
    _write_jsonl(decline_path, decline_rows or [])

    may1_path = tmp_path / "may1.jsonl"
    _write_jsonl(may1_path, may1_rows or [])

    return seed_path, decline_path, may1_path


def _run_inspector(
    *,
    seed_path: Path,
    decline_path: Path,
    may1_path: Path,
    extra_args: list[str] | None = None,
) -> tuple[int, str]:
    """Run the inspector CLI programmatically and return (exit_code, stdout)."""
    import io

    # Build argparse args list
    args_list = [
        "--seed", str(seed_path),
        "--decline-interviews", str(decline_path),
        "--crosswalk", str(may1_path),
    ]
    if extra_args:
        args_list.extend(extra_args)

    buf = io.StringIO()
    # Swap stdout temporarily
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        try:
            rc = _insp_mod.main.__wrapped__(*args_list) if hasattr(  # type: ignore[attr-defined]
                _insp_mod.main, "__wrapped__"
            ) else _invoke_inspector_main(args_list)
        except SystemExit as e:
            rc = int(e.code) if e.code is not None else 0
    finally:
        sys.stdout = old_stdout

    return rc, buf.getvalue()


def _invoke_inspector_main(args_list: list[str]) -> int:
    """Invoke the inspector's main() with a specific argument list by patching sys.argv."""
    old_argv = sys.argv
    sys.argv = ["inspect_confabulation_candidates.py"] + args_list
    try:
        rc = _insp_mod.main()  # type: ignore[attr-defined]
    finally:
        sys.argv = old_argv
    return rc


def test_inspector_summary_counts_by_label(
    tmp_path: Path, capsys: pytest.CaptureFixture  # type: ignore[type-arg]
) -> None:
    """--summary flag prints correct counts for each label."""
    seed_rows = [
        {
            "decline_interview_id": f"id-{i:03d}",
            "confabulation_label": label,
            "confabulation_rationale": "",
            "under_blind_spot": True,
            "classifier_id": "mark",
        }
        for i, label in enumerate([
            "safety_attribution_confabulation",
            "task_paradox_confabulation",
            "topic_sensitivity_confabulation",
            "UNCLASSIFIED",
            "UNCLASSIFIED",
            "UNCLASSIFIED",
        ])
    ]
    seed_path, decline_path, may1_path = _make_inspector_fixtures(
        tmp_path, seed_rows=seed_rows
    )

    old_argv = sys.argv
    sys.argv = [
        "inspect_confabulation_candidates.py",
        "--seed", str(seed_path),
        "--decline-interviews", str(decline_path),
        "--crosswalk", str(may1_path),
        "--summary",
    ]
    try:
        _insp_mod.main()  # type: ignore[attr-defined]
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    stdout = captured.out

    # Check counts appear in the summary
    assert "safety_attribution_confabulation" in stdout
    assert "UNCLASSIFIED" in stdout
    assert "3" in stdout  # 3 UNCLASSIFIED
    # Classified = 3, Remaining = 3
    assert "Classified: 3" in stdout


def test_inspector_unclassified_only_filters_rows(
    tmp_path: Path, capsys: pytest.CaptureFixture  # type: ignore[type-arg]
) -> None:
    """--unclassified-only shows only UNCLASSIFIED rows."""
    seed_rows = [
        {
            "decline_interview_id": "id-classified",
            "confabulation_label": "mixed_attribution",
            "confabulation_rationale": "some rationale",
            "under_blind_spot": True,
            "classifier_id": "mark",
        },
        {
            "decline_interview_id": "id-unclassified",
            "confabulation_label": "UNCLASSIFIED",
            "confabulation_rationale": "",
            "under_blind_spot": True,
            "classifier_id": "mark",
        },
    ]
    decline_rows = [
        _make_decline_interview_row(decline_interview_id="id-classified"),
        _make_decline_interview_row(decline_interview_id="id-unclassified"),
    ]
    seed_path, decline_path, may1_path = _make_inspector_fixtures(
        tmp_path, seed_rows=seed_rows, decline_rows=decline_rows
    )

    old_argv = sys.argv
    sys.argv = [
        "inspect_confabulation_candidates.py",
        "--seed", str(seed_path),
        "--decline-interviews", str(decline_path),
        "--crosswalk", str(may1_path),
        "--unclassified-only",
    ]
    try:
        _insp_mod.main()  # type: ignore[attr-defined]
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    stdout = captured.out

    # Only the unclassified row should appear
    assert "id-unclassified" in stdout
    # The classified row header should not appear in row headers
    # (the label itself may appear in the label legend, which is fine)
    assert "id-classified" not in stdout


def test_inspector_shows_crosswalk_label(
    tmp_path: Path, capsys: pytest.CaptureFixture  # type: ignore[type-arg]
) -> None:
    """Inspector shows the May 1 cross-walk label with NON-AUTHORITATIVE marker."""
    seed_rows = [
        {
            "decline_interview_id": "id-001",
            "confabulation_label": "UNCLASSIFIED",
            "confabulation_rationale": "",
            "under_blind_spot": True,
            "classifier_id": "mark",
        }
    ]
    may1_rows = [
        _make_source_row(decline_interview_id="id-001", safety_attribution_subtype="k_frame")
    ]
    decline_rows = [_make_decline_interview_row(decline_interview_id="id-001")]

    seed_path, decline_path, may1_path = _make_inspector_fixtures(
        tmp_path,
        seed_rows=seed_rows,
        decline_rows=decline_rows,
        may1_rows=may1_rows,
    )

    old_argv = sys.argv
    sys.argv = [
        "inspect_confabulation_candidates.py",
        "--seed", str(seed_path),
        "--decline-interviews", str(decline_path),
        "--crosswalk", str(may1_path),
    ]
    try:
        _insp_mod.main()  # type: ignore[attr-defined]
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    stdout = captured.out

    assert "NON-AUTHORITATIVE" in stdout
    assert "k_frame" in stdout


def test_inspector_shows_response_verbatim(
    tmp_path: Path, capsys: pytest.CaptureFixture  # type: ignore[type-arg]
) -> None:
    """Inspector prints response_verbatim from the decline_interviews source."""
    verbatim_text = "Unique test verbatim content that should appear in output."
    seed_rows = [
        {
            "decline_interview_id": "id-001",
            "confabulation_label": "UNCLASSIFIED",
            "confabulation_rationale": "",
            "under_blind_spot": True,
            "classifier_id": "mark",
        }
    ]
    decline_rows = [
        _make_decline_interview_row(
            decline_interview_id="id-001",
            response_verbatim=verbatim_text,
        )
    ]

    seed_path, decline_path, may1_path = _make_inspector_fixtures(
        tmp_path, seed_rows=seed_rows, decline_rows=decline_rows
    )

    old_argv = sys.argv
    sys.argv = [
        "inspect_confabulation_candidates.py",
        "--seed", str(seed_path),
        "--decline-interviews", str(decline_path),
        "--crosswalk", str(may1_path),
    ]
    try:
        _insp_mod.main()  # type: ignore[attr-defined]
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert verbatim_text in captured.out


# ── No LLM imports test ───────────────────────────────────────────────────────


def test_confabulation_classification_module_has_no_llm_imports() -> None:
    """confabulation_classification.py must not import any LLM client library.

    CLAUDE.md §6 rule 12: no LLM calls in cdb_analyze.
    """
    module_path = (
        _REPO_ROOT
        / "packages"
        / "cdb_analyze"
        / "cdb_analyze"
        / "confabulation_classification.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = [
        "anthropic",
        "openai",
        "google.generativeai",
        "huggingface_hub",
        "InferenceClient",
    ]
    for token in forbidden:
        assert token not in content, (
            f"Forbidden LLM import found in confabulation_classification.py: {token!r}"
        )


# ── ALL_CONFABULATION_LABELS completeness ─────────────────────────────────────


def test_all_confabulation_labels_includes_all_values() -> None:
    """ALL_CONFABULATION_LABELS must include all 5 concrete values plus UNCLASSIFIED."""
    assert "UNCLASSIFIED" in ALL_CONFABULATION_LABELS
    for label in VALID_LABEL_VALUES:
        assert label in ALL_CONFABULATION_LABELS, (
            f"{label!r} is missing from ALL_CONFABULATION_LABELS"
        )
    assert len(ALL_CONFABULATION_LABELS) == 6


# ── Pydantic edge-case behavior documentation ─────────────────────────────────
# These tests document the *current* Pydantic behavior for edge inputs.
# They are behavioral documentation tests: if the schema is tightened later
# (e.g., strip() added to the non-empty validators), these tests will signal
# the change and require deliberate update.


def test_whitespace_only_classifier_id_accepted_by_current_schema() -> None:
    """Document: classifier_id='   ' (whitespace-only) passes the current non-empty
    validator because '   ' is truthy.

    The validator uses ``if not v``, which does not strip whitespace.  A
    whitespace-only classifier_id is technically non-empty under this rule.
    This test documents the current behavior; any future tightening (e.g.,
    ``if not v.strip()``) should be deliberate and will update this test.
    """
    data = _make_classification(classifier_id="   ")
    # Current behavior: accepted (whitespace string is truthy)
    model = ConfabulationClassification.model_validate(data)
    assert model.classifier_id == "   "


def test_whitespace_only_decline_interview_id_accepted_by_current_schema() -> None:
    """Document: decline_interview_id='   ' (whitespace-only) passes the current
    non-empty validator because '   ' is truthy.

    Same reasoning as whitespace_only_classifier_id above.  The validator uses
    ``if not v``; leading/trailing whitespace is not stripped.  This test
    documents the current behavior; any future tightening should be deliberate
    and will update this test.
    """
    data = _make_classification(decline_interview_id="   ")
    model = ConfabulationClassification.model_validate(data)
    assert model.decline_interview_id == "   "


# ── Seed builder additional error-path coverage ───────────────────────────────


def test_seed_builder_empty_source_emits_zero_rows(tmp_path: Path) -> None:
    """Seed builder writes a zero-row seed file (exit 0) when source is empty.

    The source JSONL exists but contains no non-empty lines.  The builder
    succeeds silently with an empty output, which is the correct behavior for
    an empty source but is worth documenting — zero-row seeds are unusual and
    callers should know this path exits 0.
    """
    source_path = tmp_path / "source.jsonl"
    source_path.write_text("", encoding="utf-8")  # empty file
    output_path = tmp_path / "seed.jsonl"

    rc = build_seed(source_path=source_path, output_path=output_path)
    assert rc == 0, f"Expected exit 0 for empty source, got {rc}"
    assert output_path.exists(), "Output file must be created even for empty source"

    seed_lines = [
        ln
        for ln in output_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert len(seed_lines) == 0, (
        f"Expected 0 seed rows for empty source, got {len(seed_lines)}"
    )


def test_seed_builder_invalid_json_in_source_exits_2(tmp_path: Path) -> None:
    """Seed builder exits 2 when the source JSONL contains a malformed line.

    A line that is not valid JSON causes the builder to print an error and
    return exit code 2.  The output file must not be created.
    """
    import json as _json

    source_path = tmp_path / "source.jsonl"
    valid_line = _json.dumps({"decline_interview_id": "id-001"})
    source_path.write_text(f"{valid_line}\nNOT VALID JSON\n", encoding="utf-8")
    output_path = tmp_path / "seed.jsonl"

    rc = build_seed(source_path=source_path, output_path=output_path)
    assert rc == 2, f"Expected exit code 2 for invalid JSON in source, got {rc}"
    assert not output_path.exists(), (
        "Output file must not be created when source contains invalid JSON"
    )
