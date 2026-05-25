/**
 * ClusterTree — left-to-right hierarchical clustering dendrogram.
 *
 * Renders a scipy linkage matrix as a left-to-right tree (root left, leaves
 * right). Each internal node's merge distance drives the horizontal position;
 * leaves are evenly spaced vertically.
 *
 * Branch coloring:
 *   - Single-cluster subtrees: colored with the cluster palette
 *   - Cross-cluster merges: gray (#999)
 *
 * Bootstrap support (bpValues):
 *   - Nodes with BP >= DENDROGRAM_SUPPORT_THRESHOLD: solid branches
 *   - Nodes with BP < DENDROGRAM_SUPPORT_THRESHOLD: dashed branches with
 *     a numeric % annotation left of the node
 *
 * Per DESIGN_SYSTEM.md §11 (v0.5.2) and the UI/UX verdict
 * docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md.
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks" applied to
 * models. This component renders categorical structure, not cognition.
 */

import { useRef, useEffect, useState, useCallback } from 'react';
import { DENDROGRAM_SUPPORT_THRESHOLD } from '../config/analysis';

// Cluster color palette matching tokens.css --color-cluster-1..8
// Used as SVG fill/stroke where CSS custom properties are not reliably resolved.
// See DESIGN_SYSTEM.md §1.2.
const CLUSTER_COLORS: string[] = [
  '#e05c2e', // --color-cluster-1: warm orange-red
  '#2e7d4f', // --color-cluster-2: forest green
  '#b5590a', // --color-cluster-3: dark amber
  '#5c3298', // --color-cluster-4: dark violet
  '#1d6b8f', // --color-cluster-5: steel blue
  '#8f1d55', // --color-cluster-6: dark rose
  '#4a6e1a', // --color-cluster-7: olive green
  '#6b3a1f', // --color-cluster-8: dark brown
];

const GRAY_BRANCH = '#999999';

/** Vertical pixels between adjacent leaf rows. UI/UX verdict: n_terms * 20 + margins. */
const LEAF_SPACING = 20;

function getClusterColor(clusterIdx: number): string {
  if (clusterIdx < 0) return GRAY_BRANCH;
  return CLUSTER_COLORS[clusterIdx % CLUSTER_COLORS.length];
}

/** Internal tree node built from the scipy linkage matrix. */
interface TreeNode {
  id: number;          // leaf: 0..n-1; internal: n..2n-2
  left: TreeNode | null;
  right: TreeNode | null;
  distance: number;    // merge distance (0 for leaves)
  count: number;       // number of leaves in this subtree
  // Computed during layout:
  y: number;           // vertical center as leaf-index units (0-based in-order)
  x: number;           // horizontal position in distance units
  // Derived from cluster assignments:
  dominantCluster: number; // -1 if cross-cluster merge, otherwise cluster index
}

/** Build tree nodes from linkage matrix. Returns the root node. */
function buildTree(
  linkage: number[][],
  n: number,
  items: string[],
  clusterAssignments: Record<string, number>,
): TreeNode {
  // Initialize leaf nodes
  const nodes: TreeNode[] = items.map((term, i) => ({
    id: i,
    left: null,
    right: null,
    distance: 0,
    count: 1,
    y: 0,
    x: 0,
    dominantCluster: clusterAssignments[term] ?? 0,
  }));

  // Build internal nodes from each linkage row
  for (let k = 0; k < linkage.length; k++) {
    const [rawI, rawJ, dist, count] = linkage[k];
    const nodeId = n + k;
    const left = nodes[Math.floor(rawI)];
    const right = nodes[Math.floor(rawJ)];

    // Dominant cluster: propagated only when both subtrees share one cluster
    let dominantCluster: number;
    if (left.dominantCluster === right.dominantCluster && left.dominantCluster >= 0) {
      dominantCluster = left.dominantCluster;
    } else {
      dominantCluster = -1;
    }

    nodes[nodeId] = {
      id: nodeId,
      left,
      right,
      distance: dist,
      count: Math.round(count),
      y: 0,
      x: 0,
      dominantCluster,
    };
  }

  // Root is the last node built
  return nodes[2 * n - 2];
}

/**
 * Assign y-positions by in-order traversal (left child first).
 * Leaves get consecutive integers 0, 1, 2, ... (multiplied by LEAF_SPACING
 * when converting to SVG coordinates).
 * Internal nodes get the midpoint of their children's y values.
 */
function assignYPositions(node: TreeNode, counter: { value: number }): void {
  if (node.left === null && node.right === null) {
    node.y = counter.value++;
    return;
  }
  if (node.left) assignYPositions(node.left, counter);
  if (node.right) assignYPositions(node.right, counter);
  node.y = ((node.left?.y ?? 0) + (node.right?.y ?? 0)) / 2;
}

/**
 * Assign x-positions in distance units.
 * Internal nodes: x = node.distance.
 * Leaves: x = maxDist (placed at the right edge, where all distances converge).
 */
function assignXPositions(node: TreeNode, maxDist: number): void {
  if (node.left === null && node.right === null) {
    node.x = maxDist;
    return;
  }
  node.x = node.distance;
  if (node.left) assignXPositions(node.left, maxDist);
  if (node.right) assignXPositions(node.right, maxDist);
}

interface Margin { top: number; right: number; bottom: number; left: number }

/** Map a distance value to an SVG x coordinate (root at left, leaves at right). */
function distToSvgX(dist: number, maxDist: number, margin: Margin, svgWidth: number): number {
  const plotWidth = svgWidth - margin.left - margin.right;
  return margin.left + (dist / maxDist) * plotWidth;
}

/** Map a leaf-index y value to an SVG y coordinate. */
function leafIdxToSvgY(leafIdx: number, margin: Margin): number {
  return margin.top + leafIdx * LEAF_SPACING + LEAF_SPACING / 2;
}

/** Collect leaf id → traversal y-index into a map. */
function collectLeafY(node: TreeNode, out: Record<number, number>): void {
  if (node.left === null && node.right === null) {
    out[node.id] = node.y;
    return;
  }
  if (node.left) collectLeafY(node.left, out);
  if (node.right) collectLeafY(node.right, out);
}

/** Escape HTML special characters for safe inclusion in SVG text nodes. */
function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export interface ClusterTreeProps {
  linkage: number[][];
  items: string[];
  clusterAssignments: Record<string, number>;
  bpValues?: number[];
}

export function ClusterTree({ linkage, items, clusterAssignments, bpValues }: ClusterTreeProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');

  const render = useCallback(() => {
    if (!wrapRef.current) return;
    const containerRect = wrapRef.current.getBoundingClientRect();
    const W = Math.max(containerRect.width || 800, 500);

    const n = items.length;
    if (n === 0 || linkage.length === 0) return;

    const margin: Margin = { top: 20, right: 185, bottom: 48, left: 60 };

    // Max merge distance (root distance)
    let maxDist = 0;
    for (const row of linkage) {
      if (row[2] > maxDist) maxDist = row[2];
    }
    if (maxDist === 0) maxDist = 1;

    // Build tree structure
    const root = buildTree(linkage, n, items, clusterAssignments);

    // Assign positions
    assignYPositions(root, { value: 0 });
    assignXPositions(root, maxDist);

    // BP lookup: internal node id → bootstrap proportion value
    const bpMap: Record<number, number> = {};
    if (bpValues) {
      for (let k = 0; k < bpValues.length && k < linkage.length; k++) {
        bpMap[n + k] = bpValues[k];
      }
    }

    // Leaf traversal-y map: leaf node id → y index from in-order traversal
    const leafYMap: Record<number, number> = {};
    collectLeafY(root, leafYMap);

    // Accumulate SVG elements
    const lines: string[] = [];
    const annotations: string[] = [];

    function traverseNode(node: TreeNode): void {
      if (node.left === null && node.right === null) return;

      const bp = bpMap[node.id];
      const isDashed = bp !== undefined && bp < DENDROGRAM_SUPPORT_THRESHOLD;
      const branchColor = node.dominantCluster >= 0
        ? getClusterColor(node.dominantCluster)
        : GRAY_BRANCH;
      const strokeWidth = 1.5;
      const dashAttr = isDashed ? ' stroke-dasharray="5 3"' : '';
      const opacAttr = isDashed ? ' opacity="0.7"' : '';
      const strokeAttrs = `stroke="${branchColor}" stroke-width="${strokeWidth}"${dashAttr}${opacAttr}`;

      const nx = distToSvgX(node.x, maxDist, margin, W);
      const ny = leafIdxToSvgY(node.y, margin);

      // Draw L-shaped connector to each child
      for (const child of [node.left, node.right] as (TreeNode | null)[]) {
        if (!child) continue;
        const cx = distToSvgX(child.x, maxDist, margin, W);
        const cy = leafIdxToSvgY(child.y, margin);

        // Horizontal segment: this node's x → child's x, at child's y
        lines.push(
          `<line x1="${nx.toFixed(1)}" y1="${cy.toFixed(1)}" x2="${cx.toFixed(1)}" y2="${cy.toFixed(1)}" ${strokeAttrs}/>`
        );

        // Vertical segment: this node's y ↔ child's y, at this node's x
        const yTop = Math.min(ny, cy);
        const yBot = Math.max(ny, cy);
        lines.push(
          `<line x1="${nx.toFixed(1)}" y1="${yTop.toFixed(1)}" x2="${nx.toFixed(1)}" y2="${yBot.toFixed(1)}" ${strokeAttrs}/>`
        );
      }

      // Numeric BP annotation for low-support nodes
      if (isDashed && bp !== undefined) {
        const pct = Math.round(bp * 100);
        const annotX = (nx - 4).toFixed(1);
        const annotY = (ny - 4).toFixed(1);
        annotations.push(
          `<text x="${annotX}" y="${annotY}" font-size="9" fill="${GRAY_BRANCH}" ` +
          `text-anchor="end" font-family="var(--font-body)">${pct}%</text>`
        );
      }

      if (node.left) traverseNode(node.left);
      if (node.right) traverseNode(node.right);
    }

    traverseNode(root);

    // Leaf labels and cluster dots
    const leafX = distToSvgX(maxDist, maxDist, margin, W);
    const leafElems: string[] = [];
    for (let i = 0; i < n; i++) {
      const term = items[i];
      const traversalY = leafYMap[i] ?? i;
      const sy = leafIdxToSvgY(traversalY, margin);
      const cluster = clusterAssignments[term] ?? 0;
      const dotColor = getClusterColor(cluster);

      // Colored dot
      leafElems.push(
        `<circle cx="${(leafX + 7).toFixed(1)}" cy="${sy.toFixed(1)}" r="3" fill="${dotColor}"/>`
      );

      // Term label
      leafElems.push(
        `<text x="${(leafX + 15).toFixed(1)}" y="${(sy + 3.5).toFixed(1)}" ` +
        `font-size="10" fill="var(--color-text-primary)" font-family="var(--font-body)">${escapeHtml(term)}</text>`
      );
    }

    // Distance axis (bottom)
    const axisTop = margin.top;
    const axisBottom = margin.top + n * LEAF_SPACING;
    const rootX = distToSvgX(0, maxDist, margin, W);
    const rightX = distToSvgX(maxDist, maxDist, margin, W);
    const axisElems: string[] = [];

    // Baseline
    axisElems.push(
      `<line x1="${rootX.toFixed(1)}" y1="${axisBottom}" x2="${rootX.toFixed(1)}" y2="${axisTop}" ` +
      `stroke="var(--color-border)" stroke-width="1" opacity="0.5"/>`
    );

    // Ticks
    const tickCount = 4;
    for (let t = 0; t <= tickCount; t++) {
      const tickDist = (t / tickCount) * maxDist;
      const tx = distToSvgX(tickDist, maxDist, margin, W);
      const tickY = axisBottom + 4;
      axisElems.push(
        `<line x1="${tx.toFixed(1)}" y1="${axisBottom}" x2="${tx.toFixed(1)}" y2="${tickY.toFixed(1)}" ` +
        `stroke="var(--color-border)" stroke-width="1"/>`
      );
      axisElems.push(
        `<text x="${tx.toFixed(1)}" y="${(tickY + 10).toFixed(1)}" font-size="9" ` +
        `fill="var(--color-text-secondary)" text-anchor="middle" font-family="var(--font-body)">${tickDist.toFixed(2)}</text>`
      );
    }

    // Axis label
    const axisLabelX = ((rootX + rightX) / 2).toFixed(1);
    const axisLabelY = (axisBottom + 28).toFixed(1);
    axisElems.push(
      `<text x="${axisLabelX}" y="${axisLabelY}" font-size="9" ` +
      `fill="var(--color-text-secondary)" text-anchor="middle" font-family="var(--font-body)">Merge distance</text>`
    );

    // Legend (bottom-left area)
    const legendX = margin.left;
    const legendY = axisBottom + 38;
    const legendElems: string[] = [
      `<line x1="${legendX}" y1="${legendY}" x2="${(legendX + 20).toFixed(1)}" y2="${legendY}" ` +
      `stroke="${GRAY_BRANCH}" stroke-width="1.5"/>`,
      `<text x="${(legendX + 25).toFixed(1)}" y="${(legendY + 4).toFixed(1)}" font-size="9" ` +
      `fill="var(--color-text-secondary)" font-family="var(--font-body)">Solid: bootstrap support ≥ 70%</text>`,
      `<line x1="${legendX}" y1="${(legendY + 14).toFixed(1)}" x2="${(legendX + 20).toFixed(1)}" y2="${(legendY + 14).toFixed(1)}" ` +
      `stroke="${GRAY_BRANCH}" stroke-width="1.5" stroke-dasharray="5 3" opacity="0.7"/>`,
      `<text x="${(legendX + 25).toFixed(1)}" y="${(legendY + 18).toFixed(1)}" font-size="9" ` +
      `fill="var(--color-text-secondary)" font-family="var(--font-body)">Dashed: bootstrap support &lt; 70%</text>`,
    ];

    const totalH = legendY + 26;

    const svgBody = [
      `<svg width="${W}" height="${totalH}" viewBox="0 0 ${W} ${totalH}"`,
      `  role="img" aria-label="Hierarchical clustering tree showing how ${n} domain terms group by co-occurrence patterns"`,
      `  id="cluster-tree-svg">`,
      `<rect width="${W}" height="${totalH}" fill="var(--color-background)"/>`,
      ...lines,
      ...annotations,
      ...axisElems,
      ...legendElems,
      ...leafElems,
      `</svg>`,
    ].join('\n');

    setSvgContent(svgBody);
  }, [linkage, items, clusterAssignments, bpValues]);

  // Initial render and respond to container width changes
  useEffect(() => {
    render();
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => { render(); });
    ro.observe(el);
    return () => { ro.disconnect(); };
  }, [render]);

  if (items.length === 0 || linkage.length === 0) {
    return (
      <div className="cluster-tree cluster-tree--empty">
        <p className="cluster-tree__empty-msg">
          No clustering data available for this domain.
        </p>
      </div>
    );
  }

  return (
    <div className="cluster-tree" ref={wrapRef}>
      <p className="cluster-tree__desc">
        How domain terms cluster hierarchically based on co-occurrence patterns across model
        outputs. Merge distance reflects how dissimilar two groups are; branch annotations
        show bootstrap support (% of resamples producing this grouping).
      </p>
      {/* dangerouslySetInnerHTML used for SVG string — same rendering pattern as TermMap */}
      <div
        className="cluster-tree__svg-wrap"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
}
