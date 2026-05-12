// @vitest-environment jsdom
/**
 * FreeListCompare + FreeListColumn component tests — Phase 6 T7.
 *
 * Covers acceptance criteria from docs/status/2026-05-12-phase6-T7-architect-plan.md §3:
 *   AC #2  — freelist tab is no longer disabled in VizSwitcher
 *   AC #4  — columns render terms with R10 bars and accessible labels
 *   AC #5  — cross-column hover highlight
 *   AC #6  — keyboard focus parity with hover
 *   AC #7  — aria-label contains item + CSI + "collection runs" wording
 *   AC #8  — synthetic-fixture empty states (Case B and Case C)
 *   AC #9  — shared-term ★ glyph logic
 *   AC #10 — Case A (no models selected)
 *   AC #11 — WCAG AA: h2.sr-only present, h3 column headers, container aria-label
 *
 * Also tests VizSwitcher — Free Lists tab enabled (AC #2).
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures only.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { FreeListCompare } from "../components/FreeListCompare";
import type { FreeListCompareProps } from "../components/FreeListCompare";
import { VizSwitcher } from "../components/VizSwitcher";
import type { DomainResultPublished, WithinModelResult, EllipseParams } from "../data/types";

// ── Render helpers ────────────────────────────────────────────────────────────

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

function renderCompare(props: FreeListCompareProps): void {
  act(() => {
    root.render(createElement(FreeListCompare, props));
  });
}

// ── Fixture builders ──────────────────────────────────────────────────────────

/**
 * Builds a minimal DomainResultPublished fixture.
 * The sutrop_csi field is passed as `unknown` (via cast) to simulate the
 * actual JSON shape, which disagrees with data/types.ts (T14 doc-sweep).
 */
function makeFixture(
  modelIds: string[],
  sutropCsiOverride?: Record<
    string,
    Array<{ item: string; csi: number; f_mentions: number; n_runs: number; mean_position: number }> | undefined
  >
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
      centroid_run_id: "run-1",
      mds_within_model: [],
    });
  });

  // Build default sutrop_csi with a few terms per model
  const defaultSutropCsi: Record<
    string,
    Array<{ item: string; csi: number; f_mentions: number; n_runs: number; mean_position: number }>
  > = {};
  for (const id of modelIds) {
    defaultSutropCsi[id] = [
      { item: "alpha", csi: 0.75, f_mentions: 3, n_runs: 4, mean_position: 1.0 },
      { item: "beta",  csi: 0.50, f_mentions: 2, n_runs: 4, mean_position: 2.0 },
      { item: "gamma", csi: 0.25, f_mentions: 1, n_runs: 4, mean_position: 3.0 },
    ];
  }

  const sutropCsi = sutropCsiOverride !== undefined
    ? { ...defaultSutropCsi, ...sutropCsiOverride }
    : defaultSutropCsi;

  return {
    domain_slug: "test-domain",
    analysis_version: "0.2",
    models: modelIds.map((id) => ({
      provider: "test",
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
    mds_coordinates: mds_coordinates as unknown as Record<string, [[number, number]]>,
    mds_uncertainty,
    similarity_matrix: {},
    similarity_ci: {},
    consensus_score: 0.71,
    consensus_ci: [0.65, 0.77],
    consensus_type: "STRONG_CONSENSUS",
    sutrop_csi: sutropCsi as unknown as Record<string, Record<string, number>>,
    within_model_results,
    groundings: [],
    generated_lede: "Test lede.",
    generated_at: "2026-05-12T00:00:00Z",
    display: {
      r1_states: Object.fromEntries(modelIds.map((id) => [id, "typical_concentration" as const])),
      top_terms: Object.fromEntries(modelIds.map((id) => [id, ["alpha", "beta"]])),
      top_terms_metric: "sutrop_csi",
    },
  };
}

// ── Model colors (2-model subset) ─────────────────────────────────────────────
const TWO_MODEL_COLORS: Record<string, string> = {
  "model-a": "#3360a9",
  "model-b": "#c0392b",
};

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #2: VizSwitcher freelist tab is enabled
// ══════════════════════════════════════════════════════════════════════════════

describe("VizSwitcher — Phase 6 T7: Free Lists tab is active (AC #2)", () => {
  it("Free Lists tab does not have aria-disabled attribute", () => {
    const vsContainer = document.createElement("div");
    document.body.appendChild(vsContainer);
    const vsRoot = createRoot(vsContainer);

    act(() => {
      vsRoot.render(
        createElement(VizSwitcher, { activeTab: "mds", onTabChange: vi.fn() })
      );
    });

    const tabs = vsContainer.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    const freeListsTab = Array.from(tabs).find(
      (t) => t.textContent?.trim() === "Free Lists"
    );
    expect(freeListsTab).toBeDefined();
    expect(freeListsTab!.getAttribute("aria-disabled")).toBeNull();

    act(() => { vsRoot.unmount(); });
    vsContainer.remove();
  });

  it("clicking Free Lists tab calls onTabChange('freelist')", () => {
    const vsContainer = document.createElement("div");
    document.body.appendChild(vsContainer);
    const vsRoot = createRoot(vsContainer);

    const onTabChange = vi.fn();
    act(() => {
      vsRoot.render(
        createElement(VizSwitcher, { activeTab: "mds", onTabChange })
      );
    });

    const tabs = vsContainer.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    const freeListsTab = Array.from(tabs).find(
      (t) => t.textContent?.trim() === "Free Lists"
    )!;

    act(() => { freeListsTab.click(); });

    expect(onTabChange).toHaveBeenCalledWith("freelist");

    act(() => { vsRoot.unmount(); });
    vsContainer.remove();
  });

  it("Free Lists tab renders with aria-selected='true' when activeTab='freelist'", () => {
    const vsContainer = document.createElement("div");
    document.body.appendChild(vsContainer);
    const vsRoot = createRoot(vsContainer);

    act(() => {
      vsRoot.render(
        createElement(VizSwitcher, { activeTab: "freelist", onTabChange: vi.fn() })
      );
    });

    const tabs = vsContainer.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    const freeListsTab = Array.from(tabs).find(
      (t) => t.textContent?.trim() === "Free Lists"
    );
    expect(freeListsTab!.getAttribute("aria-selected")).toBe("true");

    act(() => { vsRoot.unmount(); });
    vsContainer.remove();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #11: WCAG AA — h2.sr-only, container aria-label, h3 headers
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — WCAG AA structure (AC #11)", () => {
  it("renders an sr-only h2 as first child of root (F-T7-A1 binding)", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const h2 = container.querySelector("h2.sr-only");
    expect(h2).not.toBeNull();
    expect(h2!.textContent).toBe("Free list comparison");
  });

  it("root element has aria-label='Side-by-side free lists'", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const root = container.querySelector("[aria-label='Side-by-side free lists']");
    expect(root).not.toBeNull();
  });

  it("each column header is an h3 element", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const h3s = container.querySelectorAll("h3");
    expect(h3s.length).toBe(2);
  });

  it("column list is an <ol> (ordered list — rank is the ordering)", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const ol = container.querySelector("ol.freelist-column__list");
    expect(ol).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #4: Terms render with R10 bars and accessible labels
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — term rendering (AC #4)", () => {
  it("renders all terms from sutrop_csi as list items", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const items = container.querySelectorAll("li.freelist-column__item");
    // Default fixture has 3 terms per model
    expect(items.length).toBe(3);
  });

  it("renders terms in descending CSI order", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const termSpans = container.querySelectorAll(".freelist-column__term");
    const termTexts = Array.from(termSpans).map((s) => s.textContent);
    // alpha(0.75) > beta(0.50) > gamma(0.25)
    expect(termTexts).toEqual(["alpha", "beta", "gamma"]);
  });

  it("each term has an R10 inclusion-frequency bar", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const bars = container.querySelectorAll(".freelist-column__freq-bar");
    expect(bars.length).toBe(3);
    const fills = container.querySelectorAll(".freelist-column__freq-fill");
    expect(fills.length).toBe(3);
  });

  it("each term has a numeric frequency label (f_mentions/n_runs)", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const labels = container.querySelectorAll(".freelist-column__freq-label");
    const labelTexts = Array.from(labels).map((l) => l.textContent);
    // alpha: 3/4, beta: 2/4, gamma: 1/4
    expect(labelTexts).toContain("3/4");
    expect(labelTexts).toContain("2/4");
    expect(labelTexts).toContain("1/4");
  });

  it("renders the R10 column caption verbatim (CDA SME §5.1 binding)", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const caption = container.querySelector(".freelist-column__r10-caption");
    expect(caption).not.toBeNull();
    // Verbatim per CDA SME §5.1
    // Use standard ASCII apostrophe (U+0027) — component renders &apos; as char 39.
    // The source file may have a smart-quote; use string without apostrophe to be safe.
    expect(caption!.textContent).toContain("Bar shows the fraction of this model");
    expect(caption!.textContent).toContain("collection runs that produced this term.");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #7: accessible label content (CDA SME §5.2 binding)
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — accessible labels (AC #7)", () => {
  it("each <li> has aria-label containing item, CSI score, and 'collection runs'", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const firstItem = container.querySelector("li.freelist-column__item");
    expect(firstItem).not.toBeNull();
    const label = firstItem!.getAttribute("aria-label");
    expect(label).not.toBeNull();
    // Must contain the item name
    expect(label).toContain("alpha");
    // Must contain "Sutrop salience score" (CDA SME §5.2 exact wording)
    expect(label).toContain("Sutrop salience score");
    // Must contain "collection runs" (CDA SME §5.2 exact wording)
    expect(label).toContain("collection runs");
  });

  it("aria-label format: 'alpha, Sutrop salience score 0.75, included in 3 of 4 collection runs'", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const items = container.querySelectorAll("li.freelist-column__item");
    const alphaItem = Array.from(items).find(
      (li) => li.getAttribute("aria-label")?.startsWith("alpha")
    );
    expect(alphaItem).toBeDefined();
    expect(alphaItem!.getAttribute("aria-label")).toBe(
      "alpha, Sutrop salience score 0.75, included in 3 of 4 collection runs"
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #5 + #6: hover and focus parity (cross-column highlight)
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — hover/focus cross-column highlight (AC #5, #6)", () => {
  it("mouseenter on a term adds --hovered class", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const firstItem = container.querySelector("li.freelist-column__item")!;

    // React's onMouseEnter is triggered by mouseover (which bubbles).
    // mouseenter does not bubble in native DOM; React synthesizes enter/leave from over/out.
    act(() => {
      firstItem.dispatchEvent(new MouseEvent("mouseover", { bubbles: true, relatedTarget: null }));
    });

    expect(firstItem.classList.contains("freelist-column__item--hovered")).toBe(true);
  });

  it("mouseleave clears the --hovered class", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const firstItem = container.querySelector("li.freelist-column__item")!;

    act(() => {
      firstItem.dispatchEvent(new MouseEvent("mouseover", { bubbles: true, relatedTarget: null }));
    });
    act(() => {
      firstItem.dispatchEvent(new MouseEvent("mouseout", { bubbles: true, relatedTarget: null }));
    });

    expect(firstItem.classList.contains("freelist-column__item--hovered")).toBe(false);
  });

  it("focus on a term adds --hovered class (keyboard focus parity)", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const firstItem = container.querySelector("li.freelist-column__item")!;

    // React's onFocus is triggered by the bubbling focusin event at the root.
    act(() => {
      firstItem.dispatchEvent(new FocusEvent("focusin", { bubbles: true }));
    });

    expect(firstItem.classList.contains("freelist-column__item--hovered")).toBe(true);
  });

  it("blur clears the --hovered class (keyboard focus parity)", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const firstItem = container.querySelector("li.freelist-column__item")!;

    act(() => {
      firstItem.dispatchEvent(new FocusEvent("focusin", { bubbles: true }));
    });
    act(() => {
      firstItem.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
    });

    expect(firstItem.classList.contains("freelist-column__item--hovered")).toBe(false);
  });

  it("hovering term in column A highlights the same term in column B (cross-column)", () => {
    // Both models have "alpha" — it should be highlighted in both when hovered
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    // Find all "alpha" items across columns
    const allItems = container.querySelectorAll("li.freelist-column__item");
    const alphaItems = Array.from(allItems).filter(
      (li) => li.getAttribute("aria-label")?.startsWith("alpha")
    );
    // Should have 2 alpha items (one per column)
    expect(alphaItems.length).toBe(2);

    // Hover the first alpha item (React synthesizes mouseenter from mouseover)
    act(() => {
      alphaItems[0].dispatchEvent(new MouseEvent("mouseover", { bubbles: true, relatedTarget: null }));
    });

    // Both alpha items should have the --hovered class
    expect(alphaItems[0].classList.contains("freelist-column__item--hovered")).toBe(true);
    expect(alphaItems[1].classList.contains("freelist-column__item--hovered")).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #9: shared-term star glyph
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — shared-term star glyph (AC #9)", () => {
  it("terms in ALL selected models get a ★ glyph", () => {
    // Both models have alpha, beta, gamma — all should be shared
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const stars = container.querySelectorAll(".freelist-column__shared-star");
    // 3 terms × 2 columns = 6 stars
    expect(stars.length).toBe(6);
  });

  it("shared terms have '; in every selected model' in aria-label", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const items = container.querySelectorAll("li.freelist-column__item");
    const sharedItems = Array.from(items).filter(
      (li) => li.getAttribute("aria-label")?.includes("; in every selected model")
    );
    // 3 shared terms × 2 columns = 6
    expect(sharedItems.length).toBe(6);
  });

  it("with only 1 model selected, no terms are shared — no star glyph", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const stars = container.querySelectorAll(".freelist-column__shared-star");
    expect(stars.length).toBe(0);
  });

  it("terms NOT in all selected models do not get a ★ glyph", () => {
    // model-a has alpha/beta/gamma; model-b has only delta/epsilon
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": [
        { item: "delta",   csi: 0.8, f_mentions: 4, n_runs: 4, mean_position: 1.0 },
        { item: "epsilon", csi: 0.4, f_mentions: 2, n_runs: 4, mean_position: 2.0 },
      ],
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const stars = container.querySelectorAll(".freelist-column__shared-star");
    // No overlap → no shared terms → no stars
    expect(stars.length).toBe(0);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #10: Case A (no models selected)
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — Case A: no models selected (AC #10)", () => {
  it("renders the Case A instruction when selectedModels is empty", () => {
    const domainResult = makeFixture([]);
    renderCompare({
      domainResult,
      modelColors: {},
      selectedModels: [],
    });

    const empty = container.querySelector(".freelist-compare__empty");
    expect(empty).not.toBeNull();
    expect(empty!.textContent).toContain(
      "Select one or more models to see their free lists."
    );
  });

  it("renders no columns when selectedModels is empty", () => {
    const domainResult = makeFixture([]);
    renderCompare({
      domainResult,
      modelColors: {},
      selectedModels: [],
    });

    const columns = container.querySelectorAll(".freelist-column");
    expect(columns.length).toBe(0);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — AC #8: empty states Case B and Case C (synthetic fixtures)
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — Case B: no salience data (AC #8)", () => {
  it("renders Case B caption '(no salience data for this model)' when sutrop_csi is missing for model", () => {
    // model-b has no sutrop_csi entry at all (key not present)
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": undefined,
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const captions = container.querySelectorAll(".freelist-column__empty-caption");
    const captionTexts = Array.from(captions).map((c) => c.textContent?.trim());
    expect(captionTexts).toContain("(no salience data for this model)");
  });

  it("Case B: column still renders header with model name", () => {
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": undefined,
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const headers = container.querySelectorAll("h3.freelist-column__model-name");
    expect(headers.length).toBe(2);
  });

  it("Case B: R10 caption is suppressed for the empty column", () => {
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": undefined,
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    // Only model-a has terms, so only 1 R10 caption
    const r10Captions = container.querySelectorAll(".freelist-column__r10-caption");
    expect(r10Captions.length).toBe(1);
  });
});

describe("FreeListCompare — Case C: no terms produced (AC #8)", () => {
  it("renders Case C caption '(no terms produced)' when sutrop_csi is empty array", () => {
    // model-b has an empty sutrop_csi array (the z-ai/glm-5.1 empty-freelist case)
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": [],
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const captions = container.querySelectorAll(".freelist-column__empty-caption");
    const captionTexts = Array.from(captions).map((c) => c.textContent?.trim());
    expect(captionTexts).toContain("(no terms produced)");
  });

  it("Case C: no term list items rendered for the empty column", () => {
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": [],
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    // Only model-a's terms should be rendered
    const items = container.querySelectorAll("li.freelist-column__item");
    expect(items.length).toBe(3); // 3 terms from model-a only
  });

  it("Case C caption does not contain forbidden vocabulary", () => {
    const domainResult = makeFixture(["model-a", "model-b"], {
      "model-b": [],
    });
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const captions = container.querySelectorAll(".freelist-column__empty-caption");
    captions.forEach((c) => {
      const text = c.textContent?.toLowerCase() ?? "";
      // CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 forbidden vocabulary
      expect(text).not.toContain("missing");
      expect(text).not.toContain("placeholder");
      expect(text).not.toContain("no data yet");
      expect(text).not.toContain("pending");
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Forbidden vocabulary in all component text
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — forbidden vocabulary (AC #15, #16)", () => {
  it("component text contains none of the CLAUDE.md §7 forbidden phrases", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const allText = container.textContent?.toLowerCase() ?? "";
    // Forbidden vocabulary per CLAUDE.md §7 / ARCHITECTURE.md §1.5.4
    expect(allText).not.toMatch(/\bbelieves\b/);
    expect(allText).not.toMatch(/\bworldview\b/);
    expect(allText).not.toMatch(/how models see the world/i);
    expect(allText).not.toMatch(/what the model understands/i);
    expect(allText).not.toMatch(/cultural bias(?!\s+\w)/i);
  });

  it("Case A empty-state text contains no forbidden vocabulary", () => {
    const domainResult = makeFixture([]);
    renderCompare({
      domainResult,
      modelColors: {},
      selectedModels: [],
    });

    const emptyText = container.querySelector(".freelist-compare__empty")?.textContent?.toLowerCase() ?? "";
    expect(emptyText).not.toContain("missing");
    expect(emptyText).not.toContain("pending");
    expect(emptyText).not.toContain("placeholder");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Sort order with deterministic tie-breaks
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — sort order (plan §2.4)", () => {
  it("sorts by CSI descending, then mean_position ascending, then item alphabetically", () => {
    // Tie: alpha and beta have same CSI — alpha has lower mean_position
    // Tie: zeta and omega have same CSI and mean_position — omega < zeta alphabetically
    const domainResult = makeFixture(["model-a"], {
      "model-a": [
        { item: "zeta",  csi: 0.5, f_mentions: 2, n_runs: 4, mean_position: 3.0 },
        { item: "beta",  csi: 0.8, f_mentions: 4, n_runs: 4, mean_position: 2.0 },
        { item: "alpha", csi: 0.8, f_mentions: 3, n_runs: 4, mean_position: 1.0 },
        { item: "omega", csi: 0.5, f_mentions: 2, n_runs: 4, mean_position: 3.0 },
      ],
    });
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const termSpans = container.querySelectorAll(".freelist-column__term");
    const termTexts = Array.from(termSpans).map((s) => s.textContent);
    // beta and alpha tie on CSI=0.8; alpha wins on lower mean_position
    // zeta and omega tie on CSI=0.5, mean_position=3.0; omega < zeta alphabetically
    expect(termTexts).toEqual(["alpha", "beta", "omega", "zeta"]);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Column count and term count line
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — column structure", () => {
  it("renders one column per selected model", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const columns = container.querySelectorAll(".freelist-column");
    expect(columns.length).toBe(2);
  });

  it("term count line shows correct count", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const count = container.querySelector(".freelist-column__count");
    expect(count).not.toBeNull();
    expect(count!.textContent).toContain("3 terms");
  });
});
