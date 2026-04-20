"""LSB core schemas — the single source of truth for all data contracts.

Defined once here; every other package imports from cdb_core.
See ARCHITECTURE.md §3.2 for the binding specification.

The Reviewer agent must reject any PR that redefines these types elsewhere
or that changes InformantRecord/GroundingRef without a matching update to
docs/DATA_DICTIONARY.md in the same PR.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

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
    cost_usd: float | None


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

    # Within-model MDS (Option B display assets)
    mds_within_model: list[list[float]] = []  # (n_items, 2) item coordinates


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
