"""Tests for cdb_analyze.safety_subtype and scripts/build_safety_subtype_seed.py.

All tests are fixture-based (synthetic in-memory rows).  No real API calls.
No access to data/raw/ or data/derived/ production artifacts.

References:
  Architect plan:  docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md §3.1
  CDA SME verdict: docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md
  B11 source:      docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md
  Mirrors:         tests/test_manual_classification.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from cdb_analyze.safety_subtype import (
    SafetyAttributionSubtype,
    load_safety_attribution_subtypes,
)
from pydantic import ValidationError

# ── Load seed builder via importlib (mirrors test_manual_classification.py) ───
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SEED_SCRIPT = _REPO_ROOT / "scripts" / "build_safety_subtype_seed.py"

_spec = importlib.util.spec_from_file_location(
    "build_safety_subtype_seed", _SEED_SCRIPT
)
assert _spec is not None and _spec.loader is not None
_seed_mod = importlib.util.module_from_spec(_spec)
sys.modules["build_safety_subtype_seed"] = _seed_mod
_spec.loader.exec_module(_seed_mod)  # type: ignore[union-attr]

build_seed = _seed_mod.build_seed  # type: ignore[attr-defined]

# ── Valid subtype enum values ─────────────────────────────────────────────────
VALID_SUBTYPE_VALUES = [
    "k_frame",
    "k_vocab_without_k_frame",
]


# ── Fixture builder helpers ───────────────────────────────────────────────────


def _make_subtype(
    *,
    decline_interview_id: str = "safety-id-001",
    safety_attribution_subtype: str = "k_frame",
    subtype_rationale: str = "Framing invoked AI-vs-human-research-subject role assumption.",
    subtype_classifier_id: str = "mark",
) -> dict:  # type: ignore[type-arg]
    """Build a valid subtype dict for use in tests."""
    return {
        "decline_interview_id": decline_interview_id,
        "safety_attribution_subtype": safety_attribution_subtype,
        "subtype_rationale": subtype_rationale,
        "subtype_classifier_id": subtype_classifier_id,
    }


def _make_manual_classification_row(
    *,
    decline_interview_id: str = "safety-id-001",
    manual_classification: str = "safety_event_attribution",
    manual_classification_rationale: str = "The response attributes to safety filter.",
    manual_classifier_id: str = "mark",
    response_verbatim_excerpt: str = "Safety protocols prevented output.",
    detector_flag_v1: bool = True,
) -> dict:  # type: ignore[type-arg]
    """Build a valid manual classification dict for use in tests."""
    return {
        "decline_interview_id": decline_interview_id,
        "manual_classification": manual_classification,
        "manual_classification_rationale": manual_classification_rationale,
        "manual_classifier_id": manual_classifier_id,
        "response_verbatim_excerpt": response_verbatim_excerpt,
        "detector_flag_v1": detector_flag_v1,
    }


def _write_jsonl(path: Path, rows: list) -> None:  # type: ignore[type-arg]
    """Write a list of dicts as JSONL to path."""
    lines = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_parent_jsonl(tmp_path: Path, rows: list) -> Path:  # type: ignore[type-arg]
    """Write a set of manual classification rows to a temp JSONL file."""
    p = tmp_path / "manual_classification.jsonl"
    _write_jsonl(p, rows)
    return p


def _make_subtype_jsonl(tmp_path: Path, rows: list) -> Path:  # type: ignore[type-arg]
    """Write a set of subtype rows to a temp JSONL file."""
    p = tmp_path / "subtype.jsonl"
    _write_jsonl(p, rows)
    return p


# ── 4 parent fixture rows used across multiple tests ─────────────────────────
#
# Row layout:
#   "safety-id-001": safety_event_attribution   (k_frame subtype expected)
#   "safety-id-002": safety_event_attribution   (k_vocab_without_k_frame subtype expected)
#   "other-id-003":  technical_glitch_attribution (non-safety — cannot be subtyped)
#   "other-id-004":  no_prior_context_acknowledgment (non-safety — cannot be subtyped)

_PARENT_ROWS = [
    _make_manual_classification_row(
        decline_interview_id="safety-id-001",
        manual_classification="safety_event_attribution",
    ),
    _make_manual_classification_row(
        decline_interview_id="safety-id-002",
        manual_classification="safety_event_attribution",
        manual_classification_rationale="Uncurated comprehensive list triggered filter.",
    ),
    _make_manual_classification_row(
        decline_interview_id="other-id-003",
        manual_classification="technical_glitch_attribution",
        manual_classification_rationale="Technical glitch, no safety attribution.",
        detector_flag_v1=False,
    ),
    _make_manual_classification_row(
        decline_interview_id="other-id-004",
        manual_classification="no_prior_context_acknowledgment",
        manual_classification_rationale="No prior context reported by model.",
        detector_flag_v1=False,
    ),
]


# ── Pydantic model schema validation tests ────────────────────────────────────


@pytest.mark.parametrize("subtype_value", VALID_SUBTYPE_VALUES)
def test_valid_subtype_each_enum_value(subtype_value: str) -> None:
    """Both k_frame and k_vocab_without_k_frame construct valid model instances."""
    data = _make_subtype(safety_attribution_subtype=subtype_value)
    model = SafetyAttributionSubtype.model_validate(data)
    assert model.safety_attribution_subtype == subtype_value


def test_unclassified_sentinel_rejected_by_pydantic() -> None:
    """The UNCLASSIFIED sentinel is outside the Literal enum and must be rejected by Pydantic."""
    data = _make_subtype(safety_attribution_subtype="UNCLASSIFIED")
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


def test_unknown_subtype_value_rejected_by_pydantic() -> None:
    """An unrecognized subtype value must be rejected by Pydantic."""
    data = _make_subtype(safety_attribution_subtype="not_a_real_subtype")
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


def test_empty_rationale_rejected() -> None:
    """Empty subtype_rationale must raise ValidationError."""
    data = _make_subtype(subtype_rationale="")
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


def test_rationale_at_200_chars_accepted() -> None:
    """Rationale of exactly 200 chars must be accepted."""
    rationale = "A" * 200
    data = _make_subtype(subtype_rationale=rationale)
    model = SafetyAttributionSubtype.model_validate(data)
    assert len(model.subtype_rationale) == 200


def test_rationale_at_201_chars_rejected() -> None:
    """Rationale of 201 chars must be rejected."""
    rationale = "A" * 201
    data = _make_subtype(subtype_rationale=rationale)
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


def test_empty_classifier_id_rejected() -> None:
    """Empty subtype_classifier_id must raise ValidationError."""
    data = _make_subtype(subtype_classifier_id="")
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


def test_empty_decline_interview_id_rejected() -> None:
    """Empty decline_interview_id must raise ValidationError."""
    data = _make_subtype(decline_interview_id="")
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


def test_extra_field_rejected() -> None:
    """Extra fields must be rejected (ConfigDict extra='forbid')."""
    data = _make_subtype()
    data["unexpected_field"] = "surprise"
    with pytest.raises(ValidationError):
        SafetyAttributionSubtype.model_validate(data)


# ── Loader behavior tests — sentinel rejection ────────────────────────────────


def test_loader_rejects_unclassified_sentinel(tmp_path: Path) -> None:
    """Loader must raise ValueError naming the row when UNCLASSIFIED is present.

    The UNCLASSIFIED sentinel is allowed in the seed file only.  The loader
    pre-checks for it before Pydantic validation and raises a descriptive error
    instructing Mark to hand-code the row.
    """
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    sentinel_row = {
        "decline_interview_id": "safety-id-001",
        "safety_attribution_subtype": "UNCLASSIFIED",
        "subtype_rationale": "",
        "subtype_classifier_id": "",
    }
    subtype_path = _make_subtype_jsonl(tmp_path, [sentinel_row])

    with pytest.raises(ValueError, match="UNCLASSIFIED"):
        load_safety_attribution_subtypes(subtype_path, parent_path)


def test_loader_rejects_unclassified_names_the_row(tmp_path: Path) -> None:
    """The UNCLASSIFIED ValueError message names the offending decline_interview_id."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    sentinel_row = {
        "decline_interview_id": "safety-id-002",
        "safety_attribution_subtype": "UNCLASSIFIED",
        "subtype_rationale": "",
        "subtype_classifier_id": "",
    }
    subtype_path = _make_subtype_jsonl(tmp_path, [sentinel_row])

    with pytest.raises(ValueError, match="safety-id-002"):
        load_safety_attribution_subtypes(subtype_path, parent_path)


# ── Loader behavior tests — parent classification join ────────────────────────


def test_loader_rejects_id_not_in_parent(tmp_path: Path) -> None:
    """A subtype row whose decline_interview_id is absent from the parent must raise ValueError."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    ghost_row = _make_subtype(decline_interview_id="ghost-id-999")
    subtype_path = _make_subtype_jsonl(tmp_path, [ghost_row])

    with pytest.raises(ValueError, match="ghost-id-999"):
        load_safety_attribution_subtypes(subtype_path, parent_path)


def test_loader_rejects_non_safety_parent_classification(tmp_path: Path) -> None:
    """A subtype row whose parent classification is not safety_event_attribution must raise.

    This is the 'you cannot subtype a non-safety row' invariant (D17).
    """
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    # other-id-003 is technical_glitch_attribution — should be rejected
    invalid_row = _make_subtype(decline_interview_id="other-id-003")
    subtype_path = _make_subtype_jsonl(tmp_path, [invalid_row])

    with pytest.raises(ValueError, match="other-id-003"):
        load_safety_attribution_subtypes(subtype_path, parent_path)


def test_loader_rejects_non_safety_names_actual_classification(tmp_path: Path) -> None:
    """The non-safety-parent error message names the actual parent classification."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    invalid_row = _make_subtype(decline_interview_id="other-id-004")
    subtype_path = _make_subtype_jsonl(tmp_path, [invalid_row])

    with pytest.raises(ValueError, match="no_prior_context_acknowledgment"):
        load_safety_attribution_subtypes(subtype_path, parent_path)


def test_loader_accepts_valid_safety_row(tmp_path: Path) -> None:
    """A valid subtype row with a safety_event_attribution parent is loaded correctly."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    valid_row = _make_subtype(
        decline_interview_id="safety-id-001",
        safety_attribution_subtype="k_frame",
    )
    subtype_path = _make_subtype_jsonl(tmp_path, [valid_row])

    result = load_safety_attribution_subtypes(subtype_path, parent_path)
    assert len(result) == 1
    assert "safety-id-001" in result
    assert result["safety-id-001"].safety_attribution_subtype == "k_frame"


# ── Loader behavior tests — missing parent artifact file ─────────────────────


def test_loader_raises_on_missing_parent_artifact(tmp_path: Path) -> None:
    """Loader raises FileNotFoundError when parent artifact file does not exist."""
    nonexistent_parent = tmp_path / "does_not_exist.jsonl"

    valid_row = _make_subtype(decline_interview_id="safety-id-001")
    subtype_path = _make_subtype_jsonl(tmp_path, [valid_row])

    with pytest.raises(FileNotFoundError):
        load_safety_attribution_subtypes(subtype_path, nonexistent_parent)


def test_loader_raises_on_missing_subtype_artifact(tmp_path: Path) -> None:
    """Loader raises FileNotFoundError when the subtype artifact file does not exist."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)
    nonexistent_subtype = tmp_path / "does_not_exist_subtype.jsonl"

    with pytest.raises(FileNotFoundError):
        load_safety_attribution_subtypes(nonexistent_subtype, parent_path)


# ── Loader behavior tests — duplicate decline_interview_id ───────────────────


def test_loader_raises_on_duplicate_decline_interview_id(tmp_path: Path) -> None:
    """Loader must raise ValueError naming the duplicate when two rows share an id."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    row_a = _make_subtype(
        decline_interview_id="safety-id-001",
        safety_attribution_subtype="k_frame",
    )
    row_b = _make_subtype(
        decline_interview_id="safety-id-001",
        safety_attribution_subtype="k_vocab_without_k_frame",
    )
    subtype_path = _make_subtype_jsonl(tmp_path, [row_a, row_b])

    with pytest.raises(ValueError, match="safety-id-001"):
        load_safety_attribution_subtypes(subtype_path, parent_path)


# ── Loader behavior tests — round-trip ───────────────────────────────────────


def test_loader_round_trip(tmp_path: Path) -> None:
    """Load 2 valid subtype rows, confirm the returned dict has correct content."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    rows = [
        _make_subtype(
            decline_interview_id="safety-id-001",
            safety_attribution_subtype="k_frame",
            subtype_rationale="Cognitive anthropology framing triggered safety layer.",
        ),
        _make_subtype(
            decline_interview_id="safety-id-002",
            safety_attribution_subtype="k_vocab_without_k_frame",
            subtype_rationale="Uncurated comprehensive list triggered safety filter.",
        ),
    ]
    subtype_path = _make_subtype_jsonl(tmp_path, rows)

    result = load_safety_attribution_subtypes(subtype_path, parent_path)

    assert len(result) == 2
    assert set(result.keys()) == {"safety-id-001", "safety-id-002"}
    assert result["safety-id-001"].safety_attribution_subtype == "k_frame"
    assert result["safety-id-002"].safety_attribution_subtype == "k_vocab_without_k_frame"
    assert result["safety-id-001"].subtype_classifier_id == "mark"


def test_loader_round_trip_re_emit_semantic_equality(tmp_path: Path) -> None:
    """Load then re-emit rows; confirm semantic equality of all fields."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    original = _make_subtype(
        decline_interview_id="safety-id-001",
        safety_attribution_subtype="k_frame",
        subtype_rationale="Framing invoked AI-vs-human-research-subject role.",
        subtype_classifier_id="mark",
    )
    subtype_path = _make_subtype_jsonl(tmp_path, [original])

    result = load_safety_attribution_subtypes(subtype_path, parent_path)
    record = result["safety-id-001"]

    # Re-emit as dict and compare semantically
    re_emitted = record.model_dump()
    assert re_emitted["decline_interview_id"] == original["decline_interview_id"]
    assert re_emitted["safety_attribution_subtype"] == original["safety_attribution_subtype"]
    assert re_emitted["subtype_rationale"] == original["subtype_rationale"]
    assert re_emitted["subtype_classifier_id"] == original["subtype_classifier_id"]


def test_loader_skips_blank_lines(tmp_path: Path) -> None:
    """Blank lines in the JSONL must be skipped without error."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    row = _make_subtype(decline_interview_id="safety-id-001")
    line = json.dumps(row, sort_keys=True, ensure_ascii=False)
    subtype_path = tmp_path / "blanks.jsonl"
    subtype_path.write_text(f"\n{line}\n\n", encoding="utf-8")

    result = load_safety_attribution_subtypes(subtype_path, parent_path)
    assert len(result) == 1
    assert "safety-id-001" in result


def test_loader_empty_file_returns_empty_dict(tmp_path: Path) -> None:
    """Loading an empty JSONL file returns an empty dict."""
    parent_path = _make_parent_jsonl(tmp_path, _PARENT_ROWS)

    subtype_path = tmp_path / "empty.jsonl"
    subtype_path.write_text("", encoding="utf-8")

    result = load_safety_attribution_subtypes(subtype_path, parent_path)
    assert result == {}


# ── No LLM imports test ───────────────────────────────────────────────────────


def test_module_has_no_llm_imports() -> None:
    """safety_subtype.py must not import any LLM client library (CLAUDE.md §6 rule 12)."""
    module_path = (
        _REPO_ROOT
        / "packages"
        / "cdb_analyze"
        / "cdb_analyze"
        / "safety_subtype.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = ["anthropic", "openai", "google.generativeai", "huggingface_hub"]
    for token in forbidden:
        assert token not in content, (
            f"Forbidden LLM import found in safety_subtype.py: {token!r}"
        )


# ── Seed builder tests ────────────────────────────────────────────────────────


def _make_full_parent_rows(
    n_safety: int, n_other: int
) -> list:  # type: ignore[type-arg]
    """Build a mixed set of parent manual classification rows for seed tests."""
    rows = []
    for i in range(n_safety):
        rows.append(
            _make_manual_classification_row(
                decline_interview_id=f"safety-{i:03d}",
                manual_classification="safety_event_attribution",
            )
        )
    for i in range(n_other):
        rows.append(
            _make_manual_classification_row(
                decline_interview_id=f"other-{i:03d}",
                manual_classification="technical_glitch_attribution",
                manual_classification_rationale="Technical glitch.",
                detector_flag_v1=False,
            )
        )
    return rows


def test_seed_builder_emits_only_safety_rows(tmp_path: Path) -> None:
    """Seed builder filters to safety_event_attribution rows only."""
    parent_rows = _make_full_parent_rows(n_safety=3, n_other=2)
    input_path = tmp_path / "mc.jsonl"
    _write_jsonl(input_path, parent_rows)

    output_path = tmp_path / "seed.jsonl"
    rc = build_seed(input_path=input_path, output_path=output_path, force=False)
    assert rc == 0

    seed_lines = [
        ln for ln in output_path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    assert len(seed_lines) == 3, (
        f"Expected 3 seed rows (3 safety of 5 total), got {len(seed_lines)}"
    )


def test_seed_builder_emits_unclassified_sentinel(tmp_path: Path) -> None:
    """Every output row's safety_attribution_subtype must be 'UNCLASSIFIED'."""
    parent_rows = _make_full_parent_rows(n_safety=2, n_other=1)
    input_path = tmp_path / "mc.jsonl"
    _write_jsonl(input_path, parent_rows)

    output_path = tmp_path / "seed.jsonl"
    build_seed(input_path=input_path, output_path=output_path, force=False)

    for line in output_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        assert row["safety_attribution_subtype"] == "UNCLASSIFIED", (
            f"Expected UNCLASSIFIED but got "
            f"{row['safety_attribution_subtype']!r} for "
            f"{row['decline_interview_id']!r}"
        )


def test_seed_builder_emits_empty_rationale_and_classifier(tmp_path: Path) -> None:
    """Seed rows must have empty subtype_rationale and subtype_classifier_id."""
    parent_rows = _make_full_parent_rows(n_safety=1, n_other=0)
    input_path = tmp_path / "mc.jsonl"
    _write_jsonl(input_path, parent_rows)

    output_path = tmp_path / "seed.jsonl"
    build_seed(input_path=input_path, output_path=output_path, force=False)

    seed_lines = [
        ln for ln in output_path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    row = json.loads(seed_lines[0])
    assert row["subtype_rationale"] == ""
    assert row["subtype_classifier_id"] == ""


def test_seed_builder_sorted_by_decline_interview_id(tmp_path: Path) -> None:
    """Seed builder sorts output rows by decline_interview_id for determinism."""
    # Deliberately insert rows in reverse alphabetical order in the source
    parent_rows = [
        _make_manual_classification_row(
            decline_interview_id="zzz-id",
            manual_classification="safety_event_attribution",
        ),
        _make_manual_classification_row(
            decline_interview_id="aaa-id",
            manual_classification="safety_event_attribution",
        ),
        _make_manual_classification_row(
            decline_interview_id="mmm-id",
            manual_classification="safety_event_attribution",
        ),
    ]
    input_path = tmp_path / "mc.jsonl"
    _write_jsonl(input_path, parent_rows)

    output_path = tmp_path / "seed.jsonl"
    build_seed(input_path=input_path, output_path=output_path, force=False)

    seed_lines = [
        ln for ln in output_path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    emitted_ids = [json.loads(ln)["decline_interview_id"] for ln in seed_lines]
    assert emitted_ids == sorted(emitted_ids), (
        f"Seed rows are not sorted by decline_interview_id: {emitted_ids}"
    )


def test_seed_builder_deterministic(tmp_path: Path) -> None:
    """Running the seed builder twice on the same input produces byte-identical output."""
    parent_rows = _make_full_parent_rows(n_safety=3, n_other=2)
    input_path = tmp_path / "mc.jsonl"
    _write_jsonl(input_path, parent_rows)

    out1 = tmp_path / "seed1.jsonl"
    out2 = tmp_path / "seed2.jsonl"

    build_seed(input_path=input_path, output_path=out1, force=False)
    build_seed(input_path=input_path, output_path=out2, force=False)

    content1 = out1.read_bytes()
    content2 = out2.read_bytes()
    assert content1 == content2, "Seed builder output is not byte-identical on repeat runs"


def test_seed_builder_idempotency_guard(tmp_path: Path) -> None:
    """Pre-existing partially-filled output causes non-zero exit; --force overrides."""
    parent_rows = _make_full_parent_rows(n_safety=1, n_other=0)
    input_path = tmp_path / "mc.jsonl"
    _write_jsonl(input_path, parent_rows)

    output_path = tmp_path / "seed.jsonl"

    # First run — writes the seed file
    rc = build_seed(input_path=input_path, output_path=output_path, force=False)
    assert rc == 0

    # Simulate Mark partially filling the file
    partial_content = json.dumps(
        {
            "decline_interview_id": "safety-000",
            "safety_attribution_subtype": "k_frame",
            "subtype_rationale": "Cognitive anthropology framing was the trigger.",
            "subtype_classifier_id": "mark",
        },
        sort_keys=True,
        ensure_ascii=False,
    ) + "\n"
    output_path.write_text(partial_content, encoding="utf-8")

    # Second run without --force — must return non-zero
    rc2 = build_seed(input_path=input_path, output_path=output_path, force=False)
    assert rc2 != 0, (
        "Expected non-zero exit when existing file differs and --force not set"
    )

    # The file should still contain Mark's partial content (not overwritten)
    assert output_path.read_text(encoding="utf-8") == partial_content

    # Third run with --force — must succeed and overwrite with seed
    rc3 = build_seed(input_path=input_path, output_path=output_path, force=True)
    assert rc3 == 0

    # File is now back to the seed content (UNCLASSIFIED)
    seed_row = json.loads(output_path.read_text(encoding="utf-8").splitlines()[0])
    assert seed_row["safety_attribution_subtype"] == "UNCLASSIFIED"


def test_seed_builder_module_importable_without_dotenv() -> None:
    """The seed builder module is importable even when .env is absent.

    build_safety_subtype_seed.py has no external imports at module scope
    (unlike build_manual_classification_seed.py which loads the v1 detector
    via importlib).  Asserting build_seed is callable is sufficient to confirm
    the import-time side effects did not raise.
    """
    assert callable(build_seed), (
        "build_seed is not callable — seed builder module failed to import cleanly"
    )
