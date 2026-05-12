/**
 * VizSwitcher — §3.2 tab bar for the Data Explorer.
 *
 * Phase 5: one active tab (MDS Plot), three disabled tabs (Free Lists,
 * Similarity, Drift). Disabled tabs are rendered as visible affordances that
 * communicate future capability without claiming it exists.
 *
 * Phase 6 T7: Free Lists tab is now active. #freelist is a valid URL fragment.
 * Similarity and Drift remain disabled (Phase-6-T5 / Phase-6-T4 territory).
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
 * URL state: clicking MDS Plot pushes #mds fragment; clicking Free Lists
 * pushes #freelist. Similarity / Drift do not update the URL (disabled).
 *
 * Reference: docs/status/2026-05-12-phase6-T7-architect-plan.md §2.1
 */

import { type KeyboardEvent } from "react";

/** Active tab values — widened from "mds" to include "freelist" at Phase 6 T7. */
export type ActiveVizTab = "mds" | "freelist";

export interface VizSwitcherProps {
  activeTab: ActiveVizTab;
  onTabChange: (tab: ActiveVizTab) => void;
}

/** Type guard for activatable tab ids. */
function isActivatableTab(id: string): id is ActiveVizTab {
  return id === "mds" || id === "freelist";
}

/** Tab definition (internal). */
interface TabDef {
  id: string;
  label: string;
  active: boolean;
  disabled: boolean;
}

const TABS: TabDef[] = [
  { id: "mds",        label: "MDS Plot",    active: true,  disabled: false },
  { id: "freelist",   label: "Free Lists",  active: false, disabled: false },
  { id: "similarity", label: "Similarity",  active: false, disabled: true  },
  { id: "drift",      label: "Drift",       active: false, disabled: true  },
];

/** Fragments that are still disabled (Phase-6-T4 / Phase-6-T5 territory). */
const DISABLED_FRAGMENTS = new Set(["similarity", "drift"]);

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
    if (raw === "freelist") {
      return "freelist";
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
