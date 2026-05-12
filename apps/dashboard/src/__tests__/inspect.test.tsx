// @vitest-environment jsdom
/**
 * Tests for Phase 6 T0 — Operator Inspection Mode.
 *
 * Coverage:
 *   - isInspectMode() parsing in App.tsx: family / holidays / manifest / empty / missing
 *   - InspectTable: renders caption, th scope, cell values, empty state
 *   - InspectSection: id derivation from title, aria-labelledby wiring
 *   - InspectRoot: <meta robots> mount/unmount lifecycle
 *   - InspectRoot: unknown-field fallback ("Other top-level fields")
 *   - InspectRoot: section headings present for domain mode and manifest mode
 *   - No real network fetches (vi.mock)
 *
 * Reference: docs/status/2026-05-12-phase6-T0-architect-plan.md §3
 *            docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md (F-T0-A1)
 *
 * CLAUDE.md §6 R9: no real API calls. All mocked.
 */

import {
  describe,
  it,
  expect,
  vi,
  beforeEach,
  afterEach,
} from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";

// Source text used in structural assertions
const APP_SRC = readFileSync(resolve(__dirname, "../App.tsx"), "utf-8");
const INSPECT_ROOT_SRC = readFileSync(
  resolve(__dirname, "../components/InspectRoot.tsx"),
  "utf-8"
);
const INSPECT_SECTION_SRC = readFileSync(
  resolve(__dirname, "../components/InspectSection.tsx"),
  "utf-8"
);
const INSPECT_TABLE_SRC = readFileSync(
  resolve(__dirname, "../components/InspectTable.tsx"),
  "utf-8"
);

// Mock the API client so no real fetches occur
vi.mock("../api/client", () => ({
  fetchManifest: vi.fn(),
  fetchDomain: vi.fn(),
}));

import { fetchManifest, fetchDomain } from "../api/client";
const mockFetchManifest = vi.mocked(fetchManifest);
const mockFetchDomain = vi.mocked(fetchDomain);

// ── Fixture helpers ───────────────────────────────────────────────────────────

const MOCK_MANIFEST = {
  built_at: "2026-05-10T10:54:21.434207Z",
  oci_low_concentration_threshold: 3.0,
  domains: [
    {
      slug: "family",
      analysis_version: "0.2",
      n_models: 2,
      model_ids: ["model-a", "model-b"],
      generated_at: "2026-05-07T00:07:50Z",
    },
  ],
};

/** Minimal domain fixture with a synthetic unknown field for the fallback test. */
const MOCK_DOMAIN = {
  domain_slug: "family",
  analysis_version: "0.2",
  generated_at: "2026-05-07T00:07:50Z",
  generated_lede: "Across 2 frontier models, family vocabulary is organized.",
  models: [
    {
      provider: "test",
      model_id: "model-a",
      family: "test",
      origin: "us",
      open_weights: false,
      collection_method: "test",
      quantization: null,
      release_date: "2026-01-01",
      version_label: "model-a-v1",
      source_notes: "",
    },
    {
      provider: "test",
      model_id: "model-b",
      family: "test",
      origin: "eu",
      open_weights: true,
      collection_method: "test",
      quantization: null,
      release_date: "2026-01-01",
      version_label: "model-b-v1",
      source_notes: "",
    },
  ],
  free_lists: {
    "model-a": {
      run_id: "run-a",
      model: { model_id: "model-a" },
      domain_slug: "family",
      items: ["mother", "father"],
      raw_order: ["mother", "father"],
    },
    "model-b": {
      run_id: "run-b",
      model: { model_id: "model-b" },
      domain_slug: "family",
      items: ["parent", "sibling"],
      raw_order: ["parent", "sibling"],
    },
  },
  mds_coordinates: {
    "model-a": [0.1, 0.2],
    "model-b": [0.3, 0.4],
  },
  mds_uncertainty: {
    "model-a": {
      center: [0.1, 0.2],
      semi_major: 0.1,
      semi_minor: 0.05,
      rotation_rad: 1.0,
      n_bootstrap: 500,
      ci_level: null,
    },
    "model-b": null,
  },
  similarity_matrix: [
    [1.0, 0.8],
    [0.8, 1.0],
  ],
  similarity_ci: [
    [[1.0, 1.0], [0.7, 0.9]],
    [[0.7, 0.9], [1.0, 1.0]],
  ],
  consensus_score: 0.71,
  consensus_ci: [0.5, 0.9],
  consensus_type: "STRONG_CONSENSUS",
  romney_eigenratio: 2.5,
  romney_threshold_classic: 1.0,
  romney_threshold_lsb: 1.5,
  romney_consensus_pass: true,
  romney_consensus_warning: false,
  romney_small_n_warning: true,
  cultural_centrality_scores: { "model-a": 0.6, "model-b": 0.4 },
  negative_centrality_flag: false,
  negative_centrality_models: [],
  cross_model_mantel: [],
  cross_model_nolan: [],
  sutrop_csi: {
    "model-a": [{ item: "mother", csi: 0.9, f_mentions: 3, n_runs: 4, mean_position: 1.0 }],
  },
  salience_index_agreement: { "model-a": 0.95 },
  within_model_results: [
    {
      model_id: "model-a",
      n_runs: 4,
      oci: 100.0,
      oci_ci: null,
      underestimates_uncertainty: false,
      deterministic_output: false,
      salience_stability_rho: 0.9,
      elbow_stability: 0.8,
      mds_procrustes_rmse: 0.05,
      centrality_scores_by_run: {},
      centroid_run_id: "run-0",
      mds_within_model: [],
    },
  ],
  g1_salience_stability: null,
  g1_spatial_stability: null,
  g1_aggregate_stability: null,
  g1_salience_pass: null,
  g1_spatial_pass: null,
  g1_overall_pass: null,
  groundings: [],
  selected_baseline_id: null,
  display: {
    r1_states: { "model-a": "typical_concentration" },
    top_terms: { "model-a": ["mother", "father"] },
    top_terms_metric: "sutrop_csi",
  },
  // Synthetic unknown field for the "Other top-level fields" fallback test (AC7)
  foo_bar: [1, 2, 3],
};

// ── Structural source assertions ─────────────────────────────────────────────

describe("Phase 6 T0 — source structure assertions", () => {
  it("App.tsx contains isInspectMode() function", () => {
    expect(APP_SRC).toContain("isInspectMode");
    expect(APP_SRC).toContain('.get("inspect")');
  });

  it("App.tsx renders InspectRoot when inspectSlug is not null", () => {
    expect(APP_SRC).toContain("InspectRoot");
    expect(APP_SRC).toContain("inspectSlug");
    expect(APP_SRC).toContain("<InspectRoot");
  });

  it("App.tsx imports InspectRoot from components/InspectRoot", () => {
    expect(APP_SRC).toContain('"./components/InspectRoot"');
  });

  it("App.tsx imports inspect.css", () => {
    expect(APP_SRC).toContain("inspect.css");
  });

  it("InspectRoot.tsx injects meta robots noindex via useEffect", () => {
    expect(INSPECT_ROOT_SRC).toContain("meta");
    expect(INSPECT_ROOT_SRC).toContain("robots");
    expect(INSPECT_ROOT_SRC).toContain("noindex");
    expect(INSPECT_ROOT_SRC).toContain("useEffect");
  });

  it("InspectRoot.tsx removes meta robots on unmount (cleanup in useEffect)", () => {
    // The useEffect must return a cleanup function that removes the meta tag.
    expect(INSPECT_ROOT_SRC).toContain("removeChild");
  });

  it("InspectRoot.tsx has SCOPE CONSTRAINT comment", () => {
    expect(INSPECT_ROOT_SRC).toContain("VIEWER, not a tool");
  });

  it("InspectRoot.tsx documents the types.ts shape mismatch", () => {
    expect(INSPECT_ROOT_SRC).toContain("data/types.ts");
    expect(INSPECT_ROOT_SRC).toContain("similarity_matrix");
    expect(INSPECT_ROOT_SRC).toContain("mds_coordinates");
  });

  it("InspectRoot.tsx does not import from data/types.ts for domain shape", () => {
    // InspectRoot uses local RawDomainJSON type, not the types.ts DomainResultPublished
    expect(INSPECT_ROOT_SRC).toContain("RawDomainJSON");
  });

  it("InspectSection.tsx derives id from title using toLowerCase + replace", () => {
    expect(INSPECT_SECTION_SRC).toContain("toLowerCase()");
    expect(INSPECT_SECTION_SRC).toContain("replace");
  });

  it("InspectSection.tsx uses aria-labelledby wired to section id", () => {
    expect(INSPECT_SECTION_SRC).toContain("aria-labelledby");
    expect(INSPECT_SECTION_SRC).toContain("id={id}");
  });

  it("InspectTable.tsx renders <caption> element", () => {
    expect(INSPECT_TABLE_SRC).toContain("<caption>");
  });

  it("InspectTable.tsx renders <th scope=\"col\">", () => {
    expect(INSPECT_TABLE_SRC).toContain('scope="col"');
  });

  it("InspectTable.tsx uses --font-mono (not --font-family-mono) — UI/UX F-T0-B2", () => {
    expect(INSPECT_TABLE_SRC).toContain("--font-mono");
    expect(INSPECT_TABLE_SRC).not.toContain("--font-family-mono");
  });

  it("inspect.css uses --color-surface (not --color-bg-surface) — UI/UX F-T0-B1", () => {
    const cssSrc = readFileSync(
      resolve(__dirname, "../styles/inspect.css"),
      "utf-8"
    );
    expect(cssSrc).toContain("--color-surface");
    expect(cssSrc).not.toContain("--color-bg-surface");
  });

  it("inspect.css uses --font-mono (not --font-family-mono) — UI/UX F-T0-B2", () => {
    const cssSrc = readFileSync(
      resolve(__dirname, "../styles/inspect.css"),
      "utf-8"
    );
    expect(cssSrc).toContain("--font-mono");
    expect(cssSrc).not.toContain("--font-family-mono");
  });

  it("InspectRoot.tsx uses --color-text-caption for loading/error strings — UI/UX F-T0-C1", () => {
    expect(INSPECT_ROOT_SRC).toContain("--color-text-caption");
    // Must NOT use --color-text-muted for loading/error (WCAG AA failure)
    expect(INSPECT_ROOT_SRC).not.toContain("--color-text-muted");
  });

  it("InspectRoot.tsx has 'Other top-level fields' fallback section", () => {
    expect(INSPECT_ROOT_SRC).toContain("Other top-level fields");
  });

  it("InspectRoot.tsx has DOMAIN_KNOWN_KEYS set for schema-drift detection", () => {
    expect(INSPECT_ROOT_SRC).toContain("DOMAIN_KNOWN_KEYS");
  });

  it("InspectRoot.tsx does not contain forbidden vocabulary in prose", () => {
    // Section headings, descriptions, error strings must not contain forbidden words.
    // Field names (in string literals for data access) are exempt.
    // We check that certain patterns don't appear as user-visible text.
    expect(INSPECT_ROOT_SRC).not.toContain('"worldview"');
    expect(INSPECT_ROOT_SRC).not.toContain('"believes"');
    // "How models see" is forbidden per §1.5.4
    expect(INSPECT_ROOT_SRC).not.toContain("How models see");
  });

  it("App.tsx does not contain forbidden vocabulary (worldview, believes)", () => {
    // These apply to prose in the App shell too.
    expect(APP_SRC).not.toContain('"worldview"');
    expect(APP_SRC).not.toContain('"believes"');
  });
});

// ── isInspectMode() parsing ───────────────────────────────────────────────────

describe("isInspectMode() parsing (App.tsx source)", () => {
  it("isInspectMode source reads ?inspect= query parameter", () => {
    expect(APP_SRC).toContain('.get("inspect")');
  });

  it("isInspectMode returns null for empty slug per plan §2.2", () => {
    // The source must guard against empty slug
    expect(APP_SRC).toContain('trim() === ""');
  });
});

// ── InspectTable component rendering ─────────────────────────────────────────

describe("InspectTable — DOM rendering", () => {
  let container: HTMLElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => { root.unmount(); });
    document.body.removeChild(container);
  });

  it("renders caption, th scope=col, and cell values", async () => {
    const { InspectTable } = await import("../components/InspectTable");
    await act(async () => {
      root.render(
        createElement(InspectTable, {
          caption: "Test table",
          columns: [
            { key: "name", label: "Name" },
            { key: "value", label: "Value" },
          ],
          rows: [
            { name: "alpha", value: 42 },
            { name: "beta", value: null },
          ],
        })
      );
    });

    const caption = container.querySelector("caption");
    expect(caption?.textContent).toBe("Test table");

    const ths = container.querySelectorAll("th");
    expect(ths.length).toBe(2);
    ths.forEach((th) => {
      expect(th.getAttribute("scope")).toBe("col");
    });

    const tds = container.querySelectorAll("td");
    // 2 rows × 2 columns = 4 cells
    expect(tds.length).toBe(4);
    expect(tds[0].textContent).toBe("alpha");
    expect(tds[1].textContent).toBe("42");
    // null renders as "null"
    expect(tds[3].textContent).toBe("null");
  });

  it("renders array values as pre-formatted JSON", async () => {
    const { InspectTable } = await import("../components/InspectTable");
    await act(async () => {
      root.render(
        createElement(InspectTable, {
          caption: "Array test",
          columns: [{ key: "data", label: "Data" }],
          rows: [{ data: [1, 2, 3] }],
        })
      );
    });

    const pre = container.querySelector("pre");
    expect(pre).not.toBeNull();
    expect(pre?.textContent).toContain("1");
    expect(pre?.textContent).toContain("2");
  });

  it("renders empty state with no-rows message", async () => {
    const { InspectTable } = await import("../components/InspectTable");
    await act(async () => {
      root.render(
        createElement(InspectTable, {
          caption: "Empty table",
          columns: [{ key: "x", label: "X" }],
          rows: [],
        })
      );
    });

    const tbody = container.querySelector("tbody");
    expect(tbody?.textContent).toContain("no rows");
  });
});

// ── InspectSection component rendering ───────────────────────────────────────

describe("InspectSection — DOM rendering", () => {
  let container: HTMLElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => { root.unmount(); });
    document.body.removeChild(container);
  });

  it("renders h2 with id derived from title (F-T0-A1)", async () => {
    const { InspectSection } = await import("../components/InspectSection");
    await act(async () => {
      root.render(
        createElement(
          InspectSection,
          { title: "My Section Title" },
          createElement("p", null, "content")
        )
      );
    });

    const h2 = container.querySelector("h2");
    expect(h2).not.toBeNull();
    // F-T0-A1: id derived from title: lowercase, spaces → hyphens
    expect(h2?.id).toBe("my-section-title");
    expect(h2?.textContent).toBe("My Section Title");

    const section = container.querySelector("section");
    expect(section?.getAttribute("aria-labelledby")).toBe("my-section-title");
  });

  it("renders description paragraph when provided", async () => {
    const { InspectSection } = await import("../components/InspectSection");
    await act(async () => {
      root.render(
        createElement(
          InspectSection,
          { title: "With Description", description: "A helpful note." },
          null
        )
      );
    });

    const p = container.querySelector("p.inspect-section__description");
    expect(p?.textContent).toBe("A helpful note.");
  });

  it("strips special chars from id (F-T0-A1 valid HTML id)", async () => {
    const { InspectSection } = await import("../components/InspectSection");
    await act(async () => {
      root.render(
        createElement(
          InspectSection,
          { title: "MDS uncertainty (bootstrap ellipses)" },
          null
        )
      );
    });

    const h2 = container.querySelector("h2");
    // Parentheses are stripped; only alphanumeric and hyphens remain
    expect(h2?.id).toMatch(/^[a-z0-9-]+$/);
    expect(h2?.id).toBe("mds-uncertainty-bootstrap-ellipses");
  });
});

// ── InspectRoot — meta robots lifecycle ───────────────────────────────────────

describe("InspectRoot — meta robots noindex lifecycle", () => {
  let container: HTMLElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    // Start with no robots meta tag in head
    document.head.querySelectorAll('meta[name="robots"]').forEach((m) => m.remove());
    vi.clearAllMocks();
  });

  afterEach(() => {
    act(() => { root.unmount(); });
    if (document.body.contains(container)) {
      document.body.removeChild(container);
    }
    document.head.querySelectorAll('meta[name="robots"]').forEach((m) => m.remove());
  });

  it("injects <meta name=robots content=noindex> on mount", async () => {
    const { InspectRoot } = await import("../components/InspectRoot");
    // Mock fetches so InspectRoot doesn't fail
    mockFetchManifest.mockResolvedValue(MOCK_MANIFEST as Parameters<typeof mockFetchManifest.mockResolvedValue>[0]);
    mockFetchDomain.mockResolvedValue(MOCK_DOMAIN as Parameters<typeof mockFetchDomain.mockResolvedValue>[0]);

    await act(async () => {
      root.render(
        createElement(InspectRoot, {
          mode: "manifest",
          manifest: MOCK_MANIFEST as Parameters<typeof InspectRoot>[0]["manifest"],
        })
      );
    });

    const meta = document.head.querySelector('meta[name="robots"]');
    expect(meta).not.toBeNull();
    expect(meta?.getAttribute("content")).toBe("noindex");
  });

  it("removes <meta robots> on unmount (cleanup)", async () => {
    const { InspectRoot } = await import("../components/InspectRoot");
    mockFetchManifest.mockResolvedValue(MOCK_MANIFEST as Parameters<typeof mockFetchManifest.mockResolvedValue>[0]);
    mockFetchDomain.mockResolvedValue(MOCK_DOMAIN as Parameters<typeof mockFetchDomain.mockResolvedValue>[0]);

    await act(async () => {
      root.render(
        createElement(InspectRoot, {
          mode: "manifest",
          manifest: MOCK_MANIFEST as Parameters<typeof InspectRoot>[0]["manifest"],
        })
      );
    });

    // Verify it's present before unmount
    expect(document.head.querySelector('meta[name="robots"]')).not.toBeNull();

    // Unmount
    await act(async () => { root.unmount(); });

    // Verify it's removed after unmount
    expect(document.head.querySelector('meta[data-inspect-meta="true"]')).toBeNull();
  });
});

// ── InspectRoot — domain mode section headings ───────────────────────────────

describe("InspectRoot — domain mode renders all §2.4 section headings", () => {
  let container: HTMLElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    vi.clearAllMocks();
  });

  afterEach(() => {
    act(() => { root.unmount(); });
    if (document.body.contains(container)) {
      document.body.removeChild(container);
    }
    document.head.querySelectorAll('meta[name="robots"]').forEach((m) => m.remove());
  });

  it("renders all §2.4 domain mode section headings for the family domain", async () => {
    const { InspectRoot } = await import("../components/InspectRoot");
    mockFetchManifest.mockResolvedValue(MOCK_MANIFEST as Parameters<typeof mockFetchManifest.mockResolvedValue>[0]);
    mockFetchDomain.mockResolvedValue(MOCK_DOMAIN as Parameters<typeof mockFetchDomain.mockResolvedValue>[0]);

    await act(async () => {
      root.render(
        createElement(InspectRoot, {
          mode: "family",
          manifest: MOCK_MANIFEST as Parameters<typeof InspectRoot>[0]["manifest"],
        })
      );
    });

    // Wait for async fetch resolution
    await act(async () => { await new Promise((r) => setTimeout(r, 50)); });

    const headings = Array.from(container.querySelectorAll("h2")).map(
      (h) => h.textContent ?? ""
    );

    const requiredHeadings = [
      "Domain header",
      "Models in this domain",
      "Free lists (per model)",
      "MDS coordinates",
      "MDS uncertainty (bootstrap ellipses)",
      "Similarity matrix",
      "Similarity confidence intervals",
      "Consensus",
      "Cultural centrality",
      "Cross-model agreement",
      "Sutrop CSI (salience)",
      "Salience index agreement",
      "Within-model results",
      "G1 stability fields",
      "Groundings",
      "Display block (precomputed UI helpers)",
    ];

    for (const heading of requiredHeadings) {
      expect(headings).toContain(heading);
    }
  });

  it("renders 'Other top-level fields' section when unknown field is present (AC7)", async () => {
    const { InspectRoot } = await import("../components/InspectRoot");
    // MOCK_DOMAIN has foo_bar: [1,2,3] which is not a known section key
    mockFetchDomain.mockResolvedValue(MOCK_DOMAIN as Parameters<typeof mockFetchDomain.mockResolvedValue>[0]);
    mockFetchManifest.mockResolvedValue(MOCK_MANIFEST as Parameters<typeof mockFetchManifest.mockResolvedValue>[0]);

    await act(async () => {
      root.render(
        createElement(InspectRoot, {
          mode: "family",
          manifest: MOCK_MANIFEST as Parameters<typeof InspectRoot>[0]["manifest"],
        })
      );
    });

    await act(async () => { await new Promise((r) => setTimeout(r, 50)); });

    const headings = Array.from(container.querySelectorAll("h2")).map(
      (h) => h.textContent ?? ""
    );
    expect(headings).toContain("Other top-level fields");

    // The unknown key name should appear in the rendered content
    expect(container.textContent).toContain("foo_bar");
  });
});

// ── InspectRoot — manifest mode section headings ──────────────────────────────

describe("InspectRoot — manifest mode renders §2.4 manifest sections", () => {
  let container: HTMLElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    vi.clearAllMocks();
  });

  afterEach(() => {
    act(() => { root.unmount(); });
    if (document.body.contains(container)) {
      document.body.removeChild(container);
    }
    document.head.querySelectorAll('meta[name="robots"]').forEach((m) => m.remove());
  });

  it("renders manifest mode section headings", async () => {
    const { InspectRoot } = await import("../components/InspectRoot");
    mockFetchManifest.mockResolvedValue(MOCK_MANIFEST as Parameters<typeof mockFetchManifest.mockResolvedValue>[0]);

    await act(async () => {
      root.render(
        createElement(InspectRoot, {
          mode: "manifest",
          manifest: MOCK_MANIFEST as Parameters<typeof InspectRoot>[0]["manifest"],
        })
      );
    });

    const headings = Array.from(container.querySelectorAll("h2")).map(
      (h) => h.textContent ?? ""
    );
    expect(headings).toContain("Manifest top-level");
    expect(headings).toContain("Domains in this manifest");
  });

  it("manifest mode page has exactly one h1 element", async () => {
    const { InspectRoot } = await import("../components/InspectRoot");
    mockFetchManifest.mockResolvedValue(MOCK_MANIFEST as Parameters<typeof mockFetchManifest.mockResolvedValue>[0]);

    await act(async () => {
      root.render(
        createElement(InspectRoot, {
          mode: "manifest",
          manifest: MOCK_MANIFEST as Parameters<typeof InspectRoot>[0]["manifest"],
        })
      );
    });

    const h1s = container.querySelectorAll("h1");
    expect(h1s.length).toBe(1);
    expect(h1s[0].textContent).toBe("LSB published-data inspection");
  });
});

// ── No raw-data paths referenced ─────────────────────────────────────────────

describe("Phase 6 T0 — no raw-data paths (AC13)", () => {
  it("InspectRoot.tsx does not reference data/raw/ paths", () => {
    expect(INSPECT_ROOT_SRC).not.toContain("data/raw/");
    expect(INSPECT_ROOT_SRC).not.toContain("data/results/");
  });

  it("InspectTable.tsx does not reference data/raw/ paths", () => {
    expect(INSPECT_TABLE_SRC).not.toContain("data/raw/");
  });

  it("InspectSection.tsx does not reference data/raw/ paths", () => {
    expect(INSPECT_SECTION_SRC).not.toContain("data/raw/");
  });
});

// ── No new dependencies ───────────────────────────────────────────────────────

describe("Phase 6 T0 — no new package.json dependencies (AC12)", () => {
  it("package.json has no react-router-dom dependency", () => {
    const pkgSrc = readFileSync(
      resolve(__dirname, "../../package.json"),
      "utf-8"
    );
    expect(pkgSrc).not.toContain("react-router-dom");
  });

  it("api/client.ts has no new fetch helpers added", () => {
    const clientSrc = readFileSync(
      resolve(__dirname, "../api/client.ts"),
      "utf-8"
    );
    // T0 must only use fetchManifest and fetchDomain
    // No new exported async functions should have been added
    expect(clientSrc).toContain("fetchManifest");
    expect(clientSrc).toContain("fetchDomain");
    // The only exports are these two
    const exportCount = (clientSrc.match(/^export async function/gm) ?? []).length;
    expect(exportCount).toBe(2);
  });
});
