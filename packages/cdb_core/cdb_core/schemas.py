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
    collection_method: Literal["anthropic_api", "openrouter", "huggingface"]
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


# ────────────���──────────────────────��─────────────────────────────────
# DomainResult — the type the frontend sees (ARCHITECTURE.md §3.2)
# ──────────────��────────────────────────────────���─────────────────────

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
    consensus_score: float
    consensus_ci: tuple[float, float]
    groundings: list[GroundingRef] = []
    selected_baseline_id: str | None = None
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
    collection_method: Literal["anthropic_api", "openrouter", "huggingface"]
    collection_mode: Literal["single_pass", "two_pass", "baseline_items", "cross_model_consensus"] = "single_pass"
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

    # ── Provenance ──
    sha256_manifest: dict[str, str]

    # ── QA ──
    qa_passed: bool
    qa_notes: str = ""
