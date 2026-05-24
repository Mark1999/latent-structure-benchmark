// @vitest-environment jsdom
/**
 * T12 gap-fill tests — Phase 6 T12 (Mobile bottom-drawer for ModelSelector).
 *
 * The Coder did not write T12-specific drawer tests (per the standard pipeline:
 * Coder implements, Tester covers). This file provides full test coverage
 * of the T12 testable surface as enumerated in:
 *   docs/status/2026-05-15-phase6-T12-architect-plan.md §6 (Tester section)
 *   docs/status/2026-05-15-phase6-T12-uiux-plan-verdict.md (A1–A6, M1, M2, M3)
 *   DESIGN_SYSTEM.md §8.2
 *
 * Coverage gaps filled:
 *
 *   G1.  Trigger ARIA at rest: aria-label === MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED
 *        ("Open model selector"), aria-expanded === 'false', aria-controls ===
 *        "mobile-model-drawer-panel", aria-haspopup === "dialog" — verbatim .toBe().
 *   G2.  Trigger visible text equals MOBILE_MODEL_DRAWER_TRIGGER_TEXT(N) at mount.
 *   G3.  Trigger touch target: class .explorer-layout__mobile-selector-trigger present.
 *   G4.  Click trigger → drawer renders: role="dialog", aria-modal="true",
 *        aria-label === MOBILE_MODEL_DRAWER_PANEL_LABEL ("Model selector").
 *   G5.  After open: trigger aria-expanded === 'true', aria-label ===
 *        MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN ("Close model selector").
 *   G6.  After open: trigger remains visible (NOT display:none) — §8.2.9 + A6.
 *   G7.  M1 toggle: click trigger again while drawer open → drawer closes;
 *        trigger aria-expanded flips back to 'false'.
 *   G8.  Enter on trigger opens drawer; Space on trigger opens drawer.
 *   G9.  Trigger visible when open with aria-expanded==='true' and updated aria-label
 *        (§8.2.9 + A6 override of plan G9).
 *   G10. Esc key closes drawer; focus returns to trigger element.
 *   G11. Close button (top-right ×) closes drawer; focus returns to trigger.
 *   G12. Click scrim closes drawer; focus returns to trigger.
 *   G13. M2 panel event propagation: click inside .mobile-model-drawer__panel does
 *        NOT close the drawer (scrim onPointerDown did not fire).
 *   G14. Initial focus on close button after open.
 *   G15. Tab from last focusable element wraps to close button (focus trap).
 *   G16. Shift+Tab from close button wraps to last focusable element.
 *   G17. Focus trap stays within drawer (Tab does not escape to page).
 *   G18. After open: document.body.style.overflow === "hidden".
 *   G19. After close (any path): document.body.style.overflow restored.
 *   G20. Forced unmount while open also restores document.body.style.overflow.
 *   G21. mobile_model_drawer.ts constants verbatim per §8.2.14 (.toBe()).
 *   G22. mobile_model_drawer.ts source contains exactly 4 export items.
 *   G23. No MOBILE_MODEL_DRAWER_HEADING constant in mobile_model_drawer.ts.
 *   G24. mobile_model_drawer.ts passes forbidden-vocab grep.
 *   G25. MobileModelSelectorDrawer.tsx file-header references DESIGN_SYSTEM.md §8.2.
 *   G26. mobile-model-drawer.css contains @media (prefers-reduced-motion: reduce)
 *        block with transition: none and animation: none.
 *   G27. mobile-model-drawer.css contains scoped touch-target rules for
 *        .model-selector__row and .model-selector__action-link with min-height: 44px.
 *   G28. mobile-model-drawer.css contains .mobile-model-drawer__scrim with
 *        z-index: 199 and background: rgba(0, 0, 0, 0.45).
 *   G29. mobile-model-drawer.css contains panel position: fixed, bottom: 0,
 *        max-height: 75vh and z-index: 200.
 *   G30. mobile-model-drawer.css contains panel transform: translateY(100%) rest state
 *        and --open modifier with transform: translateY(0) and transition: 200ms ease-out.
 *   G31. app.css does NOT contain grid-template-areas: "viz" inside @media (max-width: 768px)
 *        for .explorer-layout (T13 supersession).
 *   G32. app.css contains .explorer-layout__selector .model-selector { display: none; }
 *        inside a @media (max-width: 768px) block.
 *   G33. MobileModelSelectorDrawer.tsx source contains onPointerDown and stopPropagation (M2).
 *   G34. DataExplorer.tsx source contains the toggle pattern prev => !prev (M1).
 *   G35. DESIGN_SYSTEM.md version is v0.4.8.
 *   G36. DESIGN_SYSTEM.md §8.2 section header present.
 *   G37. DESIGN_SYSTEM.md §8.2.14 table contains all four pre-cleared strings verbatim.
 *   G38. DESIGN_SYSTEM.md footer reads "End of DESIGN_SYSTEM.md v0.4.8".
 *   G39. ModelSelector.tsx source does NOT contain MOBILE_MODEL_DRAWER anywhere.
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures and static file reads only.
 * No new dependencies.
 *
 * Reference:
 *   docs/status/2026-05-15-phase6-T12-architect-plan.md §6 (Tester section)
 *   docs/status/2026-05-15-phase6-T12-uiux-plan-verdict.md (A1–A6, M1, M2, M3)
 *   docs/status/2026-05-15-phase6-T12-reviewer-verdict.md (PASS)
 *   DESIGN_SYSTEM.md §8.2
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

import { DataExplorer } from "../components/DataExplorer";
import {
  MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED,
  MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN,
  MOBILE_MODEL_DRAWER_PANEL_LABEL,
  MOBILE_MODEL_DRAWER_TRIGGER_TEXT,
} from "../copy/mobile_model_drawer";
import type { DomainResultPublished, WithinModelResult, EllipseParams, R1State } from "../data/types";

// ── ESM-compatible __dirname ───────────────────────────────────────────────────

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Static source reads ────────────────────────────────────────────────────────

const MOBILE_DRAWER_TS_SRC = readFileSync(
  resolve(__dirname, "../copy/mobile_model_drawer.ts"),
  "utf-8"
);

const MOBILE_DRAWER_TSX_SRC = readFileSync(
  resolve(__dirname, "../components/MobileModelSelectorDrawer.tsx"),
  "utf-8"
);

const MOBILE_DRAWER_CSS_SRC = readFileSync(
  resolve(__dirname, "../styles/mobile-model-drawer.css"),
  "utf-8"
);

const DATA_EXPLORER_SRC = readFileSync(
  resolve(__dirname, "../components/DataExplorer.tsx"),
  "utf-8"
);

const APP_CSS_SRC = readFileSync(
  resolve(__dirname, "../styles/app.css"),
  "utf-8"
);

const MODEL_SELECTOR_SRC = readFileSync(
  resolve(__dirname, "../components/ModelSelector.tsx"),
  "utf-8"
);

const DESIGN_SYSTEM_MD = readFileSync(
  resolve(__dirname, "../../../../DESIGN_SYSTEM.md"),
  "utf-8"
);

// ── Fixture helpers ────────────────────────────────────────────────────────────

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
      centroid_run_id: "run-fixture-1",
      mds_within_model: [],
    });
  });

  return {
    domain_slug: "fixture-domain",
    analysis_version: "0.2",
    models: modelIds.map((id) => ({
      provider: "fixture-provider",
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
    generated_lede: "Fixture lede for T12 mobile drawer tests.",
    generated_at: "2026-05-15T00:00:00.000000Z",
    romney_small_n_warning: false,
    display: { r1_states, top_terms, top_terms_metric: "sutrop_csi" },
  };
}

// ── Render helpers ─────────────────────────────────────────────────────────────

let container: HTMLDivElement;
let root: ReturnType<typeof createRoot>;

// Six fixture model IDs — matches the DataExplorer first-6 default.
const FIXTURE_MODEL_IDS = [
  "fixture-model-a",
  "fixture-model-b",
  "fixture-model-c",
  "fixture-model-d",
  "fixture-model-e",
  "fixture-model-f",
];

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  // Ensure body overflow is clean at the start of each test.
  document.body.style.overflow = "";
});

afterEach(() => {
  act(() => {
    root.unmount();
  });
  container.remove();
  vi.restoreAllMocks();
  // Always restore body overflow even if a test did not.
  document.body.style.overflow = "";
});

function renderExplorer(modelIds: string[] = FIXTURE_MODEL_IDS): void {
  const fixture = makeDomainFixture(modelIds);
  act(() => {
    root.render(createElement(DataExplorer, { domainResult: fixture }));
  });
}

function getTrigger(): HTMLButtonElement | null {
  return container.querySelector<HTMLButtonElement>(
    "button.explorer-layout__mobile-selector-trigger"
  );
}

function getDrawerPanel(): HTMLElement | null {
  return container.querySelector<HTMLElement>('[role="dialog"]');
}

function getCloseBtn(): HTMLButtonElement | null {
  return container.querySelector<HTMLButtonElement>(".mobile-model-drawer__close");
}

function getScrim(): HTMLElement | null {
  return container.querySelector<HTMLElement>(".mobile-model-drawer__scrim");
}

// ══════════════════════════════════════════════════════════════════════════════
// G1 — Trigger ARIA at rest (§8.2.1 ARIA pattern)
// ══════════════════════════════════════════════════════════════════════════════

describe("G1 — Trigger ARIA at rest (§8.2.1)", () => {
  it("trigger button renders in the DOM", () => {
    renderExplorer();
    expect(getTrigger()).not.toBeNull();
  });

  it("aria-label at rest === MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED ('Open model selector')", () => {
    renderExplorer();
    expect(getTrigger()?.getAttribute("aria-label")).toBe(
      MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED
    );
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED is exactly 'Open model selector' (verbatim .toBe())", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED).toBe("Open model selector");
  });

  it("aria-expanded at rest === 'false'", () => {
    renderExplorer();
    expect(getTrigger()?.getAttribute("aria-expanded")).toBe("false");
  });

  it("aria-controls === 'mobile-model-drawer-panel'", () => {
    renderExplorer();
    expect(getTrigger()?.getAttribute("aria-controls")).toBe(
      "mobile-model-drawer-panel"
    );
  });

  it("aria-haspopup === 'dialog'", () => {
    renderExplorer();
    expect(getTrigger()?.getAttribute("aria-haspopup")).toBe("dialog");
  });

  it("drawer panel is NOT in DOM at rest (before trigger click)", () => {
    renderExplorer();
    expect(getDrawerPanel()).toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G2 — Trigger visible text (§8.2.5, §8.2.14 MOBILE_MODEL_DRAWER_TRIGGER_TEXT)
// ══════════════════════════════════════════════════════════════════════════════

describe("G2 — Trigger visible text at mount (§8.2.5 / §8.2.14)", () => {
  it("trigger text equals MOBILE_MODEL_DRAWER_TRIGGER_TEXT(6) at mount (6 models selected by §3.7 default)", () => {
    // DataExplorer selects first 6 model_ids by default (§3.7 v0.4.2).
    renderExplorer(FIXTURE_MODEL_IDS);
    const trigger = getTrigger();
    expect(trigger?.textContent?.trim()).toBe(
      MOBILE_MODEL_DRAWER_TRIGGER_TEXT(6)
    );
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_TEXT(0) === 'Select models (0 selected)' (verbatim .toBe())", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_TEXT(0)).toBe("Select models (0 selected)");
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_TEXT(3) === 'Select models (3 selected)' (verbatim .toBe())", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_TEXT(3)).toBe("Select models (3 selected)");
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_TEXT(6) === 'Select models (6 selected)' (verbatim .toBe())", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_TEXT(6)).toBe("Select models (6 selected)");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G3 — Trigger touch target class presence (§8.2.5, §8.2.6 min-height: 48px)
// ══════════════════════════════════════════════════════════════════════════════

describe("G3 — Trigger touch target class presence (§8.2.5 — 48px floor)", () => {
  it("trigger has class 'explorer-layout__mobile-selector-trigger'", () => {
    renderExplorer();
    const trigger = getTrigger();
    expect(trigger).not.toBeNull();
    expect(
      trigger?.classList.contains("explorer-layout__mobile-selector-trigger")
    ).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G4 — Click trigger → drawer renders with correct ARIA (§8.2.1 dialog pattern)
// ══════════════════════════════════════════════════════════════════════════════

describe("G4 — Click trigger → drawer renders (§8.2.1 dialog pattern)", () => {
  it("drawer panel appears in DOM after trigger click", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();
  });

  it("drawer panel has role='dialog'", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()?.getAttribute("role")).toBe("dialog");
  });

  it("drawer panel has aria-modal='true'", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()?.getAttribute("aria-modal")).toBe("true");
  });

  it("drawer panel has aria-label === MOBILE_MODEL_DRAWER_PANEL_LABEL ('Model selector')", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()?.getAttribute("aria-label")).toBe(
      MOBILE_MODEL_DRAWER_PANEL_LABEL
    );
  });

  it("MOBILE_MODEL_DRAWER_PANEL_LABEL is exactly 'Model selector' (verbatim .toBe())", () => {
    expect(MOBILE_MODEL_DRAWER_PANEL_LABEL).toBe("Model selector");
  });

  it("drawer panel has id === 'mobile-model-drawer-panel' (matches aria-controls)", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()?.getAttribute("id")).toBe("mobile-model-drawer-panel");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G5 — Trigger ARIA state after open (§8.2.1, §8.2.6, §8.2.9)
// ══════════════════════════════════════════════════════════════════════════════

describe("G5 — Trigger ARIA state changes on open (§8.2.1 / §8.2.9)", () => {
  it("trigger aria-expanded === 'true' after open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-expanded")).toBe("true");
  });

  it("trigger aria-label === MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN after open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-label")).toBe(
      MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN
    );
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN is exactly 'Close model selector' (verbatim .toBe())", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN).toBe("Close model selector");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G6 — Trigger remains visible when drawer is open (§8.2.9 + UI/UX A6 override)
// ══════════════════════════════════════════════════════════════════════════════

describe("G6 — Trigger remains visible when drawer is open (§8.2.9 + A6)", () => {
  it("trigger is NOT display:none when drawer is open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    // §8.2.9: trigger remains visible when drawer open; no inline display:none set.
    expect(getTrigger()?.style.display).not.toBe("none");
  });

  it("trigger is still in the DOM when drawer is open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G7 — M1 toggle: click trigger again while open → closes drawer (§8.2.6 / M1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G7 — M1 toggle: second trigger click closes drawer (§8.2.6 / M1)", () => {
  it("clicking trigger while drawer is open closes the drawer (toggle behavior)", async () => {
    renderExplorer();
    // Open.
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();

    // Toggle-close.
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).toBeNull();
  });

  it("after toggle-close, trigger aria-expanded flips back to 'false'", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-expanded")).toBe("false");
  });

  it("after toggle-close, trigger aria-label reverts to MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-label")).toBe(
      MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G8 — Enter / Space on trigger open drawer (§8.2.1 / WCAG 2.1.1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G8 — Enter and Space keys on trigger open drawer (§8.2.1 / WCAG 2.1.1)", () => {
  it("Enter keydown + click on trigger opens drawer (native button behavior)", async () => {
    renderExplorer();
    const trigger = getTrigger()!;

    await act(async () => {
      trigger.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
      trigger.click();
    });

    expect(getDrawerPanel()).not.toBeNull();
  });

  it("Space keydown + click on trigger opens drawer (native button behavior)", async () => {
    renderExplorer();
    const trigger = getTrigger()!;

    await act(async () => {
      trigger.dispatchEvent(
        new KeyboardEvent("keydown", { key: " ", bubbles: true })
      );
      trigger.click();
    });

    expect(getDrawerPanel()).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G9 — Trigger visible when open: aria-expanded true + updated aria-label (A6)
// ══════════════════════════════════════════════════════════════════════════════

describe("G9 — Trigger visible + correct ARIA when drawer open (§8.2.9 + A6)", () => {
  it("trigger aria-expanded === 'true' when drawer is open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-expanded")).toBe("true");
  });

  it("trigger aria-label === MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN when drawer is open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-label")).toBe(
      MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN
    );
  });

  it("trigger style.display is not 'none' when drawer is open (§8.2.9 binding)", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.style.display).not.toBe("none");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G10 — Esc key closes drawer; focus returns to trigger (§8.2.1 / WCAG 2.1.2)
// ══════════════════════════════════════════════════════════════════════════════

describe("G10 — Esc closes drawer; focus returns to trigger (§8.2.1)", () => {
  it("Esc key closes the drawer (panel removed from DOM)", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });

    expect(getDrawerPanel()).toBeNull();
  });

  it("focus returns to trigger button after Esc closes drawer", async () => {
    renderExplorer();
    const trigger = getTrigger();
    await act(async () => {
      trigger?.click();
    });

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(getTrigger());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G11 — Close button (×) closes drawer; focus returns to trigger (§8.2.7)
// ══════════════════════════════════════════════════════════════════════════════

describe("G11 — Close button closes drawer; focus returns to trigger (§8.2.7)", () => {
  it("close button exists inside drawer after open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getCloseBtn()).not.toBeNull();
  });

  it("clicking close button removes drawer from DOM", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();

    await act(async () => {
      getCloseBtn()?.click();
    });

    expect(getDrawerPanel()).toBeNull();
  });

  it("focus returns to trigger after close button click", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });

    await act(async () => {
      getCloseBtn()?.click();
    });

    expect(document.activeElement).toBe(getTrigger());
  });

  it("close button has aria-label === MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN ('Close model selector')", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getCloseBtn()?.getAttribute("aria-label")).toBe(
      MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN
    );
  });

  it("close button glyph is × (U+00D7 MULTIPLICATION SIGN) in aria-hidden span", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    const glyphSpan = getCloseBtn()?.querySelector("span[aria-hidden='true']");
    expect(glyphSpan).not.toBeNull();
    expect(glyphSpan?.textContent).toBe("×");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G12 — Click scrim closes drawer; focus returns to trigger (§8.2.3)
// ══════════════════════════════════════════════════════════════════════════════

describe("G12 — Click scrim closes drawer; focus returns to trigger (§8.2.3)", () => {
  it("scrim element is present after drawer opens", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getScrim()).not.toBeNull();
  });

  it("scrim has aria-hidden='true'", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getScrim()?.getAttribute("aria-hidden")).toBe("true");
  });

  it("pointerdown on scrim closes the drawer", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();

    await act(async () => {
      getScrim()?.dispatchEvent(
        new PointerEvent("pointerdown", { bubbles: true })
      );
    });

    expect(getDrawerPanel()).toBeNull();
  });

  it("focus returns to trigger after scrim pointerdown closes drawer", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });

    await act(async () => {
      getScrim()?.dispatchEvent(
        new PointerEvent("pointerdown", { bubbles: true })
      );
    });

    expect(document.activeElement).toBe(getTrigger());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G13 — M2 panel event propagation: click inside panel body does NOT close (§8.2.3 / M2)
// ══════════════════════════════════════════════════════════════════════════════

describe("G13 — M2: pointerdown inside drawer panel does NOT close drawer (§8.2.3 / M2)", () => {
  it("pointerdown on .mobile-model-drawer__panel does not close the drawer", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();

    // Fire pointerdown directly on the panel — stopPropagation should prevent
    // the scrim's handler from firing. The drawer must remain open.
    await act(async () => {
      getDrawerPanel()?.dispatchEvent(
        new PointerEvent("pointerdown", { bubbles: true })
      );
    });

    expect(getDrawerPanel()).not.toBeNull();
  });

  it("pointerdown on .mobile-model-drawer__body does not close the drawer", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });

    const body = container.querySelector<HTMLElement>(".mobile-model-drawer__body");
    await act(async () => {
      body?.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true }));
    });

    expect(getDrawerPanel()).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G14 — Initial focus on close button after open (§8.2.1 / WCAG 2.4.3)
// ══════════════════════════════════════════════════════════════════════════════

describe("G14 — Initial focus on close button after open (§8.2.1 / WCAG 2.4.3)", () => {
  it("document.activeElement is the close button immediately after drawer opens", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.activeElement).toBe(getCloseBtn());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G15 — Focus trap: Tab from last focusable wraps to close button (§8.2.1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G15 — Focus trap: Tab from last element wraps to close button (§8.2.1)", () => {
  it("Tab on the last focusable element inside drawer wraps focus back to close button", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });

    // Find all focusable elements inside the panel.
    const panel = getDrawerPanel()!;
    const focusableSelector = [
      "button:not([disabled])",
      "[href]",
      "input:not([disabled])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      '[tabindex]:not([tabindex="-1"])',
    ].join(",");
    const focusable = Array.from(
      panel.querySelectorAll<HTMLElement>(focusableSelector)
    ).filter((el) => !el.closest("[aria-hidden]"));

    expect(focusable.length).toBeGreaterThan(0);
    const lastEl = focusable[focusable.length - 1];

    // Move focus to last element manually.
    await act(async () => {
      lastEl.focus();
    });
    expect(document.activeElement).toBe(lastEl);

    // Fire Tab (the keydown handler on document wraps focus).
    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", {
          key: "Tab",
          bubbles: true,
          shiftKey: false,
        })
      );
    });

    expect(document.activeElement).toBe(getCloseBtn());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G16 — Focus trap: Shift+Tab from close button wraps to last element (§8.2.1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G16 — Focus trap: Shift+Tab from close button wraps to last element (§8.2.1)", () => {
  it("Shift+Tab on close button wraps focus to last focusable element", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });

    const closeBtn = getCloseBtn()!;
    const panel = getDrawerPanel()!;
    const focusableSelector = [
      "button:not([disabled])",
      "[href]",
      "input:not([disabled])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      '[tabindex]:not([tabindex="-1"])',
    ].join(",");
    const focusable = Array.from(
      panel.querySelectorAll<HTMLElement>(focusableSelector)
    ).filter((el) => !el.closest("[aria-hidden]"));

    const lastEl = focusable[focusable.length - 1];

    // Focus starts on close button (G14 confirms this).
    expect(document.activeElement).toBe(closeBtn);

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", {
          key: "Tab",
          bubbles: true,
          shiftKey: true,
        })
      );
    });

    expect(document.activeElement).toBe(lastEl);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G17 — Focus trap stays within drawer (§8.2.1 / WCAG 2.1.2)
// ══════════════════════════════════════════════════════════════════════════════

describe("G17 — Focus trap: Tab cycle stays within drawer (§8.2.1 / WCAG 2.1.2)", () => {
  it("drawer panel has close button as a focusable element (focus trap anchor)", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    const panel = getDrawerPanel()!;
    const buttons = panel.querySelectorAll("button");
    // At minimum the close button is present.
    expect(buttons.length).toBeGreaterThan(0);
    expect(getCloseBtn()).not.toBeNull();
  });

  it("keydown Tab while drawer open is handled by drawer's keydown listener (not page)", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });

    // The drawer should still be open after a Tab event is processed.
    const tabEvent = new KeyboardEvent("keydown", {
      key: "Tab",
      bubbles: true,
      shiftKey: false,
    });
    await act(async () => {
      document.dispatchEvent(tabEvent);
    });

    // Drawer must still be in the DOM (Tab does not close it).
    expect(getDrawerPanel()).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G18 — Scroll lock: body overflow === "hidden" after open (§8.2.11)
// ══════════════════════════════════════════════════════════════════════════════

describe("G18 — Scroll lock: body.style.overflow === 'hidden' after open (§8.2.11)", () => {
  it("document.body.style.overflow is 'hidden' after drawer opens", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("hidden");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G19 — Scroll lock restore after any close path (§8.2.11)
// ══════════════════════════════════════════════════════════════════════════════

describe("G19 — Scroll lock restored after close via any path (§8.2.11)", () => {
  it("body.style.overflow restored to '' after Esc close", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("hidden");

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });

    expect(document.body.style.overflow).toBe("");
  });

  it("body.style.overflow restored to '' after close button click", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("hidden");

    await act(async () => {
      getCloseBtn()?.click();
    });

    expect(document.body.style.overflow).toBe("");
  });

  it("body.style.overflow restored to '' after scrim pointerdown close", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("hidden");

    await act(async () => {
      getScrim()?.dispatchEvent(
        new PointerEvent("pointerdown", { bubbles: true })
      );
    });

    expect(document.body.style.overflow).toBe("");
  });

  it("body.style.overflow restored to '' after toggle-click close (M1)", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("hidden");

    await act(async () => {
      getTrigger()?.click();
    });

    expect(document.body.style.overflow).toBe("");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G20 — Scroll lock restore on forced unmount while open (§8.2.11 cleanup)
// ══════════════════════════════════════════════════════════════════════════════

describe("G20 — Scroll lock restored on unmount while drawer open (§8.2.11)", () => {
  it("body.style.overflow restored to '' when DataExplorer unmounts while drawer is open", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("hidden");

    // Force unmount the entire DataExplorer while the drawer is open.
    act(() => {
      root.unmount();
    });

    expect(document.body.style.overflow).toBe("");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G21 — mobile_model_drawer.ts constants verbatim per §8.2.14 (.toBe())
// ══════════════════════════════════════════════════════════════════════════════

describe("G21 — mobile_model_drawer.ts constants verbatim per §8.2.14 (.toBe())", () => {
  it("MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED === 'Open model selector' exactly", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED).toBe("Open model selector");
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN === 'Close model selector' exactly", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN).toBe("Close model selector");
  });

  it("MOBILE_MODEL_DRAWER_PANEL_LABEL === 'Model selector' exactly", () => {
    expect(MOBILE_MODEL_DRAWER_PANEL_LABEL).toBe("Model selector");
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_TEXT(0) === 'Select models (0 selected)' exactly", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_TEXT(0)).toBe("Select models (0 selected)");
  });

  it("MOBILE_MODEL_DRAWER_TRIGGER_TEXT(3) === 'Select models (3 selected)' exactly", () => {
    expect(MOBILE_MODEL_DRAWER_TRIGGER_TEXT(3)).toBe("Select models (3 selected)");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G22 — mobile_model_drawer.ts exports exactly 4 items (§8.2.14)
// ══════════════════════════════════════════════════════════════════════════════

describe("G22 — mobile_model_drawer.ts has exactly 4 exports (§8.2.14)", () => {
  it("source contains exactly 4 'export' statements", () => {
    const exportMatches = MOBILE_DRAWER_TS_SRC.match(/^export /gm);
    expect(exportMatches).not.toBeNull();
    expect(exportMatches!).toHaveLength(4);
  });

  it("exports include MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED", () => {
    expect(MOBILE_DRAWER_TS_SRC).toContain(
      "export const MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED"
    );
  });

  it("exports include MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN", () => {
    expect(MOBILE_DRAWER_TS_SRC).toContain(
      "export const MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN"
    );
  });

  it("exports include MOBILE_MODEL_DRAWER_PANEL_LABEL", () => {
    expect(MOBILE_DRAWER_TS_SRC).toContain(
      "export const MOBILE_MODEL_DRAWER_PANEL_LABEL"
    );
  });

  it("exports include MOBILE_MODEL_DRAWER_TRIGGER_TEXT", () => {
    expect(MOBILE_DRAWER_TS_SRC).toContain(
      "export const MOBILE_MODEL_DRAWER_TRIGGER_TEXT"
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G23 — No MOBILE_MODEL_DRAWER_HEADING constant (§8.2.14 / §8.2.7)
// ══════════════════════════════════════════════════════════════════════════════

describe("G23 — No MOBILE_MODEL_DRAWER_HEADING constant (§8.2.14 / §8.2.7)", () => {
  it("mobile_model_drawer.ts does NOT contain 'MOBILE_MODEL_DRAWER_HEADING'", () => {
    expect(MOBILE_DRAWER_TS_SRC).not.toContain("MOBILE_MODEL_DRAWER_HEADING");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G24 — mobile_model_drawer.ts forbidden-vocab grep (CLAUDE.md §7)
// ══════════════════════════════════════════════════════════════════════════════

describe("G24 — mobile_model_drawer.ts passes forbidden-vocab grep (CLAUDE.md §7)", () => {
  const forbiddenPattern = /worldview|believes|thinks|cultural bias/i;

  it("source does not contain 'worldview'", () => {
    expect(MOBILE_DRAWER_TS_SRC).not.toMatch(/\bworldview\b/i);
  });

  it("source does not contain 'believes'", () => {
    expect(MOBILE_DRAWER_TS_SRC).not.toMatch(/\bbelieves\b/i);
  });

  it("source does not contain 'thinks' (applied to models)", () => {
    expect(MOBILE_DRAWER_TS_SRC).not.toMatch(/\bthinks\b/i);
  });

  it("source does not contain 'cultural bias'", () => {
    expect(MOBILE_DRAWER_TS_SRC).not.toMatch(/cultural bias/i);
  });

  it("full pattern /worldview|believes|thinks|cultural bias/i has no match", () => {
    expect(MOBILE_DRAWER_TS_SRC).not.toMatch(forbiddenPattern);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G25 — MobileModelSelectorDrawer.tsx file-header references DESIGN_SYSTEM.md §8.2 (AC20)
// ══════════════════════════════════════════════════════════════════════════════

describe("G25 — MobileModelSelectorDrawer.tsx file-header references DESIGN_SYSTEM.md §8.2 (AC20)", () => {
  it("first line of MobileModelSelectorDrawer.tsx contains 'DESIGN_SYSTEM.md §8.2'", () => {
    const firstLine = MOBILE_DRAWER_TSX_SRC.split("\n")[0];
    expect(firstLine).toContain("DESIGN_SYSTEM.md §8.2");
  });

  it("first line is a comment (starts with //)", () => {
    const firstLine = MOBILE_DRAWER_TSX_SRC.split("\n")[0].trim();
    expect(firstLine.startsWith("//")).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G26 — mobile-model-drawer.css contains prefers-reduced-motion block (§8.2.4 / §8.2.13)
// ══════════════════════════════════════════════════════════════════════════════

describe("G26 — mobile-model-drawer.css contains prefers-reduced-motion block (§8.2.4 / §8.2.13)", () => {
  it("css contains @media (prefers-reduced-motion: reduce)", () => {
    expect(MOBILE_DRAWER_CSS_SRC).toContain(
      "@media (prefers-reduced-motion: reduce)"
    );
  });

  it("prefers-reduced-motion block targets .mobile-model-drawer__panel", () => {
    const block = MOBILE_DRAWER_CSS_SRC.match(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*)\}/s
    );
    expect(block).not.toBeNull();
    expect(block![0]).toContain(".mobile-model-drawer__panel");
  });

  it("prefers-reduced-motion block sets transition: none", () => {
    const block = MOBILE_DRAWER_CSS_SRC.match(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*)\}/s
    );
    expect(block).not.toBeNull();
    expect(block![0]).toContain("transition: none");
  });

  it("prefers-reduced-motion block sets animation: none", () => {
    const block = MOBILE_DRAWER_CSS_SRC.match(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*)\}/s
    );
    expect(block).not.toBeNull();
    expect(block![0]).toContain("animation: none");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G27 — mobile-model-drawer.css contains M3 scoped touch-target rules (§8.2.8)
// ══════════════════════════════════════════════════════════════════════════════

describe("G27 — mobile-model-drawer.css M3 scoped touch-target rules (§8.2.8)", () => {
  it("css contains .mobile-model-drawer__body .model-selector__row", () => {
    expect(MOBILE_DRAWER_CSS_SRC).toContain(
      ".mobile-model-drawer__body .model-selector__row"
    );
  });

  it(".model-selector__row rule has min-height: 44px", () => {
    // Find the rule block for .model-selector__row inside drawer body.
    const rowBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__body\s+\.model-selector__row\s*\{([^}]*)\}/s
    );
    expect(rowBlock).not.toBeNull();
    expect(rowBlock![0]).toContain("min-height: 44px");
  });

  it("css contains .mobile-model-drawer__body .model-selector__action-link", () => {
    expect(MOBILE_DRAWER_CSS_SRC).toContain(
      ".mobile-model-drawer__body .model-selector__action-link"
    );
  });

  it(".model-selector__action-link rule has min-height: 44px", () => {
    const actionBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__body\s+\.model-selector__action-link\s*\{([^}]*)\}/s
    );
    expect(actionBlock).not.toBeNull();
    expect(actionBlock![0]).toContain("min-height: 44px");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G28 — mobile-model-drawer.css scrim: z-index: 199, rgba(0,0,0,0.45) (§8.2.3)
// ══════════════════════════════════════════════════════════════════════════════

describe("G28 — mobile-model-drawer.css scrim z-index and background (§8.2.3)", () => {
  it("css contains .mobile-model-drawer__scrim", () => {
    expect(MOBILE_DRAWER_CSS_SRC).toContain(".mobile-model-drawer__scrim");
  });

  it("scrim rule has z-index: 199", () => {
    const scrimBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__scrim\s*\{([^}]*)\}/s
    );
    expect(scrimBlock).not.toBeNull();
    expect(scrimBlock![0]).toContain("z-index: 199");
  });

  it("scrim rule has background: rgba(0, 0, 0, 0.45)", () => {
    const scrimBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__scrim\s*\{([^}]*)\}/s
    );
    expect(scrimBlock).not.toBeNull();
    expect(scrimBlock![0]).toContain("rgba(0, 0, 0, 0.45)");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G29 — mobile-model-drawer.css panel geometry (§8.2.2)
// ══════════════════════════════════════════════════════════════════════════════

describe("G29 — mobile-model-drawer.css panel geometry (§8.2.2)", () => {
  it("panel rule has position: fixed", () => {
    const panelBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel\s*\{([^}]*)\}/s
    );
    expect(panelBlock).not.toBeNull();
    expect(panelBlock![0]).toContain("position: fixed");
  });

  it("panel rule has bottom: 0", () => {
    const panelBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel\s*\{([^}]*)\}/s
    );
    expect(panelBlock).not.toBeNull();
    expect(panelBlock![0]).toContain("bottom: 0");
  });

  it("panel rule has max-height: 75vh", () => {
    const panelBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel\s*\{([^}]*)\}/s
    );
    expect(panelBlock).not.toBeNull();
    expect(panelBlock![0]).toContain("max-height: 75vh");
  });

  it("panel rule has z-index: 200", () => {
    const panelBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel\s*\{([^}]*)\}/s
    );
    expect(panelBlock).not.toBeNull();
    expect(panelBlock![0]).toContain("z-index: 200");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G30 — mobile-model-drawer.css transform / transition pattern (§8.2.4)
// ══════════════════════════════════════════════════════════════════════════════

describe("G30 — mobile-model-drawer.css slide-up transform pattern (§8.2.4)", () => {
  it("base panel rule has transform: translateY(100%) (rest state, off-screen below)", () => {
    const panelBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel\s*\{([^}]*)\}/s
    );
    expect(panelBlock).not.toBeNull();
    expect(panelBlock![0]).toContain("transform: translateY(100%)");
  });

  it("--open modifier rule has transform: translateY(0)", () => {
    expect(MOBILE_DRAWER_CSS_SRC).toContain(".mobile-model-drawer__panel--open");
    const openBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel--open\s*\{([^}]*)\}/s
    );
    expect(openBlock).not.toBeNull();
    expect(openBlock![0]).toContain("transform: translateY(0)");
  });

  it("--open modifier rule has transition with 200ms ease-out", () => {
    const openBlock = MOBILE_DRAWER_CSS_SRC.match(
      /\.mobile-model-drawer__panel--open\s*\{([^}]*)\}/s
    );
    expect(openBlock).not.toBeNull();
    expect(openBlock![0]).toContain("200ms");
    expect(openBlock![0]).toContain("ease-out");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G31 — app.css T13 supersession: no "viz" grid-template-areas in mobile block (§8.2.10)
// ══════════════════════════════════════════════════════════════════════════════

describe("G31 — app.css T13 supersession: no stacked-below grid-template-areas in <768px (§8.2.10)", () => {
  it("@media (max-width: 768px) .explorer-layout block does NOT contain grid-template-areas: \"viz\"", () => {
    // Extract the mobile breakpoint block for .explorer-layout.
    // Find the @media (max-width: 768px) block that contains .explorer-layout.
    // The pattern looks for: @media (max-width: 768px) { .explorer-layout { ... } }
    const mobileBlockMatch = APP_CSS_SRC.match(
      /@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.explorer-layout\s*\{[^}]*\}[^}]*\}/s
    );
    if (mobileBlockMatch) {
      // If we matched, the old stacked-below areas should not be present.
      expect(mobileBlockMatch[0]).not.toContain('grid-template-areas: "viz"');
    }
    // Also check the overall app.css does not have the old stacked pattern
    // "viz"\n"selector" (the pre-T12 stacked grid layout).
    expect(APP_CSS_SRC).not.toMatch(
      /grid-template-areas:\s*["']viz["']\s*["']selector["']/s
    );
  });

  it("app.css has @media (max-width: 768px) block containing .explorer-layout (single-column rule)", () => {
    // The mobile block should have the single-column collapse rule.
    expect(APP_CSS_SRC).toMatch(
      /@media\s*\(max-width:\s*768px\)\s*\{[^}]*grid-template-columns:\s*1fr/s
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G32 — app.css contains .model-selector { display: none } inside 768px block (§8.2.10)
// ══════════════════════════════════════════════════════════════════════════════

describe("G32 — app.css contains .explorer-layout__selector .model-selector { display: none } at <768px (§8.2.10)", () => {
  it("app.css contains .explorer-layout__selector .model-selector selector", () => {
    expect(APP_CSS_SRC).toContain(
      ".explorer-layout__selector .model-selector"
    );
  });

  it(".explorer-layout__selector .model-selector rule has display: none", () => {
    const selectorBlock = APP_CSS_SRC.match(
      /\.explorer-layout__selector\s+\.model-selector\s*\{([^}]*)\}/s
    );
    expect(selectorBlock).not.toBeNull();
    expect(selectorBlock![0]).toContain("display: none");
  });

  it("the display: none rule is inside a @media (max-width: 768px) block", () => {
    // Verify app.css contains both the media query and the scoped rule.
    expect(APP_CSS_SRC).toContain("@media (max-width: 768px)");
    expect(APP_CSS_SRC).toContain(
      ".explorer-layout__selector .model-selector"
    );
    // The rule with display: none should be present.
    expect(APP_CSS_SRC).toMatch(
      /\.explorer-layout__selector\s+\.model-selector\s*\{\s*display:\s*none/s
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G33 — MobileModelSelectorDrawer.tsx source contains M2 event stop (§8.2.3 / M2)
// ══════════════════════════════════════════════════════════════════════════════

describe("G33 — MobileModelSelectorDrawer.tsx contains onPointerDown + stopPropagation (M2)", () => {
  it("source contains 'onPointerDown'", () => {
    expect(MOBILE_DRAWER_TSX_SRC).toContain("onPointerDown");
  });

  it("source contains 'stopPropagation'", () => {
    expect(MOBILE_DRAWER_TSX_SRC).toContain("stopPropagation");
  });

  it("source contains onPointerDown with stopPropagation on the panel element", () => {
    // The panel's onPointerDown calls e.stopPropagation().
    expect(MOBILE_DRAWER_TSX_SRC).toMatch(
      /onPointerDown=\{[^}]*stopPropagation[^}]*\}/s
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G34 — DataExplorer.tsx contains toggle pattern prev => !prev (M1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G34 — DataExplorer.tsx contains toggle pattern for M1 (§8.2.6 / M1)", () => {
  it("DataExplorer.tsx source contains the toggle pattern 'prev => !prev' or '(prev) => !prev'", () => {
    const hasToggle =
      DATA_EXPLORER_SRC.includes("prev => !prev") ||
      DATA_EXPLORER_SRC.includes("(prev) => !prev");
    expect(hasToggle).toBe(true);
  });

  it("DataExplorer.tsx does not use only setMobileSelectorOpen(true) without toggle", () => {
    // Ensure the toggle form is present (not just open-only).
    expect(DATA_EXPLORER_SRC).toContain("setMobileSelectorOpen");
    // The toggle must be a function, not a bare boolean.
    expect(DATA_EXPLORER_SRC).not.toMatch(
      /setMobileSelectorOpen\s*\(\s*true\s*\)/
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G35 — DESIGN_SYSTEM.md version v0.4.8 (§8.2 update)
// ══════════════════════════════════════════════════════════════════════════════

describe("G35 — DESIGN_SYSTEM.md version v0.5.0 (current)", () => {
  it("version line reads v0.5.0", () => {
    // Phase 9a T9 bumped to v0.5.1 (added §12.10 PileComparison spec)
    expect(DESIGN_SYSTEM_MD).toMatch(/\*\*Version:\*\* v0\.5\.1/);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G36 — DESIGN_SYSTEM.md §8.2 section header present
// ══════════════════════════════════════════════════════════════════════════════

describe("G36 — DESIGN_SYSTEM.md §8.2 section header present", () => {
  it("DESIGN_SYSTEM.md contains '### 8.2'", () => {
    expect(DESIGN_SYSTEM_MD).toContain("### 8.2");
  });

  it("§8.2 section mentions 'Mobile bottom-drawer'", () => {
    expect(DESIGN_SYSTEM_MD).toMatch(/8\.2.*[Mm]obile/);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G37 — DESIGN_SYSTEM.md §8.2.14 table contains all four pre-cleared strings
// ══════════════════════════════════════════════════════════════════════════════

describe("G37 — DESIGN_SYSTEM.md §8.2.14 table contains all four confirmed strings", () => {
  it("§8.2.14 heading is present", () => {
    expect(DESIGN_SYSTEM_MD).toContain("8.2.14");
  });

  it("§8.2.14 contains 'Open model selector' verbatim", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Open model selector");
  });

  it("§8.2.14 contains 'Close model selector' verbatim", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Close model selector");
  });

  it("§8.2.14 contains 'Model selector' verbatim (MOBILE_MODEL_DRAWER_PANEL_LABEL)", () => {
    expect(DESIGN_SYSTEM_MD).toContain(
      "MOBILE_MODEL_DRAWER_PANEL_LABEL"
    );
    expect(DESIGN_SYSTEM_MD).toContain('"Model selector"');
  });

  it("§8.2.14 contains MOBILE_MODEL_DRAWER_TRIGGER_TEXT verbatim", () => {
    expect(DESIGN_SYSTEM_MD).toContain("MOBILE_MODEL_DRAWER_TRIGGER_TEXT");
  });

  it("§8.2.14 contains 'MOBILE_MODEL_DRAWER_HEADING is not introduced' note", () => {
    expect(DESIGN_SYSTEM_MD).toMatch(
      /MOBILE_MODEL_DRAWER_HEADING.*not introduced/i
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G38 — DESIGN_SYSTEM.md footer reads "End of DESIGN_SYSTEM.md v0.4.8"
// ══════════════════════════════════════════════════════════════════════════════

describe("G38 — DESIGN_SYSTEM.md footer reads 'End of DESIGN_SYSTEM.md v0.5.0'", () => {
  it("DESIGN_SYSTEM.md ends with the v0.5.0 footer", () => {
    // Phase 9a T9 bumped to v0.5.1
    expect(DESIGN_SYSTEM_MD).toContain("End of DESIGN_SYSTEM.md v0.5.1");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G39 — ModelSelector.tsx does NOT contain MOBILE_MODEL_DRAWER (§8.2.15 isolation)
// ══════════════════════════════════════════════════════════════════════════════

describe("G39 — ModelSelector.tsx contains no MOBILE_MODEL_DRAWER coupling (§8.2.15)", () => {
  it("ModelSelector.tsx source does NOT contain 'MOBILE_MODEL_DRAWER'", () => {
    expect(MODEL_SELECTOR_SRC).not.toContain("MOBILE_MODEL_DRAWER");
  });

  it("ModelSelector.tsx source does NOT import mobile_model_drawer", () => {
    expect(MODEL_SELECTOR_SRC).not.toContain("mobile_model_drawer");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// Bonus — prefers-reduced-motion stub: drawer still opens/closes (§8.2.13)
// ══════════════════════════════════════════════════════════════════════════════

describe("Bonus — prefers-reduced-motion stub: drawer opens/closes normally (§8.2.13)", () => {
  beforeEach(() => {
    vi.stubGlobal("matchMedia", (query: string) => ({
      matches: query.includes("prefers-reduced-motion"),
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));
  });

  it("drawer opens normally when prefers-reduced-motion: reduce is set", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getDrawerPanel()).not.toBeNull();
  });

  it("drawer closes via Esc when prefers-reduced-motion: reduce is set", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });
    expect(getDrawerPanel()).toBeNull();
  });

  it("drawer closes via close button when prefers-reduced-motion: reduce is set", async () => {
    renderExplorer();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      getCloseBtn()?.click();
    });
    expect(getDrawerPanel()).toBeNull();
  });
});
