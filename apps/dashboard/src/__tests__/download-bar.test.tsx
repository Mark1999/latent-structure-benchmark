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
 * T11 acceptance criteria (PNG export):
 *   - PNG (social) button rendered with correct aria-label.
 *   - PNG hi-res button rendered with correct aria-label.
 *   - PNG button click invokes renderToPng (mocked).
 *   - PNG button click invokes injectTextMetadata (mocked).
 *   - PNG download triggered via temporary <a> element.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10, T11
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { DownloadBar } from "../components/DownloadBar";
import type { DomainResultPublished, WithinModelResult, EllipseParams, R1State } from "../data/types";

// ── Module mocks for PNG export (T11) ─────────────────────────────────────────

// We mock png-export and png-metadata so no real canvas or PNG parsing occurs.
vi.mock("../lib/png-export", () => ({
  renderToPng: vi.fn().mockResolvedValue(
    new Blob([new Uint8Array([0x89, 0x50])], { type: "image/png" })
  ),
}));

vi.mock("../lib/png-metadata", () => ({
  injectTextMetadata: vi.fn().mockImplementation(
    async (blob: Blob) => blob // pass-through
  ),
}));

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

beforeEach(async () => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);

  // Clear PNG export mocks between tests so call counts are per-test.
  const { renderToPng } = await import("../lib/png-export");
  const { injectTextMetadata } = await import("../lib/png-metadata");
  (renderToPng as ReturnType<typeof vi.fn>).mockClear();
  (injectTextMetadata as ReturnType<typeof vi.fn>).mockClear();

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
  it("renders four buttons (CSV, permalink, PNG social, PNG hi-res)", () => {
    const fixture = makeFixture(["model-a", "model-b"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const buttons = container.querySelectorAll("button");
    // CSV + permalink + png-social + png-hires = 4
    expect(buttons).toHaveLength(4);
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

// ── T11: PNG export tests ──────────────────────────────────────────────────────

describe("DownloadBar — PNG button presence (T11)", () => {
  it("renders a PNG social button", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const pngBtn = container.querySelector(".download-bar__png-btn");
    expect(pngBtn).not.toBeNull();
  });

  it("renders a PNG hi-res button", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const hiresBtn = container.querySelector(".download-bar__png-hires-btn");
    expect(hiresBtn).not.toBeNull();
  });

  it("PNG group has three buttons total (CSV, permalink, PNG social, PNG hires)", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const buttons = container.querySelectorAll("button");
    // CSV + permalink + png-social + png-hires = 4
    expect(buttons.length).toBe(4);
  });
});

describe("DownloadBar — PNG ARIA labels (T11)", () => {
  it("PNG social button has aria-label containing 'PNG' and 'social'", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const pngBtn = container.querySelector(".download-bar__png-btn");
    const label = pngBtn?.getAttribute("aria-label") ?? "";
    expect(label).toContain("PNG");
    expect(label.toLowerCase()).toContain("social");
  });

  it("PNG hi-res button has aria-label containing 'PNG' and 'hi-res'", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );
    const hiresBtn = container.querySelector(".download-bar__png-hires-btn");
    const label = hiresBtn?.getAttribute("aria-label") ?? "";
    expect(label).toContain("PNG");
    expect(label.toLowerCase()).toContain("hi-res");
  });
});

describe("DownloadBar — PNG button click invokes renderToPng + injectTextMetadata (T11)", () => {
  it("PNG social button click calls renderToPng with size='social'", async () => {
    const { renderToPng } = await import("../lib/png-export");

    // Add an SVG to the DOM so findSvg() succeeds.
    const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgEl.setAttribute("role", "img");
    document.body.appendChild(svgEl);

    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );

    const pngBtn = container.querySelector<HTMLButtonElement>(".download-bar__png-btn");
    expect(pngBtn).not.toBeNull();

    await act(async () => {
      pngBtn!.click();
      // Allow async handler to resolve.
      await Promise.resolve();
    });

    expect(renderToPng).toHaveBeenCalledWith(
      expect.any(SVGElement),
      { size: "social" }
    );

    document.body.removeChild(svgEl);
  });

  it("PNG social button click calls injectTextMetadata with domain/models fields", async () => {
    const { injectTextMetadata } = await import("../lib/png-metadata");

    const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgEl.setAttribute("role", "img");
    document.body.appendChild(svgEl);

    const fixture = makeFixture(["model-a", "model-b"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a", "model-b"],
        activeVizTab: "mds",
      })
    );

    const pngBtn = container.querySelector<HTMLButtonElement>(".download-bar__png-btn");
    await act(async () => {
      pngBtn!.click();
      await Promise.resolve();
    });

    expect(injectTextMetadata).toHaveBeenCalled();
    const kvArg = (injectTextMetadata as ReturnType<typeof vi.fn>).mock.calls[0][1] as Record<string, string>;
    expect(kvArg["Domain"]).toBe("family");
    expect(kvArg["Models"]).toContain("model-a");
    expect(kvArg["Models"]).toContain("model-b");
    expect(kvArg["Analysis-Version"]).toBe("0.2");

    document.body.removeChild(svgEl);
  });

  it("PNG hi-res button click calls renderToPng with size='highres'", async () => {
    const { renderToPng } = await import("../lib/png-export");
    (renderToPng as ReturnType<typeof vi.fn>).mockClear();

    const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgEl.setAttribute("role", "img");
    document.body.appendChild(svgEl);

    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );

    const hiresBtn = container.querySelector<HTMLButtonElement>(".download-bar__png-hires-btn");
    await act(async () => {
      hiresBtn!.click();
      await Promise.resolve();
    });

    expect(renderToPng).toHaveBeenCalledWith(
      expect.any(SVGElement),
      { size: "highres" }
    );

    document.body.removeChild(svgEl);
  });
});

describe("DownloadBar — PNG download triggers <a> element (T11)", () => {
  it("PNG button click appends and clicks a link element with download attribute", async () => {
    const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgEl.setAttribute("role", "img");
    document.body.appendChild(svgEl);

    // Spy on appendChild to detect the temporary download link.
    const appendSpy = vi.spyOn(document.body, "appendChild");

    const fixture = makeFixture(["model-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-a"],
        activeVizTab: "mds",
      })
    );

    const pngBtn = container.querySelector<HTMLButtonElement>(".download-bar__png-btn");
    await act(async () => {
      pngBtn!.click();
      await Promise.resolve();
    });

    // Find the <a> element appended by downloadBlob.
    const appendedLinks = appendSpy.mock.calls
      .map((c) => c[0])
      .filter((el): el is HTMLAnchorElement => el instanceof HTMLAnchorElement);
    expect(appendedLinks.length).toBeGreaterThan(0);
    const link = appendedLinks[appendedLinks.length - 1];
    expect(link.getAttribute("download")).toContain("family");
    expect(link.getAttribute("download")).toContain(".png");

    document.body.removeChild(svgEl);
    appendSpy.mockRestore();
  });
});
