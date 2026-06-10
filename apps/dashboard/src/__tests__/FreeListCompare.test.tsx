/**
 * FreeListCompare tests (T-CHART-TESTS-2)
 *
 * Verifies:
 *   - Renders correctly with canonical, empty, per-model-empty, and malformed fixtures.
 *   - CSI value rendering: bar-wrap aria-label matches fixture value (Sutrop CSI salience).
 *   - Top-20 cap: a fixture with 25 entries renders exactly 20 .freelist-item nodes.
 *   - Forbidden vocabulary absent in rendered DOM text.
 *   - Determinism: outerHTML stable across two renders of canonical fixture.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * CLAUDE.md §9 pitfall 8: no point-estimate chart ships without uncertainty check.
 */

import { render } from "@testing-library/react";
import { FreeListCompare } from "../components/FreeListCompare";
import type { SutropCsiEntry } from "../components/FreeListCompare";

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

// Canonical: 3 models, 5+ entries each
const FIXTURE_CSI: Record<string, SutropCsiEntry[]> = {
  "fixture-model-alpha": [
    { item: "fixture-term-1", csi: 0.85, f_mentions: 8, n_runs: 10, mean_position: 1.2 },
    { item: "fixture-term-2", csi: 0.70, f_mentions: 7, n_runs: 10, mean_position: 2.1 },
    { item: "fixture-term-3", csi: 0.60, f_mentions: 6, n_runs: 10, mean_position: 2.5 },
    { item: "fixture-term-4", csi: 0.45, f_mentions: 5, n_runs: 10, mean_position: 3.3 },
    { item: "fixture-term-5", csi: 0.30, f_mentions: 3, n_runs: 10, mean_position: 4.0 },
  ],
  "fixture-model-beta": [
    { item: "fixture-term-a", csi: 0.90, f_mentions: 9, n_runs: 10, mean_position: 1.0 },
    { item: "fixture-term-b", csi: 0.75, f_mentions: 8, n_runs: 10, mean_position: 1.5 },
    { item: "fixture-term-c", csi: 0.55, f_mentions: 5, n_runs: 10, mean_position: 2.8 },
    { item: "fixture-term-d", csi: 0.40, f_mentions: 4, n_runs: 10, mean_position: 3.5 },
    { item: "fixture-term-e", csi: 0.20, f_mentions: 2, n_runs: 10, mean_position: 5.0 },
  ],
  "fixture-model-gamma": [
    { item: "fixture-term-x", csi: 0.78, f_mentions: 7, n_runs: 10, mean_position: 1.1 },
    { item: "fixture-term-y", csi: 0.62, f_mentions: 6, n_runs: 10, mean_position: 2.0 },
    { item: "fixture-term-z", csi: 0.48, f_mentions: 5, n_runs: 10, mean_position: 3.0 },
    { item: "fixture-term-w", csi: 0.35, f_mentions: 3, n_runs: 10, mean_position: 4.2 },
    { item: "fixture-term-v", csi: 0.22, f_mentions: 2, n_runs: 10, mean_position: 5.5 },
  ],
};

// 25-entry fixture to verify the top-20 cap
function make25Entries(prefix: string): SutropCsiEntry[] {
  return Array.from({ length: 25 }, (_, i) => ({
    item: `${prefix}-term-${i + 1}`,
    csi: Math.max(0.01, 1.0 - i * 0.04),
    f_mentions: 10 - Math.floor(i / 5),
    n_runs: 10,
    mean_position: i + 1.0,
  }));
}

const FIXTURE_CSI_25: Record<string, SutropCsiEntry[]> = {
  "fixture-model-alpha": make25Entries("fixture"),
};

// Entry without mean_position (optional field absent)
const FIXTURE_CSI_NO_MEAN_POSITION: Record<string, SutropCsiEntry[]> = {
  "fixture-model-alpha": [
    { item: "fixture-no-pos-term", csi: 0.50, f_mentions: 5, n_runs: 10 },
  ],
};

const ALL_SELECTED = new Set(FIXTURE_MODELS.map((m) => m.model_id));
const ALPHA_ONLY = new Set(["fixture-model-alpha"]);

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("FreeListCompare: canonical fixture (3 models, 5 entries each)", () => {
  it("renders without crash with full canonical data", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    expect(container.querySelector(".freelist-columns")).not.toBeNull();
  });

  it("renders one .freelist-column per selected model", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    const columns = container.querySelectorAll(".freelist-column");
    expect(columns.length).toBe(3);
  });
});

describe("FreeListCompare: empty fixture (no selected models)", () => {
  it("renders the .freelist-empty element when selectedModelIds is empty", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI}
        models={FIXTURE_MODELS}
        selectedModelIds={new Set()}
      />
    );
    expect(container.querySelector(".freelist-empty")).not.toBeNull();
    expect(container.textContent).toContain("No models selected.");
  });

  it("does not render .freelist-columns when selectedModelIds is empty", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI}
        models={FIXTURE_MODELS}
        selectedModelIds={new Set()}
      />
    );
    expect(container.querySelector(".freelist-columns")).toBeNull();
  });
});

describe("FreeListCompare: per-model empty (sutropCsi[id] = [])", () => {
  it("renders .freelist-empty-col with 'No data' when a model has empty CSI array", () => {
    const emptyCsi = {
      ...FIXTURE_CSI,
      "fixture-model-beta": [],
    };

    const { container } = render(
      <FreeListCompare
        sutropCsi={emptyCsi}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );
    const emptyCol = container.querySelector(".freelist-empty-col");
    expect(emptyCol).not.toBeNull();
    expect(emptyCol!.textContent).toContain("No data");
  });
});

describe("FreeListCompare: malformed fixture (entry without mean_position)", () => {
  it("renders without crash when an entry lacks the optional mean_position field", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI_NO_MEAN_POSITION}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    expect(container.querySelector(".freelist-column")).not.toBeNull();
    expect(container.querySelector(".freelist-item")).not.toBeNull();
  });
});

describe("FreeListCompare: CSI bar-wrap aria-label contract", () => {
  it("each .freelist-item__bar-wrap carries aria-label='CSI {value.toFixed(2)}'", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    const barWraps = container.querySelectorAll(".freelist-item__bar-wrap");
    expect(barWraps.length).toBeGreaterThan(0);

    // Each bar-wrap aria-label must match "CSI X.XX" for the corresponding fixture entry.
    const alphaEntries = [...FIXTURE_CSI["fixture-model-alpha"]]
      .sort((a, b) => b.csi - a.csi);

    for (let i = 0; i < barWraps.length; i++) {
      const label = barWraps[i].getAttribute("aria-label") ?? "";
      const expected = `CSI ${alphaEntries[i].csi.toFixed(2)}`;
      expect(label).toBe(expected);
    }
  });
});

describe("FreeListCompare: top-20 cap", () => {
  it("renders exactly 20 .freelist-item nodes when fixture has 25 entries", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI_25}
        models={FIXTURE_MODELS.slice(0, 1)}
        selectedModelIds={ALPHA_ONLY}
      />
    );
    const items = container.querySelectorAll(".freelist-item");
    expect(items.length).toBe(20);
  });
});

describe("FreeListCompare: forbidden vocabulary guard", () => {
  /**
   * ARCHITECTURE.md §1.5.4 + CLAUDE.md §7 forbidden vocabulary.
   * Rendered DOM text must not contain model-cognition vocabulary.
   * CSI is the Sutrop CSI (Cultural Salience Index) -- a salience measure,
   * not a cognitive attribution.
   */
  const FORBIDDEN = [
    /\bworldview\b/i,
    /\bbelieves\b/i,
    /\bthinks\b/i,
    /\bunderstands\b/i,
  ];

  it("rendered container text contains no forbidden vocabulary", () => {
    const { container } = render(
      <FreeListCompare
        sutropCsi={FIXTURE_CSI}
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

describe("FreeListCompare: determinism", () => {
  it("is deterministic: same outerHTML across two renders of canonical fixture", () => {
    function renderAndSerialize() {
      const { container } = render(
        <FreeListCompare
          sutropCsi={FIXTURE_CSI}
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
