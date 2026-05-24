/**
 * VizSwitcher — §3.2 tab bar for the Data Explorer.
 *
 * Phase 5: one active tab (MDS Plot), three disabled tabs (Free Lists,
 * Similarity, Drift). Disabled tabs are rendered as visible affordances that
 * communicate future capability without claiming it exists.
 *
 * Phase 6 T7: Free Lists tab is now active. #freelist is a valid URL fragment.
 * Phase 6 T5: Similarity tab is now active. #similarity is a valid URL fragment.
 * Drift remains disabled (Phase-6-T4 territory).
 * Phase 9a T10: Centrality tab is now active. #centrality is a valid URL fragment.
 * Phase 9a T9: Pile Structure tab is now active. #piles is a valid URL fragment.
 * Phase 9a T6: Term Map tab is now active. #term-mds is a valid URL fragment.
 * Phase 9a T7: Cluster Tree tab is now active. #cluster-tree is a valid URL fragment.
 *   Final tab order per DESIGN_SYSTEM.md v0.5.2:
 *   MDS Plot | Term Map | Cluster Tree | Free Lists | Similarity | Centrality | Pile Structure | Drift
 *
 * Accessibility — DESIGN_SYSTEM.md §12.3 binding (overrides T8 plan spec):
 *   - Container: role="tablist" with aria-label="Visualization view".
 *   - Each tab: role="tab" with aria-selected and aria-disabled as appropriate.
 *   - Disabled tabs are FOCUSABLE (tabIndex={0} on every tab) per WCAG
 *     2.1 SC 2.1.1: keyboard users must be able to discover all visible
 *     interactive affordances.
 *   - Tooltip on disabled tabs: title="Coming in a future update" — no internal
 *     phase numbering in user-visible copy (§12.3 + F2 UI/UX verdict binding).
 *   - Active tab distinguished from disabled tabs via bottom border + bold
 *     weight — non-color indicator required by §12.3.
 *   - Keyboard: ArrowLeft / ArrowRight between tabs, Enter / Space to activate.
 *
 * URL state: clicking MDS Plot pushes #mds fragment; clicking Term Map pushes
 * #term-mds; clicking Cluster Tree pushes #cluster-tree; clicking Free Lists
 * pushes #freelist; clicking Similarity pushes #similarity; clicking Centrality
 * pushes #centrality. Drift does not update the URL (disabled).
 *
 * Reference: docs/status/2026-05-12-phase6-T7-architect-plan.md §2.1
 *            docs/status/2026-05-12-phase6-T5-architect-plan.md §2
 *            docs/status/2026-05-24-phase9a-viz-gap-kickoff.md T10
 *            docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md
 */

import { type KeyboardEvent } from "react";

/**
 * Active tab values — widened to include "centrality" at Phase 9a T10, "piles" at Phase 9a T9,
 * "term-mds" at Phase 9a T6, and "cluster-tree" at Phase 9a T7.
 */
export type ActiveVizTab = "mds" | "term-mds" | "cluster-tree" | "freelist" | "similarity" | "centrality" | "piles";

export interface VizSwitcherProps {
  activeTab: ActiveVizTab;
  onTabChange: (tab: ActiveVizTab) => void;
}

/** Type guard for activatable tab ids. */
function isActivatableTab(id: string): id is ActiveVizTab {
  return (
    id === "mds" ||
    id === "term-mds" ||
    id === "cluster-tree" ||
    id === "freelist" ||
    id === "similarity" ||
    id === "centrality" ||
    id === "piles"
  );
}

/** Tab definition (internal). */
interface TabDef {
  id: string;
  label: string;
  active: boolean;
  disabled: boolean;
}

/** Binding tab order per DESIGN_SYSTEM.md v0.5.2: MDS Plot | Term Map | Cluster Tree | Free Lists | Similarity | Centrality | Pile Structure | Drift */
const TABS: TabDef[] = [
  { id: "mds",          label: "MDS Plot",       active: true,  disabled: false },
  { id: "term-mds",     label: "Term Map",       active: true,  disabled: false },
  { id: "cluster-tree", label: "Cluster Tree",   active: true,  disabled: false },
  { id: "freelist",     label: "Free Lists",     active: false, disabled: false },
  { id: "similarity",   label: "Similarity",     active: false, disabled: false },
  { id: "centrality",   label: "Centrality",     active: false, disabled: false },
  { id: "piles",        label: "Pile Structure", active: false, disabled: false },
  { id: "drift",        label: "Drift",          active: false, disabled: true  },
];

/** Fragments that are still disabled (Phase-6-T4 territory). */
const DISABLED_FRAGMENTS = new Set(["drift"]);

/**
 * Read the URL fragment on mount and reconcile with active tabs.
 * Returns "mds" or "freelist" as appropriate; falls back to "mds" for
 * unrecognised or disabled fragments (similarity, drift).
 *
 * Exported for direct unit testing — the react-refresh mixed-export warning
 * below is intentional; this function is not a component.
 */
// eslint-disable-next-line react-refresh/only-export-components
export function resolveFragmentOnMount(): ActiveVizTab {
  try {
    const raw = window.location.hash.replace(/^#/, "").toLowerCase();
    if (raw === "mds" || raw === "") {
      return "mds";
    }
    if (raw === "term-mds") {
      return "term-mds";
    }
    if (raw === "cluster-tree") {
      return "cluster-tree";
    }
    if (raw === "freelist") {
      return "freelist";
    }
    if (raw === "similarity") {
      return "similarity";
    }
    if (raw === "centrality") {
      return "centrality";
    }
    if (raw === "piles") {
      return "piles";
    }
    if (DISABLED_FRAGMENTS.has(raw)) {
      console.warn(
        `VizSwitcher: URL fragment "#${raw}" refers to a tab that is not active ` +
          `in the current release. Treating as #mds.`
      );
      return "mds";
    }
  } catch {
    // window.location unavailable in SSR / test environments.
  }
  return "mds";
}

export function VizSwitcher({ activeTab, onTabChange }: VizSwitcherProps) {
  /**
   * Keyboard navigation within the tablist.
   * ArrowLeft / ArrowRight moves focus between tabs.
   * Enter / Space activates the focused tab (only MDS Plot is activatable).
   */
  function handleKeyDown(
    e: KeyboardEvent<HTMLButtonElement>,
    currentIndex: number,
    tab: TabDef
  ): void {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      e.preventDefault();
      const direction = e.key === "ArrowRight" ? 1 : -1;
      const total = TABS.length;
      const nextIndex = (currentIndex + direction + total) % total;
      const tabList = (e.currentTarget as HTMLElement)
        .closest("[role='tablist']")
        ?.querySelectorAll<HTMLButtonElement>("button[role='tab']");
      if (tabList && tabList[nextIndex]) {
        tabList[nextIndex].focus();
      }
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (!tab.disabled && isActivatableTab(tab.id)) {
        onTabChange(tab.id);
      }
    }
  }

  return (
    <div className="viz-switcher">
      <div
        className="viz-switcher__tablist"
        role="tablist"
        aria-label="Visualization view"
      >
        {TABS.map((tab, index) => {
          const isActive = !tab.disabled && tab.id === activeTab;

          return (
            <button
              key={tab.id}
              role="tab"
              className={[
                "viz-switcher__tab",
                isActive ? "viz-switcher__tab--active" : "",
                tab.disabled ? "viz-switcher__tab--disabled" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              aria-selected={isActive ? "true" : "false"}
              aria-disabled={tab.disabled ? "true" : undefined}
              /* Per §12.3 binding: disabled tabs MUST be focusable (tabIndex={0}).
                 The T8 plan spec's "not focusable" is superseded. */
              tabIndex={0}
              /* Browser-native tooltip accessible via both hover and keyboard focus
                 per §12.3. Exact string required: no phase numbering. */
              title={tab.disabled ? "Coming in a future update" : undefined}
              onClick={() => {
                if (!tab.disabled && isActivatableTab(tab.id)) {
                  onTabChange(tab.id);
                }
                /* Disabled tabs: click is suppressed (no onTabChange call, no
                   URL update). The button still receives the click event so the
                   browser shows the title tooltip on mobile tap, but we discard it. */
              }}
              onKeyDown={(e) => handleKeyDown(e, index, tab)}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
