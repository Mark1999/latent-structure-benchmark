/**
 * ReadAsTableToggle — toggle button for Read-as-table / Show visualization mode.
 *
 * Phase 6 T8. Implements DESIGN_SYSTEM.md §7 and the new §12.9 (v0.4.6).
 *
 * U1 (BINDING — Option A): The table container div is ALWAYS rendered in the DOM.
 *   When readAsTable = false: aria-hidden="true" + display:none on the container.
 *   aria-controls references the always-present container id.
 *   This satisfies WAI-ARIA 1.2 §6.6.5 (aria-controls must reference an existing element).
 *
 * U2 (BINDING): Pressed-state non-text visual indicator per WCAG 1.4.11.
 *   border: 2px solid var(--color-info) when pressed.
 *   border: 2px solid transparent at rest (prevents layout shift).
 *   See read-as-table.css.
 *
 * Button labels come from src/copy/screen_reader_summaries.ts (single source of truth).
 * No string literals for LSB-authored prose in this component.
 *
 * Does NOT import any LLM client (CLAUDE.md §6 R11).
 * Does NOT touch data/types.ts (AC #19).
 *
 * Reference:
 *   docs/status/2026-05-12-phase6-T8-architect-plan.md §2.2
 *   docs/status/2026-05-12-phase6-T8-uiux-plan-verdict.md U1, U2
 *   DESIGN_SYSTEM.md §12.9 (v0.4.6)
 */

import "../styles/read-as-table.css";

export interface ReadAsTableToggleProps {
  /** Whether the table mode is currently active. */
  pressed: boolean;
  /** Callback to toggle the mode. */
  onToggle: () => void;
  /**
   * The id attribute of the always-present table container div.
   * Used for aria-controls (U1 Option A — container always in DOM).
   */
  tableContainerId: string;
  /** Button labels from screen_reader_summaries.ts */
  labels: { rest: string; pressed: string };
}

export function ReadAsTableToggle({
  pressed,
  onToggle,
  tableContainerId,
  labels,
}: ReadAsTableToggleProps) {
  return (
    <div className="read-as-table-toggle">
      <button
        type="button"
        className="read-as-table-toggle__button"
        aria-pressed={pressed}
        aria-controls={tableContainerId}
        onClick={onToggle}
      >
        {pressed ? labels.pressed : labels.rest}
      </button>
    </div>
  );
}
