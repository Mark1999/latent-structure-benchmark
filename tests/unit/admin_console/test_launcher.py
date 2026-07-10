"""Unit tests for campaign_runner/launcher.py (T3).

No real subprocess. _spawn is injected via FakeSpawn. No real API calls.
tmp_path only for filesystem writes.
"""

from __future__ import annotations

import json
import stat
from pathlib import Path
from typing import Any

from cdb_social.admin_console.campaign_runner.launcher import (
    SubprocessLaneLauncher,
    _render_lane_sh,
    _safe_model,
    _write_pidfile_atomic,
)
from cdb_social.admin_console.campaign_runner.planner import (
    CampaignPlan,
    CellShortfall,
    ModelInfo,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_plan(
    cells: list[tuple[str, str, int, int]],
    campaign_id: str = "test-campaign",
    runs_per_cell: int = 5,
) -> CampaignPlan:
    """Build a CampaignPlan from (model_id, domain, passed, needed) tuples."""
    models = list({
        ModelInfo(model_id=m, display_name=m, family="test", records=0)
        for m, _, _, _ in cells
    })
    domain_slugs = list(dict.fromkeys(d for _, d, _, _ in cells))
    return CampaignPlan(
        campaign_id=campaign_id,
        models=models,
        domain_slugs=domain_slugs,
        runs_per_cell=runs_per_cell,
        cells=[
            CellShortfall(model_id=m, domain_slug=d, passed=p, needed=n)
            for m, d, p, n in cells
        ],
    )


class FakeProcess:
    """Fake subprocess.Popen return value."""

    def __init__(self, pid: int = 12345) -> None:
        self.pid = pid


class SpawnRecorder:
    """Records all _spawn calls for assertion."""

    def __init__(self, start_pid: int = 12345) -> None:
        self._pid = start_pid
        self.calls: list[dict[str, Any]] = []

    def __call__(self, argv: list[str], **kwargs: Any) -> FakeProcess:
        self.calls.append({"argv": list(argv), **kwargs})
        proc = FakeProcess(pid=self._pid)
        self._pid += 1
        return proc


# ---------------------------------------------------------------------------
# _safe_model
# ---------------------------------------------------------------------------


class TestSafeModel:
    def test_replaces_slash_with_underscore(self) -> None:
        assert _safe_model("z-ai/glm-5.2") == "z-ai_glm-5.2"

    def test_no_slash_unchanged(self) -> None:
        assert _safe_model("claude-opus-4-8") == "claude-opus-4-8"


# ---------------------------------------------------------------------------
# _write_pidfile_atomic
# ---------------------------------------------------------------------------


class TestWritePidfileAtomic:
    def test_writes_pid_to_file(self, tmp_path: Path) -> None:
        pidfile = tmp_path / "model.pid"
        _write_pidfile_atomic(pidfile, 99999)
        assert pidfile.read_text(encoding="utf-8") == "99999"

    def test_no_tmp_file_left_after_write(self, tmp_path: Path) -> None:
        pidfile = tmp_path / "model.pid"
        _write_pidfile_atomic(pidfile, 99999)
        assert not (tmp_path / "model.pid.tmp").exists()

    def test_overwrites_existing_pidfile(self, tmp_path: Path) -> None:
        pidfile = tmp_path / "model.pid"
        pidfile.write_text("11111", encoding="utf-8")
        _write_pidfile_atomic(pidfile, 22222)
        assert pidfile.read_text(encoding="utf-8") == "22222"


# ---------------------------------------------------------------------------
# _render_lane_sh
# ---------------------------------------------------------------------------


class TestRenderLaneSh:
    def test_contains_set_pipefail(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        sh = _render_lane_sh(plan, tmp_path / "log", tmp_path)
        assert "set -uo pipefail" in sh

    def test_contains_campaign_id(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)], campaign_id="cid-abc")
        sh = _render_lane_sh(plan, tmp_path / "log", tmp_path)
        assert "cid-abc" in sh

    def test_contains_uv_run_collect(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        sh = _render_lane_sh(plan, tmp_path / "log", tmp_path)
        assert "uv run python" in sh
        assert "collect.py" in sh

    def test_shebang_present(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        sh = _render_lane_sh(plan, tmp_path / "log", tmp_path)
        assert sh.startswith("#!/usr/bin/env bash")

    def test_lanes_done_sentinel(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        sh = _render_lane_sh(plan, tmp_path / "log", tmp_path)
        assert "lanes done" in sh


# ---------------------------------------------------------------------------
# SubprocessLaneLauncher
# ---------------------------------------------------------------------------


class TestSubprocessLaneLauncher:
    def test_writes_plan_json(self, tmp_path: Path) -> None:
        plan = _make_plan([("claude-opus-4-8", "family", 2, 3)])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        plan_json = log_root / "plan.json"
        assert plan_json.exists()
        data = json.loads(plan_json.read_text(encoding="utf-8"))
        assert data["campaign_id"] == "test-campaign"
        assert len(data["cells"]) == 1
        assert data["cells"][0]["model_id"] == "claude-opus-4-8"
        assert data["cells"][0]["needed"] == 3

    def test_writes_plan_txt(self, tmp_path: Path) -> None:
        plan = _make_plan([
            ("m1", "family", 0, 5),
            ("m1", "holidays", 3, 2),
        ])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        plan_txt = log_root / "plan.txt"
        assert plan_txt.exists()
        lines = [ln for ln in plan_txt.read_text(encoding="utf-8").splitlines() if ln]
        assert len(lines) == 2

    def test_writes_lane_sh(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        lane_sh = log_root / "lane.sh"
        assert lane_sh.exists()
        content = lane_sh.read_text(encoding="utf-8")
        assert "#!/usr/bin/env bash" in content

    def test_lane_sh_is_executable(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        lane_sh = log_root / "lane.sh"
        mode = lane_sh.stat().st_mode
        assert mode & stat.S_IXUSR  # owner-executable

    def test_spawns_one_process_per_model(self, tmp_path: Path) -> None:
        plan = _make_plan([
            ("model-a", "family", 0, 5),
            ("model-a", "holidays", 0, 5),
            ("model-b", "family", 0, 5),
        ])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        launcher.launch(plan, tmp_path / "log", tmp_path)
        assert len(recorder.calls) == 2

    def test_spawn_called_with_bash(self, tmp_path: Path) -> None:
        plan = _make_plan([("claude-opus-4-8", "family", 0, 5)])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        launcher.launch(plan, tmp_path / "log", tmp_path)

        assert len(recorder.calls) == 1
        argv = recorder.calls[0]["argv"]
        assert argv[0] == "bash"

    def test_spawn_argv_contains_collect_py(self, tmp_path: Path) -> None:
        plan = _make_plan([("claude-opus-4-8", "family", 0, 5)])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        launcher.launch(plan, tmp_path / "log", tmp_path)

        argv = recorder.calls[0]["argv"]
        full_cmd = " ".join(argv)
        assert "collect.py" in full_cmd
        assert "family" in full_cmd

    def test_spawn_called_with_start_new_session(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        launcher.launch(plan, tmp_path / "log", tmp_path)

        assert recorder.calls[0]["start_new_session"] is True

    def test_writes_pidfile_per_model(self, tmp_path: Path) -> None:
        plan = _make_plan([
            ("claude-opus-4-8", "family", 0, 5),
            ("z-ai/glm-5.2", "family", 0, 5),
        ])
        recorder = SpawnRecorder(start_pid=55000)
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        assert (log_root / "claude-opus-4-8.pid").exists()
        assert (log_root / "z-ai_glm-5.2.pid").exists()

    def test_pidfile_content_matches_spawn_pid(self, tmp_path: Path) -> None:
        plan = _make_plan([("m", "d", 0, 5)])
        recorder = SpawnRecorder(start_pid=77777)
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        pid_content = (log_root / "m.pid").read_text(encoding="utf-8")
        assert pid_content == "77777"

    def test_skips_models_with_no_work(self, tmp_path: Path) -> None:
        # model-b has all cells needed=0
        plan = _make_plan([
            ("model-a", "family", 0, 5),
            ("model-b", "family", 5, 0),
        ])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        launcher.launch(plan, tmp_path / "log", tmp_path)

        # Only model-a should be spawned
        assert len(recorder.calls) == 1

    def test_plan_json_excludes_zero_needed_cells(self, tmp_path: Path) -> None:
        plan = _make_plan([
            ("m1", "family", 0, 5),
            ("m1", "holidays", 5, 0),
        ])
        recorder = SpawnRecorder()
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        log_root = tmp_path / "log"
        launcher.launch(plan, log_root, tmp_path)

        data = json.loads((log_root / "plan.json").read_text(encoding="utf-8"))
        assert all(c["needed"] > 0 for c in data["cells"])

    def test_deterministic_plan_json_for_identical_plans(self, tmp_path: Path) -> None:
        plan1 = _make_plan([("m", "d", 2, 3)], campaign_id="cid")
        plan2 = _make_plan([("m", "d", 2, 3)], campaign_id="cid")
        log1 = tmp_path / "log1"
        log2 = tmp_path / "log2"
        SubprocessLaneLauncher(_spawn=SpawnRecorder()).launch(plan1, log1, tmp_path)
        SubprocessLaneLauncher(_spawn=SpawnRecorder()).launch(plan2, log2, tmp_path)
        assert (log1 / "plan.json").read_text(encoding="utf-8") == (
            log2 / "plan.json"
        ).read_text(encoding="utf-8")

    def test_returns_model_to_pid_mapping(self, tmp_path: Path) -> None:
        plan = _make_plan([
            ("model-a", "family", 0, 5),
            ("model-b", "family", 0, 5),
        ])
        recorder = SpawnRecorder(start_pid=10001)
        launcher = SubprocessLaneLauncher(_spawn=recorder)
        pids = launcher.launch(plan, tmp_path / "log", tmp_path)
        assert set(pids.keys()) == {"model-a", "model-b"}
        assert all(isinstance(v, int) for v in pids.values())
