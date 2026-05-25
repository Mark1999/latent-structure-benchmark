// @vitest-environment jsdom
/**
 * T12 gap-fill tests — coverage items not addressed by the Coder's original
 * 87 T12 tests (cite-modal.test.tsx, embed-modal.test.tsx, citation.test.ts).
 *
 * Gaps filled:
 *   1. citation.ts — buildBibtex author uses double-braces {{Cognitive Structure Lab}}
 *   2. citation.ts — yearFromIso fallback for invalid ISO input
 *   3. citation.ts — buildChicago author-date: year appears before title in string
 *   4. citation.ts — buildMla "Accessed" uses full month name (not numeric)
 *   5. CiteModal — F-T12-1 dynamic aria-label changes to "{tab} citation copied"
 *   6. CiteModal — inactive tab panels carry the `hidden` attribute
 *   7. EmbedModal — F-T12-1 dynamic aria-label changes to "Embed code copied"
 *   8. EmbedModal — snippet contains frameborder="0" and loading="lazy"
 *   9. DownloadBar T12 — Cite button: class, aria-label, click callback
 *  10. DownloadBar T12 — Embed button: class, aria-label, click callback
 *  11. DownloadBar T12 — isEmbed=true hides Permalink + Embed, keeps CSV + PNG
 *  12. DataExplorer T12 — CiteModal/EmbedModal are mounted in DataExplorer
 *  13. DataExplorer T12 — DownloadBar receives onOpenCiteModal + onOpenEmbedModal
 *  14. App.tsx — DataExplorer receives isEmbed prop (source assertion)
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 * Reference: docs/status/2026-05-11-phase5-T12-reviewer-verdict.md
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { CiteModal } from "../components/CiteModal";
import type { CiteModalProps } from "../components/CiteModal";
import { EmbedModal } from "../components/EmbedModal";
import type { EmbedModalProps } from "../components/EmbedModal";
import { DownloadBar } from "../components/DownloadBar";
import { DataExplorer } from "../components/DataExplorer";
import {
  buildBibtex,
  buildChicago,
  buildMla,
  accessDate,
} from "../lib/citation";
import type { CitationContext } from "../lib/citation";
import type { DomainResultPublished, WithinModelResult, EllipseParams, R1State } from "../data/types";

// ── Module mocks (PNG) ────────────────────────────────────────────────────────
// Required because DownloadBar imports png-export/png-metadata at module level.

vi.mock("../lib/png-export", () => ({
  renderToPng: vi.fn().mockResolvedValue(
    new Blob([new Uint8Array([0x89, 0x50])], { type: "image/png" })
  ),
}));

vi.mock("../lib/png-metadata", () => ({
  injectTextMetadata: vi.fn().mockImplementation(async (blob: Blob) => blob),
}));

// ── Source text for structural assertions ─────────────────────────────────────

const DE_SRC = readFileSync(
  resolve(__dirname, "../components/DataExplorer.tsx"),
  "utf-8"
);
const APP_SRC = readFileSync(resolve(__dirname, "../App.tsx"), "utf-8");

// ── Shared fixtures ───────────────────────────────────────────────────────────

const BASE_CTX: CitationContext = {
  domain: "family",
  domainTitle: "Family",
  analysisVersion: "0.2",
  generatedAt: "2026-05-07T00:07:50.238646Z",
  selectedModels: ["model-fixture-a", "model-fixture-b"],
};

function makeDomainFixture(modelIds: string[]): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, EllipseParams | null> = {};
  const r1_states: Record<string, R1State> = {};
  const top_terms: Record<string, string[]> = {};
  const within_model_results: WithinModelResult[] = [];

  modelIds.forEach((id, i) => {
    mds_coordinates[id] = [(i - modelIds.length / 2) * 0.1, 0];
    r1_states[id] = "typical_concentration";
    top_terms[id] = ["term-x", "term-y"];
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
    generated_lede: "Fixture lede.",
    generated_at: "2026-05-07T00:07:50.238646Z",
    romney_small_n_warning: false,
    display: { r1_states, top_terms, top_terms_metric: "sutrop_csi" },
  };
}

// ── Shared DOM render helpers ─────────────────────────────────────────────────

let container: HTMLElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);

  Object.defineProperty(navigator, "clipboard", {
    value: { writeText: vi.fn().mockResolvedValue(undefined) },
    writable: true,
    configurable: true,
  });
});

afterEach(() => {
  act(() => { root.unmount(); });
  document.body.removeChild(container);
  vi.restoreAllMocks();
  vi.useRealTimers();
});

function render(element: React.ReactElement): void {
  act(() => { root.render(element); });
}

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 1 — citation.ts: buildBibtex author field uses double curly braces
// ═══════════════════════════════════════════════════════════════════════════════

describe("citation.ts gap-fill — buildBibtex double-braces (§1.6 BibTeX author)", () => {
  it("author field uses {{Cognitive Structure Lab}} (double curly braces for BibTeX literal)", () => {
    const result = buildBibtex(BASE_CTX);
    // BibTeX requires {{...}} to prevent author parsing treating it as a person.
    expect(result).toContain("{{Cognitive Structure Lab}}");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 2 — citation.ts: yearFromIso fallback for invalid ISO input
// ═══════════════════════════════════════════════════════════════════════════════

describe("citation.ts gap-fill — yearFromIso fallback for invalid ISO", () => {
  it("buildApa uses current year when generatedAt is empty string", () => {
    const ctx: CitationContext = { ...BASE_CTX, generatedAt: "" };
    const result = buildApa(ctx);
    // Should fall back to new Date().getFullYear() — at least a 4-digit year in 2020s.
    expect(result).toMatch(/\(20\d\d\)/);
  });

  it("buildApa uses current year when generatedAt is a non-ISO string", () => {
    const ctx: CitationContext = { ...BASE_CTX, generatedAt: "not-a-date" };
    const result = buildApa(ctx);
    // Should fall back to the current year.
    expect(result).toMatch(/\(20\d\d\)/);
  });

  it("buildBibtex year field falls back for invalid ISO (not NaN or undefined)", () => {
    const ctx: CitationContext = { ...BASE_CTX, generatedAt: "???" };
    const result = buildBibtex(ctx);
    // year = field should still be a 4-digit number
    expect(result).toMatch(/year\s*=\s*\{20\d\d\}/);
  });
});

// Need buildApa for the yearFromIso fallback tests above.
import { buildApa } from "../lib/citation";

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 3 — citation.ts: buildChicago year appears before title (author-date)
// ═══════════════════════════════════════════════════════════════════════════════

describe("citation.ts gap-fill — buildChicago author-date ordering", () => {
  it("year appears before title in Chicago format (author-date style)", () => {
    const result = buildChicago(BASE_CTX);
    const yearPos = result.indexOf("2026");
    const titlePos = result.indexOf('"LSB:');
    // In Chicago author-date, year comes immediately after author, before title.
    expect(yearPos).toBeGreaterThan(-1);
    expect(titlePos).toBeGreaterThan(-1);
    expect(yearPos).toBeLessThan(titlePos);
  });

  it("Chicago format: year immediately follows the first period (author name ends with '.')", () => {
    // Pattern: "Cognitive Structure Lab. YYYY. "Title." ..."
    // Verify the year comes right after the first period+space.
    const result = buildChicago(BASE_CTX);
    expect(result).toMatch(/Cognitive Structure Lab\. 2026\./);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 4 — citation.ts: buildMla "Accessed" uses full month name
// ═══════════════════════════════════════════════════════════════════════════════

describe("citation.ts gap-fill — buildMla Accessed full month name", () => {
  it("accessDate produces full month name (not a numeric month)", () => {
    const MONTH_NAMES = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December",
    ];
    const result = accessDate();
    const hasFullName = MONTH_NAMES.some((m) => result.includes(m));
    // Must have a full month name — not "05" or "5" as standalone digit
    expect(hasFullName).toBe(true);
    // Must NOT have a bare numeric-only segment that looks like a month number
    // (i.e., result format is "DD MonthName YYYY", not "DD/MM/YYYY")
    expect(result).not.toMatch(/^\d+ \d+ \d+$/);
  });

  it("buildMla Accessed clause uses full month name in the output", () => {
    const MONTH_NAMES = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December",
    ];
    const result = buildMla(BASE_CTX);
    const hasFullName = MONTH_NAMES.some((m) => result.includes(m));
    expect(hasFullName).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 5 — CiteModal: F-T12-1 dynamic aria-label on copy button
// ═══════════════════════════════════════════════════════════════════════════════

describe("CiteModal gap-fill — F-T12-1 dynamic aria-label on copy button", () => {
  it("copy button aria-label reads 'APA citation copied' immediately after clicking copy", async () => {
    vi.useFakeTimers();

    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(CiteModal, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as CiteModalProps)
    );

    // APA is the default active tab.
    const copyBtn = document.body.querySelector(".cite-modal__copy-btn") as HTMLButtonElement;
    expect(copyBtn).not.toBeNull();

    await act(async () => {
      copyBtn.click();
      await Promise.resolve(); // allow clipboard promise to settle
    });

    // F-T12-1: aria-label must update to "{tab.label} citation copied"
    expect(copyBtn.getAttribute("aria-label")).toBe("APA citation copied");
  });

  it("copy button aria-label reverts to 'Copy APA citation' after 1.5s", async () => {
    vi.useFakeTimers();

    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(CiteModal, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as CiteModalProps)
    );

    const copyBtn = document.body.querySelector(".cite-modal__copy-btn") as HTMLButtonElement;

    await act(async () => {
      copyBtn.click();
      await Promise.resolve();
    });

    // Confirm copied state active.
    expect(copyBtn.getAttribute("aria-label")).toBe("APA citation copied");

    // Advance past the 1.5s timeout.
    await act(async () => {
      vi.advanceTimersByTime(1600);
    });

    // F-T12-1: aria-label must revert to "Copy {tab.label} citation"
    expect(copyBtn.getAttribute("aria-label")).toBe("Copy APA citation");
  });

  it("copy button aria-label reflects the active tab label (MLA)", async () => {
    vi.useFakeTimers();

    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(CiteModal, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as CiteModalProps)
    );

    // Switch to MLA tab.
    const mlaTab = Array.from(
      document.body.querySelectorAll('[role="tab"]')
    ).find((t) => t.textContent === "MLA") as HTMLButtonElement;
    expect(mlaTab).not.toBeNull();

    await act(async () => { mlaTab.click(); });

    // Now click copy on MLA panel.
    // The copy button is inside the active (non-hidden) tab panel.
    const activePanel = document.body.querySelector('[role="tabpanel"]:not([hidden])') as HTMLElement;
    expect(activePanel).not.toBeNull();
    const copyBtn = activePanel.querySelector(".cite-modal__copy-btn") as HTMLButtonElement;
    expect(copyBtn).not.toBeNull();

    await act(async () => {
      copyBtn.click();
      await Promise.resolve();
    });

    expect(copyBtn.getAttribute("aria-label")).toBe("MLA citation copied");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 6 — CiteModal: inactive tab panels carry the `hidden` attribute
// ═══════════════════════════════════════════════════════════════════════════════

describe("CiteModal gap-fill — inactive tab panels use `hidden` attribute", () => {
  it("only one tab panel is non-hidden at initial render (APA)", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(CiteModal, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as CiteModalProps)
    );

    const allPanels = document.body.querySelectorAll('[role="tabpanel"]');
    expect(allPanels).toHaveLength(4);

    const visiblePanels = Array.from(allPanels).filter((p) => !p.hasAttribute("hidden"));
    expect(visiblePanels).toHaveLength(1);
  });

  it("all three non-active tab panels carry the `hidden` attribute", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(CiteModal, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as CiteModalProps)
    );

    const allPanels = document.body.querySelectorAll('[role="tabpanel"]');
    const hiddenPanels = Array.from(allPanels).filter((p) => p.hasAttribute("hidden"));
    // 4 tabs total, 1 active → 3 hidden
    expect(hiddenPanels).toHaveLength(3);
  });

  it("switching to BibTeX tab makes the BibTeX panel non-hidden and others hidden", async () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(CiteModal, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as CiteModalProps)
    );

    const bibtexTab = Array.from(
      document.body.querySelectorAll('[role="tab"]')
    ).find((t) => t.textContent === "BibTeX") as HTMLButtonElement;
    await act(async () => { bibtexTab.click(); });

    const bibtexPanel = document.body.querySelector("#cite-panel-bibtex");
    expect(bibtexPanel).not.toBeNull();
    expect(bibtexPanel!.hasAttribute("hidden")).toBe(false);

    // APA panel must now be hidden.
    const apaPanel = document.body.querySelector("#cite-panel-apa");
    expect(apaPanel).not.toBeNull();
    expect(apaPanel!.hasAttribute("hidden")).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 7 — EmbedModal: F-T12-1 dynamic aria-label on copy button
// ═══════════════════════════════════════════════════════════════════════════════

describe("EmbedModal gap-fill — F-T12-1 dynamic aria-label on copy button", () => {
  it("copy button aria-label reads 'Embed code copied' immediately after clicking copy", async () => {
    vi.useFakeTimers();

    render(
      createElement(EmbedModal, {
        domain: "family",
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as EmbedModalProps)
    );

    const copyBtn = document.body.querySelector(".embed-modal__copy-btn") as HTMLButtonElement;
    expect(copyBtn).not.toBeNull();

    await act(async () => {
      copyBtn.click();
      await Promise.resolve();
    });

    // F-T12-1: aria-label must update to "Embed code copied"
    expect(copyBtn.getAttribute("aria-label")).toBe("Embed code copied");
  });

  it("copy button aria-label reverts to 'Copy embed code' after 1.5s", async () => {
    vi.useFakeTimers();

    render(
      createElement(EmbedModal, {
        domain: "family",
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as EmbedModalProps)
    );

    const copyBtn = document.body.querySelector(".embed-modal__copy-btn") as HTMLButtonElement;

    await act(async () => {
      copyBtn.click();
      await Promise.resolve();
    });

    expect(copyBtn.getAttribute("aria-label")).toBe("Embed code copied");

    await act(async () => { vi.advanceTimersByTime(1600); });

    // F-T12-1: aria-label must revert
    expect(copyBtn.getAttribute("aria-label")).toBe("Copy embed code");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 8 — EmbedModal: snippet contains frameborder="0" and loading="lazy"
// ═══════════════════════════════════════════════════════════════════════════════

describe("EmbedModal gap-fill — iframe attributes in snippet", () => {
  it('snippet contains frameborder="0"', () => {
    render(
      createElement(EmbedModal, {
        domain: "family",
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as EmbedModalProps)
    );
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain('frameborder="0"');
  });

  it('snippet contains loading="lazy"', () => {
    render(
      createElement(EmbedModal, {
        domain: "family",
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as EmbedModalProps)
    );
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain('loading="lazy"');
  });

  it("snippet contains src= attribute", () => {
    render(
      createElement(EmbedModal, {
        domain: "family",
        selectedModels: ["model-fixture-a"],
        isOpen: true,
        onClose: vi.fn(),
      } as EmbedModalProps)
    );
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain('src=');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 9 — DownloadBar T12: Cite button class, aria-label, callback
// ═══════════════════════════════════════════════════════════════════════════════

describe("DownloadBar T12 gap-fill — Cite button", () => {
  it("renders Cite button when onOpenCiteModal is provided", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenCiteModal: vi.fn(),
      })
    );
    const citeBtn = container.querySelector(".download-bar__cite-btn");
    expect(citeBtn).not.toBeNull();
  });

  it("Cite button has aria-label='Show citation formats'", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenCiteModal: vi.fn(),
      })
    );
    const citeBtn = container.querySelector(".download-bar__cite-btn");
    expect(citeBtn?.getAttribute("aria-label")).toBe("Show citation formats");
  });

  it("Cite button click invokes onOpenCiteModal callback", async () => {
    const onOpenCiteModal = vi.fn();
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenCiteModal,
      })
    );
    const citeBtn = container.querySelector<HTMLButtonElement>(".download-bar__cite-btn");
    expect(citeBtn).not.toBeNull();

    await act(async () => { citeBtn!.click(); });

    expect(onOpenCiteModal).toHaveBeenCalledOnce();
  });

  it("Cite button not rendered when onOpenCiteModal is not provided", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        // no onOpenCiteModal
      })
    );
    const citeBtn = container.querySelector(".download-bar__cite-btn");
    expect(citeBtn).toBeNull();
  });

  it("Cite button hidden when isEmbed=true", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenCiteModal: vi.fn(),
        isEmbed: true,
      })
    );
    const citeBtn = container.querySelector(".download-bar__cite-btn");
    expect(citeBtn).toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 10 — DownloadBar T12: Embed button class, aria-label, callback
// ═══════════════════════════════════════════════════════════════════════════════

describe("DownloadBar T12 gap-fill — Embed button", () => {
  it("renders Embed button when onOpenEmbedModal is provided", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenEmbedModal: vi.fn(),
      })
    );
    const embedBtn = container.querySelector(".download-bar__embed-btn");
    expect(embedBtn).not.toBeNull();
  });

  it("Embed button has aria-label='Show embed code'", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenEmbedModal: vi.fn(),
      })
    );
    const embedBtn = container.querySelector(".download-bar__embed-btn");
    expect(embedBtn?.getAttribute("aria-label")).toBe("Show embed code");
  });

  it("Embed button click invokes onOpenEmbedModal callback", async () => {
    const onOpenEmbedModal = vi.fn();
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenEmbedModal,
      })
    );
    const embedBtn = container.querySelector<HTMLButtonElement>(".download-bar__embed-btn");
    expect(embedBtn).not.toBeNull();

    await act(async () => { embedBtn!.click(); });

    expect(onOpenEmbedModal).toHaveBeenCalledOnce();
  });

  it("Embed button not rendered when onOpenEmbedModal is not provided", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        // no onOpenEmbedModal
      })
    );
    const embedBtn = container.querySelector(".download-bar__embed-btn");
    expect(embedBtn).toBeNull();
  });

  it("Embed button hidden when isEmbed=true (§12.5)", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenEmbedModal: vi.fn(),
        isEmbed: true,
      })
    );
    const embedBtn = container.querySelector(".download-bar__embed-btn");
    expect(embedBtn).toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 11 — DownloadBar T12: isEmbed=true hides Permalink, keeps CSV + PNG
// ═══════════════════════════════════════════════════════════════════════════════

describe("DownloadBar T12 gap-fill — isEmbed=true: Permalink hidden, CSV + PNG visible", () => {
  it("Permalink button is hidden when isEmbed=true", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        isEmbed: true,
      })
    );
    const permalinkBtn = container.querySelector(".download-bar__permalink-btn");
    expect(permalinkBtn).toBeNull();
  });

  it("CSV button remains visible when isEmbed=true", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        isEmbed: true,
      })
    );
    const csvBtn = container.querySelector(".download-bar__csv-btn");
    expect(csvBtn).not.toBeNull();
  });

  it("PNG social button remains visible when isEmbed=true", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        isEmbed: true,
      })
    );
    const pngBtn = container.querySelector(".download-bar__png-btn");
    expect(pngBtn).not.toBeNull();
  });

  it("isEmbed=false (default): all buttons including Permalink and Embed visible", () => {
    const fixture = makeDomainFixture(["model-fixture-a"]);
    render(
      createElement(DownloadBar, {
        domainResult: fixture,
        selectedModels: ["model-fixture-a"],
        activeVizTab: "mds",
        onOpenCiteModal: vi.fn(),
        onOpenEmbedModal: vi.fn(),
        isEmbed: false,
      })
    );
    expect(container.querySelector(".download-bar__permalink-btn")).not.toBeNull();
    expect(container.querySelector(".download-bar__cite-btn")).not.toBeNull();
    expect(container.querySelector(".download-bar__embed-btn")).not.toBeNull();
    expect(container.querySelector(".download-bar__csv-btn")).not.toBeNull();
    expect(container.querySelector(".download-bar__png-btn")).not.toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 12 — DataExplorer T12: CiteModal and EmbedModal are mounted in DataExplorer
// ═══════════════════════════════════════════════════════════════════════════════

describe("DataExplorer T12 gap-fill — CiteModal + EmbedModal mounted in DataExplorer", () => {
  it("DataExplorer.tsx source imports CiteModal", () => {
    expect(DE_SRC).toContain("CiteModal");
    expect(DE_SRC).toContain("from \"./CiteModal\"");
  });

  it("DataExplorer.tsx source imports EmbedModal", () => {
    expect(DE_SRC).toContain("EmbedModal");
    expect(DE_SRC).toContain("from \"./EmbedModal\"");
  });

  it("DataExplorer.tsx declares isCiteOpen state", () => {
    expect(DE_SRC).toContain("isCiteOpen");
    expect(DE_SRC).toContain("setIsCiteOpen");
  });

  it("DataExplorer.tsx declares isEmbedOpen state", () => {
    expect(DE_SRC).toContain("isEmbedOpen");
    expect(DE_SRC).toContain("setIsEmbedOpen");
  });

  it("DataExplorer.tsx declares citeTriggerRef", () => {
    expect(DE_SRC).toContain("citeTriggerRef");
  });

  it("DataExplorer.tsx declares embedTriggerRef", () => {
    expect(DE_SRC).toContain("embedTriggerRef");
  });

  it("DataExplorer renders DownloadBar with onOpenCiteModal callback", () => {
    expect(DE_SRC).toContain("onOpenCiteModal={() => setIsCiteOpen(true)}");
  });

  it("DataExplorer renders DownloadBar with onOpenEmbedModal callback", () => {
    expect(DE_SRC).toContain("onOpenEmbedModal={() => setIsEmbedOpen(true)}");
  });

  it("DataExplorer renders CiteModal with isOpen bound to isCiteOpen", () => {
    expect(DE_SRC).toContain("isOpen={isCiteOpen}");
  });

  it("DataExplorer renders EmbedModal with isOpen bound to isEmbedOpen", () => {
    expect(DE_SRC).toContain("isOpen={isEmbedOpen}");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 13 — DataExplorer T12: DownloadBar passes isEmbed prop from DataExplorer
// ═══════════════════════════════════════════════════════════════════════════════

describe("DataExplorer T12 gap-fill — isEmbed prop flows through to DownloadBar", () => {
  it("DataExplorer.tsx passes isEmbed to DownloadBar (source assertion)", () => {
    expect(DE_SRC).toContain("isEmbed={isEmbed}");
  });

  it("DataExplorer defaults isEmbed to false (source assertion)", () => {
    // DataExplorer function signature: { domainResult, isEmbed = false }
    expect(DE_SRC).toContain("isEmbed = false");
  });

  it("rendering DataExplorer with isEmbed=true hides Embed button in DOM", () => {
    const fixture = makeDomainFixture(["model-fixture-a", "model-fixture-b"]);
    render(
      createElement(DataExplorer, {
        domainResult: fixture,
        isEmbed: true,
      })
    );
    // Embed button should not exist when isEmbed=true propagates through
    const embedBtn = container.querySelector(".download-bar__embed-btn");
    expect(embedBtn).toBeNull();
  });

  it("rendering DataExplorer with isEmbed=true hides Permalink button in DOM", () => {
    const fixture = makeDomainFixture(["model-fixture-a", "model-fixture-b"]);
    render(
      createElement(DataExplorer, {
        domainResult: fixture,
        isEmbed: true,
      })
    );
    const permalinkBtn = container.querySelector(".download-bar__permalink-btn");
    expect(permalinkBtn).toBeNull();
  });

  it("rendering DataExplorer without isEmbed shows Permalink button in DOM", () => {
    const fixture = makeDomainFixture(["model-fixture-a", "model-fixture-b"]);
    render(
      createElement(DataExplorer, {
        domainResult: fixture,
        // isEmbed not set — default false
      })
    );
    const permalinkBtn = container.querySelector(".download-bar__permalink-btn");
    expect(permalinkBtn).not.toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GAP 14 — App.tsx: DataExplorer receives isEmbed={true} in embed-mode branch
// ═══════════════════════════════════════════════════════════════════════════════

describe("App.tsx T12 gap-fill — DataExplorer receives isEmbed prop (source assertion)", () => {
  it("App.tsx passes isEmbed={true} to DataExplorer in embed-mode branch", () => {
    // In App.tsx embedMode branch: <DataExplorer domainResult={domainResult} isEmbed={true} />
    expect(APP_SRC).toContain("isEmbed={true}");
  });

  it("App.tsx embed-mode branch renders DataExplorer (source assertion)", () => {
    // App.tsx should render DataExplorer with isEmbed={true} inside the embedMode block.
    expect(APP_SRC).toContain("isEmbed={true}");
  });

  it("App.tsx app-shell branch renders DataExplorer without isEmbed (not embed mode)", () => {
    // Phase 9a: the full-page mode is now an app-shell. DataExplorer is rendered
    // with external state props (externalSelectedModels, externalActiveVizTab, etc.)
    // but without isEmbed. Verify the app-shell DataExplorer call contains domainResult
    // but NOT isEmbed={true}.
    const appShellStart = APP_SRC.indexOf("// ── App-shell layout");
    expect(appShellStart).toBeGreaterThan(-1);
    const appShellBlock = APP_SRC.slice(appShellStart);
    expect(appShellBlock).toContain("<DataExplorer");
    expect(appShellBlock).toContain("domainResult={domainResult}");
    expect(appShellBlock).not.toContain("isEmbed={true}");
  });
});
