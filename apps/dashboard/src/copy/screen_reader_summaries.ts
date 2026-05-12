// apps/dashboard/src/copy/screen_reader_summaries.ts
//
// Single source of truth for T8 Read-as-table toggle labels, table captions,
// empty-state strings, and ScreenReaderSummary programmatic templates.
//
// CDA SME PASS-WITH-NOTES (S1–S11 all applied):
//   docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md
// UI/UX PASS-WITH-NOTES (U1, U2 applied):
//   docs/status/2026-05-12-phase6-T8-uiux-plan-verdict.md
//
// §1.5.4 forbidden vocabulary: all LSB-authored strings in this file have been
// scanned and are clean. Field names (model_id, csi, etc.) are exempt.
//
// IMPORTANT: do NOT reuse domainResult.generated_lede in any template below.
// The generated_lede is consumed only by ArticleHeader.tsx (CDA SME S11).
//
// Do NOT edit without CDA SME re-review.

import type { DomainResultPublished } from "../data/types";

// ── Button labels (CDA SME §3 APPROVED verbatim) ────────────────────────────

/** Button label at rest (readAsTable = false) */
export const READ_AS_TABLE_LABEL_REST = "Read as table";

/** Button label when pressed (readAsTable = true) */
export const READ_AS_TABLE_LABEL_PRESSED = "Show visualization";

// ── Table captions (CDA SME §4 binding verbatim) ────────────────────────────

/**
 * MDS table caption — binding verbatim per CDA SME §4.1.
 * Do NOT paraphrase or alter without CDA SME re-approval.
 */
export const MDS_TABLE_CAPTION =
  "Each row shows where one model lands on the MDS map and the bootstrap uncertainty around that position. Rows showing — under semi-major / semi-minor / rotation have no confidence ellipse — their output distribution had low variability or was deterministic, so the bootstrap could not estimate a position uncertainty.";

/**
 * FreeList per-model table caption template — binding verbatim per CDA SME §4.2.
 * Cross-surface consistency with T7 N5.1: "this model's collection runs" verbatim.
 * Do NOT paraphrase or alter without CDA SME re-approval.
 */
export function freeListTableCaption(modelShortName: string): string {
  return `${modelShortName}'s ranked terms for this domain, ordered by Sutrop salience score. The inclusion-frequency column shows the fraction of this model's collection runs that produced each term.`;
}

/**
 * Similarity table caption — binding verbatim per CDA SME §4.3.
 * Cross-surface consistency with T5 "no shared structure" framing verbatim.
 * Do NOT paraphrase or alter without CDA SME re-approval.
 */
export const SIMILARITY_TABLE_CAPTION =
  "Each row compares two models in the current selection. The similarity column shows how similarly the two models organize this domain (1.00 = identical organization; 0.50 = no shared structure); the 95% confidence interval columns show the bootstrap range around that value. Rows showing — under the confidence interval columns have no bootstrap interval available.";

// ── Empty-state captions (CDA SME S8 binding) ───────────────────────────────

/** MDS table empty state (no models selected) — CDA SME S8 APPROVED. */
export const MDS_TABLE_EMPTY_NO_MODELS =
  "Select one or more models to see the MDS coordinates table.";

/**
 * FreeList table empty state (no models selected) — CDA SME S8 revised.
 * Adds "for this domain" for scope-anchor symmetry with the table caption.
 */
export const FREELIST_TABLE_EMPTY_NO_MODELS =
  "Select one or more models to see the ranked-term tables for this domain.";

/**
 * Similarity table empty state (< 2 models) — CDA SME S8 revised.
 * Adds "pairwise" for symmetry with SR template's "pairwise similarity scores".
 */
export const SIMILARITY_TABLE_EMPTY_LT_2_MODELS =
  "Select at least two models to see the pairwise similarity table.";

// ── FreeList per-model empty-state captions (carry-forward from T7) ─────────

/** FreeList Case B: no sutrop_csi data for this model */
export const FREELIST_CASE_B_CAPTION = "(no salience data for this model)";

/** FreeList Case C: sutrop_csi exists but is empty */
export const FREELIST_CASE_C_CAPTION = "(no terms produced)";

// ── Consensus-type mapping (CDA SME S1 binding) ─────────────────────────────

/**
 * Maps consensus_type enum to plain-English Register-2 phrase.
 * CDA SME §2.1 binding wording — do NOT render bare enum strings.
 * Returns null for null/absent consensus_type (Sentence 2 is omitted).
 */
export function mapConsensusType(
  consensusType: string | null | undefined
): string | null {
  switch (consensusType) {
    case "STRONG_CONSENSUS":
      return "strong consensus (the models organize this domain similarly)";
    case "WEAK_CONSENSUS":
      return "weak consensus (the models partly agree on how to organize this domain)";
    case "TURBULENT":
      return "turbulent (no shared organizing structure across the model slate)";
    case "CONTESTED":
      return "contested (the models split into subgroups with different organizing structures)";
    case "SUBCULTURAL":
      return "subcultural (the models split into subgroups with internally-coherent organizing structures)";
    default:
      return null;
  }
}

// ── ScreenReaderSummary template functions ───────────────────────────────────

// Shape interfaces matching actual JSON (T14 doc-sweep concern)
interface SutropCsiItemActual {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  mean_position: number;
}

/**
 * MDS ScreenReaderSummary — CDA SME §2.1 binding output.
 * Up to 3 sentences. ≤ 3 sentence ceiling (CDA SME S10).
 * Does NOT use generated_lede (CDA SME S11).
 *
 * Sentence 1: model count + map description (always).
 * Sentence 2: Caulkins consensus-type classification (if consensus_type is non-null).
 * Sentence 3: R1-state suppressed-ellipse count (conditional on n_low + n_det > 0).
 */
export function mdsScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  const n_selected = selectedModels.length;

  if (n_selected === 0) {
    return "";
  }

  const r1_states =
    (domainResult.display?.r1_states as Record<string, string> | undefined) ?? {};
  const n_low = selectedModels.filter(
    (m) => r1_states[m] === "low_concentration"
  ).length;
  const n_det = selectedModels.filter(
    (m) => r1_states[m] === "deterministic"
  ).length;

  const consensus_phrase = mapConsensusType(domainResult.consensus_type as string | null | undefined);

  // Sentence 1 — model count + map description
  const s1 = `This chart places ${n_selected} ${n_selected === 1 ? "model" : "models"} on a two-dimensional map according to how their outputs categorize this domain; models with more similar categorical structure sit closer together.`;

  // Sentence 2 — Caulkins consensus-type classification (Register 2; omitted when null)
  const s2 =
    consensus_phrase !== null
      ? `Across the full model slate, the between-model agreement matrix classifies as ${consensus_phrase}.`
      : null;

  // Sentence 3 — R1-state suppressed-ellipse count (omitted when 0)
  const n_suppressed = n_low + n_det;
  const s3 =
    n_suppressed > 0
      ? `${n_suppressed} of these ${n_selected} ${n_selected === 1 ? "model has" : "models have"} no confidence ellipse on the map; their output distributions had low variability or were deterministic, and the bootstrap could not estimate a position uncertainty.`
      : null;

  return [s1, s2, s3].filter(Boolean).join(" ");
}

/**
 * FreeList ScreenReaderSummary — CDA SME §2.2 binding output.
 * Up to 2 sentences (or single empty-state sentence). ≤ 2 sentence ceiling (CDA SME S10).
 * Does NOT use generated_lede (CDA SME S11).
 *
 * Sentence 1: selected model count + what FreeListCompare shows.
 * Sentence 2: term-count range + shared-term count (conditional on n_selected >= 2).
 */
export function freeListScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  const n_selected = selectedModels.length;

  if (n_selected === 0) {
    return "(Select one or more models to see free-list summary.)";
  }

  // Cast-through-unknown: actual JSON is Record<string, Array<SutropCsiItemActual>>
  const rawSutropCsi = domainResult.sutrop_csi as unknown as Record<
    string,
    Array<SutropCsiItemActual>
  >;

  // Sentence 1 — selected model count + what FreeListCompare shows
  const s1 = `This chart shows the terms each of ${n_selected} ${n_selected === 1 ? "selected model" : "selected models"} produced for this domain, ordered by Sutrop salience score and paired with the fraction of collection runs that produced each term.`;

  if (n_selected === 1) {
    // Single model: report term count directly
    const terms = rawSutropCsi?.[selectedModels[0]];
    const max_terms = terms ? terms.length : 0;
    const s2 = `The selected model produced ${max_terms} terms for this domain.`;
    return `${s1} ${s2}`;
  }

  // n_selected >= 2: term-count range + shared-term count
  const termCounts = selectedModels.map((m) => {
    const terms = rawSutropCsi?.[m];
    return terms ? terms.length : 0;
  });
  const min_terms = Math.min(...termCounts);
  const max_terms = Math.max(...termCounts);

  // Compute shared terms (intersection across all selected models)
  const termSets = selectedModels
    .map((m) => {
      const terms = rawSutropCsi?.[m];
      if (!terms || terms.length === 0) return null;
      return new Set(terms.map((t) => t.item));
    })
    .filter((s): s is Set<string> => s !== null);

  let n_shared = 0;
  if (termSets.length >= 2) {
    const [first, ...rest] = termSets;
    const intersection = new Set<string>();
    for (const item of first) {
      if (rest.every((s) => s.has(item))) {
        intersection.add(item);
      }
    }
    n_shared = intersection.size;
  }

  const s2 = `Term counts range from ${min_terms} to ${max_terms} across the selected models; ${n_shared} ${n_shared === 1 ? "term appears" : "terms appear"} in every selected model's list.`;

  return `${s1} ${s2}`;
}

/**
 * Similarity ScreenReaderSummary — CDA SME §2.3 binding output.
 * Up to 3 sentences. ≤ 3 sentence ceiling (CDA SME S10).
 * Does NOT use generated_lede (CDA SME S11).
 * Cross-surface consistency with T5: "no shared structure" verbatim (CDA SME S3).
 *
 * Sentence 1: pairwise count + what the heatmap shows (n_selected >= 2).
 * Sentence 2: off-diagonal similarity range (n_selected >= 2).
 * Sentence 3: CI-includes-null count + null-CI count (conditional).
 */
export function similarityScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  const n_selected = selectedModels.length;

  if (n_selected < 2) {
    return "(Select at least two models to see similarity summary.)";
  }

  // Cast-through-unknown: actual JSON is number[][] and [number,number][][]
  const rawSimilarityMatrix = domainResult.similarity_matrix as unknown as number[][];
  const rawSimilarityCi = domainResult.similarity_ci as unknown as Array<
    Array<[number, number] | null>
  >;

  // Build modelIndexMap: model_id → index in domainResult.models array
  const modelIndexMap = new Map<string, number>();
  domainResult.models.forEach((m, i) => {
    modelIndexMap.set(m.model_id, i);
  });

  // displayedIds: selectedModels sorted lexicographically (matches SimilarityHeatmap §2.8)
  const displayedIds = [...selectedModels].sort();
  const n = displayedIds.length;
  const n_pairs = (n * (n - 1)) / 2;

  // Collect off-diagonal similarity values and CI data
  const offDiagonalSims: number[] = [];
  let n_dashed = 0;
  let n_no_ci = 0;

  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const matI = modelIndexMap.get(displayedIds[i]) ?? 0;
      const matJ = modelIndexMap.get(displayedIds[j]) ?? 0;
      const sim = rawSimilarityMatrix[matI]?.[matJ] ?? 0;
      const ci: [number, number] | null = rawSimilarityCi?.[matI]?.[matJ] ?? null;

      offDiagonalSims.push(sim);

      if (ci === null) {
        n_no_ci++;
      } else if (ci[0] < 0.5 && 0.5 < ci[1]) {
        n_dashed++;
      }
    }
  }

  const min_sim = offDiagonalSims.length > 0 ? Math.min(...offDiagonalSims) : 0;
  const max_sim = offDiagonalSims.length > 0 ? Math.max(...offDiagonalSims) : 0;
  const median_sim = (() => {
    if (offDiagonalSims.length === 0) return 0;
    const sorted = [...offDiagonalSims].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0
      ? sorted[mid]
      : (sorted[mid - 1] + sorted[mid]) / 2;
  })();

  // Sentence 1 — pairwise count + what the heatmap shows
  const s1 = `This chart shows pairwise similarity scores between each of ${n_pairs} unordered model ${n_pairs === 1 ? "pair" : "pairs"} from the ${n_selected} selected models; 1.00 indicates identical categorical organization and 0.50 indicates no shared structure between the two models' co-occurrence patterns.`;

  // Sentence 2 — off-diagonal similarity range
  const s2 = `Off-diagonal similarity scores range from ${min_sim.toFixed(2)} to ${max_sim.toFixed(2)}, with a median of ${median_sim.toFixed(2)}.`;

  // Sentence 3 — CI-includes-null count (conditional per CDA SME §2.3)
  let s3: string | null = null;
  if (n_dashed > 0 && n_no_ci > 0) {
    s3 = `${n_dashed} of the ${n_pairs} ${n_pairs === 1 ? "pair has" : "pairs have"} a 95% confidence interval that includes the no-shared-structure value of 0.50; on the heatmap these cells are shown with a dashed border. Additionally, ${n_no_ci} of the ${n_pairs} ${n_pairs === 1 ? "pair has" : "pairs have"} no confidence interval available; on the heatmap these cells are shown without a numeric range.`;
  } else if (n_dashed > 0) {
    s3 = `${n_dashed} of the ${n_pairs} ${n_pairs === 1 ? "pair has" : "pairs have"} a 95% confidence interval that includes the no-shared-structure value of 0.50; on the heatmap these cells are shown with a dashed border.`;
  } else if (n_no_ci > 0) {
    s3 = `${n_no_ci} of the ${n_pairs} ${n_pairs === 1 ? "pair has" : "pairs have"} no confidence interval available; on the heatmap these cells are shown without a numeric range.`;
  }
  // If n_dashed === 0 AND n_no_ci === 0, omit Sentence 3 entirely.

  return [s1, s2, s3].filter(Boolean).join(" ");
}
