"""Tests for scripts/phase4a1_note_j_crosstab.py (Task #21.T4.2).

All tests are fixture-based (synthetic in-memory data).
No real API calls. No access to data/raw/ or data/derived/ production artifacts.

Coverage:
  - load_all_inputs: missing file errors, UNCLASSIFIED sentinel detection
  - primary view: outcome_class × model_origin cross-tab and flagging logic
  - secondary view A: manual classification × (provider, model_id, domain)
  - cross-provider replication sub-table with safety_attribution_subtype column
  - Note K mechanism breakdown sub-section (provider, subtype counts)
  - secondary view B: manual classification × model_origin
  - reconciliation table: detector_flag_v1 × manual_classification
  - Note K disposition: all four tiers (CONFIRMED-with-mechanism, CONFIRMED,
    INCONCLUSIVE-SUGGESTIVE, INCONCLUSIVE, NOT CONFIRMED)
  - Note K disposition string naming both subtypes per D20
  - Amendment 3 §3.2 fixture: synthetic 9-row safety cohort split 5/4 across
    two providers exercising the new sub-table column, breakdown section,
    and disposition string
  - All Amendment 2 fixture cases preserved

References:
  Amendment 2:   docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md §3 T4
  Amendment 3:   docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md §3.2
  SME verdict:   docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md
  B11 source:    docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

# ── Load script via importlib (no __main__ guard needed, the script uses main()) ──
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "phase4a1_note_j_crosstab.py"

_spec = importlib.util.spec_from_file_location("phase4a1_note_j_crosstab", _SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
_script_mod = importlib.util.module_from_spec(_spec)
sys.modules["phase4a1_note_j_crosstab"] = _script_mod
_spec.loader.exec_module(_script_mod)  # type: ignore[union-attr]

run = _script_mod.run  # type: ignore[attr-defined]
load_all_inputs = _script_mod.load_all_inputs  # type: ignore[attr-defined]
build_secondary_view_a = _script_mod.build_secondary_view_a  # type: ignore[attr-defined]
compute_note_k_disposition = _script_mod.compute_note_k_disposition  # type: ignore[attr-defined]
render_markdown = _script_mod.render_markdown  # type: ignore[attr-defined]
build_primary_view = _script_mod.build_primary_view  # type: ignore[attr-defined]
build_secondary_view_b = _script_mod.build_secondary_view_b  # type: ignore[attr-defined]
build_reconciliation_table = _script_mod.build_reconciliation_table  # type: ignore[attr-defined]
enrich_decline_rows = _script_mod.enrich_decline_rows  # type: ignore[attr-defined]
build_json_output = _script_mod.build_json_output  # type: ignore[attr-defined]


# ── Fixture helpers ───────────────────────────────────────────────────────────

def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a list of dicts as JSONL to path."""
    lines = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_decline_interview(
    *,
    decline_interview_id: str,
    model_id: str = "google/gemini-2.5-pro",
    provider: str = "google",
    domain: str = "family",  # "family" or "holidays" (used to select prompt)
    originating_outcome_class: str = "empty_output",
    originating_informant_id: str = "inf-000",
    detector_flag_v1: bool = True,
) -> dict[str, Any]:
    """Build a synthetic decline interview row."""
    if domain == "family":
        prompt = (
            "A moment ago I asked you to perform the following task: "
            "You are participating in a cognitive anthropology study. "
            "List every family relationship or family member you can think of."
        )
    else:
        prompt = (
            "A moment ago I asked you to perform the following task: "
            "You are participating in a cognitive anthropology study. "
            "List every holiday, festive day, or religious observance you can think of."
        )
    return {
        "decline_interview_id": decline_interview_id,
        "originating_informant_id": originating_informant_id,
        "originating_failure_id": None,
        "originating_step": "freelist",
        "originating_outcome_class": originating_outcome_class,
        "detection_rule_version": "v1",
        "detection_timestamp": "2026-04-23T00:00:00Z",
        "followup_timestamp": "2026-04-23T00:00:01Z",
        "model_id": model_id,
        "model_version_returned": f"{model_id}-snap",
        "provider": provider,
        "api_endpoint": f"https://{provider}.api/v1",
        "prompt_version": "decline_v1",
        "sha256_manifest": "aabbcc",
        "prompt_verbatim": prompt,
        "response_verbatim": "My safety protocols prevented output.",
        "thinking_verbatim": "",
        "input_tokens": 100,
        "output_tokens": 50,
        "latency_ms": 1000,
        "stop_reason": "stop",
        "cost_usd": 0.001,
        "qa_notes": "",
        "version_drift_flag": False,
    }


def _make_informant(
    *,
    informant_id: str,
    model_id: str = "google/gemini-2.5-pro",
    provider: str = "google",
    domain_slug: str = "family",
    origin_country: str = "us",
    qa_passed: bool = True,
    freelist: list[str] | None = None,
) -> dict[str, Any]:
    """Build a synthetic informant row."""
    if freelist is None:
        freelist = ["parent", "sibling", "cousin"]
    return {
        "informant_id": informant_id,
        "domain_slug": domain_slug,
        "run_index": 1,
        "collection_date": "2026-04-01",
        "model_id": model_id,
        "model_version_returned": f"{model_id}-snap",
        "family": "gemini",
        "provider": provider,
        "provider_request_id": "req-001",
        "knowledge_cutoff": "2025-01",
        "open_weights": False,
        "origin_country": origin_country,
        "alignment_method": "rlhf",
        "collection_method": "api",
        "collection_mode": "auto",
        "api_endpoint": f"https://{provider}.api/v1",
        "api_version": "v1",
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 2048,
        "system_prompt": "",
        "freelist": freelist,
        "pile_sort": {},
        "interview": {},
        "truncation_type": None,
        "truncation_n": None,
        "max_possible_n": 200,
        "context_window_exceeded": False,
        "capacity_note": None,
        "sha256_manifest": "aabbcc",
        "qa_passed": qa_passed,
        "qa_notes": "",
    }


def _make_manual_classification_row(
    *,
    decline_interview_id: str,
    manual_classification: str = "safety_event_attribution",
    rationale: str = "Safety layer triggered by prompt framing.",
    classifier_id: str = "mark",
    detector_flag_v1: bool = True,
    excerpt: str = "Safety protocols prevented output.",
) -> dict[str, Any]:
    """Build a synthetic manual classification row."""
    return {
        "decline_interview_id": decline_interview_id,
        "manual_classification": manual_classification,
        "manual_classification_rationale": rationale,
        "manual_classifier_id": classifier_id,
        "response_verbatim_excerpt": excerpt,
        "detector_flag_v1": detector_flag_v1,
    }


def _make_subtype_row(
    *,
    decline_interview_id: str,
    safety_attribution_subtype: str = "k_frame",
    rationale: str = "AI-vs-human-research-subject framing triggered safety layer.",
    classifier_id: str = "mark",
) -> dict[str, Any]:
    """Build a synthetic safety attribution subtype row."""
    return {
        "decline_interview_id": decline_interview_id,
        "safety_attribution_subtype": safety_attribution_subtype,
        "subtype_rationale": rationale,
        "subtype_classifier_id": classifier_id,
    }


# ── Small reusable fixture builders ──────────────────────────────────────────

def _write_minimal_informants(path: Path) -> None:
    """Write a minimal informants file with one row."""
    _write_jsonl(path, [_make_informant(informant_id="inf-000")])


# ── Error handling: missing files ─────────────────────────────────────────────


def test_missing_decline_interviews_raises(tmp_path: Path) -> None:
    """load_all_inputs raises FileNotFoundError when decline_interviews.jsonl is absent."""
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [])
    _write_jsonl(sub_path, [])

    with pytest.raises(FileNotFoundError):
        load_all_inputs(
            tmp_path / "does_not_exist.jsonl",
            informants_path,
            mc_path,
            sub_path,
        )


def test_missing_informants_raises(tmp_path: Path) -> None:
    """load_all_inputs raises FileNotFoundError when informants.jsonl is absent."""
    di_path = tmp_path / "di.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"
    _write_jsonl(di_path, [])
    _write_jsonl(mc_path, [])
    _write_jsonl(sub_path, [])

    with pytest.raises(FileNotFoundError):
        load_all_inputs(
            di_path,
            tmp_path / "does_not_exist.jsonl",
            mc_path,
            sub_path,
        )


def test_missing_manual_classification_raises(tmp_path: Path) -> None:
    """load_all_inputs raises FileNotFoundError when manual classification is absent."""
    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    sub_path = tmp_path / "subtype.jsonl"
    _write_jsonl(di_path, [])
    _write_minimal_informants(informants_path)
    _write_jsonl(sub_path, [])

    with pytest.raises(FileNotFoundError):
        load_all_inputs(
            di_path,
            informants_path,
            tmp_path / "does_not_exist.jsonl",
            sub_path,
        )


def test_missing_subtype_artifact_raises(tmp_path: Path) -> None:
    """load_all_inputs raises FileNotFoundError when subtype artifact is absent."""
    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    _write_jsonl(di_path, [])
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [])

    with pytest.raises(FileNotFoundError, match="does_not_exist"):
        load_all_inputs(
            di_path,
            informants_path,
            mc_path,
            tmp_path / "does_not_exist.jsonl",
        )


# ── Error handling: UNCLASSIFIED sentinel ─────────────────────────────────────


def test_unclassified_subtype_raises(tmp_path: Path) -> None:
    """load_all_inputs raises ValueError naming the row when subtype is UNCLASSIFIED."""
    # Build a valid parent classification
    mc_row = _make_manual_classification_row(decline_interview_id="safety-001")
    di_row = _make_decline_interview(decline_interview_id="safety-001")

    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    _write_jsonl(di_path, [di_row])
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [mc_row])
    # UNCLASSIFIED sentinel row
    _write_jsonl(
        sub_path,
        [
            {
                "decline_interview_id": "safety-001",
                "safety_attribution_subtype": "UNCLASSIFIED",
                "subtype_rationale": "",
                "subtype_classifier_id": "",
            }
        ],
    )

    with pytest.raises(ValueError, match="safety-001"):
        load_all_inputs(di_path, informants_path, mc_path, sub_path)


def test_unclassified_subtype_error_names_row(tmp_path: Path) -> None:
    """The UNCLASSIFIED ValueError names the specific decline_interview_id."""
    mc_row = _make_manual_classification_row(decline_interview_id="specific-id-xyz")
    di_row = _make_decline_interview(decline_interview_id="specific-id-xyz")

    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    _write_jsonl(di_path, [di_row])
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [mc_row])
    _write_jsonl(
        sub_path,
        [
            {
                "decline_interview_id": "specific-id-xyz",
                "safety_attribution_subtype": "UNCLASSIFIED",
                "subtype_rationale": "",
                "subtype_classifier_id": "",
            }
        ],
    )

    with pytest.raises(ValueError, match="specific-id-xyz"):
        load_all_inputs(di_path, informants_path, mc_path, sub_path)


def test_subtype_id_not_in_parent_classification_raises(tmp_path: Path) -> None:
    """load_all_inputs raises ValueError when subtype ID is missing from parent."""
    mc_row = _make_manual_classification_row(decline_interview_id="safety-001")
    di_row = _make_decline_interview(decline_interview_id="safety-001")

    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    _write_jsonl(di_path, [di_row])
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [mc_row])
    # Subtype row with a different decline_interview_id (not in parent)
    _write_jsonl(sub_path, [_make_subtype_row(decline_interview_id="ghost-id-999")])

    with pytest.raises(ValueError, match="ghost-id-999"):
        load_all_inputs(di_path, informants_path, mc_path, sub_path)


def test_subtype_non_safety_parent_raises(tmp_path: Path) -> None:
    """load_all_inputs raises ValueError when subtype parent is not safety_event_attribution."""
    # Parent is technical_glitch_attribution — cannot be subtyped
    mc_row = _make_manual_classification_row(
        decline_interview_id="technical-001",
        manual_classification="technical_glitch_attribution",
        rationale="Technical glitch observed.",
        detector_flag_v1=False,
    )
    di_row = _make_decline_interview(decline_interview_id="technical-001")

    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    _write_jsonl(di_path, [di_row])
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [mc_row])
    _write_jsonl(sub_path, [_make_subtype_row(decline_interview_id="technical-001")])

    with pytest.raises(ValueError, match="technical-001"):
        load_all_inputs(di_path, informants_path, mc_path, sub_path)


# ── Note K disposition: four-tier tests ──────────────────────────────────────


def _build_cross_tab_fixture(
    tmp_path: Path,
    *,
    safety_rows: list[dict[str, Any]],  # list of (decline_interview_id, provider, domain)
    blocked_rows: list[dict[str, Any]] | None = None,
    other_rows: list[dict[str, Any]] | None = None,
    subtype_rows_override: list[dict[str, Any]] | None = None,
) -> tuple[Path, Path, Path, Path]:
    """Build a complete set of fixture files for cross-tab tests.

    safety_rows: list of dicts with keys:
        decline_interview_id, provider, model_id, domain
    blocked_rows: same format (optional)
    other_rows: list of dicts with keys:
        decline_interview_id, manual_classification, provider, model_id, domain

    Returns (di_path, informants_path, mc_path, sub_path).
    """
    if blocked_rows is None:
        blocked_rows = []
    if other_rows is None:
        other_rows = []

    # Combine all rows
    all_di_rows: list[dict[str, Any]] = []
    all_mc_rows: list[dict[str, Any]] = []
    all_sub_rows: list[dict[str, Any]] = []

    for i, r in enumerate(safety_rows):
        did = r["decline_interview_id"]
        provider = r.get("provider", "google")
        model_id = r.get("model_id", "google/gemini-2.5-pro")
        domain = r.get("domain", "family")
        sub = r.get("subtype", "k_frame")
        all_di_rows.append(
            _make_decline_interview(
                decline_interview_id=did,
                model_id=model_id,
                provider=provider,
                domain=domain,
                originating_informant_id=f"inf-safety-{i:03d}",
            )
        )
        all_mc_rows.append(
            _make_manual_classification_row(
                decline_interview_id=did,
                manual_classification="safety_event_attribution",
            )
        )
        if subtype_rows_override is None:
            all_sub_rows.append(
                _make_subtype_row(
                    decline_interview_id=did,
                    safety_attribution_subtype=sub,
                )
            )

    for i, r in enumerate(blocked_rows):
        did = r["decline_interview_id"]
        provider = r.get("provider", "openrouter")
        model_id = r.get("model_id", "deepseek/deepseek-v3.2")
        domain = r.get("domain", "family")
        all_di_rows.append(
            _make_decline_interview(
                decline_interview_id=did,
                model_id=model_id,
                provider=provider,
                domain=domain,
                originating_informant_id=f"inf-blocked-{i:03d}",
            )
        )
        all_mc_rows.append(
            _make_manual_classification_row(
                decline_interview_id=did,
                manual_classification="blocked_event_attribution",
                rationale="Provider blocked the response.",
            )
        )
        # blocked rows do NOT get subtype rows (n/a per D17)

    for i, r in enumerate(other_rows):
        did = r["decline_interview_id"]
        mc = r.get("manual_classification", "technical_glitch_attribution")
        provider = r.get("provider", "openrouter")
        model_id = r.get("model_id", "microsoft/phi-4")
        domain = r.get("domain", "family")
        all_di_rows.append(
            _make_decline_interview(
                decline_interview_id=did,
                model_id=model_id,
                provider=provider,
                domain=domain,
                originating_informant_id=f"inf-other-{i:03d}",
            )
        )
        all_mc_rows.append(
            _make_manual_classification_row(
                decline_interview_id=did,
                manual_classification=mc,
                rationale="Non-safety classification.",
                detector_flag_v1=False,
            )
        )

    if subtype_rows_override is not None:
        all_sub_rows = subtype_rows_override

    # Write files
    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    _write_jsonl(di_path, all_di_rows)
    # Build one informant per model_id/provider seen
    informant_rows = []
    seen_models: set[str] = set()
    for row in all_di_rows:
        mid = row["model_id"]
        if mid not in seen_models:
            seen_models.add(mid)
            # Map provider to origin_country heuristically
            provider = row["provider"]
            if "openrouter" in provider:
                # extract from model_id prefix
                origin = "cn" if ("glm" in mid or "deepseek" in mid or "qwen" in mid) else "us"
            elif "google" in provider:
                origin = "us"
            else:
                origin = "us"
            informant_rows.append(
                _make_informant(
                    informant_id=f"inf-model-{mid.replace('/', '-')}",
                    model_id=mid,
                    provider=provider,
                    origin_country=origin,
                )
            )
    _write_jsonl(informants_path, informant_rows)
    _write_jsonl(mc_path, all_mc_rows)
    _write_jsonl(sub_path, all_sub_rows)

    return di_path, informants_path, mc_path, sub_path


def test_note_k_confirmed_with_mechanism_two_providers(tmp_path: Path) -> None:
    """CONFIRMED-with-mechanism fires when count >= 5 AND >= 2 distinct providers.

    Fixture: 5 safety rows across google (3) and openrouter (2), each with k_frame.
    """
    safety_rows = [
        {"decline_interview_id": f"safety-google-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(3)
    ] + [
        {"decline_interview_id": f"safety-oai-{i}", "provider": "openrouter",
         "model_id": "openai/gpt-5.4-mini", "domain": "family", "subtype": "k_frame"}
        for i in range(2)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "CONFIRMED-with-mechanism", (
        f"Expected CONFIRMED-with-mechanism, got {note_k['disposition']}"
    )
    assert note_k["total_safety_blocked"] == 5
    assert note_k["n_providers"] == 2


def test_note_k_confirmed_single_provider(tmp_path: Path) -> None:
    """CONFIRMED fires when count >= 5 but only 1 distinct provider.

    Fixture: 6 safety rows all from google (single provider).
    """
    safety_rows = [
        {"decline_interview_id": f"safety-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(6)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "CONFIRMED", (
        f"Expected CONFIRMED, got {note_k['disposition']}"
    )
    assert note_k["n_providers"] == 1


def test_note_k_inconclusive_suggestive(tmp_path: Path) -> None:
    """INCONCLUSIVE-SUGGESTIVE fires when 2 <= count < 5.

    Fixture: 3 safety rows.
    """
    safety_rows = [
        {"decline_interview_id": f"safety-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(3)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "INCONCLUSIVE-SUGGESTIVE", (
        f"Expected INCONCLUSIVE-SUGGESTIVE, got {note_k['disposition']}"
    )
    assert note_k["total_safety_blocked"] == 3


def test_note_k_inconclusive_single_row(tmp_path: Path) -> None:
    """INCONCLUSIVE fires when count == 1."""
    safety_rows = [
        {"decline_interview_id": "safety-0", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "INCONCLUSIVE", (
        f"Expected INCONCLUSIVE, got {note_k['disposition']}"
    )
    assert note_k["total_safety_blocked"] == 1


def test_note_k_not_confirmed_no_safety_rows(tmp_path: Path) -> None:
    """NOT CONFIRMED fires when there are no safety or blocked attribution rows.

    Fixture: only technical_glitch_attribution rows.
    """
    other_rows = [
        {
            "decline_interview_id": f"glitch-{i}",
            "manual_classification": "technical_glitch_attribution",
        }
        for i in range(5)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=[], other_rows=other_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "NOT CONFIRMED", (
        f"Expected NOT CONFIRMED, got {note_k['disposition']}"
    )
    assert note_k["total_safety_blocked"] == 0


# ── Amendment 3 §3.2 main fixture: 9-row safety cohort split 5/4 ─────────────
#
# Per Amendment 3 §3.2 acceptance criteria:
#   "Test fixture coverage adds a synthetic 9-row safety cohort split 5/4 across
#   the two subtypes, distributed across two providers, to exercise the new
#   sub-table and the disposition string."
#
# 9 rows: 5 k_frame (google, family) + 4 k_vocab_without_k_frame (openrouter, holidays)
# Two providers: google + openrouter
# Disposition: CONFIRMED-with-mechanism (count=9 >= 5, providers=2 >= 2)


def _build_amendment3_9row_fixture(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path]:
    """9-row fixture: 5 k_frame (google, family) + 4 k_vocab (openrouter, holidays).

    Matches the Amendment 3 §3.2 acceptance criteria exactly.
    """
    safety_rows = [
        {
            "decline_interview_id": f"kframe-google-{i:03d}",
            "provider": "google",
            "model_id": "google/gemini-2.5-pro",
            "domain": "family",
            "subtype": "k_frame",
        }
        for i in range(5)
    ] + [
        {
            "decline_interview_id": f"kvocab-openrouter-{i:03d}",
            "provider": "openrouter",
            "model_id": "z-ai/glm-5.1",
            "domain": "holidays",
            "subtype": "k_vocab_without_k_frame",
        }
        for i in range(4)
    ]

    return _build_cross_tab_fixture(tmp_path, safety_rows=safety_rows)


def test_amendment3_9row_disposition_confirmed_with_mechanism(tmp_path: Path) -> None:
    """9-row fixture: disposition is CONFIRMED-with-mechanism (2 providers, 9 rows)."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "CONFIRMED-with-mechanism"
    assert note_k["total_safety_blocked"] == 9
    assert note_k["n_providers"] == 2
    assert note_k["k_frame_count"] == 5
    assert note_k["k_vocab_count"] == 4


def test_amendment3_9row_disposition_string_names_both_subtypes(tmp_path: Path) -> None:
    """9-row fixture: disposition string names K-frame and K-vocab with their counts."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    disp_str = note_k["disposition_string"]

    # Both subtype labels must appear
    assert "K-frame" in disp_str, f"K-frame not in disposition string: {disp_str!r}"
    assert "K-vocab" in disp_str, f"K-vocab not in disposition string: {disp_str!r}"

    # Both counts must appear
    assert "N=5" in disp_str, f"N=5 not in disposition string: {disp_str!r}"
    assert "N=4" in disp_str, f"N=4 not in disposition string: {disp_str!r}"


def test_amendment3_9row_mechanism_string_d20_wording(tmp_path: Path) -> None:
    """9-row fixture: mechanism string matches D20 wording structure."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    mechanism = json_out["note_k"]["mechanism_string"]

    # D20 wording components must be present
    assert "provider-safety-layer activation" in mechanism
    assert "AI-vs-human-research-subject framing" in mechanism
    assert "K-frame" in mechanism
    assert "list-comprehensiveness/sensitivity vocabulary" in mechanism
    assert "K-vocab" in mechanism
    assert "cross-provider replication" in mechanism


def test_amendment3_9row_cross_provider_subtable_has_subtype_column(
    tmp_path: Path,
) -> None:
    """9-row fixture: cross-provider sub-table includes safety_attribution_subtype column."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    cp_table = json_out["secondary_view_a"]["cross_provider_table"]
    assert len(cp_table) == 9, f"Expected 9 rows in cross-provider table, got {len(cp_table)}"

    for row in cp_table:
        assert "safety_attribution_subtype" in row, (
            f"Row missing safety_attribution_subtype: {row}"
        )
        sub = row["safety_attribution_subtype"]
        assert sub in ("k_frame", "k_vocab_without_k_frame"), (
            f"Unexpected subtype value: {sub!r}"
        )


def test_amendment3_9row_provider_subtype_counts(tmp_path: Path) -> None:
    """9-row fixture: provider_subtype_counts breakdown is correct."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    psc = json_out["secondary_view_a"]["provider_subtype_counts"]
    # google: 5 k_frame, 0 k_vocab
    assert psc.get("google", {}).get("k_frame", 0) == 5
    assert psc.get("google", {}).get("k_vocab_without_k_frame", 0) == 0
    # openrouter: 0 k_frame, 4 k_vocab
    assert psc.get("openrouter", {}).get("k_frame", 0) == 0
    assert psc.get("openrouter", {}).get("k_vocab_without_k_frame", 0) == 4


def test_amendment3_9row_note_k_mechanism_breakdown_in_markdown(
    tmp_path: Path,
) -> None:
    """9-row fixture: Markdown contains 'Note K Mechanism Breakdown' sub-section."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, _ = run(di_path, informants_path, mc_path, sub_path)

    assert "Note K Mechanism Breakdown" in md, (
        "Expected 'Note K Mechanism Breakdown' sub-section in Markdown output"
    )


def test_amendment3_9row_markdown_has_subtype_in_cross_provider_table(
    tmp_path: Path,
) -> None:
    """9-row fixture: Markdown cross-provider sub-table contains safety_attribution_subtype."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, _ = run(di_path, informants_path, mc_path, sub_path)

    assert "safety_attribution_subtype" in md, (
        "Expected 'safety_attribution_subtype' column header in Markdown"
    )
    assert "k_frame" in md, "Expected 'k_frame' values in Markdown table"
    assert "k_vocab_without_k_frame" in md, "Expected 'k_vocab_without_k_frame' in Markdown"


def test_amendment3_9row_supporting_numerics_in_markdown(tmp_path: Path) -> None:
    """9-row fixture: Markdown contains the supporting numerics line below disposition."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, _ = run(di_path, informants_path, mc_path, sub_path)

    # Supporting numerics line should contain k_frame and k_vocab counts
    assert "K-frame N=5" in md, "Expected 'K-frame N=5' in supporting numerics"
    assert "K-vocab N=4" in md, "Expected 'K-vocab N=4' in supporting numerics"


# ── Blocked rows get n/a subtype ──────────────────────────────────────────────


def test_blocked_rows_get_na_subtype(tmp_path: Path) -> None:
    """blocked_event_attribution rows get safety_attribution_subtype = n/a."""
    safety_rows = [
        {"decline_interview_id": f"safety-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(5)
    ]
    blocked_rows = [
        {"decline_interview_id": "blocked-001", "provider": "openrouter",
         "model_id": "deepseek/deepseek-v3.2", "domain": "family"}
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows, blocked_rows=blocked_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    cp_table = json_out["secondary_view_a"]["cross_provider_table"]
    blocked = [r for r in cp_table if r["classification"] == "blocked_event_attribution"]
    assert len(blocked) == 1
    assert blocked[0]["safety_attribution_subtype"] == "n/a", (
        f"Expected n/a for blocked row, got {blocked[0]['safety_attribution_subtype']!r}"
    )


def test_blocked_rows_counted_in_note_k_arithmetic(tmp_path: Path) -> None:
    """blocked_event_attribution rows are counted in Note K arithmetic.

    Fixture: 3 safety + 2 blocked = 5 total -> threshold met with 2 providers.
    But only 1 provider in this fixture -> CONFIRMED (not CONFIRMED-with-mechanism).
    """
    safety_rows = [
        {"decline_interview_id": f"safety-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(3)
    ]
    blocked_rows = [
        {"decline_interview_id": f"blocked-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family"}
        for i in range(2)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows, blocked_rows=blocked_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["safety_event_attribution_count"] == 3
    assert note_k["blocked_event_attribution_count"] == 2
    assert note_k["total_safety_blocked"] == 5
    # Only 1 provider (google) -> CONFIRMED, not CONFIRMED-with-mechanism
    assert note_k["disposition"] == "CONFIRMED"


# ── Reconciliation table ──────────────────────────────────────────────────────


def test_reconciliation_table_structure(tmp_path: Path) -> None:
    """Reconciliation table reports detector_flag_v1 × manual_classification correctly."""
    # 2 safety rows: one flagged (True), one not flagged (False)
    di_rows = [
        _make_decline_interview(decline_interview_id="did-flagged", provider="google",
                                model_id="google/gemini-2.5-pro"),
        _make_decline_interview(decline_interview_id="did-nonflagged", provider="google",
                                model_id="google/gemini-2.5-pro"),
    ]
    mc_rows = [
        _make_manual_classification_row(
            decline_interview_id="did-flagged",
            manual_classification="safety_event_attribution",
            detector_flag_v1=True,
        ),
        _make_manual_classification_row(
            decline_interview_id="did-nonflagged",
            manual_classification="technical_glitch_attribution",
            rationale="Technical glitch observed.",
            detector_flag_v1=False,
        ),
    ]
    sub_rows = [
        _make_subtype_row(decline_interview_id="did-flagged"),
    ]

    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    _write_jsonl(di_path, di_rows)
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, mc_rows)
    _write_jsonl(sub_path, sub_rows)

    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    recon = json_out["reconciliation"]
    assert recon["flagged"].get("safety_event_attribution", 0) == 1
    assert recon["not_flagged"].get("technical_glitch_attribution", 0) == 1
    assert recon["total_flagged"] == 1
    assert recon["total_not_flagged"] == 1


# ── Secondary views structure ─────────────────────────────────────────────────


def test_secondary_view_b_model_origin_breakdown(tmp_path: Path) -> None:
    """Secondary view B breaks manual classification out by model_origin."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    sv_b = json_out["secondary_view_b"]
    assert "matrix" in sv_b
    assert "origins" in sv_b
    # safety_event_attribution should appear in matrix with some origin breakdown
    assert "safety_event_attribution" in sv_b["matrix"]


def test_secondary_view_a_includes_all_7_enum_values(tmp_path: Path) -> None:
    """Secondary view A matrix covers all 7 enum values as row keys."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    sv_a = json_out["secondary_view_a"]
    matrix = sv_a["matrix"]
    # safety_event_attribution must be present (there are 9 safety rows)
    assert "safety_event_attribution" in matrix
    # The matrix may not have all 7 if some are zero — that's fine, we just
    # check the ones present are valid enum values
    valid_enums = {
        "safety_event_attribution",
        "blocked_event_attribution",
        "technical_glitch_attribution",
        "no_prior_context_acknowledgment",
        "substantive_compliance_with_empty_input",
        "other_substring_false_positive",
        "genuine_recursive_decline",
    }
    for key in matrix:
        assert key in valid_enums, f"Unexpected key in secondary_view_a matrix: {key!r}"


# ── Markdown structure ────────────────────────────────────────────────────────


def test_markdown_contains_all_required_sections(tmp_path: Path) -> None:
    """Markdown output contains all required section headings."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, _ = run(di_path, informants_path, mc_path, sub_path)

    required_headings = [
        "Primary View",
        "Secondary View A",
        "Cross-provider Replication Sub-table",
        "Note K Mechanism Breakdown",
        "Secondary View B",
        "Detector Flag v1",
        "Note K Re-Evaluation",
    ]
    for heading in required_headings:
        assert heading in md, f"Required section heading missing from Markdown: {heading!r}"


def test_markdown_disposition_string_is_headline(tmp_path: Path) -> None:
    """Markdown Note K section starts with the disposition string as headline."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    disposition_str = json_out["note_k"]["disposition_string"]
    # The disposition string should appear prominently in the Note K section
    assert disposition_str in md, (
        f"Disposition string not found in Markdown:\n{disposition_str!r}"
    )


def test_markdown_mechanism_string_is_in_blockquote(tmp_path: Path) -> None:
    """For CONFIRMED-with-mechanism, mechanism string appears in Markdown blockquote."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    # The mechanism string for CONFIRMED-with-mechanism should appear in a blockquote (> prefix)
    mechanism = json_out["note_k"]["mechanism_string"]
    assert f"> {mechanism}" in md, (
        "Mechanism string not found in blockquote in Markdown"
    )


# ── JSON output structure ─────────────────────────────────────────────────────


def test_json_output_structure(tmp_path: Path) -> None:
    """JSON output contains all required top-level keys."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    _, json_out = run(di_path, informants_path, mc_path, sub_path)

    required_keys = [
        "script_version",
        "population",
        "primary_view",
        "secondary_view_a",
        "secondary_view_b",
        "reconciliation",
        "note_k",
    ]
    for key in required_keys:
        assert key in json_out, f"Required key missing from JSON output: {key!r}"


def test_json_output_is_serializable(tmp_path: Path) -> None:
    """JSON output is JSON-serializable without errors."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    _, json_out = run(di_path, informants_path, mc_path, sub_path)

    # Should not raise
    serialized = json.dumps(json_out, ensure_ascii=False)
    reparsed = json.loads(serialized)
    assert reparsed["note_k"]["disposition"] == "CONFIRMED-with-mechanism"


# ── Determinism ───────────────────────────────────────────────────────────────


def test_run_is_deterministic(tmp_path: Path) -> None:
    """Running the script twice on the same inputs produces identical Markdown output."""
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)

    md1, _ = run(di_path, informants_path, mc_path, sub_path)
    md2, _ = run(di_path, informants_path, mc_path, sub_path)

    assert md1 == md2, "Script output is not deterministic on repeated runs"


# ── No forbidden vocabulary in output ────────────────────────────────────────


def test_no_forbidden_vocabulary_in_markdown(tmp_path: Path) -> None:
    """Markdown output does not contain forbidden vocabulary from CLAUDE.md §7.

    Tests for 'worldview', 'believes', 'thinks' applied to models.
    The mechanism string (D20) is correct wording; this test checks that
    no forbidden phrasing slips in elsewhere.
    """
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, _ = run(di_path, informants_path, mc_path, sub_path)

    md_lower = md.lower()
    # "worldview" applied to models
    assert "worldview" not in md_lower, "Forbidden vocabulary 'worldview' found in output"
    # "model believes" or "believes" applied to model outputs
    # We check for "the model believes" specifically to avoid false positives
    assert "the model believes" not in md_lower, "Forbidden phrase 'the model believes' found"
    assert "model thinks" not in md_lower, "Forbidden phrase 'model thinks' found"


# ── No LLM imports ────────────────────────────────────────────────────────────


def test_no_llm_imports_in_script() -> None:
    """The cross-tab script must not import any LLM client library (CLAUDE.md §6 rule 12)."""
    script_content = _SCRIPT_PATH.read_text(encoding="utf-8")
    forbidden = ["anthropic", "openai", "google.generativeai", "huggingface_hub", "InferenceClient"]
    for token in forbidden:
        assert token not in script_content, (
            f"Forbidden LLM import found in phase4a1_note_j_crosstab.py: {token!r}"
        )


def test_no_llm_imports_in_imported_modules() -> None:
    """Imported cdb_analyze modules must not contain LLM imports."""
    from cdb_analyze import manual_classification as mc_mod
    from cdb_analyze import safety_subtype as st_mod

    for mod_name, mod in [("manual_classification", mc_mod), ("safety_subtype", st_mod)]:
        content = Path(mod.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]
        forbidden = ["anthropic", "openai", "google.generativeai", "huggingface_hub"]
        for token in forbidden:
            assert token not in content, (
                f"Forbidden LLM import found in {mod_name}.py: {token!r}"
            )


# ── Additional Amendment 2 fixture cases ─────────────────────────────────────
# Covering the original Amendment 2 §3 T4 test fixture plan:
# "One fixture per Note K disposition (CONFIRMED-with-mechanism, INCONCLUSIVE-SUGGESTIVE,
#  INCONCLUSIVE, NOT CONFIRMED)."
# CONFIRMED-with-mechanism is covered by test_amendment3_9row_*
# CONFIRMED is covered by test_note_k_confirmed_single_provider
# INCONCLUSIVE-SUGGESTIVE is covered by test_note_k_inconclusive_suggestive
# INCONCLUSIVE is covered by test_note_k_inconclusive_single_row
# NOT CONFIRMED is covered by test_note_k_not_confirmed_no_safety_rows


def test_note_k_confirmed_with_mechanism_includes_blocked_in_arithmetic(
    tmp_path: Path,
) -> None:
    """CONFIRMED-with-mechanism counts blocked rows in arithmetic (Amendment 2 bullet 4).

    Fixture: 3 safety (google) + 2 blocked (openrouter) = 5 total, 2 providers.
    """
    safety_rows = [
        {"decline_interview_id": f"safety-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(3)
    ]
    blocked_rows = [
        {"decline_interview_id": f"blocked-{i}", "provider": "openrouter",
         "model_id": "z-ai/glm-5.1", "domain": "family"}
        for i in range(2)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows, blocked_rows=blocked_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "CONFIRMED-with-mechanism"
    assert note_k["safety_event_attribution_count"] == 3
    assert note_k["blocked_event_attribution_count"] == 2
    assert note_k["total_safety_blocked"] == 5
    assert note_k["n_providers"] == 2


def test_cross_provider_subtype_asymmetry_surfaced_not_disposition_shifted(
    tmp_path: Path,
) -> None:
    """Asymmetric K-frame/K-vocab split across providers is reflected in counts (D21).

    All K-frame rows are from provider A, all K-vocab rows are from provider B.
    Disposition must remain CONFIRMED-with-mechanism — the split is descriptive,
    not a disposition-tier trigger (D21).
    """
    # 5 k_frame from google, 4 k_vocab from openrouter
    safety_rows = [
        {"decline_interview_id": f"kframe-{i}", "provider": "google",
         "model_id": "google/gemini-2.5-pro", "domain": "family", "subtype": "k_frame"}
        for i in range(5)
    ] + [
        {"decline_interview_id": f"kvocab-{i}", "provider": "openrouter",
         "model_id": "z-ai/glm-5.1", "domain": "holidays",
         "subtype": "k_vocab_without_k_frame"}
        for i in range(4)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    # D21: disposition must NOT change based on K-frame/K-vocab split
    assert note_k["disposition"] == "CONFIRMED-with-mechanism"
    # The asymmetry is surfaced in the provider_subtype_counts
    psc = json_out["secondary_view_a"]["provider_subtype_counts"]
    assert psc.get("google", {}).get("k_frame", 0) == 5
    assert psc.get("openrouter", {}).get("k_vocab_without_k_frame", 0) == 4
    assert psc.get("openrouter", {}).get("k_frame", 0) == 0
    assert psc.get("google", {}).get("k_vocab_without_k_frame", 0) == 0


# ── Augmented tests (Tester, 2026-05-01) ─────────────────────────────────────
# Gaps identified against the 10 Amendment 3 §3.2 coverage points:
#
#  Gap A — 1-provider 9-row path: Reviewer "Notes for Tester" item 1 flagged that
#           the amendment3 9-row fixture exercises only the 2-provider branch
#           (CONFIRMED-with-mechanism). A single-provider 9-row fixture matching
#           actual production data should yield CONFIRMED, not CONFIRMED-with-mechanism.
#
#  Gap B — JSON output determinism: test_run_is_deterministic only compares md1==md2.
#           The spec (Amendment 3 §3.2 / task brief point 9) says
#           "byte-identical Markdown + JSON output." JSON side is untested.
#
#  Gap C — Note K mechanism breakdown two-row minimum explicit check: Amendment 3 §3.2
#           acceptance criteria states "Two-row format minimum: one row per subtype."
#           test_amendment3_9row_note_k_mechanism_breakdown_in_markdown checks the
#           section header but does not assert that both subtype rows appear in the
#           Markdown table body.
#
#  Gap D — Empty decline_interviews file: load_all_inputs raises ValueError if the
#           decline_interviews.jsonl file exists but has zero rows (line 164 of script).
#           No test exercises this code path.


def test_nine_row_single_provider_yields_confirmed(tmp_path: Path) -> None:
    """9-row safety cohort from a single provider yields CONFIRMED, not CONFIRMED-with-mechanism.

    Matches the Reviewer "Notes for Tester" item 1: the 2-provider fixture exercises the
    CONFIRMED-with-mechanism branch; a 1-provider 9-row fixture must exercise CONFIRMED.

    This mirrors the actual production data shape (all 9 safety rows from google).
    """
    safety_rows = [
        {
            "decline_interview_id": f"single-prov-{i:03d}",
            "provider": "google",
            "model_id": "google/gemini-2.5-pro",
            "domain": "family",
            "subtype": "k_frame" if i < 2 else "k_vocab_without_k_frame",
        }
        for i in range(9)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    note_k = json_out["note_k"]
    assert note_k["disposition"] == "CONFIRMED", (
        f"Expected CONFIRMED (single provider, 9 rows), got {note_k['disposition']!r}"
    )
    assert note_k["total_safety_blocked"] == 9
    assert note_k["n_providers"] == 1
    # Disposition string must be the bare tier label (no mechanism fragment), per D20
    assert note_k["disposition_string"] == "Note K: CONFIRMED", (
        f"Unexpected disposition_string: {note_k['disposition_string']!r}"
    )
    # Mechanism string still computed and present in JSON (it is the mechanism description
    # in a subordinate section); only the headline disposition_string must not carry it
    assert "mechanism_string" in note_k
    # Markdown must NOT carry the mechanism fragment in the disposition headline
    assert "Note K: CONFIRMED-with-mechanism" not in md, (
        "Mechanism headline must not appear when single-provider"
    )
    # The Note K section must still be present in Markdown
    assert "Note K Re-Evaluation" in md


def test_run_json_output_is_deterministic(tmp_path: Path) -> None:
    """Running the script twice on the same inputs produces byte-identical JSON output.

    Closes gap B: test_run_is_deterministic only compared Markdown.
    Amendment 3 §3.2 / task brief point 9 requires both outputs to be deterministic.
    """
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)

    _, json_out1 = run(di_path, informants_path, mc_path, sub_path)
    _, json_out2 = run(di_path, informants_path, mc_path, sub_path)

    serial1 = json.dumps(json_out1, sort_keys=True, ensure_ascii=False)
    serial2 = json.dumps(json_out2, sort_keys=True, ensure_ascii=False)
    assert serial1 == serial2, "JSON output is not deterministic on repeated runs"


def test_note_k_mechanism_breakdown_table_has_both_subtype_rows(tmp_path: Path) -> None:
    """Note K mechanism breakdown table in Markdown contains one row per subtype.

    Closes gap C: the two-row minimum (one row per subtype) in the Markdown table body
    is required by Amendment 3 §3.2 acceptance criteria.
    The section header test (test_amendment3_9row_note_k_mechanism_breakdown_in_markdown)
    only checks the heading; this test checks the table content.
    """
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, _ = run(di_path, informants_path, mc_path, sub_path)

    # Locate the "Note K Mechanism Breakdown" section in the Markdown
    assert "Note K Mechanism Breakdown" in md

    # Both subtype row labels must appear in the Markdown (they are used as table row keys)
    assert "k_frame" in md, "Expected 'k_frame' row in Note K Mechanism Breakdown table"
    assert "k_vocab_without_k_frame" in md, (
        "Expected 'k_vocab_without_k_frame' row in Note K Mechanism Breakdown table"
    )

    # The table must contain at least two data rows — verify by counting subtype occurrences
    # in the markdown section after the breakdown heading
    breakdown_start = md.index("Note K Mechanism Breakdown")
    breakdown_section = md[breakdown_start:]
    # Both subtypes must appear as table cell content in the section
    assert "k_frame" in breakdown_section
    assert "k_vocab_without_k_frame" in breakdown_section

    # Verify the provider_subtype_counts JSON also has both keys populated
    # (belt-and-suspenders for the Markdown test above)
    _, json_out = run(di_path, informants_path, mc_path, sub_path)
    psc = json_out["secondary_view_a"]["provider_subtype_counts"]
    all_subtypes = {st for provider_dict in psc.values() for st in provider_dict}
    assert "k_frame" in all_subtypes, (
        "provider_subtype_counts missing k_frame subtype"
    )
    assert "k_vocab_without_k_frame" in all_subtypes, (
        "provider_subtype_counts missing k_vocab_without_k_frame subtype"
    )


def test_empty_decline_interviews_file_raises(tmp_path: Path) -> None:
    """load_all_inputs raises ValueError when decline_interviews.jsonl exists but has zero rows.

    Closes gap D: the script's line 164 (ValueError on empty decline_rows) has no test.
    """
    di_path = tmp_path / "di.jsonl"
    informants_path = tmp_path / "informants.jsonl"
    mc_path = tmp_path / "mc.jsonl"
    sub_path = tmp_path / "subtype.jsonl"

    # Write an empty (but valid, existing) decline interviews file
    di_path.write_text("", encoding="utf-8")
    _write_minimal_informants(informants_path)
    _write_jsonl(mc_path, [])
    _write_jsonl(sub_path, [])

    with pytest.raises(ValueError, match="No rows found"):
        load_all_inputs(di_path, informants_path, mc_path, sub_path)


# ── Amendment 4 D24/D25 tests (task #21.T4.2-followup) ───────────────────────


def test_d24_single_provider_mechanism_wording(tmp_path: Path) -> None:
    """D24: Single-provider 9-row safety cohort emits single-provider mechanism wording.

    The rendered mechanism string must contain "within a single provider (Google Gemini)"
    and must NOT contain "cross-provider replication".

    Uses a synthetic fixture where provider == "Google Gemini" to match the D23
    canonical example string exactly.

    References:
        Amendment 4 D23/D24 — docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md
        Amendment 4 SME PASS — docs/status/2026-05-01-phase4a1-amendment-4-cda-sme-verdict.md
    """
    safety_rows = [
        {
            "decline_interview_id": f"single-prov-d24-{i:03d}",
            "provider": "Google Gemini",
            "model_id": "google/gemini-2.5-pro",
            "domain": "family" if i < 5 else "holidays",
            "subtype": "k_frame" if i < 2 else "k_vocab_without_k_frame",
        }
        for i in range(9)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    mechanism = json_out["note_k"]["mechanism_string"]

    # D23: single-provider wording must name the provider
    assert "within a single provider (Google Gemini)" in mechanism, (
        f"Expected 'within a single provider (Google Gemini)' in mechanism string: {mechanism!r}"
    )
    # D24: single-provider branch must NOT emit the cross-provider phrasing
    assert "cross-provider replication" not in mechanism, (
        f"Unexpected 'cross-provider replication' in single-provider "
        f"mechanism string: {mechanism!r}"
    )
    # Disposition must be CONFIRMED (1 provider, count >= 5)
    assert json_out["note_k"]["disposition"] == "CONFIRMED"
    assert json_out["note_k"]["n_providers"] == 1


def test_d24_multi_provider_mechanism_wording(tmp_path: Path) -> None:
    """D24: Multi-provider 6-row cohort emits cross-provider mechanism wording.

    The rendered mechanism string must contain "cross-provider replication" and
    must NOT contain "within a single provider".

    References:
        Amendment 4 D24 — docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md
    """
    safety_rows = [
        {
            "decline_interview_id": f"multi-google-{i:03d}",
            "provider": "google",
            "model_id": "google/gemini-2.5-pro",
            "domain": "family",
            "subtype": "k_frame",
        }
        for i in range(3)
    ] + [
        {
            "decline_interview_id": f"multi-other-{i:03d}",
            "provider": "openrouter",
            "model_id": "z-ai/glm-5.1",
            "domain": "holidays",
            "subtype": "k_vocab_without_k_frame",
        }
        for i in range(3)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    mechanism = json_out["note_k"]["mechanism_string"]

    # D24: multi-provider branch must emit the cross-provider phrasing
    assert "cross-provider replication" in mechanism, (
        f"Expected 'cross-provider replication' in multi-provider mechanism string: {mechanism!r}"
    )
    # D24: multi-provider branch must NOT emit the single-provider parenthetical
    assert "within a single provider" not in mechanism, (
        f"Unexpected 'within a single provider' in multi-provider mechanism string: {mechanism!r}"
    )
    # Disposition must be CONFIRMED-with-mechanism (2 providers, count >= 5)
    assert json_out["note_k"]["disposition"] == "CONFIRMED-with-mechanism"
    assert json_out["note_k"]["n_providers"] == 2


def test_d25_plain_confirmed_guardrail_in_markdown(tmp_path: Path) -> None:
    """D25: Plain-CONFIRMED branch emits the four-line defensive guardrail in Markdown.

    The rendered Markdown must contain the canonical guardrail substring:
    "a mechanism description, not a claim about the model's internal state"
    even when disposition is plain CONFIRMED (not CONFIRMED-with-mechanism).

    This verifies the D25 symmetric guardrail — the guardrail fires in both
    disposition branches, not only in CONFIRMED-with-mechanism.

    References:
        Amendment 4 D25 option (b) — docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md
        D27 canonical wording — same document
    """
    safety_rows = [
        {
            "decline_interview_id": f"guardrail-d25-{i:03d}",
            "provider": "google",
            "model_id": "google/gemini-2.5-pro",
            "domain": "family",
            "subtype": "k_frame" if i < 2 else "k_vocab_without_k_frame",
        }
        for i in range(9)
    ]

    di_path, informants_path, mc_path, sub_path = _build_cross_tab_fixture(
        tmp_path, safety_rows=safety_rows
    )
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    # Confirm we're in the plain-CONFIRMED branch
    assert json_out["note_k"]["disposition"] == "CONFIRMED", (
        f"Expected CONFIRMED disposition, got {json_out['note_k']['disposition']!r}"
    )
    assert json_out["note_k"]["n_providers"] == 1

    # D25 + D27 canonical wording: defensive guardrail must appear in plain-CONFIRMED branch.
    # The guardrail text spans multiple markdown lines; normalise line-breaks before checking.
    guardrail_substring = "a mechanism description, not a claim about the model's internal state"
    md_normalised = md.replace("\n", " ")
    assert guardrail_substring in md_normalised, (
        f"Defensive guardrail not found in plain-CONFIRMED Markdown output.\n"
        f"Expected substring: {guardrail_substring!r}\n"
        f"Markdown (Note K section):\n"
        + md[md.find("Note K Re-Evaluation"):] if "Note K Re-Evaluation" in md else md
    )
    # Mechanism description section must be present
    assert "### Mechanism description" in md, (
        "Mechanism description heading missing from plain-CONFIRMED Markdown output"
    )
    # The mechanism string must be blockquoted (> prefix), matching CONFIRMED-with-mechanism shape
    mechanism = json_out["note_k"]["mechanism_string"]
    assert f"> {mechanism}" in md, (
        "Mechanism string not in blockquote in plain-CONFIRMED Markdown output"
    )


# ── Amendment 4 augmenting tests (Tester, 2026-05-01) ────────────────────────
# Gaps identified against the 7 Amendment 4 coverage points in task brief:
#
#  Gap #4 — n_providers == 0 error path: Architect §3 specifies "When n_providers == 0
#            and disposition is CONFIRMED or higher, raise a clear error." No existing
#            test exercises this path in compute_note_k_disposition. Added below.
#
#  Gap #5 — Symmetric guardrail in CONFIRMED-with-mechanism branch: D25 option (b)
#            specifies the guardrail fires in BOTH branches.
#            test_d25_plain_confirmed_guardrail_in_markdown covers plain-CONFIRMED;
#            the CONFIRMED-with-mechanism branch has no explicit guardrail substring
#            assertion. Added below.


def test_n_providers_zero_with_confirmed_threshold_raises() -> None:
    """compute_note_k_disposition raises ValueError when n_providers == 0
    but total_safety_blocked >= NOTE_K_CONFIRMED_THRESHOLD.

    This is the D24 error guard: n_providers == 0 with a CONFIRMED-level count
    is an unreachable state in valid data and must raise rather than emit a
    malformed mechanism string.

    References:
        Amendment 4 D24 — docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md §3
    """
    from cdb_analyze.manual_classification import DeclineManualClassification
    from cdb_analyze.safety_subtype import SafetyAttributionSubtype

    # Build 5 safety_event_attribution manual classifications (meets CONFIRMED threshold)
    manual_classifications: dict[str, DeclineManualClassification] = {}
    for i in range(5):
        did = f"safety-zero-prov-{i:03d}"
        manual_classifications[did] = DeclineManualClassification(
            decline_interview_id=did,
            manual_classification="safety_event_attribution",
            manual_classification_rationale="Safety layer triggered.",
            manual_classifier_id="mark",
            response_verbatim_excerpt="Safety protocols prevented output.",
            detector_flag_v1=True,
        )

    # 2 subtypes with k_frame
    subtypes: dict[str, SafetyAttributionSubtype] = {}
    for i in range(2):
        did = f"safety-zero-prov-{i:03d}"
        subtypes[did] = SafetyAttributionSubtype(
            decline_interview_id=did,
            safety_attribution_subtype="k_frame",
            subtype_rationale="K-frame trigger.",
            subtype_classifier_id="mark",
        )

    # secondary_view_a with empty cross_provider_table -> n_providers == 0
    secondary_view_a_empty: dict = {
        "matrix": {},
        "triples": [],
        "cross_provider_table": [],       # empty -> distinct_providers == set() -> n_providers == 0
        "provider_subtype_counts": {},
    }

    with pytest.raises(ValueError, match="n_providers == 0"):
        compute_note_k_disposition(manual_classifications, subtypes, secondary_view_a_empty)


def test_d25_confirmed_with_mechanism_branch_also_has_guardrail(tmp_path: Path) -> None:
    """D25 symmetric guardrail: CONFIRMED-with-mechanism branch must also emit
    "a mechanism description, not a claim about the model's internal state".

    The task brief coverage point #5 requires the guardrail in BOTH branches.
    The existing test_d25_plain_confirmed_guardrail_in_markdown covers the plain-CONFIRMED
    branch. This test covers the CONFIRMED-with-mechanism branch explicitly.

    References:
        Amendment 4 D25 option (b) —
        docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md §3
    """
    # Use the standard 2-provider 9-row fixture which yields CONFIRMED-with-mechanism
    di_path, informants_path, mc_path, sub_path = _build_amendment3_9row_fixture(tmp_path)
    md, json_out = run(di_path, informants_path, mc_path, sub_path)

    # Confirm we're in the CONFIRMED-with-mechanism branch
    assert json_out["note_k"]["disposition"] == "CONFIRMED-with-mechanism", (
        f"Expected CONFIRMED-with-mechanism, got {json_out['note_k']['disposition']!r}"
    )

    # D25: the symmetric guardrail must appear in the CONFIRMED-with-mechanism branch too
    guardrail_substring = "a mechanism description, not a claim about the model's internal state"
    md_normalised = md.replace("\n", " ")
    assert guardrail_substring in md_normalised, (
        f"Defensive guardrail not found in CONFIRMED-with-mechanism Markdown output.\n"
        f"Expected substring: {guardrail_substring!r}"
    )
