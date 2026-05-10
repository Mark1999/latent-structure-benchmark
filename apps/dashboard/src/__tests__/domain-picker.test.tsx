// @vitest-environment jsdom
/**
 * DomainPicker component tests.
 *
 * Uses jsdom environment (per-file override via @vitest-environment directive).
 * Renders components with React 19 createRoot + act().
 * No @testing-library/react — DOM access via standard Web APIs.
 *
 * Tests required by T5 spec:
 *   1. Renders the right number of pills given domains prop.
 *   2. Active pill has aria-selected="true"; others "false".
 *   3. Disabled pill has aria-disabled="true" and remains in tab order.
 *   4. Click on available pill calls onSelect(slug).
 *   5. Click on disabled pill does NOT call onSelect.
 *   6. Keyboard: ArrowRight focuses next pill; ArrowLeft focuses previous; Enter activates.
 *   7. Tooltip text on disabled pill is "Coming in a future update" exactly.
 *
 * CLAUDE.md §6 R9: no real API calls.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { DomainPicker } from "../components/DomainPicker";
import type { Domain, DomainPickerProps } from "../components/DomainPicker";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const DOMAINS: Domain[] = [
  { slug: "family", label: "Family", available: true },
  { slug: "holidays", label: "Holidays", available: true },
  { slug: "food", label: "Food", available: false },
  { slug: "emotion", label: "Emotion", available: false },
];

// ── Render helper ─────────────────────────────────────────────────────────────

let container: HTMLDivElement;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
});

afterEach(() => {
  act(() => {
    createRoot(container).unmount();
  });
  container.remove();
});

function renderPicker(props: DomainPickerProps): void {
  act(() => {
    createRoot(container).render(createElement(DomainPicker, props));
  });
}

function getPills(): NodeListOf<HTMLButtonElement> {
  return container.querySelectorAll<HTMLButtonElement>("button[role='tab']");
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("DomainPicker — pill count", () => {
  it("renders the correct number of pills for the given domains prop", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    expect(pills.length).toBe(DOMAINS.length);
  });

  it("renders 2 pills when only 2 domains are provided", () => {
    const twoDomains: Domain[] = [
      { slug: "family", label: "Family", available: true },
      { slug: "holidays", label: "Holidays", available: true },
    ];
    renderPicker({ domains: twoDomains, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    expect(pills.length).toBe(2);
  });
});

describe("DomainPicker — aria-selected", () => {
  it("active pill has aria-selected='true'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const familyPill = Array.from(pills).find((p) => p.textContent === "Family");
    expect(familyPill).toBeDefined();
    expect(familyPill!.getAttribute("aria-selected")).toBe("true");
  });

  it("inactive available pill has aria-selected='false'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const holidaysPill = Array.from(pills).find((p) => p.textContent === "Holidays");
    expect(holidaysPill).toBeDefined();
    expect(holidaysPill!.getAttribute("aria-selected")).toBe("false");
  });

  it("disabled pill has aria-selected='false'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food");
    expect(foodPill).toBeDefined();
    expect(foodPill!.getAttribute("aria-selected")).toBe("false");
  });
});

describe("DomainPicker — disabled pill accessibility", () => {
  it("disabled pill has aria-disabled='true'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food");
    expect(foodPill!.getAttribute("aria-disabled")).toBe("true");
  });

  it("disabled pill remains in tab order (tabIndex is not -1)", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food");
    // tabIndex of 0 (or unset) means focusable; -1 means not focusable.
    expect(foodPill!.tabIndex).not.toBe(-1);
  });

  it("available pill has tabIndex of 0 (not removed from tab order)", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const familyPill = Array.from(pills).find((p) => p.textContent === "Family");
    expect(familyPill!.tabIndex).toBe(0);
  });
});

describe("DomainPicker — click interactions", () => {
  it("clicking an available pill calls onSelect with the pill's slug", () => {
    const onSelect = vi.fn();
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect });
    const pills = getPills();
    const holidaysPill = Array.from(pills).find((p) => p.textContent === "Holidays")!;

    act(() => {
      holidaysPill.click();
    });

    expect(onSelect).toHaveBeenCalledOnce();
    expect(onSelect).toHaveBeenCalledWith("holidays");
  });

  it("clicking a disabled pill does NOT call onSelect", () => {
    const onSelect = vi.fn();
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food")!;

    act(() => {
      foodPill.click();
    });

    expect(onSelect).not.toHaveBeenCalled();
  });
});

describe("DomainPicker — keyboard navigation", () => {
  it("ArrowRight moves focus to the next pill", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const firstPill = pills[0];
    const secondPill = pills[1];

    act(() => {
      firstPill.focus();
      firstPill.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(secondPill);
  });

  it("ArrowLeft moves focus to the previous pill", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const secondPill = pills[1];
    const firstPill = pills[0];

    act(() => {
      secondPill.focus();
      secondPill.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(firstPill);
  });

  it("ArrowRight from last pill wraps to first", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const lastPill = pills[pills.length - 1];
    const firstPill = pills[0];

    act(() => {
      lastPill.focus();
      lastPill.dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true })
      );
    });

    expect(document.activeElement).toBe(firstPill);
  });

  it("Enter key activates an available focused pill", () => {
    const onSelect = vi.fn();
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect });
    const pills = getPills();
    const holidaysPill = Array.from(pills).find((p) => p.textContent === "Holidays")!;

    act(() => {
      holidaysPill.focus();
      holidaysPill.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
    });

    expect(onSelect).toHaveBeenCalledWith("holidays");
  });

  it("Enter key on disabled pill does NOT call onSelect", () => {
    const onSelect = vi.fn();
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food")!;

    act(() => {
      foodPill.focus();
      foodPill.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
    });

    expect(onSelect).not.toHaveBeenCalled();
  });
});

describe("DomainPicker — tooltip text", () => {
  it("disabled pill has title attribute equal to 'Coming in a future update'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food")!;
    expect(foodPill.title).toBe("Coming in a future update");
  });

  it("available pill does NOT have a title tooltip", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const familyPill = Array.from(pills).find((p) => p.textContent === "Family")!;
    // Available pills have no tooltip
    expect(familyPill.title).toBeFalsy();
  });
});

describe("DomainPicker — aria-label content", () => {
  it("active pill aria-label contains 'currently displayed'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const familyPill = Array.from(pills).find((p) => p.textContent === "Family")!;
    expect(familyPill.getAttribute("aria-label")).toContain("currently displayed");
  });

  it("inactive available pill aria-label contains 'switch to view'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const holidaysPill = Array.from(pills).find((p) => p.textContent === "Holidays")!;
    expect(holidaysPill.getAttribute("aria-label")).toContain("switch to view");
  });

  it("disabled pill aria-label contains 'coming in a future update'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const pills = getPills();
    const foodPill = Array.from(pills).find((p) => p.textContent === "Food")!;
    expect(foodPill.getAttribute("aria-label")).toContain("coming in a future update");
  });
});

describe("DomainPicker — tablist role", () => {
  it("container has role='tablist'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const tablist = container.querySelector("[role='tablist']");
    expect(tablist).not.toBeNull();
  });

  it("tablist has aria-label='Domain selection'", () => {
    renderPicker({ domains: DOMAINS, activeSlug: "family", onSelect: vi.fn() });
    const tablist = container.querySelector("[role='tablist']");
    expect(tablist?.getAttribute("aria-label")).toBe("Domain selection");
  });
});
