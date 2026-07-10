"""QA histogram: bucket run_record_checks failures by check number per model.

Reads informants.jsonl and invokes run_record_checks (module import, not
shelled) to count failures per (model_id, check_num).

No LLM imports. Read-only over informants.jsonl. Rule 14 compliant.
Rule 15 compliant: invokes existing checks unchanged, no new math.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cdb_core import InformantRecord


@dataclass
class HistogramRow:
    """One bucket in the check-failure histogram."""

    model_id: str
    check_num: int
    count: int


def _load_run_record_checks(repo_root: Path) -> Callable[..., list[Any]]:
    """Load run_record_checks from scripts/qa_check.py via importlib.

    Uses importlib.util.spec_from_file_location so that no sys.path mutation
    is needed. The loaded module is ephemeral; only run_record_checks is
    returned.
    """
    qa_path = repo_root / "scripts" / "qa_check.py"
    spec = importlib.util.spec_from_file_location("_lsb_qa_check_hist", qa_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot load scripts/qa_check.py from {qa_path}"
        )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.run_record_checks  # type: ignore[attr-defined,no-any-return]


def _default_repo_root() -> Path:
    """Derive repo root from this module's filesystem location.

    histogram.py lives at:
    packages/cdb_social/cdb_social/admin_console/qa/histogram.py
    parents[5] is the repo root.
    """
    return Path(__file__).resolve().parents[5]


def bucket_failures(
    informants_path: Path,
    *,
    run_checks_fn: Callable[..., list[Any]] | None = None,
    repo_root: Path | None = None,
) -> list[HistogramRow]:
    """Read informants.jsonl and bucket run_record_checks failures.

    Results are grouped by (model_id, check_num) and returned as a sorted
    list of HistogramRow. Returns [] if informants.jsonl is absent or empty,
    or if no failures exist.

    Args:
        informants_path: Path to data/raw/informants.jsonl (read-only).
        run_checks_fn: Injectable run_record_checks function. When None, loads
            from scripts/qa_check.py via importlib. Signature must match
            run_record_checks(record, all_records) -> list[QAFailure-like].
        repo_root: Repo root for loading scripts/qa_check.py. Defaults to
            the repository root derived from this module's location.
    """
    if not informants_path.exists():
        return []

    if run_checks_fn is None:
        root = repo_root if repo_root is not None else _default_repo_root()
        run_checks_fn = _load_run_record_checks(root)

    # Load all records (needed for check_2 cross-run uniqueness).
    try:
        text = informants_path.read_text(encoding="utf-8")
    except OSError:
        return []

    all_records: list[InformantRecord] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            all_records.append(InformantRecord.model_validate_json(line))
        except Exception:
            continue

    if not all_records:
        return []

    # Bucket failures by (model_id, check_num).
    counts: dict[tuple[str, int], int] = {}
    for record in all_records:
        try:
            failures = run_checks_fn(record, all_records)
        except Exception:
            continue
        for failure in failures:
            check_num: int = getattr(failure, "check_num", 0)
            key = (record.model_id, check_num)
            counts[key] = counts.get(key, 0) + 1

    return sorted(
        [
            HistogramRow(model_id=mid, check_num=chk, count=cnt)
            for (mid, chk), cnt in counts.items()
        ],
        key=lambda r: (r.model_id, r.check_num),
    )
