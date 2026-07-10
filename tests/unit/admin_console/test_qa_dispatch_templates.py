"""Unit tests for qa/dispatch_templates.py (T7).

No real API calls. Uses synthetic HistogramRow and DivergenceRow data.
"""

from __future__ import annotations

from cdb_social.admin_console.qa.dispatch_templates import DispatchTemplate, build_templates
from cdb_social.admin_console.qa.divergence import DivergenceRow
from cdb_social.admin_console.qa.histogram import HistogramRow

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hist(*args: tuple[str, int, int]) -> list[HistogramRow]:
    """Build histogram rows from (model_id, check_num, count) tuples."""
    return [HistogramRow(model_id=m, check_num=c, count=n) for m, c, n in args]


def _div_row(
    iid: str,
    model: str,
    domain: str,
    persisted: bool,
    checks: list[int],
    error: str | None = None,
) -> DivergenceRow:
    return DivergenceRow(
        informant_id=iid,
        model_id=model,
        domain_slug=domain,
        persisted_passed=persisted,
        recomputed_check_nums=checks,
        error=error,
    )


# ---------------------------------------------------------------------------
# build_templates structure
# ---------------------------------------------------------------------------


class TestBuildTemplates:
    def test_always_returns_at_least_one_template(self) -> None:
        result = build_templates([], [])
        assert len(result) >= 1

    def test_returns_dispatch_template_instances(self) -> None:
        result = build_templates([], [])
        for t in result:
            assert isinstance(t, DispatchTemplate)
            assert isinstance(t.title, str)
            assert isinstance(t.content, str)

    def test_summary_template_present(self) -> None:
        result = build_templates([], [])
        titles = [t.title for t in result]
        assert any("Summary" in title for title in titles)

    def test_summary_includes_zero_counts_when_empty(self) -> None:
        result = build_templates([], [])
        summary = next(t for t in result if "Summary" in t.title)
        assert "0" in summary.content

    def test_per_model_template_added_when_failures_exist(self) -> None:
        rows = _hist(("model-x", 1, 3))
        result = build_templates(rows, [])
        titles = [t.title for t in result]
        assert any("model-x" in t for t in titles)

    def test_divergence_template_added_when_divergence_exists(self) -> None:
        div_rows = [_div_row("id1", "m", "d", True, [1])]
        result = build_templates([], div_rows)
        titles = [t.title for t in result]
        assert any("Divergence" in t for t in titles)

    def test_no_divergence_template_when_no_divergence(self) -> None:
        result = build_templates(_hist(("m", 1, 2)), [])
        titles = [t.title for t in result]
        assert not any("Divergence" in t for t in titles)

    def test_summary_includes_failure_count(self) -> None:
        rows = _hist(("m", 1, 5), ("m", 2, 3))
        result = build_templates(rows, [])
        summary = next(t for t in result if "Summary" in t.title)
        # Total failures = 5 + 3 = 8
        assert "8" in summary.content

    def test_summary_includes_model_count(self) -> None:
        rows = _hist(("model-a", 1, 2), ("model-b", 3, 1))
        result = build_templates(rows, [])
        summary = next(t for t in result if "Summary" in t.title)
        assert "2" in summary.content  # 2 models with failures

    def test_model_failure_template_includes_check_numbers(self) -> None:
        rows = _hist(("model-z", 1, 4), ("model-z", 5, 2))
        result = build_templates(rows, [])
        model_tmpl = next(t for t in result if "model-z" in t.title)
        assert "Check 1" in model_tmpl.content
        assert "Check 5" in model_tmpl.content

    def test_model_failure_template_includes_counts(self) -> None:
        rows = _hist(("model-z", 1, 7))
        result = build_templates(rows, [])
        model_tmpl = next(t for t in result if "model-z" in t.title)
        assert "7" in model_tmpl.content

    def test_divergence_template_includes_boundary_label(self) -> None:
        div_rows = [_div_row("id1", "m", "d", True, [1])]
        result = build_templates([], div_rows)
        div_tmpl = next(t for t in result if "Divergence" in t.title)
        assert "persisted" in div_tmpl.content.lower()
        assert "recomputed" in div_tmpl.content.lower()

    def test_divergence_template_includes_informant_id(self) -> None:
        div_rows = [_div_row("rec-999", "m", "d", False, [])]
        result = build_templates([], div_rows)
        div_tmpl = next(t for t in result if "Divergence" in t.title)
        assert "rec-999" in div_tmpl.content

    def test_divergence_template_shows_pass_when_no_failing_checks(self) -> None:
        div_rows = [_div_row("id1", "m", "d", False, [])]
        result = build_templates([], div_rows)
        div_tmpl = next(t for t in result if "Divergence" in t.title)
        assert "pass" in div_tmpl.content

    def test_divergence_template_shows_check_numbers(self) -> None:
        div_rows = [_div_row("id1", "m", "d", True, [3, 6])]
        result = build_templates([], div_rows)
        div_tmpl = next(t for t in result if "Divergence" in t.title)
        assert "C3" in div_tmpl.content
        assert "C6" in div_tmpl.content

    def test_no_em_dashes_in_any_template(self) -> None:
        rows = _hist(("model-a", 1, 3), ("model-b", 2, 1))
        div_rows = [_div_row("i1", "m", "d", True, [1], error="some error")]
        result = build_templates(rows, div_rows)
        for t in result:
            assert "—" not in t.content, (
                f"Em dash found in template {t.title!r}"
            )
            assert "–" not in t.content, (
                f"En dash found in template {t.title!r}"
            )

    def test_content_is_nonempty_string(self) -> None:
        result = build_templates(_hist(("m", 1, 1)), [])
        for t in result:
            assert t.content.strip(), f"Template {t.title!r} has empty content"
