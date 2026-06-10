/**
 * PileStructure tests (T-CHART-TESTS-4)
 *
 * Verifies:
 *   - Renders correctly with canonical, empty, per-model-absent, and malformed fixtures.
 *   - Per-model aria-label contract: .pile-column aria-label matches "Pile structure for {name}".
 *   - Term pill aria-label contract: "placed here in {pct}% of runs for {name}".
 *   - Term-stability tier classification: stability values in three bands produce
 *     the correct CSS class suffixes (high/medium/low).
 *   - Forbidden vocabulary absent in rendered DOM text.
 *   - Determinism: outerHTML stable across two renders of canonical fixture.
 *
 * CDA SME N4 (BINDING carry-through): the term-stability tier it() block labels
 * use "pile-placement stability" rather than "agreement" to avoid register-boundary
 * errors. The % in the pill is a within-model placement consistency statistic --
 * NOT a between-model consensus measure.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * CLAUDE.md §9 pitfall 8: no point-estimate chart ships without uncertainty check.
 */

import { render } from "@testing-library/react";
import { PileStructure } from "../components/PileStructure";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const FIXTURE_MODELS = [
  { model_id: "fixture-model-alpha", provider: "anthropic", family: "claude",
    origin: "us" as const, open_weights: false, collection_method: "api",
    quantization: null, release_date: "2025-01-01", version_label: "v1",
    source_notes: "" },
  { model_id: "fixture-model-beta",  provider: "openai",    family: "gpt",
    origin: "us" as const, open_weights: false, collection_method: "api",
    quantization: null, release_date: "2025-01-01", version_label: "v1",
    source_notes: "" },
  { model_id: "fixture-model-gamma", provider: "google",    family: "gemini",
    origin: "us" as const, open_weights: false, collection_method: "api",
    quantization: null, release_date: "2025-01-01", version_label: "v1",
    source_notes: "" },
];

// Stability values spanning all three tiers
// high: >= 0.8, medium: 0.6..0.79, low: < 0.6
const FIXTURE_CENTROID_PILES = {
  "fixture-model-alpha": {
    piles: [
      ["fixture-term-a", "fixture-term-b", "fixture-term-c"],
      ["fixture-term-d", "fixture-term-e"],
      ["fixture-term-f"],
    ],
    labels: ["Fixture Pile A", "Fixture Pile B", "Fixture Pile C"],
    term_stability: {
      "fixture-term-a": 0.90,  // high
      "fixture-term-b": 0.82,  // high
      "fixture-term-c": 0.70,  // medium
      "fixture-term-d": 0.65,  // medium
      "fixture-term-e": 0.50,  // low
      "fixture-term-f": 0.40,  // low
    },
  },
  "fixture-model-beta": {
    piles: [
      ["fixture-term-x", "fixture-term-y"],
      ["fixture-term-z"],
    ],
    labels: ["Beta Pile A", "Beta Pile B"],
    term_stability: {
      "fixture-term-x": 0.88,  // high
      "fixture-term-y": 0.72,  // medium
      "fixture-term-z": 0.55,  // low
    },
  },
  "fixture-model-gamma": {
    piles: [
      ["fixture-term-p", "fixture-term-q"],
    ],
    labels: ["Gamma Pile A"],
    term_stability: {
      "fixture-term-p": 0.95,  // high
      "fixture-term-q": 0.60,  // medium (boundary value: exactly 0.60)
    },
  },
};

// Fixture with missing term_stability (should default to 1.0 per component line 149)
const FIXTURE_NO_STABILITY = {
  "fixture-model-alpha": {
    piles: [["fixture-term-nostab-a", "fixture-term-nostab-b"]],
    labels: ["No Stability Pile"],
    // term_stability absent
  },
};

const ALL_SELECTED = new Set(FIXTURE_MODELS.map((m) => m.model_id));
const ALPHA_ONLY = new Set(["fixture-model-alpha"]);

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("PileStructure — canonical fixture (3 models, 3+ piles each)", () => {
  it("renders without crash with full canonical data", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    expect(container.querySelector(".pile-columns")).not.toBeNull();
  });

  it("renders one .pile-column per selected model", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    const columns = container.querySelectorAll(".pile-column");
    expect(columns.length).toBe(3);
  });
});

describe("PileStructure — empty fixture (no selected models)", () => {
  it("renders .pile-empty with 'No models selected.' when selectedModelIds is empty", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS}
        selectedModelIds={new Set()}
      />
    );
    expect(container.querySelector(".pile-empty")).not.toBeNull();
    expect(container.textContent).toContain("No models selected.");
  });

  it("does not render .pile-columns when selectedModelIds is empty", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS}
        selectedModelIds={new Set()}
      />
    );
    expect(container.querySelector(".pile-columns")).toBeNull();
  });
});

describe("PileStructure — per-model absent (centroidPiles[id] missing for one model)", () => {
  it("renders .pile-empty-col 'No pile data' for the model whose pileData is absent", () => {
    const partialPiles = {
      "fixture-model-alpha": FIXTURE_CENTROID_PILES["fixture-model-alpha"],
      // fixture-model-beta intentionally absent
      "fixture-model-gamma": FIXTURE_CENTROID_PILES["fixture-model-gamma"],
    };

    const { container } = render(
      <PileStructure
        centroidPiles={partialPiles}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    const emptyCol = container.querySelector(".pile-empty-col");
    expect(emptyCol).not.toBeNull();
    expect(emptyCol!.textContent).toContain("No pile data");
  });
});

describe("PileStructure — malformed fixture (entry without term_stability)", () => {
  it("renders without crash when term_stability is absent (defaults to 1.0)", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_NO_STABILITY}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    expect(container.querySelector(".pile-column")).not.toBeNull();
    // Terms must render even without term_stability
    expect(container.querySelector(".pile-comparison__pill")).not.toBeNull();
  });

  it("applies --stability-high class when term_stability is absent (defaults to 1.0)", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_NO_STABILITY}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    // Default stability is 1.0 which is >= 0.8 -> high tier
    const pills = container.querySelectorAll(".pile-comparison__pill--stability-high");
    expect(pills.length).toBeGreaterThan(0);
  });
});

describe("PileStructure — pile-column aria-label contract (CDA SME N4)", () => {
  it("each .pile-column carries aria-label='Pile structure for {displayName}'", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    const columns = container.querySelectorAll(".pile-column");
    expect(columns.length).toBe(3);
    for (const col of Array.from(columns)) {
      const label = col.getAttribute("aria-label") ?? "";
      expect(label).toMatch(/^Pile structure for /);
    }
  });

  it("renders the expected number of .pile-group nodes per model", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    // fixture-model-alpha has 3 piles
    const groups = container.querySelectorAll(".pile-group");
    expect(groups.length).toBe(3);
  });
});

describe("PileStructure — term pill aria-label contract (CDA SME N4)", () => {
  /**
   * CDA SME N4 (BINDING): the % in the pill is a within-model placement
   * consistency statistic (pile-placement stability within this model's runs),
   * NOT a between-model consensus measure.
   * aria-label must be: "{term}: placed here in {pct}% of runs for {displayName}"
   */

  it("each term pill aria-label contains 'placed here in' and '% of runs for'", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    const pills = container.querySelectorAll(".pile-comparison__pill[aria-label]");
    expect(pills.length).toBeGreaterThan(0);
    for (const pill of Array.from(pills)) {
      const label = pill.getAttribute("aria-label") ?? "";
      if (label.includes("absent")) continue; // skip hover-placeholder pills
      expect(label).toMatch(/placed here in \d+% of runs for /);
    }
  });
});

describe("PileStructure — term-stability tier classification (pile-placement stability)", () => {
  /**
   * CDA SME N4 (BINDING) per T-CHART-TESTS plan:
   * describe label must use "pile-placement stability" (not "agreement").
   *
   * Stability thresholds (component lines 152-157):
   *   stability >= 0.8  -> pile-comparison__pill--stability-high
   *   0.6 <= stability < 0.8 -> pile-comparison__pill--stability-medium
   *   stability < 0.6   -> pile-comparison__pill--stability-low
   */

  it("pile-placement stability >= 0.8 produces --stability-high class", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    // fixture-term-a (stability 0.90) and fixture-term-b (0.82) should be high
    const highPills = container.querySelectorAll(".pile-comparison__pill--stability-high");
    expect(highPills.length).toBeGreaterThanOrEqual(2);
  });

  it("pile-placement stability in [0.6, 0.8) produces --stability-medium class", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    // fixture-term-c (0.70) and fixture-term-d (0.65) should be medium
    const mediumPills = container.querySelectorAll(".pile-comparison__pill--stability-medium");
    expect(mediumPills.length).toBeGreaterThanOrEqual(2);
  });

  it("pile-placement stability < 0.6 produces --stability-low class", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    // fixture-term-e (0.50) and fixture-term-f (0.40) should be low
    const lowPills = container.querySelectorAll(".pile-comparison__pill--stability-low");
    expect(lowPills.length).toBeGreaterThanOrEqual(2);
  });

  it("pile-placement stability exactly at 0.6 boundary produces --stability-medium (strict < at low, >= at medium)", () => {
    // fixture-model-gamma has fixture-term-q at stability 0.60
    // stability < 0.6 -> low (fails: 0.60 is NOT < 0.6)
    // stability < 0.8 -> medium (passes) -> renders medium
    const gammaOnly = new Set(["fixture-model-gamma"]);
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS.slice(2, 3)}
        selectedModelIds={gammaOnly}
      />
    );
    // Scope to .pile-columns only; the legend row always renders all three classes
    // regardless of data content (aria-hidden="true"), so we exclude it from assertions.
    const pilesContainer = container.querySelector(".pile-columns");
    expect(pilesContainer).not.toBeNull();

    // fixture-term-q at 0.60 -> medium; fixture-term-p at 0.95 -> high
    const mediumPills = pilesContainer!.querySelectorAll(".pile-comparison__pill--stability-medium");
    const highPills   = pilesContainer!.querySelectorAll(".pile-comparison__pill--stability-high");
    expect(mediumPills.length).toBeGreaterThanOrEqual(1);
    expect(highPills.length).toBeGreaterThanOrEqual(1);
    // No low-stability pill for these two terms (within the data area only)
    const lowPills = pilesContainer!.querySelectorAll(".pile-comparison__pill--stability-low");
    expect(lowPills.length).toBe(0);
  });
});

describe("PileStructure — forbidden vocabulary guard", () => {
  /**
   * ARCHITECTURE.md §1.5.4 + CLAUDE.md §7 forbidden vocabulary.
   * The % displayed in pills is a within-model placement-consistency statistic;
   * the rendered DOM text must not use model-cognition vocabulary.
   */
  const FORBIDDEN = [
    /\bworldview\b/i,
    /\bbelieves\b/i,
    /\bthinks\b/i,
    /\bunderstands\b/i,
  ];

  it("rendered container text contains no forbidden vocabulary", () => {
    const { container } = render(
      <PileStructure
        centroidPiles={FIXTURE_CENTROID_PILES}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    const text = container.textContent ?? "";
    for (const pattern of FORBIDDEN) {
      expect(text).not.toMatch(pattern);
    }
  });
});

describe("PileStructure — determinism", () => {
  it("is deterministic: same outerHTML across two renders of canonical fixture (no hover state, no time-dependent content)", () => {
    function renderAndSerialize() {
      const { container } = render(
        <PileStructure
          centroidPiles={FIXTURE_CENTROID_PILES}
          models={FIXTURE_MODELS}
          selectedModelIds={ALL_SELECTED}
        />
      );
      return container.innerHTML;
    }

    const first  = renderAndSerialize();
    const second = renderAndSerialize();
    expect(first).toBe(second);
  });
});
