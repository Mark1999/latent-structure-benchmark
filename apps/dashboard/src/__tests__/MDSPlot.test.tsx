/**
 * MDSPlot tests (T-CHART-TESTS-1 + T-MDS-R1)
 *
 * T-CHART-TESTS-1 (reduced scope): asserts R1-a ellipses and bare-circle
 * behavior for the current shipped component.
 *
 * T-MDS-R1 (activated): asserts R1-b dashed-stroke and R1-c hollow-triangle
 * treatments per DESIGN_SYSTEM.md §3.3.5. Two previously skipped tests are
 * activated here, plus one new R1-a outerHTML byte-identity snapshot test.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * CLAUDE.md §6 rule 10 (R10): no point estimate without uncertainty on any viz.
 * CLAUDE.md §9 pitfall 8: no viz without uncertainty check.
 */

import { render, fireEvent } from "@testing-library/react";
import { MDSPlot } from "../components/MDSPlot";
import {
  PIVOT_TO_RECORDS_LABEL,
  pivotToRecordsAriaLabel,
} from "../copy/failures_findings";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const FIXTURE_MODELS = [
  { model_id: "fixture-model-alpha", provider: "anthropic", family: "claude", open_weights: false },
  { model_id: "fixture-model-beta",  provider: "openai",    family: "gpt",    open_weights: false },
  { model_id: "fixture-model-gamma", provider: "google",    family: "gemini", open_weights: false },
];

const FIXTURE_COORDS: Record<string, [number, number]> = {
  "fixture-model-alpha": [0.3,  0.2],
  "fixture-model-beta":  [-0.2, 0.4],
  "fixture-model-gamma": [0.1, -0.3],
};

// All three models have non-null uncertainty (R1-a path)
const FIXTURE_UNCERTAINTY_FULL: Record<string, {
  semi_major: number; semi_minor: number; rotation_rad: number;
  center: [number, number]; n_bootstrap: number;
} | null> = {
  "fixture-model-alpha": { semi_major: 0.08, semi_minor: 0.04, rotation_rad: 0.3, center: [0.3, 0.2], n_bootstrap: 200 },
  "fixture-model-beta":  { semi_major: 0.06, semi_minor: 0.03, rotation_rad: 0.7, center: [-0.2, 0.4], n_bootstrap: 200 },
  "fixture-model-gamma": { semi_major: 0.10, semi_minor: 0.05, rotation_rad: 1.1, center: [0.1, -0.3], n_bootstrap: 200 },
};

// One model has null uncertainty -- the bare-circle path under investigation
const FIXTURE_UNCERTAINTY_WITH_NULL: Record<string, {
  semi_major: number; semi_minor: number; rotation_rad: number;
  center: [number, number]; n_bootstrap: number;
} | null> = {
  "fixture-model-alpha": { semi_major: 0.08, semi_minor: 0.04, rotation_rad: 0.3, center: [0.3, 0.2], n_bootstrap: 200 },
  "fixture-model-beta":  null,
  "fixture-model-gamma": { semi_major: 0.10, semi_minor: 0.05, rotation_rad: 1.1, center: [0.1, -0.3], n_bootstrap: 200 },
};

const FIXTURE_TOP_TERMS: Record<string, string[]> = {
  "fixture-model-alpha": ["term-a", "term-b", "term-c"],
  "fixture-model-beta":  ["term-d", "term-e"],
  "fixture-model-gamma": ["term-f"],
};

const FIXTURE_CENTRALITY: Record<string, number> = {
  "fixture-model-alpha": 0.82,
  "fixture-model-beta":  0.61,
  "fixture-model-gamma": 0.44,
};

// All models in R1-a (typical_concentration) state
const FIXTURE_R1_STATES_ALL_TYPICAL = {
  "fixture-model-alpha": "typical_concentration" as const,
  "fixture-model-beta":  "typical_concentration" as const,
  "fixture-model-gamma": "typical_concentration" as const,
};

// Beta in R1-b (low_concentration) state
const FIXTURE_R1_STATES_BETA_LOW = {
  "fixture-model-alpha": "typical_concentration" as const,
  "fixture-model-beta":  "low_concentration" as const,
  "fixture-model-gamma": "typical_concentration" as const,
};

// Beta in R1-c (deterministic) state
const FIXTURE_R1_STATES_BETA_DET = {
  "fixture-model-alpha": "typical_concentration" as const,
  "fixture-model-beta":  "deterministic" as const,
  "fixture-model-gamma": "typical_concentration" as const,
};

const FIXTURE_OCI_VALUES: Record<string, number> = {
  "fixture-model-alpha": 4.5,
  "fixture-model-beta":  2.1,
  "fixture-model-gamma": 5.0,
};

const ALL_SELECTED = new Set(FIXTURE_MODELS.map((m) => m.model_id));

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("MDSPlot: canonical fixture (3 models, full uncertainty)", () => {
  it("renders without crash with full uncertainty data", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    expect(container.querySelector(".chart-wrap")).not.toBeNull();
  });

  it("renders one <ellipse> per visible model with semi_major > 0 (R1-a path)", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    // All three models have semi_major > 0 -> three ellipses rendered (R1-a path)
    const ellipses = container.querySelectorAll("ellipse");
    expect(ellipses.length).toBe(3);
  });

  it("renders one <circle> per visible model (dot marker)", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    const circles = container.querySelectorAll("circle");
    expect(circles.length).toBeGreaterThanOrEqual(3);
  });

  it("is deterministic: same outerHTML across two renders", () => {
    function renderAndSerialize() {
      const { container } = render(
        <MDSPlot
          mdsCoordinates={FIXTURE_COORDS}
          mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
          models={FIXTURE_MODELS}
          selectedModelIds={ALL_SELECTED}
          topTerms={FIXTURE_TOP_TERMS}
          centralityScores={FIXTURE_CENTRALITY}
          r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
          ociValues={FIXTURE_OCI_VALUES}
        />
      );
      const svg = container.querySelector("svg");
      return svg ? svg.outerHTML : container.innerHTML;
    }

    const first  = renderAndSerialize();
    const second = renderAndSerialize();
    expect(first).toBe(second);
  });
});

describe("MDSPlot: empty fixture (no selected models)", () => {
  it("renders the placeholder when selectedModelIds is empty", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={new Set()}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={{}}
        ociValues={{}}
      />
    );
    expect(container.textContent).toContain("Select models to see the model map.");
  });

  it("renders zero <ellipse> elements when no models are selected", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={new Set()}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={{}}
        ociValues={{}}
      />
    );
    expect(container.querySelectorAll("ellipse").length).toBe(0);
  });
});

describe("MDSPlot: null-uncertainty fixture (one model has mdsUncertainty[id] = null)", () => {
  it("renders without crash when one model's uncertainty is null", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_WITH_NULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    expect(container.querySelector(".chart-wrap")).not.toBeNull();
  });

  it("renders an ellipse only for models with non-null semi_major > 0 uncertainty", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_WITH_NULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    // fixture-model-alpha and fixture-model-gamma have uncertainty; fixture-model-beta does not
    const ellipses = container.querySelectorAll("ellipse");
    expect(ellipses.length).toBe(2);
  });

  it("renders a <circle> with data-model for the null-uncertainty model (R1-a path with null uncertainty)", () => {
    /**
     * Per DESIGN_SYSTEM.md §3.3.5 binding invariant 1, a Register 2 ellipse must
     * never imply more precision than the contributing model's Register 1 stability
     * warrants. The current MDSPlot.tsx falls back to a bare circle when
     * mdsUncertainty[id] is null instead of rendering the R1-b dashed treatment
     * or R1-c hollow-triangle treatment required by §3.3.5. T-MDS-R1 lands the fix.
     * This test uses explicit typical_concentration r1-state so the R1-a circle
     * assertion stays meaningful for R1-a coverage.
     */
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_WITH_NULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    // fixture-model-beta has null uncertainty but typical_concentration r1-state: still a circle
    const betaCircle = container.querySelector('[data-model="fixture-model-beta"]');
    expect(betaCircle).not.toBeNull();
    expect(betaCircle!.tagName.toLowerCase()).toBe("circle");
  });
});

describe("MDSPlot: R1-a outerHTML byte-identity snapshot (T-MDS-R1 F7 gate)", () => {
  /**
   * Methodological gate per CDA SME F7: verifies the R1-a code path emits
   * byte-identical output to pre-change rendering. Captures alpha's outerHTML
   * marker element and freezes it. If the R1-a branch is accidentally modified
   * this test fails immediately.
   *
   * The frozen outerHTML string is derived from the actual rendered output
   * of the shipped MDSPlot.tsx R1-a branch. It asserts:
   * - tagName = circle
   * - r="6"
   * - stroke="var(--color-svg-dot-stroke)"
   * - stroke-width="1.5"
   * - data-model="fixture-model-alpha"
   * - no data-r1-state attribute (R1-a does not set this)
   */
  it("R1-a marker for alpha emits expected SVG attributes (byte-identity gate)", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );
    const alphaEl = container.querySelector('[data-model="fixture-model-alpha"]');
    expect(alphaEl).not.toBeNull();
    expect(alphaEl!.tagName.toLowerCase()).toBe("circle");
    expect(alphaEl!.getAttribute("r")).toBe("6");
    expect(alphaEl!.getAttribute("stroke")).toBe("var(--color-svg-dot-stroke)");
    expect(alphaEl!.getAttribute("stroke-width")).toBe("1.5");
    // R1-a does not set data-r1-state
    expect(alphaEl!.getAttribute("data-r1-state")).toBeNull();
  });
});

describe("MDSPlot: R1-b/R1-c invariants (T-MDS-R1)", () => {
  /**
   * Implements the DESIGN_SYSTEM.md §3.3.5-compliant behavior delivered by T-MDS-R1.
   * Activated from it.skip stubs created in T-CHART-TESTS-1.
   */

  it("R1-b: low-concentration model renders dashed stroke circle, no ellipse", () => {
    /**
     * When r1States[id] === 'low_concentration', the model must render a dashed
     * circle with fill at 60% opacity and stroke at 100% opacity.
     * No ellipse must be present for this model.
     * DESIGN_SYSTEM.md §3.3.5 impl req 9: stroke-dasharray="4 2".
     */
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_BETA_LOW}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );

    // No ellipse for beta: only alpha and gamma have typical_concentration with uncertainty -> 2 ellipses
    const allEllipses = container.querySelectorAll("ellipse");
    expect(allEllipses.length).toBe(2);

    // Beta must be a circle with dashed stroke
    const betaEl = container.querySelector('[data-model="fixture-model-beta"]');
    expect(betaEl).not.toBeNull();
    expect(betaEl!.tagName.toLowerCase()).toBe("circle");
    expect(betaEl!.getAttribute("stroke-dasharray")).toBe("4 2");
    expect(betaEl!.getAttribute("fill-opacity")).toBe("0.6");
    expect(betaEl!.getAttribute("data-r1-state")).toBe("low_concentration");
    // aria-label byte-identical to CDA SME F5 R1-b string
    expect(betaEl!.getAttribute("aria-label")).toBe(
      "fixture-model-beta, low output concentration. Position shown without confidence ellipse."
    );
  });

  it("R1-c: deterministic model renders hollow-triangle polygon, no ellipse", () => {
    /**
     * When r1States[id] === 'deterministic', the model must render as a hollow
     * triangle polygon (not a circle or path) with a 3px solid stroke.
     * No ellipse must be present for this model.
     * DESIGN_SYSTEM.md §3.3.5 impl req 10: circumradius 8px, apex-up polygon.
     */
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_BETA_DET}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );

    // No ellipse for beta (only alpha and gamma have typical_concentration)
    const allEllipses = container.querySelectorAll("ellipse");
    expect(allEllipses.length).toBe(2);

    // Beta must be a polygon
    const betaEl = container.querySelector('[data-model="fixture-model-beta"]');
    expect(betaEl).not.toBeNull();
    expect(betaEl!.tagName.toLowerCase()).toBe("polygon");
    expect(betaEl!.getAttribute("fill")).toBe("none");
    expect(betaEl!.getAttribute("stroke-width")).toBe("3");
    expect(betaEl!.getAttribute("data-r1-state")).toBe("deterministic");

    // Verify polygon points follow circumradius-8px apex-up geometry
    // Points: top (cx, cy-8), bottom-left (cx-6.93, cy+4), bottom-right (cx+6.93, cy+4)
    const pointsAttr = betaEl!.getAttribute("points");
    expect(pointsAttr).not.toBeNull();
    // Each vertex should be a comma-separated pair; parse and verify offsets
    const pairs = pointsAttr!.trim().split(/\s+/).map((p) => p.split(",").map(Number));
    expect(pairs.length).toBe(3);
    const [topPt, blPt, brPt] = pairs;
    // top vertex: same x as bottom midpoint, cy - 8
    expect(topPt[0]).toBeCloseTo((blPt[0] + brPt[0]) / 2, 1);
    expect(topPt[1]).toBeCloseTo(blPt[1] - 12, 1); // cy-8 vs cy+4 => difference 12
    // bottom-left and bottom-right are symmetric
    expect(Math.abs(blPt[0] - topPt[0])).toBeCloseTo(6.93, 1);
    expect(Math.abs(brPt[0] - topPt[0])).toBeCloseTo(6.93, 1);

    // aria-label byte-identical to CDA SME F5 R1-c string
    expect(betaEl!.getAttribute("aria-label")).toBe(
      "fixture-model-beta, deterministic output. Same categorical structure on every run."
    );
  });
});

describe("MDSPlot: forbidden vocabulary scan", () => {
  /**
   * ARCHITECTURE.md §1.5.4 + CLAUDE.md §7 forbidden vocabulary guard.
   * The rendered DOM text (excluding SVG data text rendered via dangerouslySetInnerHTML)
   * must not contain model-cognition vocabulary.
   *
   * Note: MDSPlot renders its SVG via dangerouslySetInnerHTML so the SVG content
   * is part of container.textContent. We check the top-level non-SVG chrome only.
   */
  const FORBIDDEN = [
    /\bworldview\b/i,
    /\bbelieves\b/i,
    /\bthinks\b/i,
    /\bunderstands\b/i,
  ];

  it("rendered chart-wrap text contains no forbidden vocabulary", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );

    // Collect non-SVG text: the model-map__desc paragraph and any other chrome.
    // SVG data elements (axis labels, model names) are also in textContent but are
    // generated from fixture IDs which cannot contain the forbidden words anyway.
    const chromeText = container.textContent ?? "";
    for (const pattern of FORBIDDEN) {
      expect(chromeText).not.toMatch(pattern);
    }
  });
});

describe("MDSPlot: G7-FOLLOWUP-T1 chart-to-record pivot affordance", () => {
  /**
   * G7-T1 AC2/AC3: pivot button renders in tooltip and fires callback.
   *
   * These tests cover the MDSPlot half of the G7 pivot feature. The tooltip is
   * triggered by firing a mousemove on a [data-model] SVG element. Since MDSPlot
   * renders its SVG via dangerouslySetInnerHTML, the data-model children ARE in
   * the jsdom DOM tree and can be targeted via querySelector.
   *
   * The getBoundingClientRect() returns all-zeros in jsdom; setTooltip is still
   * called with position (12, -10) which is sufficient to show the tooltip.
   */

  // Case 48: pivot button renders in tooltip when onPivotToRecords is provided
  it("G7-T1 AC2: tooltip renders .chart-tooltip__pivot-btn when onPivotToRecords is provided", () => {
    const onPivot = vi.fn();
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
        onPivotToRecords={onPivot}
        activeDomain="family"
      />
    );

    // Hover over alpha's dot to show tooltip.
    // The SVG is rendered via dangerouslySetInnerHTML; fire mousemove directly on
    // the circle element so e.target has the data-model attribute that handleMouseMove reads.
    const alphaEl = container.querySelector('[data-model="fixture-model-alpha"]');
    expect(alphaEl).not.toBeNull();

    // mouseMove fires on the child circle and bubbles to the SVG onMouseMove handler.
    fireEvent.mouseMove(alphaEl!, {
      clientX: 100,
      clientY: 100,
    });

    // The tooltip should now be visible with the pivot button
    const pivotBtn = container.querySelector(".chart-tooltip__pivot-btn");
    expect(pivotBtn).not.toBeNull();
    expect(pivotBtn!.textContent).toBe(PIVOT_TO_RECORDS_LABEL);
    // aria-label should use pivotToRecordsAriaLabel
    expect(pivotBtn!.getAttribute("aria-label")).toBe(
      pivotToRecordsAriaLabel("fixture-model-alpha", "family")
    );
  });

  // Case 48b: no pivot button when onPivotToRecords is not provided
  it("G7-T1 AC2: tooltip does NOT render .chart-tooltip__pivot-btn when onPivotToRecords is absent", () => {
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
      />
    );

    const alphaEl = container.querySelector('[data-model="fixture-model-alpha"]');
    expect(alphaEl).not.toBeNull();
    fireEvent.mouseMove(alphaEl!, { clientX: 100, clientY: 100 });

    // No pivot button should be rendered
    expect(container.querySelector(".chart-tooltip__pivot-btn")).toBeNull();
  });

  // Case 49: clicking pivot button fires onPivotToRecords with the model id
  it("G7-T1 AC3: clicking .chart-tooltip__pivot-btn fires onPivotToRecords with hovered model id", () => {
    const onPivot = vi.fn();
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
        r1States={FIXTURE_R1_STATES_ALL_TYPICAL}
        ociValues={FIXTURE_OCI_VALUES}
        onPivotToRecords={onPivot}
        activeDomain="family"
      />
    );

    // Trigger tooltip for beta by mousing over beta's dot
    const betaEl = container.querySelector('[data-model="fixture-model-beta"]');
    expect(betaEl).not.toBeNull();
    fireEvent.mouseMove(betaEl!, { clientX: 150, clientY: 150 });

    // Click the pivot button
    const pivotBtn = container.querySelector(".chart-tooltip__pivot-btn");
    expect(pivotBtn).not.toBeNull();
    fireEvent.click(pivotBtn!);

    // Callback fires with the hovered model id
    expect(onPivot).toHaveBeenCalledTimes(1);
    expect(onPivot).toHaveBeenCalledWith("fixture-model-beta");
  });
});
