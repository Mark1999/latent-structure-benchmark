// @vitest-environment jsdom
/**
 * CiteModal component tests.
 *
 * Per T12 acceptance criteria:
 *   - Modal renders when isOpen=true, hidden when isOpen=false.
 *   - Escape closes (calls onClose).
 *   - Backdrop click closes.
 *   - Tab navigation cycles within modal (focus trap).
 *   - Initial focus lands on first interactive element.
 *   - Focus returns to trigger button on close.
 *   - Tabs cycle on arrow keys (APA → MLA → Chicago → BibTeX → APA).
 *   - Copy button calls navigator.clipboard.writeText (mocked).
 *   - Copy button shows "Copied!" feedback for ~1.5s.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { CiteModal } from "../components/CiteModal";
import type { CiteModalProps } from "../components/CiteModal";
import type { DomainResultPublished, WithinModelResult, EllipseParams, R1State } from "../data/types";

// ── Fixture ───────────────────────────────────────────────────────────────────

function makeFixture(modelIds: string[]): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, EllipseParams | null> = {};
  const r1_states: Record<string, R1State> = {};
  const top_terms: Record<string, string[]> = {};
  const within_model_results: WithinModelResult[] = [];

  modelIds.forEach((id, i) => {
    mds_coordinates[id] = [(i - modelIds.length / 2) * 0.1, 0];
    r1_states[id] = "typical_concentration";
    top_terms[id] = ["a", "b"];
    mds_uncertainty[id] = null;
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
    romney_small_n_warning: false,
    display: { r1_states, top_terms, top_terms_metric: "sutrop_csi" },
  };
}

// ── Test setup ─────────────────────────────────────────────────────────────────

let container: HTMLElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);

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
  vi.useRealTimers();
});

function render(props: CiteModalProps): void {
  act(() => {
    root.render(createElement(CiteModal, props));
  });
}

// ── Tests ──────────────────────────────────────────────────────────────────────

describe("CiteModal — open/close state", () => {
  it("renders the dialog when isOpen=true", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog).not.toBeNull();
  });

  it("does not render when isOpen=false", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: false,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog).toBeNull();
  });

  it("dialog has role='dialog' and aria-modal='true'", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.getAttribute("aria-modal")).toBe("true");
  });

  it("dialog has aria-labelledby referencing the heading", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    const labelledBy = dialog?.getAttribute("aria-labelledby");
    expect(labelledBy).toBeTruthy();
    const heading = document.getElementById(labelledBy!);
    expect(heading).not.toBeNull();
  });
});

describe("CiteModal — tabs render", () => {
  it("renders four tabs: APA, MLA, Chicago, BibTeX", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const tabs = document.body.querySelectorAll('[role="tab"]');
    expect(tabs).toHaveLength(4);
    const labels = Array.from(tabs).map((t) => t.textContent);
    expect(labels).toContain("APA");
    expect(labels).toContain("MLA");
    expect(labels).toContain("Chicago");
    expect(labels).toContain("BibTeX");
  });

  it("first tab (APA) is selected by default", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const apaTab = Array.from(document.body.querySelectorAll('[role="tab"]')).find(
      (t) => t.textContent === "APA"
    );
    expect(apaTab?.getAttribute("aria-selected")).toBe("true");
  });

  it("citation panel contains domain title-case and analysis version", () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    // APA panel should be visible and contain domain info
    const panel = document.body.querySelector('[role="tabpanel"]:not([hidden])');
    expect(panel?.textContent).toContain("Family");
    expect(panel?.textContent).toContain("2026");
  });
});

describe("CiteModal — close behavior", () => {
  it("Escape key calls onClose", async () => {
    const onClose = vi.fn();
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
    });

    await act(async () => {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    });

    expect(onClose).toHaveBeenCalledOnce();
  });

  it("backdrop click calls onClose", async () => {
    const onClose = vi.fn();
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
    });

    const backdrop = document.body.querySelector("[data-testid='cite-modal-backdrop']") as HTMLElement;
    expect(backdrop).not.toBeNull();

    await act(async () => {
      // Simulate clicking directly on the backdrop (not a child element).
      const event = new MouseEvent("click", { bubbles: true });
      Object.defineProperty(event, "target", { value: backdrop, enumerable: true });
      Object.defineProperty(event, "currentTarget", { value: backdrop, enumerable: true });
      backdrop.dispatchEvent(event);
    });

    expect(onClose).toHaveBeenCalled();
  });

  it("close button calls onClose", async () => {
    const onClose = vi.fn();
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
    });

    const closeBtn = document.body.querySelector(".cite-modal__close-btn") as HTMLButtonElement;
    expect(closeBtn).not.toBeNull();

    await act(async () => {
      closeBtn.click();
    });

    expect(onClose).toHaveBeenCalledOnce();
  });
});

describe("CiteModal — focus return on close", () => {
  it("returns focus to triggerRef on close", async () => {
    const triggerBtn = document.createElement("button");
    triggerBtn.textContent = "Open Cite";
    document.body.appendChild(triggerBtn);

    const triggerRef = { current: triggerBtn } as React.RefObject<HTMLButtonElement>;
    const onClose = vi.fn();
    const fixture = makeFixture(["model-a"]);

    // First render open.
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
      triggerRef,
    });

    // Re-render closed.
    act(() => {
      root.render(
        createElement(CiteModal, {
          domainResult: fixture,
          selectedModels: ["model-a"],
          isOpen: false,
          onClose,
          triggerRef,
        })
      );
    });

    // Focus should have returned to the trigger button.
    expect(document.activeElement).toBe(triggerBtn);

    document.body.removeChild(triggerBtn);
  });
});

describe("CiteModal — arrow key tab navigation", () => {
  it("ArrowRight moves from APA to MLA", async () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    await act(async () => {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
    });

    const tabs = document.body.querySelectorAll('[role="tab"]');
    const mlaTab = Array.from(tabs).find((t) => t.textContent === "MLA");
    expect(mlaTab?.getAttribute("aria-selected")).toBe("true");
  });

  it("ArrowLeft from APA wraps to BibTeX", async () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    await act(async () => {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true }));
    });

    const tabs = document.body.querySelectorAll('[role="tab"]');
    const bibtexTab = Array.from(tabs).find((t) => t.textContent === "BibTeX");
    expect(bibtexTab?.getAttribute("aria-selected")).toBe("true");
  });

  it("four ArrowRight presses from APA wraps back to APA", async () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    for (let i = 0; i < 4; i++) {
      await act(async () => {
        document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
      });
    }

    const tabs = document.body.querySelectorAll('[role="tab"]');
    const apaTab = Array.from(tabs).find((t) => t.textContent === "APA");
    expect(apaTab?.getAttribute("aria-selected")).toBe("true");
  });
});

describe("CiteModal — copy button", () => {
  it("copy button calls navigator.clipboard.writeText", async () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const copyBtn = document.body.querySelector(".cite-modal__copy-btn") as HTMLButtonElement;
    expect(copyBtn).not.toBeNull();

    await act(async () => {
      copyBtn.click();
    });

    expect(navigator.clipboard.writeText).toHaveBeenCalledOnce();
  });

  it("clipboard receives the current citation text", async () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const copyBtn = document.body.querySelector(".cite-modal__copy-btn") as HTMLButtonElement;

    await act(async () => {
      copyBtn.click();
    });

    const written = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    // APA citation should contain "Cognitive Structure Lab" and "Family"
    expect(written).toContain("Cognitive Structure Lab");
    expect(written).toContain("Family");
  });

  it("copy button shows 'Copied!' feedback after click", async () => {
    vi.useFakeTimers();

    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const copyBtn = document.body.querySelector(".cite-modal__copy-btn") as HTMLButtonElement;

    await act(async () => {
      copyBtn.click();
      await Promise.resolve();
    });

    expect(copyBtn.textContent).toContain("Copied!");

    // After 1.5s the button should revert.
    await act(async () => {
      vi.advanceTimersByTime(1600);
    });

    expect(copyBtn.textContent).not.toContain("Copied!");

    vi.useRealTimers();
  });
});

describe("CiteModal — tab click navigation", () => {
  it("clicking MLA tab activates MLA panel", async () => {
    const fixture = makeFixture(["model-a"]);
    render({
      domainResult: fixture,
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const mlaTab = Array.from(document.body.querySelectorAll('[role="tab"]')).find(
      (t) => t.textContent === "MLA"
    ) as HTMLButtonElement;
    expect(mlaTab).not.toBeNull();

    await act(async () => {
      mlaTab.click();
    });

    expect(mlaTab.getAttribute("aria-selected")).toBe("true");
  });
});
