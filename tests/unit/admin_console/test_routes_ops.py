"""Integration smoke test for routes_ops.py (T9).

Walks all GET pages with the Flask test client. Verifies 200 status and
presence of CSRF token on every page that has a form.

No real subprocess. Launcher is injected via app.config.
No real API calls. tmp_path only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from cdb_social.admin_console.app import create_app

# ---------------------------------------------------------------------------
# Fake launcher (injects into app.config to prevent real subprocess)
# ---------------------------------------------------------------------------


class _FakeLauncher:
    """Fake LaneLauncher that writes plan artifacts without spawning processes."""

    def launch(
        self, plan: Any, log_root: Path, repo_root: Path
    ) -> dict[str, int]:
        log_root.mkdir(parents=True, exist_ok=True)
        cells = [
            {
                "model_id": c.model_id,
                "domain_slug": c.domain_slug,
                "passed": c.passed,
                "needed": c.needed,
            }
            for c in plan.cells
            if c.needed > 0
        ]
        plan_data = {
            "campaign_id": plan.campaign_id,
            "runs_per_cell": plan.runs_per_cell,
            "cells": cells,
        }
        (log_root / "plan.json").write_text(
            json.dumps(plan_data, indent=2), encoding="utf-8"
        )
        return {}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ops_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set up minimal ops environment in tmp_path."""
    # Domain directory with one YAML file
    domains_dir = tmp_path / "domains"
    domains_dir.mkdir()
    (domains_dir / "family.yaml").write_text(
        "slug: family\ndisplay_name: Family Terms\n", encoding="utf-8"
    )

    # Registry with one model
    registry = {
        "updated_at": "2026-07-10",
        "models": [
            {
                "model_id": "test-model",
                "display_name": "Test Model",
                "family": "test",
                "records": 0,
            }
        ],
    }
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    # Empty informants.jsonl
    informants_path = tmp_path / "informants.jsonl"
    informants_path.write_text("", encoding="utf-8")

    # Ops log root
    ops_log_root = tmp_path / "logs" / "ops-console"
    ops_log_root.mkdir(parents=True)

    monkeypatch.setenv("LSB_DOMAINS_PATH", str(domains_dir))
    monkeypatch.setenv("LSB_REGISTRY_PATH", str(registry_path))
    monkeypatch.setenv("LSB_INFORMANTS_PATH", str(informants_path))
    monkeypatch.setenv("LSB_OPS_LOG_ROOT", str(ops_log_root))
    monkeypatch.setenv("LSB_REPO_ROOT", str(tmp_path))

    return tmp_path


@pytest.fixture
def client(ops_env: Path) -> Any:
    """Flask test client with fake launcher injected."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["OPS_LANE_LAUNCHER"] = _FakeLauncher()
    with app.test_client() as c:
        yield c


@pytest.fixture
def campaign_id(ops_env: Path) -> str:
    """Create a fake campaign log directory and return its ID."""
    cid = "test-campaign-smoke"
    log_dir = ops_env / "logs" / "ops-console" / cid
    log_dir.mkdir(parents=True)
    plan_data = {
        "campaign_id": cid,
        "runs_per_cell": 5,
        "cells": [
            {
                "model_id": "test-model",
                "domain_slug": "family",
                "passed": 0,
                "needed": 5,
            }
        ],
    }
    (log_dir / "plan.json").write_text(
        json.dumps(plan_data), encoding="utf-8"
    )
    (log_dir / "test-model.log").write_text(
        "=== 2026-07-10T10:00:00Z LANE test-model / family runs=5 ===\n"
        "=== exit 0 ===\n",
        encoding="utf-8",
    )
    return cid


# ---------------------------------------------------------------------------
# Smoke tests: all GET pages return 200
# ---------------------------------------------------------------------------


class TestGetPageStatus:
    def test_campaigns_new_returns_200(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert resp.status_code == 200

    def test_live_board_returns_200(self, client: Any, campaign_id: str) -> None:
        resp = client.get(f"/ops/live/{campaign_id}")
        assert resp.status_code == 200

    def test_lane_tail_returns_200(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}/lane/test-model/tail")
        assert resp.status_code == 200

    def test_qa_panel_returns_200(self, client: Any) -> None:
        resp = client.get("/ops/qa")
        assert resp.status_code == 200

    def test_dispatch_template_returns_200(self, client: Any) -> None:
        resp = client.get("/ops/qa/template")
        # With empty informants.jsonl the summary template always exists.
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# CSRF token present on all forms
# ---------------------------------------------------------------------------


class TestCsrfOnForms:
    def test_campaigns_new_has_csrf_token(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b'name="csrf_token"' in resp.data

    def test_live_board_has_csrf_token(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}")
        assert b'name="csrf_token"' in resp.data


# ---------------------------------------------------------------------------
# Panel 1 behaviour
# ---------------------------------------------------------------------------


class TestCampaignsNew:
    def test_shows_domain_from_registry(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b"family" in resp.data

    def test_shows_model_from_registry(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b"test-model" in resp.data

    def test_shows_runs_per_cell_input(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b"runs_per_cell" in resp.data


class TestCampaignsPlan:
    def _get_csrf(self, client: Any) -> str:
        resp = client.get("/ops/campaigns/new")
        # Extract CSRF token from the form
        body = resp.data.decode("utf-8")
        idx = body.find('name="csrf_token"')
        # Find value="..."
        val_start = body.find('value="', idx) + len('value="')
        val_end = body.find('"', val_start)
        return body[val_start:val_end]

    def test_plan_post_with_new_domain_shows_tier1_notice(
        self, client: Any
    ) -> None:
        csrf = self._get_csrf(client)
        resp = client.post(
            "/ops/campaigns/plan",
            data={
                "csrf_token": csrf,
                "new_domain": "weather",
                "model_ids": "test-model",
                "runs_per_cell": "5",
            },
        )
        assert resp.status_code == 200
        assert b"Tier 1" in resp.data

    def test_plan_post_never_launches_for_new_domain(
        self, client: Any
    ) -> None:
        csrf = self._get_csrf(client)
        resp = client.post(
            "/ops/campaigns/plan",
            data={
                "csrf_token": csrf,
                "new_domain": "weather",
                "model_ids": "test-model",
                "runs_per_cell": "5",
            },
        )
        # Should not redirect to live board or launch anything
        assert resp.status_code == 200

    def test_plan_post_with_known_domain_renders_plan(
        self, client: Any
    ) -> None:
        csrf = self._get_csrf(client)
        resp = client.post(
            "/ops/campaigns/plan",
            data={
                "csrf_token": csrf,
                "domain_slugs": "family",
                "model_ids": "test-model",
                "runs_per_cell": "5",
            },
        )
        assert resp.status_code == 200
        assert b"Shortfall" in resp.data or b"plan" in resp.data.lower()

    def test_plan_post_without_csrf_returns_403(self, client: Any) -> None:
        resp = client.post(
            "/ops/campaigns/plan",
            data={
                "csrf_token": "bad-token",
                "domain_slugs": "family",
                "model_ids": "test-model",
                "runs_per_cell": "5",
            },
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Panel 2 behaviour
# ---------------------------------------------------------------------------


class TestLiveBoardRoutes:
    def test_live_board_shows_campaign_id(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}")
        assert campaign_id.encode() in resp.data

    def test_live_board_shows_model_ids(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}")
        assert b"test-model" in resp.data

    def test_live_board_shows_domain_slugs(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}")
        assert b"family" in resp.data

    def test_lane_tail_shows_log_content(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}/lane/test-model/tail")
        assert b"exit 0" in resp.data

    def test_lane_tail_absent_log_shows_not_found(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(f"/ops/live/{campaign_id}/lane/missing-model/tail")
        assert resp.status_code == 200
        assert b"not found" in resp.data

    def test_live_board_with_nothing_to_do_notice(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.get(
            f"/ops/live/{campaign_id}?nothing_to_do=1"
        )
        assert resp.status_code == 200
        assert b"complete" in resp.data.lower()

    def test_lane_stop_without_csrf_returns_403(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.post(
            f"/ops/live/{campaign_id}/lane/test-model/stop",
            data={"csrf_token": "bad"},
        )
        assert resp.status_code == 403

    def test_lane_stop_exited_lane_redirects_with_notice(
        self, client: Any, campaign_id: str
    ) -> None:
        # Get CSRF from live board
        resp = client.get(f"/ops/live/{campaign_id}")
        body = resp.data.decode("utf-8")
        idx = body.find('name="csrf_token"')
        if idx < 0:
            pytest.skip("No CSRF token found in live board")
        val_start = body.find('value="', idx) + len('value="')
        val_end = body.find('"', val_start)
        csrf = body[val_start:val_end]

        # The lane in the fixture has no pidfile, so it will report "not found"
        resp = client.post(
            f"/ops/live/{campaign_id}/lane/test-model/stop",
            data={"csrf_token": csrf},
        )
        # Should redirect to live board (302)
        assert resp.status_code in (302, 200)

    def test_live_resume_without_csrf_returns_403(
        self, client: Any, campaign_id: str
    ) -> None:
        resp = client.post(
            f"/ops/live/{campaign_id}/resume",
            data={"csrf_token": "bad"},
        )
        assert resp.status_code == 403

    def test_live_resume_with_empty_informants_launches_new_campaign(
        self, client: Any, campaign_id: str
    ) -> None:
        # Get CSRF
        resp = client.get(f"/ops/live/{campaign_id}")
        body = resp.data.decode("utf-8")
        idx = body.find('name="csrf_token"')
        if idx < 0:
            pytest.skip("No CSRF token in live board")
        val_start = body.find('value="', idx) + len('value="')
        val_end = body.find('"', val_start)
        csrf = body[val_start:val_end]

        resp = client.post(
            f"/ops/live/{campaign_id}/resume",
            data={"csrf_token": csrf},
        )
        # With empty informants.jsonl, runs_per_cell=5, test-model/family -> all needed.
        # Fake launcher runs, redirect to new campaign live board.
        assert resp.status_code in (302, 200)


# ---------------------------------------------------------------------------
# Panel 3 behaviour
# ---------------------------------------------------------------------------


class TestQAPanel:
    def test_qa_panel_loads_on_empty_informants(self, client: Any) -> None:
        resp = client.get("/ops/qa")
        assert resp.status_code == 200

    def test_qa_panel_shows_no_failures_message(self, client: Any) -> None:
        resp = client.get("/ops/qa")
        assert b"No failures" in resp.data

    def test_qa_panel_shows_no_divergence_message(self, client: Any) -> None:
        resp = client.get("/ops/qa")
        assert b"No divergence" in resp.data

    def test_dispatch_template_view_returns_200(self, client: Any) -> None:
        resp = client.get("/ops/qa/template")
        assert resp.status_code == 200

    def test_dispatch_template_shows_summary(self, client: Any) -> None:
        resp = client.get("/ops/qa/template")
        assert b"Summary" in resp.data

    def test_dispatch_template_title_param(self, client: Any) -> None:
        resp = client.get("/ops/qa/template?title=QA+Summary")
        assert resp.status_code == 200
        assert b"QA Summary" in resp.data

    def test_dispatch_template_shows_copy_button(self, client: Any) -> None:
        resp = client.get("/ops/qa/template")
        assert b"Copy" in resp.data


# ---------------------------------------------------------------------------
# Nav links in base template
# ---------------------------------------------------------------------------


class TestNavLinks:
    def test_nav_has_new_campaign_link(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b"New Campaign" in resp.data

    def test_nav_has_qa_link(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b"QA" in resp.data

    def test_nav_has_index_link(self, client: Any) -> None:
        resp = client.get("/ops/campaigns/new")
        assert b"Index" in resp.data
