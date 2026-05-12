/**
 * InspectRoot — operator inspection mode root component.
 *
 * Rendered by App.tsx when ?inspect=<slug> is present in the URL.
 * Surfaces every published field in manifest.json and per-domain JSON
 * as flat HTML tables so Mark can inspect the published data without
 * dropping to raw JSON.
 *
 * SCOPE CONSTRAINT (Phase 6 T0): This is a VIEWER, not a tool.
 * Do NOT add sort/filter/search affordances, CSV export, pagination,
 * collapse/expand, dark mode, mobile-specific styles, or react-router-dom.
 * Do NOT add <details> collapse anywhere — all rows render inline.
 * Any such additions must go through the Architect.
 *
 * Reference: docs/status/2026-05-12-phase6-T0-architect-plan.md
 * UI/UX verdict: docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md (PASS-WITH-NOTES)
 *
 * Type/JSON shape note (deferred to Phase 6 T14 doc-sweep):
 *   data/types.ts disagrees with live JSON in three places:
 *   1. similarity_matrix: typed Record<string,Record<string,number>> but JSON is number[][]
 *   2. similarity_ci: typed Record<...> but JSON is [number,number][][]
 *   3. mds_coordinates: typed Record<string,[[number,number]]> but JSON is Record<string,[number,number]>
 *   T0 follows the live JSON, not the types. Casts through `unknown` at this boundary.
 *   See DataExplorer.tsx lines 152, 192, 229 for the same pattern.
 */

import { useEffect, useState } from "react";
import { fetchManifest, fetchDomain } from "../api/client";
import type { Manifest } from "../data/types";
import { InspectSection } from "./InspectSection";
import { InspectTable } from "./InspectTable";
import type { ColumnDef } from "./InspectTable";

// ── Local narrower interfaces matching the actual JSON shape ─────────────────
// (NOT data/types.ts which is partially mismatched — see file header note)

interface FreeListEntry {
  run_id: string;
  model: Record<string, unknown>;
  domain_slug: string;
  items: string[];
  raw_order?: string[];
}

interface SutropCsiItem {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  mean_position: number;
}

interface EllipseParamsActual {
  center?: [number, number];
  semi_major?: number;
  semi_minor?: number;
  rotation_rad?: number;
  n_bootstrap?: number;
  ci_level?: number | null;
}

// The actual published domain JSON top-level shape (matches live JSON, not types.ts)
type RawDomainJSON = Record<string, unknown>;

interface InspectRootProps {
  mode: string;  // inspect slug from ?inspect=<slug>
  manifest: Manifest | null;  // may be null if App.tsx fetch is still in progress
}

// ── Known section keys (for "Other top-level fields" fallback) ────────────────

const DOMAIN_KNOWN_KEYS = new Set([
  "domain_slug",
  "analysis_version",
  "generated_at",
  "generated_lede",
  "models",
  "free_lists",
  "mds_coordinates",
  "mds_uncertainty",
  "similarity_matrix",
  "similarity_ci",
  "consensus_score",
  "consensus_ci",
  "consensus_type",
  "romney_eigenratio",
  "romney_threshold_classic",
  "romney_threshold_lsb",
  "romney_consensus_pass",
  "romney_consensus_warning",
  "romney_small_n_warning",
  "cultural_centrality_scores",
  "negative_centrality_flag",
  "negative_centrality_models",
  "cross_model_mantel",
  "cross_model_nolan",
  "sutrop_csi",
  "salience_index_agreement",
  "within_model_results",
  "g1_salience_stability",
  "g1_spatial_stability",
  "g1_aggregate_stability",
  "g1_salience_pass",
  "g1_spatial_pass",
  "g1_overall_pass",
  "groundings",
  "selected_baseline_id",
  "display",
]);

// ── Nav link helper ───────────────────────────────────────────────────────────

function InspectNav({ activeMode }: { activeMode: string }) {
  const modes = [
    { slug: "manifest", label: "Manifest" },
    { slug: "family", label: "Family domain" },
    { slug: "holidays", label: "Holidays domain" },
  ];
  return (
    <nav className="inspect-nav" aria-label="Inspection modes">
      {modes.map(({ slug, label }) => (
        <a
          key={slug}
          href={`?inspect=${slug}`}
          className={
            activeMode === slug ? "inspect-nav__link inspect-nav__link--active" : "inspect-nav__link"
          }
          aria-current={activeMode === slug ? "page" : undefined}
        >
          {label}
        </a>
      ))}
    </nav>
  );
}

// ── Manifest mode renderer ────────────────────────────────────────────────────

function ManifestView({ manifest }: { manifest: Manifest }) {
  const topLevelCols: ColumnDef[] = [
    { key: "field", label: "Field" },
    { key: "value", label: "Value" },
  ];
  const topLevelRows = [
    { field: "built_at", value: manifest.built_at },
    {
      field: "oci_low_concentration_threshold",
      value: manifest.oci_low_concentration_threshold,
    },
  ];

  const domainCols: ColumnDef[] = [
    { key: "slug", label: "slug" },
    { key: "analysis_version", label: "analysis_version" },
    { key: "n_models", label: "n_models" },
    { key: "generated_at", label: "generated_at" },
    { key: "model_ids", label: "model_ids" },
  ];
  const domainRows = manifest.domains.map((d) => ({
    slug: d.slug,
    analysis_version: d.analysis_version,
    n_models: d.n_models,
    generated_at: d.generated_at,
    model_ids: d.model_ids,
  }));

  return (
    <>
      <InspectSection title="Manifest top-level">
        <InspectTable
          caption="Manifest scalar fields"
          columns={topLevelCols}
          rows={topLevelRows}
        />
      </InspectSection>

      <InspectSection title="Domains in this manifest">
        <InspectTable
          caption={`Domains in manifest (${domainRows.length} domain${domainRows.length !== 1 ? "s" : ""})`}
          columns={domainCols}
          rows={domainRows}
        />
      </InspectSection>
    </>
  );
}

// ── Domain mode renderer ──────────────────────────────────────────────────────

function DomainView({
  domain,
  slug,
  manifestDomain,
}: {
  domain: RawDomainJSON;
  slug: string;
  manifestDomain: Manifest["domains"][number] | undefined;
}) {
  const modelIds: string[] = Array.isArray(domain["models"])
    ? (domain["models"] as Record<string, unknown>[]).map(
        (m) => String(m["model_id"] ?? "")
      )
    : [];

  // §2.4 Domain header
  const headerCols: ColumnDef[] = [
    { key: "field", label: "Field" },
    { key: "value", label: "Value" },
  ];
  const headerRows = [
    { field: "domain_slug", value: domain["domain_slug"] },
    { field: "analysis_version", value: domain["analysis_version"] },
    { field: "generated_at", value: domain["generated_at"] },
    { field: "generated_lede", value: domain["generated_lede"] },
  ];

  // §2.4 Models in this domain
  const modelsCols: ColumnDef[] = [
    { key: "provider", label: "provider" },
    { key: "model_id", label: "model_id" },
    { key: "family", label: "family" },
    { key: "origin", label: "origin" },
    { key: "open_weights", label: "open_weights" },
    { key: "collection_method", label: "collection_method" },
    { key: "quantization", label: "quantization" },
    { key: "release_date", label: "release_date" },
    { key: "version_label", label: "version_label" },
    { key: "source_notes", label: "source_notes" },
  ];
  const modelsRows: Record<string, unknown>[] = Array.isArray(domain["models"])
    ? (domain["models"] as Record<string, unknown>[])
    : [];

  // §2.4 MDS coordinates — actual shape: Record<string, [number, number]>
  const rawMdsCoords = domain["mds_coordinates"] as unknown as Record<
    string,
    [number, number]
  >;
  const mdsCoordCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "x", label: "x" },
    { key: "y", label: "y" },
  ];
  const mdsCoordRows = Object.entries(rawMdsCoords ?? {}).map(
    ([model_id, coords]) => ({
      model_id,
      x: Array.isArray(coords) ? coords[0] : null,
      y: Array.isArray(coords) ? coords[1] : null,
    })
  );

  // §2.4 MDS uncertainty — R10: rendered immediately after MDS coordinates
  const rawMdsUnc = domain["mds_uncertainty"] as Record<
    string,
    EllipseParamsActual | null
  >;
  const mdsUncCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "center_x", label: "center_x" },
    { key: "center_y", label: "center_y" },
    { key: "semi_major", label: "semi_major" },
    { key: "semi_minor", label: "semi_minor" },
    { key: "rotation_rad", label: "rotation_rad" },
    { key: "n_bootstrap", label: "n_bootstrap" },
    { key: "ci_level", label: "ci_level" },
  ];
  const mdsUncRows = Object.entries(rawMdsUnc ?? {}).map(([model_id, unc]) => ({
    model_id,
    center_x: unc?.center ? unc.center[0] : null,
    center_y: unc?.center ? unc.center[1] : null,
    semi_major: unc?.semi_major ?? null,
    semi_minor: unc?.semi_minor ?? null,
    rotation_rad: unc?.rotation_rad ?? null,
    n_bootstrap: unc?.n_bootstrap ?? null,
    ci_level: unc?.ci_level ?? null,
  }));

  // §2.4 Similarity matrix — actual shape: number[][] indexed by models order
  const rawSimMatrix = domain["similarity_matrix"] as unknown as number[][];
  const simMatrixCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    ...modelIds.map((id) => ({ key: id, label: id })),
  ];
  const simMatrixRows = Array.isArray(rawSimMatrix)
    ? rawSimMatrix.map((row, i) => {
        const r: Record<string, unknown> = { model_id: modelIds[i] ?? String(i) };
        if (Array.isArray(row)) {
          row.forEach((val, j) => {
            r[modelIds[j] ?? String(j)] = val;
          });
        }
        return r;
      })
    : [];

  // §2.4 Similarity CI — actual shape: [number,number][][] — R10: rendered immediately after matrix
  const rawSimCI = domain["similarity_ci"] as unknown as ([number, number] | null)[][];
  const simCICols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    ...modelIds.map((id) => ({ key: id, label: id })),
  ];
  const simCIRows = Array.isArray(rawSimCI)
    ? rawSimCI.map((row, i) => {
        const r: Record<string, unknown> = { model_id: modelIds[i] ?? String(i) };
        if (Array.isArray(row)) {
          row.forEach((val, j) => {
            r[modelIds[j] ?? String(j)] =
              val === null ? null : `[${(val as number[]).join(", ")}]`;
          });
        }
        return r;
      })
    : [];

  // §2.4 Consensus (consensus_score + consensus_ci paired — R10)
  const consensusCols: ColumnDef[] = [
    { key: "field", label: "Field" },
    { key: "value", label: "Value" },
  ];
  const consensusRows = [
    { field: "consensus_score", value: domain["consensus_score"] },
    { field: "consensus_ci", value: domain["consensus_ci"] },
    { field: "consensus_type", value: domain["consensus_type"] },
    { field: "romney_eigenratio", value: domain["romney_eigenratio"] },
    { field: "romney_threshold_classic", value: domain["romney_threshold_classic"] },
    { field: "romney_threshold_lsb", value: domain["romney_threshold_lsb"] },
    { field: "romney_consensus_pass", value: domain["romney_consensus_pass"] },
    { field: "romney_consensus_warning", value: domain["romney_consensus_warning"] },
    { field: "romney_small_n_warning", value: domain["romney_small_n_warning"] },
  ];

  // §2.4 Cultural centrality
  const rawCentrality = domain["cultural_centrality_scores"] as Record<
    string,
    number
  > | null;
  const centralityCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "score", label: "cultural_centrality_score" },
  ];
  const centralityRows = Object.entries(rawCentrality ?? {}).map(
    ([model_id, score]) => ({ model_id, score })
  );
  const centralityFlagCols: ColumnDef[] = [
    { key: "field", label: "Field" },
    { key: "value", label: "Value" },
  ];
  const centralityFlagRows = [
    { field: "negative_centrality_flag", value: domain["negative_centrality_flag"] },
    { field: "negative_centrality_models", value: domain["negative_centrality_models"] },
  ];

  // §2.4 Cross-model agreement
  const crossMantel = domain["cross_model_mantel"];
  const crossNolan = domain["cross_model_nolan"];
  const crossIsEmpty =
    Array.isArray(crossMantel) &&
    crossMantel.length === 0 &&
    Array.isArray(crossNolan) &&
    crossNolan.length === 0;

  // §2.4 Sutrop CSI — per model
  const rawSutrop = domain["sutrop_csi"] as Record<
    string,
    SutropCsiItem[]
  > | null;
  const sutropCols: ColumnDef[] = [
    { key: "item", label: "item" },
    { key: "csi", label: "csi" },
    { key: "f_mentions", label: "f_mentions" },
    { key: "n_runs", label: "n_runs" },
    { key: "mean_position", label: "mean_position" },
  ];

  // §2.4 Salience index agreement
  const rawSalience = domain["salience_index_agreement"] as Record<
    string,
    number
  > | null;
  const salienceCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "score", label: "salience_index_agreement" },
  ];
  const salienceRows = Object.entries(rawSalience ?? {}).map(
    ([model_id, score]) => ({ model_id, score })
  );

  // §2.4 Within-model results — R10: oci + oci_ci columns adjacent
  const rawWmr = domain["within_model_results"] as Record<
    string,
    unknown
  >[];
  const wmrCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "n_runs", label: "n_runs" },
    { key: "oci", label: "oci" },
    { key: "oci_ci", label: "oci_ci" },
    { key: "underestimates_uncertainty", label: "underestimates_uncertainty" },
    { key: "deterministic_output", label: "deterministic_output" },
    { key: "salience_stability_rho", label: "salience_stability_rho" },
    { key: "elbow_stability", label: "elbow_stability" },
    { key: "mds_procrustes_rmse", label: "mds_procrustes_rmse" },
    { key: "centroid_run_id", label: "centroid_run_id" },
    { key: "centrality_scores_by_run", label: "centrality_scores_by_run" },
    { key: "mds_within_model", label: "mds_within_model" },
  ];
  const wmrRows: Record<string, unknown>[] = Array.isArray(rawWmr) ? rawWmr : [];

  // §2.4 G1 stability fields
  const g1Rows = [
    { field: "g1_salience_stability", value: domain["g1_salience_stability"] },
    { field: "g1_spatial_stability", value: domain["g1_spatial_stability"] },
    { field: "g1_aggregate_stability", value: domain["g1_aggregate_stability"] },
    { field: "g1_salience_pass", value: domain["g1_salience_pass"] },
    { field: "g1_spatial_pass", value: domain["g1_spatial_pass"] },
    { field: "g1_overall_pass", value: domain["g1_overall_pass"] },
  ];

  // §2.4 Display block
  const rawDisplay = domain["display"] as {
    r1_states?: Record<string, string>;
    top_terms?: Record<string, string[]>;
    top_terms_metric?: string;
  } | null;
  const r1StatesCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "r1_state", label: "r1_state" },
  ];
  const r1StatesRows = Object.entries(rawDisplay?.r1_states ?? {}).map(
    ([model_id, r1_state]) => ({ model_id, r1_state })
  );
  const topTermsCols: ColumnDef[] = [
    { key: "model_id", label: "model_id" },
    { key: "top_terms", label: "top_terms" },
  ];
  const topTermsRows = Object.entries(rawDisplay?.top_terms ?? {}).map(
    ([model_id, top_terms]) => ({ model_id, top_terms })
  );

  // §2.4 "Other top-level fields" fallback — schema-drift safety net
  const otherKeys = Object.keys(domain).filter((k) => !DOMAIN_KNOWN_KEYS.has(k));

  return (
    <>
      {/* §2.4 Domain header */}
      <InspectSection title="Domain header">
        {manifestDomain && (
          <p className="inspect-section__description" style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-caption)" }}>
            {`Manifest entry for "${slug}": analysis_version ${manifestDomain.analysis_version}, ${manifestDomain.n_models} models.`}
          </p>
        )}
        <InspectTable
          caption="Domain scalar fields"
          columns={headerCols}
          rows={headerRows}
        />
      </InspectSection>

      {/* §2.4 Models in this domain */}
      <InspectSection title="Models in this domain">
        <InspectTable
          caption={`Models (${modelsRows.length} total)`}
          columns={modelsCols}
          rows={modelsRows}
        />
      </InspectSection>

      {/* §2.4 Free lists (per model) — rendered inline, no collapse */}
      <InspectSection
        title="Free lists (per model)"
        description="Consensus free-list items and raw-order terms per model. Rendered inline — no collapse."
      >
        {Object.entries(
          (domain["free_lists"] as Record<string, FreeListEntry>) ?? {}
        ).map(([modelId, fl]) => {
          const items: string[] = fl?.items ?? [];
          const rawOrder: string[] = fl?.raw_order ?? [];
          const freeCols: ColumnDef[] = [
            { key: "rank", label: "rank" },
            { key: "canonical_item", label: "canonical_item" },
            { key: "raw_order_item", label: "raw_order_item" },
          ];
          const freeRows = items.map((item, idx) => ({
            rank: idx + 1,
            canonical_item: item,
            raw_order_item: rawOrder[idx] ?? "",
          }));
          return (
            <div key={modelId} className="inspect-freelist-block">
              <InspectTable
                caption={`${modelId} — ${items.length} terms`}
                columns={freeCols}
                rows={freeRows}
              />
            </div>
          );
        })}
      </InspectSection>

      {/* §2.4 MDS coordinates — R10: paired with uncertainty table immediately below */}
      <InspectSection title="MDS coordinates">
        <InspectTable
          caption="MDS 2D coordinates per model (x, y)"
          columns={mdsCoordCols}
          rows={mdsCoordRows}
        />
      </InspectSection>

      {/* §2.4 MDS uncertainty (bootstrap ellipses) — R10 satisfied: rendered immediately after MDS coordinates */}
      <InspectSection
        title="MDS uncertainty (bootstrap ellipses)"
        description="Bootstrap ellipse parameters paired with MDS coordinates above. R10: CI visible alongside every point estimate."
      >
        <InspectTable
          caption="Bootstrap ellipse parameters per model"
          columns={mdsUncCols}
          rows={mdsUncRows}
        />
      </InspectSection>

      {/* §2.4 Similarity matrix */}
      <InspectSection title="Similarity matrix">
        <InspectTable
          caption={`Pairwise similarity matrix (${modelIds.length} × ${modelIds.length})`}
          columns={simMatrixCols}
          rows={simMatrixRows}
        />
      </InspectSection>

      {/* §2.4 Similarity CIs — R10: rendered immediately after similarity matrix */}
      <InspectSection
        title="Similarity confidence intervals"
        description="Pairwise similarity CIs paired with the similarity matrix above. R10: CI visible alongside every point estimate."
      >
        <InspectTable
          caption={`Similarity CIs (${modelIds.length} × ${modelIds.length}), each cell [low, high] or null`}
          columns={simCICols}
          rows={simCIRows}
        />
      </InspectSection>

      {/* §2.4 Consensus (consensus_score + consensus_ci together — R10) */}
      <InspectSection title="Consensus">
        <InspectTable
          caption="Consensus statistics (score, CI, and Romney metrics)"
          columns={consensusCols}
          rows={consensusRows}
        />
      </InspectSection>

      {/* §2.4 Cultural centrality */}
      <InspectSection title="Cultural centrality">
        <InspectTable
          caption="Cultural centrality scores per model"
          columns={centralityCols}
          rows={centralityRows}
        />
        <InspectTable
          caption="Negative centrality flags"
          columns={centralityFlagCols}
          rows={centralityFlagRows}
        />
      </InspectSection>

      {/* §2.4 Cross-model agreement */}
      <InspectSection
        title="Cross-model agreement"
        description={
          crossIsEmpty
            ? "cross_model_mantel and cross_model_nolan are empty arrays — no cross-model statistics in this domain."
            : undefined
        }
      >
        <pre className="inspect-pre">
          {`cross_model_mantel: ${JSON.stringify(crossMantel, null, 2)}\ncross_model_nolan: ${JSON.stringify(crossNolan, null, 2)}`}
        </pre>
      </InspectSection>

      {/* §2.4 Sutrop CSI (salience) — per model, inline */}
      <InspectSection title="Sutrop CSI (salience)">
        {Object.entries(rawSutrop ?? {}).map(([modelId, items]) => (
          <div key={modelId} className="inspect-freelist-block">
            <InspectTable
              caption={`${modelId} — ${(items as SutropCsiItem[]).length} terms`}
              columns={sutropCols}
              rows={items as unknown as Record<string, unknown>[]}
            />
          </div>
        ))}
      </InspectSection>

      {/* §2.4 Salience index agreement */}
      <InspectSection title="Salience index agreement">
        <InspectTable
          caption="Salience index agreement per model"
          columns={salienceCols}
          rows={salienceRows}
        />
      </InspectSection>

      {/* §2.4 Within-model results — R10: oci and oci_ci columns adjacent */}
      <InspectSection
        title="Within-model results"
        description="Per-model within-model statistics. oci and oci_ci columns are adjacent (R10)."
      >
        <InspectTable
          caption={`Within-model results (${wmrRows.length} models)`}
          columns={wmrCols}
          rows={wmrRows}
        />
      </InspectSection>

      {/* §2.4 G1 stability fields */}
      <InspectSection
        title="G1 stability fields"
        description="G1 stability pass/fail indicators. null values are rendered verbatim — null is a valid first-class state."
      >
        <InspectTable
          caption="G1 stability indicators"
          columns={[
            { key: "field", label: "Field" },
            { key: "value", label: "Value" },
          ]}
          rows={g1Rows}
        />
      </InspectSection>

      {/* §2.4 Groundings */}
      <InspectSection
        title="Groundings"
        description="v1 domains are model-to-model by design per ARCHITECTURE.md §1.5.5. The groundings array is empty and selected_baseline_id is null — this is the expected first-class state, not a placeholder."
      >
        <pre className="inspect-pre">
          {`groundings: ${JSON.stringify(domain["groundings"], null, 2)}\nselected_baseline_id: ${JSON.stringify(domain["selected_baseline_id"])}`}
        </pre>
      </InspectSection>

      {/* §2.4 Display block */}
      <InspectSection title="Display block (precomputed UI helpers)">
        <InspectTable
          caption="R1 states per model"
          columns={r1StatesCols}
          rows={r1StatesRows}
        />
        <InspectTable
          caption={`Top terms per model (metric: ${rawDisplay?.top_terms_metric ?? "unknown"})`}
          columns={topTermsCols}
          rows={topTermsRows}
        />
        <InspectTable
          caption="Display block scalar fields"
          columns={[
            { key: "field", label: "Field" },
            { key: "value", label: "Value" },
          ]}
          rows={[{ field: "top_terms_metric", value: rawDisplay?.top_terms_metric }]}
        />
      </InspectSection>

      {/* Universal coverage: "Other top-level fields" — schema-drift safety net */}
      {otherKeys.length > 0 && (
        <InspectSection
          title="Other top-level fields"
          description="Fields present in the published JSON that are not mapped to a named section above. This section surfaces automatically when cdb_publish adds new fields."
        >
          {otherKeys.map((key) => (
            <div key={key} className="inspect-other-field">
              <p className="inspect-other-field__key">{key}</p>
              <pre className="inspect-pre">
                {JSON.stringify(domain[key], null, 2)}
              </pre>
            </div>
          ))}
        </InspectSection>
      )}
    </>
  );
}

// ── InspectRoot ───────────────────────────────────────────────────────────────

export function InspectRoot({ mode, manifest: passedManifest }: InspectRootProps) {
  // Inject <meta robots noindex> on mount, remove on unmount.
  // This prevents inspect URLs from being indexed by search engines.
  useEffect(() => {
    const meta = document.createElement("meta");
    meta.name = "robots";
    meta.content = "noindex";
    meta.setAttribute("data-inspect-meta", "true");
    document.head.appendChild(meta);
    return () => {
      const existing = document.head.querySelector('meta[data-inspect-meta="true"]');
      if (existing) {
        document.head.removeChild(existing);
      }
    };
  }, []);

  // Fetch manifest if not passed (this InspectRoot also self-fetches for manifest mode)
  const [localManifest, setLocalManifest] = useState<Manifest | null>(passedManifest);
  const [manifestError, setManifestError] = useState<string | null>(null);
  const [domainResult, setDomainResult] = useState<RawDomainJSON | null>(null);
  const [domainError, setDomainError] = useState<string | null>(null);
  const [domainLoading, setDomainLoading] = useState(mode !== "manifest");

  // Sync passedManifest into local state when App.tsx finishes loading it.
  // set-state-in-effect: intentional — syncing from a prop that may update later
  // (App.tsx starts with manifest=null and sets it after fetchManifest resolves).
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (passedManifest !== null) {
      setLocalManifest(passedManifest);
    }
  }, [passedManifest]);
  /* eslint-enable react-hooks/set-state-in-effect */

  // If manifest is needed but not passed yet, fetch it ourselves
  useEffect(() => {
    if (localManifest !== null) return;
    let cancelled = false;
    fetchManifest()
      .then((m) => {
        if (!cancelled) setLocalManifest(m);
      })
      .catch(() => {
        if (!cancelled) setManifestError("Could not load manifest.");
      });
    return () => { cancelled = true; };
  }, [localManifest]);

  // Fetch domain JSON for non-manifest modes.
  // set-state-in-effect: intentional — resetting loading/error state at the top of
  // the effect is the documented React pattern for loading UX
  // (https://react.dev/learn/you-might-not-need-an-effect: "loading data" is an
  //  accepted use case; the loading flag is not derived state, it's UX state).
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (mode === "manifest") return;
    let cancelled = false;
    setDomainLoading(true);
    setDomainError(null);
    fetchDomain(mode)
      .then((result) => {
        if (!cancelled) {
          setDomainResult(result as unknown as RawDomainJSON);
          setDomainLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDomainError(`Could not load domain "${mode}".`);
          setDomainLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [mode]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const manifestDomain = localManifest?.domains.find((d) => d.slug === mode);

  return (
    <div className="inspect-root">
      {/* Sticky header with H1 and nav */}
      <header className="inspect-header">
        <h1 className="inspect-header__title">LSB published-data inspection</h1>
        <InspectNav activeMode={mode} />
      </header>

      <main className="inspect-main">
        {/* Loading / error states — F-T0-C1: use --color-text-caption for WCAG AA */}
        {manifestError && (
          <p
            style={{
              color: "var(--color-text-caption)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            {manifestError}
          </p>
        )}

        {mode === "manifest" && !manifestError && localManifest === null && (
          <p
            style={{
              color: "var(--color-text-caption)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            Loading...
          </p>
        )}

        {mode === "manifest" && localManifest !== null && (
          <ManifestView manifest={localManifest} />
        )}

        {mode !== "manifest" && domainLoading && (
          <p
            style={{
              color: "var(--color-text-caption)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            Loading...
          </p>
        )}

        {mode !== "manifest" && domainError && (
          <p
            style={{
              color: "var(--color-text-caption)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            {domainError}
          </p>
        )}

        {mode !== "manifest" && !domainLoading && !domainError && domainResult !== null && (
          <DomainView
            domain={domainResult}
            slug={mode}
            manifestDomain={manifestDomain}
          />
        )}
      </main>
    </div>
  );
}
