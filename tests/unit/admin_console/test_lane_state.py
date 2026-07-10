"""Unit tests for live_board/lane_state.py (T4).

No real /proc access in tests: _proc_exists and _proc_argv_contains are
indirectly tested via the injectable helpers on discover_lanes/stop_lane.
"""

from __future__ import annotations

import signal
from pathlib import Path

from cdb_social.admin_console.live_board.lane_state import (
    LaneState,
    _infer_exit_status,
    discover_lanes,
    running_model_ids,
    stop_lane,
)

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ops_console"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_pidfile(directory: Path, safe_model_name: str, pid: int | str) -> Path:
    pidfile = directory / f"{safe_model_name}.pid"
    pidfile.write_text(str(pid), encoding="utf-8")
    return pidfile


def _write_log(directory: Path, safe_model_name: str, content: str) -> Path:
    log = directory / f"{safe_model_name}.log"
    log.write_text(content, encoding="utf-8")
    return log


# ---------------------------------------------------------------------------
# _infer_exit_status
# ---------------------------------------------------------------------------


class TestInferExitStatus:
    def test_returns_ok_for_missing_log(self, tmp_path: Path) -> None:
        assert _infer_exit_status(tmp_path / "missing.log") == "exited_ok"

    def test_returns_ok_for_exit_0(self, tmp_path: Path) -> None:
        log = tmp_path / "m.log"
        log.write_text("stuff\n=== exit 0 ===\n", encoding="utf-8")
        assert _infer_exit_status(log) == "exited_ok"

    def test_returns_error_for_exit_1(self, tmp_path: Path) -> None:
        log = tmp_path / "m.log"
        log.write_text("stuff\n=== exit 1 ===\n", encoding="utf-8")
        assert _infer_exit_status(log) == "exited_error"

    def test_returns_ok_for_no_exit_line(self, tmp_path: Path) -> None:
        log = tmp_path / "m.log"
        log.write_text("no exit line here\n", encoding="utf-8")
        assert _infer_exit_status(log) == "exited_ok"

    def test_uses_last_exit_line(self, tmp_path: Path) -> None:
        log = tmp_path / "m.log"
        log.write_text("=== exit 1 ===\n=== exit 0 ===\n", encoding="utf-8")
        assert _infer_exit_status(log) == "exited_ok"


# ---------------------------------------------------------------------------
# discover_lanes (with injectable proc_exists / cmdline checks)
# ---------------------------------------------------------------------------


class TestDiscoverLanes:
    def test_returns_empty_for_missing_log_root(self, tmp_path: Path) -> None:
        result = discover_lanes(tmp_path / "nonexistent")
        assert result == []

    def test_returns_empty_for_empty_log_root(self, tmp_path: Path) -> None:
        (tmp_path / "log").mkdir()
        result = discover_lanes(tmp_path / "log")
        assert result == []

    def test_discovers_pidfile(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        _write_pidfile(log_root, "claude-opus-4-8", 99999)
        # PID 99999 is not alive (no /proc/99999 in the test env in the normal case)
        result = discover_lanes(log_root)
        assert len(result) == 1
        assert result[0].safe_model == "claude-opus-4-8"

    def test_orphaned_pidfile_for_non_numeric_pid(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        _write_pidfile(log_root, "m", "not-a-number")
        result = discover_lanes(log_root)
        assert result[0].pid is None
        assert result[0].status == "orphaned_pidfile"

    def test_exited_ok_when_log_shows_exit_0(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        # Use a PID that certainly won't be alive
        _write_pidfile(log_root, "m", 1)
        _write_log(log_root, "m", "=== exit 0 ===\n")

        import cdb_social.admin_console.live_board.lane_state as _mod
        orig_exists = _mod._proc_exists
        orig_is_our = _mod._is_our_lane
        _mod._proc_exists = lambda pid: False  # type: ignore[assignment]
        _mod._is_our_lane = lambda pid: False  # type: ignore[assignment]
        try:
            result = discover_lanes(log_root)
        finally:
            _mod._proc_exists = orig_exists  # type: ignore[assignment]
            _mod._is_our_lane = orig_is_our  # type: ignore[assignment]

        assert result[0].status == "exited_ok"

    def test_exited_error_when_log_shows_exit_nonzero(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        _write_pidfile(log_root, "m", 1)
        _write_log(log_root, "m", "=== exit 1 ===\n")

        import cdb_social.admin_console.live_board.lane_state as _mod
        orig_exists = _mod._proc_exists
        orig_is_our = _mod._is_our_lane
        _mod._proc_exists = lambda pid: False  # type: ignore[assignment]
        _mod._is_our_lane = lambda pid: False  # type: ignore[assignment]
        try:
            result = discover_lanes(log_root)
        finally:
            _mod._proc_exists = orig_exists  # type: ignore[assignment]
            _mod._is_our_lane = orig_is_our  # type: ignore[assignment]

        assert result[0].status == "exited_error"

    def test_running_when_proc_is_our_lane(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        _write_pidfile(log_root, "m", 12345)

        import cdb_social.admin_console.live_board.lane_state as _mod
        orig_is_our = _mod._is_our_lane
        _mod._is_our_lane = lambda pid: pid == 12345  # type: ignore[assignment]
        try:
            result = discover_lanes(log_root)
        finally:
            _mod._is_our_lane = orig_is_our  # type: ignore[assignment]

        assert result[0].status == "running"
        assert result[0].pid == 12345

    def test_orphaned_when_proc_exists_but_wrong_argv(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        _write_pidfile(log_root, "m", 12345)

        import cdb_social.admin_console.live_board.lane_state as _mod
        orig_exists = _mod._proc_exists
        orig_is_our = _mod._is_our_lane
        # PID exists but is NOT our lane (PID reuse guard)
        _mod._proc_exists = lambda pid: pid == 12345  # type: ignore[assignment]
        _mod._is_our_lane = lambda pid: False  # type: ignore[assignment]
        try:
            result = discover_lanes(log_root)
        finally:
            _mod._proc_exists = orig_exists  # type: ignore[assignment]
            _mod._is_our_lane = orig_is_our  # type: ignore[assignment]

        assert result[0].status == "orphaned_pidfile"

    def test_lane_state_includes_log_and_pidfile_paths(self, tmp_path: Path) -> None:
        log_root = tmp_path / "log"
        log_root.mkdir()
        _write_pidfile(log_root, "m", 99998)
        result = discover_lanes(log_root)
        assert result[0].log_path == log_root / "m.log"
        assert result[0].pidfile_path == log_root / "m.pid"


# ---------------------------------------------------------------------------
# running_model_ids
# ---------------------------------------------------------------------------


class TestRunningModelIds:
    def test_returns_running_model_ids(self) -> None:
        lanes = [
            LaneState(
                model_id="a",
                safe_model="a",
                pid=1,
                status="running",
                log_path=Path("a.log"),
                pidfile_path=Path("a.pid"),
            ),
            LaneState(
                model_id="b",
                safe_model="b",
                pid=2,
                status="exited_ok",
                log_path=Path("b.log"),
                pidfile_path=Path("b.pid"),
            ),
        ]
        assert running_model_ids(lanes) == {"a"}

    def test_empty_for_no_running_lanes(self) -> None:
        lanes = [
            LaneState(
                model_id="x",
                safe_model="x",
                pid=None,
                status="orphaned_pidfile",
                log_path=Path("x.log"),
                pidfile_path=Path("x.pid"),
            )
        ]
        assert running_model_ids(lanes) == set()


# ---------------------------------------------------------------------------
# stop_lane
# ---------------------------------------------------------------------------


class TestStopLane:
    def test_sends_sigterm_first(self) -> None:
        signals_sent: list[tuple[int, int]] = []

        def fake_kill(pid: int, sig: int) -> None:
            signals_sent.append((pid, sig))

        def fake_exists(pid: int) -> bool:
            # Gone after SIGTERM
            return False

        stop_lane(12345, _kill=fake_kill, _proc_exists_fn=fake_exists, timeout_s=0.01)
        assert (12345, signal.SIGTERM) in signals_sent

    def test_sends_sigkill_if_process_persists(self) -> None:
        signals_sent: list[tuple[int, int]] = []

        def fake_kill(pid: int, sig: int) -> None:
            signals_sent.append((pid, sig))

        # Always alive -- forces SIGKILL
        def fake_exists(pid: int) -> bool:
            return True

        stop_lane(12345, _kill=fake_kill, _proc_exists_fn=fake_exists, timeout_s=0.01)
        assert (12345, signal.SIGTERM) in signals_sent
        assert (12345, signal.SIGKILL) in signals_sent

    def test_no_sigkill_if_process_exits_after_sigterm(self) -> None:
        signals_sent: list[tuple[int, int]] = []
        call_count = [0]

        def fake_kill(pid: int, sig: int) -> None:
            signals_sent.append((pid, sig))

        def fake_exists(pid: int) -> bool:
            # Disappears on second check
            call_count[0] += 1
            return call_count[0] <= 1

        stop_lane(12345, _kill=fake_kill, _proc_exists_fn=fake_exists, timeout_s=0.5)
        assert signal.SIGKILL not in [s for _, s in signals_sent]

    def test_suppresses_process_lookup_error_on_sigterm(self) -> None:
        def fake_kill(pid: int, sig: int) -> None:
            raise ProcessLookupError(f"No process {pid}")

        # Should not raise
        stop_lane(12345, _kill=fake_kill, _proc_exists_fn=lambda pid: False)

    def test_suppresses_process_lookup_error_on_sigkill(self) -> None:
        call_count = [0]

        def fake_kill(pid: int, sig: int) -> None:
            call_count[0] += 1
            if sig == signal.SIGKILL:
                raise ProcessLookupError("gone")

        stop_lane(12345, _kill=fake_kill, _proc_exists_fn=lambda pid: True, timeout_s=0.01)
        # SIGKILL was attempted; error suppressed
        assert call_count[0] >= 2
