// @vitest-environment jsdom
/**
 * SourceAttribution component tests.
 *
 * T10 acceptance criteria:
 *   - Renders model list, domain, prompt version, analysis version.
 *   - Renders collection month from generated_at.
 *   - Renders "+ N more" suffix when many models selected.
 *   - Renders small-n note when domainResult.romney_small_n_warning === true (Q2 binding).
 *   - Does NOT render small-n note when romney_small_n_warning === false.
 *   - No forbidden vocabulary in any rendered text.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 *         CDA SME plan-level Q2 binding (small-n surfacing)
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { SourceAttribution } from "../components/SourceAttribution";
import type { DomainResultPublished, WithinModelResult, EllipseParams, R1State } from "../data/types";

// ── Fixture builder ───────────────────────────────────────────────────────────

function makeFixture(
  modelIds: string[],
  options: {
    romney_small_n_warning?: boolean;
    generated_at?: string;
    domain_slug?: string;
    analysis_version?: string;
  } = {}
): DomainResultPublished {
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
    domain_slug: options.domain_slug ?? "family",
    analysis_version: options.analysis_version ?? "0.2",
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
    generated_at: options.generated_at ?? "2026-05-07T00:07:50.238646Z",
    romney_small_n_warning: options.romney_small_n_warning ?? false,
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
});

afterEach(() => {
  act(() => {
    root.unmount();
  });
  document.body.removeChild(container);
});

function render(element: React.ReactElement): void {
  act(() => {
    root.render(element);
  });
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("SourceAttribution — basic content", () => {
  it("renders the domain slug", () => {
    const fixture = makeFixture(["model-a", "model-b"], { domain_slug: "family" });
    render(createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] }));
    expect(container.textContent).toContain("family");
  });

  it("renders prompt version v1", () => {
    const fixture = makeFixture(["model-a"]);
    render(createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] }));
    expect(container.textContent).toContain("v1");
  });

  it("renders analysis version from domainResult.analysis_version", () => {
    const fixture = makeFixture(["model-a"], { analysis_version: "0.2" });
    render(createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] }));
    expect(container.textContent).toContain("v0.2");
  });

  it("renders 'Source:' label", () => {
    const fixture = makeFixture(["model-a"]);
    render(createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] }));
    expect(container.textContent).toContain("Source:");
  });

  it("renders 'Collected:' with month year from generated_at", () => {
    // generated_at: "2026-05-07T00:07:50.238646Z" → "May 2026"
    const fixture = makeFixture(["model-a"], { generated_at: "2026-05-07T00:07:50.238646Z" });
    render(createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] }));
    expect(container.textContent).toContain("May 2026");
  });

  it("renders 'Collected:' with April 2026 for April timestamp", () => {
    const fixture = makeFixture(["model-a"], { generated_at: "2026-04-15T12:00:00Z" });
    render(createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] }));
    expect(container.textContent).toContain("April 2026");
  });
});

describe("SourceAttribution — model list", () => {
  it("renders model short names from selectedModels", () => {
    const fixture = makeFixture(["claude-opus-4-6", "openai/gpt-5.4"]);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["claude-opus-4-6", "openai/gpt-5.4"],
      })
    );
    // "Claude Opus 4.6" is the short name for claude-opus-4-6
    expect(container.textContent).toContain("Claude Opus 4.6");
  });

  it("renders '+ N more' when selectedModels exceeds MAX_INLINE (4)", () => {
    const modelIds = [
      "claude-opus-4-6",
      "claude-sonnet-4-6",
      "openai/gpt-5.4",
      "openai/gpt-5.4-mini",
      "x-ai/grok-4",
      "microsoft/phi-4",
    ];
    const fixture = makeFixture(modelIds);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: modelIds,
      })
    );
    // 6 models with MAX_INLINE=4 → "+2 more"
    expect(container.textContent).toContain("+2 more");
  });

  it("does NOT render '+ N more' when selectedModels count <= MAX_INLINE (4)", () => {
    const fixture = makeFixture(["model-a", "model-b", "model-c"]);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["model-a", "model-b", "model-c"],
      })
    );
    expect(container.textContent).not.toContain("more");
  });

  it("renders exactly 4 inline names when 5 models selected", () => {
    const modelIds = [
      "claude-opus-4-6",
      "claude-sonnet-4-6",
      "openai/gpt-5.4",
      "openai/gpt-5.4-mini",
      "x-ai/grok-4",
    ];
    const fixture = makeFixture(modelIds);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: modelIds,
      })
    );
    // 5 models → 4 inline + "+1 more"
    expect(container.textContent).toContain("+1 more");
  });
});

describe("SourceAttribution — small-n note (Q2 binding)", () => {
  it("renders small-n note when romney_small_n_warning is true", () => {
    const fixture = makeFixture(
      ["model-a", "model-b", "model-c"],
      { romney_small_n_warning: true }
    );
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["model-a"],
      })
    );
    // Should render the small-n note
    expect(container.textContent).toContain("Small-n note");
    expect(container.textContent).toContain("n=15");
  });

  it("renders model count in small-n note", () => {
    const fixture = makeFixture(
      ["model-a", "model-b", "model-c"],
      { romney_small_n_warning: true }
    );
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["model-a"],
      })
    );
    // n=3 total models in fixture
    expect(container.textContent).toContain("n=3");
  });

  it("does NOT render small-n note when romney_small_n_warning is false", () => {
    const fixture = makeFixture(
      ["model-a", "model-b"],
      { romney_small_n_warning: false }
    );
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["model-a"],
      })
    );
    // No small-n note
    expect(container.textContent).not.toContain("Small-n note");
    expect(container.textContent).not.toContain("n=15 threshold");
  });

  it("small-n note has the source-attribution__small-n-note class", () => {
    const fixture = makeFixture(["m1"], { romney_small_n_warning: true });
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["m1"],
      })
    );
    const note = container.querySelector(".source-attribution__small-n-note");
    expect(note).not.toBeNull();
  });
});

describe("SourceAttribution — forbidden vocabulary", () => {
  it("does not contain 'believes' in rendered text", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] })
    );
    expect(container.textContent?.toLowerCase()).not.toContain("believes");
  });

  it("does not contain 'worldview' in rendered text", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] })
    );
    expect(container.textContent?.toLowerCase()).not.toContain("worldview");
  });

  it("does not contain 'thinks' in rendered text", () => {
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] })
    );
    expect(container.textContent?.toLowerCase()).not.toContain("thinks");
  });
});

// ── Gap-fill: v0.4.3 WCAG AA token + (N of M models shown) ───────────────────
// These tests target coverage gaps identified by the Tester agent at T10 review.

describe("SourceAttribution — v0.4.3 WCAG AA fix (--color-text-caption token)", () => {
  it("wrapper element uses --color-text-caption for its color style", () => {
    // The v0.4.3 fix replaced --color-text-muted (1.75:1) with --color-text-caption
    // (#6c757d, ~4.60:1) to pass WCAG AA for 12px body text.
    const fixture = makeFixture(["model-a"]);
    render(
      createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] })
    );
    const wrapper = container.querySelector<HTMLElement>(".source-attribution");
    expect(wrapper).not.toBeNull();
    // jsdom preserves the CSS variable reference string in element.style.color.
    expect(wrapper!.style.color).toBe("var(--color-text-caption)");
  });

  it("small-n note element uses --color-text-caption for its color style", () => {
    // The small-n footnote must also use --color-text-caption, not
    // --color-text-secondary (~3.40:1, insufficient for 12px italic).
    const fixture = makeFixture(["model-a"], { romney_small_n_warning: true });
    render(
      createElement(SourceAttribution, { domainResult: fixture, selectedModels: ["model-a"] })
    );
    const note = container.querySelector<HTMLElement>(".source-attribution__small-n-note");
    expect(note).not.toBeNull();
    expect(note!.style.color).toBe("var(--color-text-caption)");
  });
});

describe("SourceAttribution — (N of M models shown) subspan", () => {
  it("renders '(N of M models shown)' when selectedModels.length < totalModelCount", () => {
    // Fixture has 5 models total; selectedModels has 2. The "(2 of 5 models shown)"
    // subspan should appear because n !== totalModelCount.
    const fixture = makeFixture(["model-a", "model-b", "model-c", "model-d", "model-e"]);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["model-a", "model-b"],
      })
    );
    expect(container.textContent).toContain("2 of 5 models shown");
  });

  it("does NOT render '(N of M models shown)' when all models are selected", () => {
    // All 3 models selected — n === totalModelCount — subspan must be absent.
    const fixture = makeFixture(["model-a", "model-b", "model-c"]);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: ["model-a", "model-b", "model-c"],
      })
    );
    expect(container.textContent).not.toContain("models shown");
  });

  it("renders correct counts in '(N of M models shown)'", () => {
    // Fixture has 11 models total (standard LSB v1 set); selectedModels = 6.
    const modelIds = [
      "claude-opus-4-6",
      "claude-sonnet-4-6",
      "deepseek/deepseek-v3.2",
      "google/gemini-2.5-pro",
      "meta-llama/llama-4-maverick",
      "microsoft/phi-4",
      "mistralai/mistral-large-2512",
      "mistralai/mistral-small-2603",
      "openai/gpt-5.4",
      "openai/gpt-5.4-mini",
      "x-ai/grok-4",
    ];
    const fixture = makeFixture(modelIds);
    render(
      createElement(SourceAttribution, {
        domainResult: fixture,
        selectedModels: modelIds.slice(0, 6),
      })
    );
    // 6 selected out of 11 total.
    expect(container.textContent).toContain("6 of 11 models shown");
  });
});
