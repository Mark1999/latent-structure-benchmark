/**
 * MDSPlot tests (T-CHART-TESTS-1)
 *
 * Reduced scope per Architect plan §3 finding: MDSPlot.tsx does not yet implement
 * DESIGN_SYSTEM.md §3.3.5 R1-b (dashed-stroke low-concentration) or R1-c
 * (hollow-triangle deterministic) treatments. This suite asserts what the current
 * component ACTUALLY SHIPS (R1-a ellipses for models with mdsUncertainty data;
 * bare circle for models whose mdsUncertainty[id] is null) and stubs the missing
 * R1-b and R1-c assertions as it.skip with a T-MDS-R1 follow-up reference.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * CLAUDE.md §6 rule 10 (R10): no point estimate without uncertainty on any viz.
 * CLAUDE.md §9 pitfall 8: no viz without uncertainty check.
 */

import { render } from "@testing-library/react";
import { MDSPlot } from "../components/MDSPlot";

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
      />
    );
    // fixture-model-alpha and fixture-model-gamma have uncertainty; fixture-model-beta does not
    const ellipses = container.querySelectorAll("ellipse");
    expect(ellipses.length).toBe(2);
  });

  it("renders a <circle> with data-model for the null-uncertainty model (current shipped behavior)", () => {
    /**
     * Per DESIGN_SYSTEM.md §3.3.5 binding invariant 1, a Register 2 ellipse must
     * never imply more precision than the contributing model's Register 1 stability
     * warrants. The current MDSPlot.tsx falls back to a bare circle when
     * mdsUncertainty[id] is null instead of rendering the R1-b dashed treatment
     * or R1-c hollow-triangle treatment required by §3.3.5. T-MDS-R1 lands the fix.
     * This test asserts only what currently ships; the it.skip siblings below assert
     * the §3.3.5-compliant behavior that T-MDS-R1 will deliver.
     */
    const { container } = render(
      <MDSPlot
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_WITH_NULL}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
        topTerms={FIXTURE_TOP_TERMS}
        centralityScores={FIXTURE_CENTRALITY}
      />
    );
    // The null-uncertainty model (fixture-model-beta) must still have a dot marker
    const betaCircle = container.querySelector('[data-model="fixture-model-beta"]');
    expect(betaCircle).not.toBeNull();
    expect(betaCircle!.tagName.toLowerCase()).toBe("circle");
  });
});

describe("MDSPlot: R1-b/R1-c invariants (skipped pending T-MDS-R1)", () => {
  /**
   * These tests assert the DESIGN_SYSTEM.md §3.3.5-compliant behavior that
   * T-MDS-R1 will deliver. They are skipped here because the current MDSPlot.tsx
   * does not yet implement R1-b dashed-stroke or R1-c hollow-triangle treatment.
   * When T-MDS-R1 lands (implements deterministicOutputs + ociScores props and the
   * corresponding SVG render branches), these tests must be activated (remove .skip)
   * in the same PR.
   *
   * Reference: Architect plan T-CHART-TESTS §3 (architectural finding),
   * DESIGN_SYSTEM.md §3.3.5 R1-b and R1-c invariants.
   */

  it.skip("TODO(T-MDS-R1): R1-b: low-concentration model renders dashed stroke, no ellipse", () => {
    // When ociScores[id] < OCI_LOW_CONCENTRATION_THRESHOLD and deterministicOutputs[id] === false,
    // the model point must render a dashed 2px stroke with fill at 60% opacity (§3.3.5 R1-b).
    // No <ellipse> must be present for this model.
    // Activate this test when MDSPlot.tsx gains the ociScores + deterministicOutputs props.
    expect(true).toBe(false); // placeholder: will fail if accidentally un-skipped without implementation
  });

  it.skip("TODO(T-MDS-R1): R1-c: deterministic model renders hollow-triangle marker, no ellipse", () => {
    // When deterministicOutputs[id] === true, the model point must render as a hollow
    // triangle (△) with a 3px solid stroke at 100% model color opacity (§3.3.5 R1-c).
    // No <ellipse> must be present for this model.
    // Activate this test when MDSPlot.tsx gains the deterministicOutputs prop.
    expect(true).toBe(false); // placeholder: will fail if accidentally un-skipped without implementation
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
