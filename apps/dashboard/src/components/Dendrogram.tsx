// @vitest-environment jsdom
/**
 * Dendrogram — left-to-right hierarchical clustering tree.
 *
 * Phase 9a T7. Shows how domain terms cluster according to model pile-sort data.
 *
 * Data fields (from domain JSON — may be absent in early published data):
 *   term_cluster_linkage:     number[][]     scipy linkage matrix (n-1 rows × 4 cols)
 *   term_mds_items:           string[]       leaf labels (term names)
 *   term_cluster_assignments: Record<string, number>  item → cluster_id
 *   term_cluster_labels:      string[]       one per cluster
 *   term_cluster_bp_values:   number[]       bootstrap proportion per internal node
 *
 * Handles missing/empty data gracefully with appropriate empty state.
 *
 * Visual spec (from DESIGN_SYSTEM.md v0.5.2 §12 T7 + UI/UX verdict):
 *   - Left-to-right orientation. Root on left, leaves on right.
 *   - SVG 800px wide; height = n_terms * 20 + margin.top + margin.bottom
 *   - Margin: top 24, bottom 32
 *   - Branch color: cluster color when single-cluster subtree; gray (text-secondary) for cross-cluster merges
 *   - Stroke width 1.5px
 *   - BP >= 0.70: solid, no annotation
 *   - BP < 0.70: dashed (5 3), 60% opacity, numeric label left of node
 *   - Leaf: 4px filled circle + term name at xs
 *   - Cluster label at innermost full-cluster merge node
 *   - Tooltip (dark inverted): subtree terms, cluster labels, BP if < threshold
 *   - Legend: dashed branch explanation
 *   - Mobile <768px: hide leaf labels; leaf circles remain
 *   - ReadAsTableToggle + DendrogramTable + ScreenReaderSummary
 *
 * Rendering algorithm:
 *   1. Parse linkage matrix into tree structure
 *   2. Assign y-positions to leaves (evenly spaced, 20px apart)
 *   3. Internal nodes: y = mean of children y-positions
 *   4. x-positions: leaves at right edge, internals at x proportional to distance
 *   5. Draw L-shaped connectors (horizontal to parent-x, vertical to parent-y)
 *
 * Forbidden vocabulary: no "worldview", "believes", "thinks" (model-applied),
 *   "understands", "sees" per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
 *
 * Reference:
 *   DESIGN_SYSTEM.md v0.5.2 (Phase 9a T7 visual spec)
 *   docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md
 *   docs/status/2026-05-24-phase9a-cda-sme-verdict.md §5a (M5a BP threshold)
 */

import { useState, useMemo, useCallback } from "react";
import type { DomainResultPublished } from "../data/types";
import { DENDROGRAM_SUPPORT_THRESHOLD } from "../config/analysis";
import { ScreenReaderSummary } from "./ScreenReaderSummary";
import { ReadAsTableToggle } from "./ReadAsTableToggle";
import { DendrogramTable } from "./DendrogramTable";
import type { DendrogramTableRow } from "./DendrogramTable";
import {
  READ_AS_TABLE_LABEL_REST,
  READ_AS_TABLE_LABEL_PRESSED,
  dendrogramScreenReaderSummary,
} from "../copy/screen_reader_summaries";
import "../styles/dendrogram.css";

// ── Props ────────────────────────────────────────────────────────────────────

export interface DendrogramProps {
  domainResult: DomainResultPublished;
  selectedModels?: string[];
}

// ── Linkage tree types ────────────────────────────────────────────────────────

interface TreeNode {
  id: number;           // 0..n-1 = leaf, n..2n-2 = internal
  y: number;            // SVG y-position (computed)
  x: number;            // SVG x-position (computed)
  children: number[];   // child node ids
  isLeaf: boolean;
  leafIndex: number | null;  // index into term_mds_items for leaf nodes
  distance: number;     // merge distance (0 for leaves)
  leafSet: Set<number>; // set of leaf indices in this subtree
}

// ── SVG constants ─────────────────────────────────────────────────────────────

const SVG_WIDTH = 800;
const MARGIN = { top: 24, bottom: 32, left: 60, right: 140 };
const LEAF_SPACING = 20; // px per leaf
const LEAF_CIRCLE_RADIUS = 4;
const LABEL_OFFSET = 8; // px right of leaf circle

// ── Cluster color mapping ─────────────────────────────────────────────────────

const CLUSTER_COLORS: string[] = [
  "var(--color-cluster-1)",
  "var(--color-cluster-2)",
  "var(--color-cluster-3)",
  "var(--color-cluster-4)",
  "var(--color-cluster-5)",
  "var(--color-cluster-6)",
  "var(--color-cluster-7)",
  "var(--color-cluster-8)",
];

function clusterColor(clusterId: number): string {
  if (clusterId >= 0 && clusterId < CLUSTER_COLORS.length) {
    return CLUSTER_COLORS[clusterId];
  }
  return "var(--color-text-secondary)";
}

// ── Linkage parsing ───────────────────────────────────────────────────────────

/**
 * Parse a scipy linkage matrix into a tree of TreeNode objects.
 * Returns null if the matrix is empty or malformed.
 */
function parseLinkageMatrix(
  matrix: number[][],
  nLeaves: number
): Map<number, TreeNode> | null {
  if (!matrix || matrix.length === 0 || nLeaves < 2) return null;

  const nodes = new Map<number, TreeNode>();

  // Initialise leaf nodes (ids 0..nLeaves-1)
  for (let i = 0; i < nLeaves; i++) {
    nodes.set(i, {
      id: i,
      y: 0,
      x: 0,
      children: [],
      isLeaf: true,
      leafIndex: i,
      distance: 0,
      leafSet: new Set([i]),
    });
  }

  // Build internal nodes from linkage rows
  for (let rowIdx = 0; rowIdx < matrix.length; rowIdx++) {
    const row = matrix[rowIdx];
    if (!row || row.length < 4) continue;

    const [idx1Raw, idx2Raw, distance] = row;
    const idx1 = Math.round(idx1Raw);
    const idx2 = Math.round(idx2Raw);
    const internalId = nLeaves + rowIdx;

    const child1 = nodes.get(idx1);
    const child2 = nodes.get(idx2);
    if (!child1 || !child2) continue;

    const leafSet = new Set([...child1.leafSet, ...child2.leafSet]);

    nodes.set(internalId, {
      id: internalId,
      y: 0,
      x: 0,
      children: [idx1, idx2],
      isLeaf: false,
      leafIndex: null,
      distance,
      leafSet,
    });
  }

  return nodes;
}

/**
 * Assign y-positions to all nodes in the tree.
 * Leaves are positioned in the order they appear in a post-order traversal,
 * spaced LEAF_SPACING px apart. Internal nodes get the mean y of their children.
 */
function assignYPositions(
  nodes: Map<number, TreeNode>,
  nLeaves: number
): void {
  // Find the root (the last internal node: id = 2*nLeaves - 2)
  const rootId = 2 * nLeaves - 2;

  // Post-order traversal to assign leaf y-positions
  let leafCounter = 0;

  function traverse(nodeId: number): void {
    const node = nodes.get(nodeId);
    if (!node) return;

    if (node.isLeaf) {
      node.y = MARGIN.top + leafCounter * LEAF_SPACING;
      leafCounter++;
    } else {
      for (const childId of node.children) {
        traverse(childId);
      }
      // Internal node: mean of children y-positions
      const childYs = node.children
        .map((cid) => nodes.get(cid)?.y ?? 0);
      node.y = childYs.reduce((a, b) => a + b, 0) / childYs.length;
    }
  }

  traverse(rootId);
}

/**
 * Assign x-positions. Leaves go to the right edge (PLOT_RIGHT).
 * Internal nodes are at x proportional to distance, scaled so
 * root (max distance) sits at MARGIN.left.
 */
function assignXPositions(
  nodes: Map<number, TreeNode>,
  nLeaves: number,
  plotWidth: number
): void {
  // Collect all distances to find the range
  const distances: number[] = [];
  nodes.forEach((node) => {
    if (!node.isLeaf) distances.push(node.distance);
  });
  const maxDist = distances.length > 0 ? Math.max(...distances) : 1;

  const plotLeft = MARGIN.left;
  const plotRight = plotLeft + plotWidth;

  nodes.forEach((node) => {
    if (node.isLeaf) {
      node.x = plotRight;
    } else {
      // Map distance to x: maxDist → plotLeft; 0 → plotRight.
      // But zero distance makes no sense visually — place at right if 0.
      if (maxDist === 0) {
        node.x = plotLeft;
      } else {
        node.x = plotLeft + ((maxDist - node.distance) / maxDist) * plotWidth;
      }
    }
  });

  // Root (highest distance) should be closest to left edge.
  // Adjust: root id = 2*nLeaves - 2.
  const _ = nLeaves; void _;
}

// ── Subtree cluster detection ─────────────────────────────────────────────────

/**
 * Returns the single cluster id for a subtree if all leaves share the same
 * cluster assignment, or null if the subtree spans multiple clusters.
 */
function subtreeClusterId(
  leafSet: Set<number>,
  clusterAssignments: number[]
): number | null {
  let clusterId: number | null = null;
  for (const leafIdx of leafSet) {
    const c = clusterAssignments[leafIdx];
    if (c === undefined) return null;
    if (clusterId === null) {
      clusterId = c;
    } else if (c !== clusterId) {
      return null;
    }
  }
  return clusterId;
}

// ── Tooltip state ─────────────────────────────────────────────────────────────

interface TooltipState {
  x: number;
  y: number;
  nodeId: number;
}

// ── Description paragraph text ────────────────────────────────────────────────

function descriptionText(domainSlug: string): string {
  return `How ${domainSlug} terms cluster hierarchically: grouped terms appear together in model pile sorts. Dashed branches indicate groupings that appeared in fewer than ${Math.round(DENDROGRAM_SUPPORT_THRESHOLD * 100)}% of bootstrap resamples — treat them with caution.`;
}

// ── Legend explanation text ───────────────────────────────────────────────────

const LEGEND_TEXT = `Dashed branches: bootstrap support below ${Math.round(DENDROGRAM_SUPPORT_THRESHOLD * 100)}% — these groupings are less stable across model resampling.`;

// ── Table container ID (U1 pattern) ──────────────────────────────────────────

const DENDROGRAM_TABLE_CONTAINER_ID = "dendrogram-table-container";

// ── Main component ────────────────────────────────────────────────────────────

export function Dendrogram({ domainResult }: DendrogramProps) {
  const [readAsTable, setReadAsTable] = useState(false);
  const [showLabels, setShowLabels] = useState(true);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  // Extract raw dendrogram data — may be absent in early published JSON.
  const raw = domainResult as unknown as Record<string, unknown>;
  const linkageMatrix = (raw["term_cluster_linkage"] as number[][] | undefined) ?? null;
  const termItems = (raw["term_mds_items"] as string[] | undefined) ?? null;
  const rawAssignments = (raw["term_cluster_assignments"] as Record<string, number> | undefined) ?? null;
  const clusterLabels = (raw["term_cluster_labels"] as string[] | undefined) ?? null;
  const bpValues = (raw["term_cluster_bp_values"] as number[] | undefined) ?? null;

  // Derived: is the data available?
  const hasData = linkageMatrix !== null && termItems !== null && termItems.length >= 2;

  // Build cluster assignments array (indexed by leaf position in termItems)
  const clusterAssignments: number[] = useMemo(() => {
    if (!termItems || !rawAssignments) return [];
    return termItems.map((item) => rawAssignments[item] ?? 0);
  }, [termItems, rawAssignments]);

  // Build tree structure
  const treeNodes = useMemo(() => {
    if (!hasData || !linkageMatrix || !termItems) return null;
    const nodes = parseLinkageMatrix(linkageMatrix, termItems.length);
    if (!nodes) return null;
    assignYPositions(nodes, termItems.length);
    const plotWidth = SVG_WIDTH - MARGIN.left - MARGIN.right;
    assignXPositions(nodes, termItems.length, plotWidth);
    return nodes;
  }, [hasData, linkageMatrix, termItems]);

  const nLeaves = termItems?.length ?? 0;
  const svgHeight = nLeaves * LEAF_SPACING + MARGIN.top + MARGIN.bottom;

  // Unique cluster ids present
  const uniqueClusterIds: number[] = useMemo(() => {
    const seen = new Set<number>();
    clusterAssignments.forEach((c) => seen.add(c));
    return Array.from(seen).sort((a, b) => a - b);
  }, [clusterAssignments]);

  // Find the innermost node where each cluster's full leaf set merges
  const clusterMergeNodes: Map<number, number> = useMemo(() => {
    if (!treeNodes || clusterAssignments.length === 0) return new Map();

    const result = new Map<number, number>();

    // For each cluster, find the node with the matching leaf set
    for (const cid of uniqueClusterIds) {
      const clusterLeaves = new Set<number>(
        clusterAssignments
          .map((c, i) => (c === cid ? i : -1))
          .filter((i) => i >= 0)
      );
      if (clusterLeaves.size === 0) continue;

      // Search for the smallest internal node whose leafSet equals clusterLeaves
      let bestNode: number | null = null;
      let bestSize = Infinity;

      treeNodes.forEach((node) => {
        if (node.isLeaf) return;
        // Check if this node's leafSet exactly matches clusterLeaves
        if (node.leafSet.size !== clusterLeaves.size) return;
        let matches = true;
        for (const l of clusterLeaves) {
          if (!node.leafSet.has(l)) {
            matches = false;
            break;
          }
        }
        if (matches && node.leafSet.size < bestSize) {
          bestSize = node.leafSet.size;
          bestNode = node.id;
        }
      });

      if (bestNode !== null) {
        result.set(cid, bestNode);
      }
    }
    return result;
  }, [treeNodes, clusterAssignments, uniqueClusterIds]);

  // Build table rows for DendrogramTable
  const tableRows: DendrogramTableRow[] = useMemo(() => {
    if (!termItems || !clusterLabels || clusterAssignments.length === 0) return [];

    return termItems.map((term, leafIdx) => {
      const cid = clusterAssignments[leafIdx] ?? 0;
      const clusterLabel = clusterLabels[cid] ?? `Cluster ${cid + 1}`;

      // Compute subtree depth: how far up the tree before this leaf merges with another cluster
      // For simplicity, use the number of ancestors until a cross-cluster merge
      // (We approximate: just use the internal node depth count from leaf)
      let depth = 0;
      if (treeNodes) {
        // Walk from root to find merge depth for this leaf
        const rootId = 2 * nLeaves - 2;
        const nodeMap = treeNodes;
        function findDepth(nodeId: number, currentDepth: number): void {
          const node = nodeMap.get(nodeId);
          if (!node) return;
          if (node.isLeaf) {
            if (node.leafIndex === leafIdx) depth = currentDepth;
            return;
          }
          for (const childId of node.children) {
            findDepth(childId, currentDepth + 1);
          }
        }
        if (nLeaves >= 2) findDepth(rootId, 0);
      }

      // Find BP for the node where this leaf first joins another leaf
      // This is the first non-leaf ancestor that contains only this leaf + one more.
      let bpSupport: number | null = null;
      if (treeNodes && bpValues) {
        // Internal nodes have IDs nLeaves..2*nLeaves-2
        // bp_values[i] corresponds to linkage row i, i.e., internal node nLeaves+i
        // Find the smallest internal node containing this leaf
        let smallestInternalSize = Infinity;
        treeNodes.forEach((node) => {
          if (node.isLeaf) return;
          if (!node.leafSet.has(leafIdx)) return;
          if (node.leafSet.size < smallestInternalSize) {
            smallestInternalSize = node.leafSet.size;
            const bpIdx = node.id - nLeaves;
            bpSupport = bpValues[bpIdx] ?? null;
          }
        });
      }

      return {
        cluster: clusterLabel,
        term,
        subtreeDepth: depth,
        bpSupport,
      };
    });
  }, [termItems, clusterLabels, clusterAssignments, treeNodes, bpValues, nLeaves]);

  // SR summary
  const nClusters = uniqueClusterIds.length;
  const nUnstableBranches = bpValues
    ? bpValues.filter((bp) => bp < DENDROGRAM_SUPPORT_THRESHOLD).length
    : 0;
  const srSummaryText = dendrogramScreenReaderSummary(
    domainResult.domain_slug,
    nLeaves,
    nClusters,
    nUnstableBranches
  );

  // Tooltip handlers
  const handleBranchMouseEnter = useCallback(
    (nodeId: number, e: React.MouseEvent<SVGElement>) => {
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        nodeId,
      });
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setTooltip(null);
  }, []);

  const handleMouseMove = useCallback(
    (nodeId: number, e: React.MouseEvent<SVGElement>) => {
      const rect = (e.currentTarget.ownerSVGElement ?? e.currentTarget).getBoundingClientRect();
      setTooltip({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        nodeId,
      });
    },
    []
  );

  // Build tooltip content for a given node
  function buildTooltipContent(nodeId: number): React.ReactNode {
    if (!treeNodes || !termItems) return null;
    const node = treeNodes.get(nodeId);
    if (!node) return null;

    if (node.isLeaf) {
      // Leaf tooltip: term name + cluster label
      const leafIdx = node.leafIndex ?? 0;
      const term = termItems[leafIdx] ?? "";
      const cid = clusterAssignments[leafIdx] ?? 0;
      const clusterLabel = clusterLabels?.[cid] ?? `Cluster ${cid + 1}`;
      return (
        <div>
          <div className="dendrogram__tooltip-label">{term}</div>
          <div style={{ color: "var(--color-tooltip-dark-text)", opacity: 0.85 }}>{clusterLabel}</div>
        </div>
      );
    }

    // Internal node: up to 5 subtree terms + cluster labels + BP if < threshold
    const leafIndices = Array.from(node.leafSet);
    const terms = leafIndices.map((i) => termItems[i] ?? "").filter(Boolean);
    const shown = terms.slice(0, 5);
    const rest = terms.length - shown.length;

    // Cluster labels in this subtree
    const subtreeClusters = new Set(leafIndices.map((i) => clusterAssignments[i] ?? 0));
    const clusterLabelsList = Array.from(subtreeClusters)
      .map((cid) => clusterLabels?.[cid] ?? `Cluster ${cid + 1}`)
      .join(", ");

    const bpIdx = nodeId - nLeaves;
    const bp = bpValues?.[bpIdx] ?? null;
    const showBp = bp !== null && bp < DENDROGRAM_SUPPORT_THRESHOLD;

    return (
      <div>
        <div className="dendrogram__tooltip-terms">
          <div className="dendrogram__tooltip-label" style={{ color: "var(--color-tooltip-dark-text)" }}>
            {clusterLabelsList}
          </div>
          <div style={{ marginTop: "2px" }}>
            {shown.join(", ")}
            {rest > 0 && ` +${rest} more`}
          </div>
        </div>
        {showBp && bp !== null && (
          <div className="dendrogram__tooltip-bp">
            Bootstrap support: {(bp * 100).toFixed(0)}% (below {Math.round(DENDROGRAM_SUPPORT_THRESHOLD * 100)}% threshold)
          </div>
        )}
      </div>
    );
  }

  // Empty state
  if (!hasData) {
    return (
      <div className="dendrogram">
        <ScreenReaderSummary text="No hierarchical cluster data available for this domain." />
        <p style={{ color: "var(--color-text-caption)", fontSize: "var(--font-size-xs)" }}>
          Hierarchical cluster data is not yet available for this domain.
        </p>
      </div>
    );
  }

  // Render branches
  function renderBranches(): React.ReactNode[] {
    if (!treeNodes || !termItems) return [];
    const elements: React.ReactNode[] = [];

    treeNodes.forEach((node) => {
      if (node.isLeaf) return;

      const bpIdx = node.id - nLeaves;
      const bp = bpValues?.[bpIdx] ?? null;
      const isUnstable = bp !== null && bp < DENDROGRAM_SUPPORT_THRESHOLD;

      const strokeDasharray = isUnstable ? "5 3" : undefined;
      const opacity = isUnstable ? 0.6 : 1;

      // Draw the horizontal line from this node's x to the parent's x
      // (connecting node to where it joins the next level)
      // We only draw child-to-parent connectors here:
      // For each child of this node, draw:
      //   1. Horizontal line from child.x to node.x at child.y
      //   2. Vertical line from child.y to node.y at node.x
      for (const childId of node.children) {
        const child = treeNodes.get(childId);
        if (!child) continue;

        // Determine child branch color
        const childCid = subtreeClusterId(child.leafSet, clusterAssignments);
        const childColor =
          childCid !== null
            ? clusterColor(childCid)
            : "var(--color-text-secondary)";

        const pathD =
          `M ${child.x.toFixed(1)} ${child.y.toFixed(1)} ` +
          `H ${node.x.toFixed(1)} ` +
          `V ${node.y.toFixed(1)}`;

        elements.push(
          <path
            key={`branch-${node.id}-${childId}`}
            d={pathD}
            stroke={childColor}
            strokeWidth="1.5"
            fill="none"
            strokeDasharray={strokeDasharray}
            opacity={opacity}
            className={`dendrogram__branch${isUnstable ? " dendrogram__branch--unstable" : ""}`}
            onMouseEnter={(e) => handleBranchMouseEnter(node.id, e)}
            onMouseLeave={handleMouseLeave}
            onMouseMove={(e) => handleMouseMove(node.id, e)}
            style={{ cursor: "default" }}
          />
        );
      }

      // BP label for unstable branches (left of node)
      if (isUnstable && bp !== null) {
        elements.push(
          <text
            key={`bp-${node.id}`}
            x={node.x - 4}
            y={node.y - 3}
            textAnchor="end"
            className="dendrogram__bp-label"
            style={{ pointerEvents: "none" }}
          >
            {(bp * 100).toFixed(0)}%
          </text>
        );
      }

      // Cluster label annotation at the innermost full-cluster merge node
      for (const [cid, mergeNodeId] of clusterMergeNodes) {
        if (mergeNodeId === node.id && clusterLabels) {
          const label = clusterLabels[cid] ?? `Cluster ${cid + 1}`;
          elements.push(
            <text
              key={`cluster-label-${cid}`}
              x={node.x - 6}
              y={node.y - 10}
              textAnchor="end"
              className="dendrogram__cluster-label"
              fill={clusterColor(cid)}
              style={{ pointerEvents: "none" }}
            >
              {label}
            </text>
          );
        }
      }
    });

    return elements;
  }

  // Render leaf nodes
  function renderLeaves(): React.ReactNode[] {
    if (!treeNodes || !termItems) return [];
    const elements: React.ReactNode[] = [];

    treeNodes.forEach((node) => {
      if (!node.isLeaf || node.leafIndex === null) return;
      const term = termItems[node.leafIndex];
      const cid = clusterAssignments[node.leafIndex] ?? 0;
      const color = clusterColor(cid);

      elements.push(
        <g
          key={`leaf-${node.id}`}
          onMouseEnter={(e) => handleBranchMouseEnter(node.id, e)}
          onMouseLeave={handleMouseLeave}
          onMouseMove={(e) => handleMouseMove(node.id, e)}
          style={{ cursor: "default" }}
          aria-label={`${term} — ${clusterLabels?.[cid] ?? `Cluster ${cid + 1}`}`}
        >
          {/* Leaf circle */}
          <circle
            cx={node.x}
            cy={node.y}
            r={LEAF_CIRCLE_RADIUS}
            fill={color}
            stroke="none"
            className="dendrogram__leaf-circle"
          />
          {/* Term label */}
          {showLabels && (
            <text
              x={node.x + LEAF_CIRCLE_RADIUS + LABEL_OFFSET}
              y={node.y + 4}
              className="dendrogram__leaf-label"
              style={{ pointerEvents: "none" }}
            >
              {term}
            </text>
          )}
        </g>
      );
    });

    return elements;
  }

  // Tooltip node for current hover
  const tooltipNode = tooltip !== null && treeNodes ? treeNodes.get(tooltip.nodeId) ?? null : null;

  return (
    <div className="dendrogram">
      {/* ScreenReaderSummary — always present */}
      <ScreenReaderSummary text={srSummaryText} />

      {/* Description paragraph */}
      <p className="dendrogram__description">
        {descriptionText(domainResult.domain_slug)}
      </p>

      {/* Show-labels toggle (desktop only; hidden on mobile via CSS) */}
      <label className="dendrogram__label-toggle">
        <input
          type="checkbox"
          checked={showLabels}
          onChange={(e) => setShowLabels(e.target.checked)}
          aria-label="Show leaf term labels"
        />
        Show labels
      </label>

      {/* ReadAsTableToggle */}
      <ReadAsTableToggle
        pressed={readAsTable}
        onToggle={() => setReadAsTable((v) => !v)}
        tableContainerId={DENDROGRAM_TABLE_CONTAINER_ID}
        labels={{ rest: READ_AS_TABLE_LABEL_REST, pressed: READ_AS_TABLE_LABEL_PRESSED }}
      />

      {/* SVG — hidden when table active (U1 pattern) */}
      <div
        className="dendrogram__svg-wrapper"
        aria-hidden={readAsTable || undefined}
        style={{ display: readAsTable ? "none" : undefined }}
      >
        <svg
          className="dendrogram__svg"
          width={SVG_WIDTH}
          height={svgHeight}
          viewBox={`0 0 ${SVG_WIDTH} ${svgHeight}`}
          role="img"
          aria-label={`Hierarchical cluster tree for the ${domainResult.domain_slug} domain with ${nLeaves} terms in ${nClusters} cluster${nClusters !== 1 ? "s" : ""}.`}
        >
          {/* Branches (back layer) */}
          <g aria-hidden="true">
            {renderBranches()}
          </g>

          {/* Leaf nodes (front layer) */}
          <g>
            {renderLeaves()}
          </g>
        </svg>
      </div>

      {/* Tooltip */}
      {!readAsTable && tooltip !== null && tooltipNode !== null && (
        <div
          className="dendrogram__tooltip"
          role="tooltip"
          style={{ left: tooltip.x + 12, top: tooltip.y - 8 }}
        >
          {buildTooltipContent(tooltip.nodeId)}
        </div>
      )}

      {/* Legend */}
      {!readAsTable && (
        <div className="dendrogram__legend">
          <span className="dendrogram__legend-dashed" aria-hidden="true">
            <svg width="28" height="12" viewBox="0 0 28 12">
              <line
                x1="0" y1="6" x2="28" y2="6"
                stroke="var(--color-text-secondary)"
                strokeWidth="1.5"
                strokeDasharray="5 3"
                opacity="0.6"
              />
            </svg>
          </span>
          <span className="dendrogram__legend-text">{LEGEND_TEXT}</span>
        </div>
      )}

      {/* Cluster color key */}
      {!readAsTable && uniqueClusterIds.length > 0 && clusterLabels && (
        <div className="dendrogram__cluster-key" aria-label="Cluster color key">
          {uniqueClusterIds.map((cid) => (
            <div key={cid} className="dendrogram__cluster-key-item">
              <div
                className="dendrogram__cluster-key-swatch"
                style={{ background: clusterColor(cid) }}
                aria-hidden="true"
              />
              <span>{clusterLabels[cid] ?? `Cluster ${cid + 1}`}</span>
            </div>
          ))}
        </div>
      )}

      {/* Table container — U1 pattern: always in DOM */}
      <div
        id={DENDROGRAM_TABLE_CONTAINER_ID}
        aria-hidden={readAsTable ? undefined : true}
        style={{ display: readAsTable ? undefined : "none" }}
        className="dendrogram__table-container"
      >
        <DendrogramTable
          rows={tableRows}
          domainSlug={domainResult.domain_slug}
        />
      </div>
    </div>
  );
}
