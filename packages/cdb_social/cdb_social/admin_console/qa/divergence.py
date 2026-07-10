"""QA divergence: per-record comparison of persisted qa_passed vs recomputed.

Reads informants.jsonl, re-runs run_record_checks on each record under the
current rules, and emits a DivergenceRow for every record where the persisted
qa_passed field disagrees with the recomputed result.

Boundary label (binding for all display copy):
  "persisted = qa_passed at collection time;
   recomputed = current run_record_checks rules"

No LLM imports. Read-only over informants.jsonl. Rule 14 compliant.
Rule 15 compliant: invokes existing checks unchanged, no new math.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cdb_core import InformantRecord


@dataclass
class DivergenceRow:
    """One record that diverges between persisted and recomputed QA results."""

    informant_id: str
    model_id: str
    domain_slug: str
    persisted_passed: bool       # qa_passed field as stored in informants.jsonl
    recomputed_check_nums: list[int] = field(default_factory=list)
    # Empty list means the record passes current run_record_checks rules.
    error: str | None = None     # Set when recomputation raised an exception.


def _load_run_record_checks(repo_root: Path) -> Callable[..., list[Any]]:
    """Load run_record_checks from scripts/qa_check.py via importlib."""
    qa_path = repo_root / "scripts" / "qa_check.py"
    spec = importlib.util.spec_from_file_location("_lsb_qa_check_div", qa_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot load scripts/qa_check.py from {qa_path}"
        )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.run_record_checks  # type: ignore[attr-defined,no-any-return]


def _default_repo_root() -> Path:
    """Derive repo root from this module's filesystem location.

    divergence.py lives at:
    packages/cdb_social/cdb_social/admin_console/qa/divergence.py
    parents[5] is the repo root.
    """
    return Path(__file__).resolve().parents[5]


def compute_divergence(
    informants_path: Path,
    *,
    run_checks_fn: Callable[..., list[Any]] | None = None,
    repo_root: Path | None = None,
) -> list[DivergenceRow]:
    """Compute per-record divergence between persisted qa_passed and recomputed.

    A record is divergent when:
    - persisted qa_passed=True but recomputed checks produce failures, OR
    - persisted qa_passed=False but recomputed checks produce no failures.

    Records that cannot be parsed as InformantRecord are skipped silently.
    Records where recomputation raises an exception produce a DivergenceRow
    with error set and recomputed_check_nums=[].

    Boundary label: "persisted = qa_passed at collection time;
    recomputed = current run_record_checks rules".

    Args:
        informants_path: Path to data/raw/informants.jsonl (read-only).
        run_checks_fn: Injectable run_record_checks function. When None, loads
            from scripts/qa_check.py via importlib.
        repo_root: Repo root for loading scripts/qa_check.py. Defaults to
            the repository root derived from this module's location.

    Returns:
        List of DivergenceRow for divergent records, in file order.
    """
    if not informants_path.exists():
        return []

    if run_checks_fn is None:
        root = repo_root if repo_root is not None else _default_repo_root()
        run_checks_fn = _load_run_record_checks(root)

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

    rows: list[DivergenceRow] = []

    for record in all_records:
        persisted = record.qa_passed
        error: str | None = None
        recomputed_check_nums: list[int] = []

        try:
            failures = run_checks_fn(record, all_records)
            recomputed_check_nums = [
                getattr(f, "check_num", 0) for f in failures
            ]
        except Exception as exc:
            error = str(exc)[:200]

        recomputed_passed = len(recomputed_check_nums) == 0 and error is None

        # Emit a row only when there is divergence or an error.
        if error is not None or persisted != recomputed_passed:
            rows.append(
                DivergenceRow(
                    informant_id=record.informant_id,
                    model_id=record.model_id,
                    domain_slug=record.domain_slug,
                    persisted_passed=persisted,
                    recomputed_check_nums=recomputed_check_nums,
                    error=error,
                )
            )

    return rows
