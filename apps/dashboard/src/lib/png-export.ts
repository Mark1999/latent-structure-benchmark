/**
 * PNG export — SVG → canvas rasterization.
 *
 * Two export sizes per DESIGN_SYSTEM.md §5 and UI/UX F5 binding:
 *   social:  1600 × 900 px  (16:9, suitable for Twitter/X / Facebook share cards)
 *   highres: 2000 × 2000 px (square, suitable for academic slides + papers)
 *
 * F5 binding (explicit canvas dimensions):
 *   canvas.width = 1600; canvas.height = 900;   (social)
 *   canvas.width = 2000; canvas.height = 2000;  (highres)
 *
 * Watermark per F5:
 *   Text: "cogstructurelab.com"
 *   Opacity: 0.03
 *   Position: bottom-right at canvasWidth × 0.02 and canvasHeight × 0.02 margins
 *   Font size: canvasWidth × 0.012 (19px social, 24px highres — identical visual weight)
 *   Font family: monospace (--font-mono editorial restraint)
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T11
 *         DESIGN_SYSTEM.md §5
 *         docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md F5
 */

export type PngSize = "social" | "highres";

export interface RenderToPngOptions {
  size: PngSize;
}

/** Canvas dimensions per F5 binding. */
const CANVAS_DIMS: Record<PngSize, { width: number; height: number }> = {
  social: { width: 1600, height: 900 },
  highres: { width: 2000, height: 2000 },
};

/**
 * Rasterize an SVG element to a PNG Blob.
 *
 * Steps:
 * 1. XMLSerializer → SVG string → data: URL.
 * 2. Load into an Image element (crossOrigin = "anonymous").
 * 3. Draw to a canvas sized per the size param (explicit width/height per F5).
 *    Scale SVG to fit canvas while preserving aspect ratio (letterbox/pillarbox
 *    for the square hi-res size).
 * 4. Overlay watermark "cogstructurelab.com" at 3% opacity, bottom-right,
 *    position as percentage of canvas dimensions (not fixed pixels, per F5).
 * 5. canvas.toBlob() → PNG Blob.
 *
 * @param svg     The SVGSVGElement to rasterize.
 * @param options Size selection: "social" (1600×900) or "highres" (2000×2000).
 * @returns       Promise resolving to a PNG Blob.
 */
export async function renderToPng(
  svg: SVGSVGElement,
  options: RenderToPngOptions
): Promise<Blob> {
  // Guard: canvas must be available (not SSR/node env).
  if (
    typeof document === "undefined" ||
    typeof HTMLCanvasElement === "undefined"
  ) {
    throw new Error(
      "renderToPng: canvas API is not available in this environment. " +
        "Call this function only in a browser context."
    );
  }

  const { width: canvasWidth, height: canvasHeight } = CANVAS_DIMS[options.size];

  // ── Step 1: Serialize SVG to a data: URL ──────────────────────────────────

  // Read viewBox to get the SVG's intrinsic coordinate space.
  const viewBox = svg.viewBox?.baseVal;
  let svgNatW: number;
  let svgNatH: number;

  if (viewBox && viewBox.width > 0 && viewBox.height > 0) {
    svgNatW = viewBox.width;
    svgNatH = viewBox.height;
  } else {
    // Fall back to rendered width/height if viewBox is absent.
    svgNatW = svg.clientWidth || 600;
    svgNatH = svg.clientHeight || 480;
  }

  // Clone the SVG so we can set explicit dimensions without touching the live DOM.
  const svgClone = svg.cloneNode(true) as SVGSVGElement;

  // Compute the draw rectangle: scale-to-fit inside canvas, preserving aspect ratio.
  const scaleX = canvasWidth / svgNatW;
  const scaleY = canvasHeight / svgNatH;
  const scale = Math.min(scaleX, scaleY);

  const drawW = svgNatW * scale;
  const drawH = svgNatH * scale;
  const drawX = (canvasWidth - drawW) / 2;   // horizontal centering (letterbox)
  const drawY = (canvasHeight - drawH) / 2;  // vertical centering (pillarbox)

  // Set explicit width/height attributes on the clone so the Image element
  // knows the intrinsic size when the SVG is loaded via data: URL.
  svgClone.setAttribute("width", String(Math.round(drawW)));
  svgClone.setAttribute("height", String(Math.round(drawH)));

  const serializer = new XMLSerializer();
  const svgString = serializer.serializeToString(svgClone);

  // Wrap in a data: URL (UTF-8 → percent-encode).
  const svgDataUrl =
    "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgString);

  // ── Step 2: Load into Image ───────────────────────────────────────────────

  const img = new Image();
  img.crossOrigin = "anonymous";

  await new Promise<void>((resolve, reject) => {
    img.onload = () => resolve();
    img.onerror = (_e, _src, _lineno, _colno, err) =>
      reject(
        err ?? new Error("renderToPng: failed to load serialized SVG as Image")
      );
    img.src = svgDataUrl;
  });

  // ── Step 3: Draw to canvas ────────────────────────────────────────────────

  const canvas = document.createElement("canvas");
  // F5 binding: explicit canvas dimensions for both size variants.
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("renderToPng: canvas 2D context not available.");
  }

  // White background.
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  // Draw the SVG centered within the canvas.
  ctx.drawImage(img, drawX, drawY, drawW, drawH);

  // ── Step 4: Watermark ─────────────────────────────────────────────────────

  // F5 binding: position as percentage of canvas dimensions (NOT fixed pixels).
  const marginRight = canvasWidth * 0.02;
  const marginBottom = canvasHeight * 0.02;

  // Font size scales with canvas width → identical visual weight across sizes.
  // 1600 × 0.012 = 19.2px (social); 2000 × 0.012 = 24px (highres).
  const fontSize = canvasWidth * 0.012;

  const watermarkText = "cogstructurelab.com";

  ctx.save();
  ctx.globalAlpha = 0.03;  // 3% opacity per DESIGN_SYSTEM.md §5
  ctx.font = `${fontSize}px monospace`;
  ctx.fillStyle = "#000000";
  ctx.textBaseline = "bottom";
  ctx.textAlign = "right";
  ctx.fillText(watermarkText, canvasWidth - marginRight, canvasHeight - marginBottom);
  ctx.restore();

  // ── Step 5: canvas.toBlob() → PNG ─────────────────────────────────────────

  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error("renderToPng: canvas.toBlob() returned null."));
        }
      },
      "image/png"
    );
  });
}
