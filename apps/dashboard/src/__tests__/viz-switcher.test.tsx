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
  it("renders exactly 4 tabs", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    expect(tabs.length).toBe(4);
  });
});

describe("VizSwitcher — tab labels", () => {
  it("renders MDS Plot, Free Lists, Similarity, and Drift tabs", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const labels = Array.from(tabs).map((t) => t.textContent?.trim());
    expect(labels).toContain("MDS Plot");
    expect(labels).toContain("Free Lists");
    expect(labels).toContain("Similarity");
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
  it("Free Lists tab has aria-disabled='true'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists");
    expect(tab!.getAttribute("aria-disabled")).toBe("true");
  });

  it("Similarity tab has aria-disabled='true'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity");
    expect(tab!.getAttribute("aria-disabled")).toBe("true");
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
  it("Free Lists tab has title='Coming in a future update' (exact match)", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists");
    // §12.3: exact tooltip text required. No "Phase 6" or version-specific copy.
    expect(tab!.title).toBe("Coming in a future update");
  });

  it("Similarity tab has title='Coming in a future update'", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity");
    expect(tab!.title).toBe("Coming in a future update");
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

  it("clicking Free Lists tab does NOT call onTabChange", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Free Lists")!;

    act(() => {
      tab.click();
    });

    expect(onTabChange).not.toHaveBeenCalled();
  });

  it("clicking Similarity tab does NOT call onTabChange", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const tab = Array.from(tabs).find((t) => t.textContent?.trim() === "Similarity")!;

    act(() => {
      tab.click();
    });

    expect(onTabChange).not.toHaveBeenCalled();
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

  it("disabled tabs have viz-switcher__tab--disabled class", () => {
    renderSwitcher({ activeTab: "mds", onTabChange: vi.fn() });
    const tabs = getTabs();
    const disabledTabs = Array.from(tabs).filter(
      (t) => t.textContent?.trim() !== "MDS Plot"
    );
    disabledTabs.forEach((tab) => {
      expect(tab.classList.contains("viz-switcher__tab--disabled")).toBe(true);
    });
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

  it("Enter on disabled tab does NOT call onTabChange", () => {
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

    expect(onTabChange).not.toHaveBeenCalled();
  });

  it("Space on disabled tab does NOT call onTabChange", () => {
    const onTabChange = vi.fn();
    renderSwitcher({ activeTab: "mds", onTabChange });
    const tabs = getTabs();
    const similarityTab = tabs[2];

    act(() => {
      similarityTab.focus();
      similarityTab.dispatchEvent(
        new KeyboardEvent("keydown", { key: " ", bubbles: true })
      );
    });

    expect(onTabChange).not.toHaveBeenCalled();
  });
});
