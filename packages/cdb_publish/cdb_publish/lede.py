"""Template-based lede generator (Phase 5).

Produces the key-finding strip's lede sentence for a given DomainResult,
per docs/status/2026-05-09-phase5-architect-plan.md §1.3 + T2.

The LLM-based variant is Phase 6. This module must NOT import any LLM
client library — Phase 5 is template-based per plan §1.3.

Per CLAUDE.md §6 R11 the LLM-analysis boundary is in cdb_analyze;
cdb_publish is allowed to call LLMs in principle (per ARCHITECTURE.md
§4.2). T2 must NOT call any LLM — Phase 5 is template-based per §1.3.

Branch logic (Q1 binding — schema-literal ConsensusType values only):
  Six ConsensusType values: STRONG_CONSENSUS, WEAK_CONSENSUS,
  SUBCULTURAL, TURBULENT, CONTESTED, DETERMINISTIC.
  "NO_CONSENSUS" does not exist and must never appear here.

Strong-consensus sub-branches (Q5 binding — R1-b count):
  - all_deterministic: all visible models have deterministic_output=True
  - strong_consensus_homogeneous: STRONG_CONSENSUS, no R1-b models
  - strong_consensus_with_low_oci: STRONG_CONSENSUS, 1 <= n_low_oci < majority
  - strong_consensus_majority_low_oci: STRONG_CONSENSUS, n_low_oci > N/2

R1-b definition: deterministic_output=False AND oci < OCI_LOW_CONCENTRATION_THRESHOLD

Number formatting:
  Smith's S to 2 decimal places (e.g. "0.71")
  CI bounds to 2 decimal places (e.g. "[0.50, 0.91]")
"""

from __future__ import annotations

from cdb_core.schemas import DomainResult

from cdb_publish.templates.lede_v1 import LEDE_VERSION, PATTERNS  # noqa: F401

# Source-of-truth OCI threshold per DESIGN_SYSTEM.md §3.3.5 item 7.
# The dashboard's apps/dashboard/src/config/analysis.ts exports the same
# value. Both must be updated together if the threshold is revised.
OCI_LOW_CONCENTRATION_THRESHOLD: float = 3.0


def generate_lede(result: DomainResult) -> str:
    """Generate the lede sentence for a domain result.

    Parameters
    ----------
    result:
        A fully populated DomainResult (as loaded from data/results/).

    Returns
    -------
    str
        A single prose string suitable for the key-finding strip.
        Output is deterministic: same input always produces the same
        output (acceptance criterion (a)).
    """
    pattern_name = _select_pattern(result)
    template = PATTERNS[pattern_name]
    return _format_lede(template, result, pattern_name)


def _count_low_oci_models(result: DomainResult) -> int:
    """Count models with low output concentration (R1-b state).

    R1-b: deterministic_output=False AND oci < OCI_LOW_CONCENTRATION_THRESHOLD.
    """
    return sum(
        1
        for wmr in result.within_model_results
        if not wmr.deterministic_output and wmr.oci < OCI_LOW_CONCENTRATION_THRESHOLD
    )


def _all_deterministic(result: DomainResult) -> bool:
    """Return True when every visible model has deterministic_output=True.

    'Visible' means appearing in mds_coordinates. within_model_results
    provides the R1-state metadata; we join on model_id.
    """
    visible_ids = set(result.mds_coordinates.keys())
    if not visible_ids:
        return False

    # Build a lookup of model_id -> deterministic_output from within_model_results
    det_lookup: dict[str, bool] = {
        wmr.model_id: wmr.deterministic_output
        for wmr in result.within_model_results
    }

    # A model in mds_coordinates with no within_model_result entry is
    # treated as non-deterministic (conservative fallback).
    return all(det_lookup.get(mid, False) for mid in visible_ids)


def _select_pattern(result: DomainResult) -> str:
    """Select the pattern name for this DomainResult.

    Priority order:
    1. all_deterministic — overrides consensus_type when every visible
       model is R1-c. Also handles consensus_type == "DETERMINISTIC".
    2. STRONG_CONSENSUS sub-branches (Q5):
       - majority_low_oci if > 50% models are R1-b
       - with_low_oci if >= 1 model is R1-b
       - homogeneous if no R1-b models
    3. WEAK_CONSENSUS, SUBCULTURAL, TURBULENT, CONTESTED — one branch each.
    """
    # --- all-deterministic check (also catches consensus_type="DETERMINISTIC") ---
    if result.consensus_type == "DETERMINISTIC" or _all_deterministic(result):
        return "all_deterministic"

    n = len(result.mds_coordinates)

    if result.consensus_type == "STRONG_CONSENSUS":
        n_low_oci = _count_low_oci_models(result)
        if n_low_oci > n / 2:
            return "strong_consensus_majority_low_oci"
        if n_low_oci >= 1:
            return "strong_consensus_with_low_oci"
        return "strong_consensus_homogeneous"

    if result.consensus_type == "WEAK_CONSENSUS":
        return "weak_consensus"

    if result.consensus_type == "SUBCULTURAL":
        return "subcultural"

    if result.consensus_type == "TURBULENT":
        return "turbulent"

    if result.consensus_type == "CONTESTED":
        return "contested"

    # consensus_type is None or an unexpected value — fall back to a
    # descriptive pattern that avoids strong claims.
    return "turbulent"


def _format_lede(
    template: str,
    result: DomainResult,
    pattern_name: str,
) -> str:
    """Fill in the template placeholders.

    Placeholders:
      {n}         — len(mds_coordinates)
      {domain}    — domain_slug
      {s}         — consensus_score formatted to 2 decimals
      {lo}        — consensus_ci[0] formatted to 2 decimals
      {hi}        — consensus_ci[1] formatted to 2 decimals
      {n_low_oci} — count of R1-b models (only used in *_with_low_oci patterns)

    The all_deterministic pattern has no numeric placeholders; it is
    returned verbatim (byte-identical to DESIGN_SYSTEM.md §3.3.5 item 6).
    """
    if pattern_name == "all_deterministic":
        # Verbatim copy — no substitution needed.
        return template

    n = len(result.mds_coordinates)
    s = f"{result.consensus_score:.2f}"
    lo = f"{result.consensus_ci[0]:.2f}"
    hi = f"{result.consensus_ci[1]:.2f}"
    n_low_oci = _count_low_oci_models(result)

    return template.format(
        n=n,
        domain=result.domain_slug,
        s=s,
        lo=lo,
        hi=hi,
        n_low_oci=n_low_oci,
    )
