/**
 * SourceAttribution — source line below the chart.
 *
 * Displays: selected model list (full names, with "+ N more" overflow),
 * domain slug, prompt version (v1), analysis version, and collection month.
 *
 * Per CDA SME plan-level Q2 binding: when domainResult.romney_small_n_warning
 * is true, renders a small footnote noting that n < 15 models were measured.
 *
 * Visual placement per DESIGN_SYSTEM.md §5: below the chart, left-aligned,
 * font-size-xs (12px).
 *
 * Source: DESIGN_SYSTEM.md §5, docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 */

import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";

// ── Constants ────────────────────────────────────────────────────────────────

/** Maximum model names shown inline before "+ N more" suffix. */
const MAX_INLINE_MODELS = 4;

// ── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Parse an ISO-8601 timestamp and return "Month YYYY" string.
 * Falls back to the raw string if parsing fails.
 */
function formatCollectionMonth(isoString: string): string {
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleDateString("en-US", { month: "long", year: "numeric" });
  } catch {
    return isoString;
  }
}

// ── Props ────────────────────────────────────────────────────────────────────

export interface SourceAttributionProps {
  domainResult: DomainResultPublished;
  /** Selected model_ids to list in the source line. */
  selectedModels: string[];
}

// ── Component ────────────────────────────────────────────────────────────────

/**
 * SourceAttribution renders the source line and optional small-n footnote
 * below the chart per DESIGN_SYSTEM.md §5.
 */
export function SourceAttribution({ domainResult, selectedModels }: SourceAttributionProps) {
  const collectionMonth = formatCollectionMonth(domainResult.generated_at);
  const n = selectedModels.length;
  const inlineModels = selectedModels.slice(0, MAX_INLINE_MODELS);
  const overflow = n - MAX_INLINE_MODELS;

  // Build the model list string.
  const modelListParts = inlineModels.map((id) => modelShortName(id));
  const modelListStr =
    overflow > 0
      ? modelListParts.join(" · ") + ` · +${overflow} more`
      : modelListParts.join(" · ");

  const totalModelCount = domainResult.models.length;

  return (
    <div
      className="source-attribution"
      style={{
        fontSize: "var(--font-size-xs)",
        // v0.4.3 WCAG AA fix (UI/UX T10): --color-text-caption (~4.60:1) replaces
        // --color-text-muted (~1.75:1), which fails 4.5:1 for 12px body text.
        color: "var(--color-text-caption)",
        lineHeight: 1.5,
        marginTop: "var(--space-3)",
      }}
    >
      {/* Source line */}
      <p style={{ margin: 0 }}>
        <span style={{ fontWeight: "var(--font-weight-bold)" }}>Source:</span>{" "}
        {n === totalModelCount ? (
          <span>{modelListStr}</span>
        ) : (
          <span>
            {modelListStr}
            {" "}
            <span style={{ color: "var(--color-text-secondary)" }}>
              ({n} of {totalModelCount} models shown)
            </span>
          </span>
        )}
      </p>

      {/* Attribution line */}
      <p style={{ margin: "2px 0 0" }}>
        Domain:{" "}
        <span style={{ fontFamily: "var(--font-mono)" }}>{domainResult.domain_slug}</span>
        {" · "}
        Prompt: v1
        {" · "}
        Analysis: v{domainResult.analysis_version}
        {" · "}
        Collected: {collectionMonth}
      </p>

      {/* Q2 binding: small-n footnote when romney_small_n_warning is true */}
      {domainResult.romney_small_n_warning && (
        <p
          className="source-attribution__small-n-note"
          style={{
            margin: "4px 0 0",
            fontStyle: "italic",
            // v0.4.3 WCAG AA fix: --color-text-caption (~4.60:1) for 12px italic;
            // --color-text-secondary (~3.40:1) is insufficient.
            color: "var(--color-text-caption)",
          }}
        >
          Small-n note: this measurement is computed at n={totalModelCount} models, below the
          n=15 threshold for stable Romney CCM eigenratio reporting. See methodology for details.
        </p>
      )}
    </div>
  );
}
