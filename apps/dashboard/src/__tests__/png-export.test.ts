// @vitest-environment jsdom
/**
 * Tests for png-export.ts — renderToPng().
 *
 * jsdom does not implement a full canvas rasterizer (no GPU), so the
 * integration tests are smoke tests that verify the public API contract,
 * the F5 binding canvas dimensions, and the error-rejection behaviour.
 *
 * Tests that require real canvas rendering (visual quality, watermark
 * placement accuracy) are verified via manual visual inspection.
 *
 * F5 binding (UI/UX plan-level verdict):
 *   - canvas.width = 1600; canvas.height = 900  for social
 *   - canvas.width = 2000; canvas.height = 2000 for highres
 *   Both are set EXPLICITLY (not inferred from SVG intrinsic size).
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T11
 *         docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md F5
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import type { PngSize } from "../lib/png-export";

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Build a minimal SVGSVGElement for testing. */
function makeSvg(viewBoxW = 600, viewBoxH = 480): SVGSVGElement {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg") as SVGSVGElement;
  svg.setAttribute("viewBox", `0 0 ${viewBoxW} ${viewBoxH}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Test MDS plot");
  return svg;
}

/**
 * Canvas mock state — shared across tests in this file.
 * We install mocks on document.createElement and HTMLCanvasElement to:
 *   (a) record explicit width/height assignments (F5 binding check)
 *   (b) fire toBlob synchronously with a dummy PNG blob
 *   (c) record ctx method calls (drawImage, fillText, etc.)
 */
interface MockCtxState {
  fillStyle: string;
  globalAlpha: number;
  font: string;
  textBaseline: string;
  textAlign: string;
  fillRect: ReturnType<typeof vi.fn>;
  drawImage: ReturnType<typeof vi.fn>;
  fillText: ReturnType<typeof vi.fn>;
  save: ReturnType<typeof vi.fn>;
  restore: ReturnType<typeof vi.fn>;
}

// Per-test capture for canvas dimensions set during renderToPng.
let widthLog: number[] = [];
let heightLog: number[] = [];
let ctxState: MockCtxState;

// Global Image override — must be a class/function for vitest constructor mocking.
class MockImage {
  crossOrigin = "anonymous";
  onload: (() => void) | null = null;
  onerror: ((...args: unknown[]) => void) | null = null;
  private _src = "";

  get src() {
    return this._src;
  }

  set src(v: string) {
    this._src = v;
    // Fire onload asynchronously so the Promise chain can await it.
    Promise.resolve().then(() => {
      if (this.onload) this.onload();
    });
  }
}

// Minimal dummy PNG blob for toBlob callbacks.
const DUMMY_PNG = new Blob(
  [new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10])],
  { type: "image/png" }
);

beforeEach(() => {
  widthLog = [];
  heightLog = [];

  ctxState = {
    fillStyle: "",
    globalAlpha: 1,
    font: "",
    textBaseline: "",
    textAlign: "",
    fillRect: vi.fn(),
    drawImage: vi.fn(),
    fillText: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
  };

  // Install the Image mock on the global scope.
  (globalThis as unknown as Record<string, unknown>).Image = MockImage;

  // Stub document.createElement to intercept canvas creation.
  const originalCreateElement = document.createElement.bind(document);
  vi.spyOn(document, "createElement").mockImplementation((tag: string, ...rest) => {
    if (tag === "canvas") {
      const el = originalCreateElement("canvas") as HTMLCanvasElement;

      // Track explicit w/h assignments.
      let _w = 300;
      let _h = 150;
      Object.defineProperty(el, "width", {
        get: () => _w,
        set: (v: number) => {
          _w = v;
          widthLog.push(v);
        },
        configurable: true,
      });
      Object.defineProperty(el, "height", {
        get: () => _h,
        set: (v: number) => {
          _h = v;
          heightLog.push(v);
        },
        configurable: true,
      });

      // Mock getContext to return our spy ctx.
      vi.spyOn(el, "getContext").mockReturnValue(
        ctxState as unknown as CanvasRenderingContext2D
      );

      // Mock toBlob to fire immediately with DUMMY_PNG.
      vi.spyOn(el, "toBlob").mockImplementation((cb: BlobCallback) => {
        cb(DUMMY_PNG);
      });

      return el;
    }
    return originalCreateElement(tag, ...rest);
  });
});

afterEach(() => {
  vi.restoreAllMocks();
  // Restore native Image if it was replaced.
  // (jsdom supplies its own Image; restoreAllMocks won't touch our assignment.)
});

// ── Import after mocks are wired ──────────────────────────────────────────────

async function getRenderToPng() {
  // Dynamic import so the module sees our mocks on each test.
  const mod = await import("../lib/png-export?t=" + Date.now());
  return mod.renderToPng;
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("renderToPng — public API contract", () => {
  it("is callable and returns a Promise", async () => {
    const renderToPng = await getRenderToPng();
    expect(typeof renderToPng).toBe("function");
    const svg = makeSvg();
    const result = renderToPng(svg, { size: "social" });
    expect(result).toBeInstanceOf(Promise);
    await result; // should not throw
  });

  it("resolves to a Blob for social size", async () => {
    const renderToPng = await getRenderToPng();
    const blob = await renderToPng(makeSvg(), { size: "social" });
    expect(blob).toBeInstanceOf(Blob);
  });

  it("resolves to a Blob for highres size", async () => {
    const renderToPng = await getRenderToPng();
    const blob = await renderToPng(makeSvg(), { size: "highres" });
    expect(blob).toBeInstanceOf(Blob);
  });
});

describe("renderToPng — F5 canvas dimensions (social: 1600×900)", () => {
  it("sets canvas.width = 1600 for social", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(widthLog).toContain(1600);
  });

  it("sets canvas.height = 900 for social", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(heightLog).toContain(900);
  });

  it("does NOT set canvas.width = 2000 for social", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(widthLog).not.toContain(2000);
  });
});

describe("renderToPng — F5 canvas dimensions (highres: 2000×2000)", () => {
  it("sets canvas.width = 2000 for highres", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    expect(widthLog).toContain(2000);
  });

  it("sets canvas.height = 2000 for highres", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    expect(heightLog).toContain(2000);
  });

  it("does NOT set canvas.height = 900 for highres", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    expect(heightLog).not.toContain(900);
  });
});

describe("renderToPng — SVG serialization", () => {
  it("calls XMLSerializer.serializeToString", async () => {
    const serializeSpy = vi.spyOn(XMLSerializer.prototype, "serializeToString");
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(serializeSpy).toHaveBeenCalled();
  });

  it("serializes an SVG element (nodeName svg)", async () => {
    const serializeSpy = vi.spyOn(XMLSerializer.prototype, "serializeToString");
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    const arg = serializeSpy.mock.calls[0][0] as Element;
    expect(arg.nodeName.toLowerCase()).toBe("svg");
  });
});

describe("renderToPng — canvas context calls", () => {
  it("calls ctx.fillRect at least once (white background)", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(ctxState.fillRect).toHaveBeenCalled();
  });

  it("calls ctx.drawImage at least once (SVG image draw)", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(ctxState.drawImage).toHaveBeenCalled();
  });

  it("calls ctx.fillText with watermark text 'cogstructurelab.com'", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(ctxState.fillText).toHaveBeenCalledWith(
      "cogstructurelab.com",
      expect.any(Number),
      expect.any(Number)
    );
  });
});

describe("renderToPng — watermark visual weight (F5 binding: % of canvas)", () => {
  /**
   * F5: font size = canvasWidth × 0.012.
   * 1600 × 0.012 = 19.2px (social), 2000 × 0.012 = 24px (highres).
   * The font string on ctx should contain the expected pixel size.
   */
  it("social: font size contains 19.2px (1600 * 0.012)", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(ctxState.font).toContain("19.2px");
  });

  it("highres: font size contains 24px (2000 * 0.012)", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    expect(ctxState.font).toContain("24px");
  });

  it("save() and restore() are called (opacity isolation)", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(ctxState.save).toHaveBeenCalled();
    expect(ctxState.restore).toHaveBeenCalled();
  });
});

describe("renderToPng — error conditions", () => {
  it("rejects with descriptive error when HTMLCanvasElement is undefined (simulated SSR)", async () => {
    // Temporarily remove HTMLCanvasElement to simulate an SSR/node-like env.
    const orig = globalThis.HTMLCanvasElement;
    // @ts-expect-error — deliberate deletion to simulate missing canvas API
    delete globalThis.HTMLCanvasElement;

    const renderToPng = await getRenderToPng();
    try {
      await expect(renderToPng(makeSvg(), { size: "social" })).rejects.toThrow(
        /canvas API is not available/
      );
    } finally {
      globalThis.HTMLCanvasElement = orig;
    }
  });
});

describe("renderToPng — size param type contract", () => {
  it("accepts 'social' as a PngSize literal", () => {
    const size: PngSize = "social";
    expect(size).toBe("social");
  });

  it("accepts 'highres' as a PngSize literal", () => {
    const size: PngSize = "highres";
    expect(size).toBe("highres");
  });
});
