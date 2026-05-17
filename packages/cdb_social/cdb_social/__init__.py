"""cdb_social — social publishing pipeline for the Latent Structure Benchmark.

Drafts social posts from analysis findings and queues them for approval.
See ARCHITECTURE.md §4.6.
"""

from cdb_social.triggers import (
    DRIFT_MIN_ITEM_INTERSECTION,
    DRIFT_THRESHOLD,
    MIN_DIVERGENCE_DELTA,
    DriftDataInsufficientError,
    EvidenceContractError,
    StateFileMissingError,
    bootstrap_state,
    detect_divergence,
    detect_drift,
    detect_monthly_roundup,
    detect_new_domain,
    detect_new_model,
    validate_evidence_for_trigger_type,
)

__all__ = [
    "DRIFT_THRESHOLD",
    "DRIFT_MIN_ITEM_INTERSECTION",
    "MIN_DIVERGENCE_DELTA",
    "DriftDataInsufficientError",
    "StateFileMissingError",
    "EvidenceContractError",
    "bootstrap_state",
    "detect_new_model",
    "detect_new_domain",
    "detect_drift",
    "detect_divergence",
    "detect_monthly_roundup",
    "validate_evidence_for_trigger_type",
]
