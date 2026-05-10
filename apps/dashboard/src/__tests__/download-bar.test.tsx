// @vitest-environment jsdom
/**
 * DownloadBar component tests.
 *
 * T10 acceptance criteria:
 *   - Renders CSV button + permalink button.
 *   - CSV button has correct aria-label.
 *   - Permalink button click triggers navigator.clipboard.writeText (mocked).
 *   - Buttons are keyboard accessible (have type="button", role inferred).
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { DownloadBar } from "../components/DownloadBar";
import type { DomainResultPublished, WithinModelResult, EllipseParams, R1State } from "../data/types";

// ── Fixture builder ───────────────────────────────────────────────────────────

function makeFixture(modelIds: string[]): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, EllipseParams | null> = {};
  const r1_states: Record<string, R1State> = {};
  const top_terms: Record<string, string[]> = {};
  const within_model_results: WithinModelResult[] = [];

  modelIds.forEach((id, i) => {
    mds_coordinates[id] = [(i - modelIds.length / 2) * 0.1, (i % 3 - 1) * 0.1];
    r1_states[id] = "typical_concentration";
    top_terms[id] = ["a", "b"];
    mds_uncertainty[id] = {
      semi_major: 0.08,
      semi_minor: 0.04,
      rotation_rad: 0.5,
      n_bootstrap: 500,
      ci_level: 0.95,
    };
    within_model_results.push({
      model_id: id,
      n_runs: 5,
      oci: 50.0,
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

  return {
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
    free_lists: {},
    mds_coordinates: mds_coordinates as unknown as Record<string, [[number, number]]>,
    mds_uncertainty,
    similarity_matrix: {},
    similarity_ci: {},
    consensus_score: 0.8,
    consensus_ci: [0.7, 0.9],
    consensus_type: "STRONG_CONSENSUS",
    sutrop_csi: {},
    within_model_results,
    groundings: [],
    generated_lede: "Test lede.",
    generated_at: "2026-05-07T00:07:50.238646Z",
    romney_small_n_warning: true,
    display: { r1_states, top_terms, top_terms_metric: "sutrop_csi" },
  };
}

// ── Test setup ────────────────────────────────────────────────────────────────

let container: HTMLElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);

  // Mock navigator.clipboard.writeText
  Object.defineProperty(navigator, "clipboard", {
    value: {
      writeText: vi.fn().mockResolvedValue(undefined),
    },
    writable: true,
    configurable: true,
  });
});

afterEach(() => {
  act(() => {
    root.unmount();
  });
  document.body.removeChild(container);
  vi.restoreAllMocks();
});

function render(element: React.ReactElement): void {
  act(() => {
    root.render(element);
  });
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("DownloadBar — button presence", () => {
  it("renders two buttons", () => {
    const fixture = makeFixture(["model-a", "model-b"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const buttons = container.querySelectorAll("button");
    expect(buttons).toHaveLength(2);
  });

  it("renders a CSV download button", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const csvBtn = container.querySelector(".download-bar__csv-btn");
    expect(csvBtn).not.toBeNull();
  });

  it("renders a permalink button", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const permalinkBtn = container.querySelector(".download-bar__permalink-btn");
    expect(permalinkBtn).not.toBeNull();
  });
});

describe("DownloadBar — ARIA labels", () => {
  it("CSV button has correct aria-label containing domain slug", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const csvBtn = container.querySelector(".download-bar__csv-btn");
    expect(csvBtn?.getAttribute("aria-label")).toContain("family");
    expect(csvBtn?.getAttribute("aria-label")).toContain("CSV");
  });

  it("Permalink button has aria-label", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const permalinkBtn = container.querySelector(".download-bar__permalink-btn");
    expect(permalinkBtn?.getAttribute("aria-label")).toBeTruthy();
    expect(permalinkBtn?.getAttribute("aria-label")).toContain("permalink");
  });
});

describe("DownloadBar — keyboard accessibility", () => {
  it("all buttons have type='button' (not submit)", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const buttons = container.querySelectorAll("button");
    buttons.forEach((btn) => {
      expect(btn.getAttribute("type")).toBe("button");
    });
  });

  it("buttons are not disabled", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const buttons = container.querySelectorAll("button");
    buttons.forEach((btn) => {
      expect(btn.disabled).toBe(false);
    });
  });
});

describe("DownloadBar — permalink click", () => {
  it("calls navigator.clipboard.writeText on permalink button click", async () => {
    const fixture = makeFixture(["model-a", "model-b"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const permalinkBtn = container.querySelector<HTMLButtonElement>(".download-bar__permalink-btn");
    expect(permalinkBtn).not.toBeNull();

    await act(async () => {
      permalinkBtn!.click();
    });

    expect(navigator.clipboard.writeText).toHaveBeenCalledOnce();
    // The written URL should contain the domain slug and model id.
    const writtenUrl = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    expect(writtenUrl).toContain("family");
    expect(writtenUrl).toContain("model-a");
  });

  it("permalink URL contains #mds fragment", async () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const permalinkBtn = container.querySelector<HTMLButtonElement>(".download-bar__permalink-btn");

    await act(async () => {
      permalinkBtn!.click();
    });

    const writtenUrl = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    expect(writtenUrl).toContain("#mds");
  });

  it("shows 'Copied!' feedback after click", async () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const permalinkBtn = container.querySelector<HTMLButtonElement>(".download-bar__permalink-btn");

    await act(async () => {
      permalinkBtn!.click();
    });

    expect(container.textContent).toContain("Copied!");
  });
});
