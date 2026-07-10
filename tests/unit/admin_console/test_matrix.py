"""Unit tests for live_board/matrix.py (T4).

Deterministic matrix on fixtures; no mutation of informants.jsonl.
"""

from __future__ import annotations

import json
from pathlib import Path

from cdb_social.admin_console.live_board.matrix import compute_matrix

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ops_console"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _jsonl(*records: dict) -> str:
    return "\n".join(json.dumps(r) for r in records) + "\n"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestComputeMatrix:
    def test_returns_all_cells_for_specified_models_and_domains(
        self, tmp_path: Path
    ) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        result = compute_matrix(jsonl, ["m1", "m2"], ["d1", "d2"])
        assert "m1" in result and "m2" in result
        assert "d1" in result["m1"] and "d2" in result["m1"]

    def test_empty_jsonl_gives_zero_counts(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        result = compute_matrix(jsonl, ["m"], ["d"])
        assert result["m"]["d"].passed == 0
        assert result["m"]["d"].failed == 0

    def test_missing_jsonl_gives_zero_counts(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.jsonl"
        result = compute_matrix(missing, ["m"], ["d"])
        assert result["m"]["d"].passed == 0

    def test_counts_passed_records(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text(
            _jsonl(
                {"model_id": "m", "domain_slug": "d", "qa_passed": True},
                {"model_id": "m", "domain_slug": "d", "qa_passed": True},
                {"model_id": "m", "domain_slug": "d", "qa_passed": False},
            ),
            encoding="utf-8",
        )
        result = compute_matrix(jsonl, ["m"], ["d"])
        assert result["m"]["d"].passed == 2
        assert result["m"]["d"].failed == 1

    def test_only_counts_specified_models(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text(
            _jsonl(
                {"model_id": "included", "domain_slug": "d", "qa_passed": True},
                {"model_id": "excluded", "domain_slug": "d", "qa_passed": True},
            ),
            encoding="utf-8",
        )
        result = compute_matrix(jsonl, ["included"], ["d"])
        assert "excluded" not in result
        assert result["included"]["d"].passed == 1

    def test_only_counts_specified_domains(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text(
            _jsonl(
                {"model_id": "m", "domain_slug": "included", "qa_passed": True},
                {"model_id": "m", "domain_slug": "excluded", "qa_passed": True},
            ),
            encoding="utf-8",
        )
        result = compute_matrix(jsonl, ["m"], ["included"])
        assert "excluded" not in result["m"]
        assert result["m"]["included"].passed == 1

    def test_running_model_ids_sets_in_flight(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        result = compute_matrix(
            jsonl,
            ["m1", "m2"],
            ["d"],
            running_model_ids={"m1"},
        )
        assert result["m1"]["d"].in_flight is True
        assert result["m2"]["d"].in_flight is False

    def test_in_flight_false_by_default(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        result = compute_matrix(jsonl, ["m"], ["d"])
        assert result["m"]["d"].in_flight is False

    def test_reads_real_fixtures(self) -> None:
        jsonl = FIXTURES / "informants_mixed.jsonl"
        models = ["claude-opus-4-8", "z-ai/glm-5.2"]
        domains = ["family", "holidays"]
        result = compute_matrix(jsonl, models, domains)

        # claude-opus-4-8 / family: 2 passed, 1 failed
        assert result["claude-opus-4-8"]["family"].passed == 2
        assert result["claude-opus-4-8"]["family"].failed == 1

        # claude-opus-4-8 / holidays: 1 passed, 0 failed
        assert result["claude-opus-4-8"]["holidays"].passed == 1
        assert result["claude-opus-4-8"]["holidays"].failed == 0

        # z-ai/glm-5.2 / family: 1 passed, 3 failed
        assert result["z-ai/glm-5.2"]["family"].passed == 1
        assert result["z-ai/glm-5.2"]["family"].failed == 3

        # z-ai/glm-5.2 / holidays: 0 passed, 0 failed
        assert result["z-ai/glm-5.2"]["holidays"].passed == 0
        assert result["z-ai/glm-5.2"]["holidays"].failed == 0

    def test_skips_malformed_json_lines(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text(
            "not json at all\n"
            '{"model_id": "m", "domain_slug": "d", "qa_passed": true}\n',
            encoding="utf-8",
        )
        result = compute_matrix(jsonl, ["m"], ["d"])
        assert result["m"]["d"].passed == 1
