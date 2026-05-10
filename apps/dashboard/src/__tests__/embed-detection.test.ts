/**
 * Tests for embed mode detection logic.
 *
 * DESIGN_SYSTEM.md §12.5: ?embed=true URL parameter suppresses chrome.
 * AC3, AC8: No real fetch, no real browser.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

/**
 * Import the embed detection function.
 * Since it's defined inside App.tsx as an unexported function, we test
 * the identical logic directly here to keep tests isolated from React.
 *
 * The implementation in App.tsx is:
 *   new URLSearchParams(window.location.search).get("embed") === "true"
 */
function isEmbedMode(search: string): boolean {
  try {
    return new URLSearchParams(search).get("embed") === "true";
  } catch {
    return false;
  }
}

describe("isEmbedMode (embed detection logic from App.tsx §12.5)", () => {
  it("returns false when query string is empty", () => {
    expect(isEmbedMode("")).toBe(false);
  });

  it("returns true when ?embed=true is present", () => {
    expect(isEmbedMode("?embed=true")).toBe(true);
  });

  it("returns false when ?embed=false", () => {
    expect(isEmbedMode("?embed=false")).toBe(false);
  });

  it("returns false when embed param is absent but other params present", () => {
    expect(isEmbedMode("?domain=family&viz=mds")).toBe(false);
  });

  it("returns true when embed=true is among other params", () => {
    expect(isEmbedMode("?domain=family&embed=true&viz=mds")).toBe(true);
  });

  it("returns false when embed param value is 'TRUE' (case sensitive)", () => {
    // The spec says: get('embed') === 'true' — exact match
    expect(isEmbedMode("?embed=TRUE")).toBe(false);
  });

  it("returns false when embed param value is '1'", () => {
    expect(isEmbedMode("?embed=1")).toBe(false);
  });

  it("handles malformed query gracefully (no throw)", () => {
    // URLSearchParams handles most strings without throwing; the try-catch
    // in the implementation guards edge cases
    expect(() => isEmbedMode("???")).not.toThrow();
  });
});

describe("embed mode — integration with window.location.search mock", () => {
  const originalLocation = globalThis.location;

  afterEach(() => {
    // Restore original location
    try {
      vi.unstubAllGlobals();
    } catch {
      // Ignore if no stubs
    }
  });

  it("detects embed=true from window.location.search when stubbed", () => {
    // Stub window.location.search to simulate ?embed=true URL
    vi.stubGlobal("location", {
      ...originalLocation,
      search: "?embed=true",
      href: "https://cogstructurelab.com/?embed=true",
    });

    const search = globalThis.location?.search ?? "";
    expect(isEmbedMode(search)).toBe(true);
  });

  it("detects no embed from window.location.search when stubbed without param", () => {
    vi.stubGlobal("location", {
      ...originalLocation,
      search: "?domain=family",
      href: "https://cogstructurelab.com/?domain=family",
    });

    const search = globalThis.location?.search ?? "";
    expect(isEmbedMode(search)).toBe(false);
  });

  beforeEach(() => {
    // Ensure clean state
    try {
      vi.unstubAllGlobals();
    } catch {
      // ignore
    }
  });
});
