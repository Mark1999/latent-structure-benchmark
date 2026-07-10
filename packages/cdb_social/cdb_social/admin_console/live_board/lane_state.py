"""Lane state discovery for the LSB ops console live board.

discover_lanes reads pidfiles from the campaign log directory and checks
/proc/{pid} to classify each lane as running, exited_ok, exited_error, or
orphaned_pidfile. Console restarts survive because all state is reconstructed
from the filesystem.

stop_lane sends SIGTERM to a running lane, waiting for it to exit, then
SIGKILL if it does not exit within the timeout.

PID-reuse guard: a running /proc/{pid} entry is only counted as the lane's
process if its cmdline contains "scripts/collect.py". Any other process
occupying the same PID after the lane has exited is classified as
orphaned_pidfile, not running.

No LLM imports. No statistical computation. Does not mutate informants.jsonl.
"""

from __future__ import annotations

import contextlib
import os
import signal
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Lane status literals
# ---------------------------------------------------------------------------

LaneStatus = Literal["running", "exited_ok", "exited_error", "orphaned_pidfile"]


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------


@dataclass
class LaneState:
    """State of one per-model collection lane."""

    model_id: str
    safe_model: str
    pid: int | None  # None when pidfile is absent or unreadable
    status: LaneStatus
    log_path: Path
    pidfile_path: Path


# ---------------------------------------------------------------------------
# /proc helpers (Linux only; runs on lsb-agent-02)
# ---------------------------------------------------------------------------


def _proc_exists(pid: int) -> bool:
    """Return True if /proc/{pid} exists (the process is alive)."""
    return Path(f"/proc/{pid}").exists()


def _proc_argv_contains(pid: int, marker: str) -> bool:
    """Return True if /proc/{pid}/cmdline contains marker.

    /proc/{pid}/cmdline is NUL-delimited. Returns False on any read error
    (process may have exited between the existence check and the read).
    """
    cmdline_path = Path(f"/proc/{pid}/cmdline")
    try:
        raw = cmdline_path.read_bytes()
    except OSError:
        return False
    argv_str = raw.replace(b"\x00", b" ").decode("utf-8", errors="replace")
    return marker in argv_str


def _is_our_lane(pid: int) -> bool:
    """Return True if /proc/{pid} is a collect.py process.

    Implements the PID-reuse guard: a new process may have inherited the PID
    of a finished lane. Only classify a live PID as "running" if its cmdline
    contains "scripts/collect.py".
    """
    if not _proc_exists(pid):
        return False
    return _proc_argv_contains(pid, "scripts/collect.py")


# ---------------------------------------------------------------------------
# Exit-code inference
# ---------------------------------------------------------------------------


def _infer_exit_status(log_path: Path) -> Literal["exited_ok", "exited_error"]:
    """Infer exit status from the last "=== exit N ===" line in the log.

    Returns "exited_ok" if the last recorded exit code is "0", or if the
    log contains no exit line (cannot determine; assume clean). Returns
    "exited_error" if the last exit code is non-zero.
    """
    if not log_path.exists():
        return "exited_ok"
    try:
        # Read last 4 KiB for efficiency; exit lines are always at the end
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "exited_ok"

    last_exit_code: str | None = None
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped.startswith("=== exit ") and stripped.endswith(" ==="):
            # Pattern: "=== exit 0 ==="
            parts = stripped.split()
            if len(parts) == 4:
                last_exit_code = parts[2]
            break

    if last_exit_code is None:
        return "exited_ok"
    return "exited_ok" if last_exit_code == "0" else "exited_error"


# ---------------------------------------------------------------------------
# Lane discovery
# ---------------------------------------------------------------------------


def discover_lanes(log_root: Path) -> list[LaneState]:
    """Discover lane states from pidfiles in log_root.

    Reads every *.pid file in log_root, checks /proc for liveness, and
    applies the PID-reuse guard. Lane states are reconstructed entirely from
    the filesystem so that console restarts survive without server-memory loss.

    Args:
        log_root: Campaign log directory (e.g. logs/ops-console/{campaign_id}/).
            Returns an empty list if the directory does not exist.

    Returns:
        List of LaneState, one per pidfile found. Order is not guaranteed.
    """
    if not log_root.exists():
        return []

    result: list[LaneState] = []

    for pidfile in sorted(log_root.glob("*.pid")):
        safe_model = pidfile.stem  # filename without .pid
        log_path = log_root / f"{safe_model}.log"

        # Derive model_id: reverse the safe-name encoding (replace _ back).
        # This is an approximation; the canonical model_id is in plan.json.
        # For display purposes only; the safe_model field is always authoritative.
        model_id = safe_model.replace("_", "/")

        # Read PID
        pid: int | None = None
        try:
            raw_pid = pidfile.read_text(encoding="utf-8").strip()
            if raw_pid.isdigit():
                pid = int(raw_pid)
        except OSError:
            pass

        if pid is None:
            status: LaneStatus = "orphaned_pidfile"
        elif _is_our_lane(pid):
            status = "running"
        elif _proc_exists(pid):
            # PID exists but cmdline does not contain collect.py: reused PID
            status = "orphaned_pidfile"
        else:
            # Process is gone; infer exit status from log
            status = _infer_exit_status(log_path)

        result.append(
            LaneState(
                model_id=model_id,
                safe_model=safe_model,
                pid=pid,
                status=status,
                log_path=log_path,
                pidfile_path=pidfile,
            )
        )

    return result


def running_model_ids(lanes: list[LaneState]) -> set[str]:
    """Return the set of model_ids whose status is 'running'."""
    return {lane.model_id for lane in lanes if lane.status == "running"}


# ---------------------------------------------------------------------------
# Lane control
# ---------------------------------------------------------------------------

# Default SIGKILL timeout: seconds to wait after SIGTERM before escalating.
_SIGKILL_TIMEOUT_S: float = 5.0


def stop_lane(
    pid: int,
    *,
    _kill: Callable[[int, int], None] | None = None,
    _proc_exists_fn: Callable[[int], bool] | None = None,
    timeout_s: float = _SIGKILL_TIMEOUT_S,
) -> None:
    """Stop a lane process: SIGTERM then SIGKILL on timeout.

    Sends SIGTERM to pid. Polls /proc/{pid} for up to timeout_s seconds.
    If the process has not exited, sends SIGKILL.

    Args:
        pid: PID of the lane to stop.
        _kill: Injectable kill function (default: os.kill). Signature:
            _kill(pid, signal_number) -> None.
        _proc_exists_fn: Injectable existence check (default: _proc_exists).
        timeout_s: Seconds to wait between SIGTERM and SIGKILL.

    Errors:
        ProcessLookupError from _kill is suppressed (process already gone).
        Other OSErrors propagate.
    """
    kill_fn = _kill if _kill is not None else os.kill
    exists_fn = _proc_exists_fn if _proc_exists_fn is not None else _proc_exists

    try:
        kill_fn(pid, signal.SIGTERM)
    except ProcessLookupError:
        return  # already gone

    # Poll until the process exits or timeout elapses
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if not exists_fn(pid):
            return
        time.sleep(0.1)

    # SIGKILL if still alive
    if exists_fn(pid):
        with contextlib.suppress(ProcessLookupError):
            kill_fn(pid, signal.SIGKILL)
