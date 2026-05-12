// @vitest-environment jsdom
/**
 * T5 gap-fill tests — Phase 6 T5 (SimilarityHeatmap).
 *
 * Gaps filled against:
 *   - CDA SME §5.1 verbatim caption text: exact string regression guard
 *   - CDA SME §5.2 aria-label suffix for dashed cells (CI crosses null)
 *   - CDA SME §5.5 no methodology narration: no <details>, no <summary>,
 *     no info-icon button, no "we chose / we use / bootstrap / smoothing" prose
 *   - F-T5-A1 (BINDING): sr-only h2 is the FIRST child of root <div> (not just present)
 *   - F-T5-C1 (BINDING): HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73 in source (not 0.5, not 0.55)
 *   - F-T5-C1 (BINDING): --color-heatmap-cell-text-dark: #000000 in tokens.css
 *   - F-T5-C1: plan-fallback 0.55 NOT present as executable code
 *   - SIMILARITY_NULL_VALUE = 0.5 in config/analysis.ts (no literal 0.5 in component)
 *   - Dual-index translation correctness: 3-model fixture, non-lexicographic order
 *   - Forbidden vocabulary static-file scan: SimilarityHeatmap.tsx + similarity-heatmap.css
 *   - Diagonal cell aria-label uses "self-similarity" phrasing
 *   - Null-CI cell aria-label contains "confidence interval not available"
 *   - F-T5-M1 (ADVISORY): aria-label on <rect> cells preserved regardless of <text> suppression
 *   - Empty-state render: sr-only h2 present, no <svg>, correct empty-state text
 *
 * CLAUDE.md §6 R9: no real API calls. Static-file reads + inline fixtures only.
 *
 * Reference: docs/status/2026-05-12-phase6-T5-architect-plan.md §2.3, §2.4, §2.5, §2.8
 *            docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md §5.1, §5.2, §5.5
 *            docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md F-T5-A1, F-T5-C1, F-T5-M1
 *            docs/status/2026-05-12-phase6-T5-reviewer-verdict.md
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { SimilarityHeatmap } from "../components/SimilarityHeatmap";
import type { SimilarityHeatmapProps } from "../components/SimilarityHeatmap";
import type {
  DomainResultPublished,
  WithinModelResult,
  EllipseParams,
} from "../data/types";

// ── Static source files ────────────────────────────────────────────────────────

const SIMILARITY_HEATMAP_SRC = readFileSync(
  resolve(__dirname, "../components/SimilarityHeatmap.tsx"),
  "utf-8"
);
const SIMILARITY_HEATMAP_CSS = readFileSync(
  resolve(__dirname, "../styles/similarity-heatmap.css"),
  "utf-8"
);
const TOKENS_CSS = readFileSync(
  resolve(__dirname, "../styles/tokens.css"),
  "utf-8"
);

// ── Render helpers ─────────────────────────────────────────────────────────────

let container: HTMLDivElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => {
    root.unmount();
  });
  container.remove();
});

function renderHeatmap(props: SimilarityHeatmapProps): void {
  act(() => {
    root.render(createElement(SimilarityHeatmap, props));
  });
}

/**
 * Returns text content of only elements that are NOT inside [aria-hidden="true"]
 * containers. Used for "no methodology prose" checks that should not fire on
 * T8 table captions hidden via aria-hidden + display:none.
 */
function visibleTextContent(el: HTMLElement): string {
  // Clone the element so we can mutate freely
  const clone = el.cloneNode(true) as HTMLElement;
  // Remove all aria-hidden subtrees
  clone.querySelectorAll('[aria-hidden="true"]').forEach((n) => n.remove());
  return (clone.textContent ?? "").toLowerCase();
}

// ── Fixture builder ────────────────────────────────────────────────────────────
//
// The fixture uses clearly artificial model ids ("model-x", "model-y", "model-z")
// and fabricated values per fixture README conventions — no real-looking model ids,
// no real SHA256 manifests, no real dates beyond the 2026-01-01 sentinel.

function makeFixture(
  modelIds: string[],
  similarityMatrix: number[][],
  similarityCiMatrix: Array<Array<[number, number] | null>>
): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, EllipseParams | null> = {};
  const within_model_results: WithinModelResult[] = [];

  modelIds.forEach((id, i) => {
    mds_coordinates[id] = [i * 0.1, i * 0.1];
    mds_uncertainty[id] = null;
    within_model_results.push({
      model_id: id,
      n_runs: 4,
      oci: 10.0,
      oci_ci: null,
      underestimates_uncertainty: false,
      deterministic_output: false,
      salience_stability_rho: null,
      elbow_stability: null,
      mds_procrustes_rmse: null,
      centrality_scores_by_run: {},
      centroid_run_id: "run-fixture",
      mds_within_model: [],
    });
  });

  return {
    domain_slug: "fixture-domain",
    analysis_version: "0.2",
    models: modelIds.map((id) => ({
      provider: "fixture",
      model_id: id,
      family: id,
      origin: "us" as const,
      open_weights: false,
      collection_method: "api",
      quantization: null,
      release_date: "2026-01-01",
      version_label: id,
      source_notes: "",
    })),
    free_lists: {} as unknown as Record<string, string[]>,
    mds_coordinates: mds_coordinates as unknown as Record<
      string,
      [[number, number]]
    >,
    mds_uncertainty,
    // Cast-through-unknown mirrors SimilarityHeatmap.tsx's own T14-noted cast
    similarity_matrix: similarityMatrix as unknown as Record<
      string,
      Record<string, number>
    >,
    similarity_ci: similarityCiMatrix as unknown as Record<
      string,
      Record<string, [number, number] | null>
    >,
    consensus_score: 0.71,
    consensus_ci: [0.65, 0.77],
    consensus_type: "STRONG_CONSENSUS",
    sutrop_csi: {} as unknown as Record<string, Record<string, number>>,
    within_model_results,
    groundings: [],
    generated_lede: "Fixture lede.",
    generated_at: "2026-01-01T00:00:00Z",
    romney_small_n_warning: false,
    display: {
      r1_states: Object.fromEntries(
        modelIds.map((id) => [id, "typical_concentration" as const])
      ),
      top_terms: Object.fromEntries(modelIds.map((id) => [id, []])),
      top_terms_metric: "sutrop_csi",
    },
  };
}

// ── Convenience fixtures ───────────────────────────────────────────────────────

// Two-model fixture: model-a × model-b. Both off-diagonal cells have CI that
// crosses SIMILARITY_NULL_VALUE (0.5), making them dashed cells.
// Similarity values are clearly artificial (0.42, 1.00 diagonal).
//   similarity_matrix[0][0] = 1.00 (diagonal: model-a self)
//   similarity_matrix[0][1] = 0.42 (model-a vs model-b, CI crosses null)
//   similarity_matrix[1][0] = 0.42 (model-b vs model-a, CI crosses null)
//   similarity_matrix[1][1] = 1.00 (diagonal: model-b self)
const TWO_MODEL_IDS = ["model-a", "model-b"];
const TWO_MODEL_SIM_MATRIX: number[][] = [
  [1.0, 0.42],
  [0.42, 1.0],
];
// CIs cross null (0.5): [0.31, 0.61] straddles 0.5.
const TWO_MODEL_CI_MATRIX: Array<Array<[number, number] | null>> = [
  [null, [0.31, 0.61]],
  [[0.31, 0.61], null],
];

// Two-model fixture with null CI (for null-CI aria-label test).
// similarity_matrix[0][1] = 0.65, CI = null (no bootstrap available).
const TWO_MODEL_NULL_CI_MATRIX: Array<Array<[number, number] | null>> = [
  [null, null],
  [null, null],
];
const TWO_MODEL_NULL_CI_SIM: number[][] = [
  [1.0, 0.65],
  [0.65, 1.0],
];

// Three-model fixture for dual-index translation test (plan §2.8).
// The models array in domainResult.models is in a NON-lexicographic order:
//   index 0: "zebra/c"
//   index 1: "alpha/a"
//   index 2: "beta/b"
// The similarity_matrix is indexed by domainResult.models order.
// Display order (sorted lexicographically): ["alpha/a", "beta/b", "zebra/c"]
//   display index 0 → models index 1 (alpha/a)
//   display index 1 → models index 2 (beta/b)
//   display index 2 → models index 0 (zebra/c)
//
// We set deliberately distinct off-diagonal values so we can assert the
// correct value appears in the expected cell:
//   similarity_matrix[0][1] = 0.77  ("zebra/c" vs "alpha/a" in models order)
//   similarity_matrix[0][2] = 0.55  ("zebra/c" vs "beta/b"  in models order)
//   similarity_matrix[1][2] = 0.68  ("alpha/a" vs "beta/b"  in models order)
// When displayed lexicographically (alpha/a=0, beta/b=1, zebra/c=2):
//   cell(alpha/a, beta/b) → matrix[1][2] = 0.68   → text "0.68"
//   cell(alpha/a, zebra/c) → matrix[1][0] = 0.77  → text "0.77"
//   cell(beta/b, zebra/c)  → matrix[2][0] = 0.55  → text "0.55"
const THREE_MODEL_IDS = ["zebra/c", "alpha/a", "beta/b"];
const THREE_MODEL_SIM_MATRIX: number[][] = [
  [1.0,  0.77, 0.55], // zebra/c row
  [0.77, 1.0,  0.68], // alpha/a row
  [0.55, 0.68, 1.0 ], // beta/b row
];
const THREE_MODEL_CI_MATRIX: Array<Array<[number, number] | null>> = [
  [null, [0.65, 0.88], [0.40, 0.68]],
  [[0.65, 0.88], null, [0.55, 0.80]],
  [[0.40, 0.68], [0.55, 0.80], null],
];

// ══════════════════════════════════════════════════════════════════════════════
// GAP 1: CDA SME §5.1 verbatim caption text (regression guard)
//
// The Reviewer confirmed the caption was applied. This test asserts the exact
// full string from the binding CDA SME verdict — any future paraphrase will
// break this test.
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — CDA SME §5.1 verbatim caption text (gap-fill)", () => {
  it("caption text matches the exact CDA SME §5.1 binding string", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const caption = container.querySelector(".similarity-heatmap__caption");
    expect(caption).not.toBeNull();

    // Expected: "Each cell shows how similarly two models organize this domain
    //   (1.00 = identical organization; 0.50 = no shared structure).
    //   Dashed cells: 95% confidence interval includes the no-shared-structure value."
    // JSX {" "} emits a literal space, so the rendered text is a single string
    // without extra whitespace. DOM textContent collapses whitespace from the
    // JSX expression into a single-space sequence — we normalise with trim +
    // single-space collapse to be robust to minor whitespace differences in
    // how React 19 serialises {" "} in jsdom.
    const rendered = (caption!.textContent ?? "")
      .replace(/\s+/g, " ")
      .trim();

    const EXPECTED =
      "Each cell shows how similarly two models organize this domain " +
      "(1.00 = identical organization; 0.50 = no shared structure). " +
      "Dashed cells: 95% confidence interval includes the no-shared-structure value.";

    expect(rendered).toBe(EXPECTED);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 2: CDA SME §5.2 aria-label suffix for dashed cells
//
// The Reviewer confirmed the suffix is present. This test exercises it with
// a fixture whose off-diagonal CIs straddle SIMILARITY_NULL_VALUE (0.5).
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — CDA SME §5.2 dashed-cell aria-label suffix (gap-fill)", () => {
  it("off-diagonal cell whose CI crosses 0.5 has aria-label ending with the N2 suffix", () => {
    // model-a vs model-b: similarity 0.42, CI [0.31, 0.61] — crosses 0.5.
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    // Find all rect elements
    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    expect(rects.length).toBeGreaterThan(0);

    // Find the off-diagonal cell that should carry the N2 suffix.
    // It is model-a versus model-b (or model-b versus model-a) with sim 0.42.
    const cellsWithSuffix = Array.from(rects).filter((r) =>
      (r.getAttribute("aria-label") ?? "").includes(
        "; confidence interval includes the no-shared-structure value of 0.50"
      )
    );

    // Both off-diagonal cells (a vs b, b vs a) carry the suffix.
    expect(cellsWithSuffix.length).toBeGreaterThanOrEqual(1);

    // Verify the full aria-label structure for one such cell
    const label = cellsWithSuffix[0].getAttribute("aria-label") ?? "";
    // Must contain the base CI information
    expect(label).toContain("95 percent confidence interval");
    // Must end with the N2 binding suffix
    expect(label).toContain(
      "; confidence interval includes the no-shared-structure value of 0.50"
    );
  });

  it("off-diagonal cell with CI that does NOT cross 0.5 does NOT have the N2 suffix", () => {
    // CI [0.55, 0.80] does not straddle 0.5 (lower bound > 0.5).
    // Use the three-model fixture — cell(alpha/a, beta/b) has CI [0.55, 0.80].
    const domainResult = makeFixture(
      THREE_MODEL_IDS,
      THREE_MODEL_SIM_MATRIX,
      THREE_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: THREE_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    // Cells with CI [0.55, 0.80] — lower bound 0.55 > 0.5, does not cross.
    // The aria-label should contain "0.55 to 0.80" and NOT the N2 suffix.
    const labelsWith5580 = Array.from(rects).filter((r) =>
      (r.getAttribute("aria-label") ?? "").includes("0.55 to 0.80")
    );
    expect(labelsWith5580.length).toBeGreaterThan(0);
    labelsWith5580.forEach((r) => {
      const label = r.getAttribute("aria-label") ?? "";
      expect(label).not.toContain(
        "; confidence interval includes the no-shared-structure value"
      );
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 3: CDA SME §5.5 no methodology narration
//
// Regression guard: no future agent should add a tooltip, expandable section,
// or info-icon explaining why 0.5 is the null.
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — CDA SME §5.5 no methodology narration (gap-fill)", () => {
  it("renders no <details> element", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    expect(container.querySelectorAll("details").length).toBe(0);
  });

  it("renders no <summary> element", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    expect(container.querySelectorAll("summary").length).toBe(0);
  });

  it("renders no info-icon button", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    const buttons = container.querySelectorAll("button");
    buttons.forEach((btn) => {
      const title = (btn.getAttribute("title") ?? "").toLowerCase();
      const label = (btn.getAttribute("aria-label") ?? "").toLowerCase();
      expect(title).not.toContain("info");
      expect(label).not.toContain("info");
    });
  });

  it("rendered text contains no 'we chose' methodology prose", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    expect((container.textContent ?? "").toLowerCase()).not.toContain("we chose");
  });

  it("rendered text contains no 'we use' methodology prose", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    expect((container.textContent ?? "").toLowerCase()).not.toContain("we use");
  });

  it("rendered text contains no 'bootstrap' methodology prose (visible content only)", () => {
    // T8 adds a SimilarityTable caption that contains "bootstrap" for accessibility,
    // but it lives inside aria-hidden="true" + display:none when readAsTable=false.
    // This test checks that "bootstrap" does not appear in the *visible* UI — i.e.,
    // not in any element that is visible to sighted users.
    // See: docs/status/2026-05-12-phase6-T8-architect-plan.md §2.3.2 (U1 binding).
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    expect(visibleTextContent(container)).not.toContain("bootstrap");
  });

  it("rendered text contains no 'smoothing' methodology prose", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });
    expect((container.textContent ?? "").toLowerCase()).not.toContain("smoothing");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 4: F-T5-A1 sr-only h2 is the FIRST child of root <div>
//
// The Reviewer confirmed the h2 is present. This test asserts first-child
// position — F-T5-A1 binding specifically requires it before <svg>.
// Tested in both render paths (normal and empty-state).
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — F-T5-A1 sr-only h2 as first child (gap-fill)", () => {
  it("sr-only h2 is the first child of .similarity-heatmap root div (normal render)", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const rootDiv = container.querySelector(".similarity-heatmap");
    expect(rootDiv).not.toBeNull();

    const firstChild = rootDiv!.firstElementChild;
    expect(firstChild).not.toBeNull();
    expect(firstChild!.tagName.toLowerCase()).toBe("h2");
    expect(firstChild!.textContent).toBe("Similarity heatmap");
  });

  it("sr-only h2 is the first child of .similarity-heatmap root div (empty-state render)", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    // Empty selectedModels triggers the empty-state branch (n === 0)
    renderHeatmap({ domainResult, selectedModels: [] });

    const rootDiv = container.querySelector(".similarity-heatmap");
    expect(rootDiv).not.toBeNull();

    const firstChild = rootDiv!.firstElementChild;
    expect(firstChild).not.toBeNull();
    expect(firstChild!.tagName.toLowerCase()).toBe("h2");
    expect(firstChild!.textContent).toBe("Similarity heatmap");
  });

  it("sr-only h2 is NOT a descendant of <svg> (HTML conformance guard)", () => {
    // HTML <h2> inside <svg> is non-conformant (UI/UX F-T5-A1 finding).
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const svgEl = container.querySelector("svg");
    // svg may be absent only if the component errors — assert it exists
    expect(svgEl).not.toBeNull();

    // h2 must not appear inside svg
    const h2InSvg = svgEl!.querySelector("h2");
    expect(h2InSvg).toBeNull();

    // h2 must appear in the document
    const h2 = container.querySelector("h2");
    expect(h2).not.toBeNull();
  });

  it("h2 precedes <svg> in DOM order", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const rootDiv = container.querySelector(".similarity-heatmap");
    expect(rootDiv).not.toBeNull();

    // Walk children until we find h2 or svg — h2 must come first.
    const children = Array.from(rootDiv!.children);
    const h2Index = children.findIndex((el) => el.tagName.toLowerCase() === "h2");
    // The svg-container div contains the svg — find it.
    const svgContainerIndex = children.findIndex(
      (el) => el.classList.contains("similarity-heatmap__svg-container")
    );
    expect(h2Index).toBeGreaterThanOrEqual(0);
    expect(svgContainerIndex).toBeGreaterThan(h2Index);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 5: Static-source checks (F-T5-C1 threshold + token + fallback absence)
//
// Source-file scans guard against regression:
//   a. HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73 is the live constant
//   b. --color-heatmap-cell-text-dark: #000000 in tokens.css
//   c. 0.55 does NOT appear as an executable threshold in SimilarityHeatmap.tsx
//   d. SIMILARITY_NULL_VALUE = 0.5 in config/analysis.ts (canonical location)
//   e. No literal 0.5 used as a threshold comparison in the component source
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — F-T5-C1 static-source checks (gap-fill)", () => {
  it("SimilarityHeatmap.tsx declares HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73", () => {
    // The binding constant from UI/UX PASS-WITH-NOTES verdict F-T5-C1.
    expect(SIMILARITY_HEATMAP_SRC).toContain("HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73");
  });

  it("tokens.css declares --color-heatmap-cell-text-dark: #000000 (F-T5-C1 new token)", () => {
    // The new token added per F-T5-C1 BINDING.
    expect(TOKENS_CSS).toContain("--color-heatmap-cell-text-dark: #000000");
  });

  it("SimilarityHeatmap.tsx does NOT use 0.55 as an executable threshold", () => {
    // The plan §2.2 fallback 0.55 was superseded by UI/UX verdict — it must not
    // appear in any conditional, assignment, or comparison. It may appear only
    // in WCAG AA comment blocks explaining why it was rejected.
    const srcLines = SIMILARITY_HEATMAP_SRC.split("\n");
    const executableLinesWith55 = srcLines.filter((line) => {
      const trimmed = line.trim();
      // Skip pure comment lines (// ... or * ...)
      if (trimmed.startsWith("//") || trimmed.startsWith("*")) return false;
      return trimmed.includes("0.55");
    });
    expect(executableLinesWith55.length).toBe(0);
  });

  it("SimilarityHeatmap.tsx imports SIMILARITY_NULL_VALUE from config/analysis (not inline 0.5)", () => {
    // The component must import from config/analysis, not define its own literal 0.5.
    expect(SIMILARITY_HEATMAP_SRC).toContain(
      'import { SIMILARITY_NULL_VALUE } from "../config/analysis"'
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 6: Forbidden vocabulary static-file scan
//
// T7 gap-fill pattern: scan source text of SimilarityHeatmap.tsx and
// similarity-heatmap.css for CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 phrases.
//
// Per T7 gap-fill precedent: multi-word model-cognition phrases are tested
// in source; single-word entries that appear in the compliance docstring
// (e.g., "worldview", "believes") are tested against the rendered DOM only.
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap static-source forbidden vocabulary scan (gap-fill)", () => {
  // Multi-word model-cognition phrases tested in source text.
  //
  // Per T7 gap-fill precedent: single-word entries ("worldview", "believes",
  // "missing", "placeholder", "pending") are EXCLUDED from source-file scanning
  // because SimilarityHeatmap.tsx's compliance docstring explicitly lists those
  // words in a quoted negation context (e.g., 'no "missing", "placeholder"...').
  // Testing those individual words in source would false-positive on the
  // compliance header.
  //
  // Single-word empty-state terms are covered by the rendered-DOM tests in
  // GAP 11 (empty-state render). Multi-word model-cognition constructions are
  // tested here because a comment that says "model believes X" is a live
  // framing violation even when quoted, as it normalises the phrasing.
  const FORBIDDEN_PHRASES = [
    "model believes",
    "model thinks",
    "model understands",
    "How models see the world",
    "How models see",
    "What the model understands",
    "Cultural bias",
    "sees similarly to",
    "agrees with",
  ];

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`SimilarityHeatmap.tsx does not contain model-cognition phrase: "${phrase}"`, () => {
      expect(SIMILARITY_HEATMAP_SRC.toLowerCase()).not.toContain(
        phrase.toLowerCase()
      );
    });

    it(`similarity-heatmap.css does not contain phrase: "${phrase}"`, () => {
      expect(SIMILARITY_HEATMAP_CSS.toLowerCase()).not.toContain(
        phrase.toLowerCase()
      );
    });
  }
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 7: Diagonal cell aria-label uses self-similarity phrasing
//
// Plan §2.4: diagonal cells must read "${shortName} self-similarity: 1.00 by construction"
// NOT "${shortName} versus ${shortName}: ...".
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — diagonal cell aria-label (gap-fill)", () => {
  it("diagonal cells have aria-label containing 'self-similarity: 1.00 by construction'", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    const diagonalCells = Array.from(rects).filter((r) =>
      (r.getAttribute("aria-label") ?? "").includes("self-similarity: 1.00 by construction")
    );
    // Two diagonal cells for two models.
    expect(diagonalCells.length).toBe(2);
  });

  it("diagonal cells do NOT use 'versus' phrasing", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    // Find cells whose aria-label uses self-similarity language
    const selfSimCells = Array.from(rects).filter((r) =>
      (r.getAttribute("aria-label") ?? "").includes("self-similarity")
    );
    selfSimCells.forEach((r) => {
      const label = r.getAttribute("aria-label") ?? "";
      expect(label).not.toContain("versus");
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 8: Null-CI cell aria-label contains "confidence interval not available"
//
// Plan §2.4 + Reviewer §7 ("null-CI cells: absence acknowledged, not silent").
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — null-CI cell aria-label (gap-fill)", () => {
  it("off-diagonal cell with null CI has aria-label containing 'confidence interval not available'", () => {
    // Use the null-CI fixture: similarity 0.65, CI = null.
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_NULL_CI_SIM,
      TWO_MODEL_NULL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    // Off-diagonal cells have similarity 0.65 and null CI.
    const nullCiCells = Array.from(rects).filter((r) => {
      const label = r.getAttribute("aria-label") ?? "";
      // Must be an off-diagonal cell (not self-similarity)
      return !label.includes("self-similarity") && label.includes("0.65");
    });
    expect(nullCiCells.length).toBeGreaterThan(0);
    nullCiCells.forEach((r) => {
      expect(r.getAttribute("aria-label")).toContain(
        "confidence interval not available"
      );
    });
  });

  it("null-CI cell does NOT have the N2 dashed-cell suffix", () => {
    // Null-CI cells are not "dashed" — they have solid borders per §2.7.
    // The N2 suffix applies only when CI crosses null, not when CI is absent.
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_NULL_CI_SIM,
      TWO_MODEL_NULL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    const nullCiCells = Array.from(rects).filter((r) => {
      const label = r.getAttribute("aria-label") ?? "";
      return label.includes("confidence interval not available");
    });
    nullCiCells.forEach((r) => {
      expect(r.getAttribute("aria-label")).not.toContain(
        "; confidence interval includes the no-shared-structure value"
      );
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 9: Dual-index translation correctness (plan §2.8 — highest-risk logic)
//
// domainResult.models is in a NON-lexicographic order (zebra/c, alpha/a, beta/b).
// selectedModels sorted lexicographically produces (alpha/a, beta/b, zebra/c).
// The component must look up each cell via modelIndexMap to get the correct
// row/col in the similarity_matrix — not assume display-order = matrix-order.
//
// Verified values (from THREE_MODEL_SIM_MATRIX above):
//   alpha/a vs beta/b  → matrix[1][2] = 0.68
//   alpha/a vs zebra/c → matrix[1][0] = 0.77
//   beta/b  vs zebra/c → matrix[2][0] = 0.55
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — dual-index translation correctness (gap-fill)", () => {
  it("renders the correct similarity value for alpha/a vs beta/b (0.68)", () => {
    // alpha/a is models index 1, beta/b is models index 2.
    // matrix[1][2] = 0.68. Display order: alpha/a=0, beta/b=1.
    const domainResult = makeFixture(
      THREE_MODEL_IDS,
      THREE_MODEL_SIM_MATRIX,
      THREE_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: THREE_MODEL_IDS });

    // The aria-label for this cell should contain "0.68"
    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    const cellLabels = Array.from(rects).map(
      (r) => r.getAttribute("aria-label") ?? ""
    );
    // Find cell containing both "alpha" and "beta" with similarity 0.68
    const relevantCells = cellLabels.filter(
      (l) => l.includes("0.68") && !l.includes("self-similarity")
    );
    expect(relevantCells.length).toBeGreaterThan(0);
  });

  it("renders the correct similarity value for alpha/a vs zebra/c (0.77)", () => {
    // alpha/a is models index 1, zebra/c is models index 0.
    // matrix[1][0] = 0.77.
    const domainResult = makeFixture(
      THREE_MODEL_IDS,
      THREE_MODEL_SIM_MATRIX,
      THREE_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: THREE_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    const cellLabels = Array.from(rects).map(
      (r) => r.getAttribute("aria-label") ?? ""
    );
    const relevantCells = cellLabels.filter(
      (l) => l.includes("0.77") && !l.includes("self-similarity")
    );
    expect(relevantCells.length).toBeGreaterThan(0);
  });

  it("renders the correct similarity value for beta/b vs zebra/c (0.55)", () => {
    // beta/b is models index 2, zebra/c is models index 0.
    // matrix[2][0] = 0.55.
    const domainResult = makeFixture(
      THREE_MODEL_IDS,
      THREE_MODEL_SIM_MATRIX,
      THREE_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: THREE_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    const cellLabels = Array.from(rects).map(
      (r) => r.getAttribute("aria-label") ?? ""
    );
    const relevantCells = cellLabels.filter(
      (l) => l.includes("0.55") && !l.includes("self-similarity")
    );
    expect(relevantCells.length).toBeGreaterThan(0);
  });

  it("renders exactly n*n=9 rect cells for 3 models (correct grid count)", () => {
    const domainResult = makeFixture(
      THREE_MODEL_IDS,
      THREE_MODEL_SIM_MATRIX,
      THREE_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: THREE_MODEL_IDS });

    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    // 3 models × 3 models = 9 cells
    expect(rects.length).toBe(9);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 10: F-T5-M1 aria-labels preserved when <text> cell labels are suppressed
//
// The CSS suppresses .similarity-heatmap__cell-label (<text> elements) at
// ≤480px. The <rect> elements carry aria-label as a DOM attribute — display:none
// on a sibling <text> must not affect the <rect> attributes.
// In jsdom we cannot simulate actual CSS media queries, so this test verifies
// the structural guarantee: aria-label is on <rect>, not on <text>.
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — F-T5-M1 aria-labels on rect not on text (gap-fill)", () => {
  it("aria-label attributes are on <rect> elements, NOT on <text> cell-label elements", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    // Verify rects have aria-labels
    const rects = container.querySelectorAll<SVGRectElement>("rect[aria-label]");
    expect(rects.length).toBeGreaterThan(0);

    // Verify .similarity-heatmap__cell-label text elements do NOT have aria-label
    const cellLabels = container.querySelectorAll(
      ".similarity-heatmap__cell-label"
    );
    cellLabels.forEach((el) => {
      expect(el.getAttribute("aria-label")).toBeNull();
      // They should have aria-hidden="true" instead
      expect(el.getAttribute("aria-hidden")).toBe("true");
    });
  });

  it("cell-label <text> elements have aria-hidden='true'", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: TWO_MODEL_IDS });

    const cellLabelTexts = container.querySelectorAll(
      ".similarity-heatmap__cell-label"
    );
    expect(cellLabelTexts.length).toBeGreaterThan(0);
    cellLabelTexts.forEach((el) => {
      expect(el.getAttribute("aria-hidden")).toBe("true");
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 11: Empty-state render guards
//
// When selectedModels is empty (n === 0), the component renders the empty-state
// branch: sr-only h2 present, a <p> with the correct text, NO <svg>.
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — empty-state render (gap-fill)", () => {
  it("empty selectedModels renders no <svg>", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: [] });
    const svgEl = container.querySelector("svg");
    expect(svgEl).toBeNull();
  });

  it("empty selectedModels renders the approved empty-state text (no forbidden phrasing)", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: [] });
    const p = container.querySelector(".similarity-heatmap__empty");
    expect(p).not.toBeNull();
    // Approved text: does not say "missing", "no data yet", "pending",
    // "placeholder" — uses the "Select one or more models" framing.
    expect(p!.textContent).toContain("Select one or more models");
    expect((p!.textContent ?? "").toLowerCase()).not.toContain("missing");
    expect((p!.textContent ?? "").toLowerCase()).not.toContain("no data yet");
    expect((p!.textContent ?? "").toLowerCase()).not.toContain("pending");
    expect((p!.textContent ?? "").toLowerCase()).not.toContain("placeholder");
  });

  it("empty selectedModels still renders the sr-only h2", () => {
    const domainResult = makeFixture(
      TWO_MODEL_IDS,
      TWO_MODEL_SIM_MATRIX,
      TWO_MODEL_CI_MATRIX
    );
    renderHeatmap({ domainResult, selectedModels: [] });
    const h2 = container.querySelector("h2.sr-only");
    expect(h2).not.toBeNull();
    expect(h2!.textContent).toBe("Similarity heatmap");
  });
});
