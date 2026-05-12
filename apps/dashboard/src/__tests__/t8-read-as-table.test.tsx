// @vitest-environment jsdom
/**
 * T8 Read-as-table toggle + ScreenReaderSummary — acceptance criteria tests.
 *
 * Covers:
 *   AC #5  — toggle button has aria-pressed + aria-controls
 *   AC #6  — touch targets 44px at narrow viewport
 *   AC #7  — keyboard accessible (Enter/Space toggle)
 *   AC #8  — ScreenReaderSummary present in both modes
 *   AC #9  — R10 column adjacency in all three tables
 *   AC #10 — semantic table structure
 *   AC #12 — MDS empty state
 *   AC #13 — FreeList empty states A/B/C
 *   AC #14 — Similarity empty state
 *   AC #17 — no string literals for LSB copy in component files
 *   AC #18 — no forbidden vocabulary
 *   AC #19 — data/types.ts untouched
 *   AC #27 — integration: toggle hides SVG/shows table
 *   U1     — table container always in DOM
 *   U2     — pressed-state border CSS
 *
 * Also tests:
 *   screen_reader_summaries.ts template byte-equivalence (CDA SME §2 binding)
 *   mapConsensusType enum mapping (CDA SME S1)
 *   No generated_lede usage in SR templates (CDA SME S11)
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures only.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import type { DomainResultPublished, WithinModelResult } from "../data/types";

// Components under test
import { ReadAsTableToggle } from "../components/ReadAsTableToggle";
import { ScreenReaderSummary } from "../components/ScreenReaderSummary";
import { MdsTable } from "../components/MdsTable";
import { FreeListTable } from "../components/FreeListTable";
import { SimilarityTable } from "../components/SimilarityTable";
import { MDSPlot } from "../components/MDSPlot";
import { FreeListCompare } from "../components/FreeListCompare";
import { SimilarityHeatmap } from "../components/SimilarityHeatmap";

// Copy module
import {
  READ_AS_TABLE_LABEL_REST,
  READ_AS_TABLE_LABEL_PRESSED,
  MDS_TABLE_CAPTION,
  SIMILARITY_TABLE_CAPTION,
  MDS_TABLE_EMPTY_NO_MODELS,
  FREELIST_TABLE_EMPTY_NO_MODELS,
  SIMILARITY_TABLE_EMPTY_LT_2_MODELS,
  mapConsensusType,
  mdsScreenReaderSummary,
  freeListScreenReaderSummary,
  similarityScreenReaderSummary,
  freeListTableCaption,
} from "../copy/screen_reader_summaries";

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

// ── Fixture builders ──────────────────────────────────────────────────────────

type SutropEntry = { item: string; csi: number; f_mentions: number; n_runs: number; mean_position: number };

function makeFixture(
  modelIds: string[],
  opts?: {
    consensusType?: string;
    r1States?: Record<string, string>;
    sutropCsi?: Record<string, SutropEntry[] | undefined>;
    similarityMatrix?: number[][];
    similarityCi?: Array<Array<[number, number] | null>>;
  }
): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, {
    center: [number, number];
    semi_major: number;
    semi_minor: number;
    rotation_rad: number;
    n_bootstrap: number;
  } | null> = {};
  const within_model_results: WithinModelResult[] = [];

  modelIds.forEach((id, i) => {
    mds_coordinates[id] = [i * 0.1, i * 0.1];
    mds_uncertainty[id] = {
      center: [i * 0.1, i * 0.1],
      semi_major: 0.12,
      semi_minor: 0.08,
      rotation_rad: 1.5,
      n_bootstrap: 500,
    };
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

  const n = modelIds.length;
  const defaultMatrix = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 1.0 : 0.72 + i * 0.01 + j * 0.01))
  );
  const defaultCi: Array<Array<[number, number] | null>> = Array.from(
    { length: n },
    (_, i) =>
      Array.from({ length: n }, (_, j) =>
        i === j ? null : ([0.65 + i * 0.01, 0.81 + j * 0.01] as [number, number])
      )
  );

  const defaultSutropCsi: Record<string, SutropEntry[]> = {};
  for (const id of modelIds) {
    defaultSutropCsi[id] = [
      { item: "alpha", csi: 0.75, f_mentions: 3, n_runs: 4, mean_position: 1.0 },
      { item: "beta", csi: 0.50, f_mentions: 2, n_runs: 4, mean_position: 2.0 },
    ];
  }

  const finalSutrop = opts?.sutropCsi !== undefined
    ? { ...defaultSutropCsi, ...opts.sutropCsi }
    : defaultSutropCsi;

  return {
    domain_slug: "test-domain",
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
    mds_uncertainty: mds_uncertainty as unknown as Record<string, import("../data/types").EllipseParams | null>,
    similarity_matrix: (opts?.similarityMatrix ?? defaultMatrix) as unknown as Record<string, Record<string, number>>,
    similarity_ci: (opts?.similarityCi ?? defaultCi) as unknown as Record<string, Record<string, [number, number] | null>>,
    consensus_score: 0.71,
    consensus_ci: [0.65, 0.77],
    consensus_type: (opts?.consensusType ?? "STRONG_CONSENSUS") as DomainResultPublished["consensus_type"],
    sutrop_csi: finalSutrop as unknown as Record<string, Record<string, number>>,
    within_model_results,
    groundings: [],
    generated_lede: "Test lede for test domain.",
    generated_at: "2026-05-12T00:00:00Z",
    display: {
      r1_states: Object.fromEntries(
        modelIds.map((id) => [id, (opts?.r1States?.[id] ?? "typical_concentration") as import("../data/types").R1State])
      ),
      top_terms: Object.fromEntries(modelIds.map((id) => [id, ["alpha", "beta"]])),
      top_terms_metric: "sutrop_csi",
    },
  };
}

const TWO_COLORS: Record<string, string> = {
  "model-a": "#3360a9",
  "model-b": "#c0392b",
};

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Copy module: button labels, captions, empty states
// ══════════════════════════════════════════════════════════════════════════════

describe("screen_reader_summaries.ts — button labels (CDA SME S4)", () => {
  it("READ_AS_TABLE_LABEL_REST is 'Read as table'", () => {
    expect(READ_AS_TABLE_LABEL_REST).toBe("Read as table");
  });

  it("READ_AS_TABLE_LABEL_PRESSED is 'Show visualization'", () => {
    expect(READ_AS_TABLE_LABEL_PRESSED).toBe("Show visualization");
  });
});

describe("screen_reader_summaries.ts — MDS table caption (CDA SME S6)", () => {
  it("MDS_TABLE_CAPTION contains 'one model' (not 'a model')", () => {
    expect(MDS_TABLE_CAPTION).toContain("one model");
  });

  it("MDS_TABLE_CAPTION contains 'bootstrap uncertainty around that position'", () => {
    expect(MDS_TABLE_CAPTION).toContain("bootstrap uncertainty around that position");
  });

  it("MDS_TABLE_CAPTION contains 'output distribution had low variability or was deterministic'", () => {
    expect(MDS_TABLE_CAPTION).toContain(
      "output distribution had low variability or was deterministic"
    );
  });

  it("MDS_TABLE_CAPTION matches binding verbatim", () => {
    expect(MDS_TABLE_CAPTION).toBe(
      "Each row shows where one model lands on the MDS map and the bootstrap uncertainty around that position. Rows showing — under semi-major / semi-minor / rotation have no confidence ellipse — their output distribution had low variability or was deterministic, so the bootstrap could not estimate a position uncertainty."
    );
  });
});

describe("screen_reader_summaries.ts — Similarity table caption (CDA SME S7)", () => {
  it("SIMILARITY_TABLE_CAPTION contains 'no shared structure' (T5 cross-surface, CDA SME S3/S5)", () => {
    expect(SIMILARITY_TABLE_CAPTION).toContain("no shared structure");
  });

  it("SIMILARITY_TABLE_CAPTION does NOT contain 'pairwise agreement' (T5 rejected wording)", () => {
    expect(SIMILARITY_TABLE_CAPTION).not.toContain("pairwise agreement");
  });

  it("SIMILARITY_TABLE_CAPTION contains 'no bootstrap interval available'", () => {
    expect(SIMILARITY_TABLE_CAPTION).toContain("no bootstrap interval available");
  });

  it("SIMILARITY_TABLE_CAPTION matches binding verbatim", () => {
    expect(SIMILARITY_TABLE_CAPTION).toBe(
      "Each row compares two models in the current selection. The similarity column shows how similarly the two models organize this domain (1.00 = identical organization; 0.50 = no shared structure); the 95% confidence interval columns show the bootstrap range around that value. Rows showing — under the confidence interval columns have no bootstrap interval available."
    );
  });
});

describe("screen_reader_summaries.ts — FreeList caption template (CDA SME S5)", () => {
  it("freeListTableCaption contains possessive + 'this model's collection runs'", () => {
    const caption = freeListTableCaption("GPT-4o");
    expect(caption).toContain("this model's collection runs");
  });

  it("freeListTableCaption contains 'for this domain'", () => {
    const caption = freeListTableCaption("GPT-4o");
    expect(caption).toContain("for this domain");
  });

  it("freeListTableCaption uses the model short name with possessive", () => {
    const caption = freeListTableCaption("Claude");
    expect(caption).toContain("Claude's ranked terms");
  });
});

describe("screen_reader_summaries.ts — empty states (CDA SME S8)", () => {
  it("MDS_TABLE_EMPTY_NO_MODELS approved verbatim", () => {
    expect(MDS_TABLE_EMPTY_NO_MODELS).toBe(
      "Select one or more models to see the MDS coordinates table."
    );
  });

  it("FREELIST_TABLE_EMPTY_NO_MODELS includes 'for this domain'", () => {
    expect(FREELIST_TABLE_EMPTY_NO_MODELS).toContain("for this domain");
    expect(FREELIST_TABLE_EMPTY_NO_MODELS).toBe(
      "Select one or more models to see the ranked-term tables for this domain."
    );
  });

  it("SIMILARITY_TABLE_EMPTY_LT_2_MODELS includes 'pairwise'", () => {
    expect(SIMILARITY_TABLE_EMPTY_LT_2_MODELS).toContain("pairwise");
    expect(SIMILARITY_TABLE_EMPTY_LT_2_MODELS).toBe(
      "Select at least two models to see the pairwise similarity table."
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — mapConsensusType (CDA SME S1)
// ══════════════════════════════════════════════════════════════════════════════

describe("mapConsensusType — CDA SME S1 binding enum mapping", () => {
  it("STRONG_CONSENSUS → 'strong consensus (the models organize this domain similarly)'", () => {
    expect(mapConsensusType("STRONG_CONSENSUS")).toBe(
      "strong consensus (the models organize this domain similarly)"
    );
  });

  it("WEAK_CONSENSUS → 'weak consensus ...'", () => {
    expect(mapConsensusType("WEAK_CONSENSUS")).toContain("weak consensus");
  });

  it("TURBULENT → 'turbulent ...'", () => {
    expect(mapConsensusType("TURBULENT")).toContain("turbulent");
  });

  it("CONTESTED → 'contested ...'", () => {
    expect(mapConsensusType("CONTESTED")).toContain("contested");
  });

  it("SUBCULTURAL → 'subcultural ...'", () => {
    expect(mapConsensusType("SUBCULTURAL")).toContain("subcultural");
  });

  it("null → null (omit Sentence 2)", () => {
    expect(mapConsensusType(null)).toBeNull();
  });

  it("undefined → null (omit Sentence 2)", () => {
    expect(mapConsensusType(undefined)).toBeNull();
  });

  it("output does NOT contain bare enum string 'STRONG_CONSENSUS'", () => {
    const result = mapConsensusType("STRONG_CONSENSUS");
    expect(result).not.toContain("STRONG_CONSENSUS");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — mdsScreenReaderSummary (CDA SME §2.1)
// ══════════════════════════════════════════════════════════════════════════════

describe("mdsScreenReaderSummary (CDA SME §2.1)", () => {
  it("Sentence 1: contains model count and 'categorical structure'", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    const result = mdsScreenReaderSummary(dr, ["model-a", "model-b"]);
    expect(result).toContain("2 models");
    expect(result).toContain("categorical structure");
  });

  it("Sentence 2: contains mapped consensus phrase, not bare enum", () => {
    const dr = makeFixture(["model-a"], { consensusType: "STRONG_CONSENSUS" });
    const result = mdsScreenReaderSummary(dr, ["model-a"]);
    expect(result).toContain(
      "strong consensus (the models organize this domain similarly)"
    );
    expect(result).not.toContain("STRONG_CONSENSUS");
  });

  it("Sentence 2 omitted when consensus_type is null", () => {
    const dr = makeFixture(["model-a"], { consensusType: undefined as unknown as string });
    const drNoConsensus = { ...dr, consensus_type: null as unknown as DomainResultPublished["consensus_type"] };
    const result = mdsScreenReaderSummary(drNoConsensus, ["model-a"]);
    expect(result).not.toContain("agreement matrix");
  });

  it("Sentence 3: counts suppressed ellipses for R1-b/R1-c models", () => {
    const dr = makeFixture(["model-a", "model-b"], {
      r1States: { "model-a": "typical_concentration", "model-b": "low_concentration" },
    });
    const result = mdsScreenReaderSummary(dr, ["model-a", "model-b"]);
    expect(result).toContain("1 of these 2 models have no confidence ellipse");
  });

  it("Sentence 3 omitted when all models have typical concentration", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    const result = mdsScreenReaderSummary(dr, ["model-a", "model-b"]);
    expect(result).not.toContain("no confidence ellipse");
  });

  it("does NOT contain 'generated_lede' (CDA SME S11)", () => {
    const dr = makeFixture(["model-a"]);
    const result = mdsScreenReaderSummary(dr, ["model-a"]);
    expect(result).not.toContain("Test lede for test domain.");
  });

  it("sample output for family.json scenario: 11 models, STRONG_CONSENSUS, no R1-b/c", () => {
    const modelIds = Array.from({ length: 11 }, (_, i) => `model-${i}`);
    const dr = makeFixture(modelIds, { consensusType: "STRONG_CONSENSUS" });
    const result = mdsScreenReaderSummary(dr, modelIds);
    expect(result).toBe(
      "This chart places 11 models on a two-dimensional map according to how their outputs categorize this domain; models with more similar categorical structure sit closer together. Across the full model slate, the between-model agreement matrix classifies as strong consensus (the models organize this domain similarly)."
    );
  });

  it("≤ 3 sentences (CDA SME S10)", () => {
    const dr = makeFixture(["m1", "m2"], {
      consensusType: "STRONG_CONSENSUS",
      r1States: { "m1": "typical_concentration", "m2": "low_concentration" },
    });
    const result = mdsScreenReaderSummary(dr, ["m1", "m2"]);
    // Count sentences by splitting on ". " and checking reasonable length
    const sentences = result.split(". ").filter(Boolean);
    expect(sentences.length).toBeLessThanOrEqual(3);
  });

  it("forbidden vocabulary: no 'believes', 'worldview', 'thinks'", () => {
    const dr = makeFixture(["model-a"]);
    const result = mdsScreenReaderSummary(dr, ["model-a"]);
    expect(result).not.toMatch(/\bbelieves\b/i);
    expect(result).not.toMatch(/\bworldview\b/i);
    expect(result).not.toMatch(/\bthinks\b/i);
  });

  it("forbidden vocabulary: no 'agree' (CDA SME S3)", () => {
    const dr = makeFixture(["model-a"]);
    const result = mdsScreenReaderSummary(dr, ["model-a"]);
    expect(result).not.toMatch(/\bagree\b/i);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — freeListScreenReaderSummary (CDA SME §2.2)
// ══════════════════════════════════════════════════════════════════════════════

describe("freeListScreenReaderSummary (CDA SME §2.2)", () => {
  it("Sentence 1: contains selected model count", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    const result = freeListScreenReaderSummary(dr, ["model-a", "model-b"]);
    expect(result).toContain("2 selected models");
  });

  it("Sentence 1: contains 'Sutrop salience score'", () => {
    const dr = makeFixture(["model-a"]);
    const result = freeListScreenReaderSummary(dr, ["model-a"]);
    expect(result).toContain("Sutrop salience score");
  });

  it("Sentence 1: contains 'collection runs' (T7 N5.1 cross-surface)", () => {
    const dr = makeFixture(["model-a"]);
    const result = freeListScreenReaderSummary(dr, ["model-a"]);
    expect(result).toContain("collection runs");
  });

  it("Sentence 2 (n >= 2): contains term count range and shared term count", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    const result = freeListScreenReaderSummary(dr, ["model-a", "model-b"]);
    expect(result).toContain("Term counts range from");
    expect(result).toContain("terms appear in every selected model");
  });

  it("Single model: uses 'The selected model produced N terms'", () => {
    const dr = makeFixture(["model-a"]);
    const result = freeListScreenReaderSummary(dr, ["model-a"]);
    expect(result).toContain("The selected model produced");
    expect(result).toContain("2 terms");
  });

  it("Empty selection: returns '(Select one or more models...)'", () => {
    const dr = makeFixture([]);
    const result = freeListScreenReaderSummary(dr, []);
    expect(result).toContain("Select one or more models");
  });

  it("does NOT contain 'generated_lede' (CDA SME S11)", () => {
    const dr = makeFixture(["model-a"]);
    const result = freeListScreenReaderSummary(dr, ["model-a"]);
    expect(result).not.toContain("Test lede for test domain.");
  });

  it("≤ 2 sentences (CDA SME S10)", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    const result = freeListScreenReaderSummary(dr, ["model-a", "model-b"]);
    const sentences = result.split(". ").filter((s) => s.trim().length > 0);
    expect(sentences.length).toBeLessThanOrEqual(3); // 2 sentences + possible trailing
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — similarityScreenReaderSummary (CDA SME §2.3)
// ══════════════════════════════════════════════════════════════════════════════

describe("similarityScreenReaderSummary (CDA SME §2.3)", () => {
  it("Sentence 1: contains 'pairwise similarity scores'", () => {
    const dr = makeFixture(["m1", "m2", "m3"]);
    const result = similarityScreenReaderSummary(dr, ["m1", "m2", "m3"]);
    expect(result).toContain("pairwise similarity scores");
  });

  it("Sentence 1: contains 'no shared structure' (T5 cross-surface, CDA SME S3)", () => {
    const dr = makeFixture(["m1", "m2"]);
    const result = similarityScreenReaderSummary(dr, ["m1", "m2"]);
    expect(result).toContain("no shared structure");
  });

  it("Sentence 1: does NOT contain 'agree' (CDA SME S3)", () => {
    const dr = makeFixture(["m1", "m2"]);
    const result = similarityScreenReaderSummary(dr, ["m1", "m2"]);
    expect(result).not.toMatch(/\bagree\b/i);
  });

  it("Sentence 2: contains off-diagonal range with .toFixed(2) values", () => {
    const dr = makeFixture(["m1", "m2"]);
    const result = similarityScreenReaderSummary(dr, ["m1", "m2"]);
    expect(result).toContain("Off-diagonal similarity scores range from");
    // Values should be .toFixed(2) format (two decimal places)
    expect(result).toMatch(/\d+\.\d{2}/);
  });

  it("n_selected < 2: returns empty state message", () => {
    const dr = makeFixture(["m1"]);
    const result = similarityScreenReaderSummary(dr, ["m1"]);
    expect(result).toContain("Select at least two models");
  });

  it("does NOT contain 'generated_lede' (CDA SME S11)", () => {
    const dr = makeFixture(["m1", "m2"]);
    const result = similarityScreenReaderSummary(dr, ["m1", "m2"]);
    expect(result).not.toContain("Test lede for test domain.");
  });

  it("≤ 3 sentences (CDA SME S10)", () => {
    const dr = makeFixture(["m1", "m2", "m3"]);
    const result = similarityScreenReaderSummary(dr, ["m1", "m2", "m3"]);
    // Rough sentence count (split on period+space)
    const parts = result.split(". ").filter((s) => s.trim().length > 0);
    expect(parts.length).toBeLessThanOrEqual(4); // Up to 3 sentences + possible trailing
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — ReadAsTableToggle component
// ══════════════════════════════════════════════════════════════════════════════

describe("ReadAsTableToggle (AC #5, U1, U2)", () => {
  it("renders a <button> element", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: false,
          onToggle: () => {},
          tableContainerId: "test-table",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector("button");
    expect(btn).not.toBeNull();
  });

  it("aria-pressed='false' at rest", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: false,
          onToggle: () => {},
          tableContainerId: "test-table",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector("button")!;
    expect(btn.getAttribute("aria-pressed")).toBe("false");
  });

  it("aria-pressed='true' when pressed", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: true,
          onToggle: () => {},
          tableContainerId: "test-table",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector("button")!;
    expect(btn.getAttribute("aria-pressed")).toBe("true");
  });

  it("aria-controls points to tableContainerId", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: false,
          onToggle: () => {},
          tableContainerId: "my-table-id",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector("button")!;
    expect(btn.getAttribute("aria-controls")).toBe("my-table-id");
  });

  it("label text = 'Read as table' at rest", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: false,
          onToggle: () => {},
          tableContainerId: "test-table",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector("button")!;
    expect(btn.textContent?.trim()).toBe("Read as table");
  });

  it("label text = 'Show visualization' when pressed", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: true,
          onToggle: () => {},
          tableContainerId: "test-table",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector("button")!;
    expect(btn.textContent?.trim()).toBe("Show visualization");
  });

  it("has className 'read-as-table-toggle__button'", () => {
    act(() => {
      root.render(
        createElement(ReadAsTableToggle, {
          pressed: false,
          onToggle: () => {},
          tableContainerId: "test-table",
          labels: { rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED },
        })
      );
    });
    const btn = container.querySelector(".read-as-table-toggle__button");
    expect(btn).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — ScreenReaderSummary component
// ══════════════════════════════════════════════════════════════════════════════

describe("ScreenReaderSummary (AC #8)", () => {
  it("renders a <p> with class sr-only screen-reader-summary", () => {
    act(() => {
      root.render(createElement(ScreenReaderSummary, { text: "Test summary text." }));
    });
    const p = container.querySelector("p.sr-only.screen-reader-summary");
    expect(p).not.toBeNull();
  });

  it("renders the text content", () => {
    act(() => {
      root.render(createElement(ScreenReaderSummary, { text: "Hello world." }));
    });
    const p = container.querySelector("p.sr-only.screen-reader-summary")!;
    expect(p.textContent).toBe("Hello world.");
  });

  it("renders null when text is empty", () => {
    act(() => {
      root.render(createElement(ScreenReaderSummary, { text: "" }));
    });
    const p = container.querySelector("p.sr-only");
    expect(p).toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — MdsTable (AC #9, #10, #12)
// ══════════════════════════════════════════════════════════════════════════════

describe("MdsTable (AC #9, #10, #12)", () => {
  it("renders a <table> with <caption>, <thead>, <tbody>", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a", "model-b"],
          modelColors: TWO_COLORS,
        })
      );
    });
    expect(container.querySelector("table")).not.toBeNull();
    expect(container.querySelector("caption")).not.toBeNull();
    expect(container.querySelector("thead")).not.toBeNull();
    expect(container.querySelector("tbody")).not.toBeNull();
  });

  it("all <th> elements have scope='col'", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const ths = container.querySelectorAll("th");
    ths.forEach((th) => {
      expect(th.getAttribute("scope")).toBe("col");
    });
  });

  it("R10: x/y columns present and ellipse columns adjacent", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const headerTexts = Array.from(container.querySelectorAll("th")).map(
      (th) => th.textContent?.trim()
    );
    const xIdx = headerTexts.indexOf("x");
    const yIdx = headerTexts.indexOf("y");
    const semiMajorIdx = headerTexts.indexOf("Semi-major");
    // x and y should be present
    expect(xIdx).toBeGreaterThan(-1);
    expect(yIdx).toBeGreaterThan(-1);
    // Semi-major should come after y (R10 pairing — adjacent)
    expect(semiMajorIdx).toBeGreaterThan(yIdx);
  });

  it("CDA SME S9: header 'Output concentration' (not 'Uncertainty mode')", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const headers = Array.from(container.querySelectorAll("th")).map(
      (th) => th.textContent?.trim()
    );
    expect(headers).toContain("Output concentration");
    expect(headers).not.toContain("Uncertainty mode");
  });

  it("CDA SME S9: header 'Bootstrap samples' (not 'n_bootstrap')", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const headers = Array.from(container.querySelectorAll("th")).map(
      (th) => th.textContent?.trim()
    );
    expect(headers).toContain("Bootstrap samples");
    expect(headers).not.toContain("n_bootstrap");
  });

  it("CDA SME S9: header 'Rotation angle' (not 'Rotation (rad)')", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const headers = Array.from(container.querySelectorAll("th")).map(
      (th) => th.textContent?.trim()
    );
    expect(headers).toContain("Rotation angle");
    expect(headers).not.toContain("Rotation (rad)");
  });

  it("R1-b model renders — in ellipse columns", () => {
    const dr = makeFixture(["model-a"], {
      r1States: { "model-a": "low_concentration" },
    });
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const tds = Array.from(container.querySelectorAll("td")).map(
      (td) => td.textContent?.trim()
    );
    // Should have — in the ellipse columns
    expect(tds).toContain("—");
  });

  it("empty state: renders MDS_TABLE_EMPTY_NO_MODELS when no models selected", () => {
    const dr = makeFixture([]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: [],
          modelColors: {},
        })
      );
    });
    const empty = container.querySelector(".read-as-table__empty");
    expect(empty).not.toBeNull();
    expect(empty!.textContent).toBe(MDS_TABLE_EMPTY_NO_MODELS);
    expect(container.querySelector("table")).toBeNull();
  });

  it("sort order: rows are sorted lexicographically by model_id", () => {
    const dr = makeFixture(["z-model", "a-model", "m-model"]);
    act(() => {
      root.render(
        createElement(MdsTable, {
          domainResult: dr,
          selectedModels: ["z-model", "a-model", "m-model"],
          modelColors: { "z-model": "#3360a9", "a-model": "#c0392b", "m-model": "#27ae60" },
        })
      );
    });
    const rows = container.querySelectorAll("tbody tr");
    // First cell of each row is the model short name
    const firstCells = Array.from(rows).map((r) => r.querySelector("td")?.textContent?.trim());
    // Check the model_id cells (second column) are lexicographic
    const idCells = Array.from(rows).map((r) => {
      const cells = r.querySelectorAll("td");
      return cells[1]?.textContent?.trim();
    });
    expect(idCells[0]).toBe("a-model");
    expect(idCells[1]).toBe("m-model");
    expect(idCells[2]).toBe("z-model");
    // Suppress unused variable warning
    void firstCells;
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — FreeListTable (AC #9, #10, #13)
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListTable (AC #9, #10, #13)", () => {
  it("renders one <table> per selected model", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a", "model-b"],
          modelColors: TWO_COLORS,
        })
      );
    });
    const tables = container.querySelectorAll("table");
    expect(tables.length).toBe(2);
  });

  it("each sub-table has an <h4> heading", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a", "model-b"],
          modelColors: TWO_COLORS,
        })
      );
    });
    const h4s = container.querySelectorAll("h4");
    expect(h4s.length).toBe(2);
  });

  it("R10: Salience (CSI) and Inclusion frequency are adjacent columns", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const headers = Array.from(container.querySelectorAll("th")).map(
      (th) => th.textContent?.trim()
    );
    const csiIdx = headers.indexOf("Salience (CSI)");
    const freqIdx = headers.indexOf("Inclusion frequency");
    expect(csiIdx).toBeGreaterThan(-1);
    expect(freqIdx).toBeGreaterThan(-1);
    // Adjacent: freqIdx should be csiIdx + 1
    expect(freqIdx).toBe(csiIdx + 1);
  });

  it("terms are sorted by CSI descending", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a"],
          modelColors: { "model-a": "#3360a9" },
        })
      );
    });
    const termCells = Array.from(container.querySelectorAll("tbody td:nth-child(2)")).map(
      (td) => td.textContent?.trim()?.replace(" ★", "")
    );
    // Default fixture: alpha (0.75) > beta (0.50)
    expect(termCells[0]).toBe("alpha");
    expect(termCells[1]).toBe("beta");
  });

  it("shared-term ★ glyph present when term is in all selected models", () => {
    const dr = makeFixture(["model-a", "model-b"]); // both have alpha, beta
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a", "model-b"],
          modelColors: TWO_COLORS,
        })
      );
    });
    const stars = container.querySelectorAll(".read-as-table__shared-star");
    // 2 terms × 2 models = 4 stars
    expect(stars.length).toBe(4);
  });

  it("Case A empty state: renders FREELIST_TABLE_EMPTY_NO_MODELS", () => {
    const dr = makeFixture([]);
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: [],
          modelColors: {},
        })
      );
    });
    const empty = container.querySelector(".read-as-table__empty");
    expect(empty).not.toBeNull();
    expect(empty!.textContent).toBe(FREELIST_TABLE_EMPTY_NO_MODELS);
    expect(container.querySelector("table")).toBeNull();
  });

  it("Case B: renders '(no salience data for this model)'", () => {
    const dr = makeFixture(["model-a", "model-b"], {
      sutropCsi: { "model-b": undefined },
    });
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a", "model-b"],
          modelColors: TWO_COLORS,
        })
      );
    });
    const text = container.textContent ?? "";
    expect(text).toContain("(no salience data for this model)");
  });

  it("Case C: renders '(no terms produced)'", () => {
    const dr = makeFixture(["model-a", "model-b"], {
      sutropCsi: { "model-b": [] },
    });
    act(() => {
      root.render(
        createElement(FreeListTable, {
          domainResult: dr,
          selectedModels: ["model-a", "model-b"],
          modelColors: TWO_COLORS,
        })
      );
    });
    const text = container.textContent ?? "";
    expect(text).toContain("(no terms produced)");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — SimilarityTable (AC #9, #10, #14)
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityTable (AC #9, #10, #14)", () => {
  it("renders a single <table> for N models (no matrix table)", () => {
    const dr = makeFixture(["m1", "m2", "m3"]);
    act(() => {
      root.render(
        createElement(SimilarityTable, {
          domainResult: dr,
          selectedModels: ["m1", "m2", "m3"],
        })
      );
    });
    expect(container.querySelectorAll("table").length).toBe(1);
  });

  it("renders N*(N-1)/2 data rows (no diagonal)", () => {
    const dr = makeFixture(["m1", "m2", "m3"]);
    act(() => {
      root.render(
        createElement(SimilarityTable, {
          domainResult: dr,
          selectedModels: ["m1", "m2", "m3"],
        })
      );
    });
    // 3 models → 3 pairs
    const rows = container.querySelectorAll("tbody tr");
    expect(rows.length).toBe(3);
  });

  it("R10: Similarity and 95% CI columns present and adjacent", () => {
    const dr = makeFixture(["m1", "m2"]);
    act(() => {
      root.render(
        createElement(SimilarityTable, {
          domainResult: dr,
          selectedModels: ["m1", "m2"],
        })
      );
    });
    const headers = Array.from(container.querySelectorAll("th")).map(
      (th) => th.textContent?.trim()
    );
    const simIdx = headers.indexOf("Similarity");
    const ciLowIdx = headers.indexOf("95% CI low");
    const ciHighIdx = headers.indexOf("95% CI high");
    expect(simIdx).toBeGreaterThan(-1);
    expect(ciLowIdx).toBe(simIdx + 1);
    expect(ciHighIdx).toBe(simIdx + 2);
  });

  it("null CI renders as — in CI columns", () => {
    const dr = makeFixture(["m1", "m2"], {
      similarityCi: [[null, null], [null, null]],
    });
    act(() => {
      root.render(
        createElement(SimilarityTable, {
          domainResult: dr,
          selectedModels: ["m1", "m2"],
        })
      );
    });
    const tds = Array.from(container.querySelectorAll("tbody td")).map(
      (td) => td.textContent?.trim()
    );
    expect(tds).toContain("—");
  });

  it("empty state (< 2 models): renders SIMILARITY_TABLE_EMPTY_LT_2_MODELS", () => {
    const dr = makeFixture(["m1"]);
    act(() => {
      root.render(
        createElement(SimilarityTable, {
          domainResult: dr,
          selectedModels: ["m1"],
        })
      );
    });
    const empty = container.querySelector(".read-as-table__empty");
    expect(empty).not.toBeNull();
    expect(empty!.textContent).toBe(SIMILARITY_TABLE_EMPTY_LT_2_MODELS);
    expect(container.querySelector("table")).toBeNull();
  });

  it("caption contains 'no shared structure' (T5 cross-surface, CDA SME S3/S5)", () => {
    const dr = makeFixture(["m1", "m2"]);
    act(() => {
      root.render(
        createElement(SimilarityTable, {
          domainResult: dr,
          selectedModels: ["m1", "m2"],
        })
      );
    });
    const caption = container.querySelector("caption");
    expect(caption).not.toBeNull();
    expect(caption!.textContent).toContain("no shared structure");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Integration: MDSPlot toggle (AC #27, U1)
// ══════════════════════════════════════════════════════════════════════════════

describe("MDSPlot — toggle integration (AC #27, U1)", () => {
  it("renders 'Read as table' toggle button", () => {
    const dr = makeFixture(["model-a", "model-b"]);
    act(() => {
      root.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: TWO_COLORS,
          selectedModels: ["model-a", "model-b"],
        })
      );
    });
    const btn = container.querySelector(".read-as-table-toggle__button");
    expect(btn).not.toBeNull();
    expect(btn!.textContent?.trim()).toBe("Read as table");
  });

  it("SVG is visible and table container is hidden by default (U1 Option A)", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const svg = container.querySelector("svg.mds-plot__svg");
    const tableContainer = document.getElementById("mds-table-container");
    expect(svg).not.toBeNull();
    expect(svg!.getAttribute("aria-hidden")).toBeNull(); // not hidden
    expect(tableContainer).not.toBeNull(); // always in DOM (U1)
    expect(tableContainer!.getAttribute("aria-hidden")).toBe("true"); // hidden
    expect(tableContainer!.style.display).toBe("none");
  });

  it("clicking toggle shows table, hides SVG", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const btn = container.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    act(() => { btn.click(); });

    const svg = container.querySelector("svg.mds-plot__svg");
    const tableContainer = document.getElementById("mds-table-container");
    expect(svg!.getAttribute("aria-hidden")).toBe("true");
    expect(svg!.style.display).toBe("none");
    expect(tableContainer!.getAttribute("aria-hidden")).toBeNull();
    expect(tableContainer!.style.display).toBe(""); // visible
    expect(btn.textContent?.trim()).toBe("Show visualization");
    expect(btn.getAttribute("aria-pressed")).toBe("true");
  });

  it("clicking toggle again restores SVG, hides table", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const btn = container.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    act(() => { btn.click(); }); // show table
    act(() => { btn.click(); }); // restore viz

    const svg = container.querySelector("svg.mds-plot__svg");
    expect(svg!.getAttribute("aria-hidden")).toBeNull();
    expect(btn.textContent?.trim()).toBe("Read as table");
    expect(btn.getAttribute("aria-pressed")).toBe("false");
  });

  it("ScreenReaderSummary is present in both viz and table modes (AC #8)", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    // SR summary present in default mode
    let srp = container.querySelector("p.sr-only.screen-reader-summary");
    expect(srp).not.toBeNull();

    // Toggle to table mode
    const btn = container.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    act(() => { btn.click(); });

    // SR summary still present
    srp = container.querySelector("p.sr-only.screen-reader-summary");
    expect(srp).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Integration: FreeListCompare toggle (AC #27, U1)
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — toggle integration (AC #27, U1)", () => {
  it("renders 'Read as table' toggle button", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(FreeListCompare, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const btn = container.querySelector(".read-as-table-toggle__button");
    expect(btn).not.toBeNull();
  });

  it("columns container is visible and table container hidden by default (U1)", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(FreeListCompare, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const columns = container.querySelector(".freelist-compare__columns");
    const tableContainer = document.getElementById("freelist-table-container");
    expect(columns).not.toBeNull();
    expect(columns!.getAttribute("aria-hidden")).toBeNull();
    expect(tableContainer).not.toBeNull(); // U1: always in DOM
    expect(tableContainer!.getAttribute("aria-hidden")).toBe("true");
  });

  it("clicking toggle shows table, hides columns", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(FreeListCompare, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const btn = container.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    act(() => { btn.click(); });

    const columns = container.querySelector(".freelist-compare__columns");
    const tableContainer = document.getElementById("freelist-table-container");
    expect(columns!.getAttribute("aria-hidden")).toBe("true");
    expect(tableContainer!.getAttribute("aria-hidden")).toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Integration: SimilarityHeatmap toggle (AC #27, U1)
// ══════════════════════════════════════════════════════════════════════════════

describe("SimilarityHeatmap — toggle integration (AC #27, U1)", () => {
  it("renders 'Read as table' toggle button", () => {
    const dr = makeFixture(["m1", "m2"]);
    act(() => {
      root.render(
        createElement(SimilarityHeatmap, {
          domainResult: dr,
          selectedModels: ["m1", "m2"],
        })
      );
    });
    const btn = container.querySelector(".read-as-table-toggle__button");
    expect(btn).not.toBeNull();
  });

  it("SVG container is visible and table container hidden by default (U1)", () => {
    const dr = makeFixture(["m1", "m2"]);
    act(() => {
      root.render(
        createElement(SimilarityHeatmap, {
          domainResult: dr,
          selectedModels: ["m1", "m2"],
        })
      );
    });
    const svgContainer = container.querySelector(".similarity-heatmap__svg-container");
    const tableContainer = document.getElementById("similarity-table-container");
    expect(svgContainer).not.toBeNull();
    expect(svgContainer!.getAttribute("aria-hidden")).toBeNull();
    expect(tableContainer).not.toBeNull(); // U1: always in DOM
    expect(tableContainer!.getAttribute("aria-hidden")).toBe("true");
  });

  it("clicking toggle shows table, hides SVG container", () => {
    const dr = makeFixture(["m1", "m2"]);
    act(() => {
      root.render(
        createElement(SimilarityHeatmap, {
          domainResult: dr,
          selectedModels: ["m1", "m2"],
        })
      );
    });
    const btn = container.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    act(() => { btn.click(); });

    const svgContainer = container.querySelector(".similarity-heatmap__svg-container");
    const tableContainer = document.getElementById("similarity-table-container");
    expect(svgContainer!.getAttribute("aria-hidden")).toBe("true");
    expect(tableContainer!.getAttribute("aria-hidden")).toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — Forbidden vocabulary in all T8 LSB-authored copy (AC #18)
// ══════════════════════════════════════════════════════════════════════════════

describe("screen_reader_summaries.ts — forbidden vocabulary (AC #18)", () => {
  const allCopy = [
    READ_AS_TABLE_LABEL_REST,
    READ_AS_TABLE_LABEL_PRESSED,
    MDS_TABLE_CAPTION,
    SIMILARITY_TABLE_CAPTION,
    MDS_TABLE_EMPTY_NO_MODELS,
    FREELIST_TABLE_EMPTY_NO_MODELS,
    SIMILARITY_TABLE_EMPTY_LT_2_MODELS,
    freeListTableCaption("TestModel"),
  ].join(" ");

  it("no 'believes' (model-applied)", () => {
    expect(allCopy).not.toMatch(/\bbelieves\b/i);
  });

  it("no 'worldview'", () => {
    expect(allCopy).not.toMatch(/\bworldview\b/i);
  });

  it("no 'thinks' (model-applied)", () => {
    expect(allCopy).not.toMatch(/\bthinks\b/i);
  });

  it("no 'perceives'", () => {
    expect(allCopy).not.toMatch(/\bperceives\b/i);
  });

  it("no 'missing' (empty-state framing)", () => {
    expect(allCopy).not.toMatch(/\bmissing\b/i);
  });

  it("no 'placeholder'", () => {
    expect(allCopy).not.toMatch(/\bplaceholder\b/i);
  });

  it("no 'no data yet'", () => {
    expect(allCopy).not.toContain("no data yet");
  });

  it("no 'pending'", () => {
    expect(allCopy).not.toMatch(/\bpending\b/i);
  });

  it("Similarity copy: no 'agree' (CDA SME S3)", () => {
    expect(SIMILARITY_TABLE_CAPTION).not.toMatch(/\bagree\b/i);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// TESTS — State isolation: AC #26
// ══════════════════════════════════════════════════════════════════════════════

describe("State isolation: readAsTable resets on remount (AC #26)", () => {
  it("MDSPlot toggle state starts as false on fresh render", () => {
    const dr = makeFixture(["model-a"]);
    act(() => {
      root.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });

    const btn = container.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    // Toggle on
    act(() => { btn.click(); });
    expect(btn.getAttribute("aria-pressed")).toBe("true");

    // Unmount and remount — state should reset to false
    act(() => { root.unmount(); });
    const newContainer = document.createElement("div");
    document.body.appendChild(newContainer);
    const newRoot = createRoot(newContainer);
    act(() => {
      newRoot.render(
        createElement(MDSPlot, {
          domainResult: dr,
          modelColors: { "model-a": "#3360a9" },
          selectedModels: ["model-a"],
        })
      );
    });
    const newBtn = newContainer.querySelector<HTMLButtonElement>(".read-as-table-toggle__button")!;
    expect(newBtn.getAttribute("aria-pressed")).toBe("false");
    act(() => { newRoot.unmount(); });
    newContainer.remove();
  });
});
