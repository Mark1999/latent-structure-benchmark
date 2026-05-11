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

/**
 * When true, the canvas mock fires toBlob with null instead of DUMMY_PNG.
 * Set to true inside a test and reset in the test's finally block.
 */
let forceToBlobNull = false;

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

      // Mock toBlob to fire immediately with DUMMY_PNG (or null when forceToBlobNull).
      vi.spyOn(el, "toBlob").mockImplementation((cb: BlobCallback) => {
        cb(forceToBlobNull ? null : DUMMY_PNG);
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

// ── Gap-fill tests (T11 tester audit) ─────────────────────────────────────────

describe("renderToPng — watermark opacity (F5 binding: 3%)", () => {
  it("social: ctx.globalAlpha is set to 0.03 before drawing watermark", async () => {
    // The mock ctx records the last value assigned to globalAlpha.
    // png-export.ts sets it inside ctx.save()...ctx.restore(), so we check
    // the value captured at the time fillText is called.
    // We instrument fillText to snapshot globalAlpha at call time.
    let alphaAtFillText: number | undefined;
    const renderToPng = await getRenderToPng();

    // Wrap fillText to capture globalAlpha at invocation time.
    const origFillText = ctxState.fillText;
    ctxState.fillText = vi.fn().mockImplementation((...args: unknown[]) => {
      alphaAtFillText = ctxState.globalAlpha;
      return origFillText(...args);
    });

    await renderToPng(makeSvg(), { size: "social" });
    expect(alphaAtFillText).toBe(0.03);
  });

  it("highres: ctx.globalAlpha is set to 0.03 before drawing watermark", async () => {
    let alphaAtFillText: number | undefined;
    const renderToPng = await getRenderToPng();

    const origFillText = ctxState.fillText;
    ctxState.fillText = vi.fn().mockImplementation((...args: unknown[]) => {
      alphaAtFillText = ctxState.globalAlpha;
      return origFillText(...args);
    });

    await renderToPng(makeSvg(), { size: "highres" });
    expect(alphaAtFillText).toBe(0.03);
  });
});

describe("renderToPng — watermark margin as 2% of canvas dimensions (F5 binding)", () => {
  /**
   * F5: position = canvasWidth * 0.02 (right margin) and canvasHeight * 0.02
   * (bottom margin).  renderToPng calls:
   *   ctx.fillText(text, canvasWidth - marginRight, canvasHeight - marginBottom)
   * which for social is fillText("cogstructurelab.com", 1600-32, 900-18).
   * i.e., fillText(text, 1568, 882).
   */
  it("social: fillText X coordinate equals canvasWidth - canvasWidth*0.02 = 1568", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    const [, xArg] = ctxState.fillText.mock.calls[0] as [string, number, number];
    expect(xArg).toBeCloseTo(1600 - 1600 * 0.02, 5);
  });

  it("social: fillText Y coordinate equals canvasHeight - canvasHeight*0.02 = 882", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    const [, , yArg] = ctxState.fillText.mock.calls[0] as [string, number, number];
    expect(yArg).toBeCloseTo(900 - 900 * 0.02, 5);
  });

  it("highres: fillText X coordinate equals canvasWidth - canvasWidth*0.02 = 1960", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    const [, xArg] = ctxState.fillText.mock.calls[0] as [string, number, number];
    expect(xArg).toBeCloseTo(2000 - 2000 * 0.02, 5);
  });

  it("highres: fillText Y coordinate equals canvasHeight - canvasHeight*0.02 = 1960", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    const [, , yArg] = ctxState.fillText.mock.calls[0] as [string, number, number];
    expect(yArg).toBeCloseTo(2000 - 2000 * 0.02, 5);
  });
});

describe("renderToPng — watermark font family monospace (F5 binding)", () => {
  it("social: ctx.font string contains 'monospace'", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "social" });
    expect(ctxState.font).toContain("monospace");
  });

  it("highres: ctx.font string contains 'monospace'", async () => {
    const renderToPng = await getRenderToPng();
    await renderToPng(makeSvg(), { size: "highres" });
    expect(ctxState.font).toContain("monospace");
  });
});

describe("renderToPng — SVG aspect ratio letterboxing", () => {
  /**
   * A 900×600 SVG (3:2 ratio) rendered onto a 2000×2000 (1:1) canvas should
   * be letter-boxed: the image fills width-first (scale = 2000/900 ≈ 2.22),
   * and drawImage is called with height = 600 * 2.22 ≈ 1333, which is < 2000.
   * The drawX offset should be 0 (width fills the canvas), and drawY should
   * be (2000 - 1333) / 2 ≈ 333 (vertical centering).
   *
   * We verify that drawImage is called with correct positioning rather than
   * clipping the image to the canvas.
   */
  it("square canvas: drawImage called with height < canvasHeight for wide SVG", async () => {
    const renderToPng = await getRenderToPng();
    // 900×600 SVG (wider than square), rendered on 2000×2000 canvas.
    await renderToPng(makeSvg(900, 600), { size: "highres" });

    expect(ctxState.drawImage).toHaveBeenCalled();
    const drawArgs = ctxState.drawImage.mock.calls[0] as [unknown, number, number, number, number];
    const [, , , drawW, drawH] = drawArgs;

    // The draw should scale to fill 2000px wide.
    // scaleX = 2000/900 ≈ 2.222, scaleY = 2000/600 ≈ 3.333 → scale = min = 2.222
    // drawW ≈ 2000, drawH ≈ 1333 (< 2000 confirms letterboxing, not clipping)
    expect(drawW).toBeCloseTo(2000, 0);
    expect(drawH).toBeLessThan(2000);
  });

  it("square canvas: drawImage called with width < canvasWidth for tall SVG", async () => {
    const renderToPng = await getRenderToPng();
    // 600×900 SVG (taller than square), rendered on 2000×2000 canvas.
    await renderToPng(makeSvg(600, 900), { size: "highres" });

    expect(ctxState.drawImage).toHaveBeenCalled();
    const drawArgs = ctxState.drawImage.mock.calls[0] as [unknown, number, number, number, number];
    const [, , , drawW, drawH] = drawArgs;

    // scaleX = 2000/600 ≈ 3.333, scaleY = 2000/900 ≈ 2.222 → scale = min = 2.222
    // drawW ≈ 1333 (< 2000 confirms pillarboxing), drawH ≈ 2000
    expect(drawW).toBeLessThan(2000);
    expect(drawH).toBeCloseTo(2000, 0);
  });
});

describe("renderToPng — toBlob returns null → rejects", () => {
  it("rejects with descriptive error when canvas.toBlob returns null", async () => {
    // The beforeEach createElement spy reads forceToBlobNull to decide what
    // the toBlob mock returns. Set it to true for this test so the canvas
    // calls cb(null), which should cause renderToPng to reject.
    forceToBlobNull = true;
    try {
      const renderToPng = await getRenderToPng();
      await expect(renderToPng(makeSvg(), { size: "social" })).rejects.toThrow(
        /toBlob\(\) returned null/
      );
    } finally {
      forceToBlobNull = false;
    }
  });
});

describe("renderToPng — Image onerror rejects promise", () => {
  it("rejects with an error when the Image fires onerror", async () => {
    // Install a MockImage class that fires onerror instead of onload.
    class ErrorImage {
      crossOrigin = "anonymous";
      onload: (() => void) | null = null;
      onerror: ((...args: unknown[]) => void) | null = null;
      private _src = "";

      get src() { return this._src; }
      set src(v: string) {
        this._src = v;
        Promise.resolve().then(() => {
          if (this.onerror) this.onerror(null, null, null, null, new Error("SVG load failed"));
        });
      }
    }

    (globalThis as unknown as Record<string, unknown>).Image = ErrorImage;

    const renderToPng = await getRenderToPng();
    await expect(renderToPng(makeSvg(), { size: "social" })).rejects.toThrow();
  });
});
