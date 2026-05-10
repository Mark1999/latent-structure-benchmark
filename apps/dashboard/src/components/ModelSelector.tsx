/**
 * ModelSelector — control panel per DESIGN_SYSTEM.md §3.7.
 *
 * Renders one checkbox row per model in domainResult.models filtered to those
 * with MDS coordinates. Features:
 *   - Checkbox toggle (label wrapping input for full click-target affordance)
 *   - 12px color dot in model color
 *   - Model short name
 *   - Origin badge [US] / [EU] / [CN] in --color-origin-{us,eu,cn} token color
 *   - Open/closed weights indicator (text badge "open" / "closed")
 *   - Models grouped by origin: US first, then EU, then CN. Thin dividers.
 *   - "Select all" / "Clear all" links at the bottom
 *   - Max-6-selected enforcement: attempt to add a 7th shows role="alert" warning
 *     and does NOT call onSelectionChange.
 *
 * Accessibility (§7 binding):
 *   - Each checkbox is a <label> wrapping <input type="checkbox">
 *   - aria-label on each input: "Toggle {short name} (origin: {US|EU|CN}; weights: {open|closed})"
 *   - Keyboard: native checkbox semantics (Tab navigates, Space toggles)
 *   - Max-6 warning: role="alert" aria-live="polite" for screen reader announcement
 *   - "Select all" / "Clear all" are <button> elements with aria-label
 *
 * Styling: all via design tokens — no hardcoded colors or sizes.
 * Token colors are applied via inline style (CSS custom properties are not
 * directly accessible from JS, so we resolve to the known token values).
 *
 * Origin token values from DESIGN_SYSTEM.md §1.2:
 *   --color-origin-us: #3360a9
 *   --color-origin-eu: #27ae60
 *   --color-origin-cn: #c0392b
 */

import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";

// ── Origin token color resolution ────────────────────────────────────────────
// Values from DESIGN_SYSTEM.md §1.2 color palette.

const ORIGIN_COLORS: Record<string, string> = {
  us: "#3360a9", // --color-origin-us
  eu: "#27ae60", // --color-origin-eu
  cn: "#c0392b", // --color-origin-cn
};

const ORIGIN_LABELS: Record<string, string> = {
  us: "US",
  eu: "EU",
  cn: "CN",
};

// ── Constants ─────────────────────────────────────────────────────────────────

/** Maximum models that may be selected simultaneously per §3.7 binding. */
const MAX_SELECTED = 6;

// ── Origin group ordering ────────────────────────────────────────────────────

const ORIGIN_ORDER = ["us", "eu", "cn"];

// ── Props ────────────────────────────────────────────────────────────────────

export interface ModelSelectorProps {
  domainResult: DomainResultPublished;
  /** Currently selected model_ids. Controlled prop. */
  selectedModels: string[];
  /** Called when selection should change. The caller is responsible for state. */
  onSelectionChange: (next: string[]) => void;
  /** model_id → CSS hex color. Per §12.4 sorted-model_id algorithm (owned by App.tsx). */
  modelColors: Record<string, string>;
}

// ── Component ────────────────────────────────────────────────────────────────

/**
 * ModelSelector renders the control panel for toggling which models appear
 * on the MDS plot. Selection is controlled externally via selectedModels /
 * onSelectionChange.
 */
export function ModelSelector({
  domainResult,
  selectedModels,
  onSelectionChange,
  modelColors,
}: ModelSelectorProps) {
  // Build the available model list: only models that have MDS coordinates.
  const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
  const coordModelIds = new Set(Object.keys(rawCoords));

  const availableModels = domainResult.models.filter((m) =>
    coordModelIds.has(m.model_id)
  );

  // Group by origin in ORIGIN_ORDER. Models with unknown origins go last.
  const grouped: { origin: string; models: typeof availableModels }[] = [];
  const usedOrigins = new Set<string>();

  for (const origin of ORIGIN_ORDER) {
    const group = availableModels.filter((m) => m.origin === origin);
    if (group.length > 0) {
      grouped.push({ origin, models: group });
      usedOrigins.add(origin);
    }
  }
  // Any remaining origins not in ORIGIN_ORDER.
  const otherModels = availableModels.filter((m) => !usedOrigins.has(m.origin));
  if (otherModels.length > 0) {
    grouped.push({ origin: "other", models: otherModels });
  }

  const selectedSet = new Set(selectedModels);
  const allIds = availableModels.map((m) => m.model_id);

  const isMaxReached = selectedModels.length >= MAX_SELECTED;

  // Whether to show the max warning — shown when user is AT the limit.
  // The warning appears when 6 are already selected (not on attempt; we
  // prevent the toggle and show the warning inline at the top of the panel).
  const showMaxWarning = selectedModels.length >= MAX_SELECTED;

  function handleToggle(modelId: string) {
    const isSelected = selectedSet.has(modelId);
    if (!isSelected && isMaxReached) {
      // Refuse the selection — do not call onSelectionChange.
      // The warning is already visible because showMaxWarning is true.
      return;
    }
    if (isSelected) {
      onSelectionChange(selectedModels.filter((id) => id !== modelId));
    } else {
      onSelectionChange([...selectedModels, modelId]);
    }
  }

  function handleSelectAll() {
    // Select all available models (may exceed 6 if corpus grows; spec says to
    // apply max enforcement at toggle time, not at "Select all" — select all
    // always sets to the full available set per the AC 4 requirement).
    onSelectionChange(allIds);
  }

  function handleClearAll() {
    onSelectionChange([]);
  }

  return (
    <div className="model-selector" aria-label="Model selection panel">
      <h3 className="model-selector__heading">Models</h3>

      {/* Max-6 warning — role="alert" aria-live="polite" for screen reader announcement */}
      {showMaxWarning && (
        <div
          className="model-selector__max-warning"
          role="alert"
          aria-live="polite"
        >
          Maximum of 6 models for readability — deselect one to add another
        </div>
      )}

      {/* Origin groups */}
      {grouped.map((group, groupIdx) => {
        const originLabel =
          group.origin in ORIGIN_LABELS ? ORIGIN_LABELS[group.origin] : group.origin.toUpperCase();
        const originColor =
          group.origin in ORIGIN_COLORS ? ORIGIN_COLORS[group.origin] : "var(--color-text-secondary)";

        return (
          <div key={group.origin} className="model-selector__group">
            {/* Thin divider between groups (not before the first) */}
            {groupIdx > 0 && <div className="model-selector__group-divider" aria-hidden="true" />}

            {group.models.map((model) => {
              const isSelected = selectedSet.has(model.model_id);
              const isDisabled = !isSelected && isMaxReached;
              const shortName = modelShortName(model.model_id);
              const color = modelColors[model.model_id] ?? "#7f8c8d";
              const modelOriginLabel =
                model.origin in ORIGIN_LABELS ? ORIGIN_LABELS[model.origin] : model.origin.toUpperCase();
              const weightsLabel = model.open_weights ? "open" : "closed";

              return (
                <label
                  key={model.model_id}
                  className={
                    "model-selector__row" +
                    (isSelected ? " model-selector__row--selected" : "") +
                    (isDisabled ? " model-selector__row--disabled" : "")
                  }
                  title={
                    isDisabled
                      ? "Maximum of 6 models for readability — deselect one to add another"
                      : undefined
                  }
                >
                  <input
                    type="checkbox"
                    className="model-selector__checkbox"
                    checked={isSelected}
                    disabled={isDisabled}
                    onChange={() => handleToggle(model.model_id)}
                    aria-label={`Toggle ${shortName} (origin: ${modelOriginLabel}; weights: ${weightsLabel})`}
                  />
                  {/* 12px color dot in model color */}
                  <span
                    className="model-selector__dot"
                    style={{ backgroundColor: color }}
                    aria-hidden="true"
                  />
                  {/* Model short name */}
                  <span className="model-selector__name">{shortName}</span>
                  {/* Origin badge: [US] / [EU] / [CN] in origin token color */}
                  <span
                    className="model-selector__origin-badge"
                    style={{ color: originColor }}
                    aria-hidden="true"
                  >
                    [{originLabel}]
                  </span>
                  {/* Open/closed weights indicator */}
                  <span
                    className={
                      "model-selector__weights-badge" +
                      (model.open_weights
                        ? " model-selector__weights-badge--open"
                        : " model-selector__weights-badge--closed")
                    }
                    aria-hidden="true"
                  >
                    {model.open_weights ? "open" : "closed"}
                  </span>
                </label>
              );
            })}
          </div>
        );
      })}

      {/* Select all / Clear all links */}
      <div className="model-selector__actions">
        <button
          type="button"
          className="model-selector__action-link"
          onClick={handleSelectAll}
          aria-label="Select all models"
        >
          Select all
        </button>
        <span className="model-selector__action-sep" aria-hidden="true">/</span>
        <button
          type="button"
          className="model-selector__action-link"
          onClick={handleClearAll}
          aria-label="Clear all model selections"
        >
          Clear all
        </button>
      </div>
    </div>
  );
}
