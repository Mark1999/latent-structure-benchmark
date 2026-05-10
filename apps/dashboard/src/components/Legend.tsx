/**
 * Legend — standalone marker-sample legend for the MDS plot.
 *
 * Extracted from MDSPlot.tsx at T7 so the legend can be reused by
 * other vizzes without importing the full MDSPlot module.
 *
 * Renders actual 14px marker samples per §3.3.5 implementation requirement 4
 * (binding — text tags alone do not satisfy WCAG non-text contrast).
 *
 * Sample color: --color-model-1 (#3360a9) — passes 3:1 contrast on white.
 *
 * Props:
 *   showDescriptions — if false, renders a more compact horizontal layout
 *   without the secondary italic description line. Defaults to true.
 */

// ── Helper: hex color → rgba ─────────────────────────────────────────────────

function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  if (isNaN(r) || isNaN(g) || isNaN(b)) return hex;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// ── Helper: triangle path for R1-c sample ───────────────────────────────────

function trianglePathD(cx: number, cy: number, r: number): string {
  const top: [number, number] = [cx, cy - r];
  const bl: [number, number] = [cx - r * Math.sin(Math.PI * 2 / 3), cy + r * Math.cos(Math.PI * 2 / 3)];
  const br: [number, number] = [cx + r * Math.sin(Math.PI * 2 / 3), cy + r * Math.cos(Math.PI * 2 / 3)];
  const fmt = (n: number) => n.toFixed(2);
  return `M ${fmt(top[0])} ${fmt(top[1])} L ${fmt(br[0])} ${fmt(br[1])} L ${fmt(bl[0])} ${fmt(bl[1])} Z`;
}

// ── Props ────────────────────────────────────────────────────────────────────

export interface LegendProps {
  /**
   * If false, renders a more compact horizontal layout without the secondary
   * italic description line. Defaults to true (vertical, with descriptions).
   */
  showDescriptions?: boolean;
}

// ── Component ────────────────────────────────────────────────────────────────

/**
 * Legend renders the three R1-state marker samples with labels.
 * Each sample is a 14px SVG matching the actual marker style on the plot.
 * §3.3.5 imp. req. 4 binding: rendered marker samples (not text tags).
 */
export function Legend({ showDescriptions = true }: LegendProps) {
  // Sample color: --color-model-1 = #3360a9 (~7.2:1 contrast on white — well above 3:1)
  const sampleColor = "#3360a9";
  const sampleColorFill60 = hexToRgba(sampleColor, 0.6);

  // R1-a: solid filled circle
  const r1aSvg = (
    <svg width="14" height="14" aria-hidden="true" focusable="false">
      <circle
        cx="7"
        cy="7"
        r="5"
        fill={sampleColor}
        stroke="white"
        strokeWidth="2"
      />
    </svg>
  );

  // R1-b: dashed-stroke circle with lighter fill (60% opacity fill, 100% stroke)
  const r1bSvg = (
    <svg width="14" height="14" aria-hidden="true" focusable="false">
      <circle
        cx="7"
        cy="7"
        r="5"
        fill={sampleColorFill60}
        stroke={sampleColor}
        strokeWidth="2"
        strokeDasharray="3 2"
      />
    </svg>
  );

  // R1-c: hollow triangle, 3px stroke, no fill
  const r1cTriPath = trianglePathD(7, 7, 5.5);
  const r1cSvg = (
    <svg width="14" height="14" aria-hidden="true" focusable="false">
      <path
        d={r1cTriPath}
        fill="none"
        stroke={sampleColor}
        strokeWidth="3"
        strokeLinejoin="round"
      />
    </svg>
  );

  return (
    <div className="mds-plot__legend" role="list" aria-label="Map marker legend">
      <div className="mds-plot__legend-item" role="listitem">
        {r1aSvg}
        <div className="mds-plot__legend-label">
          <span className="mds-plot__legend-primary">Typical concentration</span>
          {showDescriptions && (
            <span className="mds-plot__legend-secondary">confidence ellipse shown</span>
          )}
        </div>
      </div>
      <div className="mds-plot__legend-item" role="listitem">
        {r1bSvg}
        <div className="mds-plot__legend-label">
          <span className="mds-plot__legend-primary">Low output concentration</span>
          {showDescriptions && (
            <span className="mds-plot__legend-secondary">position uncertain</span>
          )}
        </div>
      </div>
      <div className="mds-plot__legend-item" role="listitem">
        {r1cSvg}
        <div className="mds-plot__legend-label">
          <span className="mds-plot__legend-primary">Deterministic output</span>
          {showDescriptions && (
            <span className="mds-plot__legend-secondary">
              zero variance — the mismatch is the finding
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
