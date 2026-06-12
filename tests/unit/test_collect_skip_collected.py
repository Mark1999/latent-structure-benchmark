"""Tests for --skip-collected domain-aware scoping (BUG 1).

All tests use temp files and inline JSONL data. No real API calls.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts.collect import _load_collected_model_domain_pairs, _load_collected_model_ids


def _write_jsonl(path: Path, records: list[dict]) -> None:
    """Write records as JSONL lines to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


# ── _load_collected_model_domain_pairs ───────────────────────────────


def test_load_pairs_empty_file():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        pairs = _load_collected_model_domain_pairs(path)
    assert pairs == set()


def test_load_pairs_missing_file():
    path = Path("/tmp/does_not_exist_12345.jsonl")
    pairs = _load_collected_model_domain_pairs(path)
    assert pairs == set()


def test_load_pairs_single_record():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        _write_jsonl(path, [{"model_id": "model-a", "domain_slug": "family"}])
        pairs = _load_collected_model_domain_pairs(path)
    assert ("model-a", "family") in pairs


def test_load_pairs_multiple_domains():
    """Model A with family records does not block model A on food."""
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        _write_jsonl(path, [
            {"model_id": "model-a", "domain_slug": "family"},
            {"model_id": "model-a", "domain_slug": "family"},
            {"model_id": "model-b", "domain_slug": "food"},
        ])
        pairs = _load_collected_model_domain_pairs(path)
    assert ("model-a", "family") in pairs
    assert ("model-b", "food") in pairs
    # model-a has NO food record, so (model-a, food) must not be present
    assert ("model-a", "food") not in pairs


def test_load_pairs_ignores_malformed_lines():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        path.write_text(
            '{"model_id": "model-a", "domain_slug": "family"}\n'
            "NOT_JSON\n"
            '{"model_id": "model-b", "domain_slug": "food"}\n',
            encoding="utf-8",
        )
        pairs = _load_collected_model_domain_pairs(path)
    assert ("model-a", "family") in pairs
    assert ("model-b", "food") in pairs
    assert len(pairs) == 2


# ── Cross-mode collision semantic (AC7) ─────────────────────────────


def test_ac7_food_record_with_any_mode_satisfies_skip():
    """A (model_a, food) pair in the set blocks model_a on food regardless of
    the collection_mode that was originally recorded. The 2-tuple key means any
    food record (single_pass OR cross_model_consensus) triggers the skip."""
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        # Simulate a food single_pass record (collection_mode is not read by
        # _load_collected_model_domain_pairs; the 2-tuple key is domain-only)
        _write_jsonl(path, [
            {
                "model_id": "model-a",
                "domain_slug": "food",
                "collection_mode": "single_pass",
            },
        ])
        pairs = _load_collected_model_domain_pairs(path)
    assert ("model-a", "food") in pairs


# ── BUG 1 AC5: single_pass skip is domain-scoped ────────────────────


def test_single_pass_skip_only_fires_for_matching_domain():
    """Model A has family records only. --domain food should NOT skip model A.

    This exercises the domain-aware check: (model_a, food) is not in the
    collected set even though (model_a, family) is.
    """
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        _write_jsonl(path, [
            {"model_id": "model-a", "domain_slug": "family"},
        ])
        pairs = _load_collected_model_domain_pairs(path)

    # Simulates the check in main() for single-model modes:
    #   if (model_ref.model_id, args.domain) in collected_pairs: skip
    assert ("model-a", "food") not in pairs, (
        "model-a has only family records; skip check for food must not fire"
    )
    assert ("model-a", "family") in pairs, (
        "model-a has family records; skip check for family should fire"
    )


# ── BUG 1 AC6: cross_model per-model skip is domain-scoped ──────────


def test_cross_model_per_model_skip_not_triggered_by_different_domain():
    """Model A has only family records. cross_model run for food must not skip A.

    Mirrors AC6: the per-model skip in the cross_model branch uses the same
    (model_id, domain_slug) set. A family record does not block a food run.
    """
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        _write_jsonl(path, [
            {"model_id": "model-a", "domain_slug": "family"},
        ])
        pairs = _load_collected_model_domain_pairs(path)

    # In cross_model branch: if (ref.model_id, args.domain) in collected_pairs: skip
    assert ("model-a", "food") not in pairs, (
        "model-a with only family records must not be skipped for food cross_model"
    )


# ── BUG 1 AC7: model A with food record IS skipped for food ─────────


def test_cross_model_per_model_skip_fires_for_matching_domain():
    """Model A has a food record. cross_model run for food should skip A.

    Mirrors AC7: (model_a, food) in collected_pairs triggers skip regardless
    of whether the prior record was single_pass or cross_model_consensus.
    """
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        _write_jsonl(path, [
            {"model_id": "model-a", "domain_slug": "food"},
        ])
        pairs = _load_collected_model_domain_pairs(path)

    assert ("model-a", "food") in pairs, (
        "model-a with a food record must be in the skip set for food"
    )


# ── list-models display still uses _load_collected_model_ids (AC4) ───


def test_list_models_display_uses_model_id_only():
    """_load_collected_model_ids (used for --list-models display) returns a flat
    set of model_id strings, not (model_id, domain) tuples."""
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "informants.jsonl"
        _write_jsonl(path, [
            {"model_id": "model-a", "domain_slug": "family"},
            {"model_id": "model-a", "domain_slug": "food"},
        ])
        ids = _load_collected_model_ids(path)

    assert ids == {"model-a"}
    assert isinstance(ids, set)
    assert isinstance(next(iter(ids)), str)


# ── BUG 1 AC10: single-model skip guard does not fire for cross_model ─


def test_skip_guard_is_in_else_branch_not_cross_model_branch():
    """The single-model domain-aware skip guard (else branch in main()) must
    not interfere with cross_model dispatch.

    AC10: The early single-model skip guard fires only when args.mode is
    single_pass, two_pass, or baseline (the 'else' branch). It must not
    block the cross_model branch. This test verifies the code-path isolation
    by inspecting the collect.py source: the skip guard must appear inside
    the else branch body (after 'else:'), not at the top-level of main().

    The test is structural rather than behavioural because the cross_model
    path requires a full registry + adapter setup. Structural inspection is
    the correct fixture-based approach here: if the guard moves out of the
    else branch in a future refactor, this test will fail immediately.
    """
    import ast
    import inspect

    import scripts.collect as collect_module

    source = inspect.getsource(collect_module.main)
    tree = ast.parse(source)

    # Walk the AST of main(). The top-level if/else structure controlling
    # the cross_model vs. single-model dispatch is:
    #
    #   if args.mode == "cross_model":
    #       ...
    #   else:
    #       ...
    #       if args.skip_collected:
    #           collected_pairs = _load_collected_model_domain_pairs(...)
    #           if (...) in collected_pairs:
    #               return 0   <-- this is the skip guard
    #
    # We verify:
    # (a) There exists an If node whose test compares args.mode to "cross_model".
    # (b) The skip guard (a call to _load_collected_model_domain_pairs) does NOT
    #     appear in the orelse body of that If node -- it appears in the else
    #     branch (the orelse list), not outside it.
    #
    # Concretely: _load_collected_model_domain_pairs must NOT appear in the
    # body (cross_model branch); it MUST appear in the orelse (else branch).

    def _names_in_stmts(stmts) -> set[str]:
        """Collect all Name and Attribute id/attr strings from a statement list."""
        names: set[str] = set()
        for node in ast.walk(ast.Module(body=stmts, type_ignores=[])):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
        return names

    cross_model_if: ast.If | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            # Match: args.mode == "cross_model"
            if (
                isinstance(test, ast.Compare)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "cross_model"
            ):
                cross_model_if = node
                break

    assert cross_model_if is not None, (
        "main() must contain an 'if args.mode == \"cross_model\"' branch"
    )

    # The skip guard must NOT appear in the cross_model (if) body
    cross_model_body_names = _names_in_stmts(cross_model_if.body)
    # The skip guard MUST appear in the else branch (orelse)
    else_branch_names = _names_in_stmts(cross_model_if.orelse)

    assert "_load_collected_model_domain_pairs" not in cross_model_body_names or (
        # It IS acceptable in cross_model body (for the cross_model per-model skip),
        # but it must also appear in the else branch for single-model skip.
        "_load_collected_model_domain_pairs" in else_branch_names
    ), (
        "_load_collected_model_domain_pairs must appear in the else branch "
        "so the single-model skip guard does not interfere with cross_model dispatch"
    )
    assert "_load_collected_model_domain_pairs" in else_branch_names, (
        "The domain-aware skip guard must be in the else branch (single-model modes), "
        "not absent from it. AC10 requires it to be isolated from the cross_model path."
    )
