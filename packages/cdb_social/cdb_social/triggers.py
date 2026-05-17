"""Social post trigger detectors — pure functions over the published results store.

Each ``detect_*`` function returns a list of ``SocialTrigger`` objects that the
cron orchestrator uses to decide whether to draft a post.  The functions are
stateless computation over (published data, on-disk state files); they do not
call any LLM and do not write to ``data/raw/`` or ``data/processed/``.  All
state is in ``out/social/state/`` (see ARCHITECTURE.md §4.6 and the T1 schema
in ``cdb_core/schemas.py``).

Ordering constraint for the orchestrator
-----------------------------------------
``detect_new_model`` MUST be called before ``detect_divergence`` so that the
new-model exclusion list is available for the divergence computation.  The
orchestrator passes the result of ``detect_new_model`` into
``detect_divergence`` via the ``new_models_this_run`` argument.

Trigger dedupe
--------------
Every emitted ``SocialTrigger`` carries a ``dedupe_key`` that is stable across
``drafter_version`` and ``prompt_version`` bumps.  If the operator wants to
re-fire a posted event under a new drafter prompt (e.g., to re-publish under a
v2 prompt that produces clearer language), the manual procedure is:

1. Remove the relevant key from ``out/social/state/posted_dedupe_keys.json``.
2. The next cron run will re-fire the trigger (the ``detect_*`` function
   re-emits the SocialTrigger; the orchestrator no longer skips it because the
   key is absent from the dedupe state).
3. A new ``SocialDraft`` is produced with the bumped ``prompt_version``.

See ``cdb_core/schemas.py`` docstring on ``SocialTrigger.dedupe_key`` for the
construction formula.  See
``docs/status/2026-05-17-phase7-T1-cda-sme-verdict.md`` §5.8 for the
methodological rationale.

State-file semantics (§5.3 binding note)
-----------------------------------------
State-file absence is treated as state-loss, NOT as first-run.  State-file
absence causes ``StateFileMissingError`` to be raised; the cron orchestrator
surfaces this to the operator, who must invoke ``bootstrap_state()`` explicitly
to initialize the state.  This defends against accidental state deletion
silently re-emitting every model or domain as new.

See ARCHITECTURE.md §4.6.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cdb_core.schemas import DomainResult, SocialTrigger, TriggerType

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Top-of-module constants
# ─────────────────────────────────────────────────────────────────────────────

# Placeholder threshold per ARCHITECTURE.md §4.6 line 1209 ("start at 0.15,
# tune later").  The value is unvalidated against real multi-date data; the
# cron's enable=False flag is the load-bearing lockout.  When real multi-date
# data first lands, the threshold should be revisited at a dedicated CDA SME
# review against the empirical distribution of Procrustes distances.
DRIFT_THRESHOLD: float = 0.15

# Register-3 minimum item intersection per docs/SME_REVIEW.md (≥ 8 shared
# items between any version pair for Procrustes drift to be meaningful).
DRIFT_MIN_ITEM_INTERSECTION: int = 8

# Minimum-delta floor on divergence-gap increases.  Placeholder pending
# empirical-distribution review.  A new "high" within MIN_DIVERGENCE_DELTA
# of the prior high is within bootstrap-CI-noise and does not fire.
# The 0.02 floor is set against the typical bootstrap-CI half-width visible on
# the existing dashboard data (rough order: bootstrap mean similarity values
# have CI half-widths in the 0.01–0.05 range).
MIN_DIVERGENCE_DELTA: float = 0.02


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class DriftDataInsufficientError(ValueError):
    """Raised when detect_drift is invoked on data that does not satisfy
    the Register-3 minimum (>= DRIFT_MIN_ITEM_INTERSECTION shared items
    between version pair).  The lockout is data-shaped, not flag-shaped.

    The exception message names the model_family, version_pair, and the
    n_shared_items count so the operator can diagnose the shortfall.
    """


class StateFileMissingError(FileNotFoundError):
    """Raised when a required state file is absent from state_dir.

    State-file absence is treated as state-loss (an operator-recoverable
    error), NOT as first-run.  The operator must explicitly invoke
    bootstrap_state() to initialize the state file.  See §5.3.
    """


class EvidenceContractError(ValueError):
    """Raised when a SocialTrigger's evidence dict is missing required keys.

    Each trigger type has a minimum evidence-key contract (see EVIDENCE_MIN_KEYS
    below and cdb_core/schemas.py lines 692–701).  This exception is raised
    inside validate_evidence_for_trigger_type() and propagates from the
    detect_* function that emitted the trigger.  It is never silenced.
    """


# ─────────────────────────────────────────────────────────────────────────────
# Evidence-key contract (Option B per CDA SME §5.7)
# ─────────────────────────────────────────────────────────────────────────────

EVIDENCE_MIN_KEYS: dict[TriggerType, set[str]] = {
    TriggerType.NEW_MODEL: {"first_seen_in_domain"},
    TriggerType.NEW_DOMAIN: {"domain_slug", "n_models"},
    TriggerType.DIVERGENCE: {"domain_slug", "model_pair", "old_high", "new_high", "gap_delta"},
    TriggerType.DRIFT: {"model_version_returned", "procrustes_distance", "date_pair"},
    TriggerType.MONTHLY_ROUNDUP: {"month"},
}


def validate_evidence_for_trigger_type(trigger: SocialTrigger) -> None:
    """Validate that trigger.evidence contains the minimum keys required
    for trigger.trigger_type per the contract in cdb_core/schemas.py:684-701.

    Called at every trigger-emission site inside each detect_* function
    immediately before the trigger is appended to the return list.

    Raises:
        EvidenceContractError: if any required key is missing.  The error
            message names the trigger_type, the missing keys, and the
            expected shape.
    """
    required = EVIDENCE_MIN_KEYS[trigger.trigger_type]
    missing = required - set(trigger.evidence.keys())
    if missing:
        raise EvidenceContractError(
            f"trigger {trigger.trigger_type} missing evidence keys: {sorted(missing)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _compute_dedupe_key(
    trigger_type: TriggerType,
    domain_slug: str | None,
    model_id: str | None,
    evidence: dict[str, Any],
) -> str:
    """Compute the 16-character dedupe key per cdb_core/schemas.py formula.

    Formula: SHA256(trigger_type + '|' + (domain_slug or '') + '|' +
    (model_id or '') + '|' + canonical_json(evidence))[:16].

    The formula intentionally excludes drafter_version and prompt_version.
    A drafter-prompt bump does not by itself justify re-firing a posted
    trigger.
    """
    canonical = json.dumps(evidence, sort_keys=True, ensure_ascii=True)
    raw = (
        str(trigger_type)
        + "|"
        + (domain_slug or "")
        + "|"
        + (model_id or "")
        + "|"
        + canonical
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically via a temp file in the same directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=True)
        os.replace(tmp, path)
    except Exception:
        import contextlib
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def _read_state_file(path: Path) -> dict[str, Any]:
    """Read a JSON state file or raise StateFileMissingError if absent."""
    if not path.exists():
        raise StateFileMissingError(
            f"State file absent: {path}. "
            "Run bootstrap_state() to initialize. "
            "State-file absence is treated as state-loss, not first-run (§5.3)."
        )
    with path.open(encoding="utf-8") as f:
        return dict(json.load(f))


# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap helper (§5.3)
# ─────────────────────────────────────────────────────────────────────────────

def bootstrap_state(
    state_dir: Path,
    manifest: dict[str, Any],
    domain_results: list[DomainResult],
) -> None:
    """One-time install: write seed state files so subsequent detector calls
    do not raise StateFileMissingError.

    Each state file carries a ``bootstrapped_at`` sentinel (ISO-8601 UTC
    datetime string) for audit.  After bootstrap the detectors operate in
    normal-delta mode — they compare future observations against the seeded
    baseline and emit triggers only for genuinely new events.

    Bootstrap is idempotent: calling it a second time overwrites existing state
    files with the current snapshot.  The operator should invoke bootstrap_state
    only on first install or after deliberate state reset.

    Args:
        state_dir:      Path to ``out/social/state/``.
        manifest:       The current ``apps/dashboard/public/data/manifest.json``
                        as a dict.  Expected shape:
                        ``{"domains": {domain_slug: {"models": [model_id, ...]}}}``
        domain_results: All current DomainResult objects from the published
                        results store.  Used to seed divergence_highs.json.
    """
    now_iso = datetime.now(tz=UTC).isoformat()
    state_dir.mkdir(parents=True, exist_ok=True)

    # ── seen_models.json ──────────────────────────────────────────────────────
    domains_map: dict[str, Any] = manifest.get("domains", {})
    seen_models: dict[str, list[str]] = {}
    for domain_slug, domain_info in domains_map.items():
        seen_models[domain_slug] = list(domain_info.get("models", []))
    _atomic_write_json(
        state_dir / "seen_models.json",
        {"bootstrapped_at": now_iso, "domains": seen_models},
    )

    # ── seen_domains.json ─────────────────────────────────────────────────────
    _atomic_write_json(
        state_dir / "seen_domains.json",
        {"bootstrapped_at": now_iso, "domains": list(domains_map.keys())},
    )

    # ── divergence_highs.json ─────────────────────────────────────────────────
    highs: dict[str, float] = {}
    for dr in domain_results:
        n = len(dr.models)
        max_gap = 0.0
        if n >= 2 and dr.similarity_matrix:
            for i in range(n):
                for j in range(i + 1, n):
                    if i < len(dr.similarity_matrix) and j < len(dr.similarity_matrix[i]):
                        # similarity_matrix is symmetric; pairwise distance is
                        # 1 - similarity for divergence purposes.  We store
                        # the max distance across all pairs as the baseline.
                        sim = dr.similarity_matrix[i][j]
                        dist = 1.0 - sim
                        if dist > max_gap:
                            max_gap = dist
        highs[dr.domain_slug] = max_gap
    _atomic_write_json(
        state_dir / "divergence_highs.json",
        {"bootstrapped_at": now_iso, "highs": highs},
    )

    # ── monthly_roundup.json ──────────────────────────────────────────────────
    # Seed with the previous calendar month so the first cron run on/after the
    # 1st will fire for the month that just ended.
    now = datetime.now(tz=UTC)
    prev_month = (
        f"{now.year - 1}-12" if now.month == 1 else f"{now.year}-{now.month - 1:02d}"
    )
    _atomic_write_json(
        state_dir / "monthly_roundup.json",
        {"bootstrapped_at": now_iso, "last_fired_month": prev_month},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Detector functions
# ─────────────────────────────────────────────────────────────────────────────

def detect_new_model(
    manifest: dict[str, Any],
    state_dir: Path,
) -> list[SocialTrigger]:
    """Detect models that appear in manifest but not in seen_models.json.

    Emits one SocialTrigger per (domain, new_model_id) pair.  Updates
    seen_models.json atomically after computing the trigger list.

    Args:
        manifest:   The current ``apps/dashboard/public/data/manifest.json``
                    as a dict.  Expected shape:
                    ``{"domains": {domain_slug: {"models": [model_id, ...]}}}``
        state_dir:  Path to ``out/social/state/``.

    Returns:
        List of SocialTrigger objects (possibly empty).

    Raises:
        StateFileMissingError: if ``state_dir/seen_models.json`` is absent.
        EvidenceContractError: if evidence construction fails the contract.

    Evidence payload per trigger: ``{"first_seen_in_domain": domain_slug}``.
    """
    state_path = state_dir / "seen_models.json"
    state = _read_state_file(state_path)

    seen: dict[str, list[str]] = state.get("domains", {})
    triggers: list[SocialTrigger] = []
    new_seen = {k: list(v) for k, v in seen.items()}

    domains_in_manifest: dict[str, Any] = manifest.get("domains", {})
    for domain_slug, domain_info in domains_in_manifest.items():
        current_models: list[str] = list(domain_info.get("models", []))
        prior_models: set[str] = set(seen.get(domain_slug, []))
        for model_id in current_models:
            if model_id not in prior_models:
                evidence: dict[str, Any] = {"first_seen_in_domain": domain_slug}
                trigger = SocialTrigger(
                    trigger_type=TriggerType.NEW_MODEL,
                    detected_at=datetime.now(tz=UTC),
                    domain_slug=domain_slug,
                    model_id=model_id,
                    evidence=evidence,
                    dedupe_key=_compute_dedupe_key(
                        TriggerType.NEW_MODEL, domain_slug, model_id, evidence
                    ),
                )
                validate_evidence_for_trigger_type(trigger)
                triggers.append(trigger)
                # Track for state update
                if domain_slug not in new_seen:
                    new_seen[domain_slug] = []
                if model_id not in new_seen[domain_slug]:
                    new_seen[domain_slug].append(model_id)

    # Atomic state update — only on new triggers
    if triggers:
        updated_state = dict(state)
        updated_state["domains"] = new_seen
        _atomic_write_json(state_path, updated_state)

    return triggers


def detect_new_domain(
    manifest: dict[str, Any],
    state_dir: Path,
) -> list[SocialTrigger]:
    """Detect domains that appear in manifest but not in seen_domains.json.

    Emits one SocialTrigger per new domain.  Updates seen_domains.json
    atomically after computing the trigger list.

    Args:
        manifest:   The current ``apps/dashboard/public/data/manifest.json``
                    as a dict.
        state_dir:  Path to ``out/social/state/``.

    Returns:
        List of SocialTrigger objects (possibly empty).

    Raises:
        StateFileMissingError: if ``state_dir/seen_domains.json`` is absent.
        EvidenceContractError: if evidence construction fails the contract.

    Evidence payload per trigger:
        ``{"domain_slug": str, "n_models": int}``
    """
    state_path = state_dir / "seen_domains.json"
    state = _read_state_file(state_path)

    seen_domains: set[str] = set(state.get("domains", []))
    triggers: list[SocialTrigger] = []
    new_seen = list(seen_domains)

    domains_in_manifest: dict[str, Any] = manifest.get("domains", {})
    for domain_slug, domain_info in domains_in_manifest.items():
        if domain_slug not in seen_domains:
            n_models = len(domain_info.get("models", []))
            evidence: dict[str, Any] = {
                "domain_slug": domain_slug,
                "n_models": n_models,
            }
            trigger = SocialTrigger(
                trigger_type=TriggerType.NEW_DOMAIN,
                detected_at=datetime.now(tz=UTC),
                domain_slug=domain_slug,
                model_id=None,
                evidence=evidence,
                dedupe_key=_compute_dedupe_key(
                    TriggerType.NEW_DOMAIN, domain_slug, None, evidence
                ),
            )
            validate_evidence_for_trigger_type(trigger)
            triggers.append(trigger)
            new_seen.append(domain_slug)

    # Atomic state update — only on new triggers
    if triggers:
        updated_state = dict(state)
        updated_state["domains"] = new_seen
        _atomic_write_json(state_path, updated_state)

    return triggers


def detect_drift(
    domain_results: list[DomainResult],
    state_dir: Path,
    *,
    enable: bool = False,
) -> list[SocialTrigger]:
    """Detect Procrustes drift across model_version_returned × collection_date.

    This function is locked to ``enable=False`` by default (kickoff §2 item 1)
    because the 0.2 corpus has at most one collection date per model version.
    Multi-date data must exist before the detector can produce meaningful drift
    signals.

    When ``enable=True``:
      - Inspects the data shape for each (model_family, version_pair).
      - Raises ``DriftDataInsufficientError`` if fewer than
        DRIFT_MIN_ITEM_INTERSECTION items are shared between any version pair.
      - Logs a WARNING on the first call where data meets the minimum,
        reminding the operator to surface to the CDA SME before live firing.
      - Emits a trigger when procrustes_distance > DRIFT_THRESHOLD.

    DRIFT_THRESHOLD = 0.15 is a placeholder per ARCHITECTURE.md §4.6 line 1209.
    DRIFT_MIN_ITEM_INTERSECTION = 8 is the Register-3 minimum (≥ 8 shared items
    between any version pair for Procrustes drift to be meaningful).

    NOTE: The ``domain_results`` argument is the list of DomainResult objects
    from the published results store.  Actual Procrustes computation requires
    a drift substrate produced by cdb_publish (``drift/{model_family}.json``).
    When multi-date data lands, the caller should pass pre-computed drift
    values via the domain_results metadata or a separate drift manifest.  This
    function is structured to accept that substrate when it exists.

    Args:
        domain_results: Published DomainResult objects.
        state_dir:      Path to ``out/social/state/``.
        enable:         If False (default), returns [] immediately.  Set True
                        only after multi-date data is confirmed to exist.

    Returns:
        List of SocialTrigger objects (possibly empty).

    Raises:
        DriftDataInsufficientError: when enable=True and data does not meet
            DRIFT_MIN_ITEM_INTERSECTION for a given version pair.
        EvidenceContractError: if evidence construction fails the contract.

    Evidence payload per trigger:
        ``{"model_version_returned": str, "procrustes_distance": float,
           "date_pair": [str, str]}``
    """
    if not enable:
        return []

    triggers: list[SocialTrigger] = []

    # Group domain_results by model_family to look for version pairs.
    # Each DomainResult's models list carries ModelRef objects.
    # We need at least two distinct collection dates per (family, version) pair.
    # Since the published substrate (drift/{model_family}.json) is not yet
    # available (multi-date data does not exist in the 0.2 corpus), we check
    # the data shape here and raise if insufficient.

    family_versions: dict[str, set[str]] = {}
    for dr in domain_results:
        for model_ref in dr.models:
            family = model_ref.family
            # model_ref.version_label is the version identifier
            version = model_ref.version_label
            if family not in family_versions:
                family_versions[family] = set()
            family_versions[family].add(version)

    for family, versions in family_versions.items():
        version_list = sorted(versions)
        if len(version_list) < 2:
            # Only one version — no drift computation possible
            continue

        # Check item intersection across version pairs
        for i in range(len(version_list)):
            for j in range(i + 1, len(version_list)):
                v1, v2 = version_list[i], version_list[j]

                # Collect items (model_id keys) present in both versions.
                # "Items" in Register-3 are the domain vocabulary items
                # shared between two pile-sorts. Here we use domain slugs
                # as the intersection proxy since the full pile-sort item
                # data is in the raw layer (not re-exposed in DomainResult).
                # When the real drift substrate lands (drift/{family}.json),
                # this intersection must be computed from that file.
                items_v1: set[str] = {
                    dr.domain_slug
                    for dr in domain_results
                    if any(m.family == family and m.version_label == v1 for m in dr.models)
                }
                items_v2: set[str] = {
                    dr.domain_slug
                    for dr in domain_results
                    if any(m.family == family and m.version_label == v2 for m in dr.models)
                }
                intersection = items_v1 & items_v2
                n_shared = len(intersection)

                if n_shared < DRIFT_MIN_ITEM_INTERSECTION:
                    raise DriftDataInsufficientError(
                        f"Procrustes drift data insufficient for family={family!r} "
                        f"versions=({v1!r}, {v2!r}): "
                        f"n_shared_items={n_shared} < "
                        f"DRIFT_MIN_ITEM_INTERSECTION={DRIFT_MIN_ITEM_INTERSECTION}. "
                        "Wait until multi-date collection produces >= "
                        f"{DRIFT_MIN_ITEM_INTERSECTION} shared items."
                    )

                # Data meets the minimum — log a pre-fire warning per §5.1.
                # The actual Procrustes distance would be computed from the
                # drift substrate (drift/{family}.json).  Placeholder: 0.0.
                computed_distance = 0.0  # replace with real computation when substrate exists

                logger.warning(
                    "DRIFT_THRESHOLD first fire — SME review required before continued use. "
                    "family=%s version_pair=(%s, %s) n_shared_items=%d "
                    "computed_distance=%.4f DRIFT_THRESHOLD=%.4f",
                    family, v1, v2, n_shared, computed_distance, DRIFT_THRESHOLD,
                )

                if computed_distance > DRIFT_THRESHOLD:
                    evidence: dict[str, Any] = {
                        "model_version_returned": v2,
                        "procrustes_distance": computed_distance,
                        "date_pair": [v1, v2],
                    }
                    trigger = SocialTrigger(
                        trigger_type=TriggerType.DRIFT,
                        detected_at=datetime.now(tz=UTC),
                        domain_slug=None,
                        model_id=None,
                        evidence=evidence,
                        dedupe_key=_compute_dedupe_key(
                            TriggerType.DRIFT, None, None, evidence
                        ),
                    )
                    validate_evidence_for_trigger_type(trigger)
                    triggers.append(trigger)

    return triggers


def _max_pairwise_gap(
    similarity_matrix: list[list[float]],
    models: list[str],
    exclude_models: set[str] | None = None,
) -> tuple[float, tuple[str, str]]:
    """Compute the maximum pairwise distance gap in a similarity matrix.

    Distance = 1 - similarity (point-mean comparison only — NOT a statistical
    CI-overlap test; LSB does not make claim-confirming findings per §1.5.7).

    Args:
        similarity_matrix: Square matrix of similarity values.
        models:            List of model_id strings (row/column labels).
        exclude_models:    If non-None, exclude these model_ids from the
                           computation.  Used for the new-model exclusion
                           algorithm per CDA SME §5.6.

    Returns:
        Tuple of (max_gap, (model_a, model_b)) where model_a and model_b are
        the argmax pair.  Returns (0.0, ("", "")) if fewer than 2 models remain
        after exclusion.
    """
    exclude: set[str] = exclude_models or set()
    active_indices = [
        i for i, m in enumerate(models) if m not in exclude
    ]

    if len(active_indices) < 2:
        return 0.0, ("", "")

    max_gap = 0.0
    argmax_pair: tuple[str, str] = ("", "")

    for ii in range(len(active_indices)):
        for jj in range(ii + 1, len(active_indices)):
            i = active_indices[ii]
            j = active_indices[jj]
            if i < len(similarity_matrix) and j < len(similarity_matrix[i]):
                sim = similarity_matrix[i][j]
                dist = 1.0 - sim
                if dist > max_gap:
                    max_gap = dist
                    argmax_pair = (models[i], models[j])

    return max_gap, argmax_pair


def detect_divergence(
    domain_results: list[DomainResult],
    state_dir: Path,
    *,
    new_models_this_run: dict[str, list[str]] | None = None,
) -> list[SocialTrigger]:
    """Detect when the maximum pairwise divergence gap in a domain sets a new high.

    Comparison is point-mean to point-mean — NOT a CI-overlap statistical test
    (§5.2 / §1.5.7: LSB does not make claim-confirming findings).

    Per-domain new-model exclusion (CDA SME §5.6): when new models arrive in
    a domain during the same run, the pairwise-max gap is recomputed with those
    new models excluded before comparing against the stored baseline.  This
    prevents a new-model addition from masquerading as an organic divergence
    finding.  The state baseline is updated ONLY when a trigger fires — if the
    apparent new high is attributable to new-model addition, the baseline is
    NOT updated.

    Ordering constraint: the orchestrator must call detect_new_model() before
    detect_divergence() so the new_models_this_run dict is populated.

    Args:
        domain_results:       Published DomainResult objects.
        state_dir:            Path to ``out/social/state/``.
        new_models_this_run:  Dict mapping domain_slug → list of new model_ids
                              just added (from detect_new_model output).
                              If None, treated as empty (no exclusion).

    Returns:
        List of SocialTrigger objects (possibly empty).

    Raises:
        StateFileMissingError: if ``state_dir/divergence_highs.json`` is absent.
        EvidenceContractError: if evidence construction fails the contract.

    Evidence payload per trigger:
        ``{"domain_slug": str, "model_pair": [str, str],
           "old_high": float, "new_high": float, "gap_delta": float}``

    Optional evidence key (advisory, not binding): ``"new_models_excluded": list[str]``
    """
    state_path = state_dir / "divergence_highs.json"
    state = _read_state_file(state_path)

    highs: dict[str, float] = state.get("highs", {})
    new_models: dict[str, list[str]] = new_models_this_run or {}

    triggers: list[SocialTrigger] = []
    updated_highs = dict(highs)

    for dr in domain_results:
        domain_slug = dr.domain_slug
        models_in_domain = [m.model_id for m in dr.models]
        exclude_set: set[str] = set(new_models.get(domain_slug, []))

        gap_excl, argmax_pair = _max_pairwise_gap(
            dr.similarity_matrix,
            models_in_domain,
            exclude_models=exclude_set if exclude_set else None,
        )

        stored_high = highs.get(domain_slug, 0.0)
        gap_delta = gap_excl - stored_high

        if gap_delta >= MIN_DIVERGENCE_DELTA:
            evidence: dict[str, Any] = {
                "domain_slug": domain_slug,
                "model_pair": list(argmax_pair),
                "old_high": stored_high,
                "new_high": gap_excl,
                "gap_delta": gap_delta,
            }
            # Optional forensic transparency key
            if exclude_set:
                evidence["new_models_excluded"] = sorted(exclude_set)

            trigger = SocialTrigger(
                trigger_type=TriggerType.DIVERGENCE,
                detected_at=datetime.now(tz=UTC),
                domain_slug=domain_slug,
                model_id=None,
                evidence=evidence,
                dedupe_key=_compute_dedupe_key(
                    TriggerType.DIVERGENCE, domain_slug, None, evidence
                ),
            )
            validate_evidence_for_trigger_type(trigger)
            triggers.append(trigger)
            # Update the baseline only when the trigger fires
            updated_highs[domain_slug] = gap_excl

    # Atomic state update — only on new triggers
    if triggers:
        updated_state = dict(state)
        updated_state["highs"] = updated_highs
        _atomic_write_json(state_path, updated_state)

    return triggers


def detect_monthly_roundup(
    state_dir: Path,
    *,
    now: datetime,
) -> list[SocialTrigger]:
    """Fire a monthly-roundup trigger on the first cron run on/after the 1st
    of each calendar month at 14:00 UTC.

    Idempotent within a calendar month: re-running after a trigger has fired
    for a given month returns [].

    evidence['month'] is the PREVIOUS calendar month (the month being
    summarized), in YYYY-MM format.  The state file records
    last_fired_month: YYYY-MM.

    Args:
        state_dir:  Path to ``out/social/state/``.
        now:        The current datetime (should be UTC-aware).  Injected
                    for deterministic testing.

    Returns:
        List containing one SocialTrigger, or [].

    Raises:
        StateFileMissingError: if ``state_dir/monthly_roundup.json`` is absent.
        EvidenceContractError: if evidence construction fails the contract.

    Evidence payload: ``{"month": "YYYY-MM"}`` (previous calendar month).
    """
    state_path = state_dir / "monthly_roundup.json"
    state = _read_state_file(state_path)

    # Previous calendar month (the month being summarized)
    target_month = (
        f"{now.year - 1}-12" if now.month == 1 else f"{now.year}-{now.month - 1:02d}"
    )

    last_fired = state.get("last_fired_month", "")

    if last_fired == target_month:
        # Already fired for this month — idempotent
        return []

    evidence: dict[str, Any] = {"month": target_month}
    trigger = SocialTrigger(
        trigger_type=TriggerType.MONTHLY_ROUNDUP,
        detected_at=now,
        domain_slug=None,
        model_id=None,
        evidence=evidence,
        dedupe_key=_compute_dedupe_key(
            TriggerType.MONTHLY_ROUNDUP, None, None, evidence
        ),
    )
    validate_evidence_for_trigger_type(trigger)

    # Update state file atomically
    updated_state = dict(state)
    updated_state["last_fired_month"] = target_month
    _atomic_write_json(state_path, updated_state)

    return [trigger]
