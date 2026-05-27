/**
 * Focus1SelfConsistencyOverview — ranked list of model cards by OCI.
 *
 * DESIGN_SYSTEM.md §13.3–§13.5
 * CDA SME S6 binding: no evaluative framing, use tier labels only.
 */

import { useState } from 'react';
import '../styles/focus1.css';
import { useFocus1Data } from '../hooks/useFocus1Data';
import {
  OCI_CONCENTRATED_THRESHOLD,
  OCI_MODERATE_THRESHOLD,
} from '../config/analysis';
import {
  selfConsistencyDescription,
  formatOciDisplay,
  BOOTSTRAP_CAVEAT_TEXT,
  EMPTY_NO_FOCUS1_DATA,
} from '../copy/focus1';
import { PROVIDER_COLORS } from './ContentArea';
import type { PublishedModel } from '../data/types';

// Build provider color map from model list
function getModelColor(model: PublishedModel): string {
  const provider = model.provider === 'openrouter'
    ? (['gpt', 'llama', 'mistral', 'deepseek', 'phi'] as const).reduce(
        (acc: string, fam) => (model.family === fam ? ({ gpt: 'openai', llama: 'meta', mistral: 'mistral', deepseek: 'deepseek', phi: 'microsoft' } as Record<string, string>)[fam] : acc),
        model.provider
      )
    : model.provider;
  return PROVIDER_COLORS[provider] || '#888';
}

function shortName(modelId: string): string {
  return modelId
    .replace(/^claude-/, '')
    .replace(/^gpt-/, 'gpt-')
    .replace(/^gemini-/, 'gemini-')
    .replace(/^meta-llama\//, '')
    .replace(/^mistralai\//, '')
    .split('/').pop() || modelId;
}

type ConcentrationTier = 'concentrated' | 'moderate' | 'diffuse';

function getTier(oci: number): ConcentrationTier {
  if (oci >= OCI_CONCENTRATED_THRESHOLD) return 'concentrated';
  if (oci >= OCI_MODERATE_THRESHOLD) return 'moderate';
  return 'diffuse';
}

interface Focus1SelfConsistencyOverviewProps {
  domainSlug: string;
  models: PublishedModel[];
  selectedModelId: string | null;
  onSelectModel: (id: string) => void;
}

export function Focus1SelfConsistencyOverview({
  domainSlug,
  models,
  selectedModelId,
  onSelectModel,
}: Focus1SelfConsistencyOverviewProps) {
  const { data, loading, error } = useFocus1Data(domainSlug);
  const [popoverOpen, setPopoverOpen] = useState<string | null>(null);

  if (loading) {
    return <div className="f1-loading">Loading individual consistency data…</div>;
  }
  if (error || !data) {
    return <div className="f1-empty">{EMPTY_NO_FOCUS1_DATA}</div>;
  }

  // Build ranked list sorted by OCI descending
  const ranked = Object.values(data)
    .sort((a, b) => b.oci - a.oci);

  return (
    <div className="f1-container">
      <p className="f1-desc">{selfConsistencyDescription(domainSlug)}</p>

      <div className="f1-overview" role="list" aria-label="Models ranked by output concentration">
        {ranked.map((modelData, idx) => {
          const model = models.find((m) => m.model_id === modelData.model_id);
          const color = model ? getModelColor(model) : '#888';
          const tier = getTier(modelData.oci);
          const isSelected = modelData.model_id === selectedModelId;

          return (
            <div
              key={modelData.model_id}
              role="button"
              tabIndex={0}
              aria-pressed={isSelected}
              aria-label={`${shortName(modelData.model_id)}, rank ${idx + 1}, OCI ${modelData.oci.toFixed(2)}, ${tier}`}
              className={`f1-model-card${isSelected ? ' f1-model-card--selected' : ''}`}
              onClick={() => onSelectModel(modelData.model_id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectModel(modelData.model_id);
                }
              }}
            >
              {/* Header row: rank · dot · name · tier badge */}
              <div className="f1-model-card__header">
                <span className="f1-model-card__rank">{idx + 1}</span>
                <span
                  className="f1-model-card__dot"
                  style={{ background: color }}
                  aria-hidden="true"
                />
                <span className="f1-model-card__name">
                  {shortName(modelData.model_id)}
                </span>
                <span
                  className={`f1-tier-badge f1-tier-badge--${tier}`}
                  aria-label={`Concentration tier: ${tier}`}
                >
                  {tier}
                </span>
              </div>

              {/* OCI value row */}
              <div className="f1-model-card__oci-row">
                <span className="f1-model-card__oci-label">Output Concentration Index</span>
                <span className="f1-model-card__oci-value">
                  {modelData.oci.toFixed(2)}
                </span>
                {modelData.oci_ci !== null ? (
                  <span className="f1-model-card__oci-ci">
                    (95% CI [{modelData.oci_ci[0].toFixed(2)}, {modelData.oci_ci[1].toFixed(2)}],
                    N = {modelData.n_runs} runs)
                  </span>
                ) : (
                  <span className="f1-model-card__oci-ci">
                    (N = {modelData.n_runs} runs; CI unavailable)
                  </span>
                )}
                {/* Info button for bootstrap caveat (§13.5) */}
                <span className="f1-popover">
                  <button
                    className="f1-info-btn"
                    aria-label="About confidence intervals"
                    onClick={(e) => {
                      e.stopPropagation();
                      setPopoverOpen(
                        popoverOpen === modelData.model_id
                          ? null
                          : modelData.model_id
                      );
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Escape') setPopoverOpen(null);
                    }}
                  >
                    ⓘ
                  </button>
                  {popoverOpen === modelData.model_id && (
                    <div
                      role="tooltip"
                      className="f1-popover__content"
                    >
                      {BOOTSTRAP_CAVEAT_TEXT}
                    </div>
                  )}
                </span>
              </div>

              {/* Supplementary stats */}
              <div className="f1-model-card__stats">
                {modelData.salience_stability_rho !== null && (
                  <div className="f1-stat">
                    <span className="f1-stat__label">Salience ρ</span>
                    <span className="f1-stat__value">
                      {modelData.salience_stability_rho.toFixed(2)}
                    </span>
                  </div>
                )}
                <div className="f1-stat">
                  <span className="f1-stat__label">Runs</span>
                  <span className="f1-stat__value">{modelData.n_runs}</span>
                </div>
                {modelData.deterministic_output && (
                  <div className="f1-stat">
                    <span className="f1-stat__label">Note</span>
                    <span className="f1-stat__value" style={{ color: 'var(--color-text-caption)' }}>
                      deterministic output
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* OCI display full form accessible note */}
      <p className="f1-desc" style={{ marginTop: 'var(--space-2)', fontSize: '10px' }}>
        {formatOciDisplay(0, null, 0).slice(0, 0)}
        OCI = Output Concentration Index. Higher values indicate more concentrated output
        distribution across runs. Tier labels: concentrated ≥{OCI_CONCENTRATED_THRESHOLD},
        moderate ≥{OCI_MODERATE_THRESHOLD}, diffuse &lt;{OCI_MODERATE_THRESHOLD}.
      </p>
    </div>
  );
}
