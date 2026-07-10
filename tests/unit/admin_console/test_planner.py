"""Unit tests for campaign_runner/planner.py (T1).

Pure functions; no real API calls; no subprocess; tmp_path only.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cdb_social.admin_console.campaign_runner.planner import (
    NEW_DOMAIN_SENTINEL,
    CampaignPlan,
    CellShortfall,
    ModelInfo,
    compute_shortfall,
    list_domains,
    list_models,
    render_plan_text,
)

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ops_console"


# ---------------------------------------------------------------------------
# list_domains
# ---------------------------------------------------------------------------


class TestListDomains:
    def test_returns_empty_for_missing_path(self, tmp_path: Path) -> None:
        result = list_domains(tmp_path / "nonexistent")
        assert result == []

    def test_reads_yaml_files(self, tmp_path: Path) -> None:
        (tmp_path / "family.yaml").write_text(
            "slug: family\ndisplay_name: Family Terms\n", encoding="utf-8"
        )
        (tmp_path / "holidays.yaml").write_text(
            "slug: holidays\ndisplay_name: Holidays\n", encoding="utf-8"
        )
        result = list_domains(tmp_path)
        slugs = [d.slug for d in result]
        assert "family" in slugs
        assert "holidays" in slugs

    def test_returns_domain_info_fields(self, tmp_path: Path) -> None:
        (tmp_path / "food.yaml").write_text(
            "slug: food\ndisplay_name: Food Items\n", encoding="utf-8"
        )
        result = list_domains(tmp_path)
        assert len(result) == 1
        assert result[0].slug == "food"
        assert result[0].display_name == "Food Items"

    def test_skips_invalid_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "bad.yaml").write_text("---\n[invalid yaml: ]{{", encoding="utf-8")
        (tmp_path / "good.yaml").write_text("slug: good\ndisplay_name: Good\n", encoding="utf-8")
        result = list_domains(tmp_path)
        # bad.yaml is skipped; good.yaml is returned
        assert len(result) == 1
        assert result[0].slug == "good"

    def test_falls_back_to_stem_for_missing_slug(self, tmp_path: Path) -> None:
        (tmp_path / "fallback.yaml").write_text(
            "display_name: No Slug\n", encoding="utf-8"
        )
        result = list_domains(tmp_path)
        assert result[0].slug == "fallback"

    def test_reads_real_fixtures(self) -> None:
        domains_path = Path("data/domains/v1")
        if not domains_path.exists():
            pytest.skip("data/domains/v1 not present in this environment")
        result = list_domains(domains_path)
        assert len(result) >= 1
        slugs = [d.slug for d in result]
        assert "family" in slugs


# ---------------------------------------------------------------------------
# list_models
# ---------------------------------------------------------------------------


class TestListModels:
    def _make_registry(self, tmp_path: Path, models: list[dict]) -> Path:
        path = tmp_path / "registry.json"
        path.write_text(
            json.dumps({"updated_at": "2026-07-10", "models": models}),
            encoding="utf-8",
        )
        return path

    def test_returns_empty_for_missing_registry(self, tmp_path: Path) -> None:
        result = list_models(tmp_path / "missing.json")
        assert result == []

    def test_returns_empty_for_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json", encoding="utf-8")
        assert list_models(path) == []

    def test_parses_model_entries(self, tmp_path: Path) -> None:
        path = self._make_registry(
            tmp_path,
            [
                {
                    "model_id": "claude-opus-4-8",
                    "display_name": "Claude Opus 4.8",
                    "family": "claude",
                    "records": 15,
                }
            ],
        )
        result = list_models(path)
        assert len(result) == 1
        assert result[0].model_id == "claude-opus-4-8"
        assert result[0].display_name == "Claude Opus 4.8"
        assert result[0].family == "claude"
        assert result[0].records == 15

    def test_skips_entries_without_model_id(self, tmp_path: Path) -> None:
        path = self._make_registry(
            tmp_path,
            [{"display_name": "No ID", "family": "unknown", "records": 0}],
        )
        assert list_models(path) == []

    def test_defaults_records_to_zero(self, tmp_path: Path) -> None:
        path = self._make_registry(
            tmp_path,
            [{"model_id": "new-model", "display_name": "New", "family": "new"}],
        )
        result = list_models(path)
        assert result[0].records == 0

    def test_defaults_display_name_to_model_id(self, tmp_path: Path) -> None:
        path = self._make_registry(
            tmp_path,
            [{"model_id": "my-model", "family": "x"}],
        )
        result = list_models(path)
        assert result[0].display_name == "my-model"


# ---------------------------------------------------------------------------
# compute_shortfall
# ---------------------------------------------------------------------------


def _make_models(*model_ids: str) -> list[ModelInfo]:
    return [
        ModelInfo(model_id=mid, display_name=mid, family="test", records=0)
        for mid in model_ids
    ]


class TestComputeShortfall:
    def test_returns_sentinel_for_unknown_domain(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        models = _make_models("claude-opus-4-8")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["new-domain-xyz"],
            runs_per_cell=5,
            known_slugs={"family", "holidays"},
        )
        assert result is NEW_DOMAIN_SENTINEL

    def test_known_slug_returns_plan(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        models = _make_models("claude-opus-4-8")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["family"],
            runs_per_cell=5,
            known_slugs={"family", "holidays"},
        )
        assert isinstance(result, CampaignPlan)

    def test_empty_jsonl_gives_full_shortfall(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        models = _make_models("claude-opus-4-8", "z-ai/glm-5.2")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["family", "holidays"],
            runs_per_cell=5,
        )
        assert isinstance(result, CampaignPlan)
        for cell in result.cells:
            assert cell.passed == 0
            assert cell.needed == 5

    def test_missing_jsonl_gives_full_shortfall(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.jsonl"
        models = _make_models("claude-opus-4-8")
        result = compute_shortfall(
            missing,
            models,
            domain_slugs=["family"],
            runs_per_cell=5,
        )
        assert isinstance(result, CampaignPlan)
        assert result.cells[0].needed == 5

    def test_counts_only_qa_passed_true(self, tmp_path: Path) -> None:
        jsonl = FIXTURES / "informants_mixed.jsonl"
        models = _make_models("claude-opus-4-8")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["family"],
            runs_per_cell=5,
        )
        assert isinstance(result, CampaignPlan)
        family_cell = next(c for c in result.cells if c.domain_slug == "family")
        # Fixture has 2 qa_passed=True records for claude-opus-4-8 / family
        assert family_cell.passed == 2
        assert family_cell.needed == 3

    def test_needed_is_zero_when_cell_complete(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        lines = "\n".join(
            json.dumps({
                "model_id": "claude-opus-4-8",
                "domain_slug": "family",
                "qa_passed": True,
            })
            for _ in range(6)
        )
        jsonl.write_text(lines, encoding="utf-8")
        models = _make_models("claude-opus-4-8")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["family"],
            runs_per_cell=5,
        )
        assert isinstance(result, CampaignPlan)
        assert result.cells[0].needed == 0

    def test_model_not_in_jsonl_gets_full_shortfall(self, tmp_path: Path) -> None:
        jsonl = FIXTURES / "informants_mixed.jsonl"
        models = _make_models("brand-new-model")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["family"],
            runs_per_cell=5,
        )
        assert isinstance(result, CampaignPlan)
        assert result.cells[0].passed == 0
        assert result.cells[0].needed == 5

    def test_skips_malformed_json_lines(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text(
            'not json\n{"model_id":"m","domain_slug":"d","qa_passed":true}\n',
            encoding="utf-8",
        )
        models = _make_models("m")
        result = compute_shortfall(jsonl, models, domain_slugs=["d"], runs_per_cell=3)
        assert isinstance(result, CampaignPlan)
        assert result.cells[0].passed == 1

    def test_campaign_id_propagated(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        models = _make_models("m")
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["d"],
            runs_per_cell=5,
            campaign_id="my-campaign-id",
        )
        assert isinstance(result, CampaignPlan)
        assert result.campaign_id == "my-campaign-id"

    def test_no_known_slugs_never_returns_sentinel(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        models = _make_models("m")
        # When known_slugs is None, no sentinel should be returned regardless
        result = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["completely-new-domain"],
            runs_per_cell=5,
        )
        assert isinstance(result, CampaignPlan)


# ---------------------------------------------------------------------------
# render_plan_text
# ---------------------------------------------------------------------------


class TestRenderPlanText:
    def _make_plan(
        self, cells: list[tuple[str, str, int, int]]
    ) -> CampaignPlan:
        """Helper: create a CampaignPlan with given (model_id, domain, passed, needed)."""
        return CampaignPlan(
            campaign_id="test",
            models=[],
            domain_slugs=[],
            runs_per_cell=5,
            cells=[
                CellShortfall(model_id=m, domain_slug=d, passed=p, needed=n)
                for m, d, p, n in cells
            ],
        )

    def test_empty_plan_returns_empty_string(self) -> None:
        plan = self._make_plan([("m", "d", 5, 0)])
        assert render_plan_text(plan) == ""

    def test_only_includes_needed_gt_zero(self) -> None:
        plan = self._make_plan([
            ("m1", "family", 3, 2),
            ("m1", "holidays", 5, 0),
        ])
        text = render_plan_text(plan)
        assert "m1 family 2" in text
        assert "holidays" not in text

    def test_format_matches_resume_plan_txt(self) -> None:
        plan = self._make_plan([
            ("claude-opus-4-8", "family", 0, 5),
            ("z-ai/glm-5.2", "food", 2, 3),
        ])
        text = render_plan_text(plan)
        lines = [ln for ln in text.splitlines() if ln.strip()]
        assert lines[0] == "claude-opus-4-8 family 5"
        assert lines[1] == "z-ai/glm-5.2 food 3"

    def test_ends_with_newline_when_nonempty(self) -> None:
        plan = self._make_plan([("m", "d", 0, 5)])
        text = render_plan_text(plan)
        assert text.endswith("\n")

    def test_round_trip_with_compute_shortfall(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "informants.jsonl"
        jsonl.write_text("", encoding="utf-8")
        models = _make_models("claude-opus-4-8", "z-ai/glm-5.2")
        plan = compute_shortfall(
            jsonl,
            models,
            domain_slugs=["family", "food"],
            runs_per_cell=5,
        )
        assert isinstance(plan, CampaignPlan)
        text = render_plan_text(plan)
        lines = [ln for ln in text.splitlines() if ln]
        # 2 models x 2 domains = 4 cells; all needed=5
        assert len(lines) == 4
