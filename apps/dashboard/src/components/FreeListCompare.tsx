/**
 * FreeListCompare — side-by-side ranked free list comparison per DESIGN_SYSTEM.md §3.4.
 *
 * Phase 6 T7. One column per selected model, ranked by Sutrop CSI descending.
 * R10 inclusion-frequency bars on every term pill.
 *
 * Props:
 *   domainResult   — full DomainResultPublished (free_lists + sutrop_csi accessed
 *                    via cast-through-unknown, not via types.ts — see §4 note)
 *   modelColors    — Record<model_id, cssHexColor> from DataExplorer §12.4
 *   selectedModels — model_ids currently selected (from DataExplorer state)
 *
 * Type/JSON shape note (deferred to Phase 6 T14 doc-sweep):
 *   data/types.ts disagrees with live JSON in two T7-relevant places:
 *   1. free_lists: typed as Record<string, string[]> but JSON is
 *      Record<string, { run_id, model, domain_slug, items: string[], raw_order: string[] }>
 *   2. sutrop_csi: typed as Record<string, Record<string, number>> but JSON is
 *      Record<string, Array<{ item, csi, f_mentions, n_runs, mean_position }>>
 *   T7 follows the live JSON via cast-through-unknown at this boundary.
 *   See DataExplorer.tsx lines 152, 192, 229 and InspectRoot.tsx for the same pattern.
 *   T14 doc-sweep will reconcile types.ts with the actual JSON shapes.
 *
 * Empty states (plan §2.5):
 *   Case A (selectedModels.length === 0): "Select one or more models to see their free lists."
 *   Case B (sutrop_csi[modelId] missing or empty): "(no salience data for this model)"
 *   Case C (items: [] AND sutrop_csi: []): "(no terms produced)"
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks" (model-applied),
 *   "missing", "placeholder", "no data yet", "pending" per CLAUDE.md §7.
 *
 * Does NOT touch data/types.ts. CLAUDE.md §6 R11: no LLM client imports.
 *
 * F-T7-A1 (BINDING): sr-only h2 as first child of root element.
 * F-T7-C1 (ADVISORY): bar fill opacity adjusted to 0.8 — see freelist-compare.css.
 *
 * T8: ReadAsTableToggle + FreeListTable + ScreenReaderSummary.
 *   readAsTable state: local useState (per-viz, no DataExplorer state pollution).
 *   U1 (BINDING): table container div always in DOM; aria-hidden + display:none when inactive.
 *   ScreenReaderSummary: always present regardless of readAsTable state.
 *   Does NOT touch data/types.ts (AC #19).
 *
 * Reference: docs/status/2026-05-12-phase6-T7-architect-plan.md
 *            docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md §5.1–§5.2
 *            docs/status/2026-05-12-phase6-T7-uiux-plan-verdict.md F-T7-A1
 *            docs/status/2026-05-12-phase6-T8-architect-plan.md §2.3.2
 *            docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md §4.2
 */

import { useState, useMemo } from "react";
import type { DomainResultPublished } from "../data/types";
import { FreeListColumn } from "./FreeListColumn";
import type { TermRecord } from "./FreeListColumn";
import { ScreenReaderSummary } from "./ScreenReaderSummary";
import { ReadAsTableToggle } from "./ReadAsTableToggle";
import { FreeListTable } from "./FreeListTable";
import {
  READ_AS_TABLE_LABEL_REST,
  READ_AS_TABLE_LABEL_PRESSED,
  freeListScreenReaderSummary,
} from "../copy/screen_reader_summaries";
import "../styles/freelist-compare.css";

// ── Shape interfaces matching actual JSON (NOT data/types.ts — see file header) ─

interface SutropCsiItemActual {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  mean_position: number;
}

// ── Props ─────────────────────────────────────────────────────────────────────

export interface FreeListCompareProps {
  domainResult: DomainResultPublished;
  modelColors: Record<string, string>;
  selectedModels: string[];
}

// Stable ID for the T8 table container (U1: always in DOM)
const FREELIST_TABLE_CONTAINER_ID = "freelist-table-container";

// ── Component ─────────────────────────────────────────────────────────────────

export function FreeListCompare({
  domainResult,
  modelColors,
  selectedModels,
}: FreeListCompareProps) {
  // Cross-column hover highlight state
  const [hoveredTerm, setHoveredTerm] = useState<string | null>(null);
  // T8: Read-as-table toggle state (per-viz local, resets on unmount per plan §2.4)
  const [readAsTable, setReadAsTable] = useState<boolean>(false);

  // Cast-through-unknown: types.ts disagrees with actual JSON shape for sutrop_csi.
  // The actual JSON is Record<string, Array<SutropCsiItemActual>>.
  // T14 doc-sweep will reconcile data/types.ts.
  const rawSutropCsi = domainResult.sutrop_csi as unknown as Record<
    string,
    Array<SutropCsiItemActual>
  >;

  /**
   * Per-model sorted term records, keyed by model_id.
   * null means Case B (no sutrop_csi data at all for this model).
   * [] means Case C (sutrop_csi exists but is empty).
   *
   * Sort order per plan §2.4:
   *   primary: csi descending
   *   tiebreak 1: mean_position ascending (earlier mention = more salient)
   *   tiebreak 2: item lexicographic ascending (stable, deterministic)
   */
  const termsByModel = useMemo((): Record<string, TermRecord[] | null> => {
    const result: Record<string, TermRecord[] | null> = {};
    for (const modelId of selectedModels) {
      const raw = rawSutropCsi?.[modelId];
      if (raw === undefined || raw === null) {
        // Case B: no sutrop data for this model
        result[modelId] = null;
      } else {
        // Case C (empty array) or normal case
        const sorted = [...raw].sort((a, b) => {
          if (b.csi !== a.csi) return b.csi - a.csi;
          if (a.mean_position !== b.mean_position)
            return a.mean_position - b.mean_position;
          return a.item.localeCompare(b.item);
        });
        result[modelId] = sorted.map((entry) => ({
          item: entry.item,
          csi: entry.csi,
          f_mentions: entry.f_mentions,
          n_runs: entry.n_runs,
          inclusionFrequency:
            entry.n_runs > 0 ? entry.f_mentions / entry.n_runs : 0,
        }));
      }
    }
    return result;
  }, [domainResult, selectedModels]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Shared-terms set: terms that appear in ALL selected models.
   * If selectedModels.length <= 1, no terms are shared (per plan §2.4).
   * Only computed when there are 2+ selected models with data.
   */
  const sharedTerms = useMemo((): Set<string> => {
    if (selectedModels.length < 2) return new Set();
    const termSets = selectedModels
      .map((id) => {
        const terms = termsByModel[id];
        if (!terms || terms.length === 0) return null;
        return new Set(terms.map((t) => t.item));
      })
      .filter((s): s is Set<string> => s !== null);

    if (termSets.length < 2) return new Set();

    // Intersection: start with first set, intersect with each subsequent
    const [first, ...rest] = termSets;
    const intersection = new Set<string>();
    for (const item of first) {
      if (rest.every((s) => s.has(item))) {
        intersection.add(item);
      }
    }
    return intersection;
  }, [termsByModel, selectedModels]);

  // T8: ScreenReaderSummary text (always computed, always rendered)
  const srSummaryText = freeListScreenReaderSummary(domainResult, selectedModels);

  return (
    <div
      className="freelist-compare"
      aria-label="Side-by-side free lists"
    >
      {/* F-T7-A1 (BINDING): sr-only h2 as first child for heading hierarchy.
          Ensures h1 → h2 → h3 (column headers) with no skips per WCAG §1.3.1.
          The DataExplorer section has no visible h2 antecedent. */}
      <h2 className="sr-only">Free list comparison</h2>

      {/* T8: ScreenReaderSummary — always present in both viz and table modes (plan §2.5) */}
      <ScreenReaderSummary text={srSummaryText} />

      {/* T8: ReadAsTableToggle — below the description, above the columns (plan §2.2) */}
      <ReadAsTableToggle
        pressed={readAsTable}
        onToggle={() => setReadAsTable((v) => !v)}
        tableContainerId={FREELIST_TABLE_CONTAINER_ID}
        labels={{ rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED }}
      />

      {/* Component description — functional sentence only, no marketing copy */}
      {/* Hidden when table is active (aria-hidden + display:none via U1 Option A on columns container) */}
      <p
        className="freelist-compare__description"
        aria-hidden={readAsTable || undefined}
        style={{ display: readAsTable ? "none" : undefined }}
      >
        Each column lists the terms one model produced for this domain, ordered
        by Sutrop salience (Sutrop CSI).
      </p>

      {/* Case A: no models selected — shown in viz mode only */}
      {selectedModels.length === 0 && !readAsTable && (
        <p className="freelist-compare__empty">
          Select one or more models to see their free lists.
        </p>
      )}

      {/* T8: Visualization columns — hidden via aria-hidden + display:none when table is active.
          U1 Option A: always render; use aria-hidden + display:none when inactive. */}
      {selectedModels.length > 0 && (
        <div
          className="freelist-compare__columns"
          aria-hidden={readAsTable || undefined}
          style={{ display: readAsTable ? "none" : undefined }}
        >
          {selectedModels.map((modelId) => {
            // termsByModel[modelId] may be null (Case B), [] (Case C), or populated.
            // The key may be absent if modelId wasn't in the useMemo result —
            // that cannot happen since we iterate selectedModels in both places,
            // but the ?? null guard is defensive.
            const terms = termsByModel[modelId] !== undefined
              ? termsByModel[modelId]
              : null;
            const color = modelColors[modelId] ?? "#888888";

            return (
              <FreeListColumn
                key={modelId}
                modelId={modelId}
                modelColor={color}
                terms={terms}
                sharedTerms={sharedTerms}
                hoveredTerm={hoveredTerm}
                onTermHover={setHoveredTerm}
              />
            );
          })}
        </div>
      )}

      {/* T8: FreeListTable container — U1 Option A: ALWAYS in DOM.
          aria-hidden="true" + display:none when readAsTable = false.
          FreeListTable renders conditionally inside. */}
      <div
        id={FREELIST_TABLE_CONTAINER_ID}
        aria-hidden={readAsTable ? undefined : true}
        style={{ display: readAsTable ? undefined : "none" }}
      >
        <FreeListTable
          domainResult={domainResult}
          selectedModels={selectedModels}
          modelColors={modelColors}
        />
      </div>
    </div>
  );
}
