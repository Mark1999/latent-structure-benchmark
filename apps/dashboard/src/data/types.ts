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
  semi_major: number;
  semi_minor: number;
  rotation_rad: number;
  n_bootstrap: number;
  ci_level: number;
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

  /** MDS 2D coordinates per model_id. Each value is a [x, y] pair wrapped in an outer array. */
  mds_coordinates: Record<string, [[number, number]]>;

  /** Bootstrap ellipse parameters per model_id. Null values for R1-b / R1-c. */
  mds_uncertainty: Record<string, EllipseParams | null>;

  /** Pairwise similarity matrix as a nested object. */
  similarity_matrix: Record<string, Record<string, number>>;

  /** Pairwise similarity confidence intervals. */
  similarity_ci: Record<string, Record<string, [number, number] | null>>;

  /** Cultural consensus score (0–1). */
  consensus_score: number;

  /** Bootstrap CI for consensus score. */
  consensus_ci: [number, number];

  /** Consensus classification. */
  consensus_type: ConsensusType;

  /** Sutrop CSI salience scores per model_id per term. */
  sutrop_csi: Record<string, Record<string, number>>;

  /** Within-model results array (one entry per model). */
  within_model_results: WithinModelResult[];

  /** Human baselines — empty array for all v1 domains per 2026-05-07 amendment. */
  groundings: unknown[];

  /** Pre-generated lede sentence from cdb_publish T2. */
  generated_lede: string;

  /** ISO timestamp of when this result was generated. */
  generated_at: string;

  /** Display sub-object — precomputed UI helpers added by cdb_publish T3. */
  display: DisplayBlock;
}
