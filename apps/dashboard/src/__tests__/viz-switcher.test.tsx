// @vitest-environment jsdom
/**
 * VizSwitcher component tests.
 *
 * Uses jsdom environment (per-file override via @vitest-environment directive).
 * Renders components with React 19 createRoot + act().
 * No @testing-library/react — DOM access via standard Web APIs.
 *
 * Required tests per T8 spec:
 *   1. Renders 4 tabs.
 *   2. Active tab (MDS Plot) has aria-selected="true"; others "false".
 *   3. Disabled tabs have aria-disabled="true".
 *   4. Disabled tabs are FOCUSABLE (tabIndex={0}) per DESIGN_SYSTEM.md §12.3.
 *   5. Disabled tabs have title="Coming in a future update" (exact match).
 *   6. Click on active tab calls onTabChange("mds").
 *   7. Click on disabled tab does NOT call onTabChange.
 *   8. ARIA: container has role="tablist", tabs have role="tab".
 *   9. Active tab has visual indicator class (viz-switcher__tab--active).
 *  10. Keyboard: ArrowRight / ArrowLeft moves focus between tabs.
 *  11. Enter / Space on active tab calls onTabChange; on disabled tab does not.
 *
 * CLAUDE.md §6 R9: no real API calls.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { VizSwitcher } from "../components/VizSwitcher";
import type { VizSwitcherProps } from "../components/VizSwitcher";

// ── Render helper ─────────────────────────────────────────────────────────────

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

function renderSwitcher(props: VizSwitcherProps): void {
  act(() => {
    root.render(createElement(VizSwitcher, props));
  });
}

function getTabs(): NodeListOf<HTMLButtonElement> {
  return container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("VizSwitcher — tab count", () => {
  it("renders exactly 5 tabs (Phase 9a T10 — Centrality added)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    expect(tabs.length).toBe(5);
  });
});

describe("VizSwitcher — tab labels", () => {
  it("renders MDS Plot, Free Lists, Similarity, Centrality, and Drift tabs", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const labels = Array.from(tabs).map((t) => t.textContent?.trim());
    expect(labels).toContain("MDS Plot");
    expect(labels).toContain("Free Lists");
    expect(labels).toContain("Similarity");
    expect(labels).toContain("Centrality");
    expect(labels).toContain("Drift");
  });
});

describe("VizSwitcher — aria-selected", () => {
  it("MDS Plot tab has aria-selected='true'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = Array.from(tabs).find((t) => t.textContent?.trim() === "MDS Plot");
    expect(mdsTab).toBeDefined();
    expect(mdsTab!.getAttribute("aria-selected")).toBe("true");
  });

  it("Free Lists tab has aria-selected='false'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists");
    expect(tab!.getAttribute("aria-selected")).toBe("false");
  });

  it("Similarity tab has aria-selected='false'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity");
    expect(tab!.getAttribute("aria-selected")).toBe("false");
  });

  it("Drift tab has aria-selected='false'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Drift");
    expect(tab!.getAttribute("aria-selected")).toBe("false");
  });
});

describe("VizSwitcher — aria-disabled", () => {
  // Phase 6 T7: Free Lists tab is now active (not disabled). Only Drift
  // remains disabled.
  // Phase 6 T5: Similarity tab is now active (not disabled). Only Drift remains.
  it("Free Lists tab does NOT have aria-disabled (Phase 6 T7 — tab is now active)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists");
    expect(tab!.getAttribute("aria-disabled")).toBeNull();
  });

  it("Similarity tab does NOT have aria-disabled (Phase 6 T5 — tab is now active)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity");
    expect(tab!.getAttribute("aria-disabled")).toBeNull();
  });

  it("Drift tab has aria-disabled='true'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Drift");
    expect(tab!.getAttribute("aria-disabled")).toBe("true");
  });

  it("MDS Plot tab does NOT have aria-disabled", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = Array.from(tabs).find((t) => t.textContent?.trim() === "MDS Plot");
    // Active tab must not carry aria-disabled.
    expect(mdsTab!.getAttribute("aria-disabled")).toBeNull();
  });
});

describe("VizSwitcher — focusability (§12.3 binding)", () => {
  it("Free Lists tab is focusable (tabIndex is not -1)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists");
    // Per §12.3 binding: disabled tabs MUST be focusable. tabIndex must NOT be -1.
    expect(tab!.tabIndex).not.toBe(-1);
  });

  it("Similarity tab is focusable (tabIndex is not -1)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity");
    expect(tab!.tabIndex).not.toBe(-1);
  });

  it("Drift tab is focusable (tabIndex is not -1)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Drift");
    expect(tab!.tabIndex).not.toBe(-1);
  });

  it("MDS Plot tab has tabIndex={0}", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = Array.from(tabs).find((t) => t.textContent?.trim() === "MDS Plot");
    expect(mdsTab!.tabIndex).toBe(0);
  });
});

describe("VizSwitcher — tooltip text (§12.3 binding)", () => {
  // Phase 6 T7: Free Lists tab is now active — no tooltip.
  it("Free Lists tab does NOT have tooltip (Phase 6 T7 — tab is now active)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists");
    // Active tab has no tooltip.
    expect(tab!.title).toBeFalsy();
  });

  // Phase 6 T5: Similarity tab is now active — no tooltip.
  it("Similarity tab does NOT have tooltip (Phase 6 T5 — tab is now active)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity");
    // Active tab has no tooltip.
    expect(tab!.title).toBeFalsy();
  });

  it("Drift tab has title='Coming in a future update'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Drift");
    expect(tab!.title).toBe("Coming in a future update");
  });

  it("MDS Plot tab does NOT have a tooltip", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = Array.from(tabs).find((t) => t.textContent?.trim() === "MDS Plot");
    expect(mdsTab!.title).toBeFalsy();
  });
});

describe("VizSwitcher — click interactions", () => {
  it("clicking MDS Plot tab calls onTabChange('mds')", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const mdsTab = Array.from(tabs).find((t) => t.textContent?.trim() === "MDS Plot")!;

    act(() => {
      mdsTab.click();
    });

    expect(onTabChange).toHaveBeenCalledOnce();
    expect(onTabChange).toHaveBeenCalledWith("mds");
  });

  // Phase 6 T7: clicking Free Lists now calls onTabChange('freelist').
  it("clicking Free Lists tab calls onTabChange('freelist')", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists")!;

    act(() => {
      tab.click();
    });

    expect(onTabChange).toHaveBeenCalledOnce();
    expect(onTabChange).toHaveBeenCalledWith("freelist");
  });

  // Phase 6 T5: clicking Similarity now calls onTabChange('similarity').
  it("clicking Similarity tab calls onTabChange('similarity') (Phase 6 T5 — tab is now active)", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity")!;

    act(() => {
      tab.click();
    });

    expect(onTabChange).toHaveBeenCalledOnce();
    expect(onTabChange).toHaveBeenCalledWith("similarity");
  });

  it("clicking Drift tab does NOT call onTabChange", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Drift")!;

    act(() => {
      tab.click();
    });

    expect(onTabChange).not.toHaveBeenCalled();
  });
});

describe("VizSwitcher — ARIA roles", () => {
  it("container has role='tablist'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tablist = container.querySelector("[role='tablist']");
    expect(tablist).not.toBeNull();
  });

  it("tablist has aria-label='Visualization view'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tablist = container.querySelector("[role='tablist']");
    expect(tablist?.getAttribute("aria-label")).toBe("Visualization view");
  });

  it("each tab has role='tab'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    tabs.forEach((tab) => {
      expect(tab.getAttribute("role")).toBe("tab");
    });
  });
});

describe("VizSwitcher — active tab visual indicator", () => {
  it("MDS Plot tab has viz-switcher__tab--active class", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = Array.from(tabs).find((t) => t.textContent?.trim() === "MDS Plot");
    // §12.3: active tab must have a non-color visual indicator.
    // The CSS class viz-switcher__tab--active applies the 3px bottom border + bold weight.
    expect(mdsTab!.classList.contains("viz-switcher__tab--active")).toBe(true);
  });

  it("disabled tabs do NOT have viz-switcher__tab--active class", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const disabledTabs = Array.from(tabs).filter(
      (t) => t.textContent?.trim() !== "MDS Plot"
    );
    disabledTabs.forEach((tab) => {
      expect(tab.classList.contains("viz-switcher__tab--active")).toBe(false);
    });
  });

  // Phase 6 T5: only Drift is still disabled (Similarity is now active).
  it("Only Drift tab has viz-switcher__tab--disabled class (Phase 6 T5)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const driftTab = Array.from(tabs).find((t) => t.textContent?.trim() === "Drift");
    expect(driftTab!.classList.contains("viz-switcher__tab--disabled")).toBe(true);
    // Verify exactly one disabled tab remains.
    const disabledTabs = Array.from(tabs).filter((t) =>
      t.classList.contains("viz-switcher__tab--disabled")
    );
    expect(disabledTabs.length).toBe(1);
  });

  it("Similarity tab does NOT have viz-switcher__tab--disabled class (Phase 6 T5 — active)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity")!;
    expect(tab.classList.contains("viz-switcher__tab--disabled")).toBe(false);
  });

  it("Free Lists tab does NOT have viz-switcher__tab--disabled class (Phase 6 T7)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists")!;
    expect(tab.classList.contains("viz-switcher__tab--disabled")).toBe(false);
  });
});

describe("VizSwitcher — keyboard navigation", () => {
  it("ArrowRight from MDS Plot moves focus to Free Lists", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = tabs[0];
    const freeListsTab = tabs[1];

    act(() => {
      mdsTab.focus();
      mdsTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(freeListsTab);
  });

  it("ArrowLeft from Free Lists moves focus back to MDS Plot", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = tabs[0];
    const freeListsTab = tabs[1];

    act(() => {
      freeListsTab.focus();
      freeListsTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(mdsTab);
  });

  it("ArrowRight from Drift (last tab) wraps to MDS Plot (first tab)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const driftTab = tabs[tabs.length - 1];
    const mdsTab = tabs[0];

    act(() => {
      driftTab.focus();
      driftTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(mdsTab);
  });

  it("Enter on MDS Plot tab calls onTabChange('mds')", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const mdsTab = tabs[0];

    act(() => {
      mdsTab.focus();
      mdsTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
    });

    expect(onTabChange).toHaveBeenCalledWith("mds");
  });

  // Phase 9a T10: tabs[3] is now Centrality (active). Use Drift (tabs[4]) for disabled test.
  it("Enter on disabled tab (Drift) does NOT call onTabChange", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const driftTab = tabs[4];

    act(() => {
      driftTab.focus();
      driftTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
    });

    expect(onTabChange).not.toHaveBeenCalled();
  });

  // Phase 6 T5: Enter on Similarity now calls onTabChange('similarity').
  it("Enter on Similarity tab calls onTabChange('similarity') (Phase 6 T5)", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const similarityTab = tabs[2];

    act(() => {
      similarityTab.focus();
      similarityTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
    });

    expect(onTabChange).toHaveBeenCalledWith("similarity");
  });

  it("Enter on Free Lists tab calls onTabChange('freelist') (Phase 6 T7)", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const freeListsTab = tabs[1];

    act(() => {
      freeListsTab.focus();
      freeListsTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
    });

    expect(onTabChange).toHaveBeenCalledWith("freelist");
  });

  // Phase 9a T10: tabs[3] is now Centrality (active). Use Drift (tabs[4]) for disabled Space test.
  it("Space on disabled tab (Drift) does NOT call onTabChange", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const driftTab = tabs[4];

    act(() => {
      driftTab.focus();
      driftTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: " ", bubbles: true })
      );
    });

    expect(onTabChange).not.toHaveBeenCalled();
  });
});

// ── Gap-fill tests (Phase 5 T8 Tester pass, 2026-05-10) ─────────────────────
//
// Gaps identified during T8 Tester inspection:
//
//   Gap G1: Space on active MDS tab — spec comment at line 20 says "Enter / Space
//            on active tab calls onTabChange" but only Enter was tested for the
//            active case. Space on disabled was tested; Space on active was not.
//
//   Gap G2: resolveFragmentOnMount with real hash values — the app-state.test.ts
//            calls the function in a node environment where window is absent, so
//            the DISABLED_FRAGMENTS branch (console.warn + return "mds") was never
//            exercised. jsdom is available here; test all three paths.
//
//   Gap G3: ArrowLeft wrap-around — ArrowRight from last→first is tested; the
//            symmetric ArrowLeft from first (MDS Plot) → last (Drift) is not.
//
// CLAUDE.md §6 R9: no real API calls.

import { resolveFragmentOnMount } from "../components/VizSwitcher";

describe("VizSwitcher — Gap G1: Space on active tab (§12.3 binding)", () => {
  it("Space on MDS Plot tab calls onTabChange('mds')", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const mdsTab = tabs[0];

    act(() => {
      mdsTab.focus();
      mdsTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: " ", bubbles: true })
      );
    });

    // §12.3: both Enter and Space must activate the focused active tab.
    expect(onTabChange).toHaveBeenCalledOnce();
    expect(onTabChange).toHaveBeenCalledWith("mds");
  });
});

describe("VizSwitcher — Gap G2: resolveFragmentOnMount with real hash values (jsdom)", () => {
  afterEach(() => {
    // Restore hash to neutral state after each test.
    window.location.hash = "";
  });

  it("returns 'mds' when hash is empty", () => {
    window.location.hash = "";
    expect(resolveFragmentOnMount()).toBe("mds");
  });

  it("returns 'mds' when hash is '#mds'", () => {
    window.location.hash = "#mds";
    expect(resolveFragmentOnMount()).toBe("mds");
  });

  // Phase 6 T7: #freelist is now an active tab — returns 'freelist', no warning.
  it("returns 'freelist' when hash is '#freelist' (Phase 6 T7 — active tab)", () => {
    window.location.hash = "#freelist";
    expect(resolveFragmentOnMount()).toBe("freelist");
  });

  // Phase 6 T5: #similarity is now an active tab — returns 'similarity', no warning.
  it("returns 'similarity' when hash is '#similarity' (Phase 6 T5 — active tab)", () => {
    window.location.hash = "#similarity";
    expect(resolveFragmentOnMount()).toBe("similarity");
  });

  it("returns 'mds' when hash is '#drift' (still disabled)", () => {
    window.location.hash = "#drift";
    expect(resolveFragmentOnMount()).toBe("mds");
  });

  // #freelist is no longer a DISABLED_FRAGMENT — no warn emitted.
  it("does NOT emit console.warn for #freelist (Phase 6 T7 — active)", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    window.location.hash = "#freelist";
    resolveFragmentOnMount();
    expect(warnSpy).not.toHaveBeenCalled();
    warnSpy.mockRestore();
  });

  // Phase 6 T5: #similarity is now active — no warn emitted.
  it("does NOT emit console.warn for #similarity (Phase 6 T5 — active)", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    window.location.hash = "#similarity";
    resolveFragmentOnMount();
    expect(warnSpy).not.toHaveBeenCalled();
    warnSpy.mockRestore();
  });

  it("emits console.warn for DISABLED_FRAGMENTS hash (#drift)", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    window.location.hash = "#drift";
    resolveFragmentOnMount();
    expect(warnSpy).toHaveBeenCalledOnce();
    expect(warnSpy.mock.calls[0][0]).toContain("drift");
    warnSpy.mockRestore();
  });

  it("does NOT emit console.warn for #mds (recognized active fragment)", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    window.location.hash = "#mds";
    resolveFragmentOnMount();
    expect(warnSpy).not.toHaveBeenCalled();
    warnSpy.mockRestore();
  });

  it("does NOT emit console.warn for empty hash", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    window.location.hash = "";
    resolveFragmentOnMount();
    expect(warnSpy).not.toHaveBeenCalled();
    warnSpy.mockRestore();
  });
});

describe("VizSwitcher — Gap G3: ArrowLeft wrap-around from first tab to last", () => {
  it("ArrowLeft from MDS Plot (first tab) wraps to Drift (last tab)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const mdsTab = tabs[0];
    const driftTab = tabs[tabs.length - 1];

    act(() => {
      mdsTab.focus();
      mdsTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(driftTab);
  });
});
