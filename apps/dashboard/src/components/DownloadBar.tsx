/**
 * DownloadBar — CSV + permalink buttons below the chart.
 *
 * Per DESIGN_SYSTEM.md §5:
 * - CSV button: downloads current view as CSV via csv-export.ts.
 * - Permalink button: copies current view URL to clipboard via
 *   navigator.clipboard.writeText.
 *
 * Buttons are left-aligned, styled with design tokens. Focus rings per §7.
 * ARIA labels on both buttons.
 *
 * Phase 5 only: activeVizTab is always "mds". PNG, Cite, Embed are T11/T12.
 *
 * Source: DESIGN_SYSTEM.md §5, docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 */

import { useState } from "react";
import type { DomainResultPublished } from "../data/types";
import { domainResultToCsv, downloadCsv } from "../lib/csv-export";
import { encodePermalink } from "../lib/permalink";

// ── Props ────────────────────────────────────────────────────────────────────

export interface DownloadBarProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  activeVizTab: "mds";
}

// ── Shared button style ───────────────────────────────────────────────────────

const buttonBase: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: "4px",
  padding: "4px 10px",
  fontSize: "var(--font-size-xs)",
  fontFamily: "var(--font-body)",
  fontWeight: "var(--font-weight-medium)",
  color: "var(--color-text-primary)",
  background: "transparent",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--border-radius-sm)",
  cursor: "pointer",
  lineHeight: 1.4,
  transition: "background-color 0.15s ease",
};

// ── Component ────────────────────────────────────────────────────────────────

/**
 * DownloadBar renders the CSV download and permalink copy buttons per §5.
 */
export function DownloadBar({ domainResult, selectedModels, activeVizTab }: DownloadBarProps) {
  const [permalinkCopied, setPermalinkCopied] = useState(false);

  function handleCsvDownload(): void {
    const csv = domainResultToCsv(domainResult, selectedModels);
    const filename = `lsb-${domainResult.domain_slug}-v${domainResult.analysis_version}.csv`;
    downloadCsv(csv, filename);
  }

  function handlePermalinkCopy(): void {
    const stateStr = encodePermalink({
      domain: domainResult.domain_slug,
      models: selectedModels,
      vizTab: activeVizTab,
    });
    // Build the full URL: origin + pathname + encoded state.
    let fullUrl: string;
    try {
      fullUrl = window.location.origin + window.location.pathname + stateStr;
    } catch {
      fullUrl = stateStr;
    }

    navigator.clipboard.writeText(fullUrl).then(
      () => {
        setPermalinkCopied(true);
        setTimeout(() => setPermalinkCopied(false), 2000);
      },
      () => {
        // Clipboard write failed — silently ignore.
      }
    );
  }

  return (
    <div
      className="download-bar"
      style={{
        display: "flex",
        gap: "var(--space-2)",
        marginTop: "var(--space-2)",
        flexWrap: "wrap",
      }}
    >
      {/* CSV Download button */}
      <button
        type="button"
        className="download-bar__csv-btn"
        aria-label={`Download ${domainResult.domain_slug} domain data as CSV`}
        onClick={handleCsvDownload}
        style={buttonBase}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor =
            "var(--color-surface-hover)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
        }}
      >
        &#8659; Download CSV
      </button>

      {/* Permalink button */}
      <button
        type="button"
        className="download-bar__permalink-btn"
        aria-label="Copy permalink to clipboard"
        onClick={handlePermalinkCopy}
        style={buttonBase}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor =
            "var(--color-surface-hover)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
        }}
      >
        {permalinkCopied ? "✓ Copied!" : "🔗 Copy permalink"}
      </button>
    </div>
  );
}
