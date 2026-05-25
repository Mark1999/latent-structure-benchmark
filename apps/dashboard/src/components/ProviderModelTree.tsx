/**
 * ProviderModelTree — sidebar provider/model cascading tree.
 *
 * Replaces the flat ModelSelector for the app-shell layout.
 * Groups models by display provider (mapping openrouter → family-based provider),
 * shows chevron expand/collapse per provider, individual model checkboxes,
 * select-all and clear quick actions, open-weights toggle filter.
 *
 * Key differences from ModelSelector:
 *   - NO max-6 limit (per Phase 9a layout task spec)
 *   - Groups by display provider (anthropic, openai, google, meta, xai,
 *     mistral, deepseek, microsoft) not by origin
 *   - Styled for 260px sidebar column
 *   - Receives domainResult + selectedModels + onSelectionChange + modelColors
 *
 * Source: docs/slicer-prototype.html (reference implementation)
 */

import { useState } from "react";
import type { DomainResultPublished } from "../data/types";
import { modelShortName } from "../lib/modelShortName";
import type { Domain } from "./DomainPicker";

// ── Provider metadata ────────────────────────────────────────────────────────

/**
 * Display provider colors — intentionally separate from the §12.4 model palette
 * colors (which encode a per-chart sorted slot assignment, not provider identity).
 * These are sidebar-UI-only color dots, not chart data encodings.
 */
const PROVIDER_COLORS: Record<string, string> = {
  anthropic:  "#d97706",
  openai:     "#10a37f",
  google:     "#4285f4",
  meta:       "#0668e1",
  xai:        "#1d1d1f",
  mistral:    "#f97316",
  deepseek:   "#0ea5e9",
  microsoft:  "#00a4ef",
};

const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
  anthropic:  "Anthropic",
  openai:     "OpenAI",
  google:     "Google",
  meta:       "Meta",
  xai:        "xAI",
  mistral:    "Mistral",
  deepseek:   "DeepSeek",
  microsoft:  "Microsoft",
};

/** Canonical display order for provider groups in the sidebar. */
const PROVIDER_ORDER = [
  "anthropic", "openai", "google", "meta", "xai",
  "mistral", "deepseek", "microsoft",
];

// ── Provider mapping ─────────────────────────────────────────────────────────

/**
 * Map a model to its display provider, resolving openrouter models by family.
 * Models from openrouter map to their underlying provider by family name.
 */
function displayProvider(model: { provider: string; family: string }): string {
  if (model.provider === "openrouter") {
    const familyMap: Record<string, string> = {
      gpt:      "openai",
      llama:    "meta",
      mistral:  "mistral",
      deepseek: "deepseek",
      phi:      "microsoft",
      // xai models on openrouter (grok) go through x-ai directly in practice
    };
    return familyMap[model.family] ?? model.provider;
  }
  // google uses "google" provider directly
  // anthropic uses "anthropic" directly
  // x-ai uses "xai" for display
  if (model.provider === "x-ai") return "xai";
  return model.provider;
}

// ── Chevron SVG ───────────────────────────────────────────────────────────────

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      className="provider-group__chevron"
      style={{ transform: open ? "rotate(90deg)" : undefined, transition: "transform 200ms" }}
      viewBox="0 0 16 16"
      width="12"
      height="12"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M6 4l4 4-4 4" />
    </svg>
  );
}

// ── Short date helper ────────────────────────────────────────────────────────

function shortDate(dateStr: string): string {
  if (!dateStr) return "";
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const parts = dateStr.split("-");
  if (parts.length < 2) return dateStr;
  const month = months[parseInt(parts[1], 10) - 1] ?? "";
  return `${month} '${parts[0].slice(2)}`;
}

// ── Props ─────────────────────────────────────────────────────────────────────

export interface ProviderModelTreeProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  onSelectionChange: (next: string[]) => void;
  modelColors: Record<string, string>;
  domains: Domain[];
  activeSlug: string;
  onDomainSelect: (slug: string) => void;
  openWeightsOnly: boolean;
  onOpenWeightsToggle: (v: boolean) => void;
}

// ── Component ────────────────────────────────────────────────────────────────

export function ProviderModelTree({
  domainResult,
  selectedModels,
  onSelectionChange,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  modelColors: _modelColors,
  domains,
  activeSlug,
  onDomainSelect,
  openWeightsOnly,
  onOpenWeightsToggle,
}: ProviderModelTreeProps) {
  // Track which provider groups are expanded. Default: first in order that has models.
  const [expandedProviders, setExpandedProviders] = useState<Set<string>>(() => {
    return new Set(["anthropic"]);
  });

  // Build available model list from MDS coordinates
  const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
  const coordModelIds = new Set(Object.keys(rawCoords));
  const availableModels = domainResult.models.filter((m) => coordModelIds.has(m.model_id));

  // Apply open-weights filter
  const filteredModels = openWeightsOnly
    ? availableModels.filter((m) => m.open_weights)
    : availableModels;

  // Group filtered models by display provider
  const grouped: Map<string, typeof filteredModels> = new Map();
  for (const prov of PROVIDER_ORDER) {
    grouped.set(prov, []);
  }
  for (const model of filteredModels) {
    const dp = displayProvider(model);
    if (!grouped.has(dp)) {
      grouped.set(dp, []);
    }
    grouped.get(dp)!.push(model);
  }

  // Further group models within each provider by family
  function groupByFamily(models: typeof filteredModels): Map<string, typeof filteredModels> {
    const fam: Map<string, typeof filteredModels> = new Map();
    for (const m of models) {
      if (!fam.has(m.family)) fam.set(m.family, []);
      fam.get(m.family)!.push(m);
    }
    return fam;
  }

  const selectedSet = new Set(selectedModels);
  const allFilteredIds = filteredModels.map((m) => m.model_id);
  const totalCount = filteredModels.length;
  const selectedCount = filteredModels.filter((m) => selectedSet.has(m.model_id)).length;

  function toggleExpanded(prov: string) {
    setExpandedProviders((prev) => {
      const next = new Set(prev);
      if (next.has(prov)) next.delete(prov);
      else next.add(prov);
      return next;
    });
  }

  function toggleModel(modelId: string) {
    if (selectedSet.has(modelId)) {
      onSelectionChange(selectedModels.filter((id) => id !== modelId));
    } else {
      onSelectionChange([...selectedModels, modelId]);
    }
  }

  function toggleProvider(prov: string) {
    const provModels = (grouped.get(prov) ?? []).map((m) => m.model_id);
    const allSelected = provModels.every((id) => selectedSet.has(id));
    if (allSelected) {
      onSelectionChange(selectedModels.filter((id) => !provModels.includes(id)));
    } else {
      const toAdd = provModels.filter((id) => !selectedSet.has(id));
      onSelectionChange([...selectedModels, ...toAdd]);
    }
  }

  function selectAll() {
    onSelectionChange([...allFilteredIds]);
  }

  function clearAll() {
    onSelectionChange([]);
  }

  return (
    <>
      {/* Domain dropdown */}
      <div className="sidebar-domain">
        <label className="sidebar-domain__label" htmlFor="sidebar-domain-select">
          Domain
        </label>
        <select
          id="sidebar-domain-select"
          className="sidebar-domain__select"
          value={activeSlug}
          onChange={(e) => onDomainSelect(e.target.value)}
          aria-label="Select domain"
        >
          {domains.map((d) => (
            <option key={d.slug} value={d.slug} disabled={!d.available}>
              {d.label}
              {!d.available ? " (coming soon)" : ""}
            </option>
          ))}
        </select>
      </div>

      {/* Providers & Models section */}
      <div className="sidebar-models">
        <div className="sidebar-section-header">
          <span>Providers &amp; Models</span>
          <span className="sidebar-section-count" aria-live="polite" aria-atomic="true">
            {selectedCount} of {totalCount}
          </span>
        </div>
        <div className="sidebar-quick-actions">
          <button
            type="button"
            className="sidebar-action-btn"
            onClick={selectAll}
            aria-label="Select all models"
          >
            Select all
          </button>
          <button
            type="button"
            className="sidebar-action-btn"
            onClick={clearAll}
            aria-label="Clear all model selections"
          >
            Clear
          </button>
        </div>

        {/* Provider groups */}
        {PROVIDER_ORDER.map((prov) => {
          const models = grouped.get(prov) ?? [];
          if (models.length === 0) return null;
          const isOpen = expandedProviders.has(prov);
          const provColor = PROVIDER_COLORS[prov] ?? "#888";
          const provName = PROVIDER_DISPLAY_NAMES[prov] ?? prov;
          const provModelIds = models.map((m) => m.model_id);
          const allProvSelected = provModelIds.every((id) => selectedSet.has(id));
          const families = groupByFamily(models);

          return (
            <div
              key={prov}
              className={`provider-group${isOpen ? " provider-group--open" : ""}`}
            >
              {/* Provider header row */}
              <div className="provider-group__header" onClick={() => toggleExpanded(prov)}>
                <ChevronIcon open={isOpen} />
                <span
                  className="provider-group__dot"
                  style={{ backgroundColor: provColor }}
                  aria-hidden="true"
                />
                <span className="provider-group__name">{provName}</span>
                <span className="provider-group__count">{models.length}</span>
                {/* Provider select-all checkbox (click stops propagation) */}
                <input
                  type="checkbox"
                  className="provider-group__checkbox"
                  checked={allProvSelected}
                  onChange={() => toggleProvider(prov)}
                  onClick={(e) => e.stopPropagation()}
                  aria-label={`${allProvSelected ? "Deselect" : "Select"} all ${provName} models`}
                />
              </div>

              {/* Expanded model list */}
              <div className="provider-group__models" aria-hidden={!isOpen}>
                {Array.from(families.entries()).map(([fam, famModels]) => (
                  <div key={fam}>
                    {families.size > 1 && (
                      <div className="model-family-label" aria-hidden="true">{fam}</div>
                    )}
                    {famModels.map((model) => {
                      const isSelected = selectedSet.has(model.model_id);
                      const shortName = modelShortName(model.model_id);
                      return (
                        <label
                          key={model.model_id}
                          className={`model-row${isSelected ? " model-row--selected" : ""}`}
                        >
                          <input
                            type="checkbox"
                            className="model-row__checkbox"
                            checked={isSelected}
                            onChange={() => toggleModel(model.model_id)}
                            aria-label={`Toggle ${shortName}`}
                          />
                          <span className="model-row__name">{shortName}</span>
                          {model.open_weights && (
                            <span className="model-row__badge" aria-label="open weights">
                              Open
                            </span>
                          )}
                          <span className="model-row__date">
                            {shortDate(model.release_date)}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Divider + filters */}
      <div className="sidebar-divider" style={{ margin: "10px 14px" }} />
      <div className="sidebar-filters">
        <div className="sidebar-section-header" style={{ marginTop: 0 }}>
          Filters
        </div>
        <div className="sidebar-toggle-row">
          <span className="sidebar-toggle-label">Open weights only</span>
          <label className="sidebar-toggle">
            <input
              type="checkbox"
              checked={openWeightsOnly}
              onChange={(e) => onOpenWeightsToggle(e.target.checked)}
              aria-label="Filter to open weights models only"
            />
            <span className="sidebar-toggle__track" />
            <span className="sidebar-toggle__thumb" />
          </label>
        </div>
      </div>
    </>
  );
}
