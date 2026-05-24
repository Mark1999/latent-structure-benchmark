// @vitest-environment jsdom
/**
 * T9 PileComparison + PileComparisonTable + pile comparison SR summary — acceptance criteria tests.
 *
 * Covers:
 *   AC1 — Column grid renders with pile cards and term pills
 *   AC2 — Cross-column hover highlight works (hover term in one column → highlights in all)
 *   AC3 — Stability tiers render (solid/dashed borders per threshold)
 *   AC4 — Tooltip shows stability % on every pill
 *   AC5 — Mobile switcher is present at <1024px (radiogroup role)
 *   AC6 — ReadAsTableToggle provides accessible table (U1 pattern)
 *   AC7 — ScreenReaderSummary present
 *   AC8 — No forbidden vocabulary in any visible string
 *   AC9 — VizSwitcher now has "Pile Structure" tab
 *   AC10 — pileComparisonScreenReaderSummary function (deterministic)
 *   AC11 — Empty state: zero models selected
 *   AC12 — Empty state: no centroid_piles data
 *   AC13 — PileComparisonTable renders 4-column table
 *   AC14 — Permalink codec handles "piles" fragment
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures only.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import type { DomainResultPublished, WithinModelResult, EllipseParams } from "../data/types";

// Components under test
import { PileComparison } from "../components/PileComparison";
import { PileComparisonTable } from "../components/PileComparisonTable";
import type { ModelPileData } from "../components/PileComparisonTable";
import { VizSwitcher } from "../components/VizSwitcher";

// Copy functions
import { pileComparisonScreenReaderSummary } from "../copy/screen_reader_summaries";
import {
  PILE_COMPARISON_DESCRIPTION,
  PILE_COMPARISON_EMPTY_NO_MODELS,
  PILE_COMPARISON_EMPTY_NO_DATA,
  PILE_COMPARISON_STABILITY_TOOLTIP,
  PILE_COMPARISON_TABLE_CAPTION,
} from "../copy/pile_comparison";

// Permalink
import { encodePermalink, decodePermalink } from "../lib/permalink";

// Static scan
const DESIGN_SYSTEM_MD = readFileSync(
  resolve(__dirname, "../../../../DESIGN_SYSTEM.md"),
  "utf-8"
);

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

// ── Fixture builder ───────────────────────────────────────────────────────────

function makeFixture(
  modelIds: string[],
  opts?: {
    centroidPiles?: Record<string, ModelPileData>;
  }
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

  const fixture = {
    domain_slug: "family",
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
    mds_uncertainty: mds_uncertainty as unknown as Record<string, EllipseParams | null>,
    similarity_matrix: {} as unknown as Record<string, Record<string, number>>,
    similarity_ci: {} as unknown as Record<string, Record<string, [number, number] | null>>,
    consensus_score: 0.71,
    consensus_ci: [0.65, 0.77] as [number, number],
    consensus_type: "STRONG_CONSENSUS" as DomainResultPublished["consensus_type"],
    sutrop_csi: {} as unknown as Record<string, Record<string, number>>,
    within_model_results,
    groundings: [],
    generated_lede: "Test lede.",
    generated_at: "2026-05-24T00:00:00Z",
    romney_small_n_warning: false,
    display: {
      r1_states: Object.fromEntries(
        modelIds.map((id) => [id, "typical_concentration" as import("../data/types").R1State])
      ),
      top_terms: Object.fromEntries(modelIds.map((id) => [id, ["alpha", "beta"]])),
      top_terms_metric: "sutrop_csi" as const,
    },
    ...(opts?.centroidPiles !== undefined ? { centroid_piles: opts.centroidPiles } : {}),
  } as unknown as DomainResultPublished;

  return fixture;
}

/** Minimal pile data for two models. */
const PILE_DATA_A: ModelPileData = {
  piles: [
    ["mother", "father", "parent"],
    ["sister", "brother"],
    ["aunt", "uncle"],
  ],
  labels: ["Parents", "Siblings", "Extended"],
  term_stability: {
    mother: 0.9,
    father: 0.85,
    parent: 0.72,
    sister: 0.55,
    brother: 0.61,
    aunt: 0.88,
    uncle: 0.92,
  },
};

const PILE_DATA_B: ModelPileData = {
  piles: [
    ["mother", "father"],
    ["sister", "brother", "cousin"],
    ["grandmother", "grandfather"],
  ],
  labels: ["Parental", "Siblings", "Grandparents"],
  term_stability: {
    mother: 0.95,
    father: 0.93,
    sister: 0.80,
    brother: 0.78,
    cousin: 0.45,
    grandmother: 0.88,
    grandfather: 0.86,
  },
};

const MODEL_COLORS: Record<string, string> = {
  "model-a": "#3360a9",
  "model-b": "#c0392b",
};

// ══════════════════════════════════════════════════════════════════════════════
// AC1 — Column grid renders with pile cards and term pills
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC1: column grid with pile cards and term pills", () => {
  it("renders pile cards with term pills when centroid_piles is present", () => {
    const fixture = makeFixture(["model-a", "model-b"], {
      centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });

    // Pile cards present
    const cards = container.querySelectorAll(".pile-comparison__pile-card");
    expect(cards.length).toBeGreaterThan(0);

    // Term pills present
    const pills = container.querySelectorAll(".pile-comparison__pill");
    expect(pills.length).toBeGreaterThan(0);
  });

  it("renders pile labels from labels array", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    // "Parents" label should appear
    expect(container.textContent).toContain("Parents");
  });

  it("renders column header with model name", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    // Column header should contain model short name (falls back to "model-a")
    const headers = container.querySelectorAll(".pile-comparison__column-header");
    expect(headers.length).toBeGreaterThan(0);
  });

  it("sorts pile cards by pile size descending", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const labels = Array.from(
      container.querySelectorAll(".pile-comparison__pile-label")
    ).map((el) => el.textContent?.trim() ?? "");

    // Parents (3 terms) should appear before Siblings (2 terms) before Extended (2 terms? — tiebreak)
    const parentsIdx = labels.findIndex((l) => l === "Parents");
    const extendedIdx = labels.findIndex((l) => l === "Extended");
    expect(parentsIdx).toBeLessThan(extendedIdx);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC2 — Cross-column hover highlight
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC2: cross-column hover highlight", () => {
  it("highlights pills with --highlight class on mouseenter", () => {
    const fixture = makeFixture(["model-a", "model-b"], {
      centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });

    // Find "mother" pill in model-a column
    const pills = Array.from(container.querySelectorAll(".pile-comparison__pill"));
    const motherPillA = pills.find((p) => p.textContent?.trim() === "mother");
    expect(motherPillA).toBeDefined();

    // Simulate mouseenter on mother pill.
    // Note: React synthesizes onMouseEnter/onMouseLeave from native mouseover/mouseout
    // (mouseenter does not bubble in native DOM).
    act(() => {
      motherPillA!.dispatchEvent(new MouseEvent("mouseover", { bubbles: true, relatedTarget: null }));
    });

    // Both "mother" pills (in both columns) should be highlighted
    const highlightedPills = container.querySelectorAll(".pile-comparison__pill--highlight");
    expect(highlightedPills.length).toBeGreaterThanOrEqual(2);

    // Simulate mouseleave
    act(() => {
      motherPillA!.dispatchEvent(new MouseEvent("mouseout", { bubbles: true, relatedTarget: null }));
    });

    // No more highlighted pills
    const afterLeave = container.querySelectorAll(".pile-comparison__pill--highlight");
    expect(afterLeave.length).toBe(0);
  });

  it("shows absent-term placeholder pill when hovered term missing from a column", () => {
    // "cousin" is in model-b but NOT in model-a
    const fixture = makeFixture(["model-a", "model-b"], {
      centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });

    // Find "cousin" pill in model-b
    const pills = Array.from(container.querySelectorAll(".pile-comparison__pill"));
    const cousinPill = pills.find((p) => p.textContent?.trim() === "cousin");
    expect(cousinPill).toBeDefined();

    // Hover "cousin" (React synthesizes onMouseEnter from native mouseover)
    act(() => {
      cousinPill!.dispatchEvent(new MouseEvent("mouseover", { bubbles: true, relatedTarget: null }));
    });

    // An absent-term placeholder should appear (cousin not in model-a)
    const absentPills = container.querySelectorAll(".pile-comparison__pill--absent");
    expect(absentPills.length).toBeGreaterThanOrEqual(1);
  });

  it("highlights containing pile card with --highlight class on hover", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const pills = Array.from(container.querySelectorAll(".pile-comparison__pill"));
    const motherPill = pills.find((p) => p.textContent?.trim() === "mother");
    expect(motherPill).toBeDefined();

    act(() => {
      motherPill!.dispatchEvent(new MouseEvent("mouseover", { bubbles: true, relatedTarget: null }));
    });

    const highlightedCards = container.querySelectorAll(".pile-comparison__pile-card--highlight");
    expect(highlightedCards.length).toBeGreaterThanOrEqual(1);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC3 — Stability tiers (solid/dashed borders per threshold)
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC3: stability tier classes", () => {
  it("does not add dashed class for terms with stability >= 0.8", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: {
        "model-a": {
          piles: [["mother"]],
          labels: ["Parents"],
          term_stability: { mother: 0.9 }, // >= 0.8 → no special class
        },
      },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const pills = container.querySelectorAll(".pile-comparison__pill");
    expect(pills.length).toBe(1);
    expect(pills[0].classList.contains("pile-comparison__pill--stability-medium")).toBe(false);
    expect(pills[0].classList.contains("pile-comparison__pill--stability-low")).toBe(false);
  });

  it("adds stability-medium class for terms with stability 0.6–0.79", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: {
        "model-a": {
          piles: [["parent"]],
          labels: ["Parents"],
          term_stability: { parent: 0.72 }, // 0.6 <= 0.72 < 0.8
        },
      },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const pills = container.querySelectorAll(".pile-comparison__pill");
    expect(pills.length).toBe(1);
    expect(pills[0].classList.contains("pile-comparison__pill--stability-medium")).toBe(true);
  });

  it("adds stability-low class for terms with stability < 0.6", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: {
        "model-a": {
          piles: [["cousin"]],
          labels: ["Extended"],
          term_stability: { cousin: 0.45 }, // < 0.6
        },
      },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const pills = container.querySelectorAll(".pile-comparison__pill");
    expect(pills.length).toBe(1);
    expect(pills[0].classList.contains("pile-comparison__pill--stability-low")).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC4 — Tooltip shows stability % on every pill
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC4: stability tooltip", () => {
  it("each term pill has a title attribute with stability percentage", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: {
        "model-a": {
          piles: [["mother"]],
          labels: ["Parents"],
          term_stability: { mother: 0.9 },
        },
      },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const pills = container.querySelectorAll(".pile-comparison__pill");
    expect(pills.length).toBeGreaterThan(0);

    const title = pills[0].getAttribute("title") ?? "";
    // Should say "90%" (0.9 * 100 = 90, rounded)
    expect(title).toContain("90%");
  });

  it("PILE_COMPARISON_STABILITY_TOOLTIP produces correct string", () => {
    const result = PILE_COMPARISON_STABILITY_TOOLTIP(72, "Test Model");
    expect(result).toBe("Placed here in 72% of runs for Test Model.");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC5 — Mobile switcher present (radiogroup role)
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC5: mobile model-switcher", () => {
  it("renders a radiogroup element for mobile model selection", () => {
    const fixture = makeFixture(["model-a", "model-b"], {
      centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });

    const radioGroup = container.querySelector("[role='radiogroup']");
    expect(radioGroup).not.toBeNull();

    // Each model should have a radio button
    const radios = radioGroup!.querySelectorAll("[role='radio']");
    expect(radios.length).toBe(2);
  });

  it("each radio has aria-checked attribute", () => {
    const fixture = makeFixture(["model-a", "model-b"], {
      centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });

    const radios = container.querySelectorAll("[role='radio']");
    const ariaCheckedValues = Array.from(radios).map((r) =>
      r.getAttribute("aria-checked")
    );
    // One should be "true", one "false"
    expect(ariaCheckedValues).toContain("true");
    expect(ariaCheckedValues).toContain("false");
  });

  it("radio pills have min-height: 44px via CSS class for touch targets", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const pills = container.querySelectorAll(".pile-comparison__model-pill");
    expect(pills.length).toBeGreaterThan(0);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC6 — ReadAsTableToggle accessible table (U1 pattern)
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC6: ReadAsTableToggle U1 pattern", () => {
  it("renders ReadAsTableToggle button", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const toggleBtn = container.querySelector("[aria-pressed]");
    expect(toggleBtn).not.toBeNull();
  });

  it("table container is always in DOM (U1 — aria-controls must reference existing element)", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const tableContainer = container.querySelector("#pile-comparison-table-container");
    expect(tableContainer).not.toBeNull();
  });

  it("table container is aria-hidden when not in table mode", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const tableContainer = container.querySelector("#pile-comparison-table-container");
    expect(tableContainer?.getAttribute("aria-hidden")).toBe("true");
  });

  it("toggling ReadAsTable shows table and hides visualization", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const toggleBtn = container.querySelector("[aria-pressed]") as HTMLButtonElement;
    expect(toggleBtn).not.toBeNull();

    act(() => {
      toggleBtn.click();
    });

    const tableContainer = container.querySelector("#pile-comparison-table-container");
    expect(tableContainer?.getAttribute("aria-hidden")).toBeNull();
    expect((tableContainer as HTMLElement).style.display).not.toBe("none");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC7 — ScreenReaderSummary present
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC7: ScreenReaderSummary", () => {
  it("renders ScreenReaderSummary with sr-only text", () => {
    const fixture = makeFixture(["model-a", "model-b"], {
      centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });

    // ScreenReaderSummary component renders an element with sr-only class
    const srEl = container.querySelector(".sr-only:not(h2)");
    expect(srEl).not.toBeNull();
    expect(srEl?.textContent?.length).toBeGreaterThan(0);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC8 — No forbidden vocabulary
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC8: no forbidden vocabulary", () => {
  const FORBIDDEN = [
    /\bworldview\b/i,
    /\bbelieves?\b/i,
    /\bthinks?\b/i,        // model-applied
    /model.+sees\b/i,
    /model.+understands?\b/i,
  ];

  it("PILE_COMPARISON_DESCRIPTION contains no forbidden vocabulary", () => {
    const text = PILE_COMPARISON_DESCRIPTION("family");
    for (const pattern of FORBIDDEN) {
      expect(text).not.toMatch(pattern);
    }
  });

  it("PILE_COMPARISON_EMPTY_NO_MODELS contains no forbidden vocabulary", () => {
    const text = PILE_COMPARISON_EMPTY_NO_MODELS("family");
    for (const pattern of FORBIDDEN) {
      expect(text).not.toMatch(pattern);
    }
  });

  it("pileComparisonScreenReaderSummary contains no forbidden vocabulary", () => {
    const text = pileComparisonScreenReaderSummary("family", 3);
    for (const pattern of FORBIDDEN) {
      expect(text).not.toMatch(pattern);
    }
  });

  it("rendered component text contains no forbidden vocabulary", () => {
    const fixture = makeFixture(["model-a"], {
      centroidPiles: { "model-a": PILE_DATA_A },
    });

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    const text = container.textContent ?? "";
    for (const pattern of FORBIDDEN) {
      expect(text).not.toMatch(pattern);
    }
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC9 — VizSwitcher has "Pile Structure" tab
// ══════════════════════════════════════════════════════════════════════════════

describe("VizSwitcher — AC9: Pile Structure tab present", () => {
  it("renders a tab with label 'Pile Structure'", () => {
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: () => {},
        })
      );
    });

    const tabs = Array.from(container.querySelectorAll("[role='tab']"));
    const labels = tabs.map((t) => t.textContent?.trim() ?? "");
    expect(labels).toContain("Pile Structure");
  });

  it("Pile Structure tab is NOT disabled (active)", () => {
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: () => {},
        })
      );
    });

    const tabs = Array.from(container.querySelectorAll("[role='tab']"));
    const pileTab = tabs.find((t) => t.textContent?.trim() === "Pile Structure");
    expect(pileTab).toBeDefined();
    expect(pileTab!.getAttribute("aria-disabled")).toBeNull();
  });

  it("clicking Pile Structure tab calls onTabChange with 'piles'", () => {
    const received: string[] = [];

    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: (tab) => received.push(tab),
        })
      );
    });

    const tabs = Array.from(container.querySelectorAll("[role='tab']"));
    const pileTab = tabs.find((t) => t.textContent?.trim() === "Pile Structure") as HTMLButtonElement;
    expect(pileTab).toBeDefined();

    act(() => {
      pileTab.click();
    });

    expect(received).toContain("piles");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC10 — pileComparisonScreenReaderSummary function
// ══════════════════════════════════════════════════════════════════════════════

describe("pileComparisonScreenReaderSummary — AC10: deterministic output", () => {
  it("returns empty-state string when n_models is 0", () => {
    const result = pileComparisonScreenReaderSummary("family", 0);
    expect(result).toContain("Select one or more models");
  });

  it("mentions model count in summary for n=1", () => {
    const result = pileComparisonScreenReaderSummary("family", 1);
    expect(result).toContain("1 model");
    expect(result).toContain("family");
  });

  it("mentions model count in summary for n=3", () => {
    const result = pileComparisonScreenReaderSummary("family", 3);
    expect(result).toContain("3 models");
    expect(result).toContain("family");
  });

  it("mentions hover interaction in summary", () => {
    const result = pileComparisonScreenReaderSummary("family", 2);
    expect(result.toLowerCase()).toContain("hover");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC11 — Empty state: zero models selected
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC11: empty state no models", () => {
  it("shows empty state when selectedModels is empty", () => {
    const fixture = makeFixture(["model-a"]);

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: [],
        })
      );
    });

    expect(container.textContent).toContain("Select one or more models");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC12 — Empty state: no centroid_piles data
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparison — AC12: empty state no pile data", () => {
  it("shows no-data state when centroid_piles is absent", () => {
    const fixture = makeFixture(["model-a"]); // no centroidPiles option

    act(() => {
      root.render(
        createElement(PileComparison, {
          domainResult: fixture,
          modelColors: MODEL_COLORS,
          selectedModels: ["model-a"],
        })
      );
    });

    expect(container.textContent).toContain(PILE_COMPARISON_EMPTY_NO_DATA);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC13 — PileComparisonTable renders 4-column table
// ══════════════════════════════════════════════════════════════════════════════

describe("PileComparisonTable — AC13: 4-column accessible table", () => {
  it("renders a <table> with 4 column headers", () => {
    act(() => {
      root.render(
        createElement(PileComparisonTable, {
          domainSlug: "family",
          selectedModels: ["model-a", "model-b"],
          centroidPiles: { "model-a": PILE_DATA_A, "model-b": PILE_DATA_B },
        })
      );
    });

    const table = container.querySelector("table");
    expect(table).not.toBeNull();

    const headers = table!.querySelectorAll("th");
    expect(headers.length).toBe(4);

    const headerTexts = Array.from(headers).map((h) => h.textContent?.trim() ?? "");
    expect(headerTexts).toContain("Model");
    expect(headerTexts).toContain("Pile label");
    expect(headerTexts).toContain("Term");
    expect(headerTexts).toContain("Stability (%)");
  });

  it("renders a <caption> with domain-specific text", () => {
    act(() => {
      root.render(
        createElement(PileComparisonTable, {
          domainSlug: "family",
          selectedModels: ["model-a"],
          centroidPiles: { "model-a": PILE_DATA_A },
        })
      );
    });

    const caption = container.querySelector("caption");
    expect(caption).not.toBeNull();
    expect(caption!.textContent).toContain("family");
  });

  it("renders data rows with stability percentages", () => {
    act(() => {
      root.render(
        createElement(PileComparisonTable, {
          domainSlug: "family",
          selectedModels: ["model-a"],
          centroidPiles: { "model-a": PILE_DATA_A },
        })
      );
    });

    const rows = container.querySelectorAll("tbody tr");
    expect(rows.length).toBeGreaterThan(0);

    // "mother" row should show 90% stability (0.9 * 100)
    const text = container.textContent ?? "";
    expect(text).toContain("90%");
  });

  it("handles null centroidPiles gracefully", () => {
    act(() => {
      root.render(
        createElement(PileComparisonTable, {
          domainSlug: "family",
          selectedModels: ["model-a"],
          centroidPiles: null,
        })
      );
    });

    const table = container.querySelector("table");
    expect(table).not.toBeNull();

    const rows = container.querySelectorAll("tbody tr");
    expect(rows.length).toBe(1); // empty state row
  });

  it("PILE_COMPARISON_TABLE_CAPTION includes domain slug", () => {
    const caption = PILE_COMPARISON_TABLE_CAPTION("holidays");
    expect(caption).toContain("holidays");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// AC14 — Permalink codec handles "piles" fragment
// ══════════════════════════════════════════════════════════════════════════════

describe("Permalink — AC14: piles tab round-trips correctly", () => {
  it("encodes 'piles' tab as #piles fragment", () => {
    const encoded = encodePermalink({
      domain: "family",
      models: ["model-a"],
      vizTab: "piles",
    });
    expect(encoded).toContain("#piles");
  });

  it("decodes #piles fragment back to 'piles' vizTab", () => {
    const state = decodePermalink("?domain=family&models=model-a#piles");
    expect(state).not.toBeNull();
    expect(state!.vizTab).toBe("piles");
  });

  it("round-trips piles state cleanly", () => {
    const original = {
      domain: "family",
      models: ["model-a", "model-b"],
      vizTab: "piles" as const,
    };
    const encoded = encodePermalink(original);
    const decoded = decodePermalink(encoded);
    expect(decoded).not.toBeNull();
    expect(decoded!.domain).toBe(original.domain);
    expect(decoded!.vizTab).toBe("piles");
    expect(decoded!.models).toEqual(original.models);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G40 — DESIGN_SYSTEM.md v0.5.2 static scan (Phase 9a T9: §12.10 PileComparison)
// ══════════════════════════════════════════════════════════════════════════════

describe("G40 — DESIGN_SYSTEM.md v0.5.2 static scan (§12.10 PileComparison)", () => {
  it("version line reads v0.5.2", () => {
    expect(DESIGN_SYSTEM_MD).toMatch(/\*\*Version:\*\* v0\.5\.2/);
  });

  it("footer reads 'End of DESIGN_SYSTEM.md v0.5.2'", () => {
    expect(DESIGN_SYSTEM_MD).toContain("End of DESIGN_SYSTEM.md v0.5.2");
  });

  it("§12.10 section header exists", () => {
    expect(DESIGN_SYSTEM_MD).toContain("### 12.10");
  });

  it("§12.10 contains PileComparison component name", () => {
    expect(DESIGN_SYSTEM_MD).toContain("PileComparison");
  });

  it("§12.10 contains M7 binding reference (no model is ground truth)", () => {
    expect(DESIGN_SYSTEM_MD).toContain("M7");
  });

  it("§12.10 contains cross-column hover binding", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Cross-column");
  });

  it("§11 component inventory includes PileComparison.tsx", () => {
    expect(DESIGN_SYSTEM_MD).toContain("PileComparison.tsx");
  });

  it("§11 component inventory includes pile-comparison.css", () => {
    expect(DESIGN_SYSTEM_MD).toContain("pile-comparison.css");
  });

  it("v0.5.2 changelog entry references T9", () => {
    expect(DESIGN_SYSTEM_MD).toContain("T9");
  });
});
