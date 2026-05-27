"""Two-level nested CDA pipeline (post-F1 SME review).

Implements the three-register framework from ARCHITECTURE.md §4.2.0:

- **Register 1 (within-model)**: N runs of one model analyzed as an
  output distribution. The primary measure is the Output Concentration
  Index (OCI) — the eigenratio of the run × run agreement matrix. OCI
  is a concentration statistic, not a cultural consensus ratio; the
  runs are iid samples from one stochastic process, not distinct
  cultural agents. See docs/SME_REVIEW.md and docs/BOOTSTRAP_DESIGN.md
  for why OCI must never be called "within-model consensus."

- **Register 2 (between-model)**: each model contributes one voice as
  its Option A consensus free list (``level_two_input``). Human
  baselines participate as reference informants with distinct markers.

- **Register 3 (cross-version drift)**: handled by ``drift.py``,
  unchanged by this module.

This module produces Register 1 results (per-model ``WithinModelResult``
objects) and the three Level-2-input representations per the SME
resolution (``options_for_level_two``):

- **Option A — pooled consensus free list** (primary Level 2 input).
  All models contribute equal voice regardless of OCI.
- **Option B — centroid run** (dashboard display only). The single
  run closest to the model's central tendency.
- **Option C — coherence-weighted diagnostic** (not an alternative
  map). A separate computation reported alongside the Register 2 map
  so readers can see whether high-OCI models cluster together.
"""

from __future__ import annotations

import numpy as np
from cdb_core import InformantRecord, RunSummary, WithinModelResult
from numpy.typing import NDArray
from scipy.stats import spearmanr

from cdb_analyze.consensus import compute_consensus_free_list, smiths_s


def run_within_model_analysis(
    records: list[InformantRecord],
    *,
    n_bootstrap: int = 0,
    random_state: int = 42,
) -> WithinModelResult:
    """Register 1 analysis for one model's N runs.

    Computes the Output Concentration Index (OCI), per-run centrality
    loadings, the centroid run (Option B display representation), and
    optional bootstrap CIs on OCI.

    Args:
        records: InformantRecords for a single (model, domain). Must
            all share the same model_id. Minimum N = 3 for a
            well-posed eigenratio; below that, OCI is returned as 0.0
            with a null CI.
        n_bootstrap: Bootstrap iterations for OCI CI. 0 means no
            bootstrap (the default for tests and for fast pipeline
            runs). When > 0, the returned ``oci_ci`` is the 95%
            percentile interval from resampling runs with replacement.
            **The CI systematically underestimates uncertainty** —
            see docs/BOOTSTRAP_DESIGN.md §2. The
            ``underestimates_uncertainty`` flag on the returned object
            is always True for Register 1.
        random_state: RNG seed.

    Returns:
        WithinModelResult populated with OCI, per-run centrality, the
        centroid run id, and optional CIs. Stability diagnostics
        (salience, elbow, Procrustes) are left null — those are
        populated by the saturation analysis runner when varying N,
        not on a single N-run record batch.

    Raises:
        ValueError: if records is empty or contains mixed model_ids.
    """
    if not records:
        msg = "Cannot run within-model analysis on empty records"
        raise ValueError(msg)

    model_ids = {r.model_id for r in records}
    if len(model_ids) != 1:
        msg = f"All records must share one model_id; got {sorted(model_ids)}"
        raise ValueError(msg)
    model_id = model_ids.pop()
    n_runs = len(records)

    agreement = _run_agreement_matrix(records)
    oci = _oci_from_matrix(agreement)
    deterministic = _is_deterministic_output(agreement)
    centrality = _centrality_loadings(agreement)
    centrality_by_run = {
        records[i].informant_id: float(centrality[i])
        for i in range(n_runs)
    }
    centroid_run_id = (
        max(centrality_by_run, key=lambda k: centrality_by_run[k])
        if centrality_by_run
        else None
    )

    oci_ci: tuple[float, float] | None = None
    if n_bootstrap > 0 and n_runs >= 3:
        oci_ci = _bootstrap_oci(records, n_bootstrap=n_bootstrap, random_state=random_state)

    run_summaries = _build_run_summaries(records, centrality)
    salience_rho = _salience_stability_rho(records)

    # Retain the agreement matrix (rounded to 4dp per CDA SME S9)
    agreement_list = np.round(agreement, 4).tolist()

    return WithinModelResult(
        model_id=model_id,
        n_runs=n_runs,
        oci=float(oci),
        oci_ci=oci_ci,
        underestimates_uncertainty=True,  # binding; see BOOTSTRAP_DESIGN.md §2
        deterministic_output=deterministic,
        centrality_scores_by_run=centrality_by_run,
        centroid_run_id=centroid_run_id,
        run_agreement_matrix=agreement_list,
        run_summaries=run_summaries,
        salience_stability_rho=salience_rho,
    )


def compute_oci(records: list[InformantRecord]) -> float:
    """Convenience wrapper — OCI only, without the full WithinModelResult."""
    if len(records) < 2:
        return 0.0
    return float(_oci_from_matrix(_run_agreement_matrix(records)))


# ---------------------------------------------------------------------------
# Level-2 input derivation (Option A / B / C per the SME resolution)
# ---------------------------------------------------------------------------

def options_for_level_two(
    records: list[InformantRecord],
) -> dict[str, object]:
    """Compute the three Level-2-input representations per SME resolution.

    Returns a dict with:

    - ``"option_a"``: list of (item, composite_smiths_s) — the pooled
      consensus free list from the model's runs. **Primary Level 2
      input**. Equal voice for all models regardless of OCI.
    - ``"option_b_centroid_run_id"``: the informant_id of the run
      closest to the model's central tendency. Used as the
      **dashboard display representation** on tooltips and model
      profile pages — a concrete, readable single run rather than a
      pooled aggregate.
    - ``"option_c_weight"``: the model's OCI, to be used only as a
      **diagnostic** in a coherence-weighted sensitivity analysis
      run alongside the Register 2 map — **never as the primary map**.
      Per SME Q2 resolution: weighting Level 2 by Level 1 coherence
      biases low-OCI models toward the margins for the wrong reason.
      **Note on CI:** this function calls ``run_within_model_analysis``
      with ``n_bootstrap=0`` — ``option_c_weight`` is a point estimate
      of OCI without a confidence interval. That is by design because
      Option C is diagnostic-only; a caller that needs an OCI CI for
      methodological reporting should use ``run_within_model_analysis``
      directly and request a bootstrap, not route through this helper.
      The §4.2.0 register boundary forbids using this value as a
      primary weighting input in any production dashboard code path.

    See ARCHITECTURE.md §4.2.0 and docs/SME_REVIEW.md for the full
    rationale and why Option B is preferred for dashboard display
    over Option A's pooled aggregate.
    """
    if not records:
        return {
            "option_a": [],
            "option_b_centroid_run_id": None,
            "option_c_weight": 0.0,
        }

    wm = run_within_model_analysis(records, n_bootstrap=0)
    option_a = compute_consensus_free_list(records)
    return {
        "option_a": option_a,
        "option_b_centroid_run_id": wm.centroid_run_id,
        "option_c_weight": wm.oci,
    }


# ---------------------------------------------------------------------------
# Focus 1 helpers
# ---------------------------------------------------------------------------

def _build_run_summaries(
    records: list[InformantRecord],
    centrality: NDArray[np.float64],
) -> list[RunSummary]:
    """Build a RunSummary for each record, in the same order as the records list."""
    return [
        RunSummary(
            run_id=r.informant_id,
            run_index=r.run_index,
            n_free_list_items=len(r.freelist.parsed_items),
            n_piles=len(r.pile_sort.parsed_piles),
            pile_labels=r.interview.parsed_pile_labels if r.interview else [],
            centrality_loading=float(centrality[i]),
        )
        for i, r in enumerate(records)
    ]


def _salience_stability_rho(
    records: list[InformantRecord],
) -> float | None:
    """Mean pairwise Spearman rho of per-run Smith's S rankings.

    Per CDA SME S2: for each run, rank items by their individual Smith's S
    within that run (S = (L - R + 1) / L). Then compute Spearman rho between
    all pairs of runs on the intersection of items present in both runs.
    Return the mean of pairwise rhos. None if fewer than 2 runs have items.
    """
    per_run_salience: list[dict[str, float]] = []
    for r in records:
        raw_order = r.freelist.parsed_raw_order
        list_length = len(raw_order)
        if list_length == 0:
            continue
        seen: set[str] = set()
        salience: dict[str, float] = {}
        for rank_0, item in enumerate(raw_order):
            if item in seen:
                continue
            seen.add(item)
            salience[item] = smiths_s(rank_0 + 1, list_length)
        per_run_salience.append(salience)

    n = len(per_run_salience)
    if n < 2:
        return None

    rhos: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            shared = sorted(set(per_run_salience[i]) & set(per_run_salience[j]))
            if len(shared) < 3:
                continue
            x = [per_run_salience[i][item] for item in shared]
            y = [per_run_salience[j][item] for item in shared]
            rho, _ = spearmanr(x, y)
            if not np.isnan(rho):
                rhos.append(float(rho))

    return float(np.mean(rhos)) if rhos else None


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _run_agreement_matrix(
    records: list[InformantRecord],
) -> NDArray[np.float64]:
    """Compute an N × N run agreement matrix.

    Agreement between two runs is the fraction of item pairs on which
    they agree — both in the same pile, or both in different piles —
    computed on the intersection of items present in both runs'
    pile-sort output. Diagonal = 1.0. Symmetric.

    This is the Register 1 analog of the RWB informant × informant
    agreement matrix. The resulting matrix's eigenratio λ₁/λ₂ is the
    Output Concentration Index.
    """
    n = len(records)
    mat = np.ones((n, n), dtype=np.float64)

    # Build a lookup of (item → pile_index) for each run for fast lookup
    per_run: list[dict[str, int]] = []
    for r in records:
        item_to_pile: dict[str, int] = {}
        for pile_idx, pile in enumerate(r.pile_sort.parsed_piles):
            for item in pile:
                item_to_pile[item] = pile_idx
        per_run.append(item_to_pile)

    for i in range(n):
        for j in range(i + 1, n):
            shared = sorted(set(per_run[i]) & set(per_run[j]))
            if len(shared) < 2:
                mat[i, j] = 0.0
                mat[j, i] = 0.0
                continue
            n_pairs = 0
            n_agree = 0
            for a_idx in range(len(shared)):
                for b_idx in range(a_idx + 1, len(shared)):
                    a, b = shared[a_idx], shared[b_idx]
                    same_i = per_run[i][a] == per_run[i][b]
                    same_j = per_run[j][a] == per_run[j][b]
                    if same_i == same_j:
                        n_agree += 1
                    n_pairs += 1
            mat[i, j] = n_agree / n_pairs if n_pairs else 0.0
            mat[j, i] = mat[i, j]
    return mat


# Floor below which the second eigenvalue of the agreement matrix is
# treated as zero — the run × run agreement matrix is effectively
# rank-1, meaning the model's N runs produced near-identical pile-sort
# structure. Used by both ``_oci_from_matrix`` (to avoid dividing by
# ~0) and ``_is_deterministic_output`` (to raise the DETERMINISTIC
# marker). Per ARCHITECTURE.md §4.2.0 and the post-F1 SME review.
#
# Scale rationale (per CDA SME review of this PR, 2026-04-20). The
# agreement matrix A is an N × N symmetric matrix whose entries lie in
# [0, 1] — each cell is the fraction of item pairs on which two runs
# agree. Since each row-sum of A is at most N, the spectral radius
# λ₁ ≤ N (Gershgorin / row-sum bound), and N is small in practice
# (typically ≈ 5–20 runs). The natural scale of the leading eigenvalue
# is therefore O(N). A threshold of 1e-12 is ~12 orders of magnitude
# below λ₁'s natural scale and cannot be confused with ordinary
# numerical noise from a stochastic but non-degenerate matrix. An
# absolute threshold is preferred over a relative one (λ₂ / λ₁) here
# because the absolute form gives a clearer semantic contract at this
# scale: "λ₂ is indistinguishable from numerical zero" rather than
# "λ₂ is a small-but-nonzero fraction of λ₁." If N ever grows past
# ~100 (not in scope for v1), reconsider the absolute form.
DETERMINISTIC_EIGENVALUE_THRESHOLD: float = 1e-12


def _oci_from_matrix(agreement: NDArray[np.float64]) -> float:
    """Compute the eigenratio λ₁/λ₂ of the agreement matrix.

    Returns 0.0 for degenerate inputs (too few rows, zero λ₂).
    """
    n = agreement.shape[0]
    if n < 2:
        return 0.0
    eigvals = np.linalg.eigvalsh(agreement)
    eigvals = np.sort(eigvals)[::-1]  # descending
    if len(eigvals) < 2:
        return 0.0
    lambda_1 = float(eigvals[0])
    lambda_2 = float(eigvals[1])
    if lambda_2 <= DETERMINISTIC_EIGENVALUE_THRESHOLD:
        # λ₂ effectively zero — concentration is effectively infinite.
        # Return a large sentinel rather than dividing by ~0; upstream
        # code treats OCI ≥ operational threshold as high concentration.
        # ``_is_deterministic_output`` raises the DETERMINISTIC marker
        # on the same condition, which is what downstream code should
        # key on rather than the sentinel value itself.
        return 100.0
    return lambda_1 / lambda_2


# Minimum N runs required before ``_is_deterministic_output`` will raise
# the flag. Per CDA SME review of PR A (2026-04-20, recommendation R2):
# at N = 2 or N = 3, a single pair of identical runs can push λ₂ below
# ``DETERMINISTIC_EIGENVALUE_THRESHOLD`` without the model being
# genuinely deterministic — two draws from a stochastic process can
# accidentally match. The N = 2 guard below is the correctness floor
# (eigendecomposition needs ≥ 2 rows to have a second eigenvalue); the
# N = 4 guard here is the *reliability* floor for treating the zero-λ₂
# signal as architectural rather than a lucky coincidence. Revisit
# after the Phase 4b saturation analysis confirms the per-model N is
# routinely ≥ 5 (the default slate's N=5 clears this guard).
MIN_RUNS_FOR_DETERMINISTIC_FLAG: int = 4


def _is_deterministic_output(agreement: NDArray[np.float64]) -> bool:
    """True when the model's run × run agreement has effectively zero λ₂.

    Indicates the model's N runs produced near-identical pile-sort structure —
    a zero-variance output distribution on this (model, domain). Triggers
    the ``ConsensusType = DETERMINISTIC`` classification per
    ARCHITECTURE.md §4.2.0 and the DESIGN_SYSTEM.md §3.3.5 visual
    convention for Register 2 points whose Level 1 concentration is the
    *least* informative case, not the most. Does not trigger on any
    current transformer model at T > 0; reserved for future deterministic
    architectures (neurosymbolic systems, zero-temperature models).

    Requires N >= ``MIN_RUNS_FOR_DETERMINISTIC_FLAG`` (4) — below that,
    a pair of identical runs can trip the eigenvalue threshold without
    the model being genuinely deterministic. See the comment on
    ``MIN_RUNS_FOR_DETERMINISTIC_FLAG`` for the reliability rationale.
    """
    n = agreement.shape[0]
    if n < MIN_RUNS_FOR_DETERMINISTIC_FLAG:
        return False
    eigvals = np.linalg.eigvalsh(agreement)
    eigvals = np.sort(eigvals)[::-1]
    if len(eigvals) < 2:
        return False
    return float(eigvals[1]) <= DETERMINISTIC_EIGENVALUE_THRESHOLD


def _centrality_loadings(
    agreement: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Per-run loadings on the first eigenvector of the agreement matrix.

    Used to identify the centroid run (highest loading) and to surface
    run-level centrality for any per-run QA or diagnostics.
    """
    n = agreement.shape[0]
    if n < 2:
        return np.zeros(n)
    eigvals, eigvecs = np.linalg.eigh(agreement)
    order = eigvals.argsort()[::-1]
    first = eigvecs[:, order[0]]
    if float(np.mean(first)) < 0:
        first = -first
    return first


def _bootstrap_oci(
    records: list[InformantRecord],
    *,
    n_bootstrap: int,
    random_state: int,
) -> tuple[float, float]:
    """95% percentile CI on OCI via resampling runs with replacement.

    **This CI systematically underestimates uncertainty** — runs are
    iid draws from one stochastic process, so effective N is less
    than nominal N. The returned interval is narrow by construction.
    See docs/BOOTSTRAP_DESIGN.md §2.
    """
    n = len(records)
    rng = np.random.default_rng(random_state)
    vals: list[float] = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        resampled = [records[i] for i in idx]
        mat = _run_agreement_matrix(resampled)
        vals.append(_oci_from_matrix(mat))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))
