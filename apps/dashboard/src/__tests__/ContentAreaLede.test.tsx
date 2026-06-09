/**
 * ContentArea lede tests (Phase 9a T2)
 *
 * Verifies:
 * 1. For each of family/holidays/food: the Focus-3 rendered lede text matches
 *    the domain's published generated_lede verbatim (normalized).
 * 2. R10 disclosure regression guard: family + food rendered DOM contains the
 *    R1-b disclosure phrases "low output concentration" and
 *    "without a confidence ellipse".
 * 3. The inline-computed label "Consensus baseline (all tested models)" is GONE.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * ARCHITECTURE.md §4.2: lede logic lives in cdb_publish, not in components.
 */

import { render } from "@testing-library/react";
import { ContentArea } from "../components/ContentArea";
import type { DomainExtended } from "../data/types";

// ---------------------------------------------------------------------------
// Minimal fixture builder
// ---------------------------------------------------------------------------

function makeDomain(slug: string, lede: string): DomainExtended {
  return {
    domain_slug: slug,
    analysis_version: "test",
    models: [],
    free_lists: {},
    mds_coordinates: {},
    mds_uncertainty: {},
    similarity_matrix: [],
    similarity_ci: [],
    consensus_score: 0.8,
    consensus_ci: [0.6, 0.95],
    consensus_type: "STRONG_CONSENSUS",
    sutrop_csi: {},
    cultural_centrality_scores: {},
    within_model_results: [],
    groundings: [],
    generated_lede: lede,
    generated_at: "2026-06-09T00:00:00Z",
    romney_small_n_warning: false,
    display: {
      r1_states: {},
      top_terms: {},
      top_terms_metric: "sutrop_csi",
    },
  } as unknown as DomainExtended;
}

// Published generated_lede strings (sourced from actual published JSON files)
const FAMILY_LEDE =
  "Across 15 frontier models, family vocabulary is organized around a shared categorical structure (Smith's S = 0.81, 95% CI [0.64, 0.95]). " +
  "1 of these 15 models produced low output concentration on this domain -- their position on the map is shown without a confidence ellipse, signaling that the runs did not converge on a single sort.";

const HOLIDAYS_LEDE =
  "Across 14 frontier models, holidays vocabulary is organized around a single shared categorical structure (Smith's S = 0.88, 95% CI [0.77, 0.97]). " +
  "The map below shows where each model sits relative to that consensus -- and which models diverge from it.";

const FOOD_LEDE =
  "Across 8 frontier models, food vocabulary is organized around a shared categorical structure (Smith's S = 0.61, 95% CI [0.48, 0.79]). " +
  "1 of these 8 models produced low output concentration on this domain -- their position on the map is shown without a confidence ellipse, signaling that the runs did not converge on a single sort.";

// Shared minimal props for ContentArea (Focus-3, no tab-specific viz)
const BASE_PROPS = {
  loading: false,
  error: null,
  selectedModelIds: new Set<string>(),
  onRemoveModel: () => {},
  activeVizTab: "mds-plot" as const,
  onVizTabChange: () => {},
  activeFocus: "focus-3" as const,
  onFocusChange: () => {},
  selectedModelId: null,
  onSelectModel: () => {},
  activeDomain: "family",
};

// ---------------------------------------------------------------------------
// Helper: get lede paragraph text from rendered DOM
// ---------------------------------------------------------------------------

function getLedeText(): string {
  // The lede is a <p class="chart-lede"> with aria-live="polite"
  const lede = document.querySelector('p.chart-lede[aria-live="polite"]');
  return lede ? (lede.textContent ?? "") : "";
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ContentArea Focus-3 lede (Phase 9a T2)", () => {
  afterEach(() => {
    // Clear DOM between tests
    document.body.innerHTML = "";
  });

  it("renders family generated_lede verbatim", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeDomain("family", FAMILY_LEDE)}
        activeDomain="family"
      />
    );
    const text = getLedeText();
    // Normalized match (collapse whitespace)
    expect(text.replace(/\s+/g, " ").trim()).toBe(
      FAMILY_LEDE.replace(/\s+/g, " ").trim()
    );
  });

  it("renders holidays generated_lede verbatim", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeDomain("holidays", HOLIDAYS_LEDE)}
        activeDomain="holidays"
      />
    );
    const text = getLedeText();
    expect(text.replace(/\s+/g, " ").trim()).toBe(
      HOLIDAYS_LEDE.replace(/\s+/g, " ").trim()
    );
  });

  it("renders food generated_lede verbatim", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeDomain("food", FOOD_LEDE)}
        activeDomain="food"
      />
    );
    const text = getLedeText();
    expect(text.replace(/\s+/g, " ").trim()).toBe(
      FOOD_LEDE.replace(/\s+/g, " ").trim()
    );
  });

  // R10 disclosure regression guard: family domain
  it("family lede DOM contains R1-b disclosure phrases (R10 regression guard)", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeDomain("family", FAMILY_LEDE)}
        activeDomain="family"
      />
    );
    const lede = document.querySelector('p.chart-lede[aria-live="polite"]');
    expect(lede).not.toBeNull();
    expect(lede!.textContent).toContain("low output concentration");
    expect(lede!.textContent).toContain("without a confidence ellipse");
  });

  // R10 disclosure regression guard: food domain
  it("food lede DOM contains R1-b disclosure phrases (R10 regression guard)", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeDomain("food", FOOD_LEDE)}
        activeDomain="food"
      />
    );
    const lede = document.querySelector('p.chart-lede[aria-live="polite"]');
    expect(lede).not.toBeNull();
    expect(lede!.textContent).toContain("low output concentration");
    expect(lede!.textContent).toContain("without a confidence ellipse");
  });

  // Inline-computed strings must be absent from the DOM
  it("does NOT contain 'Consensus baseline (all tested models)' in rendered DOM", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeDomain("family", FAMILY_LEDE)}
        activeDomain="family"
      />
    );
    expect(document.body.textContent).not.toContain(
      "Consensus baseline (all tested models)"
    );
  });

  it("does NOT contain 'Across 0 models' or selection-count strings in rendered DOM", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        // empty selection, 0 models selected
        selectedModelIds={new Set<string>()}
        domain={makeDomain("family", FAMILY_LEDE)}
        activeDomain="family"
      />
    );
    // The old inline lede would produce "Across 0 model(s)" — that string must not appear
    expect(document.body.textContent).not.toMatch(/Across \d+ model\(s\)/);
  });
});
