/**
 * DownloadBar — CSV + permalink + PNG buttons below the chart.
 *
 * Per DESIGN_SYSTEM.md §5:
 * - CSV button: downloads current view as CSV via csv-export.ts.
 * - Permalink button: copies current view URL to clipboard via
 *   navigator.clipboard.writeText.
 * - PNG (social) button: exports 1600×900 PNG via png-export.ts + png-metadata.ts.
 * - PNG hi-res link: exports 2000×2000 PNG via the same pipeline.
 *
 * PNG handler chain:
 *   1. Find the MDSPlot SVG via the svgRef prop (preferred) or
 *      document.querySelector('svg[role="img"]') (fallback).
 *   2. Call renderToPng(svg, {size}) → PNG Blob.
 *   3. Call injectTextMetadata(blob, kv) → Blob with tEXt fields.
 *   4. Trigger download via a temporary <a> element.
 *
 * tEXt metadata fields per T11 spec:
 *   Title, Author, Source, Software, Domain, Models, Analysis-Version, Generated-At
 *
 * ARIA: PNG button has aria-label="Download chart as PNG (social)" and
 *       aria-label="Download chart as PNG (hi-res)" for the hi-res link.
 *
 * Buttons are left-aligned, styled with design tokens. Focus rings per §7.
 *
 * Source: DESIGN_SYSTEM.md §5, docs/status/2026-05-09-phase5-architect-plan.md §4 T11
 */

import { useState } from "react";
import type { DomainResultPublished } from "../data/types";
import { domainResultToCsv, downloadCsv } from "../lib/csv-export";
import { encodePermalink } from "../lib/permalink";
import { renderToPng } from "../lib/png-export";
import type { PngSize } from "../lib/png-export";
import { injectTextMetadata } from "../lib/png-metadata";

// ── Props ────────────────────────────────────────────────────────────────────

export interface DownloadBarProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  activeVizTab: "mds";
  /** Optional ref to the MDSPlot SVG element for clean export without querySelector. */
  svgRef?: React.RefObject<SVGSVGElement | null>;
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

/** Small inline link style used for the "hi-res" secondary affordance. */
const linkStyle: React.CSSProperties = {
  fontSize: "var(--font-size-xs)",
  fontFamily: "var(--font-body)",
  color: "var(--color-text-secondary)",
  cursor: "pointer",
  background: "none",
  border: "none",
  padding: "0",
  textDecoration: "underline",
  lineHeight: 1.4,
  alignSelf: "center",
};

// ── PNG download helper ───────────────────────────────────────────────────────

/**
 * Build tEXt metadata kv pairs for a PNG export.
 */
function buildPngMetadata(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): Record<string, string> {
  const modelList = selectedModels.join(",");
  // tEXt chunks are Latin-1. Use ASCII-safe separators in the title.
  return {
    Title: `Cognitive Structure Lab - ${domainResult.domain_slug} domain - MDS`,
    Author: "Cognitive Structure Lab",
    Source: "cogstructurelab.com",
    Software: `LSB Dashboard v0.5.0`,
    Domain: domainResult.domain_slug,
    Models: modelList,
    "Analysis-Version": domainResult.analysis_version,
    "Generated-At": domainResult.generated_at,
  };
}

/**
 * Find the MDSPlot SVG: prefer the passed ref, fall back to querySelector.
 */
function findSvg(
  svgRef?: React.RefObject<SVGSVGElement | null>
): SVGSVGElement | null {
  if (svgRef?.current) {
    return svgRef.current;
  }
  return document.querySelector('svg[role="img"]');
}

/**
 * Trigger a PNG file download from a Blob via a temporary <a> element.
 */
function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// ── Component ────────────────────────────────────────────────────────────────

/**
 * DownloadBar renders the CSV download, permalink copy, and PNG export buttons per §5.
 *
 * PNG affordance (Architect rec):
 *   Primary:   "Download PNG (social)"  → 1600×900
 *   Secondary: "hi-res" link below      → 2000×2000
 */
export function DownloadBar({
  domainResult,
  selectedModels,
  activeVizTab,
  svgRef,
}: DownloadBarProps) {
  const [permalinkCopied, setPermalinkCopied] = useState(false);
  const [pngState, setPngState] = useState<"idle" | "loading" | "error">("idle");
  const [activePngSize, setActivePngSize] = useState<PngSize>("social");

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

  async function handlePngDownload(size: PngSize): Promise<void> {
    const svg = findSvg(svgRef);
    if (!svg) {
      // No SVG found (e.g., viz tab is not MDS). Silently do nothing.
      return;
    }

    setActivePngSize(size);
    setPngState("loading");

    try {
      const rawBlob = await renderToPng(svg, { size });
      const kv = buildPngMetadata(domainResult, selectedModels);
      const finalBlob = await injectTextMetadata(rawBlob, kv);
      const suffix = size === "social" ? "social" : "highres";
      const filename = `lsb-${domainResult.domain_slug}-mds-${suffix}.png`;
      downloadBlob(finalBlob, filename);
      setPngState("idle");
    } catch {
      setPngState("error");
      // Reset error state after a short delay so the button recovers.
      setTimeout(() => setPngState("idle"), 3000);
    }
  }

  const pngLoading = pngState === "loading";

  return (
    <div
      className="download-bar"
      style={{
        display: "flex",
        gap: "var(--space-2)",
        marginTop: "var(--space-2)",
        flexWrap: "wrap",
        alignItems: "flex-start",
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

      {/* PNG export group: primary button + hi-res link */}
      <div
        className="download-bar__png-group"
        style={{
          display: "inline-flex",
          flexDirection: "column",
          gap: "2px",
        }}
      >
        <button
          type="button"
          className="download-bar__png-btn"
          aria-label="Download chart as PNG (social)"
          onClick={() => handlePngDownload("social")}
          disabled={pngLoading}
          style={{
            ...buttonBase,
            opacity: pngLoading ? 0.6 : 1,
            cursor: pngLoading ? "wait" : "pointer",
          }}
          onMouseEnter={(e) => {
            if (!pngLoading) {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                "var(--color-surface-hover)";
            }
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
          }}
        >
          {pngState === "error"
            ? "PNG export failed"
            : pngLoading && activePngSize === "social"
              ? "Exporting…"
              : "⬇ Download PNG (social)"}
        </button>

        <button
          type="button"
          className="download-bar__png-hires-btn"
          aria-label="Download chart as PNG (hi-res)"
          onClick={() => handlePngDownload("highres")}
          disabled={pngLoading}
          style={{
            ...linkStyle,
            opacity: pngLoading ? 0.4 : 1,
            cursor: pngLoading ? "wait" : "pointer",
          }}
        >
          {pngLoading && activePngSize === "highres"
            ? "Exporting…"
            : "hi-res (2000×2000)"}
        </button>
      </div>
    </div>
  );
}
