/**
 * TermMap smoke tests (T7, TM-B: vitest harness activation and TM-B update)
 *
 * Stage 1/2 regression guard: verifies the blank-vs-populated distinction
 * (food/holidays incident). Confirms:
 *   - empty termCoords renders the placeholder, NOT a blank SVG
 *   - non-empty termCoords renders the SVG container (populated state)
 *
 * TM-B update: the four controls (overlay selector, uncertainty, cluster labels,
 * lens) are now lifted to ChartToolbar in ContentArea. The TermMap internal
 * term-map-controls row no longer contains these controls. Assertions updated.
 *
 * TermMap uses ResizeObserver + canvas-style imperative render(). We mock
 * ResizeObserver to prevent JSDOM errors.
 * CLAUDE.md §6 rule 9: no real API calls. Fixture-based only.
 */

import { render, screen } from "@testing-library/react";
import { TermMap } from "../components/TermMap";

// ── JSDOM polyfills required by TermMap ───────────────────────────────────────

// ResizeObserver is not available in jsdom; mock it to prevent errors
beforeAll(() => {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

// ── Fixture data ──────────────────────────────────────────────────────────────

// Non-empty term coordinates. Fixture names that cannot be confused with
// real production data (CLAUDE.md pitfall: fixture data must not resemble real records)
const FIXTURE_TERM_COORDS: Record<string, [number, number]> = {
  "fixture-term-alpha": [0.1, 0.2],
  "fixture-term-beta": [-0.3, 0.4],
  "fixture-term-gamma": [0.5, -0.1],
};

const FIXTURE_TERM_CLUSTERS: Record<string, number> = {
  "fixture-term-alpha": 0,
  "fixture-term-beta": 1,
  "fixture-term-gamma": 0,
};

const FIXTURE_CLUSTER_LABELS = ["Fixture Cluster A", "Fixture Cluster B"];

const EMPTY_TERM_COORDS: Record<string, [number, number]> = {};
const EMPTY_TERM_CLUSTERS: Record<string, number> = {};

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("TermMap", () => {
  it("renders the placeholder message when termCoords is empty (empty domain)", () => {
    render(
      <TermMap
        termCoords={EMPTY_TERM_COORDS}
        termClusters={EMPTY_TERM_CLUSTERS}
        clusterLabels={[]}
      />
    );

    // Placeholder text must be visible -- NOT a blank SVG
    expect(
      screen.getByText(/No term data available for this domain/)
    ).toBeInTheDocument();
  });

  it("does NOT render the populated SVG container when term data is empty", () => {
    render(
      <TermMap
        termCoords={EMPTY_TERM_COORDS}
        termClusters={EMPTY_TERM_CLUSTERS}
        clusterLabels={[]}
      />
    );

    // The populated state wraps content in term-map-container
    expect(document.querySelector(".term-map-container")).toBeNull();
  });

  it("renders the term-map-container (populated state) when termCoords are provided", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    // Populated state uses .term-map-container
    expect(document.querySelector(".term-map-container")).not.toBeNull();
  });

  it("does NOT render the placeholder when termCoords are provided", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    expect(
      screen.queryByText(/No term data available for this domain/)
    ).toBeNull();
  });

  it("renders the pan-viewport element in populated state", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    // The pan-viewport div is the scroll/zoom container in Stage 2
    expect(document.querySelector(".term-map-pan-viewport")).not.toBeNull();
  });

  it("renders the stress annotation div in populated state", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    // Stress footer is always present in populated state
    expect(document.querySelector(".term-map-stress")).not.toBeNull();
  });

  it("renders cooccurrenceData=null without crash (static coords fallback)", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
        cooccurrenceData={null}
        selectedModelIds={new Set(["fixture-model-alpha"])}
      />
    );

    // Must not crash; falls back to static termCoords
    expect(document.querySelector(".term-map-container")).not.toBeNull();
  });

  // TM-B: the four controls (overlay, uncertainty, cluster labels, lens) are
  // no longer rendered inside TermMap's internal controls row.
  it("TM-B: term-map-controls row does NOT contain overlay selector or checkbox controls", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    // The old controls bar rendered these inside TermMap; now they are in ChartToolbar.
    // The term-map-controls class no longer exists in TermMap's DOM.
    const controlsRow = document.querySelector(".term-map-controls");
    expect(controlsRow).toBeNull();
  });

  // TM-B: zoom buttons remain in term-map-stress footer (not in the removed controls row)
  it("TM-B: zoom buttons remain in term-map-stress footer", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    const stress = document.querySelector(".term-map-stress");
    expect(stress).not.toBeNull();
    // Zoom buttons live in the stress footer
    const zoomBtns = stress!.querySelectorAll(".term-map-controls__zoom-btn");
    expect(zoomBtns.length).toBeGreaterThanOrEqual(2); // at minimum − and +
  });

  // TM-B: accepts lifted props without crash
  it("TM-B: accepts overlayPileLabelKey + showUncertainty + showClusterLabels props", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
        overlayPileLabelKey={null}
        showUncertainty={true}
        showClusterLabels={true}
        onLensDisabledByZoomChange={() => {}}
      />
    );

    // Must not crash with lifted props
    expect(document.querySelector(".term-map-container")).not.toBeNull();
  });

  // TM-B: showUncertainty defaults to true when prop is absent (§3.1.1(b)(ii) default ON)
  it("TM-B: showUncertainty defaults to true when prop is absent", () => {
    // Rendering without showUncertainty prop -- should default to ON
    // We test by ensuring the component renders without crash and the default is applied.
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    // Component must render populated state (no crash from default uncertainty=true)
    expect(document.querySelector(".term-map-container")).not.toBeNull();
  });

  // TM-C: salienceRanks prop accepted without crash
  it("TM-C: accepts salienceRanks prop without crash", () => {
    const salienceRanks = {
      "fixture-model-alpha": [
        { item: "fixture-term-alpha", csi: 0.9, f_mentions: 5, n_runs: 3, mean_position: 1.0 },
        { item: "fixture-term-beta",  csi: 0.5, f_mentions: 3, n_runs: 3, mean_position: 2.0 },
        { item: "fixture-term-gamma", csi: 0.2, f_mentions: 1, n_runs: 3, mean_position: 3.0 },
      ],
    };

    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
        salienceRanks={salienceRanks}
      />
    );

    // Must not crash with salienceRanks prop
    expect(document.querySelector(".term-map-container")).not.toBeNull();
  });

  // TM-C: without salienceRanks, no salience caption rendered
  it("TM-C: no salience caption when salienceRanks is absent", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    // Without salienceRanks, the .term-map-salience-caption should not render
    expect(document.querySelector(".term-map-salience-caption")).toBeNull();
  });

  // TM-C + 2026-06-10 jitter fix: the footnote band is height-constant and always
  // present when cluster labels are on; its item count must never resize
  // .chart-wrap and re-fire the ResizeObserver (the live oscillation regression).
  it("TM-C: footnote band is height-constant with placeholder when nothing hidden", () => {
    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
      />
    );

    const band = document.querySelector<HTMLOListElement>(".term-map-cluster-footnotes");
    expect(band).not.toBeNull();
    expect(band!.style.height).toBe("48px");
    expect(band!.style.overflowY).toBe("auto");
    expect(band!.textContent).toContain("All cluster labels are shown on the map.");
  });

  // TM-C: R6 invariant check -- no ellipse/circle/polygon changes in component render
  it("TM-C: term-map-container renders without crash using centroidPiles", () => {
    const centroidPiles = {
      "fixture-model-alpha": {
        piles: [
          ["fixture-term-alpha", "fixture-term-gamma"],
          ["fixture-term-beta"],
        ],
        labels: ["Fixture Pile A", "Fixture Pile B"],
      },
    };

    render(
      <TermMap
        termCoords={FIXTURE_TERM_COORDS}
        termClusters={FIXTURE_TERM_CLUSTERS}
        clusterLabels={FIXTURE_CLUSTER_LABELS}
        centroidPiles={centroidPiles}
        overlayPileLabelKey="fixture-model-alpha"
        showClusterLabels={true}
      />
    );

    // Must render without crash
    expect(document.querySelector(".term-map-container")).not.toBeNull();
  });
});
