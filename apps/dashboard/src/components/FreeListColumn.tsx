/**
 * FreeListColumn — single model column in the FreeListCompare view.
 *
 * Phase 6 T7. Renders a ranked list of terms for one model, with R10
 * inclusion-frequency bars and accessible labels per CDA SME §5.1–§5.2.
 *
 * Props:
 *   modelId      — canonical model_id string
 *   modelColor   — hex color from DataExplorer's §12.4 modelColors
 *   terms        — sorted array of TermRecord (descending CSI)
 *   sharedTerms  — Set of terms that appear in ALL selected models
 *   hoveredTerm  — currently hovered/focused term (cross-column highlight)
 *   onTermHover  — callback to set/clear hoveredTerm in FreeListCompare
 *
 * R10 implementation (CDA SME §5.2 binding):
 *   Each <li> carries:
 *     aria-label=`${item}, Sutrop salience score ${csi.toFixed(2)},
 *                 included in ${f_mentions} of ${n_runs} collection runs`
 *   plus the optional shared-term suffix "; in every selected model".
 *
 * R10 caption (CDA SME §5.1 binding verbatim):
 *   "Bar shows the fraction of this model's collection runs that produced this term."
 *
 * Empty states (plan §2.5):
 *   Case B (sutrop_csi missing/empty): "(no salience data for this model)"
 *   Case C (no terms produced): "(no terms produced)"
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks" (model-applied),
 *   "missing", "placeholder", "no data yet", "pending" per CLAUDE.md §7.
 *
 * Does NOT touch data/types.ts — cast-through-unknown happens in parent.
 * Does NOT import anthropic, openai, or any LLM client per CLAUDE.md §6 R11.
 *
 * Reference: docs/status/2026-05-12-phase6-T7-architect-plan.md §2.3
 */

import { modelShortName } from "../lib/modelShortName";

/** One entry from sutrop_csi[modelId] — typed to match actual JSON shape. */
export interface TermRecord {
  item: string;
  csi: number;
  f_mentions: number;
  n_runs: number;
  inclusionFrequency: number; // f_mentions / n_runs, pre-computed in parent
}

export interface FreeListColumnProps {
  modelId: string;
  modelColor: string;
  /** null = Case B (no sutrop_csi data for this model); [] = Case C (no terms produced). */
  terms: TermRecord[] | null;
  sharedTerms: Set<string>;
  hoveredTerm: string | null;
  onTermHover: (term: string | null) => void;
}

export function FreeListColumn({
  modelId,
  modelColor,
  terms,
  sharedTerms,
  hoveredTerm,
  onTermHover,
}: FreeListColumnProps) {
  const shortName = modelShortName(modelId);

  // Determine which empty state applies per plan §2.5:
  //   Case B: terms === null (sutrop_csi missing/undefined for this model)
  //   Case C: terms is [] (sutrop_csi exists but is an empty array)
  //   Normal: terms.length > 0
  const isNoSalienceData = terms === null;
  const isNoTermsProduced = !isNoSalienceData && terms.length === 0;
  const hasTerms = !isNoSalienceData && terms.length > 0;

  return (
    <div className="freelist-column">
      {/* Column header: color dot + model name as h3 (heading order: h2 in parent → h3 here) */}
      <header className="freelist-column__header">
        <span
          className="freelist-column__color-dot"
          style={{ backgroundColor: modelColor }}
          aria-hidden="true"
        />
        <h3 className="freelist-column__model-name">{shortName}</h3>
      </header>

      {/* Case B: no salience data for this model */}
      {isNoSalienceData && (
        <span className="freelist-column__empty-caption">
          (no salience data for this model)
        </span>
      )}

      {/* Case C: model produced no terms */}
      {isNoTermsProduced && (
        <>
          <span className="freelist-column__count">0 terms</span>
          <span className="freelist-column__empty-caption">
            (no terms produced)
          </span>
        </>
      )}

      {/* Normal state: terms present */}
      {hasTerms && (
        <>
          {/* Term count */}
          <span className="freelist-column__count">{terms.length} terms</span>

          {/* R10 caption — binding verbatim text from CDA SME §5.1 */}
          {/* Exact wording required; do not reformat across lines */}
          {/* prettier-ignore */}
          <p className="freelist-column__r10-caption">Bar shows the fraction of this model&apos;s collection runs that produced this term.</p>

          {/* Ranked term list */}
          <ol className="freelist-column__list">
            {terms.map((record) => {
              const isHovered = hoveredTerm === record.item;
              const isShared = sharedTerms.has(record.item);
              const barWidth = `${record.inclusionFrequency * 100}%`;

              // Accessible label — CDA SME §5.2 binding verbatim
              const baseLabel = `${record.item}, Sutrop salience score ${record.csi.toFixed(2)}, included in ${record.f_mentions} of ${record.n_runs} collection runs`;
              const ariaLabel = isShared
                ? `${baseLabel}; in every selected model`
                : baseLabel;

              return (
                <li
                  key={record.item}
                  className={[
                    "freelist-column__item",
                    isHovered ? "freelist-column__item--hovered" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  aria-label={ariaLabel}
                  onMouseEnter={() => onTermHover(record.item)}
                  onMouseLeave={() => onTermHover(null)}
                  onFocus={() => onTermHover(record.item)}
                  onBlur={() => onTermHover(null)}
                  tabIndex={0}
                >
                  <div className="freelist-column__pill">
                    {/* Term text */}
                    <span className="freelist-column__term">{record.item}</span>

                    {/* Shared-term star glyph — decorative, info in aria-label */}
                    {isShared && (
                      <span
                        className="freelist-column__shared-star"
                        aria-hidden="true"
                      >
                        ★
                      </span>
                    )}

                    {/* R10 inclusion-frequency bar + numeric label */}
                    <div className="freelist-column__freq-container">
                      <div
                        className="freelist-column__freq-bar"
                        aria-hidden="true"
                      >
                        <div
                          className="freelist-column__freq-fill"
                          style={{
                            width: barWidth,
                            backgroundColor: modelColor,
                          }}
                        />
                      </div>
                      <span
                        className="freelist-column__freq-label"
                        aria-hidden="true"
                      >
                        {record.f_mentions}/{record.n_runs}
                      </span>
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </>
      )}
    </div>
  );
}
