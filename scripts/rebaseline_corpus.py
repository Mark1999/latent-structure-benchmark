"""Re-baseline corpus under the pinned numpy==2.4.4 / scipy==1.17.1 environment.

Reads from data/raw/informants.jsonl, runs the full analysis pipeline for each
domain into a STAGING directory (out/rebaseline/<domain>/), and applies a
threshold-crossing guard before reporting results.

IMPORTANT: This script writes to out/rebaseline/ only. It does NOT overwrite
data/results/**  or  apps/dashboard/public/data/** and does NOT git-commit
anything. Staging promotion happens under separate review.

Threshold-crossing guard (binding per CDA SME verdict
docs/status/2026-05-29-rebaseline-cda-sme-verdict.md §Q3):

    T-1  romney_eigenratio crosses 5.0 (STRONG_CONSENSUS <-> WEAK_CONSENSUS)
    T-2  romney_eigenratio crosses 3.0 (WEAK_CONSENSUS <-> TURBULENT/CONTESTED)
    T-3  any cultural_centrality_scores entry flips sign
    T-4  any per-model oci crosses 3.0 while deterministic_output=False
    T-5  romney_consensus_warning flips
    T-6  consensus_type differs from prior published value

A guard trip writes out/rebaseline/THRESHOLD-CROSSING-<domain>.md and halts
that domain; it does NOT swallow the crossing as an error.

Canonicalization rule for sha256 (binding per CDA SME N7):
    sha256 is computed over json.dumps(data, sort_keys=True, indent=2,
    ensure_ascii=False) encoded as UTF-8. Sorted keys and consistent
    whitespace prevent false sha256 invalidation from JSON-formatting
    drift across Python versions.

Domain sequencing (binding per Reviewer NOTE-1):
    The all-domains run processes family → holidays → food in that fixed order.
    Family is the pilot gate.  If any domain's guard result is HALTED (a
    threshold crossing), processing stops immediately — remaining domains are
    recorded in the manifest as ``guard: "skipped: halted upstream"`` and the
    run exits.  A threshold crossing must be escalated to the CDA SME and
    Architect; the Coder is not authorized to continue past a crossing.

    Single-domain runs (--domain <name>) are unaffected by the halt logic and
    remain available for targeted re-runs after a crossing is resolved.

Usage:
    uv run python scripts/rebaseline_corpus.py
    uv run python scripts/rebaseline_corpus.py --domain family
    uv run python scripts/rebaseline_corpus.py --bootstrap-B 10  # smoke test
    uv run python scripts/rebaseline_corpus.py --smoke            # --bootstrap-B 5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD

# ---------------------------------------------------------------------------
# No LLM imports — CLAUDE.md §6 R11, ARCHITECTURE.md §4.2 binding constraint.
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent.resolve()

DEFAULT_JSONL = ROOT / "data" / "raw" / "informants.jsonl"
PRIOR_RESULTS_DIR = ROOT / "data" / "results"
STAGING_ROOT = ROOT / "out" / "rebaseline"
LOG_PATH = STAGING_ROOT / "rebaseline.log"
MANIFEST_PATH = STAGING_ROOT / "baseline_manifest.json"

# Domain -> (prior published version, analysis version for the new output,
#           similarity_collection_mode for run_pipeline(),
#           approved_slate frozenset for publication-membership filter).
# family and holidays are single-mode legacy slates (single_pass only); no
# mode filter needed. food is a mixed-mode domain (single_pass + cross_model
# consensus records coexist in the corpus after 2026-06-11 campaign widening);
# similarity_collection_mode="single_pass" is required to keep the per-model
# mat.items coherent across the slate. See FOOD-FIX-A in
# docs/status/2026-06-11-phase9b-food-campaign.md.
#
# approved_slate (N17, CDA SME 2026-07-11): curator-maintained frozenset of
# model_ids approved for publication in this rebaseline. QA answers record
# fitness; the slate answers publication membership. Conflating them means
# QA-rule changes silently redefine the published slate. An empty frozenset
# is a no-op (all QA-passed records included). Add one model_id per line
# when approving a new informant for promotion.
#
# Slate composition per domain:
#   Published basis keys: from data/results/<domain>/<prior_version>.json
#                         cultural_centrality_scores (verified 2026-07-11).
#   Batch A additions (seven): claude-opus-4-8, claude-sonnet-5,
#     openai/gpt-5.5, deepseek/deepseek-v4-pro, z-ai/glm-5.2,
#     google/gemini-3.5-flash, x-ai/grok-4.3.
#   Excluded from slate: claude-fable-5 (CDA SME R1/R2 from the batch A
#     QA verdict, 2026-07-10).
#   Pending Mark's decision (one-line add when approved):
#     qwen/qwen3.6-plus, z-ai/glm-5.1.
#
# Version bump (runbook gap, N17 companion): new_version increments so
# staging output paths do not collide with citable published versions.
# Prior published versions are loaded by the threshold guard for comparison.
# Commit body notes the runbook Step 3 DOMAIN_CONFIG-bump gap as a separate
# docs task.
_BATCH_A_ADDITIONS: frozenset[str] = frozenset({
    "claude-opus-4-8",
    "claude-sonnet-5",
    "openai/gpt-5.5",
    "deepseek/deepseek-v4-pro",
    "z-ai/glm-5.2",
    "google/gemini-3.5-flash",
    "x-ai/grok-4.3",
})

DOMAIN_CONFIG: dict[str, dict] = {
    "family": {
        "prior_version": "0.3",
        "new_version": "0.4",  # bumped: N17 runbook gap; prior 0.3 still loaded for guard
        "similarity_collection_mode": None,
        # Published basis: data/results/family/0.3.json cultural_centrality_scores
        # (15 models, verified 2026-07-11) + batch A (7 models).
        "approved_slate": frozenset({
            "claude-opus-4-5",
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "deepseek/deepseek-v3.2",
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "meta-llama/llama-4-maverick",
            "microsoft/phi-4",
            "mistralai/mistral-large-2512",
            "mistralai/mistral-small-2603",
            "openai/gpt-5.2",
            "openai/gpt-5.4",
            "openai/gpt-5.4-mini",
            "x-ai/grok-4",
            "x-ai/grok-4.20",
        }) | _BATCH_A_ADDITIONS,
        # Pending Mark's decision: qwen/qwen3.6-plus, z-ai/glm-5.1
    },
    "holidays": {
        "prior_version": "0.3",
        "new_version": "0.4",  # bumped: N17 runbook gap; prior 0.3 still loaded for guard
        "similarity_collection_mode": None,
        # Published basis: data/results/holidays/0.3.json cultural_centrality_scores
        # (14 models, no microsoft/phi-4, verified 2026-07-11) + batch A (7 models).
        "approved_slate": frozenset({
            "claude-opus-4-5",
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "deepseek/deepseek-v3.2",
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "meta-llama/llama-4-maverick",
            "mistralai/mistral-large-2512",
            "mistralai/mistral-small-2603",
            "openai/gpt-5.2",
            "openai/gpt-5.4",
            "openai/gpt-5.4-mini",
            "x-ai/grok-4",
            "x-ai/grok-4.20",
        }) | _BATCH_A_ADDITIONS,
        # Pending Mark's decision: qwen/qwen3.6-plus, z-ai/glm-5.1
    },
    "food": {
        "prior_version": "0.2",
        "new_version": "0.3",  # bumped: N17 runbook gap; prior 0.2 still loaded for guard
        "similarity_collection_mode": "single_pass",
        # Published basis: data/results/food/0.2.json cultural_centrality_scores
        # (12 models, no meta-llama, no microsoft/phi-4, no x-ai/grok-4.20,
        #  verified 2026-07-11) + batch A (7 models).
        "approved_slate": frozenset({
            "claude-opus-4-5",
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "deepseek/deepseek-v3.2",
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "mistralai/mistral-large-2512",
            "mistralai/mistral-small-2603",
            "openai/gpt-5.2",
            "openai/gpt-5.4",
            "openai/gpt-5.4-mini",
            "x-ai/grok-4",
        }) | _BATCH_A_ADDITIONS,
        # Pending Mark's decision: qwen/qwen3.6-plus, z-ai/glm-5.1
    },
}
DOMAIN_ORDER = ["family", "holidays", "food"]

ROMNEY_STRONG_WEAK_BOUNDARY: float = 5.0
ROMNEY_WEAK_TURBULENT_BOUNDARY: float = 3.0


def _setup_logging() -> logging.Logger:
    """Set up a logger writing to both stdout and the staging log file."""
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("rebaseline")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger  # already configured (resumable re-entry)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


def _git_sha() -> str:
    """Return HEAD git SHA (short)."""
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _lsb_analysis_version() -> str:
    """Return the cdb_analyze package version from its pyproject.toml."""
    toml_path = ROOT / "packages" / "cdb_analyze" / "pyproject.toml"
    try:
        text = toml_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("version"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "unknown"


def _canonical_sha256(data: dict) -> str:
    """Compute sha256 over canonicalized JSON.

    Canonicalization rule (binding per CDA SME N7):
        json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)
        encoded as UTF-8.

    Sorted keys and consistent whitespace prevent false sha256 invalidation
    from JSON-formatting drift across Python versions or pretty-printers.
    """
    canonical = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_prior_published(domain: str, version: str) -> dict:
    """Load the prior published result JSON for a domain."""
    path = PRIOR_RESULTS_DIR / domain / f"{version}.json"
    if not path.exists():
        msg = f"Prior published result not found: {path}"
        raise FileNotFoundError(msg)
    return cast(dict, json.loads(path.read_text(encoding="utf-8")))


def _run_threshold_guard(
    domain: str,
    prior: dict,
    new_data: dict,
    logger: logging.Logger,
) -> list[str]:
    """Run the CDA-SME-binding threshold-crossing guard.

    Returns a list of crossing descriptions (empty = no crossings = pass).
    """
    crossings: list[str] = []

    # T-1 / T-2: romney_eigenratio boundary crossings
    prior_ratio: float | None = prior.get("romney_eigenratio")
    new_ratio: float | None = new_data.get("romney_eigenratio")

    if prior_ratio is not None and new_ratio is not None:
        for boundary, label in [
            (ROMNEY_STRONG_WEAK_BOUNDARY, "T-1 (5.0 STRONG/WEAK boundary)"),
            (ROMNEY_WEAK_TURBULENT_BOUNDARY, "T-2 (3.0 WEAK/TURBULENT boundary)"),
        ]:
            prior_side = prior_ratio >= boundary
            new_side = new_ratio >= boundary
            if prior_side != new_side:
                crossings.append(
                    f"{label}: romney_eigenratio "
                    f"prior={prior_ratio:.6f} new={new_ratio:.6f} "
                    f"(crosses {boundary})"
                )

    # T-3: sign flip in any cultural_centrality_scores entry
    prior_ccs: dict = prior.get("cultural_centrality_scores", {})
    new_ccs: dict = new_data.get("cultural_centrality_scores", {})
    for model_id, prior_val in prior_ccs.items():
        new_val = new_ccs.get(model_id)
        if new_val is not None:
            prior_sign = prior_val >= 0
            new_sign = new_val >= 0
            if prior_sign != new_sign:
                crossings.append(
                    f"T-3 (centrality sign flip): model={model_id} "
                    f"prior={prior_val:.6f} new={new_val:.6f}"
                )

    # T-4: per-model oci crossing 3.0 when deterministic_output=False
    prior_wm: dict[str, dict] = {
        r["model_id"]: r
        for r in prior.get("within_model_results", [])
        if r.get("model_id")
    }
    new_wm: dict[str, dict] = {
        r["model_id"]: r
        for r in new_data.get("within_model_results", [])
        if r.get("model_id")
    }
    for model_id, prior_r in prior_wm.items():
        new_r = new_wm.get(model_id)
        if new_r is None:
            continue
        # Guard only applies when deterministic_output=False in either record
        prior_det = prior_r.get("deterministic_output", False)
        new_det = new_r.get("deterministic_output", False)
        if prior_det or new_det:
            continue
        prior_oci: float | None = prior_r.get("oci")
        new_oci: float | None = new_r.get("oci")
        if prior_oci is None or new_oci is None:
            continue
        prior_side = prior_oci >= OCI_LOW_CONCENTRATION_THRESHOLD
        new_side = new_oci >= OCI_LOW_CONCENTRATION_THRESHOLD
        if prior_side != new_side:
            crossings.append(
                f"T-4 (OCI crossing 3.0, deterministic=False): "
                f"model={model_id} prior_oci={prior_oci:.6f} new_oci={new_oci:.6f}"
            )

    # T-5: romney_consensus_warning flip
    prior_warn = prior.get("romney_consensus_warning")
    new_warn = new_data.get("romney_consensus_warning")
    if prior_warn is not None and new_warn is not None and prior_warn != new_warn:
        crossings.append(
            f"T-5 (romney_consensus_warning flip): "
            f"prior={prior_warn} new={new_warn}"
        )

    # T-6: consensus_type changed (belt-and-braces)
    prior_ct = prior.get("consensus_type")
    new_ct = new_data.get("consensus_type")
    if prior_ct != new_ct:
        crossings.append(
            f"T-6 (consensus_type changed): prior={prior_ct!r} new={new_ct!r}"
        )

    return crossings


def _write_crossing_report(
    domain: str,
    crossings: list[str],
    prior: dict,
    new_data: dict,
) -> Path:
    """Write a halt report for a threshold-crossing event.

    Writes out/rebaseline/THRESHOLD-CROSSING-<domain>.md and returns path.
    """
    path = STAGING_ROOT / f"THRESHOLD-CROSSING-{domain}.md"
    prior_ratio = prior.get("romney_eigenratio")
    new_ratio = new_data.get("romney_eigenratio")
    lines = [
        f"# Threshold Crossing — {domain}",
        "",
        f"**Generated:** {datetime.now(UTC).isoformat()}",
        f"**Domain:** {domain}",
        "",
        "## Summary",
        "",
        "The re-baseline guard detected one or more lede-class threshold crossings.",
        "This domain's staging output is halted. Re-route to the CDA SME and Architect",
        "before any further re-baseline work on this domain.",
        "",
        "## Crossings",
        "",
    ]
    for c in crossings:
        lines.append(f"- {c}")
    lines += [
        "",
        "## Prior published values (key fields)",
        "",
        f"- `romney_eigenratio`: {prior_ratio}",
        f"- `consensus_type`: {prior.get('consensus_type')!r}",
        f"- `romney_consensus_warning`: {prior.get('romney_consensus_warning')}",
        "",
        "## New computed values (key fields)",
        "",
        f"- `romney_eigenratio`: {new_ratio}",
        f"- `consensus_type`: {new_data.get('consensus_type')!r}",
        f"- `romney_consensus_warning`: {new_data.get('romney_consensus_warning')}",
        "",
        "## Action required",
        "",
        "A crossing is not a Coder-resolvable event. It is a finding. Re-route to",
        "the CDA SME. The Coder is not authorized to ship a lede-class change.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_numeric_delta_report(
    domain: str,
    prior: dict,
    new_data: dict,
) -> Path:
    """Write a numeric delta report comparing prior vs new values.

    Fields covered: consensus_score, romney_eigenratio, per-model centrality,
    per-model oci, MDS coord max-abs-delta. Flags anything > 1e-2.
    """
    path = STAGING_ROOT / f"numeric-deltas-{domain}.md"
    FLAG_THRESHOLD = 1e-2
    lines = [
        f"# Numeric Deltas — {domain}",
        "",
        f"**Generated:** {datetime.now(UTC).isoformat()}",
        "",
        "Fields with |delta| > 1e-2 are flagged with **FLAG**.",
        "",
    ]

    def _delta_row(field: str, prior_val: object, new_val: object) -> str:
        if isinstance(prior_val, (int, float)) and isinstance(new_val, (int, float)):
            delta = float(new_val) - float(prior_val)
            flag = " **FLAG**" if abs(delta) > FLAG_THRESHOLD else ""
            return (
                f"| `{field}` | {prior_val:.6f} | {new_val:.6f} "
                f"| {delta:+.6f}{flag} |"
            )
        return f"| `{field}` | {prior_val!r} | {new_val!r} | — |"

    lines += [
        "## Scalar fields",
        "",
        "| Field | Prior | New | Delta |",
        "|---|---|---|---|",
    ]

    for field in ("consensus_score", "romney_eigenratio"):
        pv = prior.get(field)
        nv = new_data.get(field)
        lines.append(_delta_row(field, pv, nv))

    lines += ["", "## Per-model centrality scores", ""]
    prior_ccs = prior.get("cultural_centrality_scores", {})
    new_ccs = new_data.get("cultural_centrality_scores", {})
    all_models = sorted(set(list(prior_ccs) + list(new_ccs)))
    if all_models:
        lines += ["| Model | Prior | New | Delta |", "|---|---|---|---|"]
        for mid in all_models:
            pv = prior_ccs.get(mid)
            nv = new_ccs.get(mid)
            lines.append(_delta_row(mid, pv, nv))

    lines += ["", "## Per-model OCI", ""]
    prior_wm = {
        r["model_id"]: r
        for r in prior.get("within_model_results", [])
        if r.get("model_id")
    }
    new_wm = {
        r["model_id"]: r
        for r in new_data.get("within_model_results", [])
        if r.get("model_id")
    }
    all_wm_models = sorted(set(list(prior_wm) + list(new_wm)))
    if all_wm_models:
        lines += ["| Model | Prior OCI | New OCI | Delta |", "|---|---|---|---|"]
        for mid in all_wm_models:
            pv = prior_wm.get(mid, {}).get("oci")
            nv = new_wm.get(mid, {}).get("oci")
            lines.append(_delta_row(mid, pv, nv))

    # MDS coord max-abs-delta
    prior_mds = prior.get("mds_coordinates", {})
    new_mds = new_data.get("mds_coordinates", {})
    mds_deltas: list[float] = []
    for mid in set(list(prior_mds) + list(new_mds)):
        pc = prior_mds.get(mid)
        nc = new_mds.get(mid)
        if pc is not None and nc is not None:
            # coordinates may be stored as list [x, y] or dict {"x": ..., "y": ...}
            if isinstance(pc, (list, tuple)) and isinstance(nc, (list, tuple)):
                for pv, nv in zip(pc, nc, strict=False):
                    mds_deltas.append(abs(float(nv) - float(pv)))
            elif isinstance(pc, dict) and isinstance(nc, dict):
                for k in ("x", "y"):
                    if k in pc and k in nc:
                        mds_deltas.append(abs(float(nc[k]) - float(pc[k])))

    lines += ["", "## MDS coordinates max-abs-delta", ""]
    if mds_deltas:
        max_delta = max(mds_deltas)
        flag = " **FLAG**" if max_delta > FLAG_THRESHOLD else ""
        lines.append(f"- Max |delta| across all models and axes: {max_delta:.6f}{flag}")
    else:
        lines.append("- No MDS coordinate data available for comparison.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _load_manifest() -> dict:
    """Load the existing staging manifest, or return an empty scaffold."""
    if MANIFEST_PATH.exists():
        try:
            return cast(dict, json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "numpy_version": "",
        "scipy_version": "",
        "python_version": "",
        "lsb_analysis_version": "",
        "platform": "",
        "git_sha": "",
        "generated_at_utc": "",
        "domains": {},
    }


def _save_manifest(manifest: dict) -> None:
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _is_domain_complete(domain: str, manifest: dict) -> bool:
    """Return True if this domain's staging output exists and is marked complete."""
    domain_manifest = manifest.get("domains", {}).get(domain, {})
    if domain_manifest.get("guard") not in ("pass", "halted"):
        return False
    staging_dir = STAGING_ROOT / domain
    version = DOMAIN_CONFIG[domain]["new_version"]
    staging_path = staging_dir / f"{version}.json"
    return staging_path.exists()


def rebaseline_domain(
    domain: str,
    bootstrap_B: int,
    logger: logging.Logger,
    manifest: dict,
) -> dict:
    """Run re-baseline for one domain and return the updated manifest entry.

    Reads from data/raw/informants.jsonl, runs run_pipeline() + write_result()
    into out/rebaseline/<domain>/, runs the threshold guard, writes delta
    report, and returns a manifest entry dict.

    Does NOT touch data/results/ or apps/dashboard/public/data/.
    """
    cfg = DOMAIN_CONFIG[domain]
    prior_version = cfg["prior_version"]
    new_version = cfg["new_version"]
    staging_dir = STAGING_ROOT / domain
    staging_dir.mkdir(parents=True, exist_ok=True)
    staging_path = staging_dir / f"{new_version}.json"

    # similarity_collection_mode from DOMAIN_CONFIG; None for single-mode
    # legacy slates (family/holidays), "single_pass" for mixed-mode domains
    # (food). This value is passed to run_pipeline() to constrain the
    # similarity basis to a coherent within-mode item source across the slate.
    # See FOOD-FIX-A in docs/status/2026-06-11-phase9b-food-campaign.md.
    similarity_collection_mode: str | None = cfg.get("similarity_collection_mode")

    logger.info("=== [%s] START ===", domain)
    if similarity_collection_mode is not None:
        logger.info(
            "[%s] similarity_collection_mode=%r (mixed-mode domain)",
            domain,
            similarity_collection_mode,
        )

    # Late imports — keep module importable without uv environment active
    from cdb_analyze.pipeline import load_records, run_pipeline, write_result  # noqa: PLC0415

    # Load records (per-record re-QA with N15 partition; N16 guard fires if
    # any persisted-True record fails per-record re-QA).
    records = load_records(DEFAULT_JSONL, domain)
    if not records:
        msg = f"No QA-passed records found for domain '{domain}' in {DEFAULT_JSONL}"
        raise RuntimeError(msg)

    logger.info("[%s] Loaded %d records", domain, len(records))

    # N17 approved-slate filter: restrict corpus to curator-approved model_ids.
    # QA answers record fitness; the slate answers publication membership.
    # An empty approved_slate is a no-op (all QA-passed records included).
    approved_slate: frozenset[str] = cfg.get("approved_slate", frozenset())
    if approved_slate:
        pre_slate_count = len(records)
        dropped_by_model: dict[str, int] = {}
        for r in records:
            if r.model_id not in approved_slate:
                dropped_by_model[r.model_id] = dropped_by_model.get(r.model_id, 0) + 1
        records = [r for r in records if r.model_id in approved_slate]
        post_slate_count = len(records)
        n_dropped = pre_slate_count - post_slate_count
        if n_dropped > 0:
            for model_id, cnt in sorted(dropped_by_model.items()):
                logger.info(
                    "[%s] Slate filter: excluded %d record(s) for model %r "
                    "(not in approved_slate; add to DOMAIN_CONFIG to include).",
                    domain, cnt, model_id,
                )
            logger.info(
                "[%s] Slate filter: %d -> %d records (%d excluded across %d model(s)).",
                domain, pre_slate_count, post_slate_count,
                n_dropped, len(dropped_by_model),
            )
        else:
            logger.info(
                "[%s] Slate filter: all %d records are in approved_slate.",
                domain, post_slate_count,
            )

    # Run analysis pipeline into staging dir
    logger.info("[%s] Running pipeline (bootstrap_B=%d)...", domain, bootstrap_B)
    result = run_pipeline(
        records,
        analysis_version=new_version,
        n_bootstrap=bootstrap_B,
        similarity_collection_mode=similarity_collection_mode,
    )
    out_path = write_result(result, STAGING_ROOT)
    logger.info("[%s] Wrote staging output: %s", domain, out_path)

    # Compute canonicalized sha256 over the staged result
    staged_data = json.loads(staging_path.read_text(encoding="utf-8"))
    sha256 = _canonical_sha256(staged_data)
    logger.info("[%s] sha256 (canonicalized): %s", domain, sha256)

    # Load prior published values for guard comparison
    try:
        prior = _load_prior_published(domain, prior_version)
    except FileNotFoundError:
        logger.warning("[%s] Prior published result not found — guard skipped", domain)
        prior = {}

    # Run threshold-crossing guard
    crossings = _run_threshold_guard(domain, prior, staged_data, logger)
    if crossings:
        logger.warning(
            "[%s] THRESHOLD CROSSING DETECTED (%d crossings) — halting domain",
            domain,
            len(crossings),
        )
        for c in crossings:
            logger.warning("[%s]   %s", domain, c)
        crossing_path = _write_crossing_report(domain, crossings, prior, staged_data)
        logger.warning("[%s] Crossing report: %s", domain, crossing_path)
        guard_status = "halted"
    else:
        logger.info("[%s] Guard: PASS — no lede-class threshold crossings", domain)
        guard_status = "pass"

    # Write numeric delta report regardless of guard status
    if prior:
        delta_path = _write_numeric_delta_report(domain, prior, staged_data)
        logger.info("[%s] Delta report: %s", domain, delta_path)

    logger.info("=== [%s] END guard=%s ===", domain, guard_status)

    return {
        "sha256": sha256,
        "model_count": len(result.mds_coordinates),
        "bootstrap_B": bootstrap_B,
        "guard": guard_status,
        "new_version": new_version,
        "prior_version": prior_version,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Re-baseline LSB corpus under pinned numpy/scipy. "
            "Writes to out/rebaseline/ only — does NOT touch data/results/ or "
            "apps/dashboard/public/data/ and does NOT git-commit anything."
        ),
    )
    parser.add_argument(
        "--domain",
        choices=list(DOMAIN_CONFIG),
        default=None,
        help="Run one domain only. Default: all (family, then holidays, then food).",
    )
    parser.add_argument(
        "--bootstrap-B",
        type=int,
        default=500,
        help="Bootstrap resamples (default: 500 for full run).",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Smoke-test mode: --bootstrap-B 5, one domain (family by default).",
    )
    args = parser.parse_args()

    if args.smoke:
        args.bootstrap_B = 5
        if args.domain is None:
            args.domain = "family"

    logger = _setup_logging()
    logger.info(
        "rebaseline_corpus.py starting — bootstrap_B=%d domain=%s",
        args.bootstrap_B,
        args.domain or "all",
    )

    # Build manifest header (set once at start; domains updated as they complete)
    import numpy as np  # noqa: PLC0415
    import scipy  # noqa: PLC0415

    manifest = _load_manifest()
    manifest.update({
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "python_version": sys.version,
        "lsb_analysis_version": _lsb_analysis_version(),
        "platform": platform.platform(),
        "git_sha": _git_sha(),
        "generated_at_utc": datetime.now(UTC).isoformat(),
    })
    if "domains" not in manifest:
        manifest["domains"] = {}
    _save_manifest(manifest)

    domains_to_run = [args.domain] if args.domain else DOMAIN_ORDER

    halted_domains: list[str] = []

    for domain in domains_to_run:
        # Idempotency: skip if already complete
        if _is_domain_complete(domain, manifest):
            logger.info("[%s] Already complete in manifest — skipping", domain)
            continue

        try:
            domain_entry = rebaseline_domain(
                domain, args.bootstrap_B, logger, manifest,
            )
        except Exception:
            logger.exception("[%s] Unexpected error — aborting this domain", domain)
            manifest["domains"][domain] = {"guard": "error"}
            _save_manifest(manifest)
            halted_domains.append(domain)
            continue

        manifest["domains"][domain] = domain_entry
        _save_manifest(manifest)

        if domain_entry["guard"] == "halted":
            halted_domains.append(domain)
            # NOTE-1 (Reviewer binding): a threshold crossing on any domain stops
            # the all-domains run immediately.  Family is the pilot gate; a halt
            # on family must block holidays and food.  Record every un-processed
            # domain as skipped so the manifest outcome is unambiguous.
            remaining = [
                d for d in domains_to_run
                if d not in manifest.get("domains", {})
            ]
            for skipped in remaining:
                logger.warning(
                    "[%s] Skipped — upstream domain '%s' halted on threshold crossing",
                    skipped,
                    domain,
                )
                manifest["domains"][skipped] = {"guard": "skipped: halted upstream"}
            _save_manifest(manifest)
            break

    # Final summary
    logger.info("=== SUMMARY ===")
    for domain in domains_to_run:
        entry = manifest.get("domains", {}).get(domain, {})
        logger.info(
            "  %s: guard=%s bootstrap_B=%s model_count=%s sha256=%s",
            domain,
            entry.get("guard", "not_run"),
            entry.get("bootstrap_B"),
            entry.get("model_count"),
            (entry.get("sha256") or "")[:12] + "...",
        )

    if halted_domains:
        logger.warning(
            "HALTED domains (threshold crossings or errors): %s",
            ", ".join(halted_domains),
        )
        logger.warning(
            "See out/rebaseline/THRESHOLD-CROSSING-<domain>.md for each halted domain."
        )
        logger.warning("Re-route to the CDA SME and Architect before continuing.")

    logger.info("Manifest: %s", MANIFEST_PATH)
    logger.info("Staging root: %s", STAGING_ROOT)

    # Non-zero exit only on unexpected errors, not on expected guard halts
    error_domains = [
        d for d in domains_to_run
        if manifest.get("domains", {}).get(d, {}).get("guard") == "error"
    ]
    return 1 if error_domains else 0


if __name__ == "__main__":
    sys.exit(main())
