/**
 * Focus2FamilySimilarity F5-T1 degenerate bootstrap ellipse tests.
 *
 * F5-T1 (A5): equivalent fixture tests for the Focus2FamilySimilarity
 * ellipse-render path. Per DESIGN_SYSTEM.md §3.3.5 impl req 12 and
 * CDA SME T-MDS-R1 F2: degenerate semi_major <= 0 is the LIMIT case of
 * a high-stability R1-a sample. Minimum-radius ellipse floor rendered.
 * S4 aria-label on family-member inner circle.
 *
 * CLAUDE.md §6 rule 9: no real API calls. Fixture-based only.
 * CLAUDE.md §6 rule 10 (R10): no point estimate without uncertainty.
 */

import { render } from "@testing-library/react";
import { Focus2FamilySimilarity } from "../components/Focus2FamilySimilarity";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const FIXTURE_MODELS = [
  { model_id: "fixture-f2-alpha", provider: "anthropic", family: "claude", open_weights: false },
  { model_id: "fixture-f2-beta",  provider: "anthropic", family: "claude", open_weights: false },
  { model_id: "fixture-f2-gamma", provider: "openai",    family: "gpt",    open_weights: false },
];

const FIXTURE_COORDS: Record<string, [number, number]> = {
  "fixture-f2-alpha": [0.3,  0.2],
  "fixture-f2-beta":  [-0.2, 0.4],
  "fixture-f2-gamma": [0.1, -0.3],
};

// Non-degenerate uncertainty for all three models
const FIXTURE_UNCERTAINTY_FULL: Record<string, {
  semi_major: number; semi_minor: number; rotation_rad: number;
  center: [number, number]; n_bootstrap: number;
} | null> = {
  "fixture-f2-alpha": { semi_major: 0.08, semi_minor: 0.04, rotation_rad: 0.3, center: [0.3, 0.2], n_bootstrap: 200 },
  "fixture-f2-beta":  { semi_major: 0.06, semi_minor: 0.03, rotation_rad: 0.7, center: [-0.2, 0.4], n_bootstrap: 200 },
  "fixture-f2-gamma": { semi_major: 0.10, semi_minor: 0.05, rotation_rad: 1.1, center: [0.1, -0.3], n_bootstrap: 200 },
};

// Degenerate: alpha has semi_major === 0 (family member of "anthropic")
const FIXTURE_UNCERTAINTY_DEGENERATE_ZERO: Record<string, {
  semi_major: number; semi_minor: number; rotation_rad: number;
  center: [number, number]; n_bootstrap: number;
} | null> = {
  "fixture-f2-alpha": { semi_major: 0, semi_minor: 0, rotation_rad: 0, center: [0.3, 0.2], n_bootstrap: 200 },
  "fixture-f2-beta":  { semi_major: 0.06, semi_minor: 0.03, rotation_rad: 0.7, center: [-0.2, 0.4], n_bootstrap: 200 },
  "fixture-f2-gamma": { semi_major: 0.10, semi_minor: 0.05, rotation_rad: 1.1, center: [0.1, -0.3], n_bootstrap: 200 },
};

// Degenerate: alpha has semi_major === -0.001 (numerical-precision artifact)
const FIXTURE_UNCERTAINTY_DEGENERATE_NEG: Record<string, {
  semi_major: number; semi_minor: number; rotation_rad: number;
  center: [number, number]; n_bootstrap: number;
} | null> = {
  "fixture-f2-alpha": { semi_major: -0.001, semi_minor: -0.001, rotation_rad: 0, center: [0.3, 0.2], n_bootstrap: 200 },
  "fixture-f2-beta":  { semi_major: 0.06, semi_minor: 0.03, rotation_rad: 0.7, center: [-0.2, 0.4], n_bootstrap: 200 },
  "fixture-f2-gamma": { semi_major: 0.10, semi_minor: 0.05, rotation_rad: 1.1, center: [0.1, -0.3], n_bootstrap: 200 },
};

// Dummy similarity data (3x3, uniform)
const FIXTURE_SIMILARITY: number[][] = [
  [1, 0.8, 0.7],
  [0.8, 1, 0.75],
  [0.7, 0.75, 1],
];

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("Focus2FamilySimilarity: F5 degenerate bootstrap ellipse (converged-state treatment)", () => {
  /**
   * F5-T1 acceptance criteria A5 (Focus2FamilySimilarity fixture tests).
   *
   * A degenerate bootstrap envelope (semi_major <= 0) is the LIMIT case
   * of a high-stability R1-a sample per DESIGN_SYSTEM.md §3.3.5 impl req 12.
   * The component renders a minimum-radius ellipse floor (3px) and adds
   * data-degenerate-bootstrap="true" to the family-member inner circle with S4 aria-label.
   */

  it("F5 A5a: renders without crash when family-member has degenerate uncertainty (semi_major===0)", () => {
    const { container } = render(
      <Focus2FamilySimilarity
        models={FIXTURE_MODELS}
        similarityMatrix={FIXTURE_SIMILARITY}
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_DEGENERATE_ZERO}
        selectedProvider="anthropic"
      />
    );

    // Must render without crash
    expect(container.querySelector(".f2-similarity")).not.toBeNull();
  });

  it("F5 A5b: degenerate family-member circle has S4 aria-label and data-degenerate-bootstrap='true'", () => {
    /**
     * S4 (byte-identical to CDA SME S4):
     * "{displayName}, high positional stability across bootstrap resamples."
     * Disclosure threads through the family-member inner circle
     * per DESIGN_SYSTEM.md §3.3.5 impl req 12.
     */
    const { container } = render(
      <Focus2FamilySimilarity
        models={FIXTURE_MODELS}
        similarityMatrix={FIXTURE_SIMILARITY}
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_DEGENERATE_ZERO}
        selectedProvider="anthropic"
      />
    );

    // Degenerate family-member circle must have data-degenerate-bootstrap="true"
    const degCircles = container.querySelectorAll('circle[data-degenerate-bootstrap="true"]');
    expect(degCircles.length).toBeGreaterThanOrEqual(1);

    // The degenerate circle must carry the S4 aria-label
    degCircles.forEach((el) => {
      const label = el.getAttribute("aria-label") ?? "";
      expect(label).toContain("high positional stability across bootstrap resamples.");
    });
  });

  it("F5 A5b negative-value: semi_major===-0.001 (numerical-precision artifact) also gets degenerate treatment", () => {
    const { container } = render(
      <Focus2FamilySimilarity
        models={FIXTURE_MODELS}
        similarityMatrix={FIXTURE_SIMILARITY}
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_DEGENERATE_NEG}
        selectedProvider="anthropic"
      />
    );

    const degCircles = container.querySelectorAll('circle[data-degenerate-bootstrap="true"]');
    expect(degCircles.length).toBeGreaterThanOrEqual(1);
    degCircles.forEach((el) => {
      expect(el.getAttribute("aria-label")).toContain("high positional stability across bootstrap resamples.");
    });
  });

  it("F5 A5c: degenerate family-member gets minimum-radius ellipse (R10: visible artifact)", () => {
    /**
     * R10 contract: bare-point fall-through impossible.
     * Degenerate family-member gets a minimum-radius ellipse (rx=3, ry=3)
     * with data-degenerate-bootstrap="true".
     */
    const { container } = render(
      <Focus2FamilySimilarity
        models={FIXTURE_MODELS}
        similarityMatrix={FIXTURE_SIMILARITY}
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_DEGENERATE_ZERO}
        selectedProvider="anthropic"
      />
    );

    // Degenerate ellipse has the marker attribute
    const degEllipses = container.querySelectorAll('ellipse[data-degenerate-bootstrap="true"]');
    expect(degEllipses.length).toBeGreaterThanOrEqual(1);
    // Minimum radius: rx and ry are 3
    degEllipses.forEach((el) => {
      expect(el.getAttribute("rx")).toBe("3");
      expect(el.getAttribute("ry")).toBe("3");
    });
  });

  it("F5 A5d: non-degenerate family member does NOT get degenerate treatment (A3-equivalent gate)", () => {
    /**
     * A3 equivalent: the non-degenerate path must NOT activate the degenerate branch.
     * FIXTURE_UNCERTAINTY_FULL has all semi_major > 0: no degenerate markers expected.
     */
    const { container } = render(
      <Focus2FamilySimilarity
        models={FIXTURE_MODELS}
        similarityMatrix={FIXTURE_SIMILARITY}
        mdsCoordinates={FIXTURE_COORDS}
        mdsUncertainty={FIXTURE_UNCERTAINTY_FULL}
        selectedProvider="anthropic"
      />
    );

    // No degenerate circles or ellipses
    expect(container.querySelectorAll('[data-degenerate-bootstrap="true"]').length).toBe(0);
  });
});
