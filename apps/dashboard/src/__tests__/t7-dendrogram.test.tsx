// @vitest-environment jsdom
/**
 * T7 Dendrogram + DendrogramTable + dendrogram SR summary — acceptance criteria tests.
 *
 * Covers:
 *   AC1 — Dendrogram renders SVG with branches and leaf circles
 *   AC2 — Empty state when linkage data is absent
 *   AC3 — Bootstrap support annotation: dashed class on unstable branches
 *   AC4 — ScreenReaderSummary is present and non-empty
 *   AC5 — ReadAsTableToggle activates table (U1 pattern)
 *   AC6 — DendrogramTable renders correct columns
 *   AC7 — dendrogramScreenReaderSummary function (deterministic)
 *   AC8 — No forbidden vocabulary in visible strings
 *   AC9 — VizSwitcher now has "Cluster Tree" tab at index 2
 *   AC10 — Permalink codec handles "cluster-tree" fragment
 *   AC11 — DENDROGRAM_SUPPORT_THRESHOLD exported from config/analysis.ts
 *   AC12 — DendrogramTable rows sorted cluster → term lexicographic
 *   AC13 — Legend rendered below chart
 *   AC14 — Mobile leaf labels hidden via CSS class
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures only.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import type { DomainResultPublished, WithinModelResult, EllipseParams } from "../data/types";

// Components under test
import { Dendrogram } from "../components/Dendrogram";
import { DendrogramTable } from "../components/DendrogramTable";
import type { DendrogramTableRow } from "../components/DendrogramTable";
import { VizSwitcher } from "../components/VizSwitcher";

// Copy functions
import { dendrogramScreenReaderSummary } from "../copy/screen_reader_summaries";

// Config constant
import { DENDROGRAM_SUPPORT_THRESHOLD } from "../config/analysis";

// Permalink
import { encodePermalink, decodePermalink } from "../lib/permalink";

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

/**
 * Minimal linkage matrix for 4 terms:
 *   Row 0: merge(0, 1) at distance 0.2 → internal node 4
 *   Row 1: merge(2, 3) at distance 0.3 → internal node 5
 *   Row 2: merge(4, 5) at distance 0.6 → internal node 6 (root)
 */
const LINKAGE_4: number[][] = [
  [0, 1, 0.2, 2],
  [2, 3, 0.3, 2],
  [4, 5, 0.6, 4],
];

const TERM_ITEMS_4 = ["mother", "father", "sister", "brother"];

const CLUSTER_ASSIGNMENTS_4: Record<string, number> = {
  mother: 0,
  father: 0,
  sister: 1,
  brother: 1,
};

const CLUSTER_LABELS_4 = ["Parents", "Siblings"];

// BP values: one per linkage row (internal node)
// Row 0 → node4: 0.85 (stable)
// Row 1 → node5: 0.55 (unstable)
// Row 2 → node6: 0.90 (stable)
const BP_VALUES_4 = [0.85, 0.55, 0.90];

function makeFixture(opts?: {
  withData?: boolean;
  bpValues?: number[];
}): DomainResultPublished {
  const modelIds = ["model-a", "model-b"];
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

  const base = {
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
  };

  if (opts?.withData !== false) {
    return {
      ...base,
      term_cluster_linkage: LINKAGE_4,
      term_mds_items: TERM_ITEMS_4,
      term_cluster_assignments: CLUSTER_ASSIGNMENTS_4,
      term_cluster_labels: CLUSTER_LABELS_4,
      term_cluster_bp_values: opts?.bpValues ?? BP_VALUES_4,
    } as unknown as DomainResultPublished;
  }

  return base as unknown as DomainResultPublished;
}

// ── AC1: SVG renders with branches and leaf circles ──────────────────────────

describe("Dendrogram — AC1: SVG rendering", () => {
  it("renders an SVG element when linkage data is present", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const svg = container.querySelector("svg.dendrogram__svg");
    expect(svg).not.toBeNull();
  });

  it("renders leaf circles for each term", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const circles = container.querySelectorAll("circle.dendrogram__leaf-circle");
    expect(circles.length).toBe(4); // 4 terms
  });

  it("renders branch paths", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const paths = container.querySelectorAll("path.dendrogram__branch");
    // 3 internal nodes × 2 children each = 6 branch paths
    expect(paths.length).toBeGreaterThan(0);
  });
});

// ── AC2: Empty state when data is absent ─────────────────────────────────────

describe("Dendrogram — AC2: empty state", () => {
  it("renders empty state paragraph when linkage data is absent", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture({ withData: false }) }));
    });
    const svg = container.querySelector("svg.dendrogram__svg");
    expect(svg).toBeNull();
    const text = container.textContent ?? "";
    expect(text).toMatch(/not yet available|no.*data/i);
  });
});

// ── AC3: Bootstrap support annotation ────────────────────────────────────────

describe("Dendrogram — AC3: bootstrap support (M5a binding)", () => {
  it("renders dashed class on unstable branches (BP < threshold)", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    // At least one branch should be dashed (BP[1] = 0.55 < 0.70)
    const dashedBranches = container.querySelectorAll("path.dendrogram__branch--unstable");
    expect(dashedBranches.length).toBeGreaterThan(0);
  });

  it("does NOT render dashed branches when all BP values are above threshold", () => {
    act(() => {
      root.render(
        createElement(Dendrogram, {
          domainResult: makeFixture({ bpValues: [0.80, 0.90, 0.95] }),
        })
      );
    });
    const dashedBranches = container.querySelectorAll("path.dendrogram__branch--unstable");
    expect(dashedBranches.length).toBe(0);
  });
});

// ── AC4: ScreenReaderSummary ──────────────────────────────────────────────────

describe("Dendrogram — AC4: ScreenReaderSummary", () => {
  it("renders a screen reader summary element", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    // ScreenReaderSummary renders with class sr-only or role="status"
    const srEl = container.querySelector(".sr-only, [role='status']");
    expect(srEl).not.toBeNull();
  });

  it("SR summary text is non-empty when data is present", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const srEl = container.querySelector(".sr-only, [role='status']");
    expect((srEl?.textContent ?? "").trim().length).toBeGreaterThan(0);
  });
});

// ── AC5: ReadAsTableToggle activates table ────────────────────────────────────

describe("Dendrogram — AC5: ReadAsTableToggle U1 pattern", () => {
  it("table container is always in DOM (U1 binding)", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const tableContainer = container.querySelector("#dendrogram-table-container");
    expect(tableContainer).not.toBeNull();
  });

  it("table container is hidden when readAsTable is false (default)", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const tableContainer = container.querySelector("#dendrogram-table-container") as HTMLElement | null;
    expect(tableContainer).not.toBeNull();
    // Hidden by display:none or aria-hidden
    expect(
      tableContainer?.style.display === "none" || tableContainer?.getAttribute("aria-hidden") === "true"
    ).toBe(true);
  });

  it("clicking ReadAsTableToggle shows the table", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const toggleBtn = container.querySelector(
      "button[aria-pressed], button[aria-label='Read as table'], button[aria-label='Show visualization']"
    ) as HTMLButtonElement | null;
    expect(toggleBtn).not.toBeNull();

    act(() => {
      toggleBtn!.click();
    });

    const tableContainer = container.querySelector("#dendrogram-table-container") as HTMLElement | null;
    expect(tableContainer?.style.display).not.toBe("none");
  });
});

// ── AC6: DendrogramTable column structure ─────────────────────────────────────

describe("DendrogramTable — AC6: column structure", () => {
  const rows: DendrogramTableRow[] = [
    { cluster: "Parents", term: "mother", subtreeDepth: 2, bpSupport: 0.85 },
    { cluster: "Parents", term: "father", subtreeDepth: 2, bpSupport: 0.85 },
    { cluster: "Siblings", term: "sister", subtreeDepth: 1, bpSupport: 0.55 },
    { cluster: "Siblings", term: "brother", subtreeDepth: 1, bpSupport: 0.55 },
  ];

  it("renders 4 column headers", () => {
    act(() => {
      root.render(createElement(DendrogramTable, { rows, domainSlug: "family" }));
    });
    const headers = container.querySelectorAll("th");
    expect(headers.length).toBe(4);
  });

  it("renders the correct column headers", () => {
    act(() => {
      root.render(createElement(DendrogramTable, { rows, domainSlug: "family" }));
    });
    const headers = Array.from(container.querySelectorAll("th")).map((h) => h.textContent?.trim());
    expect(headers).toContain("Cluster");
    expect(headers).toContain("Term");
    expect(headers).toContain("Subtree depth");
    expect(headers).toContain("Bootstrap support (%)");
  });

  it("renders correct row count", () => {
    act(() => {
      root.render(createElement(DendrogramTable, { rows, domainSlug: "family" }));
    });
    const dataRows = container.querySelectorAll("tbody tr");
    expect(dataRows.length).toBe(4);
  });

  it("renders BP support percentage", () => {
    act(() => {
      root.render(createElement(DendrogramTable, { rows, domainSlug: "family" }));
    });
    const text = container.textContent ?? "";
    expect(text).toContain("85%");
    expect(text).toContain("55%");
  });

  it("renders — for null BP support", () => {
    const rowsWithNull: DendrogramTableRow[] = [
      { cluster: "A", term: "alpha", subtreeDepth: 1, bpSupport: null },
    ];
    act(() => {
      root.render(createElement(DendrogramTable, { rows: rowsWithNull, domainSlug: "family" }));
    });
    const text = container.textContent ?? "";
    expect(text).toContain("—");
  });
});

// ── AC7: dendrogramScreenReaderSummary (deterministic) ───────────────────────

describe("dendrogramScreenReaderSummary — AC7: deterministic output", () => {
  it("returns empty/note string for zero terms", () => {
    const result = dendrogramScreenReaderSummary("family", 0, 0, 0);
    expect(result.length).toBeGreaterThan(0);
    expect(result).toMatch(/no.*data|not yet/i);
  });

  it("sentence 1 includes term count and cluster count", () => {
    const result = dendrogramScreenReaderSummary("family", 10, 3, 0);
    expect(result).toContain("10");
    expect(result).toContain("3");
    expect(result).toContain("family");
  });

  it("sentence 2 includes unstable branch count when > 0", () => {
    const result = dendrogramScreenReaderSummary("family", 10, 3, 2);
    expect(result).toContain("2");
    expect(result).toContain("dashed");
  });

  it("omits sentence 2 when no unstable branches", () => {
    const result = dendrogramScreenReaderSummary("family", 10, 3, 0);
    expect(result).not.toContain("dashed");
  });

  it("no forbidden vocabulary in output", () => {
    const result = dendrogramScreenReaderSummary("family", 15, 4, 3);
    expect(result.toLowerCase()).not.toContain("worldview");
    expect(result.toLowerCase()).not.toContain("believes");
    // "thinks" in model-applied context: check the full result
    expect(result).not.toMatch(/model.{0,20}thinks/i);
    expect(result.toLowerCase()).not.toContain("understands");
  });
});

// ── AC8: No forbidden vocabulary in visible strings ───────────────────────────

describe("Dendrogram — AC8: no forbidden vocabulary", () => {
  it("no forbidden vocabulary in rendered text", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const text = (container.textContent ?? "").toLowerCase();
    expect(text).not.toContain("worldview");
    expect(text).not.toContain("believes");
    expect(text).not.toContain("what the model understands");
    expect(text).not.toContain("model's worldview");
    expect(text).not.toContain("cultural bias");
  });
});

// ── AC9: VizSwitcher has "Cluster Tree" tab ───────────────────────────────────

describe("VizSwitcher — AC9: Cluster Tree tab at index 2", () => {
  it("renders 8 tabs including Cluster Tree (Phase 9a T7)", () => {
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: () => {},
        })
      );
    });
    const tabs = container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    expect(tabs.length).toBe(8);
  });

  it("Cluster Tree tab is at index 2", () => {
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: () => {},
        })
      );
    });
    const tabs = container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    expect(tabs[2].textContent?.trim()).toBe("Cluster Tree");
  });

  it("Term Map tab is at index 1", () => {
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: () => {},
        })
      );
    });
    const tabs = container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    expect(tabs[1].textContent?.trim()).toBe("Term Map");
  });

  it("Cluster Tree tab fires onTabChange('cluster-tree') on click", () => {
    const calls: string[] = [];
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "mds",
          onTabChange: (tab) => calls.push(tab),
        })
      );
    });
    const tabs = container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    act(() => {
      tabs[2].click();
    });
    expect(calls).toContain("cluster-tree");
  });

  it("Cluster Tree tab has aria-selected='true' when active", () => {
    act(() => {
      root.render(
        createElement(VizSwitcher, {
          activeTab: "cluster-tree",
          onTabChange: () => {},
        })
      );
    });
    const tabs = container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    const clusterTreeTab = Array.from(tabs).find((t) => t.textContent?.trim() === "Cluster Tree");
    expect(clusterTreeTab?.getAttribute("aria-selected")).toBe("true");
  });
});

// ── AC10: Permalink handles "cluster-tree" ────────────────────────────────────

describe("Permalink — AC10: cluster-tree fragment", () => {
  it("encodePermalink with cluster-tree produces #cluster-tree fragment", () => {
    const encoded = encodePermalink({
      domain: "family",
      models: ["model-a"],
      vizTab: "cluster-tree",
    });
    expect(encoded).toContain("#cluster-tree");
  });

  it("decodePermalink with #cluster-tree returns cluster-tree vizTab", () => {
    const decoded = decodePermalink("?domain=family&models=model-a#cluster-tree");
    expect(decoded).not.toBeNull();
    expect(decoded?.vizTab).toBe("cluster-tree");
  });

  it("encode → decode round-trip for cluster-tree", () => {
    const state = {
      domain: "holidays",
      models: ["model-a", "model-b"],
      vizTab: "cluster-tree" as const,
    };
    const encoded = encodePermalink(state);
    const decoded = decodePermalink(encoded);
    expect(decoded?.vizTab).toBe("cluster-tree");
    expect(decoded?.domain).toBe("holidays");
    expect(decoded?.models).toEqual(["model-a", "model-b"]);
  });
});

// ── AC11: DENDROGRAM_SUPPORT_THRESHOLD exported ───────────────────────────────

describe("Config — AC11: DENDROGRAM_SUPPORT_THRESHOLD", () => {
  it("DENDROGRAM_SUPPORT_THRESHOLD is exported and equals 0.70", () => {
    expect(DENDROGRAM_SUPPORT_THRESHOLD).toBe(0.70);
  });

  it("DENDROGRAM_SUPPORT_THRESHOLD is a number between 0 and 1", () => {
    expect(typeof DENDROGRAM_SUPPORT_THRESHOLD).toBe("number");
    expect(DENDROGRAM_SUPPORT_THRESHOLD).toBeGreaterThan(0);
    expect(DENDROGRAM_SUPPORT_THRESHOLD).toBeLessThan(1);
  });
});

// ── AC12: DendrogramTable sort order ─────────────────────────────────────────

describe("DendrogramTable — AC12: sort order", () => {
  it("rows sorted cluster → term lexicographic", () => {
    const rows: DendrogramTableRow[] = [
      { cluster: "Siblings", term: "sister", subtreeDepth: 1, bpSupport: 0.80 },
      { cluster: "Parents", term: "mother", subtreeDepth: 2, bpSupport: 0.90 },
      { cluster: "Parents", term: "father", subtreeDepth: 2, bpSupport: 0.90 },
      { cluster: "Siblings", term: "brother", subtreeDepth: 1, bpSupport: 0.80 },
    ];
    act(() => {
      root.render(createElement(DendrogramTable, { rows, domainSlug: "family" }));
    });
    const cells = container.querySelectorAll("tbody td:nth-child(2)");
    const terms = Array.from(cells).map((c) => c.textContent?.trim());
    // Expected order: father, mother (Parents), brother, sister (Siblings)
    expect(terms[0]).toBe("father");
    expect(terms[1]).toBe("mother");
    expect(terms[2]).toBe("brother");
    expect(terms[3]).toBe("sister");
  });
});

// ── AC13: Legend rendered ─────────────────────────────────────────────────────

describe("Dendrogram — AC13: legend below chart", () => {
  it("renders legend div with dashed-branch explanation", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    const legend = container.querySelector(".dendrogram__legend");
    expect(legend).not.toBeNull();
    const text = legend?.textContent ?? "";
    expect(text).toMatch(/dashed.*bootstrap|bootstrap.*dashed/i);
  });
});

// ── AC14: Mobile leaf labels CSS class ───────────────────────────────────────

describe("Dendrogram — AC14: mobile leaf label CSS class", () => {
  it("leaf labels have class dendrogram__leaf-label", () => {
    act(() => {
      root.render(createElement(Dendrogram, { domainResult: makeFixture() }));
    });
    // Labels are <text> elements with the class; check class is present
    const labels = container.querySelectorAll("text.dendrogram__leaf-label");
    // With showLabels defaulting to true, there should be labels
    expect(labels.length).toBeGreaterThan(0);
  });
});
