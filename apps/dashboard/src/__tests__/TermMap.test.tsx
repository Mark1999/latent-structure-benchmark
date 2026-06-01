/**
 * TermMap smoke tests (T7 — vitest harness activation)
 *
 * Stage 1/2 regression guard: verifies the blank-vs-populated distinction
 * (food/holidays incident). Confirms:
 *   - empty termCoords renders the placeholder, NOT a blank SVG
 *   - non-empty termCoords renders the SVG container (populated state)
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

// Non-empty term coordinates — fixture names that cannot be confused with
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

    // Placeholder text must be visible — NOT a blank SVG
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
});
