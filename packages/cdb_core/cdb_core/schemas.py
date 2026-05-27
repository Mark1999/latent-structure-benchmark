"""LSB core schemas — the single source of truth for all data contracts.

Defined once here; every other package imports from cdb_core.
See ARCHITECTURE.md §3.2 for the binding specification.

The Reviewer agent must reject any PR that redefines these types elsewhere
or that changes InformantRecord/GroundingRef without a matching update to
docs/DATA_DICTIONARY.md in the same PR.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

# ─────────────────────────────────────────────────────────────────────
# Utility schemas
# ──────��──────────────────────────────────────────────────��───────────

class BootstrapEllipse(BaseModel):
    """95% bootstrap confidence ellipse for a point in MDS space.

    See ARCHITECTURE.md §4.2.6.
    """
    center: tuple[float, float]
    semi_major: float
    semi_minor: float
    rotation_rad: float
    n_bootstrap: int


# ─────────���───────────────────────────���───────────────────────────────
# Core entity schemas (ARCHITECTURE.md §3.2)
# ───────────���─────────────────────��───────────────────────────────────

class ModelRef(BaseModel):
    """Reference to a model in the LSB slate.

    Schema notes (binding for Coder and Reviewer agents):
    - collection_method records which of the three remote integration points
      was used: Anthropic API, OpenRouter, or Hugging Face Inference Providers.
      The same logical model may appear more than once if invoked through
      different gateways; those rows differ by collection_method and/or
      model_id string.
    - The open_weights field is a strict Boolean. License nuances (Llama's
      commercial restrictions, Mistral's mixed open/closed model line, etc.)
      are handled via source_notes rather than expanding the field into an
      enum. If a model's openness is genuinely ambiguous, set open_weights
      True if the weights are downloadable at all and document restrictions
      in source_notes.
    - The quantization field is None when the provider does not expose a
      meaningful quant label in the API response; set when HF or another path
      returns an explicit precision tag useful for provenance.
    - origin covers four production regions plus "other"; the four regions
      correspond to populated clusters in the v1 model slate (US, EU, Canada,
      China). New origin values require an architecture decision, not an
      ad-hoc schema bump.
    """
    provider: Literal[
        "anthropic", "openai", "google", "xai", "cohere",
        "openrouter", "huggingface",
    ]
    model_id: str
    family: str
    origin: Literal["us", "eu", "ca", "cn", "other"]
    open_weights: bool
    collection_method: Literal[
        "anthropic_api", "openrouter", "huggingface", "google_ai",
        "xai_api", "openai_api", "deepseek_api", "mistral_api",
    ]
    quantization: str | None
    release_date: date
    version_label: str
    source_notes: str = ""


class Domain(BaseModel):
    """A CDA domain definition. See ARCHITECTURE.md §3.2."""
    slug: str
    version: str
    display_name: str
    prompt_seed: str
    truncation_k: int = 25


class RawResponse(BaseModel):
    """Per-API-call atom. See ARCHITECTURE.md §3.2."""
    run_id: str
    model: ModelRef
    domain_slug: str
    step: Literal["free_list", "pile_sort", "pile_interview"]
    prompt_version: str
    run_index: int
    timestamp: datetime
    request: dict
    response: dict
    latency_ms: int


class FreeList(BaseModel):
    """Parsed free-list output. See ARCHITECTURE.md §3.2."""
    run_id: str
    model: ModelRef
    domain_slug: str
    items: list[str]
    raw_order: list[str]


class PileSort(BaseModel):
    """Parsed pile-sort output. See ARCHITECTURE.md §3.2."""
    run_id: str
    model: ModelRef
    domain_slug: str
    items: list[str]
    piles: list[list[str]]
    pile_labels: list[str]


class CooccurrenceMatrix(BaseModel):
    """Item-to-item co-occurrence matrix. See ARCHITECTURE.md §3.2."""
    domain_slug: str
    model: ModelRef
    items: list[str]
    matrix: list[list[float]]


# ─────��──────────────────────────��────────────────────────────────────
# GroundingRef — v0.7 multi-baseline (ARCHITECTURE.md §3.2)
# ──────────────────��─────────────────────────────���────────────────────

class GroundingRef(BaseModel):
    """A human CDA baseline treated as a virtual informant in the MDS plot.

    A domain can have zero, one, or many GroundingRef instances. Each instance
    represents one human population studied with the CDA protocol. The
    distinction between baseline kinds (published vs researcher-submitted) is
    encoded in baseline_kind and drives the visual treatment in
    DESIGN_SYSTEM.md §3.3 and §4.1 — published baselines render as black
    stars, researcher baselines as gray diamonds.
    """

    # ── Identity ──
    baseline_id: str
    baseline_kind: Literal["published", "researcher"]
    domain_slug: str

    # ── Source ──
    source_citation: str
    source_url: str | None
    collected_year: int

    # ── Population ──
    n_human_informants: int
    population_description: str

    # ── Method ──
    method: str
    irb_status: Literal["approved", "exempt", "not_applicable", "unknown"] = "unknown"

    # ── Submitter (researcher baselines only) ──
    submitter_name: str | None = None
    submitter_institution: str | None = None
    submitter_contact: str | None = None
    submission_date: date | None = None

    # ── Position in cultural space ──
    mds_coordinate: tuple[float, float]
    mds_uncertainty: BootstrapEllipse | None = None
    distance_to_nearest_model: float
    nearest_model_id: str

    # ── Item-set alignment ──
    item_intersection_size: int
    item_intersection_total: int

    # ── Register 1 cross-species extension (post-F1 SME review) ──
    # Populated only when the baseline ships with per-subject raw pile-sort
    # data (pile_sort_raw.csv). Allows the human subject pool to be
    # analyzed at Register 1 alongside models, producing a concentration
    # index directly comparable to model OCI. Null for published aggregate
    # matrices — the majority case. See ARCHITECTURE.md §4.2.5.
    human_oci: float | None = None
    human_oci_ci: tuple[float, float] | None = None
    n_subjects_with_raw_data: int | None = None


# ──────────────────────────────────────────────────────────────────────
# Consensus typology and measure result types (added post-F1 SME review)
#
# See docs/SME_REVIEW.md §1.1 (dual Romney threshold), §1.5 (cultural
# centrality), §1.6 (low-consensus typology), §2.1 (Sutrop CSI),
# §2.2 (Nolan Index), and the two-level-design discussion for OCI /
# WithinModelResult. Canonical location for ConsensusType is here
# (cdb_core) to avoid circular imports between schemas.py and
# cdb_analyze.gates where the type is also consumed.
# ──────────────────────────────────────────────────────────────────────

ConsensusType = Literal[
    "STRONG_CONSENSUS",   # λ₁/λ₂ ≥ 5.0, all centrality scores positive
    "WEAK_CONSENSUS",     # 3.0 ≤ λ₁/λ₂ < 5.0, centrality scores positive
    "SUBCULTURAL",        # λ₁/λ₂ ≥ 3.0, negative centrality scores present
    "TURBULENT",          # λ₁/λ₂ < 3.0, centrality scores positive
    "CONTESTED",          # λ₁/λ₂ < 3.0, negative centrality scores present
    "DETERMINISTIC",      # zero-variance across prompt/run variation;
                          # reserved for deterministic architectures
                          # (neurosymbolic, zero-temperature); does not
                          # trigger for any current transformer model
]


class SutropCSI(BaseModel):
    """One item's Sutrop composite salience index (Sutrop 2001).

    CSI = F / (N × mP) where F is mentions across runs, N is total
    runs, and mP is the mean 1-indexed position of the item across
    runs that contained it. Robust to list-length variance in a way
    Smith's S is not; see docs/SME_REVIEW.md §2.1.
    """
    item: str
    csi: float
    f_mentions: int   # number of runs where the item appeared
    n_runs: int       # total runs considered
    mean_position: float  # mP (1-indexed)


class NolanIndexPair(BaseModel):
    """Pairwise proportional-frequency similarity between two models.

    Robbins (2023). NI = 1 - D, D = sqrt((1/M) × Σ(d_i)²),
    d_i = proportional difference per item. Range [0, 1] where 1 is
    identical proportional distributions. See docs/SME_REVIEW.md §2.2.

    Reported alongside Jaccard and Mantel r to distinguish
    "same items, different weights" (where Jaccard says 1.0 but NI < 1)
    from "different items" (where both decrease together).
    """
    model_a: str
    model_b: str
    ni: float
    jaccard: float
    ni_vs_jaccard_delta: float  # ni - jaccard; negative when emphasis differs


class MantelPair(BaseModel):
    """Classical Mantel test between two models' co-occurrence matrices.

    Reports both the matrix correlation r and the permutation p-value
    on the upper triangle (excluding diagonal). See docs/SME_REVIEW.md
    §1.2 — added as a parallel pairwise measure alongside the Register 2
    ``g2_signal`` dispersion-permutation test which tests the full
    inter-model structure at once.
    """
    model_a: str
    model_b: str
    r: float
    p_value: float
    n_permutations: int


class CentroidPileData(BaseModel):
    """Per-model centroid pile structure published for the PileComparison view.

    Captures the pile groupings and labels from the model's centroid run
    (the run identified by WithinModelResult.centroid_run_id), plus a
    per-term pile-stability metric computed across all of the model's runs.

    Used by the T9 PileComparison frontend component (Phase 9a). Stored in
    DomainResult.centroid_piles, keyed by model_id.

    Field semantics:
    - piles: the pile_sort.parsed_piles list from the centroid run. Each
      inner list is one pile. Item order within a pile is not significant.
    - labels: interview.parsed_pile_labels from the centroid run. One label
      per pile, same ordering as piles. The model's free-text name for
      each pile from the pile interview step (CDA Step 3).
    - term_stability: per-term categorical-uncertainty proxy for R10
      compliance. For each term, the fraction of the model's runs in which
      the term co-occurs with the same set of other terms as in the centroid
      run. "Same pile" is defined by set equality of co-occurring items, NOT
      by pile index (pile ordering is arbitrary). Computed per CDA SME ruling
      F5 (2026-05-24-phase9a-cda-sme-verdict.md): for each run, find the
      pile containing the term, collect the OTHER items in that pile, and
      compare to the centroid run's co-occurring set. Stability = fraction
      of runs where those sets are equal.

    Note: a model with only one run has term_stability = 1.0 for all terms
    (vacuously stable — the single run IS the centroid run). The dashboard
    R10 compliance uses this metric as a categorical-uncertainty indicator
    (opacity or asterisk) per the T9 acceptance criteria.

    See ARCHITECTURE.md §4.2.0 (three-register framework) and
    docs/DATA_DICTIONARY.md §2.3 (CentroidPileData).
    """
    piles: list[list[str]]          # term groupings from centroid run
    labels: list[str]               # one label per pile (from interview.parsed_pile_labels)
    term_stability: dict[str, float] = {}  # item → fraction of runs in same pile as centroid


class RunSummary(BaseModel):
    """Summary of one model run for Focus 1 per-run drill-down.

    Lightweight metadata extracted from InformantRecord. Full per-run
    data (free list items, pile memberships) is available in the open
    data bundle (informants.jsonl); this schema carries only the
    summary needed for the Focus 1 dashboard view.
    """
    run_id: str             # informant_id
    run_index: int
    n_free_list_items: int  # len(freelist.parsed_items)
    n_piles: int            # len(pile_sort.parsed_piles)
    pile_labels: list[str]  # from interview.parsed_pile_labels
    centrality_loading: float  # first-eigenvector loading on run×run agreement matrix


class WithinModelResult(BaseModel):
    """Register 1 result block for one model on one domain.

    See ARCHITECTURE.md §4.2.0 for the three-register framework.
    Populated by the two-level pipeline (PR #6). All fields may be
    null on analysis versions that predate the two-level design.

    The primary measure is the Output Concentration Index (OCI) —
    the eigenratio of the within-model agreement matrix. OCI is a
    concentration statistic, not a cultural consensus statistic; the
    rows of that matrix are iid samples from one stochastic process,
    not distinct cultural agents. See docs/BOOTSTRAP_DESIGN.md §2
    for the underestimation caveat that accompanies every R1 CI.
    """
    model_id: str
    n_runs: int

    # Register 1 primary measure
    oci: float                              # λ₁/λ₂ of within-model agreement matrix
    oci_ci: tuple[float, float] | None = None  # 95% bootstrap CI (see BOOTSTRAP_DESIGN.md)
    underestimates_uncertainty: bool = True  # binding: see §2 of BOOTSTRAP_DESIGN.md

    # Deterministic-output marker (post-F1 SME review, 2026-04-20).
    # True when the run × run agreement matrix has effectively zero second
    # eigenvalue, indicating the model produced near-identical pile-sort
    # structure on every run (zero-variance output distribution). Triggers
    # the ConsensusType = DETERMINISTIC classification and drives the
    # Register 2 visual convention in DESIGN_SYSTEM.md §3.3.5 — not
    # suppression, a distinct marker, because the mismatch is the finding.
    # Does not trigger on any current transformer model at T > 0; reserved
    # for future deterministic architectures (neurosymbolic, zero-temp).
    deterministic_output: bool = False

    # Stability diagnostics
    salience_stability_rho: float | None = None  # Spearman rho of Smith's S across runs
    elbow_stability: bool | None = None          # elbow position stable across N sweeps
    mds_procrustes_rmse: float | None = None     # within-model MDS RMSE across runs

    # Per-run centrality (flags runs most/least representative of this model's
    # central tendency). Used to pick the Option B centroid run for the
    # dashboard display representation per ARCHITECTURE.md §4.2.0.
    centrality_scores_by_run: dict[str, float] = {}
    centroid_run_id: str | None = None   # informant_id of highest-centrality run

    # Within-model MDS (Option B display assets) — Register 1 output.
    # Phase 9a T2 (2026-05-24): populated by pipeline.py as list[dict] where
    # each dict is {"item": str, "x": float, "y": float}.
    # The `Any` element type preserves backward compatibility with pre-Phase-9a
    # records that may carry list[list[float]] from earlier pipeline versions.
    # See docs/DATA_DICTIONARY.md §2.1 (mds_within_model field semantics) and
    # CDA SME F3 (2026-05-24-phase9a-cda-sme-verdict.md): per-model item MDS
    # is Register 1; the underestimates_uncertainty=True annotation applies.
    mds_within_model: list[Any] = []  # list[{"item": str, "x": float, "y": float}]
    within_model_mds_stress: float | None = None  # MDS stress for within-model term MDS

    # Focus 1 fields (2026-05-27). Per-run drill-down data and the run×run
    # agreement matrix that OCI is derived from (previously computed and
    # discarded; now retained for the Focus 1 dashboard view and open data).
    run_agreement_matrix: list[list[float]] = []  # N×N agreement fractions
    run_summaries: list[RunSummary] = []           # per-run metadata summaries


# ──────────────────────────────────────────────────────────────────────
# DomainResult — the type the frontend sees (ARCHITECTURE.md §3.2)
# ──────────────────────────────────────────────────────────────────────

# Romney consensus eigenratio thresholds (post-F1 SME review, §1.1).
# Binding operational gate is 5.0; 3.0 is retained as the classic RWB
# threshold (Romney/Weller/Batchelder 1986) and reported for
# cross-study comparability. A ratio in [3.0, 5.0) is a warning zone:
# passes the classic threshold, fails the operational one.
ROMNEY_THRESHOLD_CLASSIC: float = 3.0
ROMNEY_THRESHOLD_LSB: float = 5.0


class DomainResult(BaseModel):
    """The thing the dashboard serves. One per (domain, analysis_version).

    Note: groundings is a list, NOT a singleton. The v0.7 schema supports
    zero, one, or many human baselines per domain. An empty list means the
    domain is ungrounded — a normal first-class state, not a fallback.
    """
    domain_slug: str
    analysis_version: str
    models: list[ModelRef]
    free_lists: dict[str, FreeList]
    mds_coordinates: dict[str, tuple[float, float]]
    mds_uncertainty: dict[str, BootstrapEllipse]
    similarity_matrix: list[list[float]]
    similarity_ci: list[list[tuple[float, float]]]

    # Register 2 cultural consensus analysis (post-F1 SME review)
    consensus_score: float  # retained as alias for romney_eigenratio;
                            # existing code paths write this. New code
                            # should prefer romney_eigenratio.
    consensus_ci: tuple[float, float]
    romney_eigenratio: float | None = None
    romney_threshold_classic: float = ROMNEY_THRESHOLD_CLASSIC  # = 3.0
    romney_threshold_lsb: float = ROMNEY_THRESHOLD_LSB          # = 5.0
    romney_consensus_pass: bool | None = None       # based on operational 5.0
    romney_consensus_warning: bool | None = None    # 3.0 ≤ ratio < 5.0
    romney_small_n_warning: bool = False  # True when n_models < 15 at Romney
                                          # computation time. Dual-threshold
                                          # pass/fail is statistically under-
                                          # powered below n=15; flag will be
                                          # set on every canonical run until
                                          # corpora grow. See SME verdict
                                          # 2026-04-23 reconciliation
                                          # (docs/status/2026-04-23-small-n-
                                          # threshold-sme-amendment.md) —
                                          # supersedes the F2-T02 n<8
                                          # threshold from 2026-04-20.
    consensus_type: ConsensusType | None = None
    cultural_centrality_scores: dict[str, float] = {}  # model_id → score
    negative_centrality_flag: bool = False
    negative_centrality_models: list[str] = []

    # Pairwise measures (post-F1 SME review)
    cross_model_mantel: list[MantelPair] = []
    cross_model_nolan: list[NolanIndexPair] = []

    # Salience indices (post-F1 SME review, §2.1)
    sutrop_csi: dict[str, list[SutropCSI]] = {}  # per-model CSI lists
    salience_index_agreement: dict[str, float] = {}  # model_id → Spearman ρ
                                                     # between Smith's S and CSI

    # Register 1 within-model results (populated by PR #6 two-level pipeline)
    within_model_results: list[WithinModelResult] = []

    # G1 split stability (SME §1.3 un-deferred 2026-04-20).
    # When populated (after a sensitivity study has run), carries both
    # stability ratios plus the combined pass flag. g1_overall_pass is
    # the binding gate criterion: True iff BOTH axes are below the
    # threshold (0.5 by default). The two individual ratios are diagnostic
    # — a model can be salience-stable and spatially-unstable (or vice
    # versa), and the split reports that distinction rather than
    # collapsing to a single pass/fail. g1_aggregate_stability is the
    # legacy single-axis composite retained for cross-study comparability.
    # Null on analysis versions that predate the un-defer. See
    # packages/cdb_analyze/cdb_analyze/gates.py G1SplitResult.
    g1_salience_stability: float | None = None
    g1_spatial_stability: float | None = None
    g1_aggregate_stability: float | None = None
    g1_salience_pass: bool | None = None
    g1_spatial_pass: bool | None = None
    g1_overall_pass: bool | None = None

    # Grounding
    groundings: list[GroundingRef] = []
    selected_baseline_id: str | None = None

    # Per-model centroid pile structure for the PileComparison view (Phase 9a T9).
    # Keyed by model_id. Each entry holds the centroid run's pile groupings and
    # labels, plus per-term pile-stability scores for R10 compliance.
    # Empty dict when the pipeline has not yet populated centroid pile data.
    # See CentroidPileData docstring and docs/DATA_DICTIONARY.md §2.3.
    centroid_piles: dict[str, CentroidPileData] = {}

    # Term-level MDS (Phase 9a T1/T2).
    # term_mds_coordinates: pooled cross-model term MDS, one (x, y) per term.
    # term_mds_items: ordered item list (deterministic sort) used as the term
    #   index for the pooled MDS — consumers should treat this as the canonical
    #   item ordering for all term-level analyses in this DomainResult.
    # Populated by pipeline.py after the pooled co-occurrence matrix is built
    # via build_pooled_cooccurrence_matrix(). Empty dicts/lists on analysis
    # versions that predate Phase 9a. See docs/DATA_DICTIONARY.md §2.4.
    term_mds_coordinates: dict[str, list[float]] = {}   # item_name → [x, y]
    term_mds_items: list[str] = []                       # ordered item list

    # Term-level AHC (Phase 9a T3).
    # term_cluster_linkage: scipy linkage matrix as nested list; shape (n-1, 4).
    #   Columns: [child_idx_1, child_idx_2, merge_distance, cluster_size].
    #   Average-linkage (UPGMA) per CDA SME M2 (2026-05-24-phase9a-cda-sme-verdict.md).
    #   Row order matches scipy.cluster.hierarchy.linkage() output.
    # term_cluster_assignments: item_name → integer cluster ID at the default cut.
    # term_cluster_labels: one human-readable label per cluster (derived from
    #   model pile labels via the T5 label aggregation pass — left empty by
    #   pipeline.py; populated by the publish layer or T5 task).
    # See docs/DATA_DICTIONARY.md §2.5.
    term_cluster_linkage: list[list[float]] = []         # (n-1, 4) scipy linkage
    term_cluster_assignments: dict[str, int] = {}        # item_name → cluster_id
    term_cluster_labels: list[str] = []                  # one label per cluster

    # Term-level bootstrap uncertainty (Phase 9a T4).
    # term_mds_uncertainty: per-term 95% confidence ellipses on the pooled term MDS.
    #   Stored as dict[str, Any] to allow JSON round-trip via BootstrapEllipse fields.
    #   Populated by bootstrap_term_mds_ellipses() in cdb_analyze/bootstrap.py.
    #   Register 2 output — reflects between-model structural variance only.
    #   Per CDA SME M4/M4a (2026-05-24-phase9a-cda-sme-verdict.md):
    #     "Term position confidence reflects agreement across models, not
    #     within-model sampling variance."
    #   R10 compliance mechanism: the term MDS cannot ship without these ellipses.
    # term_cluster_bp_values: bootstrap proportion (BP) per internal node in the
    #   term AHC dendrogram. One float per row of term_cluster_linkage.
    #   BP = fraction of bootstrap iterations in which the bipartition for that
    #   internal node appears in the bootstrap dendrogram (CDA SME M5).
    #   Dashboard labels as "bootstrap support (%)" not "AU p-value" (M5a).
    #   Branches with BP < 0.70 render with dashed lines (display threshold only,
    #   not a statistical gate).
    # See docs/DATA_DICTIONARY.md §2.6.
    term_mds_uncertainty: dict[str, Any] = {}            # item_name → BootstrapEllipse-like dict
    term_cluster_bp_values: list[float] = []             # BP per internal node (linkage row order)

    # Term-set truncation metadata (Phase 9a term-truncation task).
    # Records the method, parameters, and pre/post item counts for the
    # cross-model frequency elbow truncation step that runs upstream of
    # build_pooled_cooccurrence_matrix(). Required for reproducibility:
    # a different truncation produces a different pooled matrix and therefore
    # different MDS, AHC, and bootstrap outputs.
    # Per CDA SME T5 (2026-05-24-phase9a-term-truncation-sme-ruling.md):
    # "The published DomainResult must carry metadata documenting the
    # truncation. External researchers wishing to replicate the analysis
    # with a different truncation can rebuild from informants.jsonl."
    # Empty string / empty dict / zero values on pre-truncation analysis
    # versions. All four fields default to falsy — no breaking changes.
    term_truncation_method: str = ""      # e.g. "cross_model_frequency_elbow"
    term_truncation_params: dict[str, Any] = {}  # min_items, max_items, min_model_count, elbow_idx
    term_n_total_before_truncation: int = 0      # item count before any truncation
    term_n_after_truncation: int = 0             # item count entering the pooled matrix

    # Output
    generated_lede: str
    generated_at: datetime


# ────────��───────────────────────��───────────────────────────��────────
# InformantRecord and step records (ARCHITECTURE.md §3.2, added v0.6)
# ────���───────────────��───────────────────────────────���────────────────

class FreelistRecord(BaseModel):
    """CDA Step 1 record — free listing."""
    prompt_verbatim: str
    prompt_version: str
    response_verbatim: str
    thinking_verbatim: str = ""
    response_object_json: dict
    input_tokens: int
    output_tokens: int
    thoughts_token_count: int = 0
    latency_ms: int
    stop_reason: str
    parsed_items: list[str]
    parsed_raw_order: list[str]


class PileSortRecord(BaseModel):
    """CDA Step 2 record — pile sorting."""
    prompt_verbatim: str
    prompt_version: str
    response_verbatim: str
    thinking_verbatim: str = ""
    response_object_json: dict
    input_tokens: int
    output_tokens: int
    thoughts_token_count: int = 0
    latency_ms: int
    stop_reason: str
    parsed_piles: list[list[str]]
    parsed_matrix: list[list[int]]
    item_source: str = "own_freelist"


class InterviewRecord(BaseModel):
    """CDA Step 3 record — pile interview / naming."""
    prompt_verbatim: str
    prompt_version: str
    response_verbatim: str
    thinking_verbatim: str = ""
    response_object_json: dict
    input_tokens: int
    output_tokens: int
    thoughts_token_count: int = 0
    latency_ms: int
    stop_reason: str
    parsed_pile_labels: list[str]


class InformantRecord(BaseModel):
    """Full subject record for one LLM-as-informant run on one domain.

    One InformantRecord per (model, domain, run_index). Append-only — never
    overwritten. This is the canonical raw data of LSB and the primary
    content of the open data bundle (see ARCHITECTURE.md §6.7).

    Provenance: every InformantRecord carries the provider's request ID
    (independent audit path through the provider's logs) and a SHA256
    manifest covering the verbatim prompts and verbatim responses
    (cryptographic audit path through the local data). See §1 commitment 7.
    """

    # ── Identity ──
    informant_id: str
    domain_slug: str
    run_index: int
    collection_date: datetime

    # ── Model identity ──
    model_id: str
    model_version_returned: str
    family: str
    provider: Literal[
        "anthropic", "openai", "google", "xai", "cohere",
        "openrouter", "huggingface",
    ]
    provider_request_id: str
    knowledge_cutoff: date | None
    open_weights: bool
    origin_country: Literal["us", "eu", "ca", "cn", "other"]
    alignment_method: str | None

    # ── Collection conditions ──
    collection_method: Literal[
        "anthropic_api", "openrouter", "huggingface", "google_ai",
        "xai_api", "openai_api", "deepseek_api", "mistral_api",
    ]
    collection_mode: Literal[
        "single_pass", "two_pass", "baseline_items", "cross_model_consensus",
    ] = "single_pass"
    api_endpoint: str
    api_version: str
    temperature: float
    top_p: float | None
    max_tokens: int
    system_prompt: str

    # ── CDA step records ──
    freelist: FreelistRecord
    pile_sort: PileSortRecord
    interview: InterviewRecord

    # ── Capacity-constrained truncation (post-F1 SME review, SME_REVIEW.md §1.7) ──
    # LLMs do not fatigue like humans. The natural list length for an LLM is
    # bounded by its context window, not by cognitive exhaustion. These fields
    # record which termination mode ended the free listing and (for
    # ``context_window_exceeded``) which step was affected. A
    # ``context_window_exceeded = True`` value is **not** a QA failure; it is a
    # finding about the architecture's categorical-processing capacity.
    #
    # truncation_type:
    #   "elbow"                    — data-driven elbow cutoff per
    #                                consensus.find_salience_elbow (the normal
    #                                case for well-formed outputs)
    #   "capacity"                  — the model stopped listing on its own at N
    #                                items before hitting any ceiling
    #   "prompt_ceiling"           — the prompt's "aim for ≥ 30" floor was the
    #                                active cap; lift the ceiling to measure
    #                                natural capacity
    #   "context_window_exceeded"  — the model was still generating when the
    #                                provider truncated at max_tokens / context
    truncation_type: Literal[
        "elbow", "capacity", "prompt_ceiling", "context_window_exceeded",
    ] | None = None
    truncation_n: int | None = None        # items kept after truncation
    max_possible_n: int | None = None      # longest list the model could return
                                           # under the no-ceiling condition, if
                                           # known; null for records collected
                                           # under the standard protocol
    context_window_exceeded: bool = False  # True on at least one step; see
                                           # capacity_note for which step
    capacity_note: str = ""                # free-text detail, e.g. "model
                                           # returned 487 items before context
                                           # limit at step 2"

    # ── Provenance ──
    sha256_manifest: dict[str, str]

    # ── QA ──
    qa_passed: bool
    qa_notes: str = ""


# ──────────────────────────────────────────────────────────────────────
# DeclineInterview — follow-up elicitation for failed/refused sessions
# (ARCHITECTURE.md §Stream B, CDA SME verdict 2026-04-23)
# ──────────────────────────────────────────────────────────────────────

class DeclineInterview(BaseModel):
    """Follow-up interview record for a session that failed or returned
    no interpretable primary-step output.

    Produced by Phase 4a.1 remediation and by Phase 4b+ collection when
    the decline-interview protocol triggers. Persisted to
    ``data/raw/decline_interviews.jsonl``, one record per line.

    Exactly one of ``originating_informant_id`` or
    ``originating_failure_id`` must be set (xor invariant). The
    ``_xor_originator`` validator enforces this at construction time.

    ``thinking_verbatim`` captures the **follow-up call's** reasoning
    trace (not the originating session's). Models that do not expose a
    thinking trace will have an empty string here.

    ``version_drift_flag`` is ``True`` when the follow-up's
    ``model_version_returned`` differs from the originating session's
    ``model_version_returned``. Indicates that the provider rolled a
    snapshot between the original collection and the decline-interview
    pass (expected in async Phase 4a.1 scenarios). See SME Note F
    (2026-04-23 verdict).

    See docs/DECLINE_INTERVIEW_PROTOCOL.md and
    docs/DATA_DICTIONARY.md §10 for full field semantics.
    """

    # ── Identity ──
    decline_interview_id: str
    originating_informant_id: str | None = None
    originating_failure_id: str | None = None

    # ── Origin characterisation ──
    originating_step: Literal["freelist", "pile_sort", "interview", "pre_session"]
    originating_outcome_class: Literal[
        "empty_output",
        "refusal_string_match",
        "single_degenerate_pile",
        "parse_failure",
        "http_error",
        "timeout",
        "other",
    ]
    detection_rule_version: str        # "v1" at this commit

    # ── Timestamps ──
    detection_timestamp: datetime
    followup_timestamp: datetime

    # ── Model identity ──
    model_id: str
    model_version_returned: str
    provider: str
    api_endpoint: str

    # ── Prompt provenance ──
    prompt_version: str                 # "decline_v1"
    sha256_manifest: str
    prompt_verbatim: str
    response_verbatim: str
    thinking_verbatim: str = ""         # follow-up call's trace, not originating's

    # ── Token / cost accounting ──
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str

    # ── QA / drift ──
    qa_notes: str = ""
    version_drift_flag: bool = False    # True if follow-up model_version_returned
                                        # differs from originating session's version

    @model_validator(mode="after")
    def _xor_originator(self) -> DeclineInterview:
        """Enforce exactly-one-of originating_informant_id / originating_failure_id."""
        a = self.originating_informant_id is not None
        b = self.originating_failure_id is not None
        if a == b:
            raise ValueError(
                "DeclineInterview requires exactly one of "
                "originating_informant_id or originating_failure_id "
                "(one must be set, the other must be None)"
            )
        return self


# ──────────────────────────────────────────────────────────────────────
# Social publishing pipeline schemas (Phase 7 T1)
# See ARCHITECTURE.md §4.6 and docs/DATA_DICTIONARY.md §13.
# ──────────────────────────────────────────────────────────────────────

class TriggerType(StrEnum):
    """Enumeration of post-worthy event types detected by cdb_social.triggers."""
    NEW_MODEL = "new_model"
    NEW_DOMAIN = "new_domain"
    DRIFT = "drift"
    DIVERGENCE = "divergence"
    MONTHLY_ROUNDUP = "monthly_roundup"


class Platform(StrEnum):
    """Social platform targets. BLUESKY has live publish support in Phase 7;
    X and LINKEDIN are draft-only (see ARCHITECTURE.md §4.6 and Phase 7 §2)."""
    BLUESKY = "bluesky"
    X = "x"
    LINKEDIN = "linkedin"


class PublishStatus(StrEnum):
    """Outcome of a publish attempt recorded in SocialPostRecord."""
    PUBLISHED = "published"
    FAILED = "failed"
    DRY_RUN = "dry_run"
    RETRY_PENDING = "retry_pending"


class SocialTrigger(BaseModel):
    """A post-worthy event detected over the published results store.

    Detection is performed by pure functions in cdb_social.triggers; the
    cron orchestrator decides whether to draft based on the dedupe_key
    and the enable flags per trigger type.
    """
    trigger_type: TriggerType
    detected_at: datetime
    domain_slug: str | None = None
    model_id: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict, description=(
        "Trigger-type-specific evidence payload. The expected shape of this "
        "dict for each TriggerType value is documented in T2's "
        "cdb_social/triggers.py module on the corresponding detect_* "
        "function. The dict[str, Any] shape is the T1↔T2 type-system "
        "contract, not a license for unstructured drift. T2's CDA SME gate "
        "reviews the per-trigger-type evidence-payload schema. "
        "Per CDA SME §5.6. "
        "Minimum keys per TriggerType (defined at T2; listed here for "
        "cross-reference): "
        "NEW_MODEL → {'first_seen_in_domain': str}; "
        "NEW_DOMAIN → {'domain_slug': str, 'n_models': int}; "
        "DIVERGENCE → {'domain_slug': str, 'model_pair': [str, str], "
        "'old_high': float, 'new_high': float, 'gap_delta': float}; "
        "DRIFT → {'model_version_returned': str, 'procrustes_distance': "
        "float, 'date_pair': [str, str]}; "
        "MONTHLY_ROUNDUP → {'month': str (YYYY-MM)}."
    ))
    dedupe_key: str = Field(description=(
        "Stable idempotency key for the trigger event. Construction: "
        "SHA256(trigger_type + '|' + (domain_slug or '') + '|' + "
        "(model_id or '') + '|' + canonical_json(evidence))[:16]. "
        "The formula intentionally excludes drafter_version and "
        "prompt_version. A drafter-prompt bump does not by itself justify "
        "re-firing a posted trigger; if a re-fire is needed (e.g., to "
        "re-publish under a new drafter), that is a manual operation — "
        "the operator removes the entry from "
        "out/social/state/posted_dedupe_keys.json and the next cron run "
        "emits a fresh draft. "
        "Per CDA SME §5.8 — re-firing the same event after a prompt bump "
        "does NOT produce a new draft because dedupe_key is stable across "
        "drafter_version and prompt_version bumps."
    ))


class SocialDraft(BaseModel):
    """A platform-specific draft persisted in out/social/queue/pending/.

    Produced by cdb_social.drafters; reviewed by Mark via the review CLI;
    moved to queue/approved/ on approval and to queue/published/ or
    queue/failed/ on publish.
    """
    draft_id: str = Field(description=(
        "SHA256[:16] of (trigger.dedupe_key + platform + drafter_version "
        "+ prompt_version). A prompt-version bump produces a NEW draft "
        "for an already-seen trigger because draft_id incorporates "
        "prompt_version even though trigger.dedupe_key does not."
    ))
    trigger: SocialTrigger
    platform: Platform
    text: str
    text_history: list[str] = Field(default_factory=list, description=(
        "Append-only history of prior text values when Mark edits via "
        "the review CLI. The current text is in `text`; prior values are "
        "appended here on each edit. Never overwritten."
    ))
    image_path: str | None = None
    suggested_posting_time: datetime = Field(description=(
        "Platform-specific operational hint for posting time based on "
        "audience-engagement windows. Not a methodological signal about "
        "the finding's readiness. The T5 reviewer may override or ignore. "
        "T3 drafters compute this field per platform; the algorithm is "
        "platform-marketing-internal and is not part of LSB's "
        "methodological claims. Per CDA SME §5.5."
    ))
    drafter_self_rating: float = Field(default=0.0, ge=0.0, le=1.0, description=(
        "Drafter's self-reported heuristic score for ordering the "
        "human-review queue (T5's review CLI may sort by this field). "
        "Not calibrated. Not used in any analysis. Not surfaced on the "
        "public dashboard or in the open data bundle. Drafters that do "
        "not produce a self-rating set this to 0.0. The score is not a "
        "methodological signal about draft quality; it is an internal "
        "drafter heuristic for operator convenience. Per CDA SME §5.4 — "
        "renamed from confidence_score to defuse the calibration "
        "implication."
    ))
    methodology_url: str = Field(description=(
        "URL pattern for the methodology page link. Set to the article-"
        "shell URL (cogstructurelab.com/{domain}) while Phase 6 T1+T2 "
        "remain blocked; flip to /methodology once those land."
    ))
    dashboard_url: str
    forbidden_terms_hit: list[str] = Field(default_factory=list, description=(
        "Substrings from the §1.5.4 language-guardrails table "
        "(ARCHITECTURE.md §1.5.4) that the drafter's output matched "
        "during the T3 post-generation validation pass. A draft with any "
        "matched terms must not be admitted to the queue; the "
        "queue-acceptance precondition is forbidden_terms_hit == []. "
        "The T5 review CLI and the T6 publisher both enforce this "
        "precondition. Populated by T3's validate_draft(). "
        "Per CDA SME §5.2. This field's persistence in the schema is a "
        "forensic audit trail — if a draft somehow reaches the queue "
        "with a non-empty list, that is a bug in the drafter validator "
        "and the review CLI must surface it."
    ))
    framing_check_passed: bool = Field(default=False, description=(
        "Single-boolean queue-acceptance signal for the §1.5 / §1.5.7 "
        "framing checks. Default False; the T3 drafter sets to True only "
        "after every per-check entry in framing_checks is True. The "
        "queue-acceptance precondition is framing_check_passed == True "
        "AND every value in framing_checks is True (the redundancy is "
        "intentional: the bool is the fast-grep contract; the dict is "
        "the forensic audit trail). Per CDA SME §5.3."
    ))
    framing_checks: dict[str, bool] = Field(default_factory=dict, description=(
        "Per-check audit trail keyed by framing-check name (e.g., "
        "'hypothesis_framing', 'cognition_attribution', "
        "'bare_numeric_without_ci'). Each value is True if that check "
        "passed. The T3 drafter populates this dict; T5 reviewers and "
        "post-mortem analyses consume it. The exact set of check names "
        "is defined by T3. Per CDA SME §5.3."
    ))
    drafter_version: str
    prompt_version: str
    created_at: datetime


class SocialPostRecord(BaseModel):
    """The publish outcome for a SocialDraft.

    Persisted in out/social/queue/published/{YYYY-MM}/ on success or
    out/social/queue/failed/ on failure.
    """
    draft_id: str
    published_at: datetime
    platform_post_id: str | None = None
    platform_post_url: str | None = None
    publish_status: PublishStatus
    error_message: str | None = None
