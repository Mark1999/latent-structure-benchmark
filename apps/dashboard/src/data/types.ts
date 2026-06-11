/**
 * TypeScript interfaces mirroring the published domain JSON shape.
 *
 * These types describe the PUBLISHED artifact (output of cdb_publish),
 * NOT the internal cdb_core DomainResult schema. The published JSON
 * includes the `display` sub-object added by T3 (the publish layer).
 *
 * Source: apps/dashboard/public/data/family.json (canonical reference).
 * Updated when cdb_publish output shape changes.
 */

/**
 * Consensus type values matching ARCHITECTURE.md §4.2.
 * Strings match what cdb_analyze / cdb_publish write into the published JSON.
 */
export type ConsensusType =
  | "STRONG_CONSENSUS"
  | "WEAK_CONSENSUS"
  | "SUBCULTURAL"
  | "TURBULENT"
  | "CONTESTED"
  | "DETERMINISTIC";

/**
 * Register 1 state for a single model's within-model output.
 * Source: DESIGN_SYSTEM.md §3.3.5.
 */
export type R1State =
  | "typical_concentration"
  | "low_concentration"
  | "deterministic";

/**
 * Model metadata as published in the domain JSON.
 */
export interface PublishedModel {
  provider: string;
  model_id: string;
  family: string;
  origin: "us" | "eu" | "cn" | string;
  open_weights: boolean;
  collection_method: string;
  quantization: string | null;
  release_date: string;
  version_label: string;
  source_notes: string;
}

/**
 * Within-model result for a single model.
 * Source: WithinModelResult in cdb_analyze.
 */
export interface WithinModelResult {
  model_id: string;
  n_runs: number;
  oci: number;
  oci_ci: [number, number] | null;
  underestimates_uncertainty: boolean;
  deterministic_output: boolean;
  salience_stability_rho: number | null;
  elbow_stability: number | null;
  mds_procrustes_rmse: number | null;
  centrality_scores_by_run: Record<string, number>;
  centroid_run_id: string;
  mds_within_model: number[][];
}

/**
 * Bootstrap ellipse parameters for MDS uncertainty visualization.
 * Fields may be null for R1-b (low concentration) and R1-c (deterministic) models.
 */
export interface EllipseParams {
  center: [number, number];
  semi_major: number;
  semi_minor: number;
  rotation_rad: number;
  n_bootstrap: number;
}

/**
 * Display sub-object added by cdb_publish T3 — precomputed UI helpers.
 */
export interface DisplayBlock {
  /** R1 state per model_id — drives ellipse suppression and marker shape. */
  r1_states: Record<string, R1State>;
  /** Top N terms per model_id by Sutrop CSI salience. */
  top_terms: Record<string, string[]>;
  /** Metric used for salience ranking in top_terms. */
  top_terms_metric: "sutrop_csi";
}

/**
 * A single domain in the manifest's domains array.
 */
export interface ManifestDomain {
  slug: string;
  analysis_version: string;
  n_models: number;
  model_ids: string[];
  generated_at: string;
}

/**
 * The top-level manifest.json structure.
 * Fetched at app startup from /data/manifest.json.
 */
export interface Manifest {
  built_at: string;
  domains: ManifestDomain[];
  /** OCI threshold below which R1-b ellipse suppression applies. */
  oci_low_concentration_threshold: number;
}

// ===== Focus 1 types =====

/**
 * Published run summary for a single pile-sort run.
 * Subset of RunResult exposed in the Focus 1 published JSON.
 */
export interface RunSummaryPublished {
  run_id: string;
  run_index: number;
  n_free_list_items: number;
  n_piles: number;
  pile_labels: string[];
  centrality_loading: number;
}

/**
 * Centroid pile data as published in focus1.json.
 */
export interface CentroidPilesPublished {
  piles: string[][];
  labels: string[];
  term_stability: Record<string, number>;
}

/**
 * Sutrop CSI entry for a single term, as published in focus1.json.
 */
export interface SutropCsiEntry {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  mean_position: number;
}

/**
 * Within-model MDS coordinate entry.
 */
export interface WithinModelMdsItem {
  item: string;
  x: number;
  y: number;
}

/**
 * Focus 1 data for a single model.
 * Extends the within-model fields from WithinModelResult with Focus 1 additions.
 */
export interface Focus1ModelData {
  model_id: string;
  n_runs: number;
  oci: number;
  oci_ci: [number, number] | null;
  underestimates_uncertainty: boolean;
  deterministic_output: boolean;
  salience_stability_rho: number | null;
  elbow_stability: number | null;
  mds_procrustes_rmse: number | null;
  centrality_scores_by_run: Record<string, number>;
  centroid_run_id: string;
  /** Within-model MDS coordinates — list of {item, x, y} objects. */
  mds_within_model: WithinModelMdsItem[];
  /** Stress value from within-model MDS fit. */
  within_model_mds_stress: number | null;
  /** Run-by-run agreement matrix (n_runs × n_runs). */
  run_agreement_matrix: number[][];
  /** Per-run summary data. */
  run_summaries: RunSummaryPublished[];
  /** Centroid piles with term stability. Null if not computed. */
  centroid_piles: CentroidPilesPublished | null;
  /** Sutrop CSI salience ranking for this model in this domain. Null if not computed. */
  sutrop_csi: SutropCsiEntry[] | null;
}

/**
 * The full Focus 1 published file: model_id → Focus1ModelData.
 * Fetched on-demand from /data/{slug}-focus1.json.
 */
export type Focus1Data = Record<string, Focus1ModelData>;

// ===== Domain result types =====

/**
 * Full published domain result.
 * Fetched on-demand from /data/{slug}.json (or /{slug}.v{version}.json).
 */
export interface DomainResultPublished {
  domain_slug: string;
  analysis_version: string;

  /** Models included in this result. */
  models: PublishedModel[];

  /** Free-list term lists per model_id. */
  free_lists: Record<string, string[]>;

  /** MDS 2D coordinates per model_id. Each value is a flat [x, y] pair. */
  mds_coordinates: Record<string, [number, number]>;

  /** Bootstrap ellipse parameters per model_id. Null values for R1-b / R1-c. */
  mds_uncertainty: Record<string, EllipseParams | null>;

  /**
   * Model × model similarity, ordered by `models`.
   * Source: DATA_DICTIONARY.md §1.1 field `similarity_matrix`.
   */
  similarity_matrix: number[][];

  /**
   * Per-cell 95% CI from the bootstrap, ordered by `models`.
   * Source: DATA_DICTIONARY.md §1.1 field `similarity_ci`.
   */
  similarity_ci: ([number, number] | null)[][];

  /**
   * Authoritative row/column order for similarity_matrix and similarity_ci.
   * Length equals similarity_matrix.length. Subset of models[].model_id.
   * Models in `models` but absent here were excluded from the similarity basis
   * (e.g., mode-coherent filtering, centrality-null basis exclusion).
   * Empty array on legacy results pre-FOOD-V02-FIX-SIMIDS; consumers fall back
   * to the legacy invariant (matrix dims == models.length, row i keyed by models[i]).
   */
  similarity_model_ids?: string[];

  /** Cultural consensus score (0–1). */
  consensus_score: number;

  /** Bootstrap CI for consensus score. */
  consensus_ci: [number, number];

  /** Consensus classification (auto-derived; retained for audit trail). */
  consensus_type: ConsensusType;

  /**
   * CDA-SME-mandated override for the published classification label.
   * When non-null, this is the published label; consensus_type retains its
   * auto-derived value for forensic purposes.
   * Published classification = consensus_type_override ?? consensus_type.
   * Added PROMOTE-FOOD-V02 (2026-06-11). See DATA_DICTIONARY.md v0.1.27.
   */
  consensus_type_override?: ConsensusType | null;

  /**
   * Human-readable rationale for consensus_type_override.
   * Empty string when no override is set.
   */
  consensus_type_override_reason?: string | null;

  /**
   * Sutrop CSI salience ranking per model_id.
   * Each value is a list of SutropCsiEntry sorted descending by CSI.
   */
  sutrop_csi: Record<string, SutropCsiEntry[]>;

  /**
   * Per-model centrality scores from the first eigenvector of the
   * inter-model similarity matrix (Caulkins 1999).
   * Source: DATA_DICTIONARY.md §1.1 field `cultural_centrality_scores`.
   */
  cultural_centrality_scores: Record<string, number>;

  /** Within-model results array (one entry per model). */
  within_model_results: WithinModelResult[];

  /** Human baselines — empty array for all v1 domains per 2026-05-07 amendment. */
  groundings: unknown[];

  /** Pre-generated lede sentence from cdb_publish T2. */
  generated_lede: string;

  /** ISO timestamp of when this result was generated. */
  generated_at: string;

  /**
   * Small-n warning: true when n_models < 15 (Romney CCM eigenratio
   * reporting threshold). When true, SourceAttribution surfaces a footnote
   * per CDA SME plan-level Q2 binding.
   */
  romney_small_n_warning: boolean;

  /** Display sub-object — precomputed UI helpers added by cdb_publish T3. */
  display: DisplayBlock;

  /**
   * Per-model 95% bootstrap CI on cultural centrality score.
   * Shape: model_id → [lo, hi] (percentile method, B=500, model-resampling).
   * Empty dict ({}) when n_models < 3 (degenerate regime).
   * Added by Remedy B T2/T3. See DATA_DICTIONARY.md §1.1 for full audit trail.
   */
  centrality_ci?: Record<string, [number, number]>;
}

// ===== Failures types =====

/**
 * A single pipeline retry attempt on a FailureRecord.
 * Mirrors the per-attempt dict in PublishedFailureRecord.retry_attempts
 * from cdb_publish/schemas/failures.py.
 *
 * These are PIPELINE retries: the same prompt was re-issued by LSB after a
 * parser-state failure. There is no per-attempt prompt_verbatim because the
 * prompt is shared across all attempts (AC11 / kickoff §6 Train C register).
 *
 * Source: apps/dashboard/public/data/failures/family.json (canonical reference,
 * lines ~617-640). Added CR-T8.
 */
export interface RetryAttempt {
  attempt_index: number;
  response_verbatim: string;
  thinking_verbatim: string;
  stop_reason?: string | null;
  input_tokens?: number | null;
  output_tokens?: number | null;
  thoughts_token_count?: number | null;
  latency_ms?: number | null;
  parse_error_message?: string | null;
}

/**
 * LSB pipeline outcome class values (7-enum).
 * These name LSB-side detection rules, not model state-of-mind.
 * Source: apps/dashboard/public/data/failures/family.json (canonical reference).
 */
export type FailureOutcomeClass =
  | "empty_output"
  | "refusal_string_match"
  | "single_degenerate_pile"
  | "parse_failure"
  | "http_error"
  | "timeout"
  | "other";

/**
 * A collection failure record: a session that did not produce a parseable
 * primary-step response. record_type === "failure".
 */
export interface FailureRecord {
  record_type: "failure";
  collection_date: string;
  model_id: string;
  domain_slug: string;
  error_type: string;
  error_message: string;
  run_index: number;
  originating_outcome_class: FailureOutcomeClass | null;
  /** Pipeline retry attempts (AC1/AC2, CR-T8). Empty array when no retries occurred. */
  retry_attempts?: RetryAttempt[] | null;
}

/**
 * A decline interview record: a follow-up prompt sent after a failure.
 * record_type === "decline_interview".
 */
export interface DeclineInterviewRecord {
  record_type: "decline_interview";
  collection_date: string;
  model_id: string;
  domain_slug: string;
  decline_interview_id: string;
  originating_informant_id: string | null;
  originating_failure_id: string | null;
  originating_step: string;
  originating_outcome_class: FailureOutcomeClass | null;
  detection_rule_version: string;
  model_version_returned: string;
  provider: string;
  api_endpoint: string;
  prompt_version: string;
  sha256_manifest: string;
  prompt_verbatim: string;
  response_verbatim: string;
  thinking_verbatim: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  stop_reason: string;
  qa_notes: string;
  version_drift_flag: boolean;
  /** Defensive: pipeline retry attempts (AC2/AC12, CR-T8). Runtime expectation: absent on decline_interview records. */
  retry_attempts?: RetryAttempt[] | null;
}

/**
 * Union type for a single record in a failures file.
 */
export type FailuresRecord = FailureRecord | DeclineInterviewRecord;

/**
 * Top-level structure of a failures/{slug}.json file.
 */
export interface FailuresFile {
  domain_slug: string;
  generated_at: string;
  n_records: number;
  n_failure_records: number;
  n_decline_interview_records: number;
  framing_note: string;
  records: FailuresRecord[];
}

// ===== Records summary types (CR-T4 / CR-T5) =====

/**
 * A single row in a per-domain records summary file.
 * Mirrors the published shape in apps/dashboard/public/data/records/{slug}.json.
 * Source: DATA_DICTIONARY.md §12.6.
 */
export interface RecordsModelRow {
  model_id: string;
  provider: string;
  n_runs: number;
  n_qa_passed: number;
  model_version_returned: string;
  model_version_returned_count: number;
}

/**
 * Top-level structure of a records/{slug}.json summary file.
 * Published by cdb_publish successes builder (CR-T4).
 * "Successful" here means the LSB pipeline parsed a primary-step response --
 * NOT a quality judgment on the model output (DATA_DICTIONARY.md §12.6).
 */
export interface RecordsSummaryFile {
  domain_slug: string;
  generated_at: string;
  n_informants: number;
  by_model: RecordsModelRow[];
  framing_note: string;
}

// ===== Per-record detail types (CR-T7) =====

/**
 * Verbatim bytes for one CDA elicitation step.
 * Mirrors PublishedStepExchange in cdb_publish/schemas/successes.py.
 * Per CDA SME N2 disposition (a): prompt_verbatim and response_verbatim
 * are required (non-optional). thinking_verbatim may be empty string.
 */
export interface PublishedStepExchange {
  prompt_verbatim: string;
  response_verbatim: string;
  thinking_verbatim: string;
  model_version_returned: string;
  prompt_version: string;
}

/**
 * Provenance and pipeline identifiers for a single collection session.
 * Mirrors PublishedRecordProvenance in cdb_publish/schemas/successes.py.
 */
export interface PublishedRecordProvenance {
  provider_request_id: string;
  model_id: string;
  model_version_returned: string;
  provider: string;
  domain_slug: string;
  run_index: number;
  collection_date: string;
  sha256_manifest: Record<string, string>;
}

/**
 * Per-record detail JSON: verbatim bytes for all three CDA steps plus
 * provenance identifiers.
 * Mirrors PublishedRecordDetail in cdb_publish/schemas/successes.py.
 *
 * The three step fields (freelist, pile_sort, pile_interview) are
 * non-Optional per CDA SME N2 disposition (a).
 *
 * pile_interview corresponds to InformantRecord.interview (renamed per
 * CDA SME N1 to avoid confusion with the DeclineInterview record kind).
 */
export interface PublishedRecordDetail {
  informant_id: string;
  framing_note_detail: string;
  freelist: PublishedStepExchange;
  pile_sort: PublishedStepExchange;
  pile_interview: PublishedStepExchange;
  provenance: PublishedRecordProvenance;
}

/** Type-guard: is the fetched value a valid PublishedRecordDetail? */
export function isPublishedRecordDetail(val: unknown): val is PublishedRecordDetail {
  if (typeof val !== 'object' || val === null) return false;
  const v = val as Record<string, unknown>;
  if (
    typeof v.informant_id !== 'string' ||
    typeof v.framing_note_detail !== 'string' ||
    typeof v.freelist !== 'object' || v.freelist === null ||
    typeof v.pile_sort !== 'object' || v.pile_sort === null ||
    typeof v.pile_interview !== 'object' || v.pile_interview === null ||
    typeof v.provenance !== 'object' || v.provenance === null
  ) return false;
  // Validate step shape (spot-check the required fields)
  function isStep(s: unknown): s is PublishedStepExchange {
    if (typeof s !== 'object' || s === null) return false;
    const st = s as Record<string, unknown>;
    return (
      typeof st.prompt_verbatim === 'string' &&
      typeof st.response_verbatim === 'string' &&
      typeof st.thinking_verbatim === 'string'
    );
  }
  if (!isStep(v.freelist) || !isStep(v.pile_sort) || !isStep(v.pile_interview)) return false;
  // Validate provenance shape
  const p = v.provenance as Record<string, unknown>;
  return (
    typeof p.provider_request_id === 'string' &&
    typeof p.model_id === 'string' &&
    typeof p.model_version_returned === 'string' &&
    typeof p.sha256_manifest === 'object' && p.sha256_manifest !== null
  );
}

/**
 * Extended domain result carrying optional fields present in published JSON
 * beyond the base DomainResultPublished interface.  Exported so App.tsx and
 * ContentArea.tsx can share a single authoritative definition.
 *
 * All extended fields are optional because they are only populated by some
 * analysis pipeline variants (e.g. term-MDS, centroid piles).
 */
export interface DomainExtended extends DomainResultPublished {
  /** Term-level MDS coordinates: term → [x, y]. */
  term_mds_coordinates?: Record<string, [number, number]>;
  /** Cluster assignment per term (index into term_cluster_labels). */
  term_cluster_assignments?: Record<string, number>;
  /** Human-readable label per cluster index. */
  term_cluster_labels?: string[];
  /**
   * Centroid pile groups per model_id.
   * Shape mirrors TermMap's ModelPileData: { piles: string[][]; labels: string[] }.
   */
  centroid_piles?: Record<string, { piles: string[][]; labels: string[] }>;
  /** Scipy linkage matrix: rows of [idx1, idx2, distance, count]. */
  term_cluster_linkage?: number[][];
  /** Ordered term names corresponding to leaf indices 0..n-1 in the linkage matrix. */
  term_mds_items?: string[];
  /** Bootstrap proportion per internal linkage node (one value per linkage row). */
  term_cluster_bp_values?: number[];
  /** Bootstrap ellipse params for term-level MDS points. */
  term_mds_uncertainty?: Record<string, EllipseParams | null>;
}
